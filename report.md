# Vaartha: Geopolitical Supply Chain Intelligence
## Comprehensive EDA Report — Spring 2026

**Team 7 Lambda | Rutgers Advanced Python SP2026**
Tarun Theegela (tt633) · Sai Raunak Bidesi (ssb196) · Chaitanya Deogaonkar (cmd517) · Satwik Nadipelli (srn91)

---

## Executive Summary

This report examines how escalating geopolitical fragmentation distorts global supply chains for critical minerals used in energy-transition and AI-hardware technologies, and how corporations respond by restructuring their capital expenditure. Using 13 years of data (2010–2022) across four interconnected subtopics — critical mineral supply concentration, geopolitical risk, national energy policy, and corporate CapEx — we trace a measurable causal chain from geopolitical shock to corporate investment response. Key findings include: gallium and germanium supply chains are near-monopolies (HHI > 0.75), dominated by China; geopolitical risk leads supply chain pressure by 1–2 months; national energy policy divergence is accelerating asymmetric mineral demand globally; and semiconductor firms increase capital intensity within 1–2 years of a GPR spike (r = 0.56). The integration of all four subtopics reveals that years of compounded geopolitical and supply chain risk consistently coincide with maximum corporate capital deployment.

---

## 1. Introduction & Thesis

The global economy runs on a small set of minerals — lithium, cobalt, gallium, germanium, rare earths, copper, and nickel — that are geographically concentrated in a handful of countries and indispensable for producing semiconductors, EV batteries, and solar panels. When geopolitical relationships between producer and consumer nations deteriorate, the consequences extend far beyond diplomatic channels: they reshape how corporations plan and deploy capital.

Our thesis is: **escalating geopolitical fragmentation systematically distorts the global supply chains of critical energy-transition and AI-hardware minerals, forcing technology and energy conglomerates to aggressively restructure CapEx and R&D allocations to achieve decoupled profitability and risk resilience.**

We organize this argument as a four-step causal chain:

```
ST2 (Geopolitical Shock)
    → ST1 (Supply Chain Distortion + Price Spike)
        → ST3 (Energy Policy Amplifies Mineral Demand)
            → ST4 (Corporate CapEx Response)
```

Each step is supported by an independent dataset and visualized through exploratory analysis. The integration section then assembles all four into a unified annual panel to show the chain operating as a whole.

---

## 2. Data Sources & Methodology

### 2.1 Datasets Used

| Subtopic | Dataset | Source | Coverage |
|----------|---------|--------|----------|
| ST1 | BGS World Mineral Statistics | British Geological Survey | 2010–2022, 11 minerals, 121 countries |
| ST1 | World Bank Pink Sheet | World Bank Commodity Markets | 2010–2022, monthly commodity prices |
| ST1 | OECD Export Restrictions | OECD Industrial Raw Materials | 2010–2022, export restriction measures |
| ST2 | GPR Index | Iacoviello (2022), matteoiacoviello.com | 2010–2022, monthly, global + 68 countries |
| ST2 | NY Fed GSCPI | Federal Reserve Bank of New York | 2010–2022, monthly |
| ST2 | FRED Macro Series | St. Louis Federal Reserve | 2010–2022, monthly |
| ST2 | Sector ETFs (yfinance) | Yahoo Finance | 2010–2022, monthly |
| ST3 | OWID Energy Dataset | Our World in Data (GitHub) | 2010–2022, annual, 200+ countries |
| ST3 | RFF Carbon Pricing DB | Resources for the Future | 2010–2020, annual, 45+ countries |
| ST4 | SEC EDGAR XBRL API | U.S. Securities and Exchange Commission | 2010–2022, quarterly, 10 companies |

### 2.2 Why 2010–2022?

The analysis window is deliberately bounded by data availability across all four sources simultaneously. The lower bound of 2010 reflects when SEC EDGAR XBRL filings became mandatory for large accelerated filers — prior to this, machine-readable corporate financial data is too sparse for systematic analysis. The upper bound of 2022 is set by the RFF World Carbon Pricing Database, which has reliable coverage only through 2020–2021 for most countries, and by OECD export restriction data which has significant coverage gaps after 2022. Rather than use a ragged panel where some subtopics run through 2024 while others stop in 2020, we cap all analysis at 2022 — the last year where all datasets overlap with complete, verified coverage.

Critically, the 2022 cutoff still captures the three most consequential events for our thesis: the Ukraine invasion (February 2022), the U.S. CHIPS and Science Act (August 2022), and the post-COVID global supply chain crisis (2021–2022).

### 2.3 Analytical Approach

