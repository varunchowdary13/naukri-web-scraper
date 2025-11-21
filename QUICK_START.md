# Quick Start Guide - Naukri Web Scraper

## 🚀 Getting Started in 3 Steps

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```
✅ **COMPLETED** - Dependencies are already installed!

---

### Step 2: Choose Your Method

#### **Option A: Quick Single Search (Recommended for First Time)**

Run a simple search with command line:

```bash
python naukri_scraper.py --keyword "Python Developer" --location "Bangalore" --pages 1
```

**More Examples:**

```bash
# Search for Data Scientists in Mumbai (2 pages)
python naukri_scraper.py -k "Data Scientist" -l "Mumbai" -p 2

# Search with experience filter
python naukri_scraper.py -k "Full Stack Developer" -l "Hyderabad" -e "2-5" -p 2

# Run in headless mode (faster, no browser window)
python naukri_scraper.py -k "DevOps Engineer" -l "Pune" -p 1 --headless

# Custom output filename
python naukri_scraper.py -k "Java Developer" -l "Noida" -o my_jobs.json
```

#### **Option B: Batch Processing (Multiple Searches at Once)**

1. Edit `config.json` to add your search queries
2. Run: `python batch_scraper.py`

Example config.json:
```json
{
  "search_configs": [
    {
      "name": "Python Jobs Bangalore",
      "keyword": "Python Developer",
      "location": "Bangalore",
      "experience": "",
      "max_pages": 2
    },
    {
      "name": "Data Science Mumbai",
      "keyword": "Data Scientist",
      "location": "Mumbai",
      "experience": "2-5",
      "max_pages": 1
    }
  ],
  "scraper_settings": {
    "headless": true,
    "scroll_count": 5
  }
}
```

---

### Step 3: View Results

Results are saved as JSON files:

- **Single search**: `naukri_jobs_YYYYMMDD_HHMMSS.json` (or your custom filename)
- **Batch processing**: Saved in `scraping_results_YYYYMMDD_HHMMSS/` directory

**Sample Output Structure:**
```json
{
  "metadata": {
    "total_jobs": 45,
    "scraped_at": "2025-11-20T21:30:00",
    "source": "Naukri.com"
  },
  "jobs": [
    {
      "index": 1,
      "title": "Senior Python Developer",
      "link": "https://www.naukri.com/job-listings-...",
      "company": "TechCorp India Pvt Ltd",
      "experience": "3-6 years",
      "salary": "₹8-15 Lacs P.A.",
      "location": "Bangalore/Bengaluru",
      "description": "Required Skills: Python, Django, REST APIs...",
      "posted_date": "2 Days Ago",
      "scraped_at": "2025-11-20T21:30:00.123456"
    }
  ]
}
```

---

## 📋 Command Line Options

| Option | Short | Description | Required | Example |
|--------|-------|-------------|----------|---------|
| `--keyword` | `-k` | Job search keyword | ✅ Yes | `"Python Developer"` |
| `--location` | `-l` | Job location | ❌ No | `"Bangalore"` |
| `--experience` | `-e` | Experience range | ❌ No | `"2-5"` |
| `--pages` | `-p` | Number of pages | ❌ No (default: 1) | `2` |
| `--output` | `-o` | Custom filename | ❌ No | `"jobs.json"` |
| `--headless` | - | Run without GUI | ❌ No | (flag only) |

---

## 🧪 Test the Scraper

Run the test script to verify everything works:

```bash
python test_scraper.py
```

This will:
- Open Chrome browser (visible mode)
- Search for Python Developer jobs in Bangalore
- Scrape 1 page
- Save results to `test_results.json`

---

## 💡 Tips & Best Practices

### 1. **Start Small**
- Begin with 1-2 pages to test
- Use visible browser mode first (no `--headless`) to see what happens

### 2. **Avoid Getting Blocked**
- Don't scrape too many pages at once
- Use delays between requests (built-in)
- Don't run the scraper too frequently

### 3. **Optimize for Speed**
- Use `--headless` mode once you're confident it works
- Batch process during off-peak hours

### 4. **Data Quality**
- Some fields might be "N/A" if not available on job listing
- Job links are the most reliable data point
- Always check a few results manually

---

## 🐛 Troubleshooting

### "ChromeDriver not found"
**Solution:** The webdriver-manager should handle this automatically. If issues persist:
```bash
pip install --upgrade webdriver-manager
```

### "No jobs found"
**Possible causes:**
1. Naukri.com might have changed their HTML structure
2. Search returned no results
3. Connection issues

**Solution:** Run without `--headless` to see what's happening

### "Timeout errors"
**Causes:**
- Slow internet connection
- Naukri is blocking automated access

**Solution:**
- Try again later
- Reduce the number of pages
- Check your internet connection

### "Module not found"
**Solution:**
```bash
pip install -r requirements.txt
```

---

## 📁 Project Files

```
├── naukri_scraper.py      # Main scraper (CLI mode)
├── batch_scraper.py       # Batch processing script
├── test_scraper.py        # Test script
├── config.json            # Configuration for batch mode
├── requirements.txt       # Python dependencies
├── README.md             # Full documentation
├── QUICK_START.md        # This file
└── .gitignore            # Git ignore rules
```

---

## 🎯 Common Use Cases

### Use Case 1: Daily Job Monitoring
```bash
# Run every morning
python naukri_scraper.py -k "Your Job Title" -l "Your City" -p 3 --headless
```

### Use Case 2: Multiple Job Roles
```bash
# Use batch_scraper.py with config.json
python batch_scraper.py
```

### Use Case 3: Specific Company Jobs
```bash
# Search with company name in keyword
python naukri_scraper.py -k "Python Developer Google" -l "Bangalore" -p 2
```

---

## ⚖️ Legal & Ethical Notes

- ✅ For **personal use** only
- ✅ Respect Naukri.com's **Terms of Service**
- ✅ Don't overload their servers
- ✅ Use reasonable delays and rate limiting
- ❌ Don't resell or republish scraped data
- ❌ Don't scrape personal/sensitive information

---

## 🎉 You're Ready!

Try your first search:
```bash
python naukri_scraper.py -k "Your Dream Job" -l "Your City" -p 1
```

**Happy Job Hunting! 🚀**

---

## 📞 Need Help?

1. Check `naukri_scraper.log` for detailed error messages
2. Review the full `README.md` for detailed documentation
3. Try the test script: `python test_scraper.py`
