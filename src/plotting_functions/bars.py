from __future__ import annotations
from typing import Optional, Sequence
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
from pathlib import Path


def stacked_bar_length_width(
    df: pd.DataFrame,
    *,
    out_path: str | Path,
    length_col: str = "length_size",
    width_col: str = "width_label",
    count_col: str = "count",
    title: str = "",
    relative: bool = False,
    source: str = "",
    brand: Optional[str] = None,
    width_order: Optional[Sequence[str]] = None,   # e.g., ["B", "D", "2E", "4E"]
    length_order: Optional[Sequence[float | str]] = None,
    annotate: bool = True,
    figsize: tuple[int, int] = (12, 6),
    dpi: int = 150,
) -> None:
    """
    Create a stacked bar chart of counts (or shares) by length, stacked by width.
    Expects df with columns: [brand_name, gender_age, length_col, width_col, count_col]

    - If brand is provided, filters df to that brand.
    - If relative=True, normalizes to total share (0..1) and shows percent axis.
    - width_order/length_order let you control the stacking and x-axis order.
    - Saves figure to out_path and closes it (no plt.show()).
    """
    data = df.copy()

    # Optional brand filter
    if brand is not None and "brand_name" in data.columns:
        data = data[data["brand_name"] == brand]

    # Early exit with empty figure
    if data.empty:
        plt.figure(figsize=figsize)
        plt.title(title or "No data to plot")
        Path(out_path).parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(out_path, dpi=dpi)
        plt.close()
        return

    # Try to infer gender label safely
    gender = None
    if "gender_age" in data.columns and not data["gender_age"].isna().all():
        gender = str(data["gender_age"].dropna().iloc[0])

    # Pivot so widths become columns and counts are summed
    pivot_df = data.pivot_table(
        index=length_col,
        columns=width_col,
        values=count_col,
        aggfunc="sum",
        fill_value=0,
    )

    # Apply optional width ordering
    if width_order is not None:
        existing = [w for w in width_order if w in pivot_df.columns]
        remaining = [w for w in pivot_df.columns if w not in existing]
        pivot_df = pivot_df[[*existing, *remaining]]

    # Apply optional length ordering; otherwise sort numerically if possible
    if length_order is not None:
        ordered_index = [x for x in length_order if x in pivot_df.index.tolist()]
        remaining_idx = [x for x in pivot_df.index.tolist() if x not in ordered_index]
        pivot_df = pivot_df.loc[[*ordered_index, *remaining_idx]]
    else:
        try:
            pivot_df.index = pivot_df.index.astype(float)
            pivot_df = pivot_df.sort_index()
        except Exception:
            pivot_df = pivot_df.sort_index()

    # Relative normalization (share of total)
    if relative:
        total_sum = pivot_df.values.sum()
        if total_sum > 0:
            pivot_df = pivot_df / total_sum

    # Colors: map specific widths if present; otherwise use Matplotlib cycle
    default_colors = plt.rcParams["axes.prop_cycle"].by_key().get("color", [])
    specific_colors = {
        "4E": "#2ca02c",  # green
        "D":  "#1f77b4",  # blue
        "2E": "#ff7f0e",  # orange
    }
    colors = []
    for i, w in enumerate(pivot_df.columns):
        colors.append(specific_colors.get(str(w), default_colors[i % len(default_colors)] if default_colors else None))

    # Plot
    fig, ax = plt.subplots(figsize=figsize)
    pivot_df.plot(kind="bar", stacked=True, color=colors, ax=ax)

    # Dynamic title if not provided
    if not title:
        pieces = []
        if source:
            pieces.append(str(source).title())
        if gender:
            pieces.append(str(gender).title())
        if brand:
            pieces.append(str(brand).title())
        base = "Sizing Distribution"
        suffix = " (%)" if relative else ""
        ctx = " – ".join(pieces) if pieces else None
        title = f"{base}{f' in {ctx}' if ctx else ''}{suffix}"

    ax.set_title(title)
    ax.set_xlabel("Length Size")
    ax.set_ylabel("Share of Total" if relative else "Count")

    if relative:
        ax.yaxis.set_major_formatter(PercentFormatter(1.0))

    # Optional annotations per stacked segment
    if annotate:
        for container in ax.containers:
            for rect in container:
                height = rect.get_height()
                if height <= 0:
                    continue
                x = rect.get_x() + rect.get_width() / 2
                y = rect.get_y() + height / 2
                label = f"{height:.1%}" if relative else f"{int(round(height))}"
                ax.text(x, y, label, ha="center", va="center", fontsize=9, color="black")

    ax.legend(title="Width", bbox_to_anchor=(1.02, 1), loc="upper left")
    fig.tight_layout()

    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=dpi)
    plt.close(fig)


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
