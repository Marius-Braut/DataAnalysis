# src/utils/paths.py
from __future__ import annotations

import os
from pathlib import Path
from datetime import datetime
from typing import Tuple

def analysis_out_dir(analysis_name: str, with_timestamp: bool = False) -> Path:
    """(Kept for backward compatibility) Root folder for an analysis."""
    root = Path(os.environ.get("REPORTS_DIR", "./reports")).resolve()
    out = root / analysis_name
    if with_timestamp:
        out = out / datetime.now().strftime("%Y-%m-%d_%H%M%S")
    (out / "tables").mkdir(parents=True, exist_ok=True)
    (out / "figures").mkdir(parents=True, exist_ok=True)
    return out

def prepare_analysis_dirs(analysis_name: str, *, with_timestamp: bool = False) -> Tuple[Path, Path, Path]:
    """
    Create & return (out_dir, tables_dir, figures_dir) under reports/<AnalysisName>[/timestamp].
    Always guarantees tables/, figures/ exist.
    """
    out_dir = analysis_out_dir(analysis_name, with_timestamp=with_timestamp)
    tables_dir = out_dir / "tables"
    figures_dir = out_dir / "figures"
    return out_dir, tables_dir, figures_dir

def analysis_sql_path(analysis_name: str, filename: str) -> Path:
    """Return sql/<AnalysisName>/<filename>."""
    return Path("sql") / analysis_name / filename
