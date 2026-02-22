from __future__ import annotations

from datetime import datetime

import pandas as pd


def build_markdown_report(
    raw_df: pd.DataFrame,
    cleaned_df: pd.DataFrame,
    transformations: list[str],
    source_type: str,
    ingestion_notes: list[str],
) -> str:
    generated_at = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    report_lines = [
        "# Automated Data Analysis Report",
        "",
        f"Generated: **{generated_at}**",
        f"Source format: **{source_type.upper()}**",
        "",
        "## 1) Dataset Overview",
        f"- Raw shape: `{raw_df.shape[0]} rows x {raw_df.shape[1]} columns`",
        f"- Cleaned shape: `{cleaned_df.shape[0]} rows x {cleaned_df.shape[1]} columns`",
        f"- Columns: `{', '.join(map(str, cleaned_df.columns.tolist()))}`",
        "",
        "## 2) Ingestion Notes",
    ]

    if ingestion_notes:
        report_lines.extend([f"- {note}" for note in ingestion_notes])
    else:
        report_lines.append("- No ingestion warnings.")

    report_lines.extend(["", "## 3) Processing Steps"])
    if transformations:
        report_lines.extend([f"- {item}" for item in transformations])
    else:
        report_lines.append("- No explicit transformations were needed.")

    report_lines.extend(["", "## 4) Numeric Summary"])
    numeric_df = cleaned_df.select_dtypes(include=["number"])
    if not numeric_df.empty:
        desc = numeric_df.describe().to_markdown()
        report_lines.extend(["", desc])
    else:
        report_lines.append("- No numeric columns available.")

    report_lines.extend(["", "## 5) Recommended Next Actions"])
    report_lines.extend(
        [
            "- Validate business rules and domain constraints for key variables.",
            "- Review top correlated features and assess causality before using them in models.",
            "- Consider exporting cleaned data to cloud storage for team collaboration.",
        ]
    )

    return "\n".join(report_lines)
