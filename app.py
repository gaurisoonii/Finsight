import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

import streamlit as st

st.set_page_config(
    page_title="FinSight",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── DB bootstrap ──────────────────────────────────────────────────────────────
from modules.cleaner import DB_PATH, generate_synthetic_data, load_to_db

@st.cache_resource(show_spinner="Initialising database …")
def boot_db():
    if not DB_PATH.exists():
        load_to_db(generate_synthetic_data(50_000))
    return True
boot_db()


# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root{
    --bg:#F8FAFC;
    --surface:#FFFFFF;

    --ink:#0F172A;
    --text:#334155;
    --soft:#475569;

    --line:#E2E8F0;

    --brand:#0F766E;
    --brand-dark:#115E59;
    --brand-light:#ECFDF5;

    --accent:#2563EB;
    --gold:#C4913A;

    --danger:#DC2626;
    --warn:#D97706;
    --ok:#16A34A;

    --shadow:0 6px 18px rgba(15,23,42,.08);
}

html,body,[class*="css"]{
    font-family:'Inter',system-ui,sans-serif;
    background:var(--bg);
    color:var(--text);
}

.main .block-container{
    padding-top:26px;
    max-width:1180px;
}

h1,h2,h3,h4,h5,h6,p,span,div,label{
    color:var(--text);
}

.page-header{
    background:var(--surface);
    border:1px solid var(--line);
    border-left:5px solid var(--brand);
    border-radius:10px;
    padding:18px 22px;
    margin-bottom:22px;
    box-shadow:0 2px 8px rgba(15,23,42,.05);
}

.page-header h2{
    margin:0 0 8px 0;
    font-size:1.45rem;
    font-weight:800;
    color:var(--ink);
}

.page-header p{
    margin:0;
    font-size:.95rem;
    line-height:1.65;
    color:#1F2937;
    font-weight:500;
}

[data-testid="stSidebar"]{
    background:#FFFFFF !important;
    border-right:1px solid var(--line);
}

[data-testid="stSidebar"] *{
    color:var(--ink) !important;
}

[data-testid="stSidebar"] .stRadio label{
    border-radius:8px;
    padding:10px 12px;
    margin-bottom:4px;
    border:1px solid transparent;
    font-weight:600;
}

[data-testid="stSidebar"] .stRadio label:hover{
    background:#ECFDF5;
    border-color:#99F6E4;
}

[data-testid="metric-container"]{
    background:var(--surface);
    border:1px solid var(--line);
    border-radius:10px;
    padding:15px 18px;
    box-shadow:var(--shadow);
    transition:.25s ease;
}

[data-testid="metric-container"] label{
    color:#1F2937 !important;
    font-size:.76rem !important;
    font-weight:800 !important;
    text-transform:uppercase;
}

[data-testid="metric-container"] [data-testid="stMetricValue"]{
    color:var(--ink) !important;
    font-size:1.65rem !important;
    font-weight:800 !important;
}

.exec-card,.rec-card,.ai-box{
    background:#FFFFFF;
    border:1px solid var(--line);
    border-radius:10px;
    padding:16px 18px;
    margin-bottom:12px;
    box-shadow:0 1px 6px rgba(15,23,42,.06);
}

.exec-card .label{
    color:#1F2937;
    font-size:.75rem;
    font-weight:800;
    text-transform:uppercase;
}

.exec-card .value{
    color:var(--ink);
    font-size:1.05rem;
    font-weight:700;
}

.ai-box{
    border-left:5px solid var(--accent);
    color:#1F2937;
    line-height:1.7;
    font-weight:500;
}

.rec-card h4{
    color:var(--ink);
    margin:10px 0 6px;
    font-size:1rem;
}

.rec-card p{
    color:#1F2937;
    line-height:1.65;
    font-weight:500;
}

.risk-card{
    border-radius:10px;
    padding:20px 22px;
    margin-bottom:18px;
    border:1px solid var(--line);
    background:#FFFFFF;
}

