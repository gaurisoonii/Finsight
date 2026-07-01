"""
Module 4 — PDF Report Generator
Generates a professional monthly complaint intelligence report using ReportLab.
"""

import io
from datetime import datetime
from typing import Optional

import pandas as pd

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.lib.colors import HexColor, white, black
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
        HRFlowable, PageBreak,
    )
    from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


# ── Colour palette ──────────────────────────────────────────────────────────
NAVY   = HexColor("#1A2B4A") if REPORTLAB_AVAILABLE else None
TEAL   = HexColor("#0F6E56") if REPORTLAB_AVAILABLE else None
AMBER  = HexColor("#BA7517") if REPORTLAB_AVAILABLE else None
RED    = HexColor("#A32D2D") if REPORTLAB_AVAILABLE else None
LIGHT  = HexColor("#F1EFE8") if REPORTLAB_AVAILABLE else None
MUTED  = HexColor("#5F5E5A") if REPORTLAB_AVAILABLE else None


def _styles():
    ss = getSampleStyleSheet()

    def add(name, **kw):
        ss.add(ParagraphStyle(name=name, **kw))

    add("RBITitle",    fontName="Helvetica-Bold",   fontSize=20, textColor=NAVY,   spaceAfter=4,   spaceBefore=0,  alignment=TA_LEFT, leading=26)
    add("RBISubtitle", fontName="Helvetica",         fontSize=11, textColor=MUTED,  spaceAfter=10,  spaceBefore=0,  alignment=TA_LEFT)
    add("RBIH1",       fontName="Helvetica-Bold",   fontSize=13, textColor=NAVY,   spaceBefore=14, spaceAfter=6)
    add("RBIH2",       fontName="Helvetica-Bold",   fontSize=10, textColor=TEAL,   spaceBefore=8,  spaceAfter=4)
    add("RBIBody",     fontName="Helvetica",         fontSize=9,  textColor=black,  spaceAfter=6,   leading=14, alignment=TA_JUSTIFY)
    add("RBICaption",  fontName="Helvetica-Oblique", fontSize=8,  textColor=MUTED,  spaceAfter=8)
    add("RBIKpiLabel", fontName="Helvetica",         fontSize=8,  textColor=MUTED,  spaceAfter=2,   leading=10)
    add("RBIKpiValue", fontName="Helvetica-Bold",    fontSize=17, textColor=NAVY,   spaceAfter=0,   leading=22)
    add("RBIFooter",   fontName="Helvetica",         fontSize=7,  textColor=MUTED,  alignment=TA_CENTER, leading=11)
    add("SevCRITICAL", fontName="Helvetica-Bold",   fontSize=9,  textColor=HexColor("#B42B2B"), spaceBefore=6)
    add("SevHIGH",     fontName="Helvetica-Bold",   fontSize=9,  textColor=HexColor("#9A6200"), spaceBefore=6)
    add("SevMEDIUM",   fontName="Helvetica-Bold",   fontSize=9,  textColor=HexColor("#1A5FAD"), spaceBefore=6)
    add("SevLOW",      fontName="Helvetica-Bold",   fontSize=9,  textColor=HexColor("#0F7A56"), spaceBefore=6)
    return ss


