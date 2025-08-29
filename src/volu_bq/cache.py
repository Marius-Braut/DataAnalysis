from __future__ import annotations

import hashlib
import json
import os
import time
from pathlib import Path
from typing import Any, Dict, Optional

import pandas as pd


def _default_cache_dir() -> Path:
    return Path(os.environ.get("CACHE_DIR", "./data")).resolve()


def _file_sha1(path: Path) -> str:
    import hashlib

    h = hashlib.sha1()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def _canonical_params(params: Optional[Dict[str, Any]]) -> str:
    # Stable JSON for hashing (sorted keys)
    return json.dumps(params or {}, sort_keys=True, default=str)


def _cache_key_for_sqlfile(
    *,
    sql_path: Path,
    params: Optional[Dict[str, Any]],
    project: Optional[str],
    location: Optional[str],
    maximum_bytes_billed: Optional[int],
) -> str:
    parts = {
        "sql_path": str(sql_path),
        "sql_sha1": _file_sha1(sql_path),
        "params": _canonical_params(params),
        "project": project or "",
        "location": location or "",
        "max_bytes": maximum_bytes_billed or "",
    }
    raw = json.dumps(parts, sort_keys=True).encode("utf-8")
    return hashlib.sha1(raw).hexdigest()


def _cache_file_path(
    *,
    analysis_name: str,
    cache_key: str,
    cache_dir: Optional[Path] = None,
) -> Path:
    root = cache_dir or _default_cache_dir()
    p = root / analysis_name / "cache" / f"{cache_key}.parquet"
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def _is_fresh(path: Path, ttl_hours: Optional[int]) -> bool:
    if ttl_hours is None:
        return True  # treat as infinite cache if TTL not provided
    if not path.exists():
        return False
    age_sec = time.time() - path.stat().st_mtime
    return age_sec <= ttl_hours * 3600


def save_df(df: pd.DataFrame, path: Path) -> None:
    try:
        df.to_parquet(path, index=False)
    except Exception:
        # Fallback to CSV if parquet not available
        path = path.with_suffix(".csv")
        df.to_csv(path, index=False)


def load_df(path: Path) -> pd.DataFrame:
    if path.suffix == ".csv":
        return pd.read_csv(path)
    # If parquet missing but csv exists (from fallback), load csv
    if not path.exists() and path.with_suffix(".csv").exists():
        return pd.read_csv(path.with_suffix(".csv"))
    return pd.read_parquet(path)


def read_or_query_sqlfile(
    *,
    analysis_name: str,
    sql_path: Path,
    params: Optional[Dict[str, Any]],
    project: Optional[str],
    location: Optional[str],
    maximum_bytes_billed: Optional[int],
    ttl_hours: Optional[int] = None,
    force_refresh: bool = False,
) -> pd.DataFrame:
    """
    Return cached DataFrame if fresh; otherwise run the query and cache it.
    """
    cache_key = _cache_key_for_sqlfile(
        sql_path=sql_path,
        params=params,
        project=project,
        location=location,
        maximum_bytes_billed=maximum_bytes_billed,
    )
    cache_path = _cache_file_path(analysis_name=analysis_name, cache_key=cache_key)

    if (not force_refresh) and cache_path.exists() and _is_fresh(cache_path, ttl_hours):
        return load_df(cache_path)

    # Import here to avoid circular dependency at module import time
    from src.volu_bq.query import run_sql_file

    df = run_sql_file(str(sql_path), params=params, maximum_bytes_billed=maximum_bytes_billed)
    save_df(df, cache_path)
    return df
