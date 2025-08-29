from pathlib import Path
from datetime import datetime
import os

def analysis_out_dir(analysis_name: str, with_timestamp: bool = False) -> Path:
    """
    Returns a Path like reports/<analysis_name>/[YYYY-MM-DD_HHMMSS]
    and ensures the directory exists.
    """
    root = Path(os.environ.get("REPORTS_DIR", "./reports")).resolve()
    out = root / analysis_name
    if with_timestamp:
        out = out / datetime.now().strftime("%Y-%m-%d_%H%M%S")
    out.mkdir(parents=True, exist_ok=True)
    return out

def analysis_sql_path(analysis_name: str, filename: str) -> Path:
    """Return sql/<analysis_name>/<filename> as a Path."""
    return Path("sql") / analysis_name / filename