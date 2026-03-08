# SAMI Compliance Engine

AI-powered compliance validation for UK regulated industries. Uses NLP and deterministic rule matching to detect regulatory violations in business documents.

## What It Does

Takes business documents (tenancy agreements, contracts, compliance forms) as input and validates them against UK regulatory rules, flagging violations with specific legal citations.

## How It Works
Document Input → Text Extraction → Rule Matching → NLP Classification → Compliance Report
↓                    ↓
Exact Match           Semantic Match
(prohibited terms)    (variant detection)
↓                    ↓
Merge Results → Generate Report
↓
GREEN (Pass) / RED (Fail)
+ Specific Legal Citations
## Regulations Covered

- **Tenant Fees Act 2019** — Prohibited fee detection with semantic variant matching
- **GDPR Article 17** — Right to erasure compliance validation
- **Deposit Protection** — Tenancy deposit scheme compliance checks

## Tech Stack

- Python 3.11
- scikit-learn (text classification)
- spaCy (NLP processing)
- FastAPI (REST API)
- PostgreSQL (audit trail)

## Installation
```bash
git clone https://github.com/mihirdabhi/sami-compliance-engine.git
cd sami-compliance-engine
pip install -r requirements.txt
```

## Usage
```bash
# Run validation on a document
python -m app.validate sample_tenancy_agreement.txt

# Start API server
uvicorn app.main:app --reload
```

## Project Structure

sami-compliance-engine/
├── app/
│   ├── init.py
│   ├── main.py                 # FastAPI application
│   ├── validate.py             # CLI validation tool
│   └── rules/
│       ├── init.py
│       ├── base.py             # Base rule class
│       ├── tenant_fees.py      # Tenant Fees Act 2019
│       ├── gdpr.py             # GDPR compliance
│       └── deposit.py          # Deposit protection
├── tests/
│   ├── init.py
│   └── test_tenant_fees.py     # Unit tests
├── requirements.txt
└── README.md
## Technical Approach

This engine applies techniques from fraud detection ML research to regulatory compliance:

- **Pattern matching** — Same approach as detecting fraudulent transaction patterns, applied to detecting prohibited contractual terms
- **Anomaly detection** — Identifying unusual clauses that may violate regulations
- **Deterministic validation** — Hard-coded rule functions that produce consistent, auditable results (unlike probabilistic LLM outputs)
- **Semantic matching** — NLP classification to catch variant phrasings of prohibited terms

## Context

Built by Mihir Dabhi, Founder of SAMI Systems Ltd (Companies House #16916704).
MSc Big Data Technologies, University of Westminster.

The compliance engine applies machine learning and NLP techniques from academic research in fraud detection to the problem of regulatory compliance validation in UK regulated industries.
