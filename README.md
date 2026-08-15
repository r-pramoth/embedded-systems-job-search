# Embedded Systems Fresher Job Search

Automated daily job search for Embedded Systems entry-level positions in India and internationally.

## How It Works

- **Frequency:** Daily at 7:30 AM IST (2:00 AM UTC)
- **Search Criteria:** Freshers/0-years experience, ₹1 lakh/month salary preference
- **Coverage:** India + International opportunities with visa sponsorship info
- **Output:** Job listings with company details, requirements, and direct apply links

## Results

Results are published in multiple places:

1. **GitHub Actions Artifacts** — Download results directly
2. **Email Notifications** — Sent to configured email address
3. **GitHub Issues** — Automatically created for each search

## Customization

Edit `scripts/job_search.py` to modify:
- Salary preference
- Target roles
- Technologies to prioritize
- Search scope

Edit `.github/workflows/job-search.yml` to modify:
- Schedule time (cron expression)
- Notification settings
- Result storage

## Setup

See `GITHUB_SETUP_GUIDE.md` for detailed setup instructions.
