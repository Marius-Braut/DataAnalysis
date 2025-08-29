import os
from pathlib import Path
from src.volu_bq.query import run_sql_file
from src.features.fit_accuracy.viz import plot_recs_per_brand
from src.utils.paths import analysis_out_dir

ANALYSIS_NAME = "FitAccuracy"

def main():
    # Choose whether you want a timestamped subfolder; False keeps it stable.
    out_dir = analysis_out_dir(ANALYSIS_NAME, with_timestamp=False)

    max_bytes = os.environ.get("MAX_BYTES_BILLED")
    max_bytes_int = int(max_bytes) if max_bytes is not None else None

    # 1) Run SQL
    df = run_sql_file("sql/FitAccuracy/fit_accuracy_recs_per_brand.sql.j2", maximum_bytes_billed=max_bytes_int)
    print(df.head(10))

    # 2) Save CSV
    csv_path = out_dir / "recs_per_brand.csv"
    df.to_csv(csv_path, index=False)
    print(f"Wrote {csv_path}")

    # 3) Plot
    png_path = out_dir / "recs_per_brand.png"
    plot_recs_per_brand(df, str(png_path))
    print(f"Wrote {png_path}")

if __name__ == "__main__":
    main()
