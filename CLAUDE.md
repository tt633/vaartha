# CLAUDE.md — Team 7 Lambda | SP2026 Midterm

This file gives Claude Code full context on this project. Read it before touching any file.

---

## What this project is

**Academic:** Advanced Python midterm (30% of grade). Due dates: presentation Mar 9, full submission Mar 16.

**Thesis:** Escalating geopolitical fragmentation systematically distorts the global supply chains of critical energy-transition and AI-hardware minerals, forcing technology and energy conglomerates to aggressively restructure CapEx and R&D allocations to achieve decoupled profitability and risk resilience.

**Long-term goal:** This EDA project is the foundation for a geopolitical supply chain intelligence SaaS application. Write code that is clean and modular enough to be reused in a production app later.

**Team:** Tarun Theegela (tt633) · Sai Raunak Bidesi (ssb196) · Chaitanya Deogaonkar (cmd517) · Satwik Nadipelli (srn91)

---

## Project structure

```
team7_lambda/
├── CLAUDE.md                  ← you are here
├── README.md                  ← setup instructions for humans
├── requirements.txt           ← pinned dependencies
├── .env                       ← API keys (never read or modify this file)
├── .env.example               ← template showing what keys are needed
├── .gitignore
├── src/
│   ├── config.py              ← SINGLE SOURCE OF TRUTH for all constants
│   └── utils.py               ← shared functions used by all notebooks
├── data/
│   ├── raw/                   ← downloaded source files (may not exist yet)
│   │   ├── usgs/              ← USGS Mineral Commodity CSVs
│   │   ├── worldbank/         ← pink_sheet.xlsx
│   │   ├── gpr/               ← gpr_data.xlsx (Iacoviello)
│   │   ├── nyfed/             ← gscpi.xlsx (NY Fed)
│   │   ├── owid/              ← owid-energy-data.csv
│   │   └── oecd/              ← export_restrictions.csv
│   └── processed/             ← cleaned Parquet files output by notebooks
├── notebooks/
│   ├── phase1_ingestion/
│   │   ├── 01_ST1_minerals_ingestion.ipynb       ← DONE ✓
│   │   ├── 02_ST2_geopolitical_risk_ingestion.ipynb ← DONE ✓
│   │   ├── 03_ST3_energy_policy_ingestion.ipynb  ← DONE ✓
│   │   └── 04_ST4_capex_ingestion.ipynb          ← DONE ✓
│   ├── phase2_analysis/
│   │   ├── 05_ST1_analysis.ipynb                 ← DONE ✓
│   │   ├── 06_ST2_analysis.ipynb                 ← DONE ✓
│   │   ├── 07_ST3_analysis.ipynb                 ← DONE ✓
│   │   └── 08_ST4_analysis.ipynb                 ← DONE ✓
│   └── phase3_integration/
│       └── 09_integration.ipynb                  ← DONE ✓
└── outputs/
    ├── charts/                ← saved figures (.png / .html)
    └── tables/                ← summary tables (.csv)
```

---

## Four subtopics (ST)

Every file, variable, and function should be namespaced to its subtopic.

| ID | Name | Core question | Key datasets |
|----|------|--------------|--------------|
| ST1 | Critical Minerals | Where are global supply chokepoints and how concentrated are they? | USGS, World Bank Pink Sheet, OECD Export Restrictions |
| ST2 | Geopolitical Risk | How does geopolitical risk transmit into supply chain pressure and commodity prices? | GPR (Iacoviello), NY Fed GSCPI, FRED, yfinance ETFs |
| ST3 | Energy Policy | How do divergent national energy policies create asymmetric mineral demand? | OWID energy, Ember, RFF Carbon Pricing DB |
| ST4 | Corporate CapEx | How are companies restructuring CapEx/R&D in response to supply chain risk? | SEC EDGAR XBRL API, Census ACES, SimFin |

**Causal chain (the thesis argument):**
ST2 (geopolitical shock) → ST1 (supply chain distortion, price spike) → ST3 (energy policy amplifies demand) → ST4 (corporate CapEx response)

---

## src/config.py — always import from here

Never hardcode paths, years, country lists, or API keys inline. Everything lives in `config.py`.

Key constants:
- `DATA_RAW`, `DATA_PROC`, `CHARTS`, `TABLES` — Path objects, always use these
- `FOCAL_COUNTRIES` — dict of ISO-3 → country name (12 countries)
- `MINERAL_HS_CODES` — dict of mineral name → HS6 code string
- `FRED_SERIES` — dict of label → FRED series ID
- `SECTOR_ETFS` — dict of sector → ticker
- `CAPEX_COMPANIES` — dict of ticker → {cik, sector, name} with verified SEC CIKs
- `XBRL_CONCEPTS` — dict of label → XBRL concept name for SEC API
- `START_YEAR = 2005`, `END_YEAR = 2024`
- `GPR_SMOOTH_WINDOW = 3`
- `HHI_HIGH_THRESHOLD = 0.25`

