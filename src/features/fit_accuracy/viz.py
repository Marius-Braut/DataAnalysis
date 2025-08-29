# src/features/fit_accuracy/viz.py

from __future__ import annotations
import pandas as pd
from pathlib import Path
from src.plotting_functions.bars import bar_plot

def plot_brand_accuracy(df_by_brand: pd.DataFrame, out_dir: Path) -> Path:
    out_path = out_dir / "figures" / "fit_accuracy_rate_exact_by_brand.png"
    bar_plot(
        df=df_by_brand,
        x="brand_name",
        y="fit_accuracy_rate_exact",
        out_path=out_path,
        title="Fit Accuracy (Exact) by Brand",
        rotate_x=45,
        annotate=True,
        figsize=(12, 6),
        sort_desc=True,
    )
    return out_path
