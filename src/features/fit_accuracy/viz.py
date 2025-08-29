# src/features/fit_accuracy/viz.py
import pandas as pd
from pathlib import Path
from src.plotting_functions.bars import bar_plot

def plot_recs_per_brand(df: pd.DataFrame, out_path: str) -> None:
    """
    Wraps the generic bar plot for this analysis.
    Expects columns: brand_name, recs
    """
    out = Path(out_path)
    bar_plot(
        df=df,
        x="brand_name",
        y="recs",
        out_path=out,
        title=None,          # let it auto-infer "Recs by Brand Name"
        rotate_x=45,
        annotate=True,
        figsize=(12, 6),
        sort_desc=True,
    )
