# Vaartha — Presentation Plan
## 15-Minute Deck | Monday Mar 9, 2026

**Speakers:**
- Tarun — Intro, ST1, ST3, Integration, Closing
- Chaitanya — ST2
- Raunak — ST4

**Timing breakdown:**
| Section | Slides | Time | Speaker |
|---------|--------|------|---------|
| Hook + Thesis | 2 | 1.5 min | Tarun |
| ST1 — Critical Minerals | 3 | 2.5 min | Tarun |
| ST2 — Geopolitical Risk | 3 | 2.5 min | Chaitanya |
| ST3 — Energy Policy | 2 | 2 min | Tarun |
| ST4 — Corporate CapEx | 2 | 2 min | Raunak |
| Integration | 2 | 2 min | Tarun |
| Closing | 1 | 0.5 min | Tarun |
| **Total** | **15** | **15 min** | |

---

## Slide 1 — Hook (Tarun) | 45 sec

**Title:** "What happens when a country weaponizes a mineral?"

**Visual:** Split image — left side: a chip/EV battery, right side: a map of China highlighted with "controls 77% of global gallium"

**Talking points:**
- "In 2023, China banned the export of gallium and germanium overnight. These two minerals are in every advanced semiconductor ever made."
- "NVIDIA's stock dropped. Intel fast-tracked a $20 billion fab in Ohio. The U.S. passed the CHIPS Act."
- "This project asks: is this pattern measurable? Does geopolitical risk systematically force corporations to restructure how they invest?"
- "We built a 13-year data pipeline across 4 datasets to find out."

---

## Slide 2 — Thesis & Causal Chain (Tarun) | 45 sec

**Title:** "The Causal Chain We're Testing"

**Visual:** Simple arrow diagram — boxes for ST2 → ST1 → ST3 → ST4 with one-line labels

```
Geopolitical Shock → Supply Distortion → Energy Policy Amplifies → CapEx Response
     (ST2)                (ST1)               (ST3)                   (ST4)
```

**Talking points:**
- "Our thesis: geopolitical fragmentation distorts critical mineral supply chains, and corporations respond by aggressively restructuring capital investment."
- "We broke this into 4 linked subtopics — each one a step in the chain."
- "13 years of data, 9 datasets, 10 companies, 121 countries."
- "Every finding is strictly descriptive — we're showing the pattern, not making causal claims."

---

## Slide 3 — ST1: The Chokepoints (Tarun) | 1 min

**Title:** "ST1: A Handful of Countries Control Everything"

**Visual:** `st1_hhi_over_time.png`

**Talking points:**
- "The HHI — Herfindahl-Hirschman Index — measures supply concentration from 0 to 1. Above 0.25 is high risk."
- "Gallium sits at 0.77. Germanium at 0.76. Rare earths at 0.71. These are near-monopolies."
- "All three are dominated by China — and the concentration has not improved in 13 years."
- "This is structural fragility, not a temporary blip."

---

## Slide 4 — ST1: Trade Flows (Tarun) | 45 sec

**Title:** "The Same Country Dominates Multiple Minerals"

**Visual:** `st1_sankey_flows.html` (screenshot or live if browser available)

**Talking points:**
- "This Sankey maps top producing countries to the minerals they supply."
- "The compounded exposure problem: one diplomatic incident with China simultaneously disrupts gallium, germanium, rare earths, AND graphite."
- "That's not one supply chain risk — that's four correlated shocks from a single source."

---

## Slide 5 — ST1: Policy Escalation (Tarun) | 45 sec

**Title:** "Governments Are Actively Weaponizing Restrictions"

**Visual:** `st1_oecd_restrictions.png`

**Talking points:**
- "Export restrictions on critical minerals have increased every year since 2018."
- "The 2022 spike aligns exactly with the Ukraine invasion and the resulting sanctions environment."
- "This isn't just market risk — it's policy risk. Governments are using mineral access as leverage."
- "That brings us to ST2 — how do we measure that geopolitical pressure?"

---

## Slide 6 — ST2: Measuring the Shock (Chaitanya) | 1 min

**Title:** "ST2: Geopolitical Risk Is Measurable — and It Transmits"

**Visual:** `st2_gpr_timeseries.png`

**Talking points:**
- "The GPR Index is built from newspaper article counts tracking geopolitical threats and acts."
- "Every major event is visible: 2014 Crimea, 2018 trade war, 2020 COVID, 2022 Ukraine."
- "We split it into GPRT (threats — forward looking) and GPRA (realized acts). Acts produce faster price responses."
- "But the key question isn't whether GPR spikes — it's whether those spikes actually reach supply chains."

---

## Slide 7 — ST2: Transmission to Supply Chains (Chaitanya) | 1 min

**Title:** "GPR Leads Supply Chain Pressure by 1–2 Months"

**Visual:** `st2_gpr_gscpi_correlation.png`

**Talking points:**
- "The bottom panel shows the 24-month rolling correlation between GPR and the NY Fed's Global Supply Chain Pressure Index."
- "Positive correlation has been persistent since 2016 and strengthened sharply after 2020."
- "Geopolitical risk is now a reliable predictor of supply chain disruption — that relationship didn't exist as strongly a decade ago."
- "The transmission is getting faster and stronger over time."

---

## Slide 8 — ST2: Ukraine Event Study (Chaitanya) | 30 sec

**Title:** "The Ukraine Invasion: A Live Test of the Chain"

**Visual:** `st2_event_study_ukraine.png`