def _kpi_table(kpis: dict, styles):
    data = [
        [
            Paragraph("Total complaints",  styles["RBIKpiLabel"]),
            Paragraph("Resolution rate",   styles["RBIKpiLabel"]),
            Paragraph("MoM growth",        styles["RBIKpiLabel"]),
            Paragraph("Daily avg",         styles["RBIKpiLabel"]),
        ],
        [
            Paragraph(f"{kpis.get('total', 0):,}",           styles["RBIKpiValue"]),
            Paragraph(f"{kpis.get('resolved_pct', 0):.1f}%", styles["RBIKpiValue"]),
            Paragraph(f"{kpis.get('mom_growth', 0):+.1f}%",  styles["RBIKpiValue"]),
            Paragraph(f"{kpis.get('avg_daily', 0):.0f}",     styles["RBIKpiValue"]),
        ],
    ]
    # 4 equal columns fitting within A4 body (17cm usable width)
    t = Table(data, colWidths=[4.25*cm, 4.25*cm, 4.25*cm, 4.25*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND",   (0,0), (-1,-1), LIGHT),
        ("BOX",          (0,0), (-1,-1), 0.5, MUTED),
        ("LINEAFTER",    (0,0), (2,-1),  0.25, MUTED),
        ("TOPPADDING",   (0,0), (-1,-1), 10),
        ("BOTTOMPADDING",(0,0), (-1,-1), 10),
        ("LEFTPADDING",  (0,0), (-1,-1), 12),
        ("RIGHTPADDING", (0,0), (-1,-1), 12),
    ]))
    return t


