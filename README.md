# Vaartha — Geopolitical Supply Chain Intelligence

**Team 7 Lambda · Rutgers Advanced Python SP2026 Midterm**
Tarun Theegela · Sai Raunak Bidesi · Chaitanya Deogaonkar · Satwik Nadipelli

---

## What We're Investigating

> **Thesis:** Escalating geopolitical fragmentation systematically distorts the global supply chains of critical energy-transition and AI-hardware minerals, forcing technology and energy conglomerates to aggressively restructure CapEx and R&D allocations to achieve decoupled profitability and risk resilience.

In plain terms: when geopolitical tensions spike — trade wars, invasions, sanctions — countries that control the minerals needed for EV batteries, semiconductors, and solar panels use that control as leverage. This forces companies like NVIDIA, Intel, and Alphabet to spend more on building redundant supply chains rather than on pure innovation. We use 13 years of data to show exactly how that chain reaction plays out.

### The Causal Chain

```
ST2 — Geopolitical Shock
  (GPR index spikes, trade restrictions escalate)
      ↓
ST1 — Supply Chain Distortion
  (HHI concentration rises, commodity prices spike)
      ↓
ST3 — Energy Policy Amplifies Demand
  (renewables buildout accelerates mineral demand further)
      ↓
ST4 — Corporate CapEx Response
  (semiconductor and hyperscaler firms front-load capital investment)
```

Each subtopic is both a standalone analysis and one link in this chain.

---

## Why 2010–2022?

A common question: why not use data through 2025 or 2026?

The short answer is **data availability and consistency across all four sources**. Here's why each boundary was chosen:

| Boundary | Reason |
|----------|--------|
| **Start: 2010** | SEC EDGAR XBRL filings became mandatory for large accelerated filers in 2009–2010. Before 2010, machine-readable corporate financial data is too sparse and inconsistent to rely on. |
| **End: 2022** | The RFF World Carbon Pricing Database (our ST3 source) currently ends at 2020–2021 for most countries. OECD export restriction data has significant coverage gaps after 2022. To avoid an unbalanced panel where some subtopics have 2023–2024 data and others don't, we cap at 2022 — the last year where all four datasets have solid, verified coverage. |
| **Why not 2023–2024?** | Using partial-year or unverified data for some subtopics while others are complete would introduce systematic bias into the cross-subtopic integration analysis. A clean 13-year window (2010–2022) is more analytically sound than a ragged 15-year one. |

This is a deliberate methodological choice, not a limitation. The 2022 cutoff still captures the full Ukraine invasion shock (February 2022), the CHIPS Act (August 2022), and the post-COVID supply chain crisis — the three most consequential events for our thesis.

---

## Project Structure

```
vaartha/
├── src/
│   ├── config.py                  ← single source of truth: all paths, constants, API keys
│   ├── utils.py                   ← shared helpers (HHI, ISO-3, merge, plotting)
│   ├── st2_pipeline.py            ← ST2 transmission pipeline module
│   └── st2_transmission.py        ← lag scanning and forward response analysis
│
├── notebooks/
│   ├── phase1_ingestion/          ← download, clean, save Parquets
│   │   ├── 01_ST1_minerals_ingestion.ipynb
│   │   ├── 02_ST2_geopolitical_risk_ingestion.ipynb
│   │   ├── 03_ST3_energy_policy_ingestion.ipynb
│   │   └── 04_ST4_capex_ingestion.ipynb
│   │
│   ├── phase2_analysis/           ← EDA + 5 charts per subtopic
│   │   ├── 05_ST1_analysis.ipynb
│   │   ├── 06_ST2_analysis.ipynb
│   │   ├── 07_ST3_analysis.ipynb
│   │   └── 08_ST4_analysis.ipynb
│   │
│   └── phase3_integration/        ← cross-subtopic integration + causal chain
│       └── 09_integration.ipynb
│
├── data/
│   ├── raw/
│   │   ├── DOWNLOAD.md            ← where to get each source file
│   │   ├── ST1/bgs|worldbank|oecd
│   │   ├── ST2/                   ← GPR, GSCPI (FRED + yfinance auto-download)
│   │   ├── ST3/                   ← OWID + RFF auto-download
│   │   └── ST4/                   ← SEC EDGAR auto-fetched
│   └── processed/                 ← cleaned Parquets (committed to repo)
│       ├── ST1/
│       ├── ST2/
│       ├── ST3/
│       └── ST4/
│
├── outputs/
│   ├── charts/                    ← 24 saved figures (.png / .html)
│   └── tables/                    ← summary tables (.csv)
│
└── scripts/
    ├── check_st2_inputs.py
    ├── preprocess_st2_raw.py
    └── run_st2_transmission.py
```

