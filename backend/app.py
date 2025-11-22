"""
Flask Backend API for Naukri Scraper
Provides REST API endpoints for the Angular frontend
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import json
import os
import sys
import subprocess
import threading
import time
from datetime import datetime

# Add parent directory to path to import naukri_scraper and batch_scraper
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import batch_scraper
except ImportError:
    # Fallback if running from root
    sys.path.append(os.getcwd())
    import batch_scraper

app = Flask(__name__)
CORS(app)  # Enable CORS for Angular frontend

# Global variable to track scraping status
scraping_status = {
    'state': 'idle',  # idle, running, completed, failed
    'progress': 0,
    'message': '',
    'last_updated': None,
    'error': None
}

def run_scraper(config_data):
    """Run the scraper in a separate thread"""
    global scraping_status
    
    try:
        scraping_status['state'] = 'running'
        scraping_status['progress'] = 10
        scraping_status['message'] = 'Initializing scraper...'
        scraping_status['last_updated'] = datetime.now().isoformat()
        scraping_status['error'] = None
        
        # Update config.json with new parameters
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.json')
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # Update job_search parameters
        config['job_search']['keyword'] = config_data['keyword']
        config['job_search']['location'] = config_data['location']
        config['job_search']['experience'] = int(config_data['experience'])
        config['job_search']['max_jobs'] = int(config_data['max_jobs'])
        config['job_search']['sort_by'] = config_data['sort_by']
        config['job_search']['freshness'] = int(config_data['freshness'])
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4)
        
        scraping_status['progress'] = 30
        scraping_status['message'] = 'Configuration updated. Starting scraper...'
        scraping_status['last_updated'] = datetime.now().isoformat()
        
        scraping_status['progress'] = 50
        scraping_status['message'] = 'Scraping jobs from Naukri.com...'
        scraping_status['last_updated'] = datetime.now().isoformat()
        
        # Execute the scraper directly
        # We reload to ensure fresh config is picked up if the module caches it
        import importlib
        importlib.reload(batch_scraper)
        
        print("DEBUG: Calling batch_scraper.run_scraping()...")
        # Run the scraping function
        batch_scraper.run_scraping()
        print("DEBUG: batch_scraper.run_scraping() returned.")
        
        scraping_status['progress'] = 100
        scraping_status['state'] = 'completed'
        scraping_status['message'] = 'Scraping completed successfully!'
        scraping_status['last_updated'] = datetime.now().isoformat()
        
    except BaseException as e:
        print(f"Scraping error (caught BaseException): {str(e)}")
        import traceback
        traceback.print_exc()
        
        scraping_status['progress'] = 0
        scraping_status['state'] = 'failed'
        scraping_status['message'] = f'Error: {str(e)}'
        scraping_status['error'] = str(e)
        scraping_status['last_updated'] = datetime.now().isoformat()


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'timestamp': datetime.now().isoformat()})


@app.route('/api/scrape', methods=['POST'])
def start_scraping():
    """Start the scraping process"""
    global scraping_status
    
    if scraping_status['state'] == 'running':
        return jsonify({
            'success': False,
            'message': 'Scraping is already in progress'
        }), 400
    
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['keyword', 'location', 'experience', 'max_jobs', 'sort_by', 'freshness']
        for field in required_fields:
            if field not in data or data[field] == '':
                return jsonify({
                    'success': False,
                    'message': f'Missing required field: {field}'
                }), 400
        
        # Validate numeric fields
        try:
            int(data['experience'])
            int(data['max_jobs'])
            int(data['freshness'])
        except ValueError:
            return jsonify({
                'success': False,
                'message': 'Experience, max_jobs, and freshness must be valid numbers'
            }), 400
        
        # Validate sort_by
        if data['sort_by'] not in ['date', 'relevance']:
            return jsonify({
                'success': False,
                'message': 'sort_by must be either "date" or "relevance"'
            }), 400
        
        # Validate freshness
        if int(data['freshness']) not in [1, 3, 7, 15, 30]:
            return jsonify({
                'success': False,
                'message': 'freshness must be one of: 1, 3, 7, 15, 30'
            }), 400
        
        # Reset status
        scraping_status = {
            'state': 'running',
            'progress': 0,
            'message': 'Starting scraper...',
            'last_updated': datetime.now().isoformat(),
            'error': None
        }
        
        # Start scraping in background thread
        thread = threading.Thread(target=run_scraper, args=(data,))
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'message': 'Scraping started successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error starting scraper: {str(e)}'
        }), 500


@app.route('/api/status', methods=['GET'])
def get_status():
    """Get current scraping status"""
    return jsonify(scraping_status)


@app.route('/api/results', methods=['GET'])
def get_results():
    """Get scraped job results"""
    try:
        results_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'scrapped_job_details.json')
        
        if not os.path.exists(results_path):
            return jsonify({
                'success': False,
                'message': 'No results found. Please run a scrape first.'
            }), 404
        
        with open(results_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return jsonify({
            'success': True,
            'data': data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error reading results: {str(e)}'
        }), 500


@app.route('/api/config', methods=['GET'])
def get_config():
    """Get current configuration"""
    try:
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.json')
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        return jsonify({
            'success': True,
            'data': config
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error reading config: {str(e)}'
        }), 500


if __name__ == '__main__':
    print("=" * 70)
    print("Naukri Scraper Backend API")
    print("=" * 70)
    print("Server starting on http://localhost:5000")
    print("API Endpoints:")
    print("  GET  /api/health   - Health check")
    print("  POST /api/scrape   - Start scraping")
    print("  GET  /api/status   - Get scraping status")
    print("  GET  /api/results  - Get scraped results")
    print("  GET  /api/config   - Get current config")
    print("=" * 70)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
