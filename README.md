# MediPolicy_IQ 🏥

**MediPolicy_IQ** is an enterprise-grade AI-powered Healthcare Insurance & Claims Intelligence Platform. It automates the complete insurance claim lifecycle (claims adjudication, eligibility verification, dynamic policy rule evaluation, OCR invoice & prescription extraction, medical coding ICD-10/CPT checks, multi-policy Coordination of Benefits (COB), claim decisioning, fraud risk scoring, and RAG policy Q&A assistant).

---

## 🌟 Key Highlights & Features

- **FastAPI Backend**: Layered clean architecture with Repository Pattern, Pydantic schemas, and SQLAlchemy ORM.
- **Dynamic Policy Rule Engine**: Database-driven policy configurations (deductibles, co-pays, sub-limits, non-network penalties, cosmetic exclusions).
- **Multi-Policy Coordination of Benefits (COB)**: Primary vs. Secondary insurance liability split calculator.
- **Explainable AI Fraud Detection**: Risk scoring model (0-100) analyzing billing anomalies, diagnosis-to-length-of-stay deviations, and overbilled CPT procedures.
- **Document OCR Suite**: Data extraction from medical invoices, prescriptions, and insurance cards into structured JSON format.
- **Policy RAG Assistant**: Natural language Q&A interface for instant policy clause verification.
- **Interactive Streamlit Dashboard**: Analytics, claims entry, OCR workspace, rule editor, and fraud dashboard.
- **Dockerized & CI/CD Ready**: Docker Compose setup and GitHub Actions testing workflow.

---

## 📁 Repository Structure

```text
MediPolicy_IQ/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── dependencies/   # Auth & RBAC dependencies
│   │   │   ├── routes/         # Auth, Patients, Policies, Claims, OCR, RAG, Analytics
│   │   │   └── router.py
│   │   ├── ai/                 # RAG Policy Assistant
│   │   ├── core/               # App config, security, logging, constants
│   │   ├── database/           # Engine, sessions, base, seed
│   │   ├── models/             # SQLAlchemy ORM models
│   │   ├── schemas/            # Pydantic schemas
│   │   ├── repositories/       # Generic Base Repository
│   │   ├── services/           # Claim service, COB, Fraud, Medical coding
│   │   ├── ocr/                # Document OCR parser
│   │   ├── rules/              # Dynamic Policy Rule Engine
│   │   └── main.py             # FastAPI entrypoint
│   ├── tests/                  # Pytest test suite
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── pages/                  # Streamlit multi-page layout
│   ├── services/               # API client wrapper
│   └── streamlit_app.py        # Streamlit entrypoint
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
├── .github/
│   └── workflows/ci-cd.yml
└── README.md
```

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- Python 3.12+
- Docker & Docker Compose (Optional)

### 2. Local Setup & Execution

#### A. Backend (FastAPI)
```bash
cd backend

# Create virtual environment
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# Install requirements
pip install -r requirements.txt

# Run FastAPI server (Auto-creates SQLite DB & seeds initial sample data)
uvicorn app.main:app --app-dir backend --reload --host 127.0.0.1 --port 8000
```
- Swagger Documentation: `http://127.0.0.1:8000/docs`
- Health Check: `http://127.0.0.1:8000/`

#### B. Frontend (Streamlit)
Open a separate terminal window:
```bash
cd frontend

# Activate virtual environment
..\backend\venv\Scripts\activate

# Launch Streamlit dashboard
streamlit run streamlit_app.py
```
- Streamlit Web UI: `http://localhost:8501`

---

## 🧪 Running Unit Tests

Run the backend Pytest test suite:
```bash
cd backend
python -m pytest tests/
```

---

## 🐳 Docker Deployment

To build and launch both Backend and Frontend via Docker Compose:
```bash
docker-compose -f docker/docker-compose.yml up --build
```
- Backend: `http://localhost:8000`
- Frontend: `http://localhost:8501`

---

## 📜 License
This project is licensed under the MIT License.
