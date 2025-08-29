import os
from typing import Optional, Dict, Any, List
import pandas as pd
from google.cloud import bigquery

def _to_bq_params(params: Optional[Dict[str, Any]]) -> Optional[List[bigquery.ScalarQueryParameter]]:
    if not params:
        return None
    out: List[bigquery.ScalarQueryParameter] = []
    for k, v in params.items():
        # Infer simple types
        if isinstance(v, bool):
            out.append(bigquery.ScalarQueryParameter(k, "BOOL", v))
        elif isinstance(v, int):
            out.append(bigquery.ScalarQueryParameter(k, "INT64", v))
        elif isinstance(v, float):
            out.append(bigquery.ScalarQueryParameter(k, "FLOAT64", v))
        else:
            # Dates should be 'YYYY-MM-DD' strings; BigQuery DATE param
            # If you want DATETIME/TIMESTAMP, adjust here.
            if k.endswith("date") or k.endswith("start_date") or k.endswith("end_date"):
                out.append(bigquery.ScalarQueryParameter(k, "DATE", v))
            else:
                out.append(bigquery.ScalarQueryParameter(k, "STRING", v))
    return out

def run_sql_file(path: str, *, params: Optional[Dict[str, Any]] = None, maximum_bytes_billed: Optional[int] = None) -> pd.DataFrame:
    """
    Reads a SQL file and executes it in BigQuery, returning a DataFrame.
    Supports named scalar parameters via @param_name in the SQL.
    """
    with open(path, "r", encoding="utf-8") as f:
        sql = f.read()

    project = os.environ.get("GCP_PROJECT")
    location = os.environ.get("BQ_LOCATION", "EU")
    client = bigquery.Client(project=project, location=location)

    job_config = bigquery.QueryJobConfig()
    if maximum_bytes_billed is not None:
        job_config.maximum_bytes_billed = maximum_bytes_billed

    bq_params = _to_bq_params(params)
    if bq_params:
        job_config.query_parameters = bq_params

    job = client.query(sql, job_config=job_config)
    return job.to_dataframe()
