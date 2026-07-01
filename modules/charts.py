"""
Utility — Chart Builder
Plotly figure factories for CCID dashboard.
Warm-light aesthetic: cream backgrounds, charcoal text, gold/teal accents.
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

# ── Colour palette ──────────────────────────────────────────────────────────
CHARCOAL   = "#1C1F26"
GOLD       = "#C4913A"
TEAL       = "#0F7A56"
WARM_RED   = "#B42B2B"
WARM_AMBER = "#9A6200"
SLATE      = "#5A6070"
WARM_GRAY  = "#8C8880"
CREAM      = "#F6F4EF"
CARD_BG    = "#FFFFFF"
BORDER     = "#EAE7DF"

CATEGORY_COLORS = {
    "Digital payments":     "#033726",
    "Credit / debit card":  "#2A821D",
    "ATM":                  "#C4913A",
    "Loans":                "#5B4BC8",
    "Bank account":         "#2E86C1",
    "Fraud / Unauthorized": "#B42B2B",
    "Fund transfer":        "#8B6914",
    "Insurance":            "#7B3FA8",
    "Debt collection":      "#071E5D",
    "Other":                "#A8A4A0",
}

# Bright, high-contrast donut palette
SEVERITY_COLORS = {
    "CRITICAL": "#D94040",   # vivid red
    "HIGH":     "#E08C1A",   # vivid amber
    "MEDIUM":   "#2B7EC9",   # vivid blue
    "LOW":      "#1AA870",   # vivid green
}

RISK_TIER_COLORS = {
    "CRITICAL": "#D94040",
    "HIGH":     "#E08C1A",
    "MEDIUM":   "#2B7EC9",
    "LOW":      "#1AA870",
}

LAYOUT_BASE = dict(
    font_family   = "'DM Sans', system-ui, sans-serif",
    font_color    = "#F8F6F2",
    paper_bgcolor = "rgba(0,0,0,0)",
    plot_bgcolor  = "rgba(0,0,0,0)",
    margin        = dict(l=8, r=8, t=44, b=8),
    legend        = dict(
        orientation="h",
        yanchor="top", y=-0.12,
        xanchor="left", x=0,
        font_size=11,
        bgcolor="rgba(0,0,0,0)",
    ),
    xaxis=dict(
    showgrid=False,
    zeroline=False,
    color="#F8F6F2",
    tickfont=dict(
        size=11,
        color="#F8F6F2"
    )
),
    yaxis=dict(
    showgrid=True,
    gridcolor="#4A4A4A",
    zeroline=False,
    color="#F8F6F2",
    tickfont=dict(
        size=11,
        color="#F8F6F2"
    )
),
)


def _apply_base(fig: go.Figure, title: str = "") -> go.Figure:
    fig.update_layout(
        **LAYOUT_BASE,
        title=dict(
            text=title,
            x=0,
            font=dict(
                family="'DM Serif Display', serif",
                size=18,
                color="#F8F6F2"
            )
        )
    )
    return fig


# ── 1. Monthly trend ────────────────────────────────────────────────────────

def monthly_trend_chart(trend_df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=trend_df["month_label"],
        y=trend_df["count"],
        name="Complaints",
        marker_color=TEAL,
        marker_opacity=0.6,
        hovertemplate="%{x}<br>Complaints: %{y:,}<extra></extra>",
    ))

    fig.add_trace(go.Scatter(
        x=trend_df["month_label"],
        y=trend_df["rolling_avg"],
        mode="lines",
        name="3-month avg",
        line=dict(color=GOLD, width=2.5),
        hovertemplate="%{x}<br>3-mo avg: %{y:.0f}<extra></extra>",
    ))

    _apply_base(fig, "Monthly complaint volume")
    fig.update_layout(
        barmode="overlay",
        bargap=0.3,
        legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.18,
        xanchor="left",
        x=0,
        font=dict(
        size=11,
        color="#F8F6F2"
    ),
    bgcolor="rgba(0,0,0,0)"
),

    margin=dict(
        l=8,
        r=8,
        t=90,
        b=20
)
    )
    return fig


# ── 2. Category bar ─────────────────────────────────────────────────────────

def category_bar(cat_df: pd.DataFrame) -> go.Figure:
    cat_df = cat_df.sort_values("count", ascending=True).tail(10)
    colors = [CATEGORY_COLORS.get(c, WARM_GRAY) for c in cat_df["category"]]

    fig = go.Figure(go.Bar(
        x=cat_df["count"],
        y=cat_df["category"],
        orientation="h",
        marker_color=colors,
        text=cat_df["count"].apply(lambda x: f"{x:,}"),
        textposition="outside",
        hovertemplate="%{y}<br>Complaints: %{x:,}<extra></extra>",
    ))

    _apply_base(fig, "Complaints by category")
    fig.update_layout(
        xaxis=dict(showgrid=False, visible=False),
        margin=dict(l=8, r=70, t=44, b=8),
    )
    return fig


# ── 3. Bank bar ─────────────────────────────────────────────────────────────

def bank_bar(bank_df: pd.DataFrame) -> go.Figure:
    bank_df = bank_df.sort_values("total", ascending=True)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=bank_df["total"],
        y=bank_df["bank"],
        orientation="h",
        name="Total",
        marker_color=CHARCOAL,
        marker_opacity=0.75,
        hovertemplate="%{y}<br>Total: %{x:,}<extra></extra>",
    ))
    fig.add_trace(go.Bar(
        x=bank_df["resolved"],
        y=bank_df["bank"],
        orientation="h",
        name="Resolved",
        marker_color=TEAL,
        marker_opacity=0.75,
        hovertemplate="%{y}<br>Resolved: %{x:,}<extra></extra>",
    ))

    _apply_base(fig, "Complaints by bank")
    fig.update_layout(
        barmode="overlay",
        xaxis=dict(showgrid=True, gridcolor="#EEEBE4"),
        legend=dict(
            orientation="h",
            yanchor="bottom", y=1.04,
            xanchor="left", x=0,
            font_size=11,
            bgcolor="rgba(0,0,0,0)",
        ),
    )
    return fig


# ── 4. India state heatmap ──────────────────────────────────────────────────

def india_heatmap(state_df: pd.DataFrame) -> go.Figure:
    fig = go.Figure(go.Bar(
        x=state_df["count"].head(10),
        y=state_df["state_india"].head(10),
        orientation="h",
        marker=dict(
            color=state_df["count"].head(10),
            colorscale=[[0,"#EAF7F1"],[0.5,"#0F7A56"],[1,"#1C1F26"]],
            showscale=True,
            colorbar=dict(thickness=10, len=0.6, tickfont_size=10),
        ),
        hovertemplate="%{y}<br>Complaints: %{x:,}<extra></extra>",
    ))
    _apply_base(fig, "Complaints by state (top 10)")
    fig.update_layout(margin=dict(l=8, r=60, t=44, b=8))
    return fig


# ── 5. Anomaly chart ────────────────────────────────────────────────────────

def anomaly_chart(anomaly_df: pd.DataFrame) -> go.Figure:
    if anomaly_df.empty:
        fig = go.Figure()
        _apply_base(fig, "Weekly complaints — no anomalies detected")
        return fig

    normal  = anomaly_df[~anomaly_df["is_anomaly"]]
    flagged = anomaly_df[anomaly_df["is_anomaly"]]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=normal["week"], y=normal["count"],
        mode="lines+markers",
        name="Normal",
        line=dict(color=TEAL, width=2),
        marker=dict(size=5, color=TEAL),
        hovertemplate="Week %{x}<br>Complaints: %{y:,}<extra></extra>",
    ))
    if not flagged.empty:
        fig.add_trace(go.Scatter(
            x=flagged["week"], y=flagged["count"],
            mode="markers",
            name="Anomaly",
            marker=dict(size=11, color=WARM_RED, symbol="diamond",
                        line=dict(color="#FFFFFF", width=1.5)),
            hovertemplate="Week %{x}<br>⚠️ Anomaly: %{y:,}<extra></extra>",
        ))
    _apply_base(fig, "Weekly complaint volume — anomaly detection")
    fig.update_layout(
        legend=dict(
            orientation="h", yanchor="bottom", y=1.04, xanchor="left", x=0,
            font_size=11, bgcolor="rgba(0,0,0,0)",
        ),
    )
    return fig


# ── 6. Category trend area ──────────────────────────────────────────────────

def category_trend_area(cat_trend_df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    cats = cat_trend_df["category"].unique() if "category" in cat_trend_df.columns else []

    for cat in cats:
        d = cat_trend_df[cat_trend_df["category"] == cat]
        color = CATEGORY_COLORS.get(cat, WARM_GRAY)
        fig.add_trace(go.Scatter(
            x=d["month_label"], y=d["count"],
            mode="lines",
            name=cat,
            line=dict(color=color, width=2),
            stackgroup="one",
            hovertemplate=f"{cat}<br>%{{x}}<br>%{{y:,}}<extra></extra>",
        ))

    _apply_base(fig, "Monthly complaints by category")
    fig.update_layout(
        legend=dict(
            orientation="h", yanchor="top", y=-0.18,
            xanchor="left", x=0, font_size=10,
            bgcolor="rgba(0,0,0,0)",
        ),
        margin=dict(l=8, r=8, t=44, b=80),
    )
    return fig


# ── 7. Severity donut ───────────────────────────────────────────────────────

def severity_donut(recommendations: list[dict]) -> go.Figure:
    from collections import Counter
    counts = Counter(r["severity"] for r in recommendations)
    order  = ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
    labels = [s for s in order if s in counts]
    values = [counts[l] for l in labels]
    colors = [SEVERITY_COLORS[l] for l in labels]

    fig = go.Figure(go.Pie(
        labels=labels,
        values=values,
        hole=0.62,
        marker=dict(
            colors=colors,
            line=dict(color="#E99393", width=3),   # white gaps = crisp contrast
        ),
        textinfo="label+percent",
        textfont=dict(size=12, color="#770E0E"),
        insidetextorientation="radial",
        hovertemplate="%{label}: %{value} flag(s)<extra></extra>",
        pull=[0.04 if l == "CRITICAL" else 0 for l in labels],
    ))

    _apply_base(fig, "Policy flags by severity")
    fig.update_layout(
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="middle", y=0.5,
            xanchor="left", x=1.05,
            font_size=11,
            bgcolor="rgba(0,0,0,0)",
        ),
        margin=dict(l=8, r=80, t=44, b=8),
        annotations=[dict(
            text=f"<b>{len(recommendations)}</b><br><span style='font-size:10px'>flags</span>",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=18, color= 'YELLOW' , family="'DM Serif Display', serif"),
        )],
    )
    return fig


# ── 8. Risk score bar ────────────────────────────────────────────────────────

def risk_score_bar(risk_df: pd.DataFrame) -> go.Figure:
    df     = risk_df.sort_values("risk_score", ascending=True)
    colors = [RISK_TIER_COLORS.get(t, WARM_GRAY) for t in df["risk_tier"]]

    fig = go.Figure(go.Bar(
        x=df["risk_score"],
        y=df["category"],
        orientation="h",
        marker_color=colors,
        text=df["risk_score"].round(1),
        texttemplate="%{text:.0f}",
        textposition="outside",
        hovertemplate="%{y}<br>Risk score: %{x:.1f}<extra></extra>",
    ))

    _apply_base(fig, "Risk score by category (0–100)")
    fig.update_layout(
        xaxis=dict(range=[0, 110], showgrid=True, gridcolor="#EEEBE4"),
        yaxis=dict(showgrid=False),
        showlegend=False,
        height=max(260, 38 * len(df)),
    )
    return fig


# ── 9. Risk gauge ────────────────────────────────────────────────────────────

def risk_gauge(score_or_dict, grade: str | None = None) -> go.Figure:
    """
    Accepts either:
      risk_gauge(score: float, grade: str)  ← new usage
      risk_gauge(risk_index: dict)           ← backward-compat
    """
    if isinstance(score_or_dict, dict):
        value = float(score_or_dict.get("index", score_or_dict.get("total_score", 0)))
        grade = score_or_dict.get("tier",  score_or_dict.get("grade", "LOW"))
    else:
        value = float(score_or_dict)
        grade = grade or "LOW"

    color = RISK_TIER_COLORS.get(grade, TEAL)

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        number={"suffix": "", "font": {"size": 28, "color": CHARCOAL,
                                       "family": "'DM Serif Display', serif"}},
        gauge={
            "axis": {"range": [0, 100], "tickcolor": WARM_GRAY, "tickwidth": 1,
                     "tickfont": {"size": 9}},
            "bar":  {"color": color, "thickness": 0.28},
            "bgcolor": "rgba(0,0,0,0)",
            "borderwidth": 0,
            "steps": [
                {"range": [0,  35],  "color": "#EDF9F3"},
                {"range": [35, 55],  "color": "#EBF2FC"},
                {"range": [55, 75],  "color": "#FDF8EE"},
                {"range": [75, 100], "color": "#FDF0F0"},
            ],
        },
    ))
    base = {k: v for k, v in LAYOUT_BASE.items() if k not in ("xaxis","yaxis","margin","legend")}
    fig.update_layout(**base, height=200, margin=dict(l=20, r=20, t=10, b=10))
    return fig


# ── 10. Risk radar ───────────────────────────────────────────────────────────

def risk_radar(dimensions: list[dict]) -> go.Figure:
    if not dimensions:
        fig = go.Figure()
        _apply_base(fig, "Risk dimensions")
        return fig

    cats = [d["name"] for d in dimensions]
    scores = [d["score"] for d in dimensions]

    cats.append(cats[0])
    scores.append(scores[0])

    fig = go.Figure(
        go.Scatterpolar(
            r=scores,
            theta=cats,
            fill="toself",
            fillcolor="rgba(196,145,58,0.18)",
            line=dict(color=GOLD, width=3),
            marker=dict(size=6, color=GOLD),
            hovertemplate="%{theta}<br>Score: %{r:.0f}/100<extra></extra>",
        )
    )

    base = {
    k: v
    for k, v in LAYOUT_BASE.items()
    if k not in (
        "xaxis",
        "yaxis",
        "margin",
        "legend",
        "paper_bgcolor",
        "plot_bgcolor",
        "font_color",
        "font_family"
    )
}

    fig.update_layout(
        **base,

        font=dict(
            family="DM Sans",
            size=12,
            color="#F8F6F2"
        ),

        polar=dict(
            bgcolor="rgba(0,0,0,0)",

            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickfont=dict(
                    size=10,
                    color="#F8F6F2"
                ),
                tickfont_color="#F8F6F2",
                tickcolor="#F8F6F2",
                linecolor="#AD861B",
                gridcolor="#87620C"
            ),

            angularaxis=dict(
                tickfont=dict(
                    size=12,
                    color="#F8F6F2"
                ),
                linecolor="#AD861B",
                gridcolor="#87620C"
            )
        ),

        showlegend=False,
        height=240,
        margin=dict(
            l=30,
            r=30,
            t=20,
            b=20
        )
    )
    
    return fig

