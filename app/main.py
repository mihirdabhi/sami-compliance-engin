"""
SAMI Compliance Engine — FastAPI Application

REST API for validating documents against UK regulations.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict
from .rules.tenant_fees import TenantFeesRule
from .rules.gdpr import GDPRRule
from .rules.deposit import DepositProtectionRule

app = FastAPI(
    title="SAMI Compliance Engine",
    description="AI-powered compliance validation for UK regulated industries",
    version="0.1.0",
)

# Initialise all validation rules
RULES = [
    TenantFeesRule(),
    GDPRRule(),
    DepositProtectionRule(),
]


class DocumentInput(BaseModel):
    """Input model for document validation."""
    text: str
    document_type: str = "general"


class ValidationResponse(BaseModel):
    """Response model for validation results."""
    document_type: str
    total_rules_checked: int
    total_violations: int
    overall_status: str
    results: List[Dict]


@app.get("/")
def root():
    return {
        "service": "SAMI Compliance Engine",
        "version": "0.1.0",
        "rules_loaded": len(RULES),
        "regulations": [rule.name for rule in RULES],
    }


@app.post("/validate", response_model=ValidationResponse)
def validate_document(doc: DocumentInput):
    """
    Validate a document against all loaded compliance rules.

    Returns detailed results for each regulation checked,
    including specific violations with legal citations.
    """
    if not doc.text.strip():
        raise HTTPException(status_code=400, detail="Document text cannot be empty")

    results = []
    total_violations = 0

    for rule in RULES:
        result = rule.validate(doc.text)
        results.append(result.to_dict())
        total_violations += result.total_violations

    overall_status = "FAIL" if total_violations > 0 else "PASS"

    return ValidationResponse(
        document_type=doc.document_type,
        total_rules_checked=len(RULES),
        total_violations=total_violations,
        overall_status=overall_status,
        results=results,
    )


@app.get("/rules")
def list_rules():
    """List all available compliance validation rules."""
    return {
        "total_rules": len(RULES),
        "rules": [
            {"name": rule.name, "legislation": rule.legislation}
            for rule in RULES
        ],
    }
