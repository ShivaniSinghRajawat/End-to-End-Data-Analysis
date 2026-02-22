from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def numeric_summary(df: pd.DataFrame) -> pd.DataFrame:
    numeric_df = df.select_dtypes(include=["number"])
    if numeric_df.empty:
        return pd.DataFrame()
    return numeric_df.describe().T.reset_index(names="feature")


def correlation_heatmap(df: pd.DataFrame) -> go.Figure | None:
    numeric_df = df.select_dtypes(include=["number"])
    if numeric_df.shape[1] < 2:
        return None

    corr = numeric_df.corr(numeric_only=True)
    return px.imshow(
        corr,
        text_auto=True,
        title="Correlation Heatmap",
        color_continuous_scale="RdBu",
        zmin=-1,
        zmax=1,
    )


def distribution_plot(df: pd.DataFrame, column: str) -> go.Figure:
    return px.histogram(df, x=column, nbins=40, marginal="box", title=f"Distribution: {column}")


def categorical_plot(df: pd.DataFrame, column: str) -> go.Figure:
    counts = df[column].value_counts(dropna=False).head(15).reset_index()
    counts.columns = [column, "count"]
    return px.bar(counts, x=column, y="count", title=f"Top Categories: {column}")


def time_series_plot(df: pd.DataFrame, time_column: str, value_column: str) -> go.Figure:
    grouped = df[[time_column, value_column]].dropna()
    grouped = grouped.groupby(time_column, as_index=False)[value_column].mean()
    return px.line(
        grouped,
        x=time_column,
        y=value_column,
        markers=True,
        title=f"{value_column} Trend over {time_column}",
    )
