"""
SAMI Compliance Engine — Command Line Validator

Usage:
    python -m app.validate "path/to/document.txt"
    python -m app.validate --text "The tenant must pay an admin fee of £150"
"""

import sys
import json
from .rules.tenant_fees import TenantFeesRule
from .rules.gdpr import GDPRRule
from .rules.deposit import DepositProtectionRule


def validate_text(text: str) -> dict:
    """Run all compliance rules against provided text."""
    rules = [
        TenantFeesRule(),
        GDPRRule(),
        DepositProtectionRule(),
    ]

    results = []
    total_violations = 0

    for rule in rules:
        result = rule.validate(text)
        results.append(result.to_dict())
        total_violations += result.total_violations

    return {
        "total_rules_checked": len(rules),
        "total_violations": total_violations,
        "overall_status": "FAIL" if total_violations > 0 else "PASS",
        "results": results,
    }


def validate_file(filepath: str) -> dict:
    """Load a text file and validate its contents."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()
    except FileNotFoundError:
        return {"error": f"File not found: {filepath}"}
    except Exception as e:
        return {"error": f"Could not read file: {str(e)}"}

    return validate_text(text)


def print_report(results: dict):
    """Print a formatted compliance report."""
    if "error" in results:
        print(f"\nError: {results['error']}")
        return

    status = results["overall_status"]
    total = results["total_violations"]

    print("\n" + "=" * 60)
    print("  SAMI COMPLIANCE ENGINE — Validation Report")
    print("=" * 60)
    print(f"\n  Overall Status: {status}")
    print(f"  Rules Checked:  {results['total_rules_checked']}")
    print(f"  Total Violations: {total}")
    print("-" * 60)

    for rule_result in results["results"]:
        rule_status = rule_result["status"]
        rule_name = rule_result["rule"]
        violations = rule_result["violations"]

        icon = "PASS" if rule_status == "PASS" else "FAIL"
        print(f"\n  [{icon}] {rule_name}")
        print(f"       {rule_result['summary']}")

        for v in violations:
            print(f"\n       [{v['severity']}] '{v['term']}'")
            print(f"       Citation: {v['citation']}")
            if v.get("description"):
                print(f"       Detail: {v['description']}")
            if v.get("context") and v["context"] != "Element not found in document":
                print(f"       Context: ...{v['context']}...")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print('  python -m app.validate document.txt')
        print('  python -m app.validate --text "document text here"')
        sys.exit(1)

    if sys.argv[1] == "--text":
        text = " ".join(sys.argv[2:])
        results = validate_text(text)
    else:
        results = validate_file(sys.argv[1])

    print_report(results)
```

Commit message: `Add CLI validation tool for document compliance checking`

Then also create a sample document to test against. Create `samples/sample_tenancy_agreement.txt`:
```
ASSURED SHORTHOLD TENANCY AGREEMENT

Property: 42 Oak Street, London, E1 6AN

1. RENT AND FEES
The monthly rent is £1,400 payable on the 1st of each month.
The tenant shall pay an administration fee of £200 upon signing this agreement.
A referencing fee of £50 per person is required before move-in.
The renewal fee for extending this tenancy is £100.

2. DEPOSIT
A tenancy deposit of £2,000 is required before the start of the tenancy.
The deposit will be held by the landlord in a separate account.

3. DATA AND PRIVACY
The landlord will indefinitely retain all personal data collected during
this tenancy for record-keeping purposes. The tenant provides irrevocable
consent to the processing of their personal data. The landlord may share
your data with any third parties we choose for referencing and marketing.

4. OBLIGATIONS
The tenant is responsible for council tax and utility bills.
A professional cleaning fee of £250 is required at the end of the tenancy.

5. TERMINATION
Either party may terminate this agreement by providing 2 months notice.
