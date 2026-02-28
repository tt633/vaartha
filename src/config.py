"""
config.py — Team 7 Lambda
Central configuration: paths, constants, country lists, HS codes.
Import this at the top of every notebook/script.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()  # loads .env from project root

# ── Root Paths ──────────────────────────────────────────────────────────────
ROOT      = Path(__file__).resolve().parent.parent   # lambda/
DATA_RAW  = ROOT / "data" / "raw"
DATA_PROC = ROOT / "data" / "processed"
OUTPUTS   = ROOT / "outputs"
CHARTS    = OUTPUTS / "charts"
TABLES    = OUTPUTS / "tables"

# ── Per-Subtopic Raw Data Paths ────────────────────────────────────────────
# ST1 — Critical Minerals
ST1_RAW       = DATA_RAW  / "ST1"
ST1_BGS       = ST1_RAW   / "bgs"        # BGS World Mineral Statistics CSVs
ST1_WORLDBANK = ST1_RAW   / "worldbank"  # World Bank Pink Sheet
ST1_OECD      = ST1_RAW   / "oecd"       # OECD Export Restrictions

# ST2 — Geopolitical Risk
ST2_RAW   = DATA_RAW / "ST2"             # GPR, GSCPI, FRED, yfinance

# ST3 — Energy Policy
ST3_RAW   = DATA_RAW / "ST3"             # OWID, Ember, RFF carbon pricing

# ST4 — Corporate CapEx
ST4_RAW   = DATA_RAW / "ST4"             # SEC EDGAR XBRL

# ── Per-Subtopic Processed Data Paths ─────────────────────────────────────
ST1_PROC  = DATA_PROC / "ST1"
ST2_PROC  = DATA_PROC / "ST2"
ST3_PROC  = DATA_PROC / "ST3"
ST4_PROC  = DATA_PROC / "ST4"

for p in [ST1_BGS, ST1_WORLDBANK, ST1_OECD,
          ST2_RAW, ST3_RAW, ST4_RAW,
          ST1_PROC, ST2_PROC, ST3_PROC, ST4_PROC,
          CHARTS, TABLES]:
    p.mkdir(parents=True, exist_ok=True)

# ── API Keys ───────────────────────────────────────────────────────────────
FRED_API_KEY   = os.getenv("FRED_API_KEY", "")
SEC_USER_AGENT = os.getenv("SEC_USER_AGENT", "TeamLambda student@school.edu")
IEA_TOKEN      = os.getenv("IEA_TOKEN", "")

# ── Focal Countries (ISO-3166-1 alpha-3) ───────────────────────────────────
FOCAL_COUNTRIES = {
    "USA": "United States",
    "CHN": "China",
    "DEU": "Germany",
    "FRA": "France",
    "IND": "India",
    "JPN": "Japan",
    "GBR": "United Kingdom",
    "AUS": "Australia",
    "BRA": "Brazil",
    "ZAF": "South Africa",
    "CHL": "Chile",          # world's largest lithium producer
    "COD": "Dem. Rep. Congo", # world's largest cobalt producer
}

# ── Critical Mineral HS6 Codes ─────────────────────────────────────────────
# Use these to filter BACI / UN Comtrade trade data
MINERAL_HS_CODES = {
    "Lithium carbonate":   "283691",
    "Lithium oxide":       "282520",
    "Cobalt ores":         "260500",
    "Cobalt compounds":    "282200",
    "Gallium":             "811292",
    "Germanium":           "811294",
    "Rare earth metals":   "280530",
    "Natural graphite":    "250410",
    "Silicon":             "280461",
    "Nickel ores":         "260400",
    "Copper ores":         "260300",
    "Manganese ores":      "260200",
}

# ── FRED Series IDs ────────────────────────────────────────────────────────
FRED_SERIES = {
    "CPI":           "CPIAUCSL",      # Consumer Price Index (monthly)
    "YIELD_CURVE":   "T10Y2Y",        # 10Y-2Y spread (daily → resample monthly)
    "OIL_PRICE":     "DCOILWTICO",    # WTI crude (daily)
    "GOLD_PRICE":    "GOLDPMGBD228NLBM",  # Gold (daily)
    "GDP_GROWTH":    "A191RL1Q225SBEA",   # Real GDP growth (quarterly)
    "INDUSTRIAL_PROD": "INDPRO",      # Industrial production index (monthly)
}

# ── S&P 500 Sector ETFs ───────────────────────────────────────────────────
SECTOR_ETFS = {
    "Technology":   "XLK",
    "Energy":       "XLE",
    "Materials":    "XLB",
    "Semiconductors": "SOXX",
    "Utilities":    "XLU",
    "Industrials":  "XLI",
}

# ── Key Companies for CapEx Analysis (ticker → CIK) ───────────────────────
# CIKs are verified from SEC EDGAR
CAPEX_COMPANIES = {
    # Semiconductors
    "NVDA": {"cik": "0001045810", "sector": "semiconductor", "name": "NVIDIA"},
    "INTC": {"cik": "0000050863", "sector": "semiconductor", "name": "Intel"},
    "AMD":  {"cik": "0000002488", "sector": "semiconductor", "name": "AMD"},
    # Hyperscalers
    "MSFT": {"cik": "0000789019", "sector": "hyperscaler",   "name": "Microsoft"},
    "GOOGL":{"cik": "0001652044", "sector": "hyperscaler",   "name": "Alphabet"},
    "AMZN": {"cik": "0001018724", "sector": "hyperscaler",   "name": "Amazon"},
    # Energy
    "XOM":  {"cik": "0000034088", "sector": "energy",        "name": "ExxonMobil"},
    "NEE":  {"cik": "0000753308", "sector": "energy",        "name": "NextEra Energy"},
    # Critical minerals / mining
    "ALB":  {"cik": "0000915779", "sector": "mining",        "name": "Albemarle"},  # lithium
    "MP":   {"cik": "0001801368", "sector": "mining",        "name": "MP Materials"}, # rare earths
}

# ── XBRL Concept Names (for SEC EDGAR API) ────────────────────────────────
XBRL_CONCEPTS = {
    "capex":    "PaymentsToAcquirePropertyPlantAndEquipment",
    "rd":       "ResearchAndDevelopmentExpense",
    "revenue":  "Revenues",
    "ebitda":   "OperatingIncomeLoss",  # proxy; true EBITDA needs D&A add-back
}

# ── Analysis Parameters ────────────────────────────────────────────────────
START_YEAR   = 2010   # analysis window start — 2010: EDGAR XBRL reliable, OECD clean
END_YEAR     = 2022   # analysis window end   — 2022: last year all datasets overlap (RFF carbon ends 2020, OWID 2023)
GPR_SMOOTH_WINDOW = 3  # rolling mean months for GPR smoothing
HHI_HIGH_THRESHOLD = 0.25  # HHI above this = high concentration
