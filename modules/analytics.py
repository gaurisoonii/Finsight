"""
Module 2 — Analytics Engine
Provides all KPI and trend computations used by the Streamlit pages.
All functions accept an optional `filters` dict:
    filters = {"category": [...], "bank": [...], "state": [...], "date_range": (start, end)}
"""

import sqlite3
import pandas as pd
import numpy as np
from pathlib import Path
from scipy import stats as scipy_stats

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "complaints.db"


# ── DB helpers ─────────────────────────────────────────────────────────────

def _get_conn() -> sqlite3.Connection:
    return sqlite3.connect(DB_PATH)


def _apply_filters(df: pd.DataFrame, filters: dict | None) -> pd.DataFrame:
    if not filters:
        return df
    if filters.get("category"):
        df = df[df["category"].isin(filters["category"])]
    if filters.get("bank"):
        df = df[df["bank"].isin(filters["bank"])]
    if filters.get("state"):
        df = df[df["state_india"].isin(filters["state"])]
    if filters.get("date_range"):
        start, end = filters["date_range"]
        df = df[(df["date_received"] >= str(start)) & (df["date_received"] <= str(end))]
    return df


def load_all(filters: dict | None = None) -> pd.DataFrame:
    """Load full complaints table with filters applied."""
    conn = _get_conn()
    df = pd.read_sql("SELECT * FROM complaints", conn, parse_dates=["date_received"])
    conn.close()
    return _apply_filters(df, filters)


# ── KPIs ───────────────────────────────────────────────────────────────────

def kpis(filters: dict | None = None) -> dict:
    """Return top-level KPI dict."""
    df = load_all(filters)
    if df.empty:
        return {"total": 0, "resolved_pct": 0, "mom_growth": 0, "avg_daily": 0}

    total = len(df)

    resolved_pct = round(df["resolved"].mean() * 100, 1) if "resolved" in df.columns else 0.0

    # Month-over-month growth (last full month vs previous)
    monthly = (
        df.groupby("month_label")
        .size()
        .reset_index(name="count")
        .sort_values("month_label")
    )
    if len(monthly) >= 2:
        last, prev = monthly["count"].iloc[-1], monthly["count"].iloc[-2]
        mom_growth = round((last - prev) / max(prev, 1) * 100, 1)
    else:
        mom_growth = 0.0

    date_range_days = max((df["date_received"].max() - df["date_received"].min()).days, 1)
    avg_daily = round(total / date_range_days, 1)

    return {
        "total":        total,
        "resolved_pct": resolved_pct,
        "mom_growth":   mom_growth,
        "avg_daily":    avg_daily,
    }


# ── Trend ──────────────────────────────────────────────────────────────────

def monthly_trend(filters: dict | None = None) -> pd.DataFrame:
    """Monthly complaint volume with 3-month rolling average."""
    df = load_all(filters)
    trend = (
        df.groupby("month_label")
        .size()
        .reset_index(name="count")
        .sort_values("month_label")
    )
    trend["rolling_avg"] = trend["count"].rolling(3, min_periods=1).mean().round(1)
    return trend


def category_trend(filters: dict | None = None) -> pd.DataFrame:
    """Monthly complaint count broken down by category."""
    df = load_all(filters)
    return (
        df.groupby(["month_label", "category"])
        .size()
        .reset_index(name="count")
        .sort_values(["month_label", "category"])
    )


# ── Breakdown ─────────────────────────────────────────────────────────────

def category_breakdown(filters: dict | None = None) -> pd.DataFrame:
    df = load_all(filters)
    return (
        df.groupby("category")
        .size()
        .reset_index(name="count")
        .sort_values("count", ascending=False)
    )


def bank_breakdown(filters: dict | None = None, top_n: int = 10) -> pd.DataFrame:
    df = load_all(filters)
    return (
        df.groupby("bank")
        .agg(
            total=("complaint_id", "count"),
            resolved=("resolved", "sum"),
        )
        .assign(resolution_rate=lambda x: (x["resolved"] / x["total"] * 100).round(1))
        .sort_values("total", ascending=False)
        .head(top_n)
        .reset_index()
    )


def state_breakdown(filters: dict | None = None) -> pd.DataFrame:
    df = load_all(filters)
    return (
        df.groupby("state_india")
        .size()
        .reset_index(name="count")
        .sort_values("count", ascending=False)
    )


# ── Anomaly detection ──────────────────────────────────────────────────────

