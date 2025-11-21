"""
Batch Job Scraper
Run multiple scraping jobs based on configuration file
"""

import json
import os
import time
from datetime import datetime
from naukri_scraper import NaukriScraper


def load_config(config_file: str = 'config.json') -> dict:
    """Load configuration from JSON file"""
    with open(config_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def run_batch_scraping(config_file: str = 'config.json'):
    """
    Run batch scraping based on configuration file
    
    Args:
        config_file (str): Path to configuration file
    """
    print("=" * 70)
    print("Naukri.com Batch Job Scraper")
    print("=" * 70)
    
    # Load configuration
    config = load_config(config_file)
    search_configs = config.get('search_configs', [])
    scraper_settings = config.get('scraper_settings', {})
    
    if not search_configs:
        print("No search configurations found in config.json")
        return
    
    print(f"\nFound {len(search_configs)} search configurations")
    print(f"Scraper settings: {scraper_settings}\n")
    
    # Create output directory for this batch
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = f"scraping_results_{timestamp}"
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize scraper once for all searches
    scraper = NaukriScraper(headless=scraper_settings.get('headless', True))
    
    all_results = []
    
    try:
        for idx, search_config in enumerate(search_configs, 1):
            print(f"\n{'='*70}")
            print(f"Search {idx}/{len(search_configs)}: {search_config['name']}")
            print(f"{'='*70}")
            print(f"Keyword: {search_config['keyword']}")
            print(f"Location: {search_config.get('location', 'Any')}")
            print(f"Experience: {search_config.get('experience', 'Any')}")
            print(f"Pages: {search_config.get('max_pages', 1)}")
            
            # Run scraping
            jobs = scraper.scrape_jobs(
                keyword=search_config['keyword'],
                location=search_config.get('location', ''),
                experience=search_config.get('experience', ''),
                max_pages=search_config.get('max_pages', 1),
                scroll_count=scraper_settings.get('scroll_count', 5)
            )
            
            # Save individual results
            safe_name = search_config['name'].replace(' ', '_').lower()
            output_file = os.path.join(output_dir, f"{safe_name}.json")
            scraper.save_to_json(output_file)
            
            # Store for combined results
            all_results.append({
                'search_name': search_config['name'],
                'search_params': search_config,
                'jobs_found': len(jobs),
                'jobs': jobs
            })
            
            print(f"✓ Completed: {len(jobs)} jobs found")
            
            # Wait between searches
            if idx < len(search_configs):
                wait_time = 5
                print(f"\nWaiting {wait_time} seconds before next search...")
                time.sleep(wait_time)
    
    finally:
        scraper.close()
    
    # Save combined results
    combined_output = {
        'metadata': {
            'total_searches': len(search_configs),
            'total_jobs': sum(r['jobs_found'] for r in all_results),
            'scraped_at': datetime.now().isoformat(),
            'source': 'Naukri.com'
        },
        'results': all_results
    }
    
    combined_file = os.path.join(output_dir, 'combined_results.json')
    with open(combined_file, 'w', encoding='utf-8') as f:
        json.dump(combined_output, f, indent=2, ensure_ascii=False)
    
    # Print summary
    print("\n" + "=" * 70)
    print("BATCH SCRAPING COMPLETED")
    print("=" * 70)
    print(f"Total searches: {len(search_configs)}")
    print(f"Total jobs found: {combined_output['metadata']['total_jobs']}")
    print(f"Results saved in: {output_dir}/")
    print("=" * 70)


if __name__ == "__main__":
    run_batch_scraping()
