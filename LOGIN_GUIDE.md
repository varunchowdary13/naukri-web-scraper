# Naukri Web Scraper - Enhanced with Login Feature

## 🆕 NEW FEATURE: User Login

The scraper now supports **interactive login** to access actual apply links!

### Why Login?

Without login, Naukri shows "Login to Apply" instead of the real application link. By logging in first, you get:
- ✅ **Actual apply links** (not just "Login to Apply")
- ✅ **External application URLs** for jobs that redirect to company websites
- ✅ **Direct access** to the application process

---

## Usage Examples

### Basic Usage (No Login)
```bash
python naukri_scraper.py -k "Data Scientist" -l "Mumbai" -p 1
```
Result: Gets job details URLs, but shows "naukri" as apply type (requires login)

### With Login (Recommended)
```bash
python naukri_scraper.py -k "Data Scientist" -l "Mumbai" -p 1 --login
```

**What happens:**
1. 🌐 Browser opens to Naukri login page
2. ⏱️ You have 2 minutes to login (manual login using any method)
3. ✅ Scraper detects when you're logged in
4. 🚀 Scraping begins automatically after successful login

### With Login + Deep Scrape
```bash
python naukri_scraper.py -k "Python Developer" -l "Bangalore" -p 2 --login --deep-scrape
```

This is the **most powerful mode**:
- Logs you in first
- Visits each job posting
- Extracts the actual apply link
- Creates comprehensive JSON output

---

## Login Process

### Step 1: Command Execution
Run with `--login` flag:
```bash
python naukri_scraper.py -k "Your Job Title" -l "Your City" --login -p 1
```

### Step 2: Login Page Opens
```
======================================================================
USER LOGIN REQUIRED
======================================================================
Opening Naukri login page...
Please login using your credentials (username/password or Google)
You have 120 seconds (2 minutes) to complete login.
The scraper will automatically detect when you're logged in.
======================================================================

Waiting for login... (115 seconds remaining)
```

### Step 3: You Login Manually
Choose any method:
- 📧 Email/Password
- 🔑 Google Sign-In
- 📱 OTP/Phone Login

### Step 4: Auto-Detection
The scraper checks every 5 seconds for successful login.

### Step 5: Scraping Starts
```
✓ Login successful! Proceeding with scraping...

======================================================================
Starting job scraping...
======================================================================
```

---

## Complete Command Options

```bash
python naukri_scraper.py \
  --keyword "Job Title" \        # Required: Job search keyword
  --location "City" \            # Optional: Job location
  --experience "2-5" \           # Optional: Years of experience
  --pages 2 \                    # Optional: Number of pages (default: 1)
  --output my_jobs.json \        # Optional: Custom output filename
  --login \                      # Optional: Login before scraping
  --deep-scrape \                # Optional: Visit each job for apply link
  --headless                     # Optional: Run without GUI (not compatible with --login)
```

---

## Output Format

### Without Login
```json
{
  "title": "Data Scientist",
  "company": "TechCorp",
  "job_details_url": "https://www.naukri.com/job-listings-...",
  "apply_link": "https://www.naukri.com/job-listings-...",
  "apply_type": "naukri"
}
```

### With Login
```json
{
  "title": "Data Scientist",
  "company": "TechCorp",
  "job_details_url": "https://www.naukri.com/job-listings-...",
  "apply_link": "https://careers.techcorp.com/apply/12345",
  "apply_type": "external"
}
```
OR
```json
{
  "apply_link": "https://www.naukri.com/job-listings-...-complete-with-sid",
  "apply_type": "naukri"
}
```

---

## Important Notes

### ⚠️ Login + Headless Mode
You **cannot** use `--login` with `--headless` because you need to see the browser to login manually. The scraper will automatically disable headless mode if both are specified.

### ⏱️ Timeout
- You have **2 minutes (120 seconds)** to complete login
- The scraper checks every **5 seconds** for successful login
- If you don't login in time, scraping is aborted

### 🔒 Security
- Your credentials are **never stored** by the scraper
- You login manually in your own browser
- The scraper only detects when login is complete

### 🚀 Performance
- Login is checked every 5 seconds (minimal overhead)
- Once logged in, scraping proceeds normally
- No additional delays added to scraping process

---

## Recommended Workflows

### For Quick Jobs (Without Login)
```bash
python naukri_scraper.py -k "Python Developer" -l "Bangalore" -p 1 --headless
```
Fast, gets basic job info and Naukri links.

### For Serious Job Hunting (With Login)
```bash
python naukri_scraper.py -k "Data Scientist" -l "Mumbai" -p 3 --login --deep-scrape
```
Slower, but gets actual apply links and complete information.

### For Daily Monitoring
1. Use batch_scraper.py with login enabled
2. Set up multiple searches in config.json
3. Run once per day to track new postings

---

## Troubleshooting

### "Login timeout!"
**Cause:** You didn't complete login within 2 minutes.
**Solution:** Run again and login faster, or use a faster internet connection.

### "Login required but not completed"
**Cause:** Login timed out or failed.
**Solution:** Check your credentials and try again.

### Browser hangs after login
**Cause:** Login detection might have failed.
**Solution:** Wait a few more seconds, or press Ctrl+C and try again.

---

## Next Steps

Try the login feature now:
```bash
python naukri_scraper.py -k "Your Job Title" -l "Your City" --login -p 1
```

Happy job hunting! 🎯