---

## What Each Subtopic Finds

### ST1 — Critical Minerals
**Question:** Where are the global supply chokepoints?

Key finding: gallium (HHI 0.77), germanium (0.76), and rare earths (0.71) are near-monopolies — China controls all three. Lithium is dominated by Chile and Australia. Supply concentration has **increased** since 2018, not decreased.

Charts: HHI over time · production choropleth · Sankey trade flows · HHI vs price volatility · OECD export restrictions

### ST2 — Geopolitical Risk
**Question:** How does geopolitical risk transmit into supply chain pressure?

Key finding: GPR spikes lead GSCPI (supply chain pressure) by ~1–2 months. The transmission strengthened materially after 2020 — geopolitical shocks now convert to supply chain disruption faster than they did pre-COVID.

Charts: GPR/GPRT/GPRA timeseries · GPR→GSCPI rolling correlation · GSCPI→ETF returns · sector ETF heatmap · Ukraine event study

### ST3 — Energy Policy
**Question:** How do divergent national energy policies amplify mineral demand?

Key finding: Germany and the UK are accelerating renewables at 3× the pace of India and Brazil. This divergence creates structurally asymmetric demand for lithium, cobalt, silicon, and copper — countries moving fastest create the sharpest mineral demand spikes.

Charts: energy mix faceted · carbon price vs renewables · policy divergence heatmap · mineral demand projection

### ST4 — Corporate CapEx
**Question:** How are companies restructuring CapEx in response?

Key finding: semiconductor CapEx intensity and annual GPR are positively correlated (r = 0.56). Following GPR spikes, semiconductor firms increase CapEx intensity by ~1.5pp within 1–2 years. Hyperscalers show the same pattern with a longer lag.

Charts: CapEx intensity heatmap · GPR vs semiconductor CapEx · R&D intensity by sector · OLS descriptive table

### Integration (09)
Combines all four into a single annual panel (2010–2022) and shows:
- **Correlation matrix**: GSCPI→semiconductor CapEx r = 0.71; renewables→CapEx r = 0.82
- **Four-Box regime map**: years with high GPR + high HHI (Double Risk) show the largest CapEx bubbles
- **Causal chain timeline**: the 4-step shock-to-response sequence, annotated with events
- **Rolling correlations**: cross-ST associations have strengthened since 2018

---

## Quick Start

### 1. Clone and install

```bash
git clone https://github.com/tt633/vaartha.git
cd vaartha
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Set up environment

```bash
cp .env.example .env
```

Fill in `.env`:
```
FRED_API_KEY=your_key_here        # free at https://fred.stlouisfed.org/docs/api/api_key.html
SEC_USER_AGENT=Your Name your@email.com
```

### 3. Option A — Skip ingestion (recommended for new users)

All processed Parquets are already committed. Jump straight to analysis:

```bash
jupyter notebook notebooks/phase2_analysis/05_ST1_analysis.ipynb
```

Run notebooks 05 → 09 in order. Charts save to `outputs/charts/` automatically.

### 4. Option B — Re-run everything from raw data

First download the raw files per `data/raw/DOWNLOAD.md`, then:

```bash
# Phase 1 — ingestion (generates Parquets)
jupyter nbconvert --to notebook --execute --inplace notebooks/phase1_ingestion/01_ST1_minerals_ingestion.ipynb
jupyter nbconvert --to notebook --execute --inplace notebooks/phase1_ingestion/02_ST2_geopolitical_risk_ingestion.ipynb
jupyter nbconvert --to notebook --execute --inplace notebooks/phase1_ingestion/03_ST3_energy_policy_ingestion.ipynb
jupyter nbconvert --to notebook --execute --inplace notebooks/phase1_ingestion/04_ST4_capex_ingestion.ipynb

