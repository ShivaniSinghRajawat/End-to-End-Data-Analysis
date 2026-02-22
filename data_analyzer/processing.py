from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass
class ProcessingResult:
    cleaned_df: pd.DataFrame
    dropped_duplicates: int
    imputed_cells: int
    transformations: list[str]


def clean_and_process(df: pd.DataFrame) -> ProcessingResult:
    work_df = df.copy()
    transformations: list[str] = []

    original_rows = len(work_df)
    work_df = work_df.drop_duplicates()
    dropped_duplicates = original_rows - len(work_df)
    if dropped_duplicates:
        transformations.append(f"Dropped {dropped_duplicates} duplicate row(s).")

    for column in work_df.columns:
        if work_df[column].dtype == object:
            work_df[column] = work_df[column].apply(
                lambda value: value.strip() if isinstance(value, str) else value
            )

    imputed_cells = 0
    for column in work_df.columns:
        missing_before = work_df[column].isna().sum()
        if not missing_before:
            continue

        if pd.api.types.is_numeric_dtype(work_df[column]):
            median_value = work_df[column].median()
            work_df[column] = work_df[column].fillna(median_value)
            transformations.append(f"Filled missing numeric values in '{column}' with median.")
        elif pd.api.types.is_datetime64_any_dtype(work_df[column]):
            work_df[column] = work_df[column].fillna(method="ffill")
            transformations.append(
                f"Forward-filled missing datetime values in '{column}'."
            )
        else:
            mode_value = work_df[column].mode(dropna=True)
            fill_value = mode_value.iloc[0] if not mode_value.empty else "Unknown"
            work_df[column] = work_df[column].fillna(fill_value)
            transformations.append(
                f"Filled missing categorical values in '{column}' with mode/Unknown."
            )

        imputed_cells += int(missing_before)

    for column in work_df.columns:
        if work_df[column].dtype != object:
            continue

        parsed = pd.to_datetime(work_df[column], errors="coerce")
        parse_ratio = parsed.notna().mean()
        if parse_ratio > 0.8:
            work_df[column] = parsed
            transformations.append(f"Auto-parsed '{column}' as datetime.")

    for column in work_df.select_dtypes(include=[np.number]).columns:
        q1 = work_df[column].quantile(0.25)
        q3 = work_df[column].quantile(0.75)
        iqr = q3 - q1
        if iqr == 0 or pd.isna(iqr):
            continue

        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr
        clipped = work_df[column].clip(lower=lower, upper=upper)
        changed = (clipped != work_df[column]).sum()
        if changed:
            work_df[column] = clipped
            transformations.append(
                f"Capped {int(changed)} outlier value(s) in '{column}' using IQR clipping."
            )

    return ProcessingResult(work_df, dropped_duplicates, imputed_cells, transformations)