def _category_table(cat_df: pd.DataFrame, styles):
    if cat_df is None or cat_df.empty:
        return Paragraph("No category data available.", styles["RBIBody"])

    header = ["Category", "Complaints", "% share"]
    total  = cat_df["count"].sum()

    rows = [header]
    for _, row in cat_df.head(10).iterrows():
        pct = f"{row['count'] / total * 100:.1f}%"
        rows.append([row["category"], f"{row['count']:,}", pct])

    t = Table(rows, colWidths=[8*cm, 4*cm, 4*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND",  (0,0), (-1,0), NAVY),
        ("TEXTCOLOR",   (0,0), (-1,0), white),
        ("FONTNAME",    (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE",    (0,0), (-1,-1), 9),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[white, LIGHT]),
        ("GRID",        (0,0), (-1,-1), 0.25, MUTED),
        ("TOPPADDING",  (0,0), (-1,-1), 6),
        ("BOTTOMPADDING",(0,0),(-1,-1), 6),
        ("LEFTPADDING", (0,0), (-1,-1), 8),
    ]))
    return t


def _bank_table(bank_df: pd.DataFrame, styles):
    if bank_df is None or bank_df.empty:
        return Paragraph("No bank data available.", styles["RBIBody"])

    header = ["Bank", "Complaints", "Resolved", "Resolution rate"]
    rows = [header]
    for _, row in bank_df.iterrows():
        rows.append([
            row["bank"],
            f"{row['total']:,}",
            f"{row['resolved']:,}",
            f"{row['resolution_rate']:.1f}%",
        ])

    t = Table(rows, colWidths=[6*cm, 3*cm, 3*cm, 4*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND",  (0,0), (-1,0), TEAL),
        ("TEXTCOLOR",   (0,0), (-1,0), white),
        ("FONTNAME",    (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE",    (0,0), (-1,-1), 9),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[white, LIGHT]),
        ("GRID",        (0,0), (-1,-1), 0.25, MUTED),
        ("TOPPADDING",  (0,0), (-1,-1), 6),
        ("BOTTOMPADDING",(0,0),(-1,-1), 6),
        ("LEFTPADDING", (0,0), (-1,-1), 8),
    ]))
    return t


def _policy_section(recommendations: list[dict], insight: str, styles):
    items = []
    items.append(Paragraph("Policy Insight", styles["RBIH2"]))
    items.append(Paragraph(insight or "No significant spikes detected.", styles["RBIBody"]))
    items.append(Spacer(1, 0.3*cm))

    for rec in recommendations:
        sev_style = styles.get(f"Sev{rec['severity']}", styles["RBIH2"])
        items.append(Paragraph(
            f"[{rec['severity']}] {rec['category']} — {rec['growth_pct']:+.1f}% growth",
            sev_style,
        ))
        items.append(Paragraph(rec["recommendation"], styles["RBIBody"]))
        items.append(HRFlowable(width="100%", thickness=0.25, color=MUTED, spaceAfter=6))

    return items


def _risk_table(risk_df: pd.DataFrame, styles):
    if risk_df is None or risk_df.empty:
        return Paragraph("No risk scoring data available.", styles["RBIBody"])

    header = ["Category", "Risk score", "Tier", "MoM growth", "Resolution rate"]
    rows = [header]
    for _, row in risk_df.iterrows():
        rows.append([
            row["category"],
            f"{row['risk_score']:.1f}",
            row["risk_tier"],
            f"{row['mom_pct_change']:+.1f}%",
            f"{row['resolution_rate']:.1f}%",
        ])

    t = Table(rows, colWidths=[5.5*cm, 2.5*cm, 2.5*cm, 3*cm, 3*cm])
    style_cmds = [
        ("BACKGROUND",   (0,0), (-1,0), NAVY),
        ("TEXTCOLOR",    (0,0), (-1,0), white),
        ("FONTNAME",     (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE",     (0,0), (-1,-1), 9),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[white, LIGHT]),
        ("GRID",         (0,0), (-1,-1), 0.25, MUTED),
        ("TOPPADDING",   (0,0), (-1,-1), 6),
        ("BOTTOMPADDING",(0,0), (-1,-1), 6),
        ("LEFTPADDING",  (0,0), (-1,-1), 8),
    ]
    tier_colors = {"CRITICAL": RED, "HIGH": AMBER, "MEDIUM": HexColor("#185FA5"), "LOW": TEAL}
    for i, row in enumerate(risk_df.itertuples(), start=1):
        tc = tier_colors.get(row.risk_tier)
        if tc:
            style_cmds.append(("TEXTCOLOR", (2, i), (2, i), tc))
            style_cmds.append(("FONTNAME", (2, i), (2, i), "Helvetica-Bold"))
    t.setStyle(TableStyle(style_cmds))
    return t


def generate_pdf(
    kpis:            dict,
    cat_df:          Optional[pd.DataFrame],
    bank_df:         Optional[pd.DataFrame],
    recommendations: list[dict],
    policy_insight:  str,
    ai_summary:      str,
    report_month:    str = "",
) -> bytes:
    if not REPORTLAB_AVAILABLE:
        return b"[ReportLab not installed - run: pip install reportlab]"

    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=2.2*cm, rightMargin=2.2*cm,
        topMargin=2.2*cm,  bottomMargin=2.2*cm,
    )
    styles = _styles()
    month  = report_month or datetime.now().strftime("%B %Y")
    story  = []

    # ── Page 1: Cover + KPIs + AI narrative ──
    story.append(Paragraph("Reserve Bank of India", styles["RBISubtitle"]))
    story.append(Spacer(1, 0.1*cm))
    story.append(Paragraph("Consumer Complaint Intelligence Report", styles["RBITitle"]))
    story.append(Spacer(1, 0.15*cm))
    story.append(Paragraph(f"Reporting period: {month}", styles["RBISubtitle"]))
    story.append(Paragraph(
        f"Generated: {datetime.now().strftime('%d %B %Y, %H:%M')}  ·  "
        "Data Analytics & Policy Research Division",
        styles["RBICaption"],
    ))
    story.append(HRFlowable(width="100%", thickness=1, color=NAVY, spaceAfter=14))

    story.append(Paragraph("Executive Summary — Key Indicators", styles["RBIH1"]))
    story.append(_kpi_table(kpis, styles))
    story.append(Spacer(1, 0.6*cm))

    if ai_summary:
        story.append(Paragraph("AI Trend Analysis", styles["RBIH2"]))
        story.append(Spacer(1, 0.1*cm))
        story.append(Paragraph(ai_summary, styles["RBIBody"]))

    story.append(PageBreak())

    # ── Page 2: Category + Bank ──
    story.append(Paragraph("Complaint Category Breakdown", styles["RBIH1"]))
    story.append(Spacer(1, 0.2*cm))
    story.append(_category_table(cat_df, styles))
    story.append(Spacer(1, 0.7*cm))

    story.append(Paragraph("Institution-wise Complaint Analysis", styles["RBIH1"]))
    story.append(Spacer(1, 0.2*cm))
    story.append(_bank_table(bank_df, styles))

    story.append(PageBreak())

    # ── Page 3: Policy recommendations ──
    story.append(Paragraph("Policy Recommendations", styles["RBIH1"]))
    story.append(Spacer(1, 0.2*cm))
    story.extend(_policy_section(recommendations, policy_insight, styles))

    story.append(Spacer(1, 1.2*cm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=MUTED, spaceAfter=6))
    story.append(Paragraph(
        "CONFIDENTIAL — For internal RBI use only. "
        "This report is generated by the CCID automated analytics platform. "
        "Recommendations are AI-assisted and subject to expert review before action.",
        styles["RBIFooter"],
    ))

    doc.build(story)
    return buf.getvalue()


def generate_policy_brief_pdf(
    kpis:            dict,
    risk_index:      dict,
    risk_df:         Optional[pd.DataFrame],
    recommendations: list[dict],
    executive_summary: str,
    policy_insight:  str,
    report_month:    str = "",
) -> bytes:
    """
    Generate the standalone PDF Policy Brief — a short (1-2 page) leadership-facing
    document covering: executive summary, overall risk index, per-category risk
    scoring, and active policy recommendations. Distinct from the full monthly
    report (which includes category/bank breakdowns and AI trend narrative).
    """
    if not REPORTLAB_AVAILABLE:
        return b"[ReportLab not installed - run: pip install reportlab]"

    buf    = io.BytesIO()
    doc    = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm,
        topMargin=2*cm,  bottomMargin=2*cm,
    )
    styles = _styles()
    month  = report_month or datetime.now().strftime("%B %Y")

    story = []

    # ── Cover header ──
    story.append(Paragraph("Reserve Bank of India", styles["RBISubtitle"]))
    story.append(Paragraph("Consumer Complaint Intelligence — Policy Brief", styles["RBITitle"]))
    story.append(Paragraph(f"Reporting period: {month}", styles["RBISubtitle"]))
    story.append(Paragraph(
        f"Generated: {datetime.now().strftime('%d %B %Y, %H:%M')}  |  "
        "Data Analytics & Policy Research Division",
        styles["RBICaption"],
    ))
    story.append(HRFlowable(width="100%", thickness=1, color=NAVY, spaceAfter=16))

    # ── Executive summary ──
    story.append(Paragraph("Executive Summary", styles["RBIH1"]))
    story.append(Paragraph(executive_summary or "No executive summary available.", styles["RBIBody"]))
    story.append(Spacer(1, 0.3*cm))
    story.append(_kpi_table(kpis, styles))
    story.append(Spacer(1, 0.5*cm))

    # ── Overall risk index ──
    story.append(Paragraph("Risk Scoring", styles["RBIH1"]))
    idx_data = [
        [
            Paragraph("Overall risk index", styles["RBIKpiLabel"]),
            Paragraph("Risk tier",           styles["RBIKpiLabel"]),
            Paragraph("Critical categories",  styles["RBIKpiLabel"]),
            Paragraph("High categories",      styles["RBIKpiLabel"]),
        ],
        [
            Paragraph(f"{risk_index.get('index', 0):.1f} / 100", styles["RBIKpiValue"]),
            Paragraph(risk_index.get("tier", "LOW"),              styles["RBIKpiValue"]),
            Paragraph(str(risk_index.get("counts", {}).get("CRITICAL", 0)), styles["RBIKpiValue"]),
            Paragraph(str(risk_index.get("counts", {}).get("HIGH", 0)),     styles["RBIKpiValue"]),
        ],
    ]
    idx_table = Table(idx_data, colWidths=[4*cm, 4*cm, 4*cm, 4*cm])
    idx_table.setStyle(TableStyle([
        ("BACKGROUND",  (0,0), (-1,-1), LIGHT),
        ("BOX",         (0,0), (-1,-1), 0.5, MUTED),
        ("GRID",        (0,0), (-1,-1), 0.25, MUTED),
        ("TOPPADDING",  (0,0), (-1,-1), 8),
        ("BOTTOMPADDING",(0,0),(-1,-1), 8),
        ("LEFTPADDING", (0,0), (-1,-1), 10),
        ("RIGHTPADDING",(0,0), (-1,-1), 10),
    ]))
    story.append(idx_table)
    story.append(Spacer(1, 0.4*cm))

    story.append(Paragraph("Risk score by category", styles["RBIH2"]))
    story.append(_risk_table(risk_df, styles))

    story.append(PageBreak())

    # ── Policy recommendations ──
    story.append(Paragraph("Policy Recommendations", styles["RBIH1"]))
    story.extend(_policy_section(recommendations, policy_insight, styles))

    # ── Footer note ──
    story.append(Spacer(1, 1*cm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=MUTED, spaceAfter=6))
    story.append(Paragraph(
        "CONFIDENTIAL — For internal RBI use only. "
        "This policy brief is generated by the CCID automated analytics platform. "
        "Recommendations are AI-assisted and subject to expert review.",
        styles["RBIFooter"],
    ))

    doc.build(story)
    return buf.getvalue()


# Backward-compatible alias (some app.py versions import this shorter name)
generate_policy_brief = generate_policy_brief_pdf


# ── generate_policy_brief ─────────────────────────────────────────────────────
# New-style entry point called by app.py:
#   generate_policy_brief(risk=..., recommendations=..., policy_insight=...,
#                         kpis=..., report_month=...)
# Where `risk` is the dict returned by analytics.risk_score() with keys:
#   grade, total_score, interpretation, dimensions, fraud_count

def generate_policy_brief(
    risk:            dict,
    recommendations: list,
    policy_insight:  str,
    kpis:            dict,
    report_month:    str = "",
) -> bytes:
    """
    2-page PDF Policy Brief using the new risk_score() dict format.
    Distinct from generate_policy_brief_pdf() which uses the old overall_risk_index format.
    """
    if not REPORTLAB_AVAILABLE:
        return b"[ReportLab not installed - run: pip install reportlab]"

    buf     = io.BytesIO()
    doc     = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm,
        topMargin=2*cm,  bottomMargin=2*cm,
    )
    styles  = _styles()
    month   = report_month or datetime.now().strftime("%B %Y")

    # Tier colours for PDF
    _tc = {"CRITICAL": RED, "HIGH": AMBER, "MEDIUM": HexColor("#185FA5"), "LOW": TEAL}

    grade       = risk.get("grade", "LOW")
    total_score = risk.get("total_score", 0.0)
    interp      = risk.get("interpretation", "")
    dimensions  = risk.get("dimensions", [])
    tier_color  = _tc.get(grade, TEAL)

    story = []

    # ── Cover header ──
    story.append(Paragraph("Reserve Bank of India", styles["RBISubtitle"]))
    story.append(Paragraph("Consumer Complaint Intelligence — Policy Brief", styles["RBITitle"]))
    story.append(Paragraph(f"Reporting period: {month}", styles["RBISubtitle"]))
    story.append(Paragraph(
        f"Generated: {datetime.now().strftime('%d %B %Y, %H:%M')}  |  "
        "Data Analytics & Policy Research Division",
        styles["RBICaption"],
    ))
    story.append(HRFlowable(width="100%", thickness=1, color=NAVY, spaceAfter=16))

    # ── Risk index strip ──
    story.append(Paragraph("Composite Risk Assessment", styles["RBIH1"]))
    idx_data = [
        [Paragraph("Risk score",  styles["RBIKpiLabel"]),
         Paragraph("Grade",       styles["RBIKpiLabel"]),
         Paragraph("Fraud cases", styles["RBIKpiLabel"]),
         Paragraph("Active flags",styles["RBIKpiLabel"])],
        [Paragraph(f"{total_score:.1f} / 100", styles["RBIKpiValue"]),
         Paragraph(grade,                       styles["RBIKpiValue"]),
         Paragraph(str(risk.get("fraud_count", 0)), styles["RBIKpiValue"]),
         Paragraph(str(len(recommendations)),   styles["RBIKpiValue"])],
    ]
    idx_t = Table(idx_data, colWidths=[4*cm]*4)
    idx_t.setStyle(TableStyle([
        ("BACKGROUND",   (0,0), (-1,-1), LIGHT),
        ("BOX",          (0,0), (-1,-1), 0.5, MUTED),
        ("GRID",         (0,0), (-1,-1), 0.25, MUTED),
        ("TOPPADDING",   (0,0), (-1,-1), 8),
        ("BOTTOMPADDING",(0,0), (-1,-1), 8),
        ("LEFTPADDING",  (0,0), (-1,-1), 10),
        ("TEXTCOLOR",    (1,1), (1,1), tier_color),
        ("FONTNAME",     (1,1), (1,1), "Helvetica-Bold"),
    ]))
    story.append(idx_t)
    story.append(Spacer(1, 0.4*cm))
    story.append(Paragraph(interp, styles["RBIBody"]))

    # ── KPI strip ──
    story.append(Paragraph("Key Performance Indicators", styles["RBIH1"]))
    story.append(_kpi_table(kpis, styles))

    # ── Risk dimensions table ──
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph("Risk Dimension Breakdown", styles["RBIH1"]))
    if dimensions:
        dim_header = [["Dimension", "Score / 100", "Raw value", "Weight"]]
        dim_rows   = [[d["name"], f"{d['score']:.0f}", d["raw"], d["weight"]] for d in dimensions]
        dim_t = Table(dim_header + dim_rows, colWidths=[6*cm, 3*cm, 4.5*cm, 2.5*cm])
        dim_t.setStyle(TableStyle([
            ("BACKGROUND",   (0,0), (-1,0), NAVY),
            ("TEXTCOLOR",    (0,0), (-1,0), white),
            ("FONTNAME",     (0,0), (-1,0), "Helvetica-Bold"),
            ("FONTSIZE",     (0,0), (-1,-1), 9),
            ("ROWBACKGROUNDS",(0,1),(-1,-1),[white, LIGHT]),
            ("GRID",         (0,0), (-1,-1), 0.25, MUTED),
            ("TOPPADDING",   (0,0), (-1,-1), 6),
            ("BOTTOMPADDING",(0,0), (-1,-1), 6),
            ("LEFTPADDING",  (0,0), (-1,-1), 8),
        ]))
        story.append(dim_t)

    story.append(PageBreak())

    # ── Policy recommendations ──
    story.append(Paragraph("Policy Recommendations", styles["RBIH1"]))
    story.extend(_policy_section(recommendations, policy_insight, styles))

    # ── Sign-off block ──
    story.append(Spacer(1, 1.5*cm))
    sign_data = [
        ["Prepared by", "Reviewed by", "Authorised by"],
        [" " * 30, " " * 30, " " * 30],
        ["Data Analytics Division", "Chief Risk Officer", "Governor's Office"],
    ]
    sign_t = Table(sign_data, colWidths=[5.5*cm]*3)
    sign_t.setStyle(TableStyle([
        ("FONTNAME",     (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE",     (0,0), (-1,-1), 9),
        ("TEXTCOLOR",    (0,0), (-1,-1), MUTED),
        ("LINEABOVE",    (0,1), (-1,1), 0.5, MUTED),
        ("TOPPADDING",   (0,0), (-1,-1), 8),
        ("BOTTOMPADDING",(0,0), (-1,-1), 8),
        ("LEFTPADDING",  (0,0), (-1,-1), 6),
    ]))
    story.append(sign_t)

    # ── Footer ──
    story.append(Spacer(1, 0.8*cm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=MUTED, spaceAfter=6))
    story.append(Paragraph(
        "CONFIDENTIAL — For internal RBI use only. "
        "This policy brief is AI-assisted and subject to expert review before circulation.",
        styles["RBIFooter"],
    ))

    doc.build(story)
    return buf.getvalue()
