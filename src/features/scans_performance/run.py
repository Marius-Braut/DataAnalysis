import argparse
import os
from pathlib import Path
from src.volu_bq.query import run_sql_file
from src.utils.paths import analysis_out_dir, analysis_sql_path
from src.plotting_functions.bars import bar_plot

ANALYSIS_NAME = "ScansPerformance"

def main(start_date: str, end_date: str, top_org: str | None):
    out_dir = analysis_out_dir(ANALYSIS_NAME, with_timestamp=False)

    max_bytes = os.environ.get("MAX_BYTES_BILLED")
    max_bytes_int = int(max_bytes) if max_bytes is not None else None

    sql_path = analysis_sql_path(ANALYSIS_NAME, "scans_by_top_org.sql.j2")

    df = run_sql_file(
        str(sql_path),
        params={
            "start_date": start_date,
            "end_date": end_date,
            "top_organisation": top_org,  # can be None
        },
        maximum_bytes_billed=max_bytes_int,
    )

    # Save CSV
    csv_path = out_dir / f"scans_by_top_org_{start_date}_{end_date}.csv"
    df.to_csv(csv_path, index=False)
    print(f"Wrote {csv_path}")

    # Plot (bar) using the generic plotter
    png_path = out_dir / f"scans_by_top_org_{start_date}_{end_date}.png"
    bar_plot(
        df=df,
        x="top_organisation",
        y="scans",
        out_path=png_path,
        title=None,         # auto: "Scans by Top Organisation"
        rotate_x=45,
        annotate=True,
        figsize=(12, 6),
        sort_desc=True,
    )
    print(f"Wrote {png_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ScansPerformance analysis")
    parser.add_argument("--start-date", required=True, help="YYYY-MM-DD")
    parser.add_argument("--end-date", required=True, help="YYYY-MM-DD")
    parser.add_argument("--top-org", default=None, help="Filter to a single top_organisation (optional)")
    args = parser.parse_args()
    main(args.start_date, args.end_date, args.top_org)
