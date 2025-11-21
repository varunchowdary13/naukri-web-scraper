# Naukri.com Job Scraper (Last 24 Hours)

A robust and customizable web scraper for extracting the **latest job listings (last 24 hours)** from Naukri.com. 

## Features

✅ **Latest Jobs Only**: Automatically filters for jobs posted in the last 24 hours.
✅ **Smart Sorting**: Sorts jobs by "Date" on the website AND performs a local sort to ensure "Just now" jobs appear first.
✅ **Deep Scraping**: Visits each job page to extract the full description and direct apply link.
✅ **No Login Required**: Scrapes publicly available job data without needing a Naukri account.
✅ **Clean Extraction**: Gets the direct job link without clicking "Apply" buttons or opening external sites.
✅ **Output**: Saves results in a structured JSON format.

## Installation

1. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

## Usage

### Method 1: Command Line Interface (Single Search)

Run a single search with custom parameters:

```bash
python naukri_scraper.py --keyword "Python Developer" --location "Bangalore" --max-jobs 20 --deep-scrape
```

**Available Options:**
- `--keyword, -k`: Job search keyword (required)
- `--location, -l`: Job location (optional)
- `--experience, -e`: Experience range like "2-5" (optional)
- `--max-jobs, -m`: Maximum jobs to scrape (default: 40)
- `--deep-scrape`: Visit each job page to extract full description (recommended)
- `--output, -o`: Custom output filename (optional)
- `--headless`: Run in headless mode (no visible browser)

### Method 2: Batch Processing (Config File)

Edit `config.json` to define your search, then run:

```bash
python batch_scraper.py
```

**Sample config.json:**
```json
{
    "job_search": {
        "name": "Data Scientist Jobs",
        "keyword": "Data Scientist",
        "location": "Mumbai",
        "experience": "2-5",
        "max_jobs": 10
    },
    "scraper_settings": {
        "headless": false,
        "deep_scrape": true
    }
}
```

## Output Format

Jobs are saved in JSON format:

```json
{
  "metadata": {
    "total_jobs": 10,
    "scraped_at": "2025-11-21T22:00:00",
    "source": "Naukri.com"
  },
  "jobs": [
    {
      "index": 1,
      "job_id": 1234567890,
      "title": "Python Developer",
      "company": "Tech Corp",
      "experience": "2-5 Yrs",
      "salary": "Not Disclosed",
      "location": "Bangalore",
      "posted_date": "Just now",
      "description": "Full job description...",
      "apply_link": "https://www.naukri.com/job-listings...",
      "apply_type": "naukri"
    }
  ]
}
```

## Project Structure

- `naukri_scraper.py`: Main scraper script.
- `batch_scraper.py`: Script to run from config.
- `config.json`: Configuration file.
- `requirements.txt`: Dependencies.

## Disclaimer

This tool is for educational and personal use only. Respect Naukri.com's Terms of Service and robots.txt.
