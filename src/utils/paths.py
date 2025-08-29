# src/utils/paths.py

from __future__ import annotations
from pathlib import Path
from datetime import datetime
import os
from typing import Optional

def analysis_out_dir(analysis_name: str, with_timestamp: bool = False) -> Path:
    root = Path(os.environ.get("REPORTS_DIR", "./reports")).resolve()
    out = root / analysis_name
    if with_timestamp:
        out = out / datetime.now().strftime("%Y-%m-%d_%H%M%S")
    (out / "tables").mkdir(parents=True, exist_ok=True)
    (out / "figures").mkdir(parents=True, exist_ok=True)
    return out

def analysis_sql_path(analysis_name: str, filename: str) -> Path:
    return Path("sql") / analysis_name / filename
