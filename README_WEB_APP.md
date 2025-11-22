# Naukri Job Scraper Web Application

This is a modern web interface for the Naukri Job Scraper, built with Angular (Frontend) and Flask (Backend).

## Prerequisites

- Python 3.8+
- Node.js 18+ and npm

## Project Structure

- `backend/`: Flask API server
- `frontend/`: Angular application
- `naukri_scraper.py`: Core scraping logic
- `batch_scraper.py`: Batch processing script

## Setup & Running

### 1. Start the Backend Server

The backend handles the scraping logic and serves data to the frontend.

```bash
# Open a terminal
cd "c:\Users\gurra\job related applications\naukri web scrapper custom built"

# Install dependencies (if not already done)
pip install -r backend/requirements.txt

# Run the server
python backend/app.py
```

The backend will start at `http://localhost:5000`.

### 2. Start the Frontend Application

The frontend provides the user interface.

```bash
# Open a NEW terminal
cd "c:\Users\gurra\job related applications\naukri web scrapper custom built\frontend"

# Install dependencies (first time only)
npm install

# Run the development server
npm start
```

The application will be available at `http://localhost:4200`.

## Features

- **Modern UI**: Dark mode, responsive design, and smooth animations.
- **Configurable Search**: Set keywords, location, experience, max jobs, sort order, and freshness.
- **Real-time Progress**: Visual progress bar and status updates during scraping.
- **Results Table**: Sortable and clickable job listings.
- **Direct Links**: One-click access to job postings.

## Notes

- The scraper runs in a background thread to keep the UI responsive.
- Scraped data is saved to `scrapped_job_details.json` in the root directory.
- Ensure you have a stable internet connection for scraping.
