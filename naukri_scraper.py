"""
Naukri.com Job Scraper
A custom web scraper to extract job listings from Naukri.com
"""

import time
import json
import logging
import re
import argparse
from datetime import datetime
from typing import List, Dict, Optional

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException


class NaukriScraper:
    """Web scraper for Naukri.com job portal"""
    
    def __init__(self, headless: bool = True):
        """
        Initialize the Naukri scraper
        
        Args:
            headless (bool): Run browser in headless mode (no GUI)
        """
        self.base_url = "https://www.naukri.com"
        self.jobs_data = []
        self.setup_logging()
        self.driver = self.setup_driver(headless)
        
    def setup_logging(self):
        """Configure logging for the scraper"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('naukri_scraper.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def setup_driver(self, headless: bool) -> webdriver.Chrome:
        """
        Setup Chrome WebDriver with optimized options for scraping
        
        Args:
            headless (bool): Run in headless mode
            
        Returns:
            webdriver.Chrome: Configured Chrome driver
        """
        chrome_options = Options()
        
        # Headless mode
        if headless:
            chrome_options.add_argument('--headless')
        
        # === INCOGNITO MODE (Clean slate every run) ===
        chrome_options.add_argument('--incognito')
        
        # === SUPPRESS CHROME LOGS & ERRORS ===
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging', 'enable-automation'])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument('--log-level=3')  # Only fatal errors
        
        # === DISABLE CHROME SERVICES (Prevent GCM/sync errors) ===
        chrome_options.add_argument('--disable-sync')
        chrome_options.add_argument('--disable-background-networking')
        chrome_options.add_argument('--disable-default-apps')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-background-timer-throttling')
        chrome_options.add_argument('--disable-backgrounding-occluded-windows')
        chrome_options.add_argument('--disable-breakpad')
        chrome_options.add_argument('--disable-component-extensions-with-background-pages')
        chrome_options.add_argument('--disable-features=TranslateUI')
        chrome_options.add_argument('--disable-ipc-flooding-protection')
        chrome_options.add_argument('--disable-renderer-backgrounding')
        
        # === DISABLE POPUPS & NOTIFICATIONS ===
        chrome_options.add_argument('--disable-notifications')
        chrome_options.add_argument('--disable-popup-blocking')
        prefs = {
            'profile.default_content_setting_values.notifications': 2,  # Block notifications
            'profile.default_content_setting_values.popups': 0,  # Allow popups (for job links)
            'credentials_enable_service': False,  # Disable save password prompts
            'profile.password_manager_enabled': False  # Disable password manager
        }
        chrome_options.add_experimental_option('prefs', prefs)
        
        # === PERFORMANCE & STABILITY ===
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')  # Disable GPU acceleration
        chrome_options.add_argument('--disable-software-rasterizer')
        
        # === ANTI-DETECTION ===
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        self.logger.info("Launching Chrome WebDriver in incognito mode...")
        driver = webdriver.Chrome(options=chrome_options)
        driver.maximize_window()
        
        return driver
    
    def build_search_url(self, 
                        keyword: str, 
                        location: str = "", 
                        experience: int = 0,
                        salary: str = "",
                        freshness: int = 1) -> str:
        """
        Build search URL with query parameters (matches Naukri's official search format)
        
        Args:
            keyword (str): Job title or keyword (supports comma-separated values)
            location (str): Job location (supports comma-separated values)
            experience (int): Experience in years (e.g., 4 for 4 years, 0 for any experience)
            salary (str): Salary range
            freshness (int): Filter jobs posted within last N days (1, 3, 7, 15, 30)
            
        Returns:
            str: Formatted search URL with query parameters
        """
        from urllib.parse import quote
        
        # Build base URL path (still uses hyphenated format for SEO-friendly URL)
        search_url = f"{self.base_url}/{keyword.replace(' ', '-').lower()}-jobs"
        
        if location:
            search_url += f"-in-{location.replace(' ', '-').lower()}"
        
        # Build query parameters (Naukri's official format)
        params = []
        
        # Add keyword parameter (supports multiple comma-separated values)
        # Use lowercase to match Naukri's format
        params.append(f"k={quote(keyword.lower())}")
        
        # Add location parameter (supports multiple comma-separated values)
        if location:
            params.append(f"l={quote(location.lower())}")
        
        # Add experience parameter (integer value in years)
        if experience and experience > 0:
            params.append(f"experience={experience}")
        
        # Add freshness filter (jobAge parameter)
        if freshness and freshness in [1, 3, 7, 15, 30]:
            params.append(f"jobAge={freshness}")
        
        # Add salary if provided
        if salary:
            params.append(f"salary={quote(salary)}")
            
        if params:
            search_url += "?" + "&".join(params)
        
        return search_url
    
    def get_apply_link(self, job_url: str) -> Dict[str, str]:
        """
        Visit job details page and extract full description.
        Does NOT click apply button.
        
        Args:
            job_url (str): URL of the job details page
            
        Returns:
            Dict: Dictionary with apply_link (same as job_url), apply_type, and full_description
        """
        original_window = self.driver.current_window_handle
        
        try:
            # Open job in new tab
            self.driver.execute_script(f"window.open('{job_url}', '_blank');")
            time.sleep(1)
            
            # Switch to new tab
            new_window = [w for w in self.driver.window_handles if w != original_window][0]
            self.driver.switch_to.window(new_window)
            time.sleep(2)  # Wait for page to load
            
            result = {
                'apply_link': job_url,  # Just return the post URL
                'apply_type': 'naukri',
                'full_description': 'N/A'
            }
            
            # Extract full job description
            try:
                desc_selectors = [
                    '.job-desc',
                    '.job-description',
                    '[class*="description"]',
                    '.styles_JDC__dang-inner-html__h0K4t',
                ]
                
                for selector in desc_selectors:
                    try:
                        desc_elem = self.driver.find_element(By.CSS_SELECTOR, selector)
                        if desc_elem:
                            full_desc = desc_elem.text.strip()
                            if full_desc and len(full_desc) > 50:
                                result['full_description'] = full_desc
                                break
                    except NoSuchElementException:
                        continue
            except Exception as e:
                self.logger.debug(f"Could not extract full description: {str(e)}")
            
            # Close the tab
            self.driver.close()
            self.driver.switch_to.window(original_window)
            
            return result
                
        except Exception as e:
            # If anything goes wrong, close extra windows and return result
            try:
                for window in self.driver.window_handles:
                    if window != original_window:
                        self.driver.switch_to.window(window)
                        self.driver.close()
                self.driver.switch_to.window(original_window)
            except:
                pass
            
            return {
                'apply_link': job_url,
                'apply_type': 'naukri',
                'full_description': 'N/A'
            }
    
    def extract_job_info(self, card, index: int, deep_scrape: bool = False) -> Optional[Dict]:
        """
        Extract information from a single job card
        
        Args:
            card: Selenium WebElement representing a job card
            index (int): Job index number
            deep_scrape (bool): If True, visit job page to get apply link
            
        Returns:
            Optional[Dict]: Job information dictionary
        """
        job_data = {
            'index': index,
            'scraped_at': datetime.now().isoformat()
        }
        
        # Extract Job ID for sorting
        try:
            job_id = card.get_attribute('data-job-id')
            if job_id:
                job_data['job_id'] = int(job_id)
            else:
                # Try to extract from tuple ID
                tuple_id = card.get_attribute('id')
                if tuple_id:
                    job_data['job_id'] = int(''.join(filter(str.isdigit, tuple_id)))
                else:
                    job_data['job_id'] = 0
        except:
            job_data['job_id'] = 0
        
        try:
            # Job Title and Link
            title_elem = card.find_element(By.CSS_SELECTOR, "a.title")
            job_data['title'] = title_elem.text.strip()
            
            # Get the job link
            job_link = title_elem.get_attribute('href')
            if job_link and not job_link.startswith('http'):
                job_link = self.base_url + job_link
            
            job_data['job_details_url'] = job_link
            
            # If we didn't get job_id from attribute, try from link
            if job_data['job_id'] == 0 and job_link:
                try:
                    match = re.search(r'(\d+)$', job_link)
                    if match:
                        job_data['job_id'] = int(match.group(1))
                except:
                    pass
            
            # Deep scrape logic
            if deep_scrape and job_link:
                apply_info = self.get_apply_link(job_link)
                job_data['apply_link'] = apply_info['apply_link']
                job_data['apply_type'] = apply_info['apply_type']
                job_data['description'] = apply_info.get('full_description', 'N/A')
            else:
                job_data['apply_link'] = job_link
                job_data['apply_type'] = 'naukri'
                try:
                    desc_elem = card.find_element(By.CLASS_NAME, "job-desc")
                    job_data['description'] = desc_elem.text.strip()
                except NoSuchElementException:
                    job_data['description'] = "N/A"
            
        except NoSuchElementException:
            self.logger.warning(f"Could not find title/link for job {index}")
            return None
        
        # Company Name
        try:
            company_elem = card.find_element(By.CSS_SELECTOR, "a.comp-name")
            job_data['company'] = company_elem.text.strip()
        except NoSuchElementException:
            try:
                company_elem = card.find_element(By.CSS_SELECTOR, ".company-name")
                job_data['company'] = company_elem.text.strip()
            except:
                job_data['company'] = "N/A"
        
        # Experience
        try:
            exp_elem = card.find_element(By.CLASS_NAME, "expwdth")
            job_data['experience'] = exp_elem.text.strip()
        except NoSuchElementException:
            job_data['experience'] = "N/A"
            
        # Salary
        try:
            salary_elem = card.find_element(By.CLASS_NAME, "sal")
            job_data['salary'] = salary_elem.text.strip()
        except NoSuchElementException:
            job_data['salary'] = "N/A"
        
        # Location
        try:
            location_elem = card.find_element(By.CLASS_NAME, "locWdth")
            job_data['location'] = location_elem.text.strip()
        except NoSuchElementException:
            job_data['location'] = "N/A"
        
        # Posted Date
        try:
            date_elem = card.find_element(By.CLASS_NAME, "job-post-day")
            job_data['posted_date'] = date_elem.text.strip()
        except NoSuchElementException:
            job_data['posted_date'] = "N/A"
        
        return job_data
    
    def extract_job_cards(self, deep_scrape: bool = False, max_jobs_needed: int = None) -> List[Dict]:
        """
        Extract job information from job cards on the page
        
        Args:
            deep_scrape (bool): If True, visit each job page to get apply link
            max_jobs_needed (int): Maximum number of jobs to extract
            
        Returns:
            List[Dict]: List of job dictionaries
        """
        jobs = []
        
        try:
            wait = WebDriverWait(self.driver, 10)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".srp-jobtuple-wrapper, .cust-job-tuple")))
            
            job_cards = self.driver.find_elements(By.CSS_SELECTOR, ".srp-jobtuple-wrapper, .cust-job-tuple")
            self.logger.info(f"Found {len(job_cards)} job listings")
            
            for idx, card in enumerate(job_cards, 1):
                if max_jobs_needed and len(jobs) >= max_jobs_needed:
                    self.logger.info(f"Reached max jobs limit ({max_jobs_needed}), stopping extraction")
                    break
                
                try:
                    job_info = self.extract_job_info(card, idx, deep_scrape=deep_scrape)
                    if job_info:
                        jobs.append(job_info)
                        if deep_scrape:
                            self.logger.info(f"Job {len(jobs)}: {job_info['title']} - Apply type: {job_info['apply_type']}")
                except Exception as e:
                    self.logger.warning(f"Error extracting job {idx}: {str(e)}")
                    continue
            
        except TimeoutException:
            self.logger.error("Timeout waiting for job listings to load")
        except Exception as e:
            self.logger.error(f"Error extracting job cards: {str(e)}")
        
        return jobs
    
    def scrape_jobs(self, 
                   keyword: str, 
                   location: str = "",
                   experience: int = 0,
                   max_jobs: int = 100,
                   deep_scrape: bool = False,
                   sort_by: str = "date",
                   freshness: int = 1) -> List[Dict]:
        """
        Main scraping function with auto-pagination and UI sorting
        
        Args:
            keyword (str): Job search keyword
            location (str): Job location
            experience (int): Experience in years (e.g., 4 for 4 years, 0 for any)
            max_jobs (int): Maximum number of jobs to scrape (default: 100)
            deep_scrape (bool): If True, visit each job to extract apply link
            sort_by (str): Sort option - 'date' or 'relevance' (default: 'date')
            freshness (int): Filter jobs posted within last N days (1, 3, 7, 15, 30)
            
        Returns:
            List[Dict]: List of scraped jobs
        """
        print("\n" + "=" * 70)
        print("Starting job scraping...")
        print("=" * 70 + "\n")
        
        all_jobs = []
        page = 1
        
        while len(all_jobs) < max_jobs:
            self.logger.info(f"Scraping page {page} (collected {len(all_jobs)}/{max_jobs} jobs so far)")
            print(f"📄 Page {page}: {len(all_jobs)}/{max_jobs} jobs collected so far...")
            
            search_url = self.build_search_url(keyword, location, experience, freshness=freshness)
            if page > 1:
                search_url += f"&page={page}" if "?" in search_url else f"?page={page}"
            
            self.logger.info(f"Accessing URL: {search_url}")
            
            try:
                self.driver.get(search_url)
                time.sleep(3)
                
                # UI SORTING LOGIC
                if page == 1 and sort_by in ['date', 'relevance']:
                    try:
                        sort_option_name = 'Date' if sort_by == 'date' else 'Relevance'
                        self.logger.info(f"Attempting to switch sort to '{sort_option_name}' via UI...")
                        print(f"⚡ Trying to click 'Sort by' dropdown...")
                        
                        sort_button = None
                        try:
                            sort_xpath = "//*[contains(text(), 'Sort by')]"
                            sort_button = self.driver.find_element(By.XPATH, sort_xpath)
                        except:
                            sort_button = self.driver.find_element(By.CSS_SELECTOR, ".sort-droopdown, .sort-label")
                            
                        if sort_button:
                            self.driver.execute_script("arguments[0].style.border='3px solid red'", sort_button)
                            time.sleep(1)
                            self.driver.execute_script("arguments[0].click();", sort_button)
                            time.sleep(2)
                            
                            print(f"⚡ Looking for '{sort_option_name}' option...")
                            sort_option = None
                            try:
                                # Try to find by text (Date or Relevance)
                                option_xpath = f"//li//*[contains(text(), '{sort_option_name}')] | //a[contains(text(), '{sort_option_name}')]"
                                sort_option = self.driver.find_element(By.XPATH, option_xpath)
                            except:
                                # Fallback: Date is usually 2nd item, Relevance is 1st
                                nth_child = "2" if sort_by == 'date' else "1"
                                sort_option = self.driver.find_element(By.CSS_SELECTOR, f"ul.dropdown li:nth-child({nth_child})")
                                
                            if sort_option:
                                self.driver.execute_script("arguments[0].style.backgroundColor='yellow'", sort_option)
                                time.sleep(1)
                                self.driver.execute_script("arguments[0].click();", sort_option)
                                print(f"✓ Clicked '{sort_option_name}' option!")
                                time.sleep(3)
                            else:
                                print(f"✗ Could not find '{sort_option_name}' option to click")
                                
                    except Exception as e:
                        print(f"⚠ UI Sort failed: {str(e)}")
                        self.logger.warning(f"UI Sort failed: {e}")
                
                
                # Calculate how many jobs we still need
                jobs_remaining = max_jobs - len(all_jobs)
                
                # Dynamic scrolling - only scroll until we have enough jobs for THIS page
                current_job_count = 0
                scrolls = 0
                max_scrolls_limit = min(5, (jobs_remaining // 5) + 2)  # Adaptive scroll limit
                
                while current_job_count < jobs_remaining and scrolls < max_scrolls_limit:
                    job_cards = self.driver.find_elements(By.CSS_SELECTOR, ".srp-jobtuple-wrapper, .cust-job-tuple")
                    current_job_count = len(job_cards)
                    
                    if current_job_count >= jobs_remaining:
                        self.logger.info(f"Found enough jobs ({current_job_count} >= {jobs_remaining}), stopping scroll.")
                        break
                        
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(2)
                    scrolls += 1
                    self.logger.info(f"Scrolled {scrolls} times, found {current_job_count} jobs so far...")
                
                page_jobs = self.extract_job_cards(deep_scrape=deep_scrape, max_jobs_needed=jobs_remaining)
                
                if not page_jobs:
                    self.logger.info("No more jobs found, stopping pagination")
                    print("✓ No more jobs available")
                    break
                
                all_jobs.extend(page_jobs)
                
                self.logger.info(f"Extracted {len(page_jobs)} jobs from page {page}, total now: {len(all_jobs)}")
                print(f"✓ Collected {len(all_jobs)}/{max_jobs} jobs")
                
                if len(all_jobs) >= max_jobs:
                    self.logger.info(f"Reached max_jobs limit ({max_jobs})")
                    print(f"✓ Collected maximum {max_jobs} jobs!")
                    break
                
                page += 1
                time.sleep(2)
                    
            except Exception as e:
                self.logger.error(f"Error scraping page {page}: {str(e)}")
                break
        
        # Local Sorting Logic
        def parse_date_for_sorting(job):
            posted = job.get('posted_date', '').lower()
            job_id = job.get('job_id', 0)
            days_ago = 999
            
            if not posted or posted == 'n/a':
                days_ago = 999
            elif 'just now' in posted:
                days_ago = -0.2
            elif 'few hours' in posted:
                days_ago = -0.1
            elif 'today' in posted:
                days_ago = 0
            elif 'hour' in posted:
                days_ago = 0
            elif 'day' in posted:
                try:
                    match = re.search(r'(\d+)', posted)
                    days_ago = int(match.group(1)) if match else 1
                except:
                    days_ago = 1
            elif 'week' in posted:
                try:
                    match = re.search(r'(\d+)', posted)
                    days_ago = int(match.group(1)) * 7 if match else 7
                except:
                    days_ago = 7
            elif 'month' in posted:
                days_ago = 30
            
            return (days_ago, -job_id)
        
        all_jobs.sort(key=parse_date_for_sorting)
        self.logger.info(f"Sorted {len(all_jobs)} jobs by recency (newest first)")
        
        print("\n" + "="*80)
        print(f"FINAL SORTED LIST ({len(all_jobs)} jobs)")
        print("="*80)
        print(f"{'#':<4} | {'Posted':<15} | {'Job ID':<12} | {'Title'}")
        print("-" * 80)
        for i, job in enumerate(all_jobs):
            print(f"{i+1:<4} | {job.get('posted_date', 'N/A'):<15} | {job.get('job_id', 0):<12} | {job.get('title', 'N/A')[:40]}")
        print("="*80 + "\n")
        
        self.jobs_data = all_jobs
        return all_jobs
    
    def save_to_json(self, filename: str = None):
        """Save scraped jobs to JSON file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"naukri_jobs_{timestamp}.json"
        
        if not filename.endswith('.json'):
            filename += '.json'
        
        output_data = {
            'metadata': {
                'total_jobs': len(self.jobs_data),
                'scraped_at': datetime.now().isoformat(),
                'source': 'Naukri.com'
            },
            'jobs': self.jobs_data
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Saved {len(self.jobs_data)} jobs to {filename}")
        print(f"\n✓ Successfully saved {len(self.jobs_data)} jobs to '{filename}'")
    
    def close(self):
        """Close the browser and cleanup"""
        if self.driver:
            self.driver.quit()
            self.logger.info("Browser closed")


def main():
    """Main entry point for CLI usage"""
    parser = argparse.ArgumentParser(description='Naukri.com Job Scraper - Auto-paginates for last 24hrs jobs')
    parser.add_argument('--keyword', '-k', required=True, help='Job search keyword')
    parser.add_argument('--location', '-l', default='', help='Job location')
    parser.add_argument('--experience', '-e', type=int, default=0, help='Experience in years (e.g., 4 for 4 years)')
    parser.add_argument('--max-jobs', '-m', type=int, default=100, help='Maximum jobs to scrape (default: 100)')
    parser.add_argument('--output', '-o', help='Output JSON filename')
    parser.add_argument('--headless', action='store_true', help='Run browser in headless mode')
    parser.add_argument('--deep-scrape', action='store_true', help='Visit each job to extract description')
    parser.add_argument('--sort-by', '-s', choices=['date', 'relevance'], default='date', help='Sort by date or relevance (default: date)')
    parser.add_argument('--freshness', '-f', type=int, choices=[1, 3, 7, 15, 30], default=1, help='Jobs posted within last N days (1, 3, 7, 15, 30)')
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("Naukri.com Job Scraper")
    print("=" * 70)
    print(f"Keyword: {args.keyword}")
    print(f"Location: {args.location or 'Any'}")
    print(f"Experience: {args.experience or 'Any'}")
    print(f"Max Jobs: {args.max_jobs}")
    print(f"Sort By: {args.sort_by.capitalize()}")
    print(f"Freshness: Last {args.freshness} day(s)")
    print(f"Deep Scrape: {'Yes' if args.deep_scrape else 'No'}")
    print("=" * 70)
    
    scraper = NaukriScraper(headless=args.headless)
    
    try:
        jobs = scraper.scrape_jobs(
            keyword=args.keyword,
            location=args.location,
            experience=args.experience,
            max_jobs=args.max_jobs,
            deep_scrape=args.deep_scrape,
            sort_by=args.sort_by,
            freshness=args.freshness
        )
        
        if jobs:
            scraper.save_to_json(args.output)
        else:
            print("\nNo jobs found matching criteria.")
            
    except KeyboardInterrupt:
        print("\n\nScraping interrupted by user.")
    except Exception as e:
        print(f"\n\nAn error occurred: {str(e)}")
    finally:
        scraper.close()


if __name__ == "__main__":
    main()