def detect_anomalies(filters: dict | None = None, z_threshold: float = 2.0) -> pd.DataFrame:
    """
    Weekly complaint volume with z-score anomaly flag.
    Returns DataFrame with columns: week, count, z_score, is_anomaly.
    """
    df = load_all(filters)
    df["week"] = df["date_received"].dt.to_period("W").astype(str)

    weekly = df.groupby("week").size().reset_index(name="count").sort_values("week")

    if len(weekly) < 4:
        weekly["z_score"]    = 0.0
        weekly["is_anomaly"] = False
        return weekly

    counts = weekly["count"].values
    rolling_mean = pd.Series(counts).rolling(4, min_periods=2).mean()
    rolling_std  = pd.Series(counts).rolling(4, min_periods=2).std().fillna(1)

    weekly["z_score"]    = ((counts - rolling_mean) / rolling_std).round(2)
    weekly["is_anomaly"] = weekly["z_score"].abs() > z_threshold
    return weekly


def category_anomalies(filters: dict | None = None) -> pd.DataFrame:
    """
    Per-category monthly growth rate.
    Flags categories with > 20% month-over-month spike.
    """
    trend = category_trend(filters)
    if trend.empty:
        return pd.DataFrame()

    pivot = trend.pivot_table(index="month_label", columns="category", values="count", fill_value=0)
    pct_change = pivot.pct_change() * 100

    last_month = pct_change.iloc[-1].reset_index()
    last_month.columns = ["category", "mom_pct_change"]
    last_month["spiked"] = last_month["mom_pct_change"] > 20
    return last_month.sort_values("mom_pct_change", ascending=False)


# ── Policy rules ───────────────────────────────────────────────────────────

POLICY_RULES = [
    {
        "condition": lambda cat_df: _category_spike(cat_df, "Digital payments", 20),
        "severity": "HIGH",
        "category": "Digital payments",
        "recommendation": (
            "Strengthen UPI transaction failure monitoring. "
            "Issue advisory to payment aggregators on refund timelines. "
            "Mandate 24-hour auto-reversal for failed transactions."
        ),
    },
    {
        "condition": lambda cat_df: _category_spike(cat_df, "Fraud / Unauthorized", 15),
        "severity": "CRITICAL",
        "category": "Fraud / Unauthorized",
        "recommendation": (
            "Issue immediate fraud alert circular to all scheduled banks. "
            "Review two-factor authentication compliance. "
            "Activate emergency cyber-fraud monitoring cell."
        ),
    },
    {
        "condition": lambda cat_df: _category_spike(cat_df, "ATM", 10),
        "severity": "MEDIUM",
        "category": "ATM",
        "recommendation": (
            "Review ATM network uptime SLA compliance. "
            "Enhance cash replenishment monitoring in Tier-2/3 cities. "
            "Audit failed cash-dispense reversal timelines."
        ),
    },
    {
        "condition": lambda cat_df: _category_spike(cat_df, "Loans", 10),
        "severity": "MEDIUM",
        "category": "Loans",
        "recommendation": (
            "Examine retail loan disbursement and documentation delays. "
            "Review EMI deduction error rates across top-5 lenders. "
            "Issue guidance on fair lending practice adherence."
        ),
    },
    {
        "condition": lambda cat_df: _category_spike(cat_df, "Credit / debit card", 15),
        "severity": "HIGH",
        "category": "Credit / debit card",
        "recommendation": (
            "Audit card dispute resolution timelines (target < 7 days). "
            "Review mis-selling of card products. "
            "Mandate SMS/email alerts for all card transactions > ₹500."
        ),
    },
]


def _category_spike(cat_df: pd.DataFrame, category: str, threshold_pct: float) -> bool:
    """Check if a category has spiked above threshold in the last month."""
    row = cat_df[cat_df["category"] == category]
    if row.empty:
        return False
    return float(row["mom_pct_change"].iloc[0]) > threshold_pct


def policy_recommendations(filters: dict | None = None) -> list[dict]:
    """
    Evaluate all policy rules and return triggered recommendations.
    Each dict: {severity, category, recommendation, growth_pct}
    """
    cat_anomalies = category_anomalies(filters)
    if cat_anomalies.empty:
        return []

    triggered = []
    for rule in POLICY_RULES:
        try:
            if rule["condition"](cat_anomalies):
                row = cat_anomalies[cat_anomalies["category"] == rule["category"]]
                growth = float(row["mom_pct_change"].iloc[0]) if not row.empty else 0.0
                triggered.append({
                    "severity":       rule["severity"],
                    "category":       rule["category"],
                    "recommendation": rule["recommendation"],
                    "growth_pct":     round(growth, 1),
                })
        except Exception:
            pass

    # Sort by severity
    order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
    triggered.sort(key=lambda x: order.get(x["severity"], 9))
    return triggered