---

## src/utils.py — shared functions

Always import from utils, never reimplement these:

| Function | What it does |
|----------|-------------|
| `to_iso3(name)` | Country name string → ISO-3166-1 alpha-3 code |
| `normalize_countries(df, col)` | Adds `iso3` column to DataFrame, logs failures |
| `compute_hhi(df, group_col, value_col)` | HHI per group. Returns Series. |
| `flag_concentration(hhi_series)` | Boolean Series: True where HHI > 0.25 |
| `backward_merge(left, right, on, tolerance)` | `pd.merge_asof` backward — prevents look-ahead bias |
| `save_parquet(df, path, label)` | Save + log |
| `load_parquet(path, label)` | Load + log |
| `set_style()` | Apply dark-theme matplotlib rcParams |
| `annotate_events(ax, events)` | Add vertical event lines to a time-series chart |
| `KEY_EVENTS` | List of (date_str, label) for major geopolitical events |
| `TEAM_PALETTE` | Dict of subtopic → hex color |
| `log` | Pre-configured logger — use instead of print() |

---

## Hard rules — never break these

### Data integrity
- **No look-ahead bias.** All time-series joins must use `pd.merge_asof(..., direction='backward')`. Never use `pd.merge` on date columns directly for time series.
- **No print() statements.** Use `log.info()`, `log.warning()`, `log.error()` from utils.
- **Save all cleaned data as Parquet** to `data/processed/` using `save_parquet()`. Never save to CSV in processed/.
- **Forward-fill gaps max 2 periods** (`fillna(method='ffill', limit=2)`). Never fill more — it introduces bias.
- **Country names must be normalized to ISO-3** via `normalize_countries()` before any join or groupby on country.

### Code style
- **Every function needs a docstring** explaining args, returns, and a one-line usage example.
- **Every notebook cell has a comment header** (e.g., `# ── Load USGS CSV ─────────`).
- **No magic numbers.** Use constants from config.py.
- **Notebooks run top-to-bottom without errors.** If a raw file is missing, the cell logs a warning and creates an empty stub — it does not crash.
- **One notebook per subtopic per phase.** Don't mix ST1 and ST2 logic in the same notebook.

### Analysis constraints (per professor requirements)
- **Descriptive and exploratory only.** No statistical inference, no hypothesis testing, no p-values, no confidence intervals. Stay in-sample.
- **No individual stock analysis.** Always group by sector (XLK, XLE, XLB, SOXX) or by company sector tag (`semiconductor`, `hyperscaler`, `energy`, `mining`).
- **Every chart needs an annotation.** When saving a chart for the report, include a 2-sentence caption in the filename or a companion .txt file explaining why it's included.

### API keys
- **Never read, print, or log API keys.** They load via `python-dotenv` in config.py. If a key is missing, log a warning and skip — never crash.
- **SEC EDGAR:** No key needed. Always set `headers={"User-Agent": SEC_USER_AGENT}` from config.
- **FRED:** Free key. If missing, skip FRED cells gracefully.

---

## Processed data schema (what each Parquet contains)

### ST1
- `st1_minerals_production.parquet` — columns: `mineral, iso3, country, year, production, reserves`
- `st1_hhi.parquet` — columns: `year, mineral, hhi, high_concentration`
- `st1_prices.parquet` — columns: `date, commodity, price_usd_mt, price_vol_12m`
- `st1_oecd_restrictions.parquet` — columns: `iso3, country, commodity, year_introduced, measure_type` + others

### ST2
- `st2_gpr.parquet` — columns: `date, gpr, gprt, gpra, gpr_smooth` + country GPR columns
- `st2_gscpi.parquet` — columns: `date, gscpi`
- `st2_macro.parquet` — columns: `date, CPI, YIELD_CURVE, OIL_PRICE, GOLD_PRICE, GDP_GROWTH, INDUSTRIAL_PROD`
- `st2_etfs.parquet` — columns: `date, XLK, XLE, XLB, SOXX` + `*_return` columns
- `st2_master.parquet` — all ST2 series merged on monthly date

### ST3
- `st3_energy.parquet` — columns: `iso3, year, renewables_share, fossil_share, nuclear_share, solar_twh, wind_twh, hydro_twh, electricity_twh, primary_energy_twh`
- `st3_carbon_price.parquet` — columns: `iso3, year, tax_price_local, ets_price_local, has_carbon_price`

