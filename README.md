# Naukri.com Job Scraper

A robust and customizable web scraper for extracting job listings from Naukri.com. This tool uses Selenium to scrape job details including titles, company names, locations, salaries, and direct job links, saving everything in a structured JSON format.

## Features

✅ **Comprehensive Data Extraction**
- Job titles and direct links
- Company names
- Location information
- Salary ranges
- Experience requirements
- Job descriptions
- Posted dates

✅ **Flexible Search Options**
- Search by keyword
- Filter by location
- Filter by experience level
- Multi-page scraping

✅ **Multiple Running Modes**
- Single search (CLI)
- Batch processing (config file)
- Headless or visible browser mode

✅ **Output Format**
- Clean JSON structure
- Metadata included
- Timestamped files
- Combined and individual results

## Installation

### Prerequisites
- Python 3.8 or higher
- Google Chrome browser
- ChromeDriver (automatically managed by webdriver-manager)

### Setup

1. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

That's it! The `webdriver-manager` will automatically download and manage ChromeDriver for you.

## Usage

### Method 1: Command Line Interface (Single Search)

Run a single search with custom parameters:

```bash
python naukri_scraper.py --keyword "Python Developer" --location "Bangalore" --pages 2
```

**Available Options:**
- `--keyword, -k`: Job search keyword (required)
- `--location, -l`: Job location (optional)
- `--experience, -e`: Experience range like "2-5" (optional)
- `--pages, -p`: Number of pages to scrape (default: 1)
- `--output, -o`: Custom output filename (optional)
- `--headless`: Run in headless mode (no visible browser)

**Examples:**

```bash
# Basic search
python naukri_scraper.py -k "Data Scientist" -l "Mumbai"

# With experience filter and multiple pages
python naukri_scraper.py -k "Full Stack Developer" -l "Hyderabad" -e "3-6" -p 3

# Headless mode with custom output
python naukri_scraper.py -k "DevOps Engineer" -l "Pune" -p 2 -o devops_jobs.json --headless
```

### Method 2: Batch Processing (Multiple Searches)

Edit `config.json` to define multiple searches, then run:

```bash
python batch_scraper.py
```

**Sample config.json:**
```json
{
  "search_configs": [
    {
      "name": "Python Developer Jobs",
      "keyword": "Python Developer",
      "location": "Bangalore",
      "experience": "",
      "max_pages": 2
    },
    {
      "name": "Data Scientist Jobs",
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

## Output Format

Jobs are saved in JSON format with the following structure:

```json
{
  "metadata": {
    "total_jobs": 50,
    "scraped_at": "2025-11-20T21:30:00",
    "source": "Naukri.com"
  },
  "jobs": [
    {
      "index": 1,
      "title": "Python Developer",
      "link": "https://www.naukri.com/job-listings-...",
      "company": "Tech Company Pvt Ltd",
      "experience": "2-5 years",
      "salary": "₹6-10 Lacs P.A.",
      "location": "Bangalore/Bengaluru",
      "description": "Skills: Python, Django, Flask...",
      "posted_date": "30+ Days Ago",
      "scraped_at": "2025-11-20T21:30:00"
    }
  ]
}
```

## Project Structure

```
naukri-web-scrapper/
├── naukri_scraper.py      # Main scraper class and CLI
├── batch_scraper.py       # Batch processing script
├── config.json            # Configuration for batch scraping
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── naukri_scraper.log    # Log file (auto-generated)
└── scraping_results_*/   # Output directories (auto-generated)
```

## How It Works

1. **Selenium WebDriver** launches Chrome and navigates to Naukri.com
2. **Search URL is built** based on your parameters
3. **Page scrolling** loads dynamic content
4. **Job cards are extracted** using CSS selectors
5. **Data is parsed** and cleaned
6. **Results are saved** to JSON files

## Best Practices

- **Rate Limiting**: The scraper includes delays to avoid overloading Naukri's servers
- **Headless Mode**: Use `--headless` for faster scraping without GUI
- **Batch Processing**: Use config.json for regular monitoring of multiple job types
- **Error Handling**: Logs are saved to `naukri_scraper.log` for debugging

## Troubleshooting

### Chrome/ChromeDriver Issues
If you encounter ChromeDriver errors, the webdriver-manager should handle it automatically. If issues persist:
```bash
pip install --upgrade webdriver-manager
```

### No Jobs Found
- Check if Naukri.com structure has changed
- Try running without `--headless` to see what's happening
- Check the log file: `naukri_scraper.log`

### Timeout Errors
- Increase wait times in the code
- Check your internet connection
- Naukri might be blocking automated access (try reducing frequency)

## Ethical Considerations

- **Respect robots.txt**: Check Naukri's robots.txt file
- **Rate limiting**: Don't scrape too aggressively
- **Terms of Service**: Review Naukri's ToS regarding data scraping
- **Personal use**: This tool is for personal job search assistance

## Future Enhancements

Potential improvements:
- [ ] Support for more filters (job type, salary range)
- [ ] Email notifications for new jobs
- [ ] Database integration
- [ ] GUI interface
- [ ] Support for other job portals

## License

This project is for educational and personal use only.

## Support

For issues or questions, check the log file (`naukri_scraper.log`) for detailed error messages.

---

**Happy Job Hunting! 🚀**
