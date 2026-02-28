"""
utils.py — Team 7 Lambda
Shared utility functions: country name normalization, HHI computation,
data saving/loading helpers, and plot styling.
"""

import logging
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pycountry

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
log = logging.getLogger(__name__)


# ── Country Name → ISO-3166-1 alpha-3 ─────────────────────────────────────

# Manual overrides for names that pycountry won't match automatically
_COUNTRY_OVERRIDES = {
    "russia":                    "RUS",
    "iran":                      "IRN",
    "south korea":               "KOR",
    "korea, republic of":        "KOR",
    "taiwan":                    "TWN",
    "taiwan, province of china": "TWN",
    "vietnam":                   "VNM",
    "viet nam":                  "VNM",
    "bolivia":                   "BOL",
    "congo, democratic republic": "COD",
    "democratic republic of the congo": "COD",
    "drc":                       "COD",
    "czech republic":            "CZE",
    "czechia":                   "CZE",
    "united states":             "USA",
    "united states of america":  "USA",
    "uk":                        "GBR",
    "united kingdom":            "GBR",
}

def to_iso3(name: str) -> str | None:
    """
    Convert a country name string to ISO-3166-1 alpha-3 code.
    Returns None if the country cannot be matched.
    
    Usage:
        df["iso3"] = df["country"].map(to_iso3)
    """
    if pd.isna(name):
        return None
    key = str(name).strip().lower()
    if key in _COUNTRY_OVERRIDES:
        return _COUNTRY_OVERRIDES[key]
    try:
        result = pycountry.countries.search_fuzzy(name)
        return result[0].alpha_3
    except LookupError:
        log.warning(f"Could not map country: '{name}'")
        return None


def normalize_countries(df: pd.DataFrame, col: str, out_col: str = "iso3") -> pd.DataFrame:
    """
    Add an ISO-3 column to a DataFrame by normalizing a country name column.
    Logs how many rows failed to map.
    """
    df = df.copy()
    df[out_col] = df[col].map(to_iso3)
    failed = df[out_col].isna().sum()
    if failed:
        log.warning(f"{failed} rows could not be mapped to ISO-3 from column '{col}'")
        log.warning(f"Unmapped values: {df.loc[df[out_col].isna(), col].unique()[:10]}")
    return df


# ── HHI (Herfindahl-Hirschman Index) ─────────────────────────────────────

def compute_hhi(df: pd.DataFrame, group_col: str, value_col: str) -> pd.Series:
    """
    Compute HHI for each group in group_col based on shares of value_col.
    
    HHI = Σ(share_i²) where share_i = value_i / Σ(value)
    HHI range: 0 (perfectly competitive) to 1 (monopoly)
    
    Args:
        df: DataFrame with at least group_col and value_col
        group_col: column defining groups (e.g., "year" or "mineral")  
        value_col: column with production/trade values
    
    Returns:
        Series indexed by group_col with HHI values
    
    Example:
        hhi = compute_hhi(minerals_df, group_col="year", value_col="production_mt")
    """
    def _hhi(series):
        total = series.sum()
        if total == 0:
            return np.nan
        shares = series / total
        return (shares ** 2).sum()
    
    return df.groupby(group_col)[value_col].apply(_hhi)


def flag_concentration(hhi_series: pd.Series, threshold: float = 0.25) -> pd.Series:
    """
    Returns a boolean Series: True where HHI exceeds threshold (high concentration).
    DOJ threshold: 0.15 moderate, 0.25 high concentration.
    """
    return hhi_series > threshold


# ── Temporal Join ─────────────────────────────────────────────────────────

def backward_merge(
    left: pd.DataFrame,
    right: pd.DataFrame,
    on: str = "date",
    tolerance: str = "31D"
) -> pd.DataFrame:
    """
    Merge two time-indexed DataFrames using backward-looking merge_asof.
    Prevents look-ahead bias: each row in `left` gets the most recent
    value from `right` that occurred ON OR BEFORE the left date.
    
    Both DataFrames must be sorted by `on` column before calling.
    
    Args:
        left:      higher-frequency DataFrame (e.g., daily ETF prices)
        right:     lower-frequency DataFrame (e.g., monthly GPR)
        on:        datetime column name (must exist in both)
        tolerance: max backward look distance (pandas Timedelta string)
    
    Example:
        merged = backward_merge(etf_daily, gpr_monthly, on="date", tolerance="31D")
    """
    left  = left.sort_values(on)
    right = right.sort_values(on)
    return pd.merge_asof(
        left, right,
        on=on,
        direction="backward",
        tolerance=pd.Timedelta(tolerance)
    )