**Talking points:**
- "This 3-panel event study zooms into the ±6 months around February 24, 2022."
- "GPR spikes immediately. GSCPI follows 1–2 months later. Sector ETFs diverge: energy up 40%, semiconductors down 20%."
- "The sequence plays out exactly as the thesis predicts — in real time."

---

## Slide 9 — ST3: Policy Divergence (Tarun) | 1 min

**Title:** "ST3: Energy Policy Divergence Is Amplifying Demand"

**Visual:** `st3_energy_mix_faceted.png`

**Talking points:**
- "Germany and the UK are aggressively transitioning to renewables. India and Brazil are still predominantly fossil-fuel dependent."
- "That divergence creates structurally different mineral demand trajectories across our 12 focal countries."
- "Solar and wind require lithium, cobalt, silicon, copper — the same minerals already under supply pressure from ST1."
- "Policy choices in national capitals are compounding the supply chain crisis identified in ST1."

---

## Slide 10 — ST3: Demand Projection (Tarun) | 1 min

**Title:** "Renewable Growth Translates Directly Into Mineral Demand"

**Visual:** `st3_mineral_demand_projection.png`

**Talking points:**
- "Using IEA 2023 intensity factors, we converted global solar and wind TWh growth into implied mineral demand."
- "Global solar generation grew 30x in 12 years. Implied silicon demand tripled in the last 5 years alone."
- "This is the ST3 amplification: energy policy isn't a separate story — it's pouring fuel on the supply chain fire from ST1."
- "And all of this pressure ultimately lands on corporate balance sheets — which is what Raunak will show."

---

## Slide 11 — ST4: CapEx Response (Raunak) | 1 min

**Title:** "ST4: Corporations Are Spending Their Way Out of Risk"

**Visual:** `st4_capex_intensity_heatmap.png`

**Talking points:**
- "This heatmap shows CapEx intensity — CapEx as a percent of revenue — for 10 companies across 13 years."
- "Semiconductor firms: NVIDIA, Intel, AMD. Hyperscalers: Microsoft, Google, Amazon. Energy: ExxonMobil, NextEra. Mining: Albemarle."
- "The darkening gradient in semiconductor and hyperscaler rows after 2018 is the behavioral signal we were looking for."
- "These firms are building redundant capacity — not because it's efficient, but because geopolitical risk makes it necessary."

---

## Slide 12 — ST4: GPR Drives CapEx (Raunak) | 1 min

**Title:** "GPR Spikes Predict CapEx Increases 1–2 Years Later"

**Visual:** `st4_gpr_vs_capex.png`

**Talking points:**
- "Overlaying annual GPR with semiconductor CapEx intensity, the positive association is clear."
- "The descriptive correlation is r = 0.56 — geopolitical risk explains over a third of the variance in semiconductor capital investment."
- "Intel's $20B Ohio fab, TSMC's Arizona expansion, Samsung's Texas fab — all announced 2021–2022, right after the GPR spike."
- "This isn't coincidence. It's boardrooms pricing in supply chain risk."

---

## Slide 13 — Integration: Everything Together (Tarun) | 1 min

**Title:** "The Full Chain: From Shock to Spending"

**Visual:** `integration_causal_chain.png`

**Talking points:**
- "This is the thesis in a single chart."
- "Top panel: GPR spikes at major events. Second panel: commodity price volatility follows. Third panel: global renewables share rises continuously. Bottom panel: semiconductor CapEx intensity climbs."
- "All four panels on the same time axis, all moving in the direction the causal chain predicts."
- "The GSCPI-to-semiconductor-CapEx correlation is 0.71. Renewables-to-CapEx is 0.82."
- "The energy transition and geopolitical risk are co-conspirators in forcing corporate capital reallocation."

---

## Slide 14 — Integration: Regime Map (Tarun) | 45 sec

**Title:** "Years With Double Risk See Maximum CapEx Deployment"

**Visual:** `integration_four_box_regime.png`

**Talking points:**
- "We classified each year by its combination of geopolitical risk and supply concentration."
- "Years in the top-right Double Risk quadrant — high GPR and high HHI — have the largest CapEx bubbles."
- "2018, 2019, 2021, 2022 all cluster there. Those are exactly the years corporations announced the largest fab investments."
- "The regime map confirms: firms deploy capital hardest when both risks compound simultaneously."

---

## Slide 15 — Closing (Tarun) | 30 sec

**Title:** "What We Found — and What It Means"

**Visual:** The 4-step causal chain arrow diagram from Slide 2, now with correlation values filled in

```
Geopolitical Shock → Supply Distortion → Energy Policy Amplifies → CapEx Response
   GPR→GSCPI: r=0.20    HHI: 0.77 peak    Renewables 30x growth    GPR→CapEx: r=0.56
```

**Talking points:**
- "Geopolitical risk transmits to supply chains. Supply chains are structurally concentrated. Energy policy amplifies demand. Corporations respond with capital."
- "The chain is measurable, consistent across 13 years, and getting stronger — not weaker."
- "This project is also the analytical foundation for a geopolitical supply chain intelligence SaaS — a live dashboard that monitors this chain in real time."
- "Thank you. We're happy to take questions."

---

## Slide Design Notes

- **Dark theme** throughout — use project palette (`#0A0A0F` background, `#00FFB2` ST1, `#FF6B35` ST2, `#A78BFA` ST3, `#FACC15` ST4)
- **One key stat per slide** — large font, center-aligned, makes the number stick
- **Every chart slide:** chart takes 70% of the slide, 3 bullet talking points take 30%
- **Transition:** each section ends with a one-liner that hands off to the next speaker
- **Avoid reading off slides** — slides are visual anchors, not teleprompters
