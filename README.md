# Vaartha — Geopolitical Supply Chain Intelligence

**Team 7 Lambda | Rutgers Advanced Python SP2026 Midterm**
**Tarun Theegela · Sai Raunak Bidesi · Chaitanya Deogaonkar · Satwik Nadipelli**

---

## Project Thesis

> Escalating geopolitical fragmentation systematically distorts the global supply chains of critical energy-transition and AI-hardware minerals, forcing technology and energy conglomerates to aggressively restructure CapEx and R&D allocations to achieve decoupled profitability and risk resilience.

The project is structured as a causal chain across four subtopics:

```
ST2 (Geopolitical Shock)
    → ST1 (Supply Chain Distortion + Price Spike)
        → ST3 (Energy Policy Amplifies Mineral Demand)
            → ST4 (Corporate CapEx Response)
```

This EDA project is also the foundation for a long-term **geopolitical supply chain intelligence SaaS application**.

---

## Project Structure

```
vaartha/
├── src/
│   ├── config.py          ← single source of truth: all paths, constants, API keys
│   └── utils.py           ← shared helpers used by every notebook
├── notebooks/
│   ├── 01_ST1_minerals_ingestion.ipynb      ← Phase 1: ST1 data ingestion  ✅
│   ├── 02_ST2_geopolitical_risk_ingestion.ipynb  ← Phase 1: ST2           🔲
│   ├── 03_ST3_energy_policy_ingestion.ipynb ← Phase 1: ST3                🔲
│   ├── 04_ST4_capex_ingestion.ipynb         ← Phase 1: ST4                🔲
│   ├── 05_ST1_analysis.ipynb                ← Phase 2: ST1 EDA + charts   🔲
│   ├── 06_ST2_analysis.ipynb                ← Phase 2: ST2 EDA + charts   🔲
│   ├── 07_ST3_analysis.ipynb                ← Phase 2: ST3 EDA + charts   🔲
│   └── 08_ST4_analysis.ipynb                ← Phase 2: ST4 EDA + charts   🔲
├── data/
│   ├── raw/
│   │   ├── ST1/bgs|worldbank|oecd    ← raw source files (see download guide below)
│   │   ├── ST2/                      ← GPR, GSCPI, FRED, yfinance
│   │   ├── ST3/                      ← OWID energy, Ember, RFF carbon pricing
│   │   └── ST4/                      ← SEC EDGAR XBRL
│   └── processed/
│       ├── ST1/    ← st1_minerals_production, st1_hhi, st1_prices, st1_oecd_restrictions
│       ├── ST2/    ← st2_gpr, st2_gscpi, st2_macro, st2_etfs, st2_master
│       ├── ST3/    ← st3_energy, st3_carbon_price
│       └── ST4/    ← st4_capex
└── outputs/
    ├── charts/     ← saved .png / .html figures
    └── tables/     ← summary .csv tables
```

---

## Setup

### 1. Clone the repo
```bash
git clone https://github.com/tt633/vaartha.git
cd vaartha
```

