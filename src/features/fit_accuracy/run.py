from __future__ import annotations

import argparse
import os
from pathlib import Path

from src.utils.paths import prepare_analysis_dirs, analysis_sql_path
from src.features.fit_accuracy.metrics import headline_from_overall
from src.features.fit_accuracy.viz import plot_brand_accuracy
from src.volu_bq.cache import read_or_query_sqlfile  # <-- use the cache

ANALYSIS_NAME = "FitAccuracy"

def main(start_date: str | None, end_date: str | None, brand: str | None, force_refresh: bool):
    out_dir, tables_dir, figures_dir = prepare_analysis_dirs(ANALYSIS_NAME, with_timestamp=False)

    project = os.environ.get("GCP_PROJECT")
    location = os.environ.get("BQ_LOCATION", "EU")
    max_bytes = os.environ.get("MAX_BYTES_BILLED")
    max_bytes_int = int(max_bytes) if max_bytes is not None else None
    ttl_env = os.environ.get("CACHE_TTL_HOURS")
    ttl_hours = int(ttl_env) if ttl_env else None

    params = {"start_date": start_date, "end_date": end_date, "brand": brand}

    overall_df = read_or_query_sqlfile(
        analysis_name=ANALYSIS_NAME,
        sql_path=analysis_sql_path(ANALYSIS_NAME, "fit_accuracy_overall.sql.j2"),
        params=params,
        project=project,
        location=location,
        maximum_bytes_billed=max_bytes_int,
        ttl_hours=ttl_hours,
        force_refresh=force_refresh,
    )
    by_brand_df = read_or_query_sqlfile(
        analysis_name=ANALYSIS_NAME,
        sql_path=analysis_sql_path(ANALYSIS_NAME, "fit_accuracy_by_brand.sql.j2"),
        params=params,
        project=project,
        location=location,
        maximum_bytes_billed=max_bytes_int,
        ttl_hours=ttl_hours,
        force_refresh=force_refresh,
    )

    # (rest: write CSVs, plot, summary) — unchanged
    overall_csv = tables_dir / "fit_accuracy_overall.csv"
    by_brand_csv = tables_dir / "fit_accuracy_by_brand.csv"
    overall_df.to_csv(overall_csv, index=False)
    by_brand_df.to_csv(by_brand_csv, index=False)

    plot_brand_accuracy(by_brand_df, out_dir)

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
                "- Tables: `tables/fit_accuracy_overall.csv`, `tables/fit_accuracy_by_brand.csv`",
                "- Figure: `figures/fit_accuracy_rate_exact_by_brand.png`",
            ]
        ),
        encoding="utf-8",
    )

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="FitAccuracy analysis")
    parser.add_argument("--start-date", default=None, help="YYYY-MM-DD (optional)")
    parser.add_argument("--end-date", default=None, help="YYYY-MM-DD (optional)")
    parser.add_argument("--brand", default=None, help="Optional brand filter")
    parser.add_argument("--force-refresh", action="store_true", help="Bypass cache for this run")
    args = parser.parse_args()
    main(args.start_date, args.end_date, args.brand, args.force_refresh)
