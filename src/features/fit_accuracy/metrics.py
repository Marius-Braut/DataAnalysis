# src/features/fit_accuracy/metrics.py

from __future__ import annotations
import pandas as pd

def headline_from_overall(df_overall: pd.DataFrame) -> dict:
    row = df_overall.iloc[0].to_dict() if not df_overall.empty else {}
    return {
        "scans_total": int(row.get("scans_total", 0) or 0),
        "scans_with_purchase": int(row.get("scans_with_purchase", 0) or 0),
        "fit_accuracy_rate_exact": float(row.get("fit_accuracy_rate_exact", 0.0) or 0.0),
        "rate_gbs_size_diff_only": float(row.get("rate_gbs_size_diff_only", 0.0) or 0.0),
        "rate_exact_or_gbs": float(row.get("rate_exact_or_gbs", 0.0) or 0.0),
    }
