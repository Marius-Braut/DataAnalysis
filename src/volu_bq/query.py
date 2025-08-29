import os
import pandas as pd
from google.cloud import bigquery

def run_sql_file(path: str, *, maximum_bytes_billed: int | None = None) -> pd.DataFrame:
    """
    Reads a SQL file and executes it in BigQuery, returning a DataFrame.
    Uses Application Default Credentials and optional bytes cap.
    """
    with open(path, "r", encoding="utf-8") as f:
        sql = f.read()

    project = os.environ.get("GCP_PROJECT")  # optional; client can infer
    location = os.environ.get("BQ_LOCATION", "EU")
    client = bigquery.Client(project=project, location=location)

    job_config = bigquery.QueryJobConfig()
    if maximum_bytes_billed is not None:
        job_config.maximum_bytes_billed = maximum_bytes_billed

    job = client.query(sql, job_config=job_config)
    return job.to_dataframe()
