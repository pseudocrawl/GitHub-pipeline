# GitHub SaaS Tool Analytics Pipeline

An automated data pipeline that tracks 150+ developer tools and SaaS repositories daily, measuring growth, health, and momentum using the GitHub REST API.

**[View Live Dashboard](https://datastudio.google.com/reporting/24164e5c-beba-4de8-b925-d87e3af32703)**

---

## What This Does

Every morning, this pipeline automatically:

1. Pulls fresh data for 150+ SaaS and developer tool repositories from the GitHub API
2. Loads raw data into BigQuery with partitioning and idempotency checks
3. Transforms and tests the data using dbt
4. Updates a live Looker Studio dashboard, no manual intervention required

The result is a continuously growing time series that tracks which tools are gaining real adoption vs. riding temporary hype.

---

## Architecture

```
GitHub REST API
      ↓
Python Scraper (fetch_repos.py + scraper.py)
      ↓
BigQuery (raw dataset partitioned by month, idempotent loads)
      ↓
dbt (staging + mart models, tested, documented)
      ↓
Looker Studio (live dashboard)
      ↑
Apache Airflow (orchestrates the full pipeline at scheduled time)
```

---

## Tech Stack

| Layer | Tool |
|---|---|
| Data collection | Python, GitHub REST API |
| Cloud warehouse | Google BigQuery |
| Transformation | dbt (staging + mart models) |
| Orchestration | Apache Airflow 3.2 |
| Visualization | Looker Studio |
| Version control | Git + GitHub |

---

## Project Structure

```
github-pipeline/
├── fetch_repos.py          # Discovers repos via GitHub search API (fork + star filters)
├── scraper.py              # Pulls daily metadata for each tracked repo
├── load_to_bigquery.py     # Loads to BigQuery with idempotency + month partitioning
├── pipeline.py             # Combines scraper + loader into one callable function
├── dags/
│   └── github_pipeline_dag.py   # Airflow DAG — runs pipeline + dbt daily
└── github_analytics/            # dbt project
    └── models/
        ├── staging/
        │   └── stg_github_repos.sql        # Cleans raw data, casts types
        └── marts/
            ├── repo_growth.sql             # Daily star growth per repo (LAG window function)
            ├── repo_health_score.sql       # Composite health score (stars, forks, commits, issues)
            ├── repo_health_score_latest.sql # Latest snapshot per repo (for dashboard)
            └── repo_activity_level.sql     # Repos segmented by commit activity tier
```

---

## Key Design Decisions

**Automated repo discovery**
Instead of a hardcoded list, `fetch_repos.py` queries GitHub's search API across 7 SaaS categories using both star count and fork thresholds, eliminating artificially hyped repositories with inflated stars but no real adoption.

**Idempotent loads**
Before inserting, the loader checks whether today's data already exists in BigQuery. If the pipeline runs twice in one day, the second run skips cleanly; no duplicate rows, no data corruption.

**Month partitioning**
The raw BigQuery table is partitioned by `scraped_at` month. This means queries only scan the relevant partition instead of the full table, cheaper and faster as the dataset grows.

**Two-layer dbt models**
`repo_health_score` keeps the full time series (one row per repo per day) for trend analysis. `repo_health_score_latest` snapshots only the most recent row per repo for leaderboard-style views. Different use cases, different tables, not one overloaded table trying to do both.

**Health score formula**
A composite 0–100 score weighted across four signals:
- Commit activity (40%) | most important signal of genuine maintenance
- Stars (30%) | community awareness
- Forks (20%) | real adoption by other developers
- Open issue health (10%) | proxy for team responsiveness

---

## Data Quality

- dbt tests enforce `not_null` on critical columns (`repo_name`, `stars`)
- Suspicious repos (very high stars, very low forks) are flagged and filtered from dashboard views
- GitHub's `open_issues_count` field includes pull requests, this is noted in the dashboard as a known API behavior

---

## Running Locally

**Requirements:** Python 3.8+, Google Cloud account, GitHub personal access token

```bash
# Clone and set up environment
git clone https://github.com/pseudocrawl/GitHub-pipeline
cd GitHub-pipeline
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Add credentials
cp .env.example .env
# Fill in GITHUB_TOKEN and GCP project details

# Run the pipeline once
python pipeline.py

# Run dbt transformations
cd github_analytics
dbt run
dbt test
```

**For orchestration:** Install Airflow, copy the DAG file to `~/airflow/dags/`, and run `airflow standalone`.

---

## Dashboard

The live dashboard updates daily and includes:

- Top 20 repositories by stars and forks
- Language distribution across the tracked ecosystem
- Stars vs forks scatter (hype vs real adoption)
- Star growth over time
- Activity tier comparison (high / medium / low commit activity vs health score)
- KPI tiles: total unique repos tracked, average health score, total stars and total forks

**[Open Dashboard](https://datastudio.google.com/reporting/24164e5c-beba-4de8-b925-d87e3af32703)**

---

## What's Next

- 30+ days of data will enable meaningful trend analysis and momentum scoring
- Scheduled Airflow runs on a cloud VM for continuous unattended operation
- Additional categories: security tools, API frameworks, observability platforms