"""
Base class for all compliance validation rules.
Each rule implements a validate() method that checks
document text against specific UK regulations.
"""

from abc import ABC, abstractmethod
from typing import Dict, List
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Violation:
    """Represents a single compliance violation found in a document."""
    term: str
    position: int
    context: str
    severity: str  # HIGH, MEDIUM, LOW
    citation: str
    match_type: str  # exact_match, semantic_match
    description: str = ""


@dataclass
class ValidationResult:
    """Result of running a compliance validation rule."""
    rule_name: str
    status: str  # PASS, FAIL
    total_violations: int
    violations: List[Violation] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    summary: str = ""

    def to_dict(self) -> Dict:
        return {
            "rule": self.rule_name,
            "status": self.status,
            "total_violations": self.total_violations,
            "violations": [
                {
                    "term": v.term,
                    "position": v.position,
                    "context": v.context,
                    "severity": v.severity,
                    "citation": v.citation,
                    "match_type": v.match_type,
                    "description": v.description,
                }
                for v in self.violations
            ],
            "timestamp": self.timestamp,
            "summary": self.summary,
        }


class ComplianceRule(ABC):
    """Abstract base class for compliance rules."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable name of the regulation."""
        pass

    @property
    @abstractmethod
    def legislation(self) -> str:
        """Official legislation reference."""
        pass

    @abstractmethod
    def validate(self, document_text: str) -> ValidationResult:
        """
        Validate document text against this regulation.

        Args:
            document_text: The full text of the document to validate.

        Returns:
            ValidationResult with pass/fail status and any violations found.
        """
        pass

    def _extract_context(self, text: str, position: int, window: int = 60) -> str:
        """Extract surrounding context for a match."""
        start = max(0, position - window)
        end = min(len(text), position + window)
        return text[start:end].strip()