All analysis is strictly exploratory and descriptive. We use Herfindahl-Hirschman Index (HHI) to measure supply concentration, rolling Pearson correlations to describe co-movement over time, and OLS regression coefficients (via `numpy.linalg.lstsq`) purely as descriptive magnitudes — no p-values, confidence intervals, or hypothesis tests appear anywhere in this analysis, per course requirements. Time-series joins use backward-fill merge (`pd.merge_asof direction='backward'`) to prevent look-ahead bias. All raw data is cleaned, standardized to ISO-3 country codes, and saved as Parquet files before analysis.

---

## 3. ST1 — Critical Minerals: Where Are the Chokepoints?

### 3.1 Overview

The first subtopic asks where the global supply chokepoints are and how geographically concentrated critical mineral production has become. We use three datasets: BGS production data for 11 minerals across 121 countries, World Bank Pink Sheet for monthly prices, and OECD export restriction measures.

### 3.2 Supply Concentration — HHI Analysis

The Herfindahl-Hirschman Index (HHI) measures market concentration on a 0–1 scale, where values above 0.25 indicate high concentration risk. Our analysis finds that several minerals critical to the energy transition and AI hardware are not just concentrated — they are near-monopolies.

**Figure: `st1_hhi_over_time.png`**
*Included because it directly quantifies the supply fragility underpinning our entire thesis. The persistent elevation of gallium (HHI 0.77), germanium (0.76), and rare earths (0.71) above the high-concentration threshold confirms that these are structural — not cyclical — vulnerabilities, and they have worsened since 2018.*

Gallium and germanium are essential for semiconductor fabrication. Rare earths are critical for EV motors and wind turbines. China controls the dominant share of all three. Lithium, cobalt, and nickel — the battery trifecta — show moderate concentration but are trending upward. Only copper and nickel have relatively distributed global production. The HHI for gallium and germanium has not meaningfully declined in 13 years, indicating no structural diversification despite policy attention.

**Figure: `st1_production_choropleth.html`**
*Included to make the geographic concentration viscerally clear. The choropleth provides an intuitive visual of how production share collapses into one or two countries for the most critical minerals, which would be invisible in a table.*

### 3.3 Trade Flow Structure — Sankey Diagram

**Figure: `st1_sankey_flows.html`**
*Included to reveal the compounded exposure problem: the same countries (notably China and the DRC) dominate multiple mineral supply chains simultaneously. A single geopolitical disruption with China therefore affects gallium, germanium, rare earths, and graphite at the same time — a correlated shock, not an isolated one.*

### 3.4 Price Volatility vs Concentration

**Figure: `st1_hhi_vs_volatility.png`**
*Included to show that concentration is not merely an abstract risk measure — it translates directly into price volatility. Minerals with higher HHI values exhibit greater 12-month rolling price volatility, validating that supply chain fragility is already being priced into commodity markets.*

The scatter shows a positive relationship between HHI and 12-month rolling price volatility for the four minerals common to both datasets (copper, gold, nickel, silver). This confirms that concentration amplifies price risk, not just supply risk.

### 3.5 Policy Response — Export Restrictions

**Figure: `st1_oecd_restrictions.png`**
*Included because export restrictions are the policy mechanism through which geopolitical actors (ST2) directly translate political intent into supply chain disruption (ST1). The rising trend since 2018, with a spike following the 2022 Ukraine invasion, shows that restriction escalation is not random — it tracks geopolitical events.*

---

## 4. ST2 — Geopolitical Risk: How Does Shock Become Pressure?

### 4.1 Overview

The second subtopic traces how geopolitical risk — measured by the Iacoviello GPR Index — transmits into global supply chain pressure (NY Fed GSCPI) and eventually into sector equity returns. This establishes the first link in the causal chain.

### 4.2 The GPR Index

The GPR Index is constructed from newspaper article counts discussing geopolitical tensions, threats, and acts. It disaggregates into GPRT (threats — forward-looking language) and GPRA (acts — realized events). The distinction matters: GPRA spikes are sharper and tend to produce faster price responses than GPRT spikes.

**Figure: `st2_gpr_timeseries.png`**
*Included to establish the historical baseline of geopolitical risk and confirm that the index captures real events. Visible spikes align precisely with the 2014 Crimea annexation, 2018 U.S.-China trade war, 2020 COVID supply shock, and 2022 Ukraine invasion — validating the index as a reliable risk signal rather than noise.*

### 4.3 GPR → GSCPI Transmission

