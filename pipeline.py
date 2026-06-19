import os
from scraper import scrape_all
from load_to_bigquery import load_to_bq

def run_pipeline():
    print("Starting pipeline...")
    print("Step 1: Scraping GitHub API for SaaS/Dev tools...")
    df = scrape_all()

    print("Step 2: Saving to CSV...")
    if os.path.exists("raw_repo_data.csv"):
        df.to_csv("raw_repo_data.csv", mode='a', header = False, index = False )
    else:
        df.to_csv("raw_repo_data.csv", index = False)

    print("Step 3: Loading to BigQuery...")
    load_to_bq(df)

    print("Pipeline Compelete!")

if __name__ == "__main__":
    run_pipeline()
