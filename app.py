from __future__ import annotations

import io
from datetime import datetime

import pandas as pd
import streamlit as st

from data_analyzer.cloud import upload_bytes_to_s3
from data_analyzer.eda import (
    categorical_plot,
    correlation_heatmap,
    distribution_plot,
    numeric_summary,
    time_series_plot,
)
from data_analyzer.ingestion import ingest_uploaded_file
from data_analyzer.processing import clean_and_process
from data_analyzer.reporting import build_markdown_report

st.set_page_config(page_title="End-to-End Data Analysis Studio", layout="wide")
st.title("📊 End-to-End Data Analysis Studio")
st.caption(
    "Upload raw files (CSV, Excel, JSON, Parquet, PDF), auto-clean them, run EDA, and export reports/dashboard assets."
)

uploaded_file = st.file_uploader(
    "Upload a dataset",
    type=["csv", "xlsx", "xls", "json", "parquet", "pdf", "txt", "tsv"],
)

if not uploaded_file:
    st.info("Upload a file to start analysis.")
    st.stop()

with st.spinner("Reading input file..."):
    ingested = ingest_uploaded_file(uploaded_file.name, uploaded_file.read())

raw_df = ingested.dataframe
if raw_df.empty:
    st.warning("No rows were extracted from this file. Please verify your input format.")
    st.stop()

result = clean_and_process(raw_df)
cleaned_df = result.cleaned_df

st.subheader("1) Quick Dataset Snapshot")
col1, col2, col3 = st.columns(3)
col1.metric("Raw Rows", raw_df.shape[0])
col2.metric("Cleaned Rows", cleaned_df.shape[0])
col3.metric("Columns", cleaned_df.shape[1])

st.dataframe(cleaned_df.head(100), use_container_width=True)

st.subheader("2) Data Quality & Processing Log")
st.write(f"**Duplicates dropped:** {result.dropped_duplicates}")
st.write(f"**Missing values imputed:** {result.imputed_cells}")
for note in ingested.notes + result.transformations:
    st.markdown(f"- {note}")

st.subheader("3) EDA Dashboard")
num_cols = cleaned_df.select_dtypes(include=["number"]).columns.tolist()
cat_cols = cleaned_df.select_dtypes(exclude=["number", "datetime64[ns]"]).columns.tolist()
date_cols = cleaned_df.select_dtypes(include=["datetime64[ns]"]).columns.tolist()

summary_df = numeric_summary(cleaned_df)
if not summary_df.empty:
    st.markdown("#### Numeric Summary")
    st.dataframe(summary_df, use_container_width=True)

corr_fig = correlation_heatmap(cleaned_df)
if corr_fig:
    st.plotly_chart(corr_fig, use_container_width=True)

if num_cols:
    dist_col = st.selectbox("Pick a numeric column for distribution", num_cols)
    st.plotly_chart(distribution_plot(cleaned_df, dist_col), use_container_width=True)

if cat_cols:
    cat_col = st.selectbox("Pick a categorical column", cat_cols)
    st.plotly_chart(categorical_plot(cleaned_df, cat_col), use_container_width=True)

if date_cols and num_cols:
    st.markdown("#### Time Trend")
    time_col = st.selectbox("Date column", date_cols)
    value_col = st.selectbox("Metric", num_cols, key="trend_metric")
    st.plotly_chart(
        time_series_plot(cleaned_df, time_col, value_col), use_container_width=True
    )

st.subheader("4) Report & Export")
report_md = build_markdown_report(
    raw_df,
    cleaned_df,
    result.transformations,
    ingested.source_type,
    ingested.notes,
)

st.download_button(
    "⬇️ Download cleaned data (CSV)",
    data=cleaned_df.to_csv(index=False).encode("utf-8"),
    file_name=f"cleaned_{uploaded_file.name.rsplit('.', 1)[0]}.csv",
    mime="text/csv",
)

st.download_button(
    "⬇️ Download analysis report (Markdown)",
    data=report_md.encode("utf-8"),
    file_name=f"analysis_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.md",
    mime="text/markdown",
)

with st.expander("Preview report"):
    st.markdown(report_md)

st.subheader("5) Optional Cloud Export (AWS S3)")
with st.expander("Configure S3 upload"):
    s3_bucket = st.text_input("S3 Bucket")
    s3_prefix = st.text_input("S3 Prefix", value="analysis-outputs")
    s3_region = st.text_input("AWS Region", value="us-east-1")
    aws_key = st.text_input("AWS Access Key ID", type="password")
    aws_secret = st.text_input("AWS Secret Access Key", type="password")

    if st.button("Upload cleaned data + report to S3"):
        if not all([s3_bucket, s3_region, aws_key, aws_secret]):
            st.error("Please provide all S3 credentials and bucket details.")
        else:
            try:
                dataset_key = (
                    f"{s3_prefix.rstrip('/')}/cleaned_{uploaded_file.name.rsplit('.', 1)[0]}.csv"
                )
                report_key = (
                    f"{s3_prefix.rstrip('/')}/report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.md"
                )
                csv_path = upload_bytes_to_s3(
                    cleaned_df.to_csv(index=False).encode("utf-8"),
                    s3_bucket,
                    dataset_key,
                    s3_region,
                    aws_key,
                    aws_secret,
                )
                report_path = upload_bytes_to_s3(
                    report_md.encode("utf-8"),
                    s3_bucket,
                    report_key,
                    s3_region,
                    aws_key,
                    aws_secret,
                )
                st.success(f"Uploaded successfully:\n- {csv_path}\n- {report_path}")
            except Exception as exc:
                st.exception(exc)