# ── Risk scoring ───────────────────────────────────────────────────────────

RISK_WEIGHTS = {
    "volume":     0.30,   # share of total complaint volume
    "growth":     0.35,   # MoM growth rate (spike severity)
    "resolution": 0.20,   # poor resolution rate raises risk
    "anomaly":    0.15,   # statistical anomaly (z-score) in recent weeks
}

RISK_RULE_SEVERITY = {
    # category -> base severity multiplier, mirrors POLICY_RULES intent so
    # categories with known systemic exposure (fraud, payments) score higher
    "Fraud / Unauthorized": 1.25,
    "Digital payments":     1.15,
    "Credit / debit card":  1.10,
}


def _normalise(series: pd.Series) -> pd.Series:
    """Min-max normalise a series to 0-100, safe against constant/empty input."""
    if series.empty:
        return series
    lo, hi = series.min(), series.max()
    if hi == lo:
        return pd.Series([50.0] * len(series), index=series.index)
    return ((series - lo) / (hi - lo) * 100).round(1)


def risk_scores(filters: dict | None = None) -> pd.DataFrame:
    """
    Composite risk score (0-100) per complaint category, blending:
      - volume share        (larger categories carry more systemic weight)
      - MoM growth           (spiking categories are higher risk)
      - resolution rate      (poorly-resolved categories are higher risk)
      - anomaly signal       (categories overlapping a recent weekly anomaly week)

    Returns DataFrame: category, volume, mom_pct_change, resolution_rate,
    risk_score, risk_tier.
    """
    df = load_all(filters)
    if df.empty:
        return pd.DataFrame(columns=[
            "category", "volume", "mom_pct_change", "resolution_rate",
            "risk_score", "risk_tier",
        ])

    vol = (
        df.groupby("category")
        .agg(volume=("complaint_id", "count"), resolution_rate=("resolved", "mean"))
        .reset_index()
    )
    vol["resolution_rate"] = (vol["resolution_rate"] * 100).round(1)

    growth = category_anomalies(filters)
    if growth.empty:
        growth = pd.DataFrame({"category": vol["category"], "mom_pct_change": 0.0, "spiked": False})

    risk = vol.merge(growth[["category", "mom_pct_change", "spiked"]], on="category", how="left")
    risk["mom_pct_change"] = risk["mom_pct_change"].fillna(0.0)
    risk["spiked"] = risk["spiked"].fillna(False)

    # Anomaly overlap: does the dataset contain a recent flagged anomaly week?
    anomaly_weeks = detect_anomalies(filters)
    has_anomaly_period = bool(anomaly_weeks["is_anomaly"].any()) if not anomaly_weeks.empty else False
    risk["anomaly_signal"] = risk["spiked"] | has_anomaly_period

    # Normalise components to comparable 0-100 scales
    vol_score    = _normalise(risk["volume"])
    growth_score = _normalise(risk["mom_pct_change"].clip(lower=0))
    res_score    = _normalise(100 - risk["resolution_rate"])  # lower resolution -> higher risk
    anom_score   = risk["anomaly_signal"].map({True: 100.0, False: 0.0})

    composite = (
        vol_score      * RISK_WEIGHTS["volume"]
        + growth_score * RISK_WEIGHTS["growth"]
        + res_score    * RISK_WEIGHTS["resolution"]
        + anom_score   * RISK_WEIGHTS["anomaly"]
    )

    multiplier = risk["category"].map(RISK_RULE_SEVERITY).fillna(1.0)
    risk["risk_score"] = (composite * multiplier).clip(upper=100).round(1)

    def tier(score: float) -> str:
        if score >= 75:
            return "CRITICAL"
        if score >= 55:
            return "HIGH"
        if score >= 35:
            return "MEDIUM"
        return "LOW"

    risk["risk_tier"] = risk["risk_score"].apply(tier)

    return (
        risk[["category", "volume", "mom_pct_change", "resolution_rate", "risk_score", "risk_tier"]]
        .sort_values("risk_score", ascending=False)
        .reset_index(drop=True)
    )


def overall_risk_index(filters: dict | None = None) -> dict:
    """
    Single headline risk figure for the dashboard: volume-weighted average
    of per-category risk scores, plus the count of categories in each tier.
    """
    risk_df = risk_scores(filters)
    if risk_df.empty:
        return {"index": 0.0, "tier": "LOW", "counts": {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}}

    weighted = (risk_df["risk_score"] * risk_df["volume"]).sum() / max(risk_df["volume"].sum(), 1)
    weighted = round(float(weighted), 1)

    if weighted >= 75:
        tier = "CRITICAL"
    elif weighted >= 55:
        tier = "HIGH"
    elif weighted >= 35:
        tier = "MEDIUM"
    else:
        tier = "LOW"

    counts = risk_df["risk_tier"].value_counts().to_dict()
    counts = {k: int(counts.get(k, 0)) for k in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]}

    return {"index": weighted, "tier": tier, "counts": counts}