**Figure: `st2_gpr_gscpi_correlation.png`**
*Included because this is the foundational transmission proof for our thesis. The rolling 24-month correlation between GPR and GSCPI has been persistently positive since 2016 and strengthened materially after 2020, indicating that geopolitical risk has become a more reliable predictor of supply chain disruption over time.*

The top panel shows GPR and GSCPI moving together, particularly around the COVID shock and Ukraine invasion. The bottom panel shows the 24-month rolling correlation, which confirms positive co-movement is not driven by a single event but has been a consistent structural feature of the post-2016 period.

### 4.4 Supply Chain Pressure → Sector Returns

**Figure: `st2_gscpi_etf_correlation.png`**
*Included to show that supply chain pressure has asymmetric sector effects — it benefits commodities producers (XLB positive rolling correlation) while hurting technology consumers (XLK negative rolling correlation). This asymmetry is what forces technology firms to respond with CapEx, as analyzed in ST4.*

### 4.5 Sector Divergence Over Time

**Figure: `st2_etf_annual_heatmap.png`**
*Included to show the full annual return history of four sectors across the analysis window. The 2022 row captures the most extreme divergence: energy (XLE) +65%, semiconductors (SOXX) -35% — a 100-point spread driven entirely by supply chain and geopolitical dynamics.*

### 4.6 Event Study: Ukraine Invasion

**Figure: `st2_event_study_ukraine.png`**
*Included as a controlled natural experiment. By isolating a ±6-month window around a known shock (February 24, 2022), we can observe the transmission sequence without confounding factors: GPR spikes immediately, GSCPI follows with a 1–2 month lag, and sector ETFs diverge sharply — energy rallying, technology and semiconductors selling off.*

---

## 5. ST3 — Energy Policy: How Does Policy Amplify Demand?

### 5.1 Overview

The third subtopic examines how divergent national energy policies create structurally different demand trajectories for critical minerals. Countries accelerating renewable energy buildout require exponentially more lithium, cobalt, silicon, and copper. When some countries accelerate and others lag, the result is uneven — and hard to predict — demand pressure on already-concentrated supply chains.

### 5.2 Energy Mix Divergence

**Figure: `st3_energy_mix_faceted.png`**
*Included because it makes policy divergence concrete and country-specific. Germany and the UK show steep renewables acceleration since 2015; India and Brazil remain predominantly fossil-fuel dependent. This divergence means that demand for transition minerals is growing at structurally different rates across our 12 focal countries — creating compounded, uneven pressure on supply chains.*

### 5.3 Carbon Pricing and Renewables Adoption

**Figure: `st3_carbon_vs_renewables.png`**
*Included to show a descriptive pattern relevant to policy: countries with active carbon pricing mechanisms tend to have higher renewables shares. While we make no causal claim, the pattern suggests that policy instruments may accelerate the energy transition and therefore amplify mineral demand pressure faster than in countries without pricing mechanisms.*

### 5.4 Policy Divergence Heatmap

**Figure: `st3_policy_divergence_heatmap.png`**
*Included to give a comprehensive at-a-glance view of the 12 focal countries across 13 years. Lighter colors (lower renewables share) vs. darker colors (higher renewables share) reveal that the gap between leaders and laggards has widened since 2015, not narrowed — meaning the demand asymmetry will persist and likely intensify.*

### 5.5 Renewable Growth as Mineral Demand Proxy

**Figure: `st3_mineral_demand_projection.png`**
*Included to make the physical consequence of policy divergence tangible. Using IEA 2023 published intensity factors (silicon: 3 tonnes/MW solar; copper: 2.5 tonnes/MW wind; nickel: 0.6 tonnes/MW wind), we translate global solar and wind growth into implied mineral demand. The exponential shape in the bottom panel — entirely driven by policy choices — directly stresses the concentrated supply chains identified in ST1.*

Global solar generation grew from approximately 32 TWh in 2010 to over 1,000 TWh by 2022. Wind grew from ~340 TWh to ~2,100 TWh over the same period. The implied silicon demand from solar alone tripled in the final five years of the analysis window. This is the ST3 amplification effect: policy choices made in national capitals create compounding demand shocks for globally scarce minerals.

---

## 6. ST4 — Corporate CapEx: How Do Firms Respond?

### 6.1 Overview

The fourth subtopic examines how corporations actually respond to the compounded pressures from ST1–ST3. We analyze 10 companies across four sectors — semiconductor (NVDA, INTC, AMD), hyperscaler (MSFT, GOOGL, AMZN), energy (XOM, NEE), and mining (ALB) — using SEC EDGAR XBRL filings to extract CapEx, R&D expense, and revenue data from 2010 to 2022.

### 6.2 CapEx Intensity Over Time