# Phase 2 — analysis (generates charts)
jupyter nbconvert --to notebook --execute --inplace notebooks/phase2_analysis/05_ST1_analysis.ipynb
jupyter nbconvert --to notebook --execute --inplace notebooks/phase2_analysis/06_ST2_analysis.ipynb
jupyter nbconvert --to notebook --execute --inplace notebooks/phase2_analysis/07_ST3_analysis.ipynb
jupyter nbconvert --to notebook --execute --inplace notebooks/phase2_analysis/08_ST4_analysis.ipynb

# Phase 3 — integration
jupyter nbconvert --to notebook --execute --inplace notebooks/phase3_integration/09_integration.ipynb
```

---

## Outputs

All charts are in `outputs/charts/`. Each `.png` or `.html` has a companion `.txt` file with a 2-sentence explanation of what the chart shows and why it's included.

| File | Description |
|------|-------------|
| `st1_hhi_over_time.png` | Supply concentration per mineral 2010–2022 |
| `st1_production_choropleth.html` | Interactive country production share map |
| `st1_sankey_flows.html` | Interactive producer → mineral flow diagram |
| `st1_hhi_vs_volatility.png` | Concentration vs price volatility scatter |
| `st1_oecd_restrictions.png` | Export restrictions introduced per year |
| `st2_gpr_timeseries.png` | GPR / GPRT / GPRA index with event annotations |
| `st2_gpr_gscpi_correlation.png` | GPR → GSCPI risk transmission channel |
| `st2_gscpi_etf_correlation.png` | Supply chain pressure → sector ETF returns |
| `st2_etf_annual_heatmap.png` | Sector ETF annual returns heatmap |
| `st2_event_study_ukraine.png` | 3-panel event study around Ukraine invasion |
| `st3_energy_mix_faceted.png` | Energy mix by country over time |
| `st3_carbon_vs_renewables.png` | Carbon pricing vs renewables adoption |
| `st3_policy_divergence_heatmap.png` | Renewables share divergence by country × year |
| `st3_mineral_demand_projection.png` | Solar/wind growth → implied mineral demand |
| `st4_capex_intensity_heatmap.png` | CapEx intensity by company × year |
| `st4_gpr_vs_capex.png` | GPR vs semiconductor CapEx (dual-axis) |
| `st4_rd_intensity_by_sector.png` | R&D intensity by sector |
| `st4_ols_summary_table.png` | Descriptive OLS: CapEx ~ GPR |
| `integration_correlation_matrix.png` | Cross-ST Pearson correlation matrix |
| `integration_four_box_regime.png` | Four-Box regime map (GPR × HHI) |
| `integration_causal_chain.png` | 4-panel ST2→ST1→ST3→ST4 timeline |
| `integration_rolling_correlation.png` | Rolling GPR→downstream correlations |

---

## Team & Ownership

| Subtopic | Owner | NetID |
|----------|-------|-------|
| ST1 — Critical Minerals | Tarun Theegela | tt633 |
| ST2 — Geopolitical Risk | Chaitanya Deogaonkar | cmd517 |
| ST3 — Energy Policy | Tarun Theegela | tt633 |
| ST4 — Corporate CapEx | Sai Raunak Bidesi | ssb196 |
| Integration | Tarun Theegela | tt633 |

**Deadlines:** Presentation Mar 9 · Full Submission Mar 16
