# FinSight
AI-Powered Financial Complaint Intelligence Platform

> An AI-powered analytics platform that analyses banking and digital payment complaints,
> identifies emerging issues, generates dashboards, and produces policy recommendations.
> Built to demonstrate skills directly aligned with the RBI Data Analytics & Policy Research role.

---

## Features

| Module | What it does |
|--------|-------------|
| **Data Cleaning** | Deduplicates, normalises categories, remaps states/banks |
| **Analytics Engine** | KPIs, trend analysis, category/bank breakdowns |
| **Anomaly Detector** | Z-score based weekly spike detection |
| **AI Summariser** | GPT-4o narrative summary of complaint batches |
| **Policy Engine** | Rule + LLM hybrid regulatory recommendations |
| **PDF Generator** | One-click RBI-style monthly report |

---

## Quickstart

### 1. Clone and setup

```bash
git clone https://github.com/gaurisoonii/Finsight.git
cd Finsight

python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY (optional — works without it)
```

### 3. Add data (optional)

Download the CFPB Consumer Complaints dataset from:
https://www.consumerfinance.gov/data-research/consumer-complaints/

Place it at `data/complaints.csv`. If absent, the app auto-generates
50,000 synthetic records that mirror the real dataset structure.

### 4. Run

```bash
streamlit run app.py
```

Visit http://localhost:8501

---

## Project Structure

```
ccid/
├── app.py                  ← Entry point, sidebar, routing, all pages inlined
├── requirements.txt
├── .env.example
├── data/
│   ├── complaints.csv      ← Place CFPB CSV here (optional)
│   └── complaints.db       ← Auto-generated SQLite database
└── modules/
    ├── cleaner.py          ← Data cleaning pipeline
    ├── analytics.py        ← KPIs, trends, anomalies, risk scoring, policy rules
    ├── ai_engine.py        ← OpenAI integration
    ├── charts.py           ← Plotly figure factories
    └── report_generator.py ← ReportLab PDF builder
```

> Note: this app is a single Streamlit script (`app.py`) with every page function
> defined and routed inline via a sidebar radio control. There is intentionally
> **no `pages/` folder** — Streamlit auto-generates its own multi-page navigation
> from any `pages/` directory it finds, which would conflict with and shadow the
> app's own sidebar routing. If you ever see a duplicate page list above the
> "NAVIGATION" section in the sidebar, it means a `pages/` folder was re-added —
> delete it.

---

## Tech Stack

- **Python 3.11+**
- **Pandas / NumPy** — Data manipulation
- **SQLite / SQLAlchemy** — Storage layer
- **Plotly** — Interactive charts
- **Streamlit** — UI framework
- **OpenAI GPT-4o mini** — AI summaries and policy insights
- **SciPy** — Z-score anomaly detection
- **ReportLab** — PDF report generation

---

## Note on dataset remapping

The CFPB dataset uses US state codes and US bank names. CCID applies
a deterministic remapping to Indian states and Indian banks to simulate
a realistic RBI-facing dataset. This is documented in `modules/cleaner.py`
and disclosed in the report footer. Interview note: be upfront about this
— it's actually a strength, showing awareness of real data constraints.

---

## Resume bullet

> Developed an AI-powered Consumer Complaint Intelligence Dashboard using
> Python, SQL, Streamlit, and GPT-4o to analyse 100,000+ financial complaints —
> featuring anomaly detection, category trend analysis, and a policy recommendation
> engine that flags regulatory action items with severity scoring.