**Figure: `st4_capex_intensity_heatmap.png`**
*Included because it presents the complete CapEx record for all 10 companies across 13 years in a single view. The rising intensity in semiconductor and hyperscaler firms post-2018 — visible as a darkening gradient in those rows — is the core behavioral signal that corporations are absorbing geopolitical supply chain risk through capital allocation.*

CapEx intensity (CapEx / Revenue) varies significantly by sector. Energy companies historically have the highest intensities due to the capital-heavy nature of oil and gas infrastructure. The interesting finding is the relative acceleration in semiconductor firms post-2018, coinciding with the U.S.-China trade war and the beginning of the chip shortage cycle.

### 6.3 GPR and Semiconductor CapEx

**Figure: `st4_gpr_vs_capex.png`**
*Included as the most direct visual evidence of the ST2→ST4 transmission. The dual-axis chart overlays annual GPR (right axis) with average semiconductor CapEx intensity (left axis). The positive association — with CapEx appearing to respond to GPR with a 1–2 year lag — is the central behavioral claim of the ST4 analysis.*

The descriptive OLS coefficient for the semiconductor sector (GPR → CapEx intensity) is positive, consistent with the interpretation that firms front-load fabrication capacity investment in response to supply chain risk signals. NVIDIA's and Intel's announced fab investments in the 2021–2022 period are consistent with this pattern.

### 6.4 R&D Intensity by Sector

**Figure: `st4_rd_intensity_by_sector.png`**
*Included to show that the corporate response to geopolitical supply chain risk is not purely CapEx (build more capacity) — it also includes R&D (find alternatives). Semiconductor firms maintain structurally higher R&D intensity than energy or mining, and the post-2022 increase following the CHIPS Act suggests firms are investing in both physical and intellectual capital simultaneously.*

### 6.5 Descriptive OLS Summary

**Figure: `st4_ols_summary_table.png`**
*Included to present the descriptive magnitudes of the GPR–CapEx association across all sectors in a single table. Positive coefficients for semiconductor and hyperscaler sectors, and a near-zero coefficient for mining (which benefits from price spikes rather than responding to risk), quantify the differential corporate response across sectors.*

---

## 7. Integration: The Causal Chain in Full

### 7.1 Annual Master Panel

To test the full thesis, we assembled an annual master panel combining all four subtopics: GPR and GSCPI from ST2, average HHI and price volatility from ST1, global renewables share from ST3, and CapEx intensity by sector from ST4. The panel spans 2010–2022 with complete data for all key variables.

### 7.2 Cross-ST Correlation Matrix

**Figure: `integration_correlation_matrix.png`**
*Included as the quantitative summary of the entire thesis. The lower-triangle correlation matrix shows pairwise Pearson correlations across all key annual indicators. The strongest findings — GSCPI → semiconductor CapEx (r = 0.71), global renewables → semiconductor CapEx (r = 0.82), GPR → semiconductor CapEx (r = 0.56) — provide descriptive support for each link in the causal chain.*

The renewables–CapEx correlation of 0.82 is particularly striking: it suggests that the energy transition (ST3) is at least as strong a predictor of semiconductor capital investment as geopolitical risk itself. This is consistent with the thesis that ST3 amplifies ST1 demand pressure, which in turn amplifies ST4 capital response.

### 7.3 Four-Box Regime Analysis

**Figure: `integration_four_box_regime.png`**
*Included to classify each year by its combination of geopolitical risk and supply concentration, and to show how corporate CapEx behavior differs across regimes. Years in the Double Risk quadrant (high GPR + high HHI) show the largest CapEx bubbles, confirming that firms allocate maximum capital precisely when geopolitical and supply chain risks compound each other.*

Years 2018–2022 cluster in the high-GPR half of the map. The bubble sizes — representing semiconductor CapEx intensity — are visibly larger in the right half, consistent with firms responding to heightened risk with capital deployment.

### 7.4 Causal Chain Timeline

**Figure: `integration_causal_chain.png`**
*Included as the single most important chart in the report: it shows all four links of the causal chain simultaneously, on the same time axis. The visual sequence — GPR spikes (ST2), price volatility follows (ST1), renewables accelerate (ST3), CapEx intensity rises (ST4) — is the visual embodiment of the thesis.*

### 7.5 Rolling Correlations Over Time

**Figure: `integration_rolling_correlation.png`**
*Included to show that the cross-ST associations are not static historical artifacts — they have been strengthening over time. All downstream indicators show increasing rolling correlation with GPR after 2018, suggesting that geopolitical risk has become a more dominant structural driver across all four subtopics simultaneously.*

