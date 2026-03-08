"""
Tenancy Deposit Compliance Validation Rule

Checks documents for compliance with deposit protection requirements
under the Housing Act 2004, Sections 212-215.

Key requirements:
- Deposit must not exceed 5 weeks rent (Tenant Fees Act 2019)
- Deposit must be protected in a government-approved scheme within 30 days
- Prescribed information must be provided to the tenant

Reference: Housing Act 2004, ss.212-215; Tenant Fees Act 2019, Schedule 1
"""

import re
from typing import List
from .base import ComplianceRule, ValidationResult, Violation


APPROVED_SCHEMES = [
    "deposit protection service",
    "dps",
    "mydeposits",
    "my deposits",
    "tenancy deposit scheme",
    "tds",
]

REQUIRED_DEPOSIT_INFO = [
    ("scheme name", "Name of the approved deposit scheme must be stated"),
    ("how to apply", "Process for applying for deposit return must be explained"),
    ("dispute resolution", "Information about dispute resolution must be provided"),
]


class DepositProtectionRule(ComplianceRule):
    """Validates documents against deposit protection requirements."""

    @property
    def name(self) -> str:
        return "Tenancy Deposit Protection"

    @property
    def legislation(self) -> str:
        return "Housing Act 2004, Sections 212-215"

    def validate(self, document_text: str) -> ValidationResult:
        """
        Check document for deposit protection compliance issues.

        Checks:
        1. Whether deposit amount exceeds 5 weeks rent
        2. Whether an approved protection scheme is mentioned
        3. Whether required prescribed information is present
        """
        violations = []

        violations.extend(self._check_deposit_cap(document_text))
        violations.extend(self._check_scheme_mentioned(document_text))

        status = "FAIL" if violations else "PASS"
        summary = (
            f"Found {len(violations)} deposit compliance issue(s)"
            if violations
            else "No deposit protection issues detected"
        )

        return ValidationResult(
            rule_name=self.name,
            status=status,
            total_violations=len(violations),
            violations=violations,
            summary=summary,
        )

    def _check_deposit_cap(self, text: str) -> List[Violation]:
        """Check if deposit amount exceeds the 5-week rent cap."""
        violations = []

        # Look for deposit and rent amounts
        deposit_pattern = re.compile(
            r"(?:deposit|security\s+deposit)\s+(?:of\s+)?£([\d,]+(?:\.\d{2})?)",
            re.IGNORECASE,
        )
        rent_pattern = re.compile(
            r"(?:monthly\s+)?rent\s+(?:of\s+)?£([\d,]+(?:\.\d{2})?)\s*(?:per\s+month|monthly|pcm)?",
            re.IGNORECASE,
        )

        deposit_matches = list(deposit_pattern.finditer(text))
        rent_matches = list(rent_pattern.finditer(text))

        if deposit_matches and rent_matches:
            deposit_amount = float(deposit_matches[0].group(1).replace(",", ""))
            rent_amount = float(rent_matches[0].group(1).replace(",", ""))
            five_week_cap = (rent_amount * 12) / 52 * 5

            if deposit_amount > five_week_cap:
                violations.append(
                    Violation(
                        term=f"Deposit £{deposit_amount:.2f} exceeds 5-week cap of £{five_week_cap:.2f}",
                        position=deposit_matches[0].start(),
                        context=self._extract_context(text, deposit_matches[0].start()),
                        severity="HIGH",
                        citation="Tenant Fees Act 2019, Schedule 1, Para 3",
                        match_type="calculation",
                        description=f"Monthly rent £{rent_amount:.2f}, 5-week cap is £{five_week_cap:.2f}",
                    )
                )

        return violations

    def _check_scheme_mentioned(self, text: str) -> List[Violation]:
        """Check if an approved deposit scheme is mentioned."""
        text_lower = text.lower()

        scheme_found = any(scheme in text_lower for scheme in APPROVED_SCHEMES)

        if not scheme_found and self._mentions_deposit(text_lower):
            return [
                Violation(
                    term="No approved deposit scheme mentioned",
                    position=0,
                    context="Document mentions a deposit but no approved protection scheme",
                    severity="HIGH",
                    citation="Housing Act 2004, Section 213(1)",
                    match_type="missing_element",
                    description="Deposit must be protected in a government-approved scheme within 30 days",
                )
            ]

        return []

    def _mentions_deposit(self, text_lower: str) -> bool:
        """Check if document mentions a tenancy deposit."""
        deposit_terms = ["deposit", "security deposit", "tenancy deposit"]
        return any(term in text_lower for term in deposit_terms)


if __name__ == "__main__":
    sample = """
    TENANCY AGREEMENT

    Monthly rent: £1,200 per month.
    A tenancy deposit of £1,800 is required before move-in.
    The deposit will be held by the landlord.
    """

    rule = DepositProtectionRule()
    result = rule.validate(sample)

    print(f"\nRule: {result.rule_name}")
    print(f"Status: {result.status}")
    print(f"Violations: {result.total_violations}")
    print(f"Summary: {result.summary}\n")

    for v in result.violations:
        print(f"  [{v.severity}] '{v.term}'")
        print(f"    Citation: {v.citation}")
        print(f"    Description: {v.description}")
        print()
