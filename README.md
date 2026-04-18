# FD Dropout Analyst

Behavioral intelligence for Blostem's FD platform — identifying which users
will drop off before completing their Fixed Deposit booking, why they drop off,
and what intervention to trigger for each cohort.

Built for the Blostem AI Builder Hackathon 2026 (Track 03 — Data Analytics).

## The Problem

Blostem's FD platform loses users between intent and booking. A user compares
6 banks, starts KYC, and disappears. Another browses for 3 sessions and goes
cold. Each incomplete booking is lost revenue — and the reasons are different
for every user.

Most analytics tools give you a churn score. This gives you a story.

## What It Does

**Platform Overview** — KPIs, risk distribution, cohort breakdown, at-risk
deposit value across 3,000 user profiles.

**Cohort Intelligence** — High-risk users automatically segmented into 4
named behavioral cohorts: KYC Dropout, Comparison Paralysis, Overwhelmed
First-Timer, Silent Churner. Each cohort has a distinct dropout pattern.

**AI Analyst Reports** — RAG-powered reports generated per cohort using
LLaMA 3.3 70B + FAISS vector store built on a domain knowledge base covering
RBI KYC circulars, SFB rate benchmarks, Indian investor behavior research,
and intervention playbooks. Each report surfaces: Finding → Root Cause →
Recommended Action.

**User Risk Scorer** — Real-time churn probability for individual users with
SHAP waterfall chart explaining which behavioral signals drove the score.

## Tech Stack

| Layer | Technology |
|---|---|
| Prediction | XGBoost · ROC-AUC 0.939 |
| Explainability | SHAP |
| Segmentation | Rule-based behavioral cohort assignment |
| Embeddings | sentence-transformers/all-MiniLM-L6-v2 |
| Vector Store | FAISS |
| LLM | LLaMA 3.3 70B via Groq API |
| Orchestration | LangChain |
| Frontend | Streamlit |

## Live App

[[Insert Streamlit Cloud URL here after deployment](https://fd-dropout-analyst.streamlit.app)]

## Project Structure
fd-dropout-analyst/
├── data/
│   ├── generate_data.py        # Synthetic FD user behavioral dataset (3,000 users)
│   └── fd_users.csv
├── knowledge_base/             # RAG knowledge base (5 domain documents)
│   ├── fd_basics.md
│   ├── kyc_process.md
│   ├── india_investor_behavior.md
│   ├── blostem_context.md
│   └── intervention_playbook.md
├── model/
│   ├── train_model.py          # XGBoost training + evaluation
│   ├── segment.py              # Cohort segmentation + stats extraction
│   ├── analyst.py              # RAG pipeline + LLM report generation
│   ├── churn_model.pkl
│   ├── features.pkl
│   ├── cohort_stats.json
│   └── analyst_reports.json
├── app.py                      # Streamlit application (4 pages)
└── requirements.txt

## Why This Approach

Health insurance fraud detection and FD churn prediction are structurally
the same problem — find the anomalous behavioral signal before money walks
out the door. I built a fraud detection system on 500K+ insurance claims
with SHAP explainability (deployed, live). This project applies the same
thinking to Blostem's activation gap.

The difference between this and a standard churn dashboard: the output is
not a score. It is a written analyst report — the same 3-paragraph insight
a senior data analyst would produce, generated in seconds for any cohort,
grounded in a domain knowledge base specific to Indian fintech and RBI
compliance context.

## Model Performance
XGBoost Classifier
ROC-AUC:  0.939
Accuracy: 0.940
Precision (churn): 0.94
Recall (churn):    0.92

## Running Locally

```bash
git clone https://github.com/aparnaworkspace/fd-dropout-analyst
cd fd-dropout-analyst
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

export GROQ_API_KEY=your_key_here

python data/generate_data.py
python model/train_model.py
python model/segment.py
python model/analyst.py
streamlit run app.py
```

## Built By

Aparna Sajeevan — Final year B.Tech CSE (Health Informatics), VIT Bhopal.
[GitHub](https://github.com/aparnaworkspace)