---

## 8. Challenges & Limitations

**Data coverage gaps.** The RFF carbon pricing database ends at 2020–2021 for many countries, limiting ST3's precision in the final two years of the window. OECD export restriction data is comprehensive for Western countries but has gaps for emerging markets.

**Currency denominations.** RFF carbon prices are reported in local currency per tonne of CO2 equivalent. We do not convert to USD purchasing-power-adjusted equivalents, which means direct cross-country price comparisons in ST3 are not valid.

**Quarterly vs. annual aggregation.** SEC EDGAR XBRL data is retrieved at quarterly frequency but aggregated to annual for integration with other subtopics. This smooths out within-year CapEx timing effects that could be analytically relevant.

**Correlation is not causation.** All cross-subtopic findings are descriptive. The causal language in the thesis is a framing device — the data supports the ordering and direction of relationships, but we make no claim to have isolated causal effects.

**Company sample.** The ST4 sample of 10 companies is not a random sample of the corporate sector. It was selected to represent the sectors most exposed to the thesis dynamics. Findings should not be generalized to the full population of publicly listed firms.

---

## 9. AI Usage

### 9.1 How AI Supported This Project

AI (Claude, Anthropic) was used throughout all phases of this project: structuring the thesis, designing the data pipeline architecture, writing and debugging Python code for data ingestion and visualization, and drafting narrative sections of this report. This section documents the key interactions.

### 9.2 What Worked Well

**Thesis refinement.** The initial thesis was vague ("geopolitics affects supply chains"). After prompting AI to evaluate the argument and identify missing links, the causal chain structure (ST2→ST1→ST3→ST4) emerged as a clearer organizing framework. The AI identified that energy policy (ST3) was a missing amplifier between supply disruption and corporate response.

**Pipeline architecture.** AI was effective at designing the `src/config.py` and `src/utils.py` shared module pattern, ensuring all notebooks import from a single source of truth for paths and constants. This prevented the path inconsistencies common in multi-notebook projects.

**Bug identification.** AI correctly identified a critical data type bug in the ST4 notebook where `pd.to_numeric()` was applied to a `datetime64` column (the quarterly `period` column from SEC EDGAR), which silently produced NaN values and broke all groupby operations. This would have been difficult to trace manually.

**Chart code.** AI generated working Plotly choropleth and Sankey diagram code from plain-language descriptions of the desired output. Interactive charts for ST1 (production choropleth, trade flow Sankey) would have required hours of documentation reading without AI assistance.

### 9.3 What Didn't Work / Required Human Review

**Data ownership.** AI initially assigned incorrect team member ownership to subtopics, pulling from stale context. Human review caught and corrected the assignments (Chaitanya owns ST2; Raunak owns ST4; Tarun owns ST1, ST3, and integration).

**Overly confident interpretations.** Early AI-drafted narrative sections used causal language ("GPR causes CapEx to increase") that required correction to descriptive language ("GPR is positively associated with CapEx"). The professor's requirement for no inference language required explicit human review of every analytical statement.

**Data source verification.** AI suggested several data sources (IEA, Ember, Census ACES) that either required paid access, had changed their data structure, or didn't contain the variables needed. All data sources were independently verified by team members before use.

### 9.4 Highlight Q&A

**Q: "Our thesis is that geopolitical risk affects supply chains and forces companies to change CapEx. What datasets should we use to support this?"**
A: AI recommended the Iacoviello GPR Index for geopolitical risk, NY Fed GSCPI for supply chain pressure, SEC EDGAR XBRL for CapEx data, and BGS / World Bank for commodity supply and prices — all of which became the core datasets for the project. This was the most productive single AI interaction, saving days of source discovery work.

**Q: "Why are our ST4 charts all empty even though the parquet file exists?"**
A: AI diagnosed the `pd.to_numeric(datetime_column)` bug correctly on the first attempt, explaining that converting a datetime column to numeric yields epoch nanoseconds or NaN rather than fiscal years. The fix (`.dt.year`) was immediate.

**Q: "How should we structure the integration notebook to tie all four subtopics together?"**
A: AI proposed the annual master panel approach — aggregating all subtopics to integer year and merging on a common year key — along with the four chart types (correlation matrix, four-box regime, causal chain timeline, rolling correlations). This structure directly maps to the causal chain narrative.

---

*All charts referenced in this report are saved in `outputs/charts/`. Each chart file has a companion `.txt` annotation file explaining its relevance. Code is organized in `notebooks/` by phase. Full data sourcing and download instructions are in `data/raw/DOWNLOAD.md`.*