### 2. Create a virtual environment and install dependencies
```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Set up API keys
Copy `.env.example` to `.env` and fill in your keys:
```bash
cp .env.example .env
```
Required keys:
- `FRED_API_KEY` — free at https://fred.stlouisfed.org/docs/api/api_key.html
- `SEC_USER_AGENT` — format: `Your Name your@email.com` (no key needed, just identification)
- `IEA_TOKEN` — optional, only needed for IEA energy data

### 4. Run notebooks in order
All notebooks live in `notebooks/`. Run them top-to-bottom in order (01 → 08).
```bash
jupyter notebook
```

---

## Subtopic Assignments & Status

### ST1 — Critical Minerals ✅ DONE
**Owner:** Tarun Theegela (tt633)
**Question:** Where are the global supply chokepoints and how concentrated are they?

**Phase 1 (Ingestion) — DONE.**
Processed files saved to `data/processed/ST1/`:
- `st1_minerals_production.parquet` — 11 minerals, 121 countries, 2010–2022
- `st1_hhi.parquet` — Herfindahl-Hirschman Index per mineral per year
- `st1_prices.parquet` — World Bank Pink Sheet monthly prices
- `st1_oecd_restrictions.parquet` — OECD export restriction measures

**Phase 2 (Analysis) — notebook `05_ST1_analysis.ipynb` written, needs to be run once ST2 data is available for integration.**

Key finding so far: gallium (HHI 0.77), germanium (0.76), rare earths (0.71) are extremely concentrated — China dominates all three.

---

### ST2 — Geopolitical Risk 🔲 PENDING
**Owner:** Sai Raunak Bidesi (ssb196)
**Question:** How does geopolitical risk transmit into supply chain pressure and commodity prices?

**Phase 1 (Ingestion) — notebook `02_ST2_geopolitical_risk_ingestion.ipynb` is written. You need to:**

1. **Download raw data files** and place in `data/raw/ST2/`:

   | File | Source | Filename |
   |------|--------|----------|
   | GPR Index | https://www.matteoiacoviello.com/gpr.htm → Download Excel | `gpr_data.xlsx` |
   | NY Fed GSCPI | https://www.newyorkfed.org/research/policy/gscpi → Download CSV | `gscpi.csv` |

   FRED and yfinance data are **auto-downloaded** by the notebook — no manual step needed for those.

2. **Set API keys** in `.env`:
   - `FRED_API_KEY` — free at https://fred.stlouisfed.org/docs/api/api_key.html

3. **Run the notebook:** `notebooks/02_ST2_geopolitical_risk_ingestion.ipynb`

4. **Expected outputs** in `data/processed/ST2/`:
   - `st2_gpr.parquet` — GPR index (global + country-level, smoothed)
   - `st2_gscpi.parquet` — NY Fed Global Supply Chain Pressure Index
   - `st2_macro.parquet` — FRED macro series (CPI, yield curve, oil, gold, GDP)
   - `st2_etfs.parquet` — Sector ETF prices and returns (XLK, XLE, XLB, SOXX)
   - `st2_master.parquet` — All ST2 series merged on monthly date

5. **Run Phase 2 analysis:** `notebooks/06_ST2_analysis.ipynb` — 5 charts already coded, just needs the parquets.

---

### ST3 — Energy Policy 🔲 PENDING
**Owner:** Chaitanya Deogaonkar (cmd517)
**Question:** How do divergent national energy policies create asymmetric mineral demand?

**Phase 1 (Ingestion) — notebook `03_ST3_energy_policy_ingestion.ipynb` is written. You need to:**

1. **All data auto-downloads** — no manual file placement needed. The notebook fetches:
   - OWID Energy Data (GitHub CSV)
   - RFF World Carbon Pricing Database (GitHub)

2. **Run the notebook:** `notebooks/03_ST3_energy_policy_ingestion.ipynb`

3. **Expected outputs** in `data/processed/ST3/`:
   - `st3_energy.parquet` — renewables/fossil/nuclear share + solar/wind TWh by country/year
   - `st3_carbon_price.parquet` — carbon pricing presence and price by country/year

4. **Run Phase 2 analysis:** `notebooks/07_ST3_analysis.ipynb` — 4 charts already coded.

   > **Note on data coverage:** RFF carbon pricing ends at 2020, OWID runs to 2023.
   > The analysis window is 2010–2022 — do not extend beyond this.

---

### ST4 — Corporate CapEx 🔲 PENDING
**Owner:** Satwik Nadipelli (srn91)
**Question:** How are companies restructuring CapEx and R&D in response to supply chain risk?

**Phase 1 (Ingestion) — notebook `04_ST4_capex_ingestion.ipynb` is written. You need to:**

1. **No manual downloads needed.** The notebook pulls directly from the SEC EDGAR XBRL API.

2. **Set your SEC user agent** in `.env`:
   ```
   SEC_USER_AGENT=Your Name your@email.com
   ```
   This is just an HTTP header for EDGAR politeness — no registration or key needed.

3. **Run the notebook:** `notebooks/04_ST4_capex_ingestion.ipynb`

   > Note: The notebook fetches 10 companies × 3–4 XBRL concepts = ~40 API calls.
   > There is a 150ms sleep between requests. Expect ~2 minutes to run.

4. **Expected output** in `data/processed/ST4/`:
   - `st4_capex.parquet` — ticker, sector, period, capex, rd_expense, revenue, capex_intensity, rd_intensity

5. **Run Phase 2 analysis:** `notebooks/08_ST4_analysis.ipynb` — 4 charts already coded.

   Companies covered: NVDA, INTC, AMD, MSFT, GOOGL, AMZN, XOM, NEE, ALB, MP

---

## Hard Rules (read before touching any file)

- **No `print()`** — use `log.info()`, `log.warning()`, `log.error()` from `utils.py`
- **No look-ahead bias** — all time-series joins use `pd.merge_asof(..., direction='backward')`
- **Save cleaned data as Parquet only** — never CSV in `processed/`
- **Forward-fill max 2 periods** — `fillna(method='ffill', limit=2)`
- **Country names → ISO-3** via `normalize_countries()` before any join/groupby
- **Import everything from `src/config.py`** — no hardcoded paths, years, or keys
- **Descriptive EDA only** — no p-values, no hypothesis testing, no confidence intervals
- **No individual stock analysis** — always group by sector

---

## Key Constants (from `src/config.py`)

| Constant | Value | Meaning |
|----------|-------|---------|
| `START_YEAR` | 2010 | Analysis window start |
| `END_YEAR` | 2022 | Analysis window end |
| `HHI_HIGH_THRESHOLD` | 0.25 | HHI above this = highly concentrated |
| `FOCAL_COUNTRIES` | 12 countries | USA, CHN, DEU, FRA, IND, JPN, GBR, AUS, BRA, ZAF, CHL, COD |

---

## Deadlines

| Phase | Dates | Status |
|-------|-------|--------|
| Phase 1: Ingestion & Cleaning | Feb 27 – Mar 2 | ST1 ✅, ST2/ST3/ST4 🔲 |
| Phase 2: EDA & Visualization | Mar 2 – Mar 7 | 🔲 |
| Phase 3: Integration | Mar 7 – Mar 9 | 🔲 |
| Phase 4: Report + Polish | Mar 9 – Mar 16 | 🔲 |

**Presentation: Mar 9 | Full Submission: Mar 16**
