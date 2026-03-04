"""
Preprocess ST2 raw sources (GPR + GSCPI) into processed Parquet tables.

This script mirrors notebook-level preprocessing and writes:
- data/processed/ST2/st2_gpr.parquet
- data/processed/ST2/st2_gscpi.parquet
- data/processed/ST2/st2_master.parquet
"""

from __future__ import annotations

import importlib.util
import logging
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from config import END_YEAR, GPR_SMOOTH_WINDOW, START_YEAR, ST2_PROC, ST2_RAW
from st2_pipeline import save_st2_master

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)


def save_parquet(df: pd.DataFrame, path: Path, label: str = "") -> None:
    """Save DataFrame as parquet with consistent CLI logging."""
    df.to_parquet(path, index=True)
    log.info("Saved %s: %s rows x %s cols -> %s", label or path.name, f"{df.shape[0]:,}", df.shape[1], path)


def _read_excel_with_xls_fallback(path: Path, sheet_name: str | int = 0) -> pd.DataFrame:
    """Read Excel path, handling legacy .xls only if xlrd is available."""
    suffix = path.suffix.lower()
    if suffix == ".xlsx":
        return pd.read_excel(path, sheet_name=sheet_name)
    if suffix == ".xls":
        if importlib.util.find_spec("xlrd") is None:
            raise RuntimeError(
                f"{path.name} is .xls but xlrd is not installed. Convert to .xlsx first."
            )
        return pd.read_excel(path, sheet_name=sheet_name, engine="xlrd")
    raise ValueError(f"Unsupported Excel extension: {path.suffix}")