.risk-CRITICAL{border-left:5px solid var(--danger);background:#FFF7F7;}
.risk-HIGH{border-left:5px solid var(--warn);background:#FFFBEB;}
.risk-MEDIUM{border-left:5px solid var(--accent);background:#EFF6FF;}
.risk-LOW{border-left:5px solid var(--ok);background:#ECFDF5;}

.sev-CRITICAL,.sev-HIGH,.sev-MEDIUM,.sev-LOW{
    padding:4px 10px;
    border-radius:999px;
    font-size:.74rem;
    font-weight:800;
}

.sev-CRITICAL{background:#FEE2E2;color:#991B1B;}
.sev-HIGH{background:#FEF3C7;color:#92400E;}
.sev-MEDIUM{background:#DBEAFE;color:#1D4ED8;}
.sev-LOW{background:#D1FAE5;color:#065F46;}

.stTabs [data-baseweb="tab"]{
    color:#1F2937;
    font-weight:700;
}

.stTabs [data-baseweb="tab"][aria-selected="true"]{
    color:var(--brand-dark);
    border-bottom:3px solid var(--brand);
}

.stButton>button,
.stDownloadButton button{
    border-radius:8px !important;
    font-weight:700 !important;
}

.stButton>button[kind="primary"],
.stDownloadButton button{
    background:var(--brand) !important;
    color:#FFFFFF !important;
    border:none !important;
}

.stButton>button[kind="primary"]:hover,
.stDownloadButton button:hover{
    background:var(--brand-dark) !important;
}

.stButton>button:not([kind="primary"]){
    background:#FFFFFF !important;
    border:1px solid var(--line) !important;
    color:var(--ink) !important;
}

.dim-bar-label{
    color:#1F2937;
    font-weight:700;
    display:flex;
    justify-content:space-between;
    margin-bottom:6px;
}

.dim-bar-track{
    background:#E5EAF1;
    height:10px;
    border-radius:999px;
}

.dim-bar-fill{
    height:10px;
    border-radius:999px;
}

[data-testid="stDataFrame"]{
    border:1px solid var(--line);
    border-radius:10px;
    overflow:hidden;
}

#MainMenu,footer,header{
    visibility:hidden;
}

.exec-card:hover,
.rec-card:hover,
.ai-box:hover,
[data-testid="metric-container"]:hover{
    transform:translateY(-2px);
    box-shadow:0 10px 24px rgba(15,23,42,.12);
}

</style>
""", unsafe_allow_html=True)

from modules import analytics, charts, ai_engine
from modules.report_generator import generate_pdf, generate_policy_brief
import pandas as pd
from datetime import datetime

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding-bottom:18px;">
        <div style="font-size:1.55rem;
                    font-weight:700;
                    color:#C4913A;">
            🏛 FinSight (Financial Complaint Intelligence Platform)
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div style='font-size:0.68rem;font-weight:700;color:#C4913A;"
                "letter-spacing:0.12em;text-transform:uppercase;margin-bottom:6px;'>"
                "Navigation</div>", unsafe_allow_html=True)

    page = st.radio(
    "",
    [
        "🏠 Executive Summary",
        "📊 Complaint Overview",
        "📈 Complaint Analytics",
        "🎯 Risk Assessment",
        "🤖 AI Complaint Intelligence",
        "⚖ Policy Recommendations",
        "📄 Reports"
    ],
    label_visibility="collapsed"
)

    st.markdown("---")
    st.markdown("<div style='font-size:0.7rem;font-weight:700;color:#C4913A;"
                "letter-spacing:0.1em;text-transform:uppercase;margin-bottom:8px;'>"
                "Filters</div>", unsafe_allow_html=True)

    @st.cache_data(ttl=300)
    def get_filter_options():
        df = analytics.load_all()
        return {
            "categories": sorted(df["category"].dropna().unique().tolist()),
            "banks":      sorted(df["bank"].dropna().unique().tolist()),
            "states":     sorted(df["state_india"].dropna().unique().tolist()),
            "min_date":   df["date_received"].min().date(),
            "max_date":   df["date_received"].max().date(),
        }

    opts           = get_filter_options()
    date_range     = st.date_input("Date range",
                        value=(opts["min_date"], opts["max_date"]),
                        min_value=opts["min_date"], max_value=opts["max_date"])
    sel_categories = st.multiselect("Category", opts["categories"], placeholder="All categories")
    sel_banks      = st.multiselect("Bank",     opts["banks"],      placeholder="All banks")
    sel_states     = st.multiselect("State",    opts["states"],     placeholder="All states")

    st.markdown("---")
    st.markdown("""
    <div style="font-size:0.72rem;color:#334155;line-height:2;">
        <b style="color:#C4913A;">Data</b> · CFPB remapped to India<br>
        <b style="color:#C4913A;">AI</b>   · GPT-4o mini / fallback<br>
        <b style="color:#C4913A;">Stack</b> · Python · Pandas · Plotly
    </div>""", unsafe_allow_html=True)

filters = {}
if sel_categories:             filters["category"]   = sel_categories
if sel_banks:                  filters["bank"]       = sel_banks
if sel_states:                 filters["state"]      = sel_states
if isinstance(date_range,(list,tuple)) and len(date_range)==2:
    filters["date_range"] = date_range


# ── Helpers ───────────────────────────────────────────────────────────────────
SEV_ICON = {"CRITICAL":"🔴","HIGH":"🟠","MEDIUM":"🟡","LOW":"🟢"}
GRADE_COLOR = {
    "CRITICAL":"#A32D2D","HIGH":"#854F0B","MEDIUM":"#185FA5","LOW":"#0F6E56"
}

def _dim_bar(name, score, raw, color="#0F6E56"):
    pct = int(score)
    return f"""
    <div class="dim-bar-wrap">
        <div class="dim-bar-label">
            <span>{name}</span>
            <span style="color:{color};font-weight:600;">{score:.0f}/100 · {raw}</span>
        </div>
        <div class="dim-bar-track">
            <div class="dim-bar-fill" style="width:{pct}%;background:{color};"></div>
        </div>
    </div>"""


# ══════════════════════════════════════════════════════════════════════════════
#  PAGE 0 — EXECUTIVE SUMMARY
# ══════════════════════════════════════════════════════════════════════════════
def page_executive_summary():
    st.markdown("""
    <div class="page-header">
        <h2>──────────────────────────────

        Executive Dashboard

        Financial Complaint Intelligence

        Reporting Period

        July 2026

──────────────────────────────</h2>
        <p>
            This page provides a consolidated view of the current complaint landscape,
            highlighting key performance indicators, overall risk exposure, and the
            most critical issues requiring immediate regulatory attention.
        </p>
    </div>
    """, unsafe_allow_html=True)

    with st.spinner("Compiling executive summary …"):
        summary = analytics.executive_summary(filters)

    risk  = summary["risk"]
    kpi   = summary["kpi"]
    recs  = summary["recs"]
    grade = risk["grade"]
    score = risk["total_score"]
    gc    = GRADE_COLOR.get(grade, "#1A2B4A")

    st.markdown(f"""
    <div class="risk-card risk-{grade}">
        <div style="display:flex;align-items:center;gap:20px;">
            <div style="text-align:center;min-width:90px;">
                <div style="font-size:3rem;font-weight:700;color:{gc};line-height:1;">{score:.0f}</div>
                <div style="font-size:0.72rem;color:{gc};font-weight:600;letter-spacing:0.05em;">/100 RISK SCORE</div>
            </div>
            <div style="border-left:2px solid {gc}33;padding-left:20px;flex:1;">
                <div style="font-size:1.1rem;font-weight:700;color:{gc};margin-bottom:4px;">
                    {SEV_ICON.get(grade,'')} {grade} RISK — {datetime.now().strftime('%B %Y')}
                </div>
                <div style="font-size:0.88rem;color:#1F2937;line-height:1.6;">
                    {risk['interpretation']}
                </div>
            </div>
            <div style="text-align:right;min-width:100px;">
                <div style="font-size:0.72rem;color:#334155;font-weight:600;text-transform:uppercase;">Active flags</div>
                <div style="font-size:2rem;font-weight:700;color:{gc};">{len(recs)}</div>
            </div>
        </div>
    </div>""", unsafe_allow_html=True)

    c1,c2,c3,c4,c5 = st.columns(5)
    c1.metric("Total complaints",  f"{kpi['total']:,}")
    c2.metric("Resolution rate",   f"{kpi['resolved_pct']:.1f}%")
    c3.metric("MoM growth",        f"{kpi['mom_growth']:+.1f}%",
              delta_color="inverse" if kpi['mom_growth']>0 else "normal")
    c4.metric("Anomalous weeks",   str(summary["anomaly_weeks"]))
    c5.metric("Daily average",     f"{kpi['avg_daily']:.0f}")

    st.markdown("<br>", unsafe_allow_html=True)
    col_l, col_r = st.columns([1.1, 1])

    with col_l:
        st.markdown("**Top signals**")
        signals = [
            ("Highest complaint category", summary["top_category"], "📦"),
            ("Most complaints from",       summary["top_state"],    "📍"),
            ("Highest volume bank",        summary["top_bank"],     "🏦"),
            ("Anomalous weeks detected",   str(summary["anomaly_weeks"]), "⚠️"),
            ("Policy flags triggered",     str(len(recs)),          "⚖️"),
            ("Fraud cases detected",       str(risk["fraud_count"]) + " complaints", "🔒"),
        ]
        for label, value, icon in signals:
            st.markdown(f"""
            <div class="exec-card">
                <div class="label">{icon} {label}</div>
                <div class="value">{value}</div>
            </div>""", unsafe_allow_html=True)

    with col_r:
        st.markdown("**Risk dimensions**")
        for d in risk["dimensions"]:
            s = d["score"]
            if   s >= 75: dc = "#A32D2D"
            elif s >= 55: dc = "#BA7517"
            elif s >= 35: dc = "#185FA5"
            else:         dc = "#0F6E56"
            st.markdown(_dim_bar(d["name"], s, d["raw"], dc), unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.plotly_chart(charts.risk_radar(risk["dimensions"]),
                        use_container_width=True, config={"displayModeBar":False})

    if recs:
        st.markdown("---")
        st.markdown("**Priority action items**")
        for rec in recs[:3]:
            st.markdown(f"""
            <div class="rec-card">
                <span class="sev-{rec['severity']}">{rec['severity']}</span>
                <h4>{SEV_ICON.get(rec['severity'],'')} {rec['category']}
                    <span style="font-size:0.8rem;color:#A32D2D;font-weight:500;">
                    &nbsp;{rec['growth_pct']:+.1f}% MoM</span>
                </h4>
                <p>{rec['recommendation']}</p>
            </div>""", unsafe_allow_html=True)

    st.markdown("---")
    trend_df  = analytics.monthly_trend(filters)
    narrative = ai_engine.trend_narrative(trend_df, kpi)
    if narrative:
        st.markdown(f'<div class="ai-box">🤖 {narrative}</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  PAGE 1 — OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════
def page_overview():
    st.markdown("""
    <div class="page-header">
        <h2>📊 Complaint Overview</h2>
        <p>
            Explore complaint volumes across time, geography, and product categories.
            This page helps identify overall trends, regional hotspots, and customer
            service patterns within the financial ecosystem.
        </p>
    </div>
    """, unsafe_allow_html=True)

    with st.spinner("Loading …"):
        kpi_data = analytics.kpis(filters)

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Total complaints", f"{kpi_data['total']:,}")
    c2.metric("Resolution rate",  f"{kpi_data['resolved_pct']:.1f}%")
    c3.metric("Month-on-month",   f"{kpi_data['mom_growth']:+.1f}%",
              delta_color="inverse" if kpi_data['mom_growth']>0 else "normal")
    c4.metric("Daily average",    f"{kpi_data['avg_daily']:.0f}")

    st.markdown("<br>", unsafe_allow_html=True)
    trend_df  = analytics.monthly_trend(filters)
    narrative = ai_engine.trend_narrative(trend_df, kpi_data)
    if narrative:
        st.markdown(f'<div class="ai-box">🤖 {narrative}</div>', unsafe_allow_html=True)

    st.plotly_chart(charts.monthly_trend_chart(trend_df),
                    use_container_width=True, config={"displayModeBar":False})

    col_l,col_r = st.columns([1.4,1])
    with col_l:
        state_df = analytics.state_breakdown(filters)
        st.plotly_chart(charts.india_heatmap(state_df),
                        use_container_width=True, config={"displayModeBar":False})
    with col_r:
        cat_df = analytics.category_breakdown(filters)
        st.plotly_chart(charts.category_bar(cat_df),
                        use_container_width=True, config={"displayModeBar":False})

    st.markdown("---")
    st.markdown("**Top 5 states**")
    d = state_df.head(5).rename(
    columns={
        "state_india": "State",
        "count": "Complaints"
    }
)

# Convert numbers to text so Streamlit left-aligns them
    d["Complaints"] = d["Complaints"].map(lambda x: f"{x:,}")

    st.dataframe(
        d,
        use_container_width=True,
        hide_index=True
    )

# ══════════════════════════════════════════════════════════════════════════════
#  PAGE 2 — ANALYTICS
# ══════════════════════════════════════════════════════════════════════════════
def page_analytics():
    st.markdown("""
    <div class="page-header">
        <h2>📈 Complaint Analytics</h2>
        <p>
            Perform detailed analysis of complaint behaviour across banks and
            complaint categories. Statistical methods are used to detect unusual
            growth patterns and emerging operational concerns.
        </p>
    </div>
    """, unsafe_allow_html=True)

    tab1,tab2,tab3 = st.tabs(["Category trends","Bank analysis","Anomaly detection"])

    with tab1:
        cat_trend = analytics.category_trend(filters)
        if cat_trend.empty:
            st.info("No data for selected filters.")
        else:
            st.plotly_chart(charts.category_trend_area(cat_trend),
                            use_container_width=True, config={"displayModeBar":False})
            cat_anom = analytics.category_anomalies(filters)
            if not cat_anom.empty:
                st.markdown("**Month-over-month change**")
                d = cat_anom.copy()
                d["mom_pct_change"] = d["mom_pct_change"].apply(lambda x: f"{x:+.1f}%")
                d["spiked"]         = d["spiked"].apply(lambda x: "⚠️ Spike" if x else "✓ Normal")
                d.columns = ["Category","MoM Change","Status"]
                st.dataframe(d, use_container_width=True, hide_index=True)

    with tab2:
        bank_df = analytics.bank_breakdown(filters)
        st.plotly_chart(charts.bank_bar(bank_df),
                        use_container_width=True, config={"displayModeBar":False})
        d = bank_df.copy()
        d["resolution_rate"] = d["resolution_rate"].apply(lambda x: f"{x:.1f}%")
        d.columns = ["Bank","Total","Resolved","Resolution rate"]
        st.dataframe(d, use_container_width=True, hide_index=True)

    with tab3:
        st.markdown("""<p style="font-size:0.85rem;color:#334155;">
            Anomalies flagged when weekly volume deviates &gt;2σ from 4-week rolling mean.</p>""",
            unsafe_allow_html=True)
        anomaly_df = analytics.detect_anomalies(filters)
        st.plotly_chart(charts.anomaly_chart(anomaly_df),
                        use_container_width=True, config={"displayModeBar":False})
        if anomaly_df["is_anomaly"].any():
            flagged = anomaly_df[anomaly_df["is_anomaly"]][["week","count","z_score"]]
            flagged.columns = ["Week","Complaints","Z-score"]
            st.markdown("**⚠️ Flagged weeks**")
            st.dataframe(flagged, use_container_width=True, hide_index=True)
        else:
            st.success("No anomalies detected.")


# ══════════════════════════════════════════════════════════════════════════════
#  PAGE 3 — RISK SCORING
# ══════════════════════════════════════════════════════════════════════════════
def page_risk():
    st.markdown("""
    <div class="page-header">
        <h2>🎯 Risk Assessment</h2>
        <p>
            The composite risk score combines complaint growth, fraud exposure,
            unresolved cases, category spikes, and anomaly detection to estimate
            the overall regulatory risk level.
        </p>
    </div>
    """, unsafe_allow_html=True)

    with st.spinner("Computing risk score …"):
        risk = analytics.risk_score(filters)

    grade = risk["grade"]
    score = risk["total_score"]
    gc    = GRADE_COLOR.get(grade, "#1A2B4A")

    col_g, col_c, col_d = st.columns([1, 1, 1.2])

    with col_g:
        st.plotly_chart(charts.risk_gauge(score, grade),
                        use_container_width=True, config={"displayModeBar":False})

    with col_c:
        st.markdown(f"""
        <div class="risk-card risk-{grade}" style="height:220px;display:flex;
             flex-direction:column;justify-content:center;">
            <div style="font-size:0.72rem;font-weight:700;color:{gc};
                 letter-spacing:0.1em;text-transform:uppercase;margin-bottom:8px;">Risk grade</div>
            <div style="font-size:2.8rem;font-weight:700;color:{gc};line-height:1;">
                {SEV_ICON.get(grade,'')} {grade}
            </div>
            <div style="font-size:0.88rem;color:#1F2937;margin-top:10px;line-height:1.6;">
                {risk['interpretation']}
            </div>
        </div>""", unsafe_allow_html=True)

    with col_d:
        st.plotly_chart(charts.risk_radar(risk["dimensions"]),
                        use_container_width=True, config={"displayModeBar":False})

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("**Dimension breakdown**")
    st.markdown("""<p style="font-size:0.83rem;color:#334155;margin-bottom:14px;">
    Each dimension is scored 0–100 and weighted to produce the composite score.
    Higher = higher risk.</p>""", unsafe_allow_html=True)

    for d in risk["dimensions"]:
        s = d["score"]
        if   s>=75: dc="#A32D2D"
        elif s>=55: dc="#BA7517"
        elif s>=35: dc="#185FA5"
        else:       dc="#0F6E56"
        col_a, col_b = st.columns([3,1])
        with col_a:
            st.markdown(_dim_bar(d["name"], s, d["raw"], dc), unsafe_allow_html=True)
        with col_b:
            st.markdown(f"""
            <div style="text-align:right;padding-top:4px;">
                <span style="font-size:0.75rem;color:#334155;">Weight: <b>{d['weight']}</b></span>
            </div>""", unsafe_allow_html=True)

    st.markdown("---")
    with st.expander("📐 Scoring methodology"):
        st.markdown("""
| Dimension | Weight | How it's computed |
|-----------|--------|-------------------|
| Volume growth | 30% | MoM overall complaint growth — 0% = score 0, ≥50% = score 100 |
| Fraud exposure | 25% | Fraud complaints as % of total — 0% = 0, ≥20% = 100 |
| Unresolved rate | 20% | 100 minus resolution rate |
| Category spikes | 15% | Number of spiked categories — 0 spikes = 0, ≥5 = 100 |
| Volume anomalies | 10% | Anomalous weeks via z-score — 0 = 0, ≥10 = 100 |

**Grade thresholds:** LOW (<35) · MEDIUM (35–55) · HIGH (55–75) · CRITICAL (≥75)
        """)


# ══════════════════════════════════════════════════════════════════════════════
#  PAGE 4 — AI INSIGHTS
# ══════════════════════════════════════════════════════════════════════════════
def page_ai_insights():
    st.markdown("""
    <div class="page-header">
        <h2>🤖 AI Complaint Intelligence</h2>
        <p>
            AI analyses customer complaint narratives to identify recurring issues,
            emerging risks, operational bottlenecks, and customer pain points that
            may require supervisory or policy intervention.
        </p>
    </div>
    """, unsafe_allow_html=True)

    cat_df = analytics.category_breakdown(filters)
    if cat_df.empty:
        st.warning("No complaint data for selected filters.")
        return

    col_sel,col_info = st.columns([1,2])
    with col_sel:
        selected_cat = st.selectbox("Complaint category", cat_df["category"].tolist())
        n_complaints = int(cat_df[cat_df["category"]==selected_cat]["count"].iloc[0])
        st.caption(f"{n_complaints:,} complaints in this category")

    with col_info:
        st.markdown(f"""
        <div style="background:#F0FAF6;border-radius:8px;padding:14px 18px;margin-top:4px;">
            <div style="font-size:0.75rem;color:#334155;text-transform:uppercase;
                 font-weight:600;letter-spacing:0.05em;">Selected</div>
            <div style="font-size:1.35rem;font-weight:600;color:#1A2B4A;margin-top:4px;">
                {selected_cat}</div>
            <div style="font-size:0.83rem;color:#0F6E56;margin-top:2px;">
                Narratives will be analysed by GPT-4o</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Generate Executive AI Insight", type="primary"):
        with st.spinner("Generating analysis …"):
            narratives = analytics.narrative_sample(selected_cat, n=20, filters=filters)
            summary    = ai_engine.summarise_complaints(narratives, selected_cat)
        st.markdown(f'<div class="ai-box">🤖 {summary}</div>', unsafe_allow_html=True)
        with st.expander(f"Raw narrative samples ({min(5,len(narratives))})"):
            for i,text in enumerate(narratives[:5],1):
                st.markdown(f"""
                <div style="background:#FAFAFA;border:0.5px solid #CBD5E1;border-radius:8px;
                    padding:12px 16px;margin-bottom:10px;font-size:0.86rem;
                    color:#1F2937;line-height:1.65;">
                    <span style="font-size:0.74rem;font-weight:600;color:#334155;">#{i}</span><br>
                    {str(text)[:600]}{'…' if len(str(text))>600 else ''}
                </div>""", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="text-align:center;padding:48px 20px;color:#475569;font-size:0.9rem;
             border:1px dashed #CBD5E1;border-radius:10px;margin-top:8px;">
            Select a category and click <strong>Generate AI Analysis</strong>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.plotly_chart(charts.category_bar(cat_df),
                    use_container_width=True, config={"displayModeBar":False})


# ══════════════════════════════════════════════════════════════════════════════
#  PAGE 5 — POLICY ENGINE
# ══════════════════════════════════════════════════════════════════════════════
def page_policy():
    st.markdown("""
    <div class="page-header">
        <h2>⚖ Policy Recommendation Engine</h2>
        <p>
            Rule-based analytics and AI-generated insights work together to prioritise
            complaint categories based on severity and recommend potential regulatory
            or operational actions.
        </p>
    </div>
    """, unsafe_allow_html=True)

    with st.spinner("Running policy engine …"):
        recs = analytics.policy_recommendations(filters)
        risk = analytics.risk_score(filters)

    critical = sum(1 for r in recs if r["severity"]=="CRITICAL")
    high     = sum(1 for r in recs if r["severity"]=="HIGH")
    medium   = sum(1 for r in recs if r["severity"]=="MEDIUM")

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("🔴 Critical",    critical)
    c2.metric("🟠 High",        high)
    c3.metric("🟡 Medium",      medium)
    c4.metric("🎯 Risk score",  f"{risk['total_score']:.0f}/100")

    st.markdown("<br>", unsafe_allow_html=True)

    if not recs:
        st.success("✅ No significant spikes. All categories within normal range.")
        st.markdown("---")
        _show_all_category_growth()
        return

    with st.spinner("Generating policy insight …"):
        insight = ai_engine.generate_policy_insight(recs)

    st.markdown(f'<div class="ai-box">🤖 {insight}</div>', unsafe_allow_html=True)

    col_chart,col_recs = st.columns([1,2])
    with col_chart:
        st.plotly_chart(charts.severity_donut(recs),
                        use_container_width=True, config={"displayModeBar":False})
    with col_recs:
        for rec in recs:
            st.markdown(f"""
            <div class="rec-card">
                <span class="sev-{rec['severity']}">{rec['severity']}</span>
                <h4>{SEV_ICON.get(rec['severity'],'')} {rec['category']}
                    <span style="font-size:0.8rem;color:#A32D2D;font-weight:500;">
                    &nbsp;{rec['growth_pct']:+.1f}% MoM</span>
                </h4>
                <p>{rec['recommendation']}</p>
            </div>""", unsafe_allow_html=True)

    st.markdown("---")
    _show_all_category_growth()


def _show_all_category_growth():
    cat_anom = analytics.category_anomalies(filters)
    if not cat_anom.empty:
        st.markdown("**All category growth rates**")
        d = cat_anom.copy()
        d["mom_pct_change"] = d["mom_pct_change"].apply(lambda x: f"{x:+.1f}%")
        d["spiked"]         = d["spiked"].apply(lambda x: "⚠️ Spike" if x else "—")
        d.columns = ["Category","MoM Growth","Alert"]
        st.dataframe(d, use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════════════════════════════
#  PAGE 6 — REPORTS
# ══════════════════════════════════════════════════════════════════════════════
def page_reports():
    st.markdown("""
    <div class="page-header">
        <h2>📄 Reports</h2>
        <p>
            Generate RBI-style reports and policy briefs summarising complaint
            analytics, risk assessment, AI observations, and recommended actions
            for internal review and decision-making.
        </p>
    </div>
    """, unsafe_allow_html=True)

    tab_full, tab_brief = st.tabs(["📋  Full Monthly Report", "📝  Policy Brief"])

    with tab_full:
        col_l,col_r = st.columns([1,2])
        with col_l:
            st.markdown("**Configuration**")
            report_month   = st.text_input("Reporting period",
                                value=datetime.now().strftime("%B %Y"), key="full_month")
            include_ai     = st.checkbox("Include AI narrative",   value=True, key="full_ai")
            include_policy = st.checkbox("Include policy section", value=True, key="full_pol")
        with col_r:
            st.markdown("""
            <div style="background:#F8FAFC;border:0.5px solid #CBD5E1;
                 border-radius:10px;padding:18px 22px;">
                <div style="font-size:0.85rem;font-weight:600;color:#1A2B4A;margin-bottom:10px;">
                    Full report includes</div>
                <ul style="font-size:0.85rem;color:#1F2937;line-height:2.1;
                    padding-left:18px;margin:0;">
                    <li>Executive summary KPI table</li>
                    <li>Category breakdown (top 10)</li>
                    <li>Institution analysis (top 10)</li>
                    <li>AI trend narrative</li>
                    <li>Policy recommendations</li>
                    <li>RBI confidentiality footer</li>
                </ul>
            </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("⬇️  Generate Monthly Intelligence Report", type="primary", key="gen_full"):
            with st.spinner("Compiling …"):
                kpi_data = analytics.kpis(filters)
                cat_df   = analytics.category_breakdown(filters)
                bank_df  = analytics.bank_breakdown(filters)
                trend_df = analytics.monthly_trend(filters)
                recs     = analytics.policy_recommendations(filters) if include_policy else []
                insight  = ai_engine.generate_policy_insight(recs)  if include_policy else ""
                ai_sum   = ai_engine.trend_narrative(trend_df, kpi_data) if include_ai else ""
                pdf = generate_pdf(kpis=kpi_data, cat_df=cat_df, bank_df=bank_df,
                                   recommendations=recs, policy_insight=insight,
                                   ai_summary=ai_sum, report_month=report_month)
            if pdf and not pdf.startswith(b"["):
                st.success("✅ Full report ready!")
                st.download_button("📥 Download PDF", data=pdf,
                    file_name=f"CCID_Report_{report_month.replace(' ','_')}.pdf",
                    mime="application/pdf")
            else:
                st.error(pdf.decode() if pdf else "Failed.")

    with tab_brief:
        col_l,col_r = st.columns([1,2])
        with col_l:
            st.markdown("**Configuration**")
            brief_month = st.text_input("Reporting period",
                             value=datetime.now().strftime("%B %Y"), key="brief_month")
        with col_r:
            st.markdown("""
            <div style="background:#F0FAF6;border:0.5px solid #9FE1CB;
                 border-radius:10px;padding:18px 22px;">
                <div style="font-size:0.85rem;font-weight:600;color:#1A2B4A;margin-bottom:10px;">
                    Policy Brief includes (2 pages)</div>
                <ul style="font-size:0.85rem;color:#1F2937;line-height:2.1;
                    padding-left:18px;margin:0;">
                    <li>Composite risk score (0–100) with grade</li>
                    <li>5-dimension risk breakdown table</li>
                    <li>Key KPI summary strip</li>
                    <li>AI regulatory intelligence assessment</li>
                    <li>Numbered action items by severity</li>
                    <li>Sign-off block for circulation</li>
                </ul>
            </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("⬇️  Generate Policy Brief", type="primary", key="gen_brief"):
            with st.spinner("Compiling policy brief …"):
                risk    = analytics.risk_score(filters)
                kpi_d   = analytics.kpis(filters)
                recs    = analytics.policy_recommendations(filters)
                insight = ai_engine.generate_policy_insight(recs)
                pdf = generate_policy_brief(risk=risk, recommendations=recs,
                                            policy_insight=insight, kpis=kpi_d,
                                            report_month=brief_month)
            if pdf and not pdf.startswith(b"["):
                st.success("✅ Policy brief ready!")
                st.download_button("📥 Download Policy Brief", data=pdf,
                    file_name=f"CCID_PolicyBrief_{brief_month.replace(' ','_')}.pdf",
                    mime="application/pdf")
            else:
                st.error(pdf.decode() if pdf else "Failed.")

        st.markdown("---")
        st.markdown("**Live preview**")
        with st.expander("Risk score preview"):
            risk = analytics.risk_score(filters)
            c1,c2 = st.columns(2)
            c1.metric("Risk score", f"{risk['total_score']:.0f}/100")
            c2.metric("Grade",      risk["grade"])
            for d in risk["dimensions"]:
                st.markdown(_dim_bar(d["name"], d["score"], d["raw"]), unsafe_allow_html=True)
        with st.expander("Active flags preview"):
            recs = analytics.policy_recommendations(filters)
            if recs:
                for r in recs:
                    st.markdown(f"**{r['severity']}** — {r['category']} "
                                f"({r['growth_pct']:+.1f}%): {r['recommendation']}")
            else:
                st.write("No active flags.")


# ══════════════════════════════════════════════════════════════════════════════
#  ROUTER
# ══════════════════════════════════════════════════════════════════════════════
import traceback

try:
    if "Executive" in page:
        page_executive_summary()
    elif "Overview" in page:
        page_overview()
    elif "Analytics" in page:
        page_analytics()
    elif "Risk" in page:
        page_risk()
    elif "AI" in page:
        page_ai_insights()
    elif "Policy" in page:
        page_policy()
    elif "Report" in page:
        page_reports()
except Exception as e:
    st.exception(e)
    st.code(traceback.format_exc())
    
def page_header(title, description):
    st.markdown(f"""
    <div class="page-header">
        <h2>{title}</h2>
        <p>{description}</p>
    </div>
    """, unsafe_allow_html=True)
    
print ("FinSight v1.0 \n Developed for Financial Complaint Analytics \n© 2026 Gauri Soni")