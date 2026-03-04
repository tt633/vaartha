"""
st2_pipeline.py
Pipeline helpers for ST2 ingestion and transmission-table generation.
"""

from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd

from st2_transmission import (
    compute_lag_profile,
    merge_monthly_series,
    rank_target_lags,
    summarize_forward_response,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)


def _coerce_monthly_date(df: pd.DataFrame, date_col: str = "date") -> pd.DataFrame:
    """Return a copy with a normalized month-start datetime column."""
    out = df.copy()
    out[date_col] = pd.to_datetime(out[date_col], errors="coerce")
    out = out.dropna(subset=[date_col]).sort_values(date_col)
    out[date_col] = out[date_col].dt.to_period("M").dt.to_timestamp()
    return out.reset_index(drop=True)


def build_st2_master(
    gpr_df: pd.DataFrame | None = None,
    gscpi_df: pd.DataFrame | None = None,
    macro_df: pd.DataFrame | None = None,
    etf_df: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """
    Merge ST2 source tables into one monthly panel without renaming existing columns.
    """
    frames: list[pd.DataFrame] = []

    for frame in [gpr_df, gscpi_df, macro_df, etf_df]:
        if frame is None or frame.empty:
            continue
        if "date" not in frame.columns:
            continue
        frames.append(_coerce_monthly_date(frame))

    if not frames:
        log.warning("No ST2 frames provided; cannot build master table.")
        return pd.DataFrame()

    master = frames[0]
    for frame in frames[1:]:
        overlap = [col for col in frame.columns if col != "date" and col in master.columns]
        if overlap:
            frame = frame.drop(columns=overlap)
        master = master.merge(frame, on="date", how="outer")

    master = master.sort_values("date").reset_index(drop=True)
    value_cols = [col for col in master.columns if col != "date"]
    if value_cols:
        master[value_cols] = master[value_cols].ffill(limit=2)

    log.info("Built ST2 master table: %s rows x %s cols", f"{master.shape[0]:,}", master.shape[1])
    return master


def save_st2_master(
    output_path: Path,
    gpr_df: pd.DataFrame | None = None,
    gscpi_df: pd.DataFrame | None = None,
    macro_df: pd.DataFrame | None = None,
    etf_df: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """Build and save the ST2 master parquet."""
    master = build_st2_master(
        gpr_df=gpr_df,
        gscpi_df=gscpi_df,
        macro_df=macro_df,
        etf_df=etf_df,
    )
    if not master.empty:
        master.to_parquet(output_path, index=True)
        log.info(
            "Saved ST2 Master: %s rows x %s cols -> %s",
            f"{master.shape[0]:,}",
            master.shape[1],
            output_path,
        )
    return master


def build_st1_price_panel(st1_prices_df: pd.DataFrame) -> pd.DataFrame:
    """
    Pivot ST1 monthly commodity prices to a wide panel:
    date | price_<commodity> | vol_<commodity>
    """
    required = {"date", "commodity", "price_usd_mt"}
    missing = sorted(required - set(st1_prices_df.columns))
    if missing:
        raise KeyError(f"Missing required ST1 price columns: {missing}")

    frame = _coerce_monthly_date(st1_prices_df[["date", "commodity", "price_usd_mt"]].copy())
    frame["commodity_key"] = (
        frame["commodity"]
        .astype(str)
        .str.strip()
        .str.lower()
        .str.replace(r"[^a-z0-9]+", "_", regex=True)
        .str.strip("_")
    )

    price_panel = (
        frame.pivot_table(
            index="date",
            columns="commodity_key",
            values="price_usd_mt",
            aggfunc="mean",
        )
        .sort_index()
        .add_prefix("price_")
        .reset_index()
    )

    if "price_vol_12m" in st1_prices_df.columns:
        vol_frame = _coerce_monthly_date(
            st1_prices_df[["date", "commodity", "price_vol_12m"]].copy()
        )
        vol_frame["commodity_key"] = (
            vol_frame["commodity"]
            .astype(str)
            .str.strip()
            .str.lower()
            .str.replace(r"[^a-z0-9]+", "_", regex=True)
            .str.strip("_")
        )
        vol_panel = (
            vol_frame.pivot_table(
                index="date",
                columns="commodity_key",
                values="price_vol_12m",
                aggfunc="mean",
            )
            .sort_index()
            .add_prefix("vol_")
            .reset_index()
        )
        price_panel = price_panel.merge(vol_panel, on="date", how="left")

    log.info(
        "Built ST1 price panel: %s rows x %s cols",
        f"{price_panel.shape[0]:,}",
        price_panel.shape[1],
    )
    return price_panel


def build_st2_st1_bridge(master_df: pd.DataFrame, st1_prices_df: pd.DataFrame) -> pd.DataFrame:
    """
    Merge the ST2 master panel with wide ST1 commodity prices on monthly date.
    """
    if master_df.empty:
        raise ValueError("master_df is empty")

    price_panel = build_st1_price_panel(st1_prices_df)
    bridge = merge_monthly_series(
        {
            "st2": master_df,
            "st1": price_panel,
        }
    )

    rename_map = {}
    for col in bridge.columns:
        if col.startswith("st2_"):
            rename_map[col] = col.replace("st2_", "", 1)
        elif col.startswith("st1_price_"):
            rename_map[col] = col.replace("st1_", "", 1)
        elif col.startswith("st1_vol_"):
            rename_map[col] = col.replace("st1_", "", 1)

    bridge = bridge.rename(columns=rename_map)
    log.info(
        "Built ST2-ST1 bridge: %s rows x %s cols",
        f"{bridge.shape[0]:,}",
        bridge.shape[1],
    )
    return bridge


def export_transmission_tables(
    master_df: pd.DataFrame,
    st1_prices_df: pd.DataFrame,
    output_dir: Path,
    max_lag: int = 12,
) -> dict[str, pd.DataFrame]:
    """
    Generate CSV-ready transmission tables for ST2:
    - GPR -> GSCPI lag profile
    - GSCPI -> commodity strongest lag
    - GPR -> commodity strongest lag
    - forward response summaries after large GPR shocks
    """
    if master_df.empty:
        raise ValueError("master_df is empty")

    bridge = build_st2_st1_bridge(master_df, st1_prices_df)
    commodity_cols = [col for col in bridge.columns if col.startswith("price_")]

    if "gpr" not in bridge.columns or "gscpi" not in bridge.columns:
        raise KeyError("Bridge must contain 'gpr' and 'gscpi' columns")

    gpr_to_gscpi = compute_lag_profile(
        df=bridge,
        lead_col="gpr",
        target_col="gscpi",
        max_lag=max_lag,
    )

    gscpi_to_commodities = rank_target_lags(
        df=bridge,
        lead_col="gscpi",
        target_cols=commodity_cols,
        max_lag=max_lag,
    )

    gpr_to_commodities = rank_target_lags(
        df=bridge,
        lead_col="gpr",
        target_cols=commodity_cols,
        max_lag=max_lag,
    )

    forward_rows = []
    for col in commodity_cols:
        summary = summarize_forward_response(
            df=bridge,
            shock_col="gpr",
            response_col=col,
            horizon_months=3,
            shock_quantile=0.9,
        )
        summary["response_col"] = col
        forward_rows.append(summary)

    forward_response = pd.DataFrame(forward_rows).sort_values(
        "median_forward_change",
        ascending=False,
        na_position="last",
    )

    output_dir.mkdir(parents=True, exist_ok=True)
    outputs = {
        "st2_gpr_to_gscpi_lag_profile.csv": gpr_to_gscpi,
        "st2_gscpi_to_commodity_lag_rank.csv": gscpi_to_commodities,
        "st2_gpr_to_commodity_lag_rank.csv": gpr_to_commodities,
        "st2_gpr_shock_forward_response.csv": forward_response,
        "st2_st1_bridge_preview.csv": bridge,
    }

    for filename, table in outputs.items():
        table.to_csv(output_dir / filename, index=False)
        log.info("Saved transmission table: %s", output_dir / filename)

    return {
        "gpr_to_gscpi": gpr_to_gscpi,
        "gscpi_to_commodities": gscpi_to_commodities,
        "gpr_to_commodities": gpr_to_commodities,
        "forward_response": forward_response,
        "bridge": bridge,
    }
