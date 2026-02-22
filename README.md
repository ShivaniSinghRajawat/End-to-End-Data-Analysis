# End-to-End Data Analysis Studio

A full workflow application for raw data ingestion, automated cleaning/processing, exploratory analysis, report generation, and optional cloud export.

## Features

- **Multi-format ingestion:** CSV, Excel, JSON, Parquet, PDF tables, TXT/TSV.
- **Automated data cleaning:** deduplication, missing-value handling, datetime parsing, outlier capping.
- **EDA dashboard:** numeric summary, distributions, categorical exploration, correlation heatmap, time trends.
- **Deliverables:** downloadable cleaned CSV + markdown report.
- **Cloud connectivity:** optional AWS S3 upload for cleaned dataset and generated report.

## Project structure

```text
.
├── app.py
├── data_analyzer
│   ├── cloud.py
│   ├── eda.py
│   ├── ingestion.py
│   ├── processing.py
│   └── reporting.py
└── requirements.txt
```

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Open the Streamlit URL (typically http://localhost:8501).


## Run with Docker

```bash
docker build -t end-to-end-data-analysis-studio .
docker run --rm -p 8501:8501 end-to-end-data-analysis-studio
```

Then open http://localhost:8501.

## Recommended production extensions

- Add user authentication/roles.
- Persist metadata/history in PostgreSQL.
- Add scheduled pipelines (Airflow/Prefect).
- Add richer PDF extraction and OCR for scanned docs.
- Deploy with Docker + reverse proxy.
