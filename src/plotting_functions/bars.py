# src/plotting_functions/bars.py
from pathlib import Path
from typing import Optional
import pandas as pd
import matplotlib.pyplot as plt

def _auto_title(x: str, y: str) -> str:
    def nice(s: str) -> str:
        return s.replace("_", " ").title()
    return f"{nice(y)} by {nice(x)}"

def bar_plot(
    df: pd.DataFrame,
    x: str,
    y: str,
    out_path: str | Path,
    title: Optional[str] = None,
    rotate_x: int = 45,
    annotate: bool = True,
    figsize: tuple[int, int] = (10, 6),
    sort_desc: bool = True,
) -> None:
    """
    Generic bar plot. Infers title from columns if not provided.
    - df: DataFrame with columns x and y
    - x: column name for x-axis (categorical)
    - y: column name for y-axis (numeric)
    - out_path: file path to save (e.g., 'reports/plot.png')
    """
    assert x in df.columns and y in df.columns, f"Columns {x} or {y} not in DataFrame."

    data = df.copy()
    if sort_desc:
        data = data.sort_values(y, ascending=False)

    plt.figure(figsize=figsize)
    bars = plt.bar(data[x].astype(str), data[y].astype(float))

    plt.xlabel(x.replace("_", " ").title())
    plt.ylabel(y.replace("_", " ").title())
    plt.title(title or _auto_title(x, y))
    plt.xticks(rotation=rotate_x, ha="right")
    plt.tight_layout()

    if annotate:
        for rect, val in zip(bars, data[y].tolist()):
            height = rect.get_height()
            plt.annotate(
                f"{val:,}",
                xy=(rect.get_x() + rect.get_width() / 2, height),
                xytext=(0, 3),
                textcoords="offset points",
                ha="center",
                va="bottom",
            )

    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_path, dpi=150)
    plt.close()