# ── Narrative sample ───────────────────────────────────────────────────────

def narrative_sample(category: str, n: int = 20, filters: dict | None = None) -> list[str]:
    """Return up to n complaint narratives for a given category."""
    df = load_all(filters)
    subset = df[(df["category"] == category) & (df["has_narrative"] == 1) & df["narrative"].notna()]
    return subset["narrative"].dropna().sample(min(n, len(subset)), random_state=42).tolist()


# ── Composite Risk Score (single-dict format for app.py pages) ───────────────

def risk_score(filters: dict | None = None) -> dict:
    """
    Returns a single dict describing the system-wide composite risk score,
    decomposed into 5 weighted dimensions. Used by Risk Scoring page,
    Executive Summary, Policy Engine, and PDF Policy Brief.

    Grade thresholds: LOW <35 · MEDIUM 35-55 · HIGH 55-75 · CRITICAL ≥75
    """
    kpi_data = kpis(filters)
    df       = load_all(filters)

    total_rows = max(len(df), 1)

    # ── Dimension 1: Volume Growth (30%) ──
    mom = kpi_data.get("mom_growth", 0.0)
    vol_score = float(min(100, max(0, mom / 50 * 100))) if mom > 0 else 0.0

    # ── Dimension 2: Fraud Exposure (25%) ──
    fraud_count = int(df["category"].str.contains("Fraud", case=False, na=False).sum()) if not df.empty else 0
    fraud_pct   = fraud_count / total_rows * 100
    fraud_score = float(min(100, fraud_pct / 20 * 100))

    # ── Dimension 3: Unresolved Rate (20%) ──
    res_rate    = kpi_data.get("resolved_pct", 50.0)
    unres_score = float(max(0, 100 - res_rate))

    # ── Dimension 4: Category Spikes (15%) ──
    cat_anom  = category_anomalies(filters)
    n_spikes  = int(cat_anom["spiked"].sum()) if not cat_anom.empty else 0
    spike_score = float(min(100, n_spikes / 5 * 100))

    # ── Dimension 5: Volume Anomalies (10%) ──
    anom_df  = detect_anomalies(filters)
    n_anom   = int(anom_df["is_anomaly"].sum()) if not anom_df.empty else 0
    anom_score = float(min(100, n_anom / 10 * 100))

    total_score = round(
        vol_score   * 0.30 +
        fraud_score * 0.25 +
        unres_score * 0.20 +
        spike_score * 0.15 +
        anom_score  * 0.10,
        1,
    )

    if   total_score >= 75: grade = "CRITICAL"
    elif total_score >= 55: grade = "HIGH"
    elif total_score >= 35: grade = "MEDIUM"
    else:                   grade = "LOW"

    INTERPRETATIONS = {
        "CRITICAL": "Systemic risk is elevated. Immediate regulatory intervention is advised.",
        "HIGH":     "Multiple categories show concerning trends. Targeted oversight is recommended.",
        "MEDIUM":   "Risk is moderate. Continued monitoring with selective intervention.",
        "LOW":      "Complaint landscape is stable. Routine monitoring is sufficient.",
    }

    dimensions = [
        {"name": "Volume Growth",    "score": round(vol_score,   1), "raw": f"{mom:+.1f}%",            "weight": "30%"},
        {"name": "Fraud Exposure",   "score": round(fraud_score, 1), "raw": f"{fraud_pct:.1f}% of total","weight": "25%"},
        {"name": "Unresolved Rate",  "score": round(unres_score, 1), "raw": f"{100-res_rate:.1f}% unresolved","weight": "20%"},
        {"name": "Category Spikes",  "score": round(spike_score, 1), "raw": f"{n_spikes} categories",  "weight": "15%"},
        {"name": "Volume Anomalies", "score": round(anom_score,  1), "raw": f"{n_anom} weeks",         "weight": "10%"},
    ]

    return {
        "grade":          grade,
        "total_score":    total_score,
        "interpretation": INTERPRETATIONS[grade],
        "dimensions":     dimensions,
        "fraud_count":    fraud_count,
    }


# ── Executive Summary (aggregated dict for home page) ────────────────────────

