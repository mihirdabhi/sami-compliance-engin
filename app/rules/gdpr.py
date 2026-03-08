"""
GDPR Compliance Validation Rule

Checks documents for compliance with key GDPR requirements
relevant to UK estate agencies and regulated businesses.

Focuses on:
- Article 13/14: Privacy notice requirements
- Article 17: Right to erasure provisions
- Article 30: Record-keeping obligations

Reference: UK GDPR (retained EU law) + Data Protection Act 2018
"""

import re
from typing import List
from .base import ComplianceRule, ValidationResult, Violation


# Required privacy notice elements under Article 13/14
REQUIRED_PRIVACY_ELEMENTS = [
    ("data controller", "Identity of data controller must be stated"),
    ("purpose", "Purpose of data processing must be specified"),
    ("legal basis", "Legal basis for processing must be identified"),
    ("retention", "Data retention period must be specified"),
    ("right to erasure", "Right to erasure must be mentioned"),
    ("right to access", "Right of access must be mentioned"),
    ("right to rectification", "Right to rectification must be mentioned"),
    ("data protection officer", "DPO contact details should be provided"),
    ("complain", "Right to lodge a complaint must be mentioned"),
]

# Red flag terms suggesting non-compliant data practices
RED_FLAG_TERMS = [
    (r"indefinite(?:ly)?\s+(?:retain|store|keep|hold)", "Data stored indefinitely violates retention principles"),
    (r"share\s+(?:your\s+)?data\s+with\s+(?:any\s+)?third\s+part(?:y|ies)\s+(?:we\s+)?(?:choose|wish|want)", "Blanket third-party sharing without specification"),
    (r"cannot\s+(?:be\s+)?delete[d]?", "Denying right to erasure may violate Article 17"),
    (r"irrevocabl[ey]\s+consent", "Consent must be freely withdrawable under GDPR"),
    (r"waive\s+(?:your\s+)?(?:data\s+protection\s+)?rights", "Data protection rights cannot be waived"),
    (r"no\s+right\s+to\s+(?:access|erasure|deletion)", "Cannot deny statutory data rights"),
]


class GDPRRule(ComplianceRule):
    """Validates documents against UK GDPR requirements."""

    @property
    def name(self) -> str:
        return "UK GDPR Compliance"

    @property
    def legislation(self) -> str:
        return "UK GDPR (retained EU law) + Data Protection Act 2018"

    def validate(self, document_text: str) -> ValidationResult:
        """
        Check document for GDPR compliance issues.

        Performs two checks:
        1. Scans for red flag terms indicating non-compliant practices
        2. Checks if required privacy notice elements are present
        """
        violations = []

        # Check 1: Red flag terms
        violations.extend(self._check_red_flags(document_text))

        # Check 2: Missing privacy elements (only for privacy notices)
        if self._is_privacy_notice(document_text):
            violations.extend(self._check_missing_elements(document_text))

        status = "FAIL" if violations else "PASS"
        summary = (
            f"Found {len(violations)} GDPR compliance issue(s)"
            if violations
            else "No GDPR compliance issues detected"
        )

        return ValidationResult(
            rule_name=self.name,
            status=status,
            total_violations=len(violations),
            violations=violations,
            summary=summary,
        )

    def _check_red_flags(self, text: str) -> List[Violation]:
        """Check for terms indicating non-compliant data practices."""
        violations = []

        for pattern_str, description in RED_FLAG_TERMS:
            pattern = re.compile(pattern_str, re.IGNORECASE)
            for match in pattern.finditer(text):
                violations.append(
                    Violation(
                        term=match.group(),
                        position=match.start(),
                        context=self._extract_context(text, match.start()),
                        severity="HIGH",
                        citation="UK GDPR, Article 17 / Article 7(3)",
                        match_type="semantic_match",
                        description=description,
                    )
                )

        return violations

    def _check_missing_elements(self, text: str) -> List[Violation]:
        """Check if required privacy notice elements are present."""
        violations = []
        text_lower = text.lower()

        for element, description in REQUIRED_PRIVACY_ELEMENTS:
            if element not in text_lower:
                violations.append(
                    Violation(
                        term=element,
                        position=0,
                        context="Element not found in document",
                        severity="MEDIUM",
                        citation="UK GDPR, Article 13/14 — Information Requirements",
                        match_type="missing_element",
                        description=f"Missing required element: {description}",
                    )
                )

        return violations

    def _is_privacy_notice(self, text: str) -> bool:
        """Detect if the document is a privacy notice or policy."""
        privacy_indicators = [
            "privacy notice",
            "privacy policy",
            "data protection notice",
            "data privacy",
            "how we use your data",
            "how we use your information",
            "fair processing notice",
        ]
        text_lower = text.lower()
        return any(indicator in text_lower for indicator in privacy_indicators)


if __name__ == "__main__":
    sample_contract = """
    TENANCY AGREEMENT

    The landlord will indefinitely retain all personal data collected
    during this tenancy. The tenant provides irrevocable consent to
    share data with any third parties we choose for marketing purposes.
    The tenant waives their data protection rights in relation to
    information held by the landlord.
    """

    rule = GDPRRule()
    result = rule.validate(sample_contract)

    print(f"\nRule: {result.rule_name}")
    print(f"Status: {result.status}")
    print(f"Violations: {result.total_violations}")
    print(f"Summary: {result.summary}\n")

    for v in result.violations:
        print(f"  [{v.severity}] '{v.term}'")
        print(f"    Citation: {v.citation}")
        print(f"    Description: {v.description}")
        print()
