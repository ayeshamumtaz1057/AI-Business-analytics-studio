"""File ingestion: CSV / Excel / JSON / ZIP / SQL with encoding + delimiter sniffing."""
from __future__ import annotations
import csv
import io
import json
import zipfile
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, inspect

from .config import SAMPLE_DIR

ENCODINGS = ["utf-8", "utf-8-sig", "latin-1", "cp1252", "utf-16"]


def detect_encoding(raw: bytes) -> str:
    try:
        import chardet  # optional dependency
        guess = chardet.detect(raw[:200_000])
        if guess and guess.get("encoding") and (guess.get("confidence") or 0) > 0.6:
            return guess["encoding"]
    except Exception:
        pass
    for enc in ENCODINGS:
        try:
            raw[:200_000].decode(enc)
            return enc
        except Exception:
            continue
    return "utf-8"


def detect_delimiter(text: str) -> str:
    sample = "\n".join(text.splitlines()[:20])
    try:
        return csv.Sniffer().sniff(sample, delimiters=",;\t|").delimiter
    except Exception:
        counts = {d: sample.count(d) for d in [",", ";", "\t", "|"]}
        return max(counts, key=counts.get) if max(counts.values()) else ","


def read_csv_bytes(raw: bytes, encoding: str | None = None, delimiter: str | None = None):
    enc = encoding or detect_encoding(raw)
    text = raw.decode(enc, errors="replace")
    sep = delimiter or detect_delimiter(text)
    df = pd.read_csv(io.StringIO(text), sep=sep, engine="python")
    return df, {"encoding": enc, "delimiter": repr(sep)}


def read_excel_bytes(raw: bytes, sheet=0):
    xls = pd.ExcelFile(io.BytesIO(raw))
    sheet_name = xls.sheet_names[sheet] if isinstance(sheet, int) else sheet
    return xls.parse(sheet_name), {"sheets": xls.sheet_names, "sheet": sheet_name}


def read_json_bytes(raw: bytes):
    enc = detect_encoding(raw)
    payload = json.loads(raw.decode(enc, errors="replace"))
    if isinstance(payload, dict):
        for v in payload.values():
            if isinstance(v, list):
                payload = v
                break
    return pd.json_normalize(payload), {"encoding": enc}


def read_zip_bytes(raw: bytes) -> dict[str, pd.DataFrame]:
    out: dict[str, pd.DataFrame] = {}
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        for info in z.infolist():
            if info.is_dir() or info.filename.startswith("__MACOSX"):
                continue
            ext = Path(info.filename).suffix.lower()
            data = z.read(info)
            try:
                if ext == ".csv":
                    out[Path(info.filename).name], _ = read_csv_bytes(data)
                elif ext in (".xlsx", ".xls"):
                    out[Path(info.filename).name], _ = read_excel_bytes(data)
                elif ext == ".json":
                    out[Path(info.filename).name], _ = read_json_bytes(data)
            except Exception:
                continue
    return out


def load_any(filename: str, raw: bytes):
    """Return (dict_of_dataframes, meta)."""
    ext = Path(filename).suffix.lower()
    if ext == ".csv" or ext == ".txt":
        df, meta = read_csv_bytes(raw)
        return {Path(filename).stem: df}, meta
    if ext in (".xlsx", ".xls", ".xlsm"):
        xls = pd.ExcelFile(io.BytesIO(raw))
        return ({s: xls.parse(s) for s in xls.sheet_names}, {"sheets": xls.sheet_names})
    if ext == ".json":
        df, meta = read_json_bytes(raw)
        return {Path(filename).stem: df}, meta
    if ext == ".zip":
        frames = read_zip_bytes(raw)
        return frames, {"files": list(frames)}
    if ext in (".db", ".sqlite", ".sqlite3"):
        tmp = Path("/tmp") / Path(filename).name
        tmp.write_bytes(raw)
        return sql_tables(f"sqlite:///{tmp}"), {"uri": f"sqlite:///{tmp}"}
    raise ValueError(f"Unsupported file type: {ext}")


def sql_tables(uri: str, limit: int | None = None) -> dict[str, pd.DataFrame]:
    eng = create_engine(uri)
    frames = {}
    for t in inspect(eng).get_table_names():
        q = f"SELECT * FROM {t}" + (f" LIMIT {int(limit)}" if limit else "")
        frames[t] = pd.read_sql(q, eng)
    return frames


def sql_query(uri: str, sql: str) -> pd.DataFrame:
    return pd.read_sql(sql, create_engine(uri))


def validate(df: pd.DataFrame) -> list[tuple[str, str]]:
    """Return a list of (level, message) validation findings."""
    out = []
    if df.empty:
        out.append(("error", "Dataset contains 0 rows."))
        return out
    out.append(("ok", f"Loaded {len(df):,} rows x {df.shape[1]} columns."))
    unnamed = [c for c in df.columns if str(c).startswith("Unnamed")]
    if unnamed:
        out.append(("warn", f"{len(unnamed)} unnamed column(s) detected — consider renaming or dropping."))
    dupes = int(df.duplicated().sum())
    if dupes:
        out.append(("warn", f"{dupes:,} duplicate row(s) found."))
    nulls = float(df.isna().mean().mean() * 100)
    if nulls > 20:
        out.append(("warn", f"High missingness: {nulls:.1f}% of all cells are empty."))
    elif nulls > 0:
        out.append(("ok", f"Missing values: {nulls:.1f}% of cells."))
    const = [c for c in df.columns if df[c].nunique(dropna=False) <= 1]
    if const:
        out.append(("warn", f"{len(const)} constant column(s): {', '.join(map(str, const[:5]))}"))
    return out


def load_sample() -> tuple[str, pd.DataFrame]:
    path = SAMPLE_DIR / "sales_2024.csv"
    if not path.exists():
        from scripts.generate_sample_data import build
        build(path)
    return "Sales_2024.csv", pd.read_csv(path)
