from __future__ import annotations

import argparse
import os

from src.volu_bq.query import run_sql_file
from src.utils.paths import analysis_out_dir, analysis_sql_path
from src.features.fit_accuracy.metrics import headline_from_overall
from src.features.fit_accuracy.viz import plot_brand_accuracy


ANALYSIS_NAME = "FitAccuracy"

def main(start_date: str | None, end_date: str | None, brand: str | None):
    out_dir = analysis_out_dir(ANALYSIS_NAME, with_timestamp=False)
    tables_dir = out_dir / "tables"

    max_bytes = os.environ.get("MAX_BYTES_BILLED")
    max_bytes_int = int(max_bytes) if max_bytes is not None else None

    overall_sql = analysis_sql_path(ANALYSIS_NAME, "fit_accuracy_overall.sql.j2")
    by_brand_sql = analysis_sql_path(ANALYSIS_NAME, "fit_accuracy_by_brand.sql.j2")

    # Dates are optional (and currently unused in SQL if the table has no date column)
    params = {"start_date": start_date, "end_date": end_date, "brand": brand}

    overall_df = run_sql_file(str(overall_sql), params=params, maximum_bytes_billed=max_bytes_int)
    by_brand_df = run_sql_file(str(by_brand_sql), params=params, maximum_bytes_billed=max_bytes_int)

    overall_csv = tables_dir / f"fit_accuracy_overall.csv"
    by_brand_csv = tables_dir / f"fit_accuracy_by_brand.csv"
    overall_df.to_csv(overall_csv, index=False)
    by_brand_df.to_csv(by_brand_csv, index=False)

    fig_path = plot_brand_accuracy(by_brand_df, out_dir)

    headline = headline_from_overall(overall_df)
    summary_md = out_dir / "summary.md"
    summary_md.write_text(
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
                f"Tables: `{overall_csv}` , `{by_brand_csv}`",
                f"Figure: `{fig_path}`",
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
