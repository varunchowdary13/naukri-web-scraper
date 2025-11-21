"""
Quick Test Script for Naukri Scraper
This script runs a quick test to verify the scraper is working
"""

from naukri_scraper import NaukriScraper
import sys


def quick_test():
    """Run a quick test scrape"""
    print("=" * 70)
    print("Naukri Scraper - Quick Test")
    print("=" * 70)
    print("\nThis will scrape 1 page of Python Developer jobs in Bangalore")
    print("Running in visible browser mode so you can see what's happening...\n")
    
    # Initialize scraper (not headless so you can see it work)
    scraper = NaukriScraper(headless=False)
    
    try:
        # Scrape one page
        jobs = scraper.scrape_jobs(
            keyword="Python Developer",
            location="Bangalore",
            max_pages=1,
            scroll_count=3
        )
        
        print(f"\n{'='*70}")
        print(f"✓ Test successful! Found {len(jobs)} jobs")
        print(f"{'='*70}")
        
        if jobs:
            print("\nFirst job preview:")
            print(f"Title: {jobs[0].get('title', 'N/A')}")
            print(f"Company: {jobs[0].get('company', 'N/A')}")
            print(f"Location: {jobs[0].get('location', 'N/A')}")
            print(f"Link: {jobs[0].get('link', 'N/A')}")
        
        # Save results
        scraper.save_to_json("test_results.json")
        
        print(f"\n{'='*70}")
        print("Check 'test_results.json' for full results!")
        print(f"{'='*70}")
        
    except Exception as e:
        print(f"\n✗ Test failed: {str(e)}")
        print("\nPlease check:")
        print("1. Chrome browser is installed")
        print("2. Internet connection is working")
        print("3. Dependencies are installed (pip install -r requirements.txt)")
        sys.exit(1)
        
    finally:
        scraper.close()


if __name__ == "__main__":
    quick_test()