def executive_summary(filters: dict | None = None) -> dict:
    """
    Aggregates all data needed for the Executive Summary page into one dict,
    minimising redundant DB calls.
    """
    kpi_data    = kpis(filters)
    risk        = risk_score(filters)
    recs        = policy_recommendations(filters)

    cat_df      = category_breakdown(filters)
    state_df    = state_breakdown(filters)
    bank_df     = bank_breakdown(filters)
    anom_df     = detect_anomalies(filters)

    top_category = cat_df.iloc[0]["category"]       if not cat_df.empty   else "N/A"
    top_state    = state_df.iloc[0]["state_india"]   if not state_df.empty else "N/A"
    top_bank     = bank_df.iloc[0]["bank"]           if not bank_df.empty  else "N/A"
    anomaly_weeks = int(anom_df["is_anomaly"].sum()) if not anom_df.empty  else 0

    return {
        "risk":          risk,
        "kpi":           kpi_data,
        "recs":          recs,
        "anomaly_weeks": anomaly_weeks,
        "top_category":  top_category,
        "top_state":     top_state,
        "top_bank":      top_bank,
    }


# ── Composite Risk Score (single-dict format for app.py pages) ───────────────

def risk_score(filters=None):
    kpi_data = kpis(filters)
    df       = load_all(filters)
    total_rows = max(len(df), 1)

    mom = kpi_data.get("mom_growth", 0.0)
    vol_score = float(min(100, max(0, mom / 50 * 100))) if mom > 0 else 0.0

    fraud_count = int(df["category"].str.contains("Fraud", case=False, na=False).sum()) if not df.empty else 0
    fraud_pct   = fraud_count / total_rows * 100
    fraud_score = float(min(100, fraud_pct / 20 * 100))

    res_rate    = kpi_data.get("resolved_pct", 50.0)
    unres_score = float(max(0, 100 - res_rate))

    cat_anom    = category_anomalies(filters)
    n_spikes    = int(cat_anom["spiked"].sum()) if not cat_anom.empty else 0
    spike_score = float(min(100, n_spikes / 5 * 100))

    anom_df     = detect_anomalies(filters)
    n_anom      = int(anom_df["is_anomaly"].sum()) if not anom_df.empty else 0
    anom_score  = float(min(100, n_anom / 10 * 100))

    total_score = round(
        vol_score * 0.30 + fraud_score * 0.25 +
        unres_score * 0.20 + spike_score * 0.15 + anom_score * 0.10, 1)

    if   total_score >= 75: grade = "CRITICAL"
    elif total_score >= 55: grade = "HIGH"
    elif total_score >= 35: grade = "MEDIUM"
    else:                   grade = "LOW"

    INTERP = {
        "CRITICAL": "Systemic risk is elevated. Immediate regulatory intervention is advised.",
        "HIGH":     "Multiple categories show concerning trends. Targeted oversight is recommended.",
        "MEDIUM":   "Risk is moderate. Continued monitoring with selective intervention.",
        "LOW":      "Complaint landscape is stable. Routine monitoring is sufficient.",
    }
    return {
        "grade":          grade,
        "total_score":    total_score,
        "interpretation": INTERP[grade],
        "dimensions": [
            {"name": "Volume Growth",    "score": round(vol_score,   1), "raw": f"{mom:+.1f}%",                  "weight": "30%"},
            {"name": "Fraud Exposure",   "score": round(fraud_score, 1), "raw": f"{fraud_pct:.1f}% of total",    "weight": "25%"},
            {"name": "Unresolved Rate",  "score": round(unres_score, 1), "raw": f"{100-res_rate:.1f}% unresolved","weight": "20%"},
            {"name": "Category Spikes",  "score": round(spike_score, 1), "raw": f"{n_spikes} categories",        "weight": "15%"},
            {"name": "Volume Anomalies", "score": round(anom_score,  1), "raw": f"{n_anom} weeks",               "weight": "10%"},
        ],
        "fraud_count": fraud_count,
    }


def executive_summary(filters=None):
    kpi_data     = kpis(filters)
    risk         = risk_score(filters)
    recs         = policy_recommendations(filters)
    cat_df       = category_breakdown(filters)
    state_df     = state_breakdown(filters)
    bank_df      = bank_breakdown(filters)
    anom_df      = detect_anomalies(filters)
    return {
        "risk":          risk,
        "kpi":           kpi_data,
        "recs":          recs,
        "anomaly_weeks": int(anom_df["is_anomaly"].sum()) if not anom_df.empty else 0,
        "top_category":  cat_df.iloc[0]["category"]      if not cat_df.empty   else "N/A",
        "top_state":     state_df.iloc[0]["state_india"]  if not state_df.empty else "N/A",
        "top_bank":      bank_df.iloc[0]["bank"]          if not bank_df.empty  else "N/A",
    }
