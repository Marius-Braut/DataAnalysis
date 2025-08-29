# DataAnalysis

Analytics project template for Volumental using **PyCharm + BigQuery**.  
First analysis: **FitAccuracy**.

---

## How the setup works

### PyCharm project
- This repo is opened as a **new PyCharm project**.
- Code lives under `src/`, SQL templates under `sql/`, configs under `configs/`.

### Virtual environment
- A project-local virtual environment `.venv` is created inside the repo.
- All dependencies (BigQuery client, pandas, plotly, etc.) are installed here.
- PyCharm is configured to use this venv as the interpreter.

### Environment variables
- A `.env` file in the project root contains runtime config such as:
```text
GCP_PROJECT=volumental-data
BQ_LOCATION=EU
MAX_BYTES_BILLED=80000000000
CACHE_DIR=./data
REPORTS_DIR=./reports
```
- The `.env` file is loaded automatically when running analyses.

### Run Configuration (PyCharm)
- **Script path:** `src/features/fit_accuracy/run.py`  
- **Working directory:** project root (the folder containing `src/`, `sql/`, `.env`, etc.)  
- **Env file:** `.env` (requires the [EnvFile plugin](https://plugins.jetbrains.com/plugin/7861-envfile) in PyCharm)

When you click **Run** in PyCharm:
1. The interpreter from `.venv` is activated.
2. Environment variables from `.env` are loaded.
3. The script `src/features/fit_accuracy/run.py` is executed.
4. It connects to BigQuery, runs SQL templates, calculates metrics, and writes outputs to `/reports`.

---

## Project structure

```text
DataAnalysis/
├─ .env                  # not committed; local config
├─ .env.example          # template for teammates
├─ README.md
├─ requirements.txt
├─ sql/                  # SQL templates (Jinja2)
│   └─ fit_accuracy.sql.j2
├─ src/
│   ├─ volu_bq/          # shared BigQuery utilities
│   └─ features/
│       └─ fit_accuracy/ # first analysis
│           ├─ run.py
│           ├─ metrics.py
│           └─ viz.py
├─ data/                 # local cache (gitignored)
└─ reports/              # outputs (csv/png/md)
```
---

## Adding a New Analysis

To add a new analysis to this project, follow these steps:

1. **Create the feature package**
   - Make a new folder under `src/features/` named after your analysis (e.g. `scans_performance`).
   - Inside it, create an empty `__init__.py` file to make it a Python package.
   - Add a `run.py` script here — this will be the entry point for your analysis.

2. **Create the SQL folder**
   - Under `sql/`, create a folder named after your analysis (e.g. `ScansPerformance`).
   - Add one or more `.sql.j2` files here for your queries.

3. **Write your queries**
   - In the `.sql.j2` file(s), write the BigQuery SQL your analysis needs.
   - If your analysis requires parameters (dates, filters, etc.), use named parameters (`@start_date`, `@end_date`, etc.).
   - These will be passed in from Python when the analysis runs.

4. **Use the shared helpers**
   - Use `src/volu_bq/query.py` to execute your SQL templates.
   - Use `src/utils/paths.py` (`analysis_out_dir`, `analysis_sql_path`) to resolve paths and save results into the correct folder under `reports/`.
   - Use plotting functions from `src/plotting_functions/` (e.g. `bar_plot`) for charts.

5. **Decide on outputs**
   - Each analysis should write its outputs (CSV, PNG, etc.) to `reports/<AnalysisName>/`.
   - You can choose to add a timestamped subfolder if you want to keep multiple runs.

6. **Register it in the Makefile**
   - Add a new target in the `Makefile` for your analysis.
   - Typically, you’ll want three commands:
     - `run-<analysis>` → runs the analysis with required parameters.
     - `clean-<analysis>` → deletes the reports for that analysis.
     - `rerun-<analysis>` → cleans and runs in one step.

7. **(Optional) PyCharm Run Configuration**
   - In PyCharm, create a new Run Configuration pointing at your `run.py` script.
   - Use the project root as the working directory, and load `.env` as the environment file.
   - Add any arguments (like `--start-date` and `--end-date`) in the parameters field.

8. **Test the flow**
   - Run the analysis either from PyCharm or the terminal (via `make run-<analysis>`).
   - Verify that CSVs and plots are written into `reports/<AnalysisName>/`.

---

### Example Workflow

- Add a new analysis: `ScansPerformance`.
- Create `src/features/scans_performance/run.py`.
- Create `sql/ScansPerformance/scans_by_top_org.sql.j2`.
- Add Makefile commands: `run-scans-performance`, `clean-scans-performance`, `rerun-scans-performance`.
- Run it:
  ```bash
  make run-scans-performance start=2025-01-01 end=2025-08-10