def load_gpr(path: Path) -> pd.DataFrame:
    """Load and preprocess Iacoviello GPR workbook."""
    if not path.exists():
        raise FileNotFoundError(f"GPR file not found: {path}")

    df = _read_excel_with_xls_fallback(path, sheet_name=0)
    df.columns = df.columns.astype(str).str.strip().str.lower()

    date_col = next((c for c in df.columns if c in ["month", "date", "year_month"]), df.columns[0])
    df = df.rename(columns={date_col: "date"})
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    # Keep only rows that contain actual monthly GPR values.
    for col in ["gpr", "gprt", "gpra"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    keep_mask = pd.Series(False, index=df.index)
    for col in ["gpr", "gprt", "gpra"]:
        if col in df.columns:
            keep_mask |= df[col].notna()
    df = df.loc[keep_mask].copy()

    if df.empty:
        raise RuntimeError("GPR preprocessing produced an empty frame.")

    # Retain date + GPR-family columns only.
    gpr_cols = [c for c in df.columns if c.startswith("gpr")]
    df = df[["date", *gpr_cols]].copy()

    # Coerce all value columns numeric.
    for col in gpr_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    for col in ["gpr", "gprt", "gpra"]:
        if col in df.columns:
            df[f"{col}_smooth"] = df[col].rolling(GPR_SMOOTH_WINDOW, min_periods=1).mean()

    value_cols = [c for c in df.columns if c != "date"]
    df[value_cols] = df[value_cols].ffill(limit=2)

    df = df.dropna(subset=["date"]).sort_values("date")
    df = df[(df["date"].dt.year >= START_YEAR) & (df["date"].dt.year <= END_YEAR)]
    df["date"] = df["date"].dt.to_period("M").dt.to_timestamp()

    log.info("GPR loaded: %s rows x %s cols", f"{df.shape[0]:,}", df.shape[1])
    return df.reset_index(drop=True)


def _read_best_gscpi_excel(path: Path) -> pd.DataFrame:
    """
    Select the most plausible GSCPI tab by scoring sheets on valid date/value rows.
    """
    xls = pd.ExcelFile(path)
    candidates: list[tuple[int, pd.DataFrame]] = []

    for sheet in xls.sheet_names:
        try:
            frame = _read_excel_with_xls_fallback(path, sheet_name=sheet)
        except Exception:
            continue
        if frame.empty:
            continue

        cols = frame.columns.astype(str).str.strip().str.lower()
        frame.columns = cols

        date_col = next((c for c in cols if "date" in c or "month" in c or "period" in c), None)
        value_col = next((c for c in cols if "gscpi" in c or "index" in c or "pressure" in c), None)
        if date_col is None or value_col is None:
            continue

        probe = frame[[date_col, value_col]].copy()
        probe[date_col] = pd.to_datetime(probe[date_col], errors="coerce")
        probe[value_col] = pd.to_numeric(probe[value_col], errors="coerce")
        score = int(probe.dropna().shape[0])
        if score > 0:
            candidates.append((score, frame))

    if not candidates:
        raise RuntimeError(f"Could not locate a usable GSCPI sheet in {path.name}")

    candidates.sort(key=lambda x: x[0], reverse=True)
    return candidates[0][1]


def load_gscpi(path: Path) -> pd.DataFrame:
    """Load and preprocess NY Fed GSCPI data from CSV/XLSX/XLS."""
    if not path.exists():
        raise FileNotFoundError(f"GSCPI file not found: {path}")

    if path.suffix.lower() == ".csv":
        df = pd.read_csv(path)
    else:
        df = _read_best_gscpi_excel(path)

    df.columns = df.columns.astype(str).str.strip().str.lower()
    date_col = next((c for c in df.columns if "date" in c or "month" in c or "period" in c), df.columns[0])
    gscpi_col = next(
        (c for c in df.columns if "gscpi" in c or "index" in c or "pressure" in c),
        df.columns[1],
    )

    out = df.rename(columns={date_col: "date", gscpi_col: "gscpi"})[["date", "gscpi"]].copy()
    out["date"] = pd.to_datetime(out["date"], errors="coerce")
    out["gscpi"] = pd.to_numeric(out["gscpi"], errors="coerce")
    out = out.dropna(subset=["date", "gscpi"]).sort_values("date")
    out = out[(out["date"].dt.year >= START_YEAR) & (out["date"].dt.year <= END_YEAR)]
    out["date"] = out["date"].dt.to_period("M").dt.to_timestamp()

    log.info("GSCPI loaded: %s rows x %s cols", f"{out.shape[0]:,}", out.shape[1])
    return out.reset_index(drop=True)


def main() -> int:
    st2_proc = ST2_PROC
    st2_proc.mkdir(parents=True, exist_ok=True)

    gpr_candidates = [
        ST2_RAW / "data_gpr_export.xlsx",
        ST2_RAW / "data_gpr_export.xls",
    ]
    gscpi_candidates = [
        ST2_RAW / "gscpi.csv",
        ST2_RAW / "gscpi.xlsx",
        ST2_RAW / "gscpi_data.xlsx",
        ST2_RAW / "gscpi_data.xls",
        Path.home() / "Downloads" / "gscpi_data.xlsx",
        Path.home() / "Downloads" / "gscpi_data.xls",
    ]

    gpr_path = next((p for p in gpr_candidates if p.exists()), None)
    gscpi_path = next((p for p in gscpi_candidates if p.exists()), None)

    if gpr_path is None or gscpi_path is None:
        if gpr_path is None:
            log.error("Missing GPR source in: %s", ", ".join(str(p) for p in gpr_candidates))
        if gscpi_path is None:
            log.error("Missing GSCPI source in: %s", ", ".join(str(p) for p in gscpi_candidates))
        return 1

    log.info("Using GPR source: %s", gpr_path)
    log.info("Using GSCPI source: %s", gscpi_path)

    gpr_df = load_gpr(gpr_path)
    gscpi_df = load_gscpi(gscpi_path)

    save_parquet(gpr_df, st2_proc / "st2_gpr.parquet", "GPR")
    save_parquet(gscpi_df, st2_proc / "st2_gscpi.parquet", "GSCPI")

    master = save_st2_master(
        output_path=st2_proc / "st2_master.parquet",
        gpr_df=gpr_df,
        gscpi_df=gscpi_df,
    )
    if master.empty:
        log.error("ST2 master is empty after preprocessing.")
        return 1

    log.info("ST2 preprocessing complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
