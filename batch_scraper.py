"""
Single Job Search Scraper
Run job scraping based on config.json configuration
"""

import json
import os
from datetime import datetime
from naukri_scraper import NaukriScraper


def load_config(config_file: str = 'config.json') -> dict:
    """Load configuration from JSON file"""
    with open(config_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def run_scraping(config_file: str = 'config.json'):
    """
    Run scraping based on configuration file
    
    Args:
        config_file (str): Path to configuration file
    """
    print("=" * 70)
    print("Naukri.com Job Scraper - Config Mode")
    print("=" * 70)
    
    # Load configuration
    config = load_config(config_file)
    job_search = config.get('job_search', {})
    scraper_settings = config.get('scraper_settings', {})
    
    if not job_search or not job_search.get('keyword'):
        print("❌ Error: No job search configuration found in config.json")
        print("Please set 'job_search' with at least a 'keyword' field")
        return
    
    # Display configuration
    print(f"\n📋 Job Search Configuration:")
    print(f"  Keyword: {job_search['keyword']}")
    print(f"  Location: {job_search.get('location', 'Any')}")
    print(f"  Experience: {job_search.get('experience', 0)} years" if job_search.get('experience', 0) > 0 else "  Experience: Any")
    print(f"  Max Jobs: {job_search.get('max_jobs', 40)}")
    
    print(f"\n⚙️ Scraper Settings:")
    print(f"  Time Filter: Last {scraper_settings.get('posted_within_days', 1)} day(s)")
    print(f"  Deep Scrape: {'Yes' if scraper_settings.get('deep_scrape', False) else 'No'}")
    print(f"  Headless Mode: {'Yes' if scraper_settings.get('headless', False) else 'No'}")
    print("=" * 70 + "\n")
    
    # Initialize scraper
    scraper = NaukriScraper(headless=scraper_settings.get('headless', False))
    
    try:
        # Run scraping
        jobs = scraper.scrape_jobs(
            keyword=job_search['keyword'],
            location=job_search.get('location', ''),
            experience=job_search.get('experience', 0),
            max_jobs=job_search.get('max_jobs', 40),
            deep_scrape=scraper_settings.get('deep_scrape', False)
        )
        
        # Generate output filename from keyword
        safe_keyword = job_search['keyword'].replace(' ', '_').lower()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"{safe_keyword}_{timestamp}.json"
        
        # Save results
        scraper.save_to_json(output_file)
        
        # Print summary
        print("\n" + "=" * 70)
        print("✅ SCRAPING COMPLETED")
        print("=" * 70)
        print(f"Total jobs found: {len(jobs)}")
        print(f"Results saved to: {output_file}")
        print("=" * 70)
        
    finally:
        scraper.close()


if __name__ == "__main__":
    run_scraping()
