from google.cloud import bigquery
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

PROJECT_ID = 'project-574b3547-7112-4651-817'
DATASET = "raw"
TABLE = "github_repos"

def load_to_bq(df):
    client = bigquery.Client(project=PROJECT_ID)
    table_id = f"{PROJECT_ID}.{DATASET}.{TABLE}"

    job_config = bigquery.LoadJobConfig(
        write_disposition = "WRITE_APPEND",
        autodetect = True,
    )

    job = client.load_table_from_dataframe(df, table_id, job_config = job_config)
    job.result()

    print(f"Loaded {len(df)} rows to {table_id}")

if __name__ == "__main__":
    df = pd.read_csv("raw_repo_data.csv", encoding='utf-8', encoding_errors='ignore')
    load_to_bq(df)