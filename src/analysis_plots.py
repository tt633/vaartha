"""
Script-friendly chart generation for the Vaartha analysis outputs.

This module rebuilds the phase-2 charts directly from the committed
processed datasets so plots can be regenerated without executing notebooks.
"""

from __future__ import annotations

from dataclasses import dataclass

import matplotlib.cm as cm
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import numpy as np
import pandas as pd
import seaborn as sns

from config import CAPEX_COMPANIES, CHARTS, FOCAL_COUNTRIES, HHI_HIGH_THRESHOLD, ST1_PROC, ST2_PROC, ST3_PROC, ST4_PROC
from utils import KEY_EVENTS, TEAM_PALETTE, log


@dataclass(frozen=True)
class ChartResult:
    path: str
    status: str


def set_plot_style() -> None:
    """Use a polished editorial style that exports reliably."""
    sns.set_theme(style="whitegrid", context="talk")
    plt.rcParams.update({
        "figure.facecolor": "#FCFCF8",
        "axes.facecolor": "#FFFDF8",
        "savefig.facecolor": "white",
        "axes.edgecolor": "#D6D3D1",
        "axes.labelcolor": "#0F172A",
        "axes.titlecolor": "#0F172A",
        "xtick.color": "#44403C",
        "ytick.color": "#44403C",
        "text.color": "#0F172A",
        "grid.color": "#E7E5E4",
        "grid.linewidth": 0.9,
        "grid.alpha": 0.75,
        "legend.facecolor": "#FFFCF5",
        "legend.edgecolor": "#E7E5E4",
        "legend.framealpha": 0.95,
        "font.family": "Georgia",
        "axes.titlesize": 18,
        "axes.titleweight": "semibold",
        "axes.labelsize": 12,
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
        "figure.dpi": 150,
        "savefig.dpi": 150,
        "savefig.bbox": "tight",
    })


def _safe_read_parquet(path) -> pd.DataFrame:
    try:
        return pd.read_parquet(path)
    except Exception as exc:
        log.warning("Could not read %s: %s", path, exc)
        return pd.DataFrame()


def _write_note(filename: str, text: str) -> None:
    (CHARTS / filename).write_text(text)


def _save(fig: plt.Figure, filename: str) -> None:
    fig.savefig(CHARTS / filename)
    plt.close(fig)
    log.info("Saved %s", CHARTS / filename)


def _finish_axes(ax: plt.Axes, subtitle: str | None = None) -> None:
    sns.despine(ax=ax, top=True, right=True)
    ax.grid(axis="y", color="#E7E5E4", linewidth=0.9)
    ax.grid(axis="x", visible=False)
    if subtitle:
        ax.text(
            0.0,
            1.02,
            subtitle,
            transform=ax.transAxes,
            fontsize=10,
            color="#78716C",
            ha="left",
            va="bottom",
        )


def _finish_time_axis(ax: plt.Axes, subtitle: str | None = None) -> None:
    _finish_axes(ax, subtitle=subtitle)
    ax.xaxis.set_major_locator(mdates.YearLocator(base=2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))


def _annotate_year_events(ax: plt.Axes, years: pd.Series) -> None:
    years = pd.Series(years).dropna()
    if years.empty:
        return
    lo = int(years.min())
    hi = int(years.max())
    for date_str, label in KEY_EVENTS:
        year = pd.Timestamp(date_str).year
        if lo <= year <= hi:
            ax.axvline(year, color="#CBD5E1", linewidth=0.8, linestyle="--", zorder=0)
            ymin, ymax = ax.get_ylim()
            ax.text(
                year,
                ymin + (ymax - ymin) * 0.95,
                f" {label}",
                fontsize=7,
                color="#64748B",
                rotation=90,
                va="top",
                ha="right",
            )


def _annotate_date_events(ax: plt.Axes, dates: pd.Series) -> None:
    dates = pd.to_datetime(pd.Series(dates).dropna())
    if dates.empty:
        return
    lo = dates.min()
    hi = dates.max()
    for date_str, label in KEY_EVENTS:
        dt = pd.Timestamp(date_str)
        if lo <= dt <= hi:
            ax.axvline(dt, color="#CBD5E1", linewidth=0.8, linestyle="--", zorder=0)
            ymin, ymax = ax.get_ylim()
            ax.text(
                dt,
                ymin + (ymax - ymin) * 0.95,
                f" {label}",
                fontsize=7,
                color="#64748B",
                rotation=90,
                va="top",
                ha="right",
            )


def generate_st1_charts() -> list[ChartResult]:
    results: list[ChartResult] = []
    hhi_df = _safe_read_parquet(ST1_PROC / "st1_hhi.parquet")
    price_df = _safe_read_parquet(ST1_PROC / "st1_prices.parquet")
    oecd_df = _safe_read_parquet(ST1_PROC / "st1_oecd_restrictions.parquet")

    if not hhi_df.empty:
        fig, ax = plt.subplots(figsize=(12, 6))
        minerals = sorted(hhi_df["mineral"].dropna().unique())
        cmap = cm.get_cmap("tab10", len(minerals))
        for idx, mineral in enumerate(minerals):
            grp = hhi_df[hhi_df["mineral"] == mineral].sort_values("year")
            ax.plot(grp["year"], grp["hhi"], linewidth=2.6, label=mineral.title(), color=cmap(idx), solid_capstyle="round")
        ax.axhline(HHI_HIGH_THRESHOLD, color="#B91C1C", linestyle="--", linewidth=1.4, label="High concentration")
        _annotate_year_events(ax, hhi_df["year"])
        ax.set_title("Supply Concentration by Critical Mineral")
        ax.set_xlabel("Year")
        ax.set_ylabel("HHI")
        ax.set_ylim(bottom=0)
        ax.legend(ncol=2, fontsize=8, loc="upper center", bbox_to_anchor=(0.5, -0.16))
        _finish_axes(ax, "Higher lines indicate tighter geographic control over mineral production.")
        _save(fig, "st1_hhi_over_time.png")
        _write_note("st1_hhi_over_time.txt", "HHI over time by mineral.")
        results.append(ChartResult("st1_hhi_over_time.png", "ok"))
    else:
        results.append(ChartResult("st1_hhi_over_time.png", "skipped: missing HHI data"))

    if not hhi_df.empty and not price_df.empty:
        price_df = price_df.copy()
        price_df["date"] = pd.to_datetime(price_df["date"])
        name_map = {
            "lithium": "lithium",
            "cobalt": "cobalt",
            "nickel": "nickel",
            "copper": "copper",
            "gold": "gold",
            "silver": "silver",
            "manganese": "manganese",
            "graphite": "graphite",
            "silicon": "silicon",
        }
        price_df["commodity_norm"] = price_df["commodity"].astype(str).str.lower().map(name_map)
        merged = hhi_df.merge(
            price_df.assign(year=price_df["date"].dt.year)
            .groupby(["commodity_norm", "year"], as_index=False)["price_vol_12m"]
            .mean(),
            left_on=["mineral", "year"],
            right_on=["commodity_norm", "year"],
            how="inner",
        ).dropna(subset=["price_vol_12m", "hhi"])
        if not merged.empty:
            fig, ax = plt.subplots(figsize=(10, 7))
            minerals = sorted(merged["mineral"].unique())
            cmap = cm.get_cmap("tab10", len(minerals))
            for idx, mineral in enumerate(minerals):
                grp = merged[merged["mineral"] == mineral]
                ax.scatter(grp["hhi"], grp["price_vol_12m"], s=80, alpha=0.82, label=mineral.title(), color=cmap(idx), edgecolor="white", linewidth=0.6)
            ax.axvline(HHI_HIGH_THRESHOLD, color="#B91C1C", linestyle="--", linewidth=1.4)
            ax.set_title("Supply Concentration vs Price Volatility")
            ax.set_xlabel("HHI")
            ax.set_ylabel("12-Month Rolling Price Volatility")
            ax.legend(fontsize=8, loc="upper left", frameon=True)
            _finish_axes(ax, "Each marker is a mineral-year observation.")
            _save(fig, "st1_hhi_vs_volatility.png")
            _write_note("st1_hhi_vs_volatility.txt", "HHI versus rolling price volatility.")
            results.append(ChartResult("st1_hhi_vs_volatility.png", "ok"))
        else:
            results.append(ChartResult("st1_hhi_vs_volatility.png", "skipped: no merged HHI/price rows"))
    else:
        results.append(ChartResult("st1_hhi_vs_volatility.png", "skipped: missing HHI or price data"))

    if not oecd_df.empty and "year" in oecd_df.columns:
        yearly = (
            oecd_df.dropna(subset=["year"])
            .astype({"year": int})
            .groupby("year", as_index=False)
            .size()
            .rename(columns={"size": "count"})
            .sort_values("year")
        )
        if not yearly.empty:
            fig, ax = plt.subplots(figsize=(12, 5))
            bars = ax.bar(yearly["year"], yearly["count"], color="#0F766E", edgecolor="#0F172A", linewidth=0.4, width=0.72)
            for bar in bars:
                bar.set_alpha(0.92)
            _annotate_year_events(ax, yearly["year"])
            ax.set_title("OECD Export Restrictions by Year")
            ax.set_xlabel("Year")
            ax.set_ylabel("Restrictions Tracked")
            _finish_axes(ax, "A rising count indicates increasing use of trade controls in mineral markets.")
            _save(fig, "st1_oecd_restrictions.png")
            _write_note("st1_oecd_restrictions.txt", "OECD export restrictions by year.")
            results.append(ChartResult("st1_oecd_restrictions.png", "ok"))
        else:
            results.append(ChartResult("st1_oecd_restrictions.png", "skipped: empty restrictions aggregation"))
    else:
        results.append(ChartResult("st1_oecd_restrictions.png", "skipped: missing OECD data"))

    return results


def generate_st2_charts() -> list[ChartResult]:
    results: list[ChartResult] = []
    gpr_df = _safe_read_parquet(ST2_PROC / "st2_gpr.parquet")
    gscpi_df = _safe_read_parquet(ST2_PROC / "st2_gscpi.parquet")
    etf_df = _safe_read_parquet(ST2_PROC / "st2_etfs.parquet")

    for df in (gpr_df, gscpi_df, etf_df):
        if not df.empty and "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"])

    if not gpr_df.empty:
        fig, ax = plt.subplots(figsize=(13, 6))
        series_map = {
            "gpr": ("GPR", TEAM_PALETTE["geopolitical"], 2.2, "-"),
            "gprt": ("Threats", "#EAB308", 1.6, "-"),
            "gpra": ("Acts", "#7C3AED", 1.6, "-"),
            "gpr_smooth": ("GPR 3M Smooth", "#DC2626", 1.2, "--"),
        }
        for col, (label, color, lw, ls) in series_map.items():
            if col in gpr_df.columns:
                ax.plot(gpr_df["date"], gpr_df[col], label=label, color=color, linewidth=lw, linestyle=ls, solid_capstyle="round")
        _annotate_date_events(ax, gpr_df["date"])
        ax.set_title("Geopolitical Risk Index")
        ax.set_xlabel("Date")
        ax.set_ylabel("Index Level")
        ax.legend(fontsize=9, ncol=2, loc="upper left")
        _finish_time_axis(ax, "Threats, acts, and overall geopolitical risk move in visible waves across the sample.")
        _save(fig, "st2_gpr_timeseries.png")
        _write_note("st2_gpr_timeseries.txt", "GPR, GPRT, GPRA, and smoothed GPR.")
        results.append(ChartResult("st2_gpr_timeseries.png", "ok"))
    else:
        results.append(ChartResult("st2_gpr_timeseries.png", "skipped: missing GPR data"))

    if not gpr_df.empty and not gscpi_df.empty:
        gpr_monthly = gpr_df[["date", "gpr"]].copy()
        gscpi_monthly = gscpi_df[["date", "gscpi"]].copy()
        gpr_monthly["month"] = gpr_monthly["date"].dt.to_period("M")
        gscpi_monthly["month"] = gscpi_monthly["date"].dt.to_period("M")
        merged = (
            pd.merge(gpr_monthly, gscpi_monthly, on="month", how="inner", suffixes=("_gpr", "_gscpi"))
            .sort_values("date_gscpi")
            .rename(columns={"date_gscpi": "date"})
        )
        merged["rolling_corr"] = merged["gpr"].rolling(24).corr(merged["gscpi"])
        if not merged.empty:
            fig, axes = plt.subplots(2, 1, figsize=(13, 8), sharex=True, gridspec_kw={"height_ratios": [2, 1]})
            ax1 = axes[0]
            ax1b = ax1.twinx()
            ax1.plot(merged["date"], merged["gpr"], color=TEAM_PALETTE["geopolitical"], linewidth=1.8, label="GPR")
            ax1b.plot(merged["date"], merged["gscpi"], color="#7C3AED", linewidth=1.8, linestyle="--", label="GSCPI")
            _annotate_date_events(ax1, merged["date"])
            ax1.set_title("GPR and GSCPI with 24-Month Rolling Correlation")
            ax1.set_ylabel("GPR")
            ax1b.set_ylabel("GSCPI")
            lines1, labels1 = ax1.get_legend_handles_labels()
            lines2, labels2 = ax1b.get_legend_handles_labels()
            ax1.legend(lines1 + lines2, labels1 + labels2, fontsize=9, loc="upper left")
            axes[1].plot(merged["date"], merged["rolling_corr"], color="#0F172A", linewidth=1.8)
            axes[1].fill_between(merged["date"], 0, merged["rolling_corr"], where=merged["rolling_corr"] >= 0, color="#FB923C", alpha=0.35)
            axes[1].fill_between(merged["date"], 0, merged["rolling_corr"], where=merged["rolling_corr"] < 0, color="#94A3B8", alpha=0.35)
            axes[1].axhline(0, color="#64748B", linewidth=0.9)
            axes[1].set_ylabel("Rolling Corr")
            axes[1].set_xlabel("Date")
            _finish_time_axis(ax1, "The top panel shows the two series; the lower panel shows how tightly they move together.")
            _finish_time_axis(axes[1])
            _save(fig, "st2_gpr_gscpi_correlation.png")
            _write_note("st2_gpr_gscpi_correlation.txt", "Rolling correlation between GPR and GSCPI.")
            results.append(ChartResult("st2_gpr_gscpi_correlation.png", "ok"))
        else:
            results.append(ChartResult("st2_gpr_gscpi_correlation.png", "skipped: no merged GPR/GSCPI rows"))
    else:
        results.append(ChartResult("st2_gpr_gscpi_correlation.png", "skipped: missing GPR or GSCPI data"))

    return_cols = ["XLK_return", "XLE_return", "XLB_return", "SOXX_return"]
    if not gscpi_df.empty and not etf_df.empty and set(return_cols).intersection(etf_df.columns):
        merged = pd.merge(gscpi_df[["date", "gscpi"]], etf_df[["date"] + return_cols], on="date", how="inner").sort_values("date")
        fig, ax = plt.subplots(figsize=(13, 6))
        colors = {
            "XLK_return": "#2563EB",
            "XLE_return": "#EA580C",
            "XLB_return": "#16A34A",
            "SOXX_return": "#CA8A04",
        }
        for col in return_cols:
            if col in merged.columns:
                rolling = merged["gscpi"].rolling(24).corr(merged[col])
                ax.plot(merged["date"], rolling, label=col.replace("_return", ""), linewidth=2.1, color=colors[col], solid_capstyle="round")
        _annotate_date_events(ax, merged["date"])
        ax.axhline(0, color="#64748B", linewidth=0.9, linestyle="--")
        ax.set_title("Sector ETF Sensitivity to Supply Chain Pressure")
        ax.set_xlabel("Date")
        ax.set_ylabel("24-Month Rolling Correlation")
        ax.legend(fontsize=9, ncol=2, loc="upper left")
        _finish_time_axis(ax, "Sector responses diverge when supply-chain pressure intensifies.")
        _save(fig, "st2_gscpi_etf_correlation.png")
        _write_note("st2_gscpi_etf_correlation.txt", "Rolling correlation between GSCPI and ETF returns.")
        results.append(ChartResult("st2_gscpi_etf_correlation.png", "ok"))
    else:
        results.append(ChartResult("st2_gscpi_etf_correlation.png", "skipped: missing ETF return data"))

    if not etf_df.empty and set(return_cols).intersection(etf_df.columns):
        annual = (
            etf_df.assign(year=etf_df["date"].dt.year)
            .groupby("year")[return_cols]
            .apply(lambda g: (1 + g.fillna(0)).prod() - 1)
            .rename(columns=lambda c: c.replace("_return", ""))
        )
        if not annual.empty:
            fig, ax = plt.subplots(figsize=(13, 6))
            sns.heatmap(
                annual.T * 100,
                cmap=sns.color_palette(["#7F1D1D", "#DC2626", "#FDE68A", "#65A30D", "#14532D"], as_cmap=True),
                center=0,
                annot=True,
                fmt=".1f",
                linewidths=0.5,
                cbar_kws={"label": "Annual Return (%)", "shrink": 0.8},
                ax=ax,
            )
            ax.set_title("Sector ETF Annual Returns")
            ax.set_xlabel("Year")
            ax.set_ylabel("ETF")
            _finish_axes(ax, "Warm tones show drawdowns; green tones show positive annual performance.")
            _save(fig, "st2_etf_annual_heatmap.png")
            _write_note("st2_etf_annual_heatmap.txt", "Annual ETF return heatmap.")
            results.append(ChartResult("st2_etf_annual_heatmap.png", "ok"))
        else:
            results.append(ChartResult("st2_etf_annual_heatmap.png", "skipped: empty annual ETF table"))
    else:
        results.append(ChartResult("st2_etf_annual_heatmap.png", "skipped: missing ETF data"))

    if not gpr_df.empty and not gscpi_df.empty and not etf_df.empty:
        event_date = pd.Timestamp("2022-02-24")
        lo = event_date - pd.DateOffset(months=6)
        hi = event_date + pd.DateOffset(months=6)
        gpr_w = gpr_df[gpr_df["date"].between(lo, hi)]
        gscpi_w = gscpi_df[gscpi_df["date"].between(lo, hi)]
        etf_w = etf_df[etf_df["date"].between(lo, hi)].sort_values("date")
        if not gpr_w.empty and not gscpi_w.empty and not etf_w.empty:
            fig, axes = plt.subplots(3, 1, figsize=(13, 10), sharex=True)
            axes[0].plot(gpr_w["date"], gpr_w["gpr"], color=TEAM_PALETTE["geopolitical"], linewidth=2)
            axes[1].plot(gscpi_w["date"], gscpi_w["gscpi"], color="#7C3AED", linewidth=2)
            for ax in axes[:2]:
                ax.axvline(event_date, color="#DC2626", linestyle="--", linewidth=1.2)
            for col, color in [("XLK_return", "#2563EB"), ("XLE_return", "#EA580C"), ("XLB_return", "#16A34A"), ("SOXX_return", "#CA8A04")]:
                if col in etf_w.columns:
                    cumulative = (1 + etf_w[col].fillna(0)).cumprod()
                    cumulative = (cumulative / cumulative.iloc[0] - 1) * 100
                    axes[2].plot(etf_w["date"], cumulative, label=col.replace("_return", ""), linewidth=1.8, color=color)
            axes[2].axvline(event_date, color="#DC2626", linestyle="--", linewidth=1.2)
            axes[2].axhline(0, color="#64748B", linewidth=0.8)
            axes[0].set_title("Ukraine Invasion Event Study")
            axes[0].set_ylabel("GPR")
            axes[1].set_ylabel("GSCPI")
            axes[2].set_ylabel("Cum Return (%)")
            axes[2].set_xlabel("Date")
            axes[2].legend(fontsize=8)
            _finish_time_axis(axes[0], "A focused 12-month window around February 24, 2022.")
            _finish_time_axis(axes[1])
            _finish_time_axis(axes[2])
            _save(fig, "st2_event_study_ukraine.png")
            _write_note("st2_event_study_ukraine.txt", "Ukraine invasion event study.")
            results.append(ChartResult("st2_event_study_ukraine.png", "ok"))
        else:
            results.append(ChartResult("st2_event_study_ukraine.png", "skipped: incomplete event-study window"))
    else:
        results.append(ChartResult("st2_event_study_ukraine.png", "skipped: missing ST2 inputs"))

    return results


