"""
Naukri.com Job Scraper
A custom web scraper to extract job listings from Naukri.com
"""

import time
import json
import logging
from datetime import datetime
from typing import List, Dict, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import argparse


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
        Setup Chrome WebDriver with appropriate options
        
        Args:
            headless (bool): Run in headless mode
            
        Returns:
            webdriver.Chrome: Configured Chrome driver
        """
        chrome_options = Options()
        
        if headless:
            chrome_options.add_argument('--headless')
        
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        # Disable automation flags
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        self.logger.info("Initializing Chrome WebDriver...")
        driver = webdriver.Chrome(options=chrome_options)
        driver.maximize_window()
        
        return driver
    
    def wait_for_login(self, timeout: int = 120) -> bool:
        """
        Open Naukri login page and wait for user to login manually
        
        Args:
            timeout (int): Maximum time to wait in seconds (default: 120 = 2 minutes)
            
        Returns:
            bool: True if login successful, False otherwise
        """
        login_url = "https://www.naukri.com/nlogin/login"
        
        print("\n" + "=" * 70)
        print("USER LOGIN REQUIRED")
        print("=" * 70)
        print("Opening Naukri login page...")
        print("Please login using your credentials (username/password or Google)")
        print(f"You have {timeout} seconds ({timeout//60} minutes) to complete login.")
        print("The scraper will automatically detect when you're logged in.")
        print("=" * 70 + "\n")
        
        self.logger.info("Opening Naukri login page for user authentication")
        self.driver.get(login_url)
        
        # Wait for user to login - check every 5 seconds
        check_interval = 5
        elapsed = 0
        
        while elapsed < timeout:
            time.sleep(check_interval)
            elapsed += check_interval
            
            # Check if user is logged in by looking for profile indicators
            is_logged_in = self._check_login_status()
            
            if is_logged_in:
                print("\n✓ Login successful! Proceeding with scraping...")
                self.logger.info("User login detected - proceeding with scraping")
                
                # Navigate to home page after login
                self.driver.get(self.base_url)
                time.sleep(2)
                
                return True
            else:
                remaining = timeout - elapsed
                if remaining > 0:
                    print(f"Waiting for login... ({remaining} seconds remaining)", end='\r')
        
        print("\n\n✗ Login timeout! Please login faster next time.")
        self.logger.warning("Login timeout - user did not complete login in time")
        return False
    
    def _check_login_status(self) -> bool:
        """
        Check if user is currently logged in to Naukri
        
        Returns:
            bool: True if logged in, False otherwise
        """
        try:
            # Method 1: Check for user profile/name element
            profile_selectors = [
                '.nI-gNb-drawer__icon',  # Profile icon
                '[class*="user-name"]',  # User name
                '[class*="userinfo"]',  # User info
                'div.nI-gNb-drawer__icon',  # Drawer icon
                '.nI-gNb-menuItems__profile',  # Profile menu
            ]
            
            for selector in profile_selectors:
                try:
                    elem = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if elem and elem.is_displayed():
                        return True
                except NoSuchElementException:
                    continue
            
            # Method 2: Check if we're NOT on login page anymore
            current_url = self.driver.current_url
            if 'nlogin' not in current_url and 'login' not in current_url.lower():
                # Additional check: look for any user-specific elements
                try:
                    # Check for elements that only appear when logged in
                    user_elements = self.driver.find_elements(By.CSS_SELECTOR, '[class*="user"], [class*="profile"]')
                    if len(user_elements) > 3:  # If we find multiple user-related elements
                        return True
                except:
                    pass
            
            return False
            
        except Exception as e:
            self.logger.debug(f"Error checking login status: {str(e)}")
            return False
    
    def build_search_url(self, 
                        keyword: str, 
                        location: str = "", 
                        experience: str = "",
                        salary: str = "") -> str:
        """
        Build search URL with parameters
        
        Args:
            keyword (str): Job title or keyword
            location (str): Job location
            experience (str): Experience level (e.g., "0-2", "2-5")
            salary (str): Salary range
            
        Returns:
            str: Formatted search URL
        """
        # Basic search URL format
        search_url = f"{self.base_url}/{keyword.replace(' ', '-')}-jobs"
        
        if location:
            search_url += f"-in-{location.replace(' ', '-')}"
        
        params = []
        if experience:
            params.append(f"experience={experience}")
        if salary:
            params.append(f"salary={salary}")
            
        if params:
            search_url += "?" + "&".join(params)
        
        return search_url
    
    def scroll_page(self, scroll_pause_time: float = 2.0, max_scrolls: int = 5):
        """
        Scroll the page to load dynamic content
        
        Args:
            scroll_pause_time (float): Time to wait between scrolls
            max_scrolls (int): Maximum number of scrolls
        """
        for i in range(max_scrolls):
            # Scroll to the bottom
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(scroll_pause_time)
            self.logger.info(f"Scrolled {i+1}/{max_scrolls} times")
    
    def extract_job_cards(self, deep_scrape: bool = False) -> List[Dict]:
        """
        Extract job information from job cards on the page
        
        Args:
            deep_scrape (bool): If True, visit each job page to get apply link
            
        Returns:
            List[Dict]: List of job dictionaries
        """
        jobs = []
        
        try:
            # Wait for job listings to load
            wait = WebDriverWait(self.driver, 10)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".srp-jobtuple-wrapper, .cust-job-tuple")))
            
            # Find all job cards - Naukri uses multiple class names for job cards
            job_cards = self.driver.find_elements(By.CSS_SELECTOR, ".srp-jobtuple-wrapper, .cust-job-tuple")
            self.logger.info(f"Found {len(job_cards)} job listings")
            
            for idx, card in enumerate(job_cards, 1):
                try:
                    job_info = self.extract_job_info(card, idx, deep_scrape=deep_scrape)
                    if job_info:
                        jobs.append(job_info)
                        if deep_scrape:
                            self.logger.info(f"Job {idx}: {job_info['title']} - Apply type: {job_info['apply_type']}")
                except Exception as e:
                    self.logger.warning(f"Error extracting job {idx}: {str(e)}")
                    continue
            
        except TimeoutException:
            self.logger.error("Timeout waiting for job listings to load")
        except Exception as e:
            self.logger.error(f"Error extracting job cards: {str(e)}")
        
        return jobs
    
    def get_apply_link(self, job_url: str) -> Dict[str, str]:
        """
        Visit job details page and extract apply link from the Apply button
        
        Args:
            job_url (str): URL of the job details page
            
        Returns:
            Dict: Dictionary with apply_link and apply_type
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
            
            # Try to find and extract apply link
            try:
                # Strategy 1: Look for "Apply on company site" button with direct link
                try:
                    external_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Apply on company site')] | //a[contains(text(), 'Apply on company site')]")
                    
                    # Check if it's an anchor tag with href
                    if external_btn.tag_name == 'a':
                        external_link = external_btn.get_attribute('href')
                        if external_link and 'naukri.com' not in external_link:
                            self.driver.close()
                            self.driver.switch_to.window(original_window)
                            return {
                                'apply_link': external_link,
                                'apply_type': 'external'
                            }
                    
                    # If it's a button, try to get the onclick URL
                    onclick = external_btn.get_attribute('onclick')
                    if onclick and 'http' in onclick:
                        # Extract URL from onclick
                        import re
                        urls = re.findall(r'https?://[^\'"]+', onclick)
                        if urls and 'naukri.com' not in urls[0]:
                            self.driver.close()
                            self.driver.switch_to.window(original_window)
                            return {
                                'apply_link': urls[0],
                                'apply_type': 'external'
                            }
                    
                    # Try clicking and capturing redirect
                    try:
                        # Get current URL
                        current_url_before = self.driver.current_url
                        
                        # Click the button
                        external_btn.click()
                        time.sleep(2)
                        
                        # Check if we were redirected or new window opened
                        if len(self.driver.window_handles) > 2:
                            # New window opened - switch to it
                            newest_window = [w for w in self.driver.window_handles if w not in [original_window, new_window]][0]
                            self.driver.switch_to.window(newest_window)
                            redirect_url = self.driver.current_url
                            self.driver.close()
                            self.driver.switch_to.window(new_window)
                            self.driver.close()
                            self.driver.switch_to.window(original_window)
                            
                            if 'naukri.com' not in redirect_url:
                                return {
                                    'apply_link': redirect_url,
                                    'apply_type': 'external'
                                }
                        elif self.driver.current_url != current_url_before:
                            # Same window redirected
                            redirect_url = self.driver.current_url
                            self.driver.close()
                            self.driver.switch_to.window(original_window)
                            
                            if 'naukri.com' not in redirect_url:
                                return {
                                    'apply_link': redirect_url,
                                    'apply_type': 'external'
                                }
                    except:
                        pass
                        
                except NoSuchElementException:
                    pass
                
                # Strategy 2: Look for regular "Apply" button
                try:
                    apply_btn = self.driver.find_element(By.ID, "apply-button")
                    
                    # Check if it's actually a link
                    if apply_btn.tag_name == 'a':
                        apply_link = apply_btn.get_attribute('href')
                        if apply_link:
                            self.driver.close()
                            self.driver.switch_to.window(original_window)
                            return {
                                'apply_link': apply_link,
                                'apply_type': 'naukri'
                            }
                except NoSuchElementException:
                    pass
                
                # If no apply link found, use the job details page URL
                current_url = self.driver.current_url
                self.driver.close()
                self.driver.switch_to.window(original_window)
                
                return {
                    'apply_link': current_url,
                    'apply_type': 'naukri' # Requires Naukri login/interaction
                }
                
            except Exception as e:
                self.logger.warning(f"Error extracting apply link: {str(e)}")
                self.driver.close()
                self.driver.switch_to.window(original_window)
                return {
                    'apply_link': job_url,
                    'apply_type': 'naukri'
                }
                
        except Exception as e:
            # If anything goes wrong, close extra windows and return original URL
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
                'apply_type': 'naukri'
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
        
        try:
            # Job Title and Link (combined in one element: <a class="title">)
            title_elem = card.find_element(By.CSS_SELECTOR, "a.title")
            job_data['title'] = title_elem.text.strip()
            
            # Get the job link - ensure it's complete
            job_link = title_elem.get_attribute('href')
            
            # Ensure the link is absolute
            if job_link and not job_link.startswith('http'):
                job_link = self.base_url + job_link
            
            job_data['job_details_url'] = job_link
            
            # Deep scrape: visit job page to get apply link
            if deep_scrape and job_link:
                apply_info = self.get_apply_link(job_link)
                job_data['apply_link'] = apply_info['apply_link']
                job_data['apply_type'] = apply_info['apply_type']
            else:
                # If not deep scraping, just use the job details URL
                job_data['apply_link'] = job_link
                job_data['apply_type'] = 'naukri'
            
        except NoSuchElementException:
            self.logger.warning(f"Could not find title/link for job {index}")
            return None
        
        # Company Name (optional fields from here)
        try:
            company_elem = card.find_element(By.CSS_SELECTOR, "a.comp-name")
            job_data['company'] = company_elem.text.strip()
        except NoSuchElementException:
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
        
        # Job Description/Skills
        try:
            desc_elem = card.find_element(By.CLASS_NAME, "job-desc")
            job_data['description'] = desc_elem.text.strip()
        except NoSuchElementException:
            job_data['description'] = "N/A"
        
        # Posted Date
        try:
            date_elem = card.find_element(By.CLASS_NAME, "job-post-day")
            job_data['posted_date'] = date_elem.text.strip()
        except NoSuchElementException:
            job_data['posted_date'] = "N/A"
        
        return job_data
    
    def scrape_jobs(self, 
                   keyword: str, 
                   location: str = "",
                   experience: str = "",
                   max_pages: int = 1,
                   scroll_count: int = 5,
                   deep_scrape: bool = False,
                   require_login: bool = False) -> List[Dict]:
        """
        Main scraping function
        
        Args:
            keyword (str): Job search keyword
            location (str): Job location
            experience (str): Experience level
            max_pages (int): Maximum number of pages to scrape
            scroll_count (int): Number of times to scroll per page
            deep_scrape (bool): If True, visit each job to extract apply link
            require_login (bool): If True, prompt user to login first
            
        Returns:
            List[Dict]: List of all scraped jobs
        """
        # Step 1: Handle login if required
        if require_login:
            login_success = self.wait_for_login(timeout=120)
            if not login_success:
                self.logger.error("Login failed or timed out - cannot proceed")
                print("\n✗ Scraping aborted: Login required but not completed.")
                return []
            print("\n" + "=" * 70)
            print("Starting job scraping...")
            print("=" * 70 + "\n")
        
        all_jobs = []
        
        for page in range(1, max_pages + 1):
            self.logger.info(f"Scraping page {page}/{max_pages}")
            
            # Build URL
            search_url = self.build_search_url(keyword, location, experience)
            if page > 1:
                search_url += f"&page={page}" if "?" in search_url else f"?page={page}"
            
            self.logger.info(f"Accessing URL: {search_url}")
            
            try:
                # Navigate to search page
                self.driver.get(search_url)
                time.sleep(3)  # Wait for initial load
                
                # Scroll to load more content
                self.scroll_page(scroll_pause_time=2.0, max_scrolls=scroll_count)
                
                # Extract jobs from current page
                page_jobs = self.extract_job_cards(deep_scrape=deep_scrape)
                all_jobs.extend(page_jobs)
                
                self.logger.info(f"Extracted {len(page_jobs)} jobs from page {page}")
                
                # Be polite - wait before next page
                if page < max_pages:
                    time.sleep(3)
                    
            except Exception as e:
                self.logger.error(f"Error scraping page {page}: {str(e)}")
                continue
        
        self.jobs_data = all_jobs
        return all_jobs
    
    def save_to_json(self, filename: str = None):
        """
        Save scraped jobs to JSON file
        
        Args:
            filename (str): Output filename (optional)
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"naukri_jobs_{timestamp}.json"
        
        # Ensure .json extension
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
    parser = argparse.ArgumentParser(description='Naukri.com Job Scraper')
    parser.add_argument('--keyword', '-k', required=True, help='Job search keyword (e.g., "Python Developer")')
    parser.add_argument('--location', '-l', default='', help='Job location (e.g., "Bangalore")')
    parser.add_argument('--experience', '-e', default='', help='Experience range (e.g., "2-5")')
    parser.add_argument('--pages', '-p', type=int, default=1, help='Number of pages to scrape (default: 1)')
    parser.add_argument('--output', '-o', help='Output JSON filename')
    parser.add_argument('--headless', action='store_true', help='Run browser in headless mode')
    parser.add_argument('--deep-scrape', action='store_true', help='Visit each job to extract apply link (slower but more accurate)')
    parser.add_argument('--login', action='store_true', help='Login to Naukri before scraping (required for actual apply links)')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("Naukri.com Job Scraper")
    print("=" * 60)
    print(f"Keyword: {args.keyword}")
    print(f"Location: {args.location or 'Any'}")
    print(f"Experience: {args.experience or 'Any'}")
    print(f"Pages: {args.pages}")
    print(f"Deep Scrape: {'Yes' if args.deep_scrape else 'No'}")
    print(f"Login Required: {'Yes' if args.login else 'No'}")
    print("=" * 60)
    
    # Note: Headless mode is incompatible with login
    if args.login and args.headless:
        print("\n⚠ Warning: Headless mode disabled because login requires visible browser.")
        args.headless = False
    
    scraper = NaukriScraper(headless=args.headless)
    
    try:
        # Scrape jobs
        jobs = scraper.scrape_jobs(
            keyword=args.keyword,
            location=args.location,
            experience=args.experience,
            max_pages=args.pages,
            deep_scrape=args.deep_scrape,
            require_login=args.login
        )
        
        print(f"\n✓ Successfully scraped {len(jobs)} jobs!")
        
        # Save to JSON
        scraper.save_to_json(args.output)
        
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        logging.error(f"Scraping failed: {str(e)}")
        
    finally:
        scraper.close()


if __name__ == "__main__":
    main()
