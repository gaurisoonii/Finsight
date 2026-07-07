# FinSight
### AI-Powered Financial Complaint Intelligence & Regulatory Analytics Platform

FinSight is an AI-powered analytics platform designed to transform large-scale financial consumer complaints into actionable regulatory intelligence. It combines statistical analytics, anomaly detection, interactive visualizations, and LLM-assisted insights to help regulators and financial institutions identify emerging risks, monitor complaint trends, and generate evidence-based policy recommendations.

Developed as a portfolio project inspired by real-world financial supervision and consumer protection workflows, FinSight demonstrates practical applications of AI, data analytics, and modern software engineering.

---

## Key Features

| Module | Capability |
|---------|------------|
| **Data Processing Pipeline** | Cleans, validates, deduplicates, and standardizes complaint records while remapping categories, banks, and regions into a consistent analytical format. |
| **Interactive Analytics Dashboard** | Presents complaint trends, KPIs, category distributions, bank-wise analysis, and geographic insights using interactive Plotly visualizations. |
| **Anomaly Detection Engine** | Identifies statistically significant complaint spikes using Z-score analysis to surface unusual patterns requiring investigation. |
| **AI Insight Generator** | Uses GPT-4o to convert analytical findings into concise executive summaries suitable for management and regulatory review. |
| **Policy Recommendation Engine** | Combines deterministic business rules with LLM reasoning to generate explainable regulatory recommendations and risk prioritization. |
| **Automated Report Generator** | Produces professional RBI-style PDF reports containing analytics, charts, AI summaries, and policy recommendations. |
| **Synthetic Data Generator** | Automatically generates realistic complaint datasets for demonstration when external datasets are unavailable. |

---

# System Architecture

```
Complaint Dataset
        │
        ▼
Data Cleaning & Validation
        │
        ▼
Feature Engineering
        │
        ▼
Statistical Analytics
        │
        ├──────────────┐
        ▼              ▼
Interactive Charts   Anomaly Detection
        │              │
        └──────┬───────┘
               ▼
      AI Insight Generator
               │
               ▼
 Policy Recommendation Engine
               │
               ▼
      Executive PDF Reports
```

---

# Technology Stack

### Programming

- Python 3.11+

### Data Engineering

- Pandas
- NumPy
- SQLite
- SQLAlchemy

### Artificial Intelligence

- OpenAI GPT-4o Mini
- Prompt Engineering
- Rule-Based Decision System

### Data Analytics

- SciPy
- Statistical Analysis
- Z-score Anomaly Detection

### Visualization

- Plotly
- Streamlit

### Reporting

- ReportLab

### Deployment

- Streamlit Cloud

---

# Project Structure

```
FinSight/
│
├── app.py
├── requirements.txt
├── .env.example
├── README.md
│
├── data/
│   ├── complaints.csv
│   └── complaints.db
│
├── modules/
│   ├── cleaner.py
│   ├── analytics.py
│   ├── ai_engine.py
│   ├── charts.py
│   └── report_generator.py
│
└── assets/
```

---

# Getting Started

## 1. Clone Repository

```bash
git clone https://github.com/gaurisoonii/Finsight.git
cd Finsight
```

## 2. Create Virtual Environment

```bash
python -m venv venv
```

Windows

```bash
venv\Scripts\activate
```

Linux / macOS

```bash
source venv/bin/activate
```

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## 4. Configure Environment

Copy the sample environment file.

```bash
cp .env.example .env
```

Add your OpenAI API key if AI summaries are required.

The application remains fully functional without an API key by automatically using deterministic fallback summaries.

---

## 5. Dataset

The application supports the CFPB Consumer Complaint Dataset.

Download from:

https://www.consumerfinance.gov/data-research/consumer-complaints/

Place the CSV file inside

```
data/complaints.csv
```

If no dataset is provided, FinSight automatically generates a synthetic dataset containing over **50,000 complaint records** that replicate the structure and distribution of real financial complaint data for demonstration purposes.

---

## 6. Launch

```bash
streamlit run app.py
```

Application URL

```
http://localhost:8501
```

---

# Design Decisions

### Why GPT is used

The LLM is responsible only for transforming structured analytical results into executive-level summaries and policy recommendations.

All numerical computations—including KPIs, anomaly detection, trend analysis, and statistical calculations—are performed deterministically within the analytics engine to ensure consistency and reproducibility.

This hybrid architecture minimizes hallucinations while improving the readability of analytical reports.

---

# Dataset Adaptation

The CFPB dataset contains U.S. banks and state identifiers.

To better simulate an RBI-oriented environment, the preprocessing pipeline deterministically maps these entities to representative Indian banks and states.

This adaptation is fully documented in the preprocessing pipeline and disclosed within generated reports to maintain transparency.

---

# Future Enhancements

- Retrieval-Augmented Generation (RAG) using RBI circulars
- Semantic search over historical complaints
- PostgreSQL backend
- Docker containerization
- Authentication and role-based access control
- REST API
- Real-time complaint ingestion
- ML-based complaint classification
- Model evaluation dashboard
- CI/CD with GitHub Actions

---

# Resume Highlight

> Developed **FinSight**, an AI-powered Financial Complaint Intelligence Platform using Python, Streamlit, SQLite, Plotly, SciPy, and GPT-4o to analyze 100,000+ financial complaint records, detect anomalies, generate executive summaries, and produce explainable policy recommendations through a hybrid analytics and LLM pipeline.
