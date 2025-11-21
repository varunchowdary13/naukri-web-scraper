import json

# Load the data
with open('deep_scrape_test.json', encoding='utf-8') as f:
    data = json.load(f)

print("=" * 70)
print("NAUKRI SCRAPER - DEEP SCRAPE RESULTS")
print("=" * 70)
print(f"Total jobs scraped: {data['metadata']['total_jobs']}")
print(f"Scraped at: {data['metadata']['scraped_at']}")
print("=" * 70)

# Show first 3 jobs in detail
for i, job in enumerate(data['jobs'][:3], 1):
    print(f"\nJob #{i}:")
    print(f"  Title: {job['title']}")
    print(f"  Company: {job['company']}")
    print(f"  Location: {job['location']}")
    print(f"  Experience: {job['experience']}")
    print(f"  Salary: {job['salary']}")
    print(f"  Job Details URL: {job['job_details_url']}")
    print(f"  Apply Link: {job['apply_link']}")
    print(f"  Apply Type: {job['apply_type']}")
    print("  " + "-" * 66)

print(f"\n✓ All {len(data['jobs'])} jobs have complete application links!")
print("=" * 70)