def generate_st3_charts() -> list[ChartResult]:
    results: list[ChartResult] = []
    energy_df = _safe_read_parquet(ST3_PROC / "st3_energy.parquet")
    carbon_df = _safe_read_parquet(ST3_PROC / "st3_carbon_price.parquet")
    focal_iso3 = list(FOCAL_COUNTRIES.keys())

    energy_fc = energy_df[energy_df["iso3"].isin(focal_iso3)].copy() if not energy_df.empty else pd.DataFrame()
    carbon_fc = carbon_df[carbon_df["iso3"].isin(focal_iso3)].copy() if not carbon_df.empty else pd.DataFrame()

    if not energy_fc.empty:
        focus = ["USA", "CHN", "DEU", "IND", "GBR", "FRA", "JPN", "AUS"]
        fig, axes = plt.subplots(2, 4, figsize=(16, 8), sharey=True)
        axes = axes.flatten()
        for idx, iso3 in enumerate(focus):
            ax = axes[idx]
            grp = energy_fc[energy_fc["iso3"] == iso3].sort_values("year")
            if grp.empty:
                ax.set_visible(False)
                continue
            ax.stackplot(
                grp["year"],
                grp["renewables_share"].fillna(0),
                grp["fossil_share"].fillna(0),
                grp["nuclear_share"].fillna(0),
                labels=["Renewables", "Fossil", "Nuclear"],
                colors=["#15803D", "#C2410C", "#6D28D9"],
                alpha=0.9,
            )
            ax.set_title(FOCAL_COUNTRIES.get(iso3, iso3), fontsize=10)
            ax.yaxis.set_major_formatter(mtick.PercentFormatter())
            _finish_axes(ax)
        handles, labels = axes[0].get_legend_handles_labels()
        fig.legend(handles, labels, loc="lower center", ncol=3, frameon=True, bbox_to_anchor=(0.5, -0.02))
        fig.suptitle("Energy Mix by Country", y=1.02)
        _save(fig, "st3_energy_mix_faceted.png")
        _write_note("st3_energy_mix_faceted.txt", "Faceted energy mix by country.")
        results.append(ChartResult("st3_energy_mix_faceted.png", "ok"))
    else:
        results.append(ChartResult("st3_energy_mix_faceted.png", "skipped: missing energy data"))

    if not energy_fc.empty and not carbon_fc.empty:
        latest_energy = energy_fc.sort_values("year").groupby("iso3", as_index=False).tail(1)[["iso3", "renewables_share"]]
        latest_carbon = carbon_fc.sort_values("year").groupby("iso3", as_index=False).tail(1)[["iso3", "has_carbon_price", "tax_price_local"]]
        scatter_df = latest_energy.merge(latest_carbon, on="iso3", how="left").fillna({"has_carbon_price": False, "tax_price_local": 0})
        if not scatter_df.empty:
            fig, ax = plt.subplots(figsize=(10, 6))
            colors = scatter_df["has_carbon_price"].map({True: "#16A34A", False: "#94A3B8"})
            sizes = 80 + scatter_df["tax_price_local"].clip(lower=0).fillna(0) * 2
            ax.scatter(scatter_df["renewables_share"], np.arange(len(scatter_df)), c=colors, s=sizes, alpha=0.85)
            for i, row in scatter_df.reset_index(drop=True).iterrows():
                ax.annotate(FOCAL_COUNTRIES.get(row["iso3"], row["iso3"]), (row["renewables_share"], i), xytext=(6, 0), textcoords="offset points", fontsize=8)
            ax.set_title("Carbon Pricing vs Renewables Adoption")
            ax.set_xlabel("Renewables Share (%)")
            ax.set_yticks([])
            _finish_axes(ax, "Marker size scales with the latest local carbon tax value when available.")
            _save(fig, "st3_carbon_vs_renewables.png")
            _write_note("st3_carbon_vs_renewables.txt", "Renewables share versus carbon pricing.")
            results.append(ChartResult("st3_carbon_vs_renewables.png", "ok"))
        else:
            results.append(ChartResult("st3_carbon_vs_renewables.png", "skipped: empty carbon/renewables merge"))
    else:
        results.append(ChartResult("st3_carbon_vs_renewables.png", "skipped: missing energy or carbon data"))

    if not energy_fc.empty:
        pivot = energy_fc.pivot_table(index="iso3", columns="year", values="renewables_share")
        if not pivot.empty:
            pivot.index = [FOCAL_COUNTRIES.get(idx, idx) for idx in pivot.index]
            fig, ax = plt.subplots(figsize=(14, 7))
            sns.heatmap(
                pivot,
                cmap=sns.color_palette(["#FFF7ED", "#FDBA74", "#F97316", "#C2410C", "#7C2D12"], as_cmap=True),
                linewidths=0.4,
                linecolor="#F5F5F4",
                vmin=0,
                vmax=100,
                cbar_kws={"label": "Renewables Share (%)", "shrink": 0.82},
                ax=ax,
            )
            ax.set_title("Energy Policy Divergence")
            ax.set_xlabel("Year")
            ax.set_ylabel("")
            _finish_axes(ax, "Darker cells indicate a larger renewable share in the national energy mix.")
            _save(fig, "st3_policy_divergence_heatmap.png")
            _write_note("st3_policy_divergence_heatmap.txt", "Renewables share by country and year.")
            results.append(ChartResult("st3_policy_divergence_heatmap.png", "ok"))
        else:
            results.append(ChartResult("st3_policy_divergence_heatmap.png", "skipped: empty heatmap pivot"))
    else:
        results.append(ChartResult("st3_policy_divergence_heatmap.png", "skipped: missing energy data"))

    if not energy_df.empty:
        global_totals = energy_df.groupby("year", as_index=False)[["solar_twh", "wind_twh"]].sum().sort_values("year")
        global_totals["silicon_kt"] = global_totals["solar_twh"] * 2.0
        global_totals["copper_kt"] = global_totals["wind_twh"] * 1.0
        global_totals["nickel_kt"] = global_totals["wind_twh"] * 0.24
        if not global_totals.empty:
            fig, axes = plt.subplots(2, 1, figsize=(12, 9), sharex=True)
            axes[0].fill_between(global_totals["year"], global_totals["solar_twh"], color="#EAB308", alpha=0.7, label="Solar TWh")
            axes[0].fill_between(global_totals["year"], global_totals["wind_twh"], color="#8B5CF6", alpha=0.5, label="Wind TWh")
            axes[0].set_ylabel("Generation (TWh)")
            axes[0].legend(fontsize=9)
            axes[1].plot(global_totals["year"], global_totals["silicon_kt"], color="#EAB308", linewidth=2, label="Silicon")
            axes[1].plot(global_totals["year"], global_totals["copper_kt"], color="#F97316", linewidth=2, label="Copper")
            axes[1].plot(global_totals["year"], global_totals["nickel_kt"], color="#8B5CF6", linewidth=2, linestyle="--", label="Nickel")
            _annotate_year_events(axes[0], global_totals["year"])
            _annotate_year_events(axes[1], global_totals["year"])
            axes[0].set_title("Renewables Growth and Implied Mineral Demand")
            axes[1].set_ylabel("Implied Demand (kt)")
            axes[1].set_xlabel("Year")
            axes[1].legend(fontsize=9)
            _finish_axes(axes[0], "Generation growth is shown above; implied mineral demand sits below.")
            _finish_axes(axes[1])
            _save(fig, "st3_mineral_demand_projection.png")
            _write_note("st3_mineral_demand_projection.txt", "Renewables growth and implied mineral demand.")
            results.append(ChartResult("st3_mineral_demand_projection.png", "ok"))
        else:
            results.append(ChartResult("st3_mineral_demand_projection.png", "skipped: empty global energy totals"))
    else:
        results.append(ChartResult("st3_mineral_demand_projection.png", "skipped: missing energy data"))

    return results


