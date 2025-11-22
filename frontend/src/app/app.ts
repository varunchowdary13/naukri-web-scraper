import { Component, OnInit, OnDestroy, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient, HttpClientModule } from '@angular/common/http';
import { interval, Subscription } from 'rxjs';

interface JobSearchParams {
  keyword: string;
  location: string;
  experience: number | string;
  max_jobs: number | string;
  sort_by: string;
  freshness: number | string;
}

interface Job {
  index: number;
  job_id: string;
  title: string;
  company: string;
  experience: string;
  salary: string;
  location: string;
  posted_date: string;
  job_url: string;
  apply_link?: string;
  apply_type?: string;
  full_description?: string;
}

interface ScrapingStatus {
  state: 'idle' | 'running' | 'completed' | 'failed';
  progress: number;
  message: string;
  last_updated: string | null;
  error?: string;
}

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, FormsModule, HttpClientModule],
  templateUrl: './app.html',
  styleUrls: ['./app.css']
})
export class AppComponent implements OnInit, OnDestroy {
  title = 'Naukri Job Scraper';

  // API Base URL
  private apiUrl = 'http://localhost:5000/api';

  // Form Data
  searchParams: JobSearchParams = {
    keyword: '',
    location: '',
    experience: '',
    max_jobs: '',
    sort_by: 'date',
    freshness: ''
  };

  // Freshness options
  freshnessOptions = [1, 3, 7, 15, 30];

  // Sort options
  sortOptions = ['date', 'relevance'];

  // Status tracking
  scrapingStatus: ScrapingStatus = {
    state: 'idle',
    progress: 0,
    message: '',
    last_updated: null
  };

  // Results
  jobs: Job[] = [];
  metadata: any = null;

  // UI State
  showResults = false;
  errorMessage = '';
  successMessage = '';

  // Polling subscription
  private statusPolling?: Subscription;

  constructor(private http: HttpClient, private cdr: ChangeDetectorRef) { }

  ngOnInit() {
    // Do NOT load existing results automatically
    // this.loadResults(); 
  }

  ngOnDestroy() {
    // Clean up polling subscription
    if (this.statusPolling) {
      this.statusPolling.unsubscribe();
    }
  }

  // Check if form is valid
  isFormValid(): boolean {
    return !!(
      this.searchParams.keyword &&
      this.searchParams.location &&
      this.searchParams.experience !== '' &&
      this.searchParams.max_jobs !== '' &&
      this.searchParams.sort_by &&
      this.searchParams.freshness !== ''
    );
  }

  // Start scraping
  startScraping() {
    this.errorMessage = '';
    this.successMessage = '';

    // Clear previous results immediately
    this.jobs = [];
    this.showResults = false;
    this.metadata = null;

    if (!this.isFormValid()) {
      this.errorMessage = 'Please fill in all required fields';
      return;
    }

    // Convert to proper types
    const params = {
      keyword: this.searchParams.keyword,
      location: this.searchParams.location,
      experience: Number(this.searchParams.experience),
      max_jobs: Number(this.searchParams.max_jobs),
      sort_by: this.searchParams.sort_by,
      freshness: Number(this.searchParams.freshness)
    };

    // Set UI to running immediately for instant feedback
    this.scrapingStatus = {
      state: 'running',
      progress: 0,
      message: 'Starting scraper...',
      last_updated: new Date().toISOString()
    };

    this.http.post(`${this.apiUrl}/scrape`, params).subscribe({
      next: (response: any) => {
        if (response.success) {
          this.successMessage = 'Scraping started successfully!';
          this.startStatusPolling();
        } else {
          this.scrapingStatus.state = 'idle';
          this.errorMessage = response.message || 'Failed to start scraping';
        }
      },
      error: (error) => {
        this.scrapingStatus.state = 'idle';
        this.errorMessage = error.error?.message || 'Failed to start scraping';
        console.error('Scraping error:', error);
      }
    });
  }

  // Poll for status updates
  startStatusPolling() {
    // Poll every 2 seconds
    this.statusPolling = interval(2000).subscribe(() => {
      this.http.get<ScrapingStatus>(`${this.apiUrl}/status`).subscribe({
        next: (status) => {
          this.scrapingStatus = status;

          // If scraping completed, load results and stop polling
          if (status.state === 'completed') {
            this.loadResults();
            if (this.statusPolling) {
              this.statusPolling.unsubscribe();
            }
          } else if (status.state === 'failed') {
            this.errorMessage = status.message || 'Scraping failed';
            if (this.statusPolling) {
              this.statusPolling.unsubscribe();
            }
          }
        },
        error: (error) => {
          console.error('Status polling error:', error);
        }
      });
    });
  }

  // Load results from backend
  loadResults() {
    console.log('Loading results...');
    this.http.get(`${this.apiUrl}/results`).subscribe({
      next: (response: any) => {
        console.log('Results response:', response);
        if (response.success) {
          this.jobs = response.data.jobs || [];
          this.metadata = response.data.metadata || null;
          this.showResults = true;
          console.log('Jobs loaded:', this.jobs.length);

          // Force change detection
          this.cdr.detectChanges();
        }
      },
      error: (error) => {
        console.error('Error loading results:', error);
      }
    });
  }

  // Open job link in new tab
  openJobLink(url: string | undefined) {
    console.log('Opening URL:', url);
    if (url && url.trim() !== '') {
      window.open(url, '_blank');
    } else {
      console.warn('Cannot open link: URL is empty or undefined');
    }
  }

  // Format date
  formatDate(dateStr: string): string {
    if (!dateStr || dateStr === 'N/A') return dateStr;
    try {
      const date = new Date(dateStr);
      return date.toLocaleString();
    } catch {
      return dateStr;
    }
  }

  // Clear messages
  clearMessages() {
    this.errorMessage = '';
    this.successMessage = '';
  }
}
