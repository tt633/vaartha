"""
CLI helper to rebuild ST2 master data and export ST2 -> ST1 transmission tables.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from config import ST1_PROC, ST2_PROC, TABLES
from st2_pipeline import export_transmission_tables, save_st2_master

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)


def load_parquet(path: Path, label: str) -> pd.DataFrame:
    """Load Parquet with lightweight logging for CLI use."""
    df = pd.read_parquet(path)
    log.info("Loaded %s: %s rows x %s cols", label, f"{df.shape[0]:,}", df.shape[1])
    return df


def main() -> int:
    gpr_path = ST2_PROC / "st2_gpr.parquet"
    gscpi_path = ST2_PROC / "st2_gscpi.parquet"
    macro_path = ST2_PROC / "st2_macro.parquet"
    etf_path = ST2_PROC / "st2_etfs.parquet"
    master_path = ST2_PROC / "st2_master.parquet"
    st1_prices_path = ST1_PROC / "st1_prices.parquet"

    required_st2 = [gpr_path, gscpi_path]
    missing_required = [path for path in required_st2 if not path.exists()]
    if missing_required:
        for path in missing_required:
            log.error("Missing required ST2 input: %s", path)
        log.error("Run notebooks/02_ST2_geopolitical_risk_ingestion.ipynb first.")
        return 1

    gpr_df = load_parquet(gpr_path, "GPR")
    gscpi_df = load_parquet(gscpi_path, "GSCPI")
    macro_df = load_parquet(macro_path, "FRED Macro") if macro_path.exists() else None
    etf_df = load_parquet(etf_path, "ETFs") if etf_path.exists() else None

    master_df = save_st2_master(
        output_path=master_path,
        gpr_df=gpr_df,
        gscpi_df=gscpi_df,
        macro_df=macro_df,
        etf_df=etf_df,
    )

    if not st1_prices_path.exists():
        log.warning("ST1 prices not found at %s. Skipping ST2-ST1 transmission export.", st1_prices_path)
        return 0

    st1_prices_df = load_parquet(st1_prices_path, "ST1 Prices")
    export_transmission_tables(
        master_df=master_df,
        st1_prices_df=st1_prices_df,
        output_dir=TABLES,
        max_lag=12,
    )
    log.info("ST2 transmission export complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
