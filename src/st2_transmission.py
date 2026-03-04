"""
st2_transmission.py
Reusable helpers for the ST2 geopolitical risk transmission workflow.
"""

from __future__ import annotations

import logging
import numpy as np
import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)


def _ensure_date_column(df: pd.DataFrame, date_col: str = "date") -> pd.DataFrame:
    """Return a copy with a normalized monthly datetime column."""
    if date_col not in df.columns:
        if df.index.name == date_col:
            df = df.reset_index()
        else:
            raise KeyError(f"Missing '{date_col}' column")

    out = df.copy()
    out[date_col] = pd.to_datetime(out[date_col], errors="coerce")
    out = out.dropna(subset=[date_col])
    out[date_col] = out[date_col].dt.to_period("M").dt.to_timestamp()
    return out.sort_values(date_col)


def merge_monthly_series(
    frames: dict[str, pd.DataFrame],
    date_col: str = "date",
    fill_limit: int = 2,
) -> pd.DataFrame:
    """
    Merge multiple monthly DataFrames on a shared date column.

    Column names are prefixed with the provided dict key to avoid collisions,
    except for the date column.
    """
    if not frames:
        return pd.DataFrame(columns=[date_col])

    merged: pd.DataFrame | None = None

    for prefix, frame in frames.items():
        current = _ensure_date_column(frame, date_col=date_col)
        rename_map = {
            col: f"{prefix}_{col}"
            for col in current.columns
            if col != date_col
        }
        current = current.rename(columns=rename_map)

        if merged is None:
            merged = current
        else:
            merged = merged.merge(current, on=date_col, how="outer")

    if merged is None:
        return pd.DataFrame(columns=[date_col])

    merged = merged.sort_values(date_col).reset_index(drop=True)
    value_cols = [col for col in merged.columns if col != date_col]
    if value_cols:
        merged[value_cols] = merged[value_cols].ffill(limit=fill_limit)

    log.info(
        "Merged monthly series: %s rows x %s cols",
        f"{merged.shape[0]:,}",
        merged.shape[1],
    )
    return merged


def compute_lag_profile(
    df: pd.DataFrame,
    lead_col: str,
    target_col: str,
    max_lag: int = 12,
) -> pd.DataFrame:
    """
    Compute correlations where `lead_col` at time t is compared with
    `target_col` at time t + lag.

    Positive lag means `lead_col` leads `target_col`.
    """
    if lead_col not in df.columns or target_col not in df.columns:
        missing = [col for col in [lead_col, target_col] if col not in df.columns]
        raise KeyError(f"Missing required columns: {missing}")

    rows: list[dict[str, float | int]] = []

    for lag in range(max_lag + 1):
        aligned = pd.DataFrame(
            {
                "lead": pd.to_numeric(df[lead_col], errors="coerce"),
                "target": pd.to_numeric(df[target_col], errors="coerce").shift(-lag),
            }
        ).dropna()

        corr = aligned["lead"].corr(aligned["target"]) if len(aligned) >= 3 else np.nan
        rows.append(
            {
                "lead_col": lead_col,
                "target_col": target_col,
                "lag_months": lag,
                "correlation": corr,
                "abs_correlation": abs(corr) if pd.notna(corr) else np.nan,
                "observations": int(len(aligned)),
            }
        )

    result = pd.DataFrame(rows).sort_values(
        ["abs_correlation", "lag_months"],
        ascending=[False, True],
    )
    return result.reset_index(drop=True)


def rank_target_lags(
    df: pd.DataFrame,
    lead_col: str,
    target_cols: list[str],
    max_lag: int = 12,
) -> pd.DataFrame:
    """Return the strongest lead-lag relationship for each target series."""
    ranked: list[pd.Series] = []

    for target_col in target_cols:
        if target_col not in df.columns:
            log.warning("Skipping missing target column: %s", target_col)
            continue

        profile = compute_lag_profile(
            df=df,
            lead_col=lead_col,
            target_col=target_col,
            max_lag=max_lag,
        )
        if not profile.empty:
            ranked.append(profile.iloc[0])

    if not ranked:
        return pd.DataFrame(
            columns=[
                "lead_col",
                "target_col",
                "lag_months",
                "correlation",
                "abs_correlation",
                "observations",
            ]
        )

    out = pd.DataFrame(ranked)
    return out.sort_values(
        ["abs_correlation", "lag_months"],
        ascending=[False, True],
    ).reset_index(drop=True)


def build_event_window(
    df: pd.DataFrame,
    event_date: str | pd.Timestamp,
    months_before: int = 6,
    months_after: int = 6,
    date_col: str = "date",
    columns: list[str] | None = None,
) -> pd.DataFrame:
    """
    Slice a monthly DataFrame around an event and add a relative month index.
    """
    frame = _ensure_date_column(df, date_col=date_col)
    event_ts = pd.Timestamp(event_date).to_period("M").to_timestamp()

    start = event_ts - pd.DateOffset(months=months_before)
    end = event_ts + pd.DateOffset(months=months_after)

    keep_cols = [date_col]
    if columns:
        keep_cols.extend([col for col in columns if col in frame.columns])
    else:
        keep_cols.extend([col for col in frame.columns if col != date_col])

    out = frame.loc[frame[date_col].between(start, end), keep_cols].copy()
    out["relative_month"] = (
        (out[date_col].dt.year - event_ts.year) * 12
        + (out[date_col].dt.month - event_ts.month)
    )
    return out.reset_index(drop=True)


def summarize_forward_response(
    df: pd.DataFrame,
    shock_col: str,
    response_col: str,
    horizon_months: int = 3,
    shock_quantile: float = 0.9,
) -> dict[str, float]:
    """
    Summarize the forward response in `response_col` after large shocks.

    A "shock" is any observation at or above the specified quantile of `shock_col`.
    """
    if shock_col not in df.columns or response_col not in df.columns:
        missing = [col for col in [shock_col, response_col] if col not in df.columns]
        raise KeyError(f"Missing required columns: {missing}")

    frame = df[[shock_col, response_col]].copy()
    frame[shock_col] = pd.to_numeric(frame[shock_col], errors="coerce")
    frame[response_col] = pd.to_numeric(frame[response_col], errors="coerce")
    frame = frame.dropna()

    if frame.empty:
        return {
            "shock_count": 0.0,
            "median_forward_change": np.nan,
            "p25_forward_change": np.nan,
            "p75_forward_change": np.nan,
        }

    threshold = frame[shock_col].quantile(shock_quantile)
    frame["forward_change"] = frame[response_col].shift(-horizon_months) - frame[response_col]
    shocks = frame.loc[frame[shock_col] >= threshold, "forward_change"].dropna()

    if shocks.empty:
        return {
            "shock_count": 0.0,
            "median_forward_change": np.nan,
            "p25_forward_change": np.nan,
            "p75_forward_change": np.nan,
        }

    return {
        "shock_count": float(len(shocks)),
        "median_forward_change": float(shocks.median()),
        "p25_forward_change": float(shocks.quantile(0.25)),
        "p75_forward_change": float(shocks.quantile(0.75)),
    }