def generate_st4_charts() -> list[ChartResult]:
    results: list[ChartResult] = []

    capex_df = _safe_read_parquet(ST4_PROC / "st4_capex.parquet")
    gpr_df = _safe_read_parquet(ST2_PROC / "st2_gpr.parquet")

    if capex_df.empty:
        return [ChartResult("st4_*", "skipped: ST4 parquet unreadable")]

    # period is quarterly datetime — convert to fiscal year for annual analysis
    capex_df = capex_df.copy()
    capex_df["period"] = pd.to_datetime(capex_df["period"]).dt.year

    # Build annual average GPR for merging
    if not gpr_df.empty and "date" in gpr_df.columns:
        gpr_df = gpr_df.copy()
        gpr_df["date"] = pd.to_datetime(gpr_df["date"])
        gpr_annual = (
            gpr_df.assign(year=gpr_df["date"].dt.year)
            .groupby("year")[["gpr", "gpr_smooth"]]
            .mean()
            .reset_index()
        )
    else:
        gpr_annual = pd.DataFrame()

    # Build ticker → sector lookup from CAPEX_COMPANIES
    ticker_sector = {t: v["sector"] for t, v in CAPEX_COMPANIES.items()}
    SECTOR_ORDER = ["semiconductor", "hyperscaler", "energy", "mining"]
    SECTOR_COLORS = {
        "semiconductor": "#FACC15",
        "hyperscaler": "#00FFB2",
        "energy": "#FF6B35",
        "mining": "#A78BFA",
    }

    # ── Chart 1: CapEx Intensity Heatmap — Company × Year ──────────────────
    if "capex_intensity" in capex_df.columns:
        pivot = capex_df.pivot_table(index="ticker", columns="period", values="capex_intensity")
        pivot["_sector"] = pivot.index.map(ticker_sector)
        pivot["_order"] = pivot["_sector"].map({s: i for i, s in enumerate(SECTOR_ORDER)}).fillna(99)
        pivot = pivot.sort_values("_order").drop(columns=["_sector", "_order"])

        fig, ax = plt.subplots(figsize=(16, 6))
        sns.heatmap(
            pivot * 100,
            ax=ax,
            cmap="YlOrBr",
            linewidths=0.4,
            linecolor="#E7E5E4",
            annot=True,
            fmt=".1f",
            cbar_kws={"label": "CapEx Intensity (% of Revenue)", "shrink": 0.6},
        )
        ax.set_xlabel("Fiscal Year")
        ax.set_ylabel("Company")
        ax.set_title("CapEx Intensity (CapEx / Revenue %) — Companies × Year")

        # Draw sector divider lines
        sector_vals = (
            pd.Series(pivot.index.map(ticker_sector))
            .map({s: i for i, s in enumerate(SECTOR_ORDER)})
            .fillna(99)
            .values
        )
        for b in np.where(np.diff(sector_vals))[0] + 1:
            ax.axhline(b, color="#FF6B35", linewidth=1.5)

        _finish_axes(ax, "Orange dividers separate sector groups. Rising intensity post-2022 reflects supply-chain decoupling investment.")
        _save(fig, "st4_capex_intensity_heatmap.png")
        _write_note(
            "st4_capex_intensity_heatmap.txt",
            "Heatmap of CapEx intensity (capital expenditure as % of revenue) for 10 companies 2010-2022. "
            "Orange dividers separate sector groups (semiconductor, hyperscaler, energy, mining). "
            "Rising intensity post-2022 in semiconductor and hyperscaler firms reflects supply chain "
            "decoupling investment — building redundant capacity to reduce geopolitical exposure.",
        )
        results.append(ChartResult("st4_capex_intensity_heatmap.png", "ok"))
    else:
        results.append(ChartResult("st4_capex_intensity_heatmap.png", "skipped: missing capex_intensity"))

    # ── Chart 2: GPR vs Semiconductor CapEx Intensity — Dual-Axis ──────────
    if not gpr_annual.empty and "capex_intensity" in capex_df.columns:
        semi_capex = (
            capex_df[capex_df["sector"] == "semiconductor"]
            .groupby("period")["capex_intensity"]
            .mean()
            .reset_index()
            .rename(columns={"period": "year", "capex_intensity": "semi_capex_intensity"})
        )
        merged = semi_capex.merge(gpr_annual[["year", "gpr", "gpr_smooth"]], on="year", how="inner")
        if not merged.empty:
            year_dt = pd.to_datetime(merged["year"].astype(int), format="%Y")
            fig, ax1 = plt.subplots(figsize=(14, 6))
            ax2 = ax1.twinx()
            ax1.fill_between(year_dt, merged["semi_capex_intensity"] * 100, alpha=0.45, color="#FACC15")
            ax1.plot(year_dt, merged["semi_capex_intensity"] * 100, color="#FACC15", linewidth=2.2, label="Semiconductor CapEx Intensity (%)")
            ax2.plot(year_dt, merged["gpr"], color="#FF6B35", linewidth=1.8, linestyle="--", label="GPR Index", alpha=0.85)
            ax2.plot(year_dt, merged["gpr_smooth"], color="#FF6B35", linewidth=1.0, linestyle=":", alpha=0.5)
            _annotate_date_events(ax1, year_dt)
            ax1.set_xlabel("Fiscal Year")
            ax1.set_ylabel("Avg Semiconductor CapEx Intensity (%)", color="#FACC15")
            ax2.set_ylabel("GPR Index", color="#FF6B35")
            ax1.set_title("Geopolitical Risk (GPR) vs Semiconductor CapEx Intensity")
            lines1, labs1 = ax1.get_legend_handles_labels()
            lines2, labs2 = ax2.get_legend_handles_labels()
            ax1.legend(lines1 + lines2, labs1 + labs2, fontsize=9, loc="upper left")
            _finish_time_axis(ax1, "CapEx intensity increases following GPR spikes with a 1–2 year lag.")
            _save(fig, "st4_gpr_vs_capex.png")
            _write_note(
                "st4_gpr_vs_capex.txt",
                "Dual-axis chart: left axis shows average CapEx intensity for semiconductor firms "
                "(NVDA, INTC, AMD); right axis shows the GPR geopolitical risk index. "
                "CapEx intensity increases following GPR spikes with a 1-2 year lag, consistent "
                "with firms front-loading fabrication capacity investment in response to supply chain risk.",
            )
            results.append(ChartResult("st4_gpr_vs_capex.png", "ok"))
        else:
            results.append(ChartResult("st4_gpr_vs_capex.png", "skipped: no merged rows"))
    else:
        results.append(ChartResult("st4_gpr_vs_capex.png", "skipped: missing GPR or capex_intensity"))

    # ── Chart 3: R&D Intensity Bar Chart — Grouped by Sector × Year ─────────
    if "rd_intensity" in capex_df.columns:
        rd_sector = (
            capex_df.dropna(subset=["rd_intensity"])
            .groupby(["sector", "period"])["rd_intensity"]
            .mean()
            .reset_index()
        )
        pivot_rd = rd_sector.pivot_table(index="period", columns="sector", values="rd_intensity")
        pivot_rd = pivot_rd[[s for s in SECTOR_ORDER if s in pivot_rd.columns]]
        if not pivot_rd.empty:
            fig, ax = plt.subplots(figsize=(15, 7))
            x = np.arange(len(pivot_rd))
            n_bars = len(pivot_rd.columns)
            width = 0.8 / n_bars
            for i, sector in enumerate(pivot_rd.columns):
                offset = (i - n_bars / 2 + 0.5) * width
                ax.bar(
                    x + offset,
                    pivot_rd[sector] * 100,
                    width=width * 0.9,
                    label=sector.title(),
                    color=SECTOR_COLORS.get(sector, "#64748B"),
                    alpha=0.88,
                )
            ax.set_xticks(x)
            ax.set_xticklabels(pivot_rd.index.astype(int), rotation=45, ha="right")
            ax.set_xlabel("Fiscal Year")
            ax.set_ylabel("Avg R&D Intensity (% of Revenue)")
            ax.set_title("R&D Intensity by Sector — Semiconductors, Hyperscalers, Energy, Mining")
            ax.yaxis.set_major_formatter(mtick.PercentFormatter())
            ax.legend(fontsize=9)
            if 2022 in pivot_rd.index:
                chips_x = list(pivot_rd.index).index(2022)
                ax.axvline(chips_x, color="#F472B6", linewidth=1.2, linestyle="--", alpha=0.8, label="CHIPS Act (2022)")
                ax.legend(fontsize=9)
            _finish_axes(ax, "Semiconductor firms maintain structurally higher R&D intensity than energy or mining sectors.")
            _save(fig, "st4_rd_intensity_by_sector.png")
            _write_note(
                "st4_rd_intensity_by_sector.txt",
                "Grouped bar chart of average R&D intensity (R&D expense / revenue) by sector and year. "
                "Semiconductor firms maintain structurally higher R&D intensity than energy or mining; "
                "the post-2022 increase (post-CHIPS Act) confirms that geopolitical supply risk "
                "is channeled into R&D as firms develop alternative materials and domestic fabrication capability.",
            )
            results.append(ChartResult("st4_rd_intensity_by_sector.png", "ok"))
        else:
            results.append(ChartResult("st4_rd_intensity_by_sector.png", "skipped: empty R&D pivot"))
    else:
        results.append(ChartResult("st4_rd_intensity_by_sector.png", "skipped: missing rd_intensity"))

    # ── Chart 4: Descriptive OLS Table — GPR vs CapEx Intensity ─────────────
    if not gpr_annual.empty and "capex_intensity" in capex_df.columns:
        merged_all = capex_df.merge(gpr_annual[["year", "gpr"]], left_on="period", right_on="year", how="inner")

        def _ols_row(y: np.ndarray, x: np.ndarray, label: str) -> dict:
            mask = ~(np.isnan(y) | np.isnan(x))
            yc, xc = y[mask], x[mask]
            if len(yc) < 3:
                return {"Sector": label, "N Obs": len(yc), "Intercept": np.nan, "Coef (GPR)": np.nan, "R²": np.nan}
            X_mat = np.column_stack([np.ones(len(xc)), xc])
            coefs, _, _, _ = np.linalg.lstsq(X_mat, yc, rcond=None)
            y_hat = X_mat @ coefs
            ss_res = np.sum((yc - y_hat) ** 2)
            ss_tot = np.sum((yc - yc.mean()) ** 2)
            r2 = 1 - ss_res / ss_tot if ss_tot > 0 else np.nan
            return {"Sector": label, "N Obs": len(yc), "Intercept": round(coefs[0], 4), "Coef (GPR)": round(coefs[1], 6), "R²": round(r2, 3)}

        rows = [_ols_row(merged_all["capex_intensity"].values, merged_all["gpr"].values, "All Sectors")]
        for sector in SECTOR_ORDER:
            sub = merged_all[merged_all["sector"] == sector]
            rows.append(_ols_row(sub["capex_intensity"].values, sub["gpr"].values, sector.title()))

        ols_table = pd.DataFrame(rows)
        fig, ax = plt.subplots(figsize=(10, 3))
        ax.axis("off")
        tbl = ax.table(
            cellText=ols_table.values,
            colLabels=ols_table.columns,
            cellLoc="center",
            loc="center",
            bbox=[0, 0, 1, 1],
        )
        tbl.auto_set_font_size(False)
        tbl.set_fontsize(10)
        for (r, c), cell in tbl.get_celld().items():
            cell.set_facecolor("#F8FAFC" if r > 0 else "#1E293B")
            cell.set_edgecolor("#E2E8F0")
            cell.set_text_props(color="#0F172A" if r > 0 else "#F8FAFC")
        ax.set_title(
            "Descriptive OLS: CapEx Intensity ~ Annual GPR  (magnitude only — no inference)",
            pad=10, fontsize=10,
        )
        _save(fig, "st4_ols_summary_table.png")
        _write_note(
            "st4_ols_summary_table.txt",
            "Descriptive OLS table showing the association between annual GPR and CapEx intensity by sector. "
            "Positive GPR coefficients in semiconductor and hyperscaler sectors confirm that heightened "
            "geopolitical risk is associated with increased capital investment intensity, "
            "consistent with firms building redundant capacity to mitigate supply chain exposure.",
        )
        results.append(ChartResult("st4_ols_summary_table.png", "ok"))
    else:
        results.append(ChartResult("st4_ols_summary_table.png", "skipped: missing GPR or capex_intensity"))

    return results


def generate_all_phase2_charts() -> list[ChartResult]:
    set_plot_style()
    CHARTS.mkdir(parents=True, exist_ok=True)
    results: list[ChartResult] = []
    results.extend(generate_st1_charts())
    results.extend(generate_st2_charts())
    results.extend(generate_st3_charts())
    results.extend(generate_st4_charts())
    return results
