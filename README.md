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

## Adding another analysis

Each analysis is a self-contained feature under `src/features/`.

### Step-by-step

1. **Create the new module**
src/features/<new_analysis>/
├─ run.py # CLI entrypoint (args/env → SQL → metrics → exports)
├─ metrics.py # pandas calculations
└─ viz.py # optional charts/plots

markdown
Copy code

2. **Add SQL templates**
sql/<new_analysis>_base.sql.j2
sql/<new_analysis>_breakdowns.sql.j2

markdown
Copy code

3. **Reuse utilities**
- Import BigQuery helpers from `src/volu_bq/` (client, query, cache).
- Reuse any common helpers from `src/utils/`.

4. **Configure Run Configuration in PyCharm**
- **Script path:** `src/features/<new_analysis>/run.py`
- **Working directory:** project root
- **Env file:** `.env`
- (Optional) add script parameters, e.g.:
  ```
  --start 2025-01-01 --end 2025-03-31
  ```