# ── Data I/O ──────────────────────────────────────────────────────────────

def save_parquet(df: pd.DataFrame, path, label: str = "") -> None:
    """Save DataFrame as Parquet with logging."""
    df.to_parquet(path, index=True)
    log.info(f"Saved {label or path}: {df.shape[0]:,} rows × {df.shape[1]} cols → {path}")


def load_parquet(path, label: str = "") -> pd.DataFrame:
    """Load Parquet with logging."""
    df = pd.read_parquet(path)
    log.info(f"Loaded {label or path}: {df.shape[0]:,} rows × {df.shape[1]} cols")
    return df


# ── Plot Styling ──────────────────────────────────────────────────────────

TEAM_PALETTE = {
    "minerals":    "#00FFB2",   # green — ST1
    "geopolitical":"#FF6B35",   # orange — ST2
    "energy":      "#A78BFA",   # purple — ST3
    "capex":       "#FACC15",   # yellow — ST4
    "neutral":     "#64748B",
    "highlight":   "#F472B6",
}

def set_style() -> None:
    """Apply consistent dark-theme matplotlib style for all project charts."""
    plt.rcParams.update({
        "figure.facecolor":  "#0A0A0F",
        "axes.facecolor":    "#0D0D1A",
        "axes.edgecolor":    "#1E1E2E",
        "axes.labelcolor":   "#94A3B8",
        "axes.titlecolor":   "#E2E8F0",
        "axes.titlesize":    13,
        "axes.labelsize":    11,
        "axes.grid":         True,
        "grid.color":        "#1E1E2E",
        "grid.linewidth":    0.8,
        "xtick.color":       "#475569",
        "ytick.color":       "#475569",
        "xtick.labelsize":   9,
        "ytick.labelsize":   9,
        "text.color":        "#94A3B8",
        "legend.facecolor":  "#0D0D1A",
        "legend.edgecolor":  "#1E1E2E",
        "legend.fontsize":   9,
        "figure.dpi":        150,
        "savefig.dpi":       150,
        "savefig.bbox":      "tight",
        "savefig.facecolor": "#0A0A0F",
        "font.family":       "monospace",
    })


def annotate_events(ax, events: list[tuple], y_frac: float = 0.92) -> None:
    """
    Add vertical event lines + labels to a time-series axis.
    
    Args:
        ax:      matplotlib Axes object
        events:  list of (date_str, label) tuples e.g. [("2022-02-24", "Ukraine")]
        y_frac:  vertical position of label (0=bottom, 1=top of y-axis)
    
    Example:
        annotate_events(ax, [
            ("2022-02-24", "Ukraine invasion"),
            ("2023-07-04", "China Ga/Ge controls"),
            ("2022-08-09", "CHIPS Act"),
        ])
    """
    ylim = ax.get_ylim()
    y_pos = ylim[0] + (ylim[1] - ylim[0]) * y_frac
    for date_str, label in events:
        ax.axvline(pd.Timestamp(date_str), color="#475569", linewidth=0.8, linestyle="--", alpha=0.6)
        ax.text(pd.Timestamp(date_str), y_pos, f" {label}", fontsize=7,
                color="#64748B", rotation=90, va="top", ha="right")


# ── Key Geopolitical Events (reuse across notebooks) ──────────────────────
KEY_EVENTS = [
    ("2001-09-11", "9/11"),
    ("2008-09-15", "GFC"),
    ("2010-09-01", "China REE quota"),
    ("2020-03-01", "COVID"),
    ("2022-02-24", "Ukraine invasion"),
    ("2022-08-09", "CHIPS Act"),
    ("2023-07-04", "China Ga/Ge controls"),
    ("2024-01-01", "US AI chip export controls"),
]
