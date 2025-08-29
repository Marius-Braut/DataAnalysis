# src/features/fit_accuracy/run.py
from __future__ import annotations

import argparse
import os
from pathlib import Path
from src.volu_bq.query import run_sql_file
from src.utils.paths import prepare_analysis_dirs, analysis_sql_path
from src.features.fit_accuracy.metrics import headline_from_overall
from src.features.fit_accuracy.viz import plot_brand_accuracy

ANALYSIS_NAME = "FitAccuracy"

def main(start_date: str | None, end_date: str | None, brand: str | None):
    out_dir, tables_dir, figures_dir = prepare_analysis_dirs(ANALYSIS_NAME, with_timestamp=False)

    max_bytes = os.environ.get("MAX_BYTES_BILLED")
    max_bytes_int = int(max_bytes) if max_bytes is not None else None

    params = {"start_date": start_date, "end_date": end_date, "brand": brand}

    overall_df = run_sql_file(
        str(analysis_sql_path(ANALYSIS_NAME, "fit_accuracy_overall.sql.j2")),
        params=params,
        maximum_bytes_billed=max_bytes_int,
    )
    by_brand_df = run_sql_file(
        str(analysis_sql_path(ANALYSIS_NAME, "fit_accuracy_by_brand.sql.j2")),
        params=params,
        maximum_bytes_billed=max_bytes_int,
    )

    # --- Standardized filenames ---
    overall_csv = tables_dir / "fit_accuracy_overall.csv"
    by_brand_csv = tables_dir / "fit_accuracy_by_brand.csv"
    overall_df.to_csv(overall_csv, index=False)
    by_brand_df.to_csv(by_brand_csv, index=False)

    fig_path = figures_dir / "fit_accuracy_rate_exact_by_brand.png"
    # plot expects a full path; we already standardized figures/
    from src.plotting_functions.bars import bar_plot  # if your viz wraps this, keep using plot_brand_accuracy
    # If you prefer the wrapper:
    # fig_path = plot_brand_accuracy(by_brand_df, out_dir)
    # else do a direct bar plot:
    # bar_plot(df=by_brand_df, x="brand_name", y="fit_accuracy_rate_exact", out_path=fig_path, annotate=True, figsize=(12,6), sort_desc=True)

    # Keep your existing wrapper for consistency:
    from src.features.fit_accuracy.viz import plot_brand_accuracy
    plot_brand_accuracy(by_brand_df, out_dir)  # writes into figures/ with the standardized name

    # --- Summary.md (always in analysis root) ---
    headline = headline_from_overall(overall_df)
    (out_dir / "summary.md").write_text(
        "\n".join(
            [
                f"# {ANALYSIS_NAME} Summary",
                f"**Date range:** {(start_date or 'All')} → {(end_date or 'All')}",
                f"**Brand filter:** {brand or 'All'}",
                "",
                f"- Scans total: {headline['scans_total']:,}",
                f"- Scans with purchase: {headline['scans_with_purchase']:,}",
                f"- Fit accuracy (exact): {headline['fit_accuracy_rate_exact']:.2%}",
                f"- Same G/B/S but size different: {headline['rate_gbs_size_diff_only']:.2%}",
                f"- Exact or G/B/S: {headline['rate_exact_or_gbs']:.2%}",
                "",
                "## Outputs",
                f"- Tables: `{overall_csv.name}`, `{by_brand_csv.name}` (in `tables/`)",
                f"- Figure: `fit_accuracy_rate_exact_by_brand.png` (in `figures/`)",
            ]
        ),
        encoding="utf-8",
    )

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="FitAccuracy analysis")
    parser.add_argument("--start-date", default=None, help="YYYY-MM-DD (optional)")
    parser.add_argument("--end-date", default=None, help="YYYY-MM-DD (optional)")
    parser.add_argument("--brand", default=None, help="Optional brand filter")
    args = parser.parse_args()
    main(args.start_date, args.end_date, args.brand)
