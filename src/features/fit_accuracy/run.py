import os
import pandas as pd
from pathlib import Path
from src.volu_bq.query import run_sql_file
from src.features.fit_accuracy.viz import plot_recs_per_brand

def main():
    reports_dir = Path(os.environ.get("REPORTS_DIR", "./reports")).resolve()
    reports_dir.mkdir(parents=True, exist_ok=True)

    max_bytes = os.environ.get("MAX_BYTES_BILLED")
    max_bytes_int = int(max_bytes) if max_bytes is not None else None

    # 1) Run the SQL
    df = run_sql_file("sql/fit_accuracy_recs_per_brand.sql.j2", maximum_bytes_billed=max_bytes_int)

    # 2) Basic sanity print
    print(df.head(10))

    # 3) Save CSV
    csv_path = reports_dir / "recs_per_brand.csv"
    df.to_csv(csv_path, index=False)
    print(f"Wrote {csv_path}")

    # 4) Plot
    png_path = reports_dir / "recs_per_brand.png"
    plot_recs_per_brand(df, str(png_path))
    print(f"Wrote {png_path}")

if __name__ == "__main__":
    main()
