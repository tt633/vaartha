# Raw Data Download Guide

Raw data files are **not committed** to this repo (too large). Download each file manually and place it in the folder shown below. Once in place, re-run the Phase 1 ingestion notebooks to regenerate the processed Parquets.

> **Note:** The `data/processed/` Parquets are already committed — you can skip straight to Phase 2 analysis without re-running ingestion.

---

## ST1 — Critical Minerals

### BGS World Mineral Statistics (`data/raw/ST1/bgs/`)
- **Source:** British Geological Survey World Mineral Statistics
- **URL:** https://www2.bgs.ac.uk/mineralsuk/statistics/worldStatistics.html
- **Files needed:** Individual mineral CSV files (cobalt, copper, lithium, etc.)
- **Format:** CSV, one file per mineral

### World Bank Pink Sheet (`data/raw/ST1/worldbank/`)
- **Source:** World Bank Commodity Markets
- **URL:** https://www.worldbank.org/en/research/commodity-markets
- **File needed:** `CMO-Historical-Data-Monthly.xlsx` (download "Pink Sheet")
- **Format:** Excel

### OECD Export Restrictions (`data/raw/ST1/oecd/`)
- **Source:** OECD Inventory of Export Restrictions on Industrial Raw Materials
- **URL:** https://qdd.oecd.org/subject.aspx?Subject=ExportRestrictions_IndustrialRawMaterials
- **File needed:** `export_restrictions.csv` (export the full dataset as CSV)
- **Format:** CSV

---

## ST2 — Geopolitical Risk

### GPR Index (`data/raw/ST2/`)
- **Source:** Matteo Iacoviello — Geopolitical Risk Index
- **URL:** https://www.matteoiacoviello.com/gpr.htm
- **File needed:** `data_gpr_export.xls` (click "Download data" on the page)
- **Format:** Excel

### NY Fed GSCPI (`data/raw/ST2/`)
- **Source:** Federal Reserve Bank of New York — Global Supply Chain Pressure Index
- **URL:** https://www.newyorkfed.org/research/policy/gscpi
- **File needed:** `gscpi_data.xlsx` or `gscpi.csv` (download from the data tab)
- **Format:** Excel or CSV

> **FRED & yfinance data** (macro series + ETF prices) are **auto-downloaded** by the notebook — no manual file needed. Requires a free FRED API key in `.env`.

---

## ST3 — Energy Policy

### OWID Energy Data (`data/raw/ST3/`)
- **Source:** Our World in Data — Energy Dataset
- **Auto-downloaded** by the notebook from:
  `https://raw.githubusercontent.com/owid/energy-data/master/owid-energy-data.csv`
- No manual download needed.

### RFF World Carbon Pricing Database (`data/raw/ST3/`)
- **Source:** Resources for the Future — World Carbon Pricing Database
- **Auto-downloaded** by the notebook from GitHub:
  `https://github.com/g-dolphin/WorldCarbonPricingDatabase`
- No manual download needed.

---

## ST4 — Corporate CapEx

### SEC EDGAR XBRL API
- **Auto-fetched** by the notebook directly from `https://data.sec.gov/api/xbrl/`
- No manual download needed.
- Requires `SEC_USER_AGENT` in `.env` (format: `Your Name your@email.com`)

---

## Environment Setup

Copy `.env.example` to `.env` and fill in:

```
FRED_API_KEY=your_key_here        # Free at https://fred.stlouisfed.org/docs/api/api_key.html
SEC_USER_AGENT=Your Name your@email.com
```
