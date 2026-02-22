from __future__ import annotations

import io
import json
from dataclasses import dataclass
from pathlib import Path

import pandas as pd
import pdfplumber


@dataclass
class IngestionResult:
    dataframe: pd.DataFrame
    source_type: str
    notes: list[str]


def _read_pdf(file_bytes: bytes) -> IngestionResult:
    notes: list[str] = []
    tables: list[pd.DataFrame] = []
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page_idx, page in enumerate(pdf.pages, start=1):
            extracted = page.extract_tables()
            if not extracted:
                continue
            for table in extracted:
                if not table:
                    continue
                header, *rows = table
                frame = pd.DataFrame(rows, columns=header)
                frame["_source_page"] = page_idx
                tables.append(frame)

    if not tables:
        notes.append("No PDF tables detected. Returning empty frame.")
        return IngestionResult(pd.DataFrame(), "pdf", notes)

    result = pd.concat(tables, ignore_index=True)
    notes.append(f"Extracted {len(tables)} table(s) from PDF.")
    return IngestionResult(result, "pdf", notes)


def ingest_uploaded_file(file_name: str, file_bytes: bytes) -> IngestionResult:
    suffix = Path(file_name).suffix.lower()

    if suffix == ".csv":
        return IngestionResult(pd.read_csv(io.BytesIO(file_bytes)), "csv", [])
    if suffix in {".xlsx", ".xls"}:
        return IngestionResult(pd.read_excel(io.BytesIO(file_bytes)), "excel", [])
    if suffix == ".json":
        obj = json.loads(file_bytes.decode("utf-8"))
        frame = pd.json_normalize(obj)
        return IngestionResult(frame, "json", [])
    if suffix == ".parquet":
        return IngestionResult(pd.read_parquet(io.BytesIO(file_bytes)), "parquet", [])
    if suffix == ".pdf":
        return _read_pdf(file_bytes)
    if suffix in {".txt", ".tsv"}:
        sep = "\t" if suffix == ".tsv" else ","
        return IngestionResult(pd.read_csv(io.BytesIO(file_bytes), sep=sep), "text", [])

    raise ValueError(
        "Unsupported file type. Upload CSV, Excel, JSON, Parquet, PDF, TXT, or TSV."
    )
