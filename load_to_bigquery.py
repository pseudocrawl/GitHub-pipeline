from google.cloud import bigquery
import pandas as pd
import os
from dotenv import load_dotenv
from google.cloud.bigquery import TimePartitioning, TimePartitioningType
from datetime import date

load_dotenv()

PROJECT_ID = 'project-574b3547-7112-4651-817'
DATASET = "raw"
TABLE = "github_repos"

def load_to_bq(df):
    client = bigquery.Client(project=PROJECT_ID)
    table_id = f"{PROJECT_ID}.{DATASET}.{TABLE}"
    today = date.today().isoformat()

    # Check if today's data already exists | idempotency
    try:
        existing_df = client.query(f"""SELECT COUNT(*) AS cnt
                                     FROM `{table_id}`
                                     WHERE DATE(scraped_at) = '{today}'""").to_dataframe()
        
        if existing_df['cnt'][0] > 0:
            print(f"Data already loaded for {today}. Skipping.")
            return

    except Exception:
        pass #table doesn't exist yet

    #convert scraped_at to datetime
    df['scraped_at'] = pd.to_datetime(df['scraped_at'])

    job_config = bigquery.LoadJobConfig(
        write_disposition = "WRITE_APPEND",
        autodetect = True,
        time_partitioning = TimePartitioning(
            type_ = TimePartitioningType.MONTH,
            field = "scraped_at"
        )
    )

    job = client.load_table_from_dataframe(df, table_id, job_config = job_config)
    job.result()

    print(f"Loaded {len(df)} rows to {table_id}")

if __name__ == "__main__":
    df = pd.read_csv("raw_repo_data.csv", encoding='utf-8', encoding_errors='ignore')
    load_to_bq(df)