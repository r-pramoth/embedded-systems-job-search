# Embedded Systems Job Discovery Automation

[![Python 3.11](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)](scripts/job_search.py)
[![GitHub Actions](https://img.shields.io/badge/Automation-GitHub_Actions-2088FF?logo=githubactions&logoColor=white)](.github/workflows/job-search.yml)

A Python automation project for discovering potentially relevant **embedded systems, firmware and graduate engineering opportunities**. It combines RSS collection, page enrichment, URL deduplication, heuristic relevance scoring and Markdown reporting.

[Read the source](scripts/job_search.py) · [Inspect the workflow](.github/workflows/job-search.yml) · [Browse result issues](https://github.com/r-pramoth/embedded-systems-job-search/issues) · [Review the regression tests](tests/test_job_search.py)

## How it works

1. Run role-, location- and company-specific queries against Google News RSS.
2. Parse titles, URLs, descriptions, sources and publication dates.
3. Deduplicate URLs and attempt to fetch linked pages.
4. Extract potential location, salary, experience and embedded-technology matches.
5. Filter results and rank them using keyword, company, location and freshness heuristics.
6. Write up to 30 ranked entries to `job_results.md`.
7. Optionally deliver the report to Telegram. The GitHub Actions workflow also uploads the report as an artifact and creates a results issue.

## What this demonstrates

| Area | Implementation |
| --- | --- |
| Data ingestion | HTTP requests, RSS/XML parsing and publication-date handling |
| Processing | Text cleaning, regular expressions and URL normalization |
| Ranking | Transparent keyword and freshness scoring |
| Reporting | Markdown generation and Telegram HTML conversion |
| Automation | Scheduled / manual GitHub Actions runs, artifacts and result issues |

## Run locally

Requires Python 3.11, matching the workflow. The script uses the Python standard library; no third-party Python packages are required.

```bash
git clone https://github.com/r-pramoth/embedded-systems-job-search.git
cd embedded-systems-job-search
python scripts/job_search.py
```

The report is written to `job_results.md` in the current directory. With Telegram environment variables unset, the script skips delivery and prints a configuration message.

Network calls cover many queries and linked pages, so runtime depends on source availability and timeouts.

## Verify the implementation

Run the offline suite from the repository root:

```bash
python -m unittest discover -s tests -v
```

The suite uses fictional fixtures and mocked HTTP responses. It blocks network requests and never runs the search scheduler or sends Telegram messages.

Regression coverage includes:

- Preserving experience ranges starting at zero, including `0–2 years`.
- Checking the lower bound of a complete experience range.
- Keeping `architecture` distinct from the senior role `architect`.
- Avoiding substring matches such as `spi` in `hospital` or `Intel` in `intelligent`.
- Keeping an unknown employer separate from the RSS publisher.
- Parsing a mocked RSS feed and exercising filtering through report generation.

[The CI workflow](.github/workflows/ci.yml) runs these checks on Python 3.11 and 3.12 for relevant pull requests and pushes to `main`. It uses read-only repository permissions and does not receive the Telegram secrets.

## GitHub Actions setup

1. Fork the repository and enable Actions in the fork.
2. To use Telegram, configure `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` as repository Actions secrets. Keep their values out of source files and logs.
3. Ensure repository policy permits the workflow's declared `contents: read` and `issues: write` permissions.
4. Open **Actions → Daily Embedded Systems Fresher Job Search → Run workflow**.
5. Inspect the logs, download the report artifact or open the resulting GitHub Issue.

Running the workflow creates a results issue. With Telegram credentials configured, it also sends report messages.

### Configured triggers

| Trigger | Behavior |
| --- | --- |
| `0 2 * * *` | Daily search at 02:00 UTC / 07:30 IST |
| `*/5 * * * *` | Poll Telegram for an authorized `/start` request; search only when requested |
| `workflow_dispatch` | Manual search |

These are the triggers defined in the workflow; successful delivery depends on Actions, network access and any configured Telegram credentials.

## Repository map

| File | Purpose |
| --- | --- |
| [scripts/job_search.py](scripts/job_search.py) | Collection, extraction, filtering, scoring, report generation and optional Telegram delivery |
| [.github/workflows/job-search.yml](.github/workflows/job-search.yml) | Scheduling, Telegram polling, artifact upload and results-issue creation |
| [tests/test_job_search.py](tests/test_job_search.py) | Offline regression tests with fictional fixtures |
| [.github/workflows/ci.yml](.github/workflows/ci.yml) | Read-only regression checks on Python 3.11 and 3.12 |

## Customize

Edit `scripts/job_search.py` to change:

- `SEARCH_QUERIES` and `PRIORITY_COMPANIES` for discovery queries.
- `EMBEDDED_KEYWORDS`, `FRESHER_KEYWORDS` and `SENIOR_KEYWORDS` for relevance heuristics.
- `score_result()` for ranking weights.
- `create_report()` for report size and presentation.

Edit `.github/workflows/job-search.yml` to change schedules or output handling. Keep schedule comparisons in the workflow consistent with any cron changes.

## Current limitations

- Discovery uses **Google News RSS**, rather than direct integrations with job boards or employer career portals.
- Returned links may lead to articles or RSS redirects rather than employer application pages.
- Publication dates describe source items and may differ from vacancy posting dates.
- Keyword-based company, location, salary and experience extraction can still misclassify results. Matching complete terms avoids some substring errors but does not verify the original vacancy.
- Seniority filtering uses the minimum of a numeric experience range. A minimum below two years is not itself rejected by this filter, so a surviving result is not proof of eligibility for zero-experience applicants.
- Freshness affects ranking; it does not guarantee that a vacancy is recent or still accepting applications.
- Salary is extracted when present; the script does not enforce a minimum salary or verify visa sponsorship.
- Individual source failures can yield a partial or empty report without failing the entire run.
- Email delivery is not implemented.

Verify eligibility, employer identity and application status at the original employer source before applying.