### ST4
- `st4_capex.parquet` — columns: `ticker, sector, period (datetime quarterly → convert to year via .dt.year), capex, rd_expense, revenue, capex_intensity, rd_intensity, us_total_capex_millions`
- **Note:** `period` is `datetime64[ns]` quarterly. Always do `pd.to_datetime(df['period']).dt.year` before any groupby or merge.

---

## Phase status

| Phase | Dates | Status |
|-------|-------|--------|
| Phase 1: Ingestion & Cleaning | Feb 27 – Mar 2 | ✓ DONE — all 4 STs, parquets committed |
| Phase 2: EDA & Visualization | Mar 2 – Mar 7 | ✓ DONE — notebooks 05–08, 5 charts each |
| Phase 3: Integration | Mar 7 – Mar 9 | ✓ DONE — 09_integration.ipynb, 4 charts |
| Phase 4: Report + Polish | Mar 9 – Mar 16 | TODO |

---

## Visualization standards

- Always call `set_style()` at the top of any notebook doing visualization.
- Use `TEAM_PALETTE` for consistent colors: ST1=`#00FFB2`, ST2=`#FF6B35`, ST3=`#A78BFA`, ST4=`#FACC15`
- Use `annotate_events(ax, KEY_EVENTS)` on every time-series chart.
- Save charts with: `plt.savefig(CHARTS / 'st1_hhi_over_time.png', dpi=150, bbox_inches='tight')`
- Interactive charts (Plotly): save as `.html` to `CHARTS/` as well.

**Required charts per subtopic (Phase 2):**
- ST1: HHI over time, choropleth production share, Sankey trade flows, HHI vs price volatility scatter, OECD restrictions bar
- ST2: GPR/GPRT/GPRA time series, cross-correlation GPR→GSCPI, cross-correlation GSCPI→prices, sector ETF heatmap, event study 3-panel
- ST3: Stacked area energy mix (faceted), carbon price vs renewables scatter, policy divergence heatmap, mineral demand projection lines
- ST4: CapEx intensity heatmap (company × quarter), GPR vs semiconductor CapEx dual-axis, R&D intensity bar by sector, OLS summary table

---

## Key external URLs (verified, do not change)

| Resource | URL |
|----------|-----|
| USGS ScienceBase | https://www.sciencebase.gov/catalog/item/677eaf95d34ea8c18376e8e7 |
| World Bank Pink Sheet | https://www.worldbank.org/en/research/commodity-markets |
| GPR Index | https://www.matteoiacoviello.com/gpr.htm |
| NY Fed GSCPI | https://www.newyorkfed.org/research/policy/gscpi |
| OWID Energy (direct CSV) | https://raw.githubusercontent.com/owid/energy-data/master/owid-energy-data.csv |
| OECD Export Restrictions | https://qdd.oecd.org/subject.aspx?Subject=ExportRestrictions_IndustrialRawMaterials |
| SEC EDGAR XBRL API | https://data.sec.gov/api/xbrl/companyconcept/ |
| FRED API docs | https://fred.stlouisfed.org/docs/api/fred/ |
| RFF Carbon Pricing DB | https://github.com/g-dolphin/WorldCarbonPricingDatabase |

---

## What to build next (Phase 4)

1. Run all notebooks top-to-bottom (01 → 09) to generate chart PNGs/HTMLs in `outputs/charts/`
2. Write the final report — one section per subtopic, cite charts from `outputs/charts/`
3. Polish: ensure all `.txt` caption files are accurate, clean up any notebook output cells before submission

## Integration notebook (09) — what it produces

- **Annual master panel** (2010–2022): GPR, GSCPI, avg HHI, avg price vol, global renewables share, CapEx intensity per sector
- **Chart 1** `integration_correlation_matrix.png` — cross-ST Pearson correlation heatmap
- **Chart 2** `integration_four_box_regime.png` — Four-Box: GPR × HHI quadrants, bubble = CapEx intensity
- **Chart 3** `integration_causal_chain.png` — 4-panel ST2→ST1→ST3→ST4 timeline
- **Chart 4** `integration_rolling_correlation.png` — 3-year rolling GPR→downstream correlations
- **Tables:** `integration_master_panel.csv`, `integration_correlation_matrix.csv`, `integration_regime_classification.csv`, `integration_summary_stats.csv`

## Key data facts (gotchas)

- `st4_capex.parquet` — `period` is `datetime64[ns]` quarterly; always convert with `.dt.year` before use
- `st2_gpr.parquet` — has `var_name`/`var_label` metadata cols; safe to ignore; 1 row per date
- ST1 HHI minerals vs ST1 price commodities only overlap on: `copper, gold, nickel, silver`
- All 4 subtopics align on 2010–2022 annual frequency
- `outputs/` is gitignored — charts are generated locally on run, not committed
