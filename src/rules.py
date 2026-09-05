import json
import re
from pathlib import Path


# ---------------------------------------------------------
# Load company standards
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
STANDARDS_FILE = BASE_DIR / "data" / "company_standards.json"


def load_standards():
    with open(STANDARDS_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


# ---------------------------------------------------------
# Helper functions
# ---------------------------------------------------------

def find_sentence(text, keywords):
    """
    Find the sentence containing one of the supplied keywords.
    This gives us evidence that can be shown to the reviewer.
    """
    sentences = re.split(r"(?<=[.!?])\s+", text)

    for sentence in sentences:
        sentence_lower = sentence.lower()

        if any(keyword.lower() in sentence_lower for keyword in keywords):
            return sentence.strip()

    return None


def extract_number(text, patterns):
    """
    Find the first numeric value matching the supplied patterns.
    """
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)

        if match:
            try:
                return float(match.group(1))
            except (ValueError, IndexError):
                pass

    return None


def extract_months(text):
    """
    Extract deposit period expressed as a number or common number word.
    """

    number_words = {
        "one": 1,
        "two": 2,
        "three": 3,
        "four": 4,
        "five": 5,
        "six": 6,
        "seven": 7,
        "eight": 8,
        "nine": 9,
        "ten": 10
    }

    numeric_match = re.search(
        r"(\d+(?:\.\d+)?)\s*(?:months?|month's?)",
        text,
        re.IGNORECASE
    )

    if numeric_match:
        return float(numeric_match.group(1))

    for word, value in number_words.items():
        if re.search(
            rf"\b{word}\s+(?:months?|month's?)",
            text,
            re.IGNORECASE
        ):
            return float(value)

    return None


def extract_days(text):
    """
    Extract notice period in days.
    """

    number_words = {
        "thirty": 30,
        "sixty": 60,
        "ninety": 90,
        "one hundred": 100
    }

    numeric_match = re.search(
        r"(\d+(?:\.\d+)?)\s*(?:days?|day's?)",
        text,
        re.IGNORECASE
    )

    if numeric_match:
        return float(numeric_match.group(1))

    for phrase, value in number_words.items():
        if re.search(
            rf"\b{phrase}\s+(?:days?|day's?)",
            text,
            re.IGNORECASE
        ):
            return float(value)

    return None


def extract_percentage(text):
    """
    Extract a percentage value.
    """
    match = re.search(
        r"(\d+(?:\.\d+)?)\s*%",
        text,
        re.IGNORECASE
    )

    if match:
        return float(match.group(1))

    number_words = {
        "one": 1,
        "two": 2,
        "three": 3,
        "four": 4,
        "five": 5,
        "six": 6,
        "seven": 7,
        "eight": 8,
        "nine": 9,
        "ten": 10
    }

    for word, value in number_words.items():
        if re.search(
            rf"\b{word}\s+percent",
            text,
            re.IGNORECASE
        ):
            return float(value)

    return None


def add_finding(
    findings,
    category,
    clause_type,
    status,
    clause,
    explanation,
    action
):
    findings.append({
        "category": category,
        "clause_type": clause_type,
        "status": status,
        "clause": clause,
        "explanation": explanation,
        "action": action
    })


def calculate_severity(finding):
    """
    Assign risk severity based on the type and status
    of the deterministic finding.

    Compliant findings carry zero risk.
    """

    if finding["category"] == "compliant":
        return "COMPLIANT", 0

    clause_type = finding.get("clause_type", "")
    status = finding.get("status", "")

    # Critical legal/control concerns
    if clause_type == "early_termination":
        return "CRITICAL", 4

    # High-impact commercial or protection issues
    if clause_type in {
        "security_deposit",
        "deposit_return",
        "rent_increase",
        "maintenance",
        "subletting"
    }:
        return "HIGH", 3

    # Notice and fee issues
    if clause_type in {
        "notice_period",
        "late_fee"
    }:
        return "MEDIUM", 2

    # Missing identity or duration information
    if clause_type in {
        "landlord_identification",
        "tenant_identification",
        "lease_duration"
    }:
        return "LOW", 1

    # Safe fallback for unexpected findings
    if status in {"DEVIATION", "AMBIGUOUS"}:
        return "MEDIUM", 2

    return "LOW", 1
    findings.append({
        "category": category,
        "clause_type": clause_type,
        "status": status,
        "clause": clause,
        "explanation": explanation,
        "action": action
    })


# ---------------------------------------------------------
# Main deterministic review
# ---------------------------------------------------------

def review_lease(text):
    """
    Compare lease text against company standards.

    This function intentionally uses deterministic Python
    logic. Gemini will be added later for interpretation
    and explanations.
    """

    standards = load_standards()

    text_lower = text.lower()
    findings = []

    # -----------------------------------------------------
    # 1. Security deposit
    # -----------------------------------------------------

    deposit_clause = find_sentence(
        text,
        ["security deposit", "deposit"]
    )

    if deposit_clause is None:
        add_finding(
            findings,
            "missing",
            "security_deposit",
            "MISSING",
            "",
            "No security deposit clause was found in the agreement.",
            "Human review required."
        )
    else:
        months = extract_months(deposit_clause)

        if months is None:
            add_finding(
                findings,
                "deviation",
                "security_deposit",
                "AMBIGUOUS",
                deposit_clause,
                "A security deposit clause was found, but its amount could not be determined.",
                "Human review required."
            )

        elif (
            months >= standards["security_deposit"]["min_months"]
            and
            months <= standards["security_deposit"]["max_months"]
        ):
            add_finding(
                findings,
                "compliant",
                "security_deposit",
                "COMPLIANT",
                deposit_clause,
                f"The deposit of {months:g} month(s) is within the allowed range of "
                f"{standards['security_deposit']['min_months']}–"
                f"{standards['security_deposit']['max_months']} months.",
                "No action required."
            )

        else:
            add_finding(
                findings,
                "deviation",
                "security_deposit",
                "DEVIATION",
                deposit_clause,
                f"The agreement specifies {months:g} month(s), while the company "
                f"allows {standards['security_deposit']['min_months']}–"
                f"{standards['security_deposit']['max_months']} months.",
                "Human review required."
            )

    # -----------------------------------------------------
    # 2. Notice period
    # -----------------------------------------------------

    notice_clause = find_sentence(
        text,
        ["notice", "termination"]
    )

    if notice_clause is None:
        add_finding(
            findings,
            "missing",
            "notice_period",
            "MISSING",
            "",
            "No notice-period clause was found.",
            "Human review required."
        )
    else:
        days = extract_days(notice_clause)

        if days is None:
            add_finding(
                findings,
                "deviation",
                "notice_period",
                "AMBIGUOUS",
                notice_clause,
                "A notice or termination clause was found, but a notice period could not be determined.",
                "Human review required."
            )

        elif (
            days >= standards["notice_period"]["min_days"]
            and
            days <= standards["notice_period"]["max_days"]
        ):
            add_finding(
                findings,
                "compliant",
                "notice_period",
                "COMPLIANT",
                notice_clause,
                f"The notice period of {days:g} days is within the allowed "
                f"range of {standards['notice_period']['min_days']}–"
                f"{standards['notice_period']['max_days']} days.",
                "No action required."
            )

        else:
            add_finding(
                findings,
                "deviation",
                "notice_period",
                "DEVIATION",
                notice_clause,
                f"The agreement specifies {days:g} days, while the company "
                f"allows {standards['notice_period']['min_days']}–"
                f"{standards['notice_period']['max_days']} days.",
                "Human review required."
            )

    # -----------------------------------------------------
    # 3. Deposit return
    # -----------------------------------------------------

    deposit_return_clause = find_sentence(
        text,
        [
            "deposit shall be returned",
            "deposit will be returned",
            "security deposit shall be returned",
            "security deposit will be returned",
            "return the security deposit",
            "return of the deposit"
        ]
    )

    if deposit_return_clause is None:
        add_finding(
            findings,
            "missing",
            "deposit_return",
            "MISSING",
            "",
            "No clause specifying when the security deposit must be returned was found.",
            "Human review required."
        )
    else:
        days = extract_days(deposit_return_clause)

        if days is not None and days <= standards["deposit_return"]["max_days"]:
            add_finding(
                findings,
                "compliant",
                "deposit_return",
                "COMPLIANT",
                deposit_return_clause,
                f"The deposit return period of {days:g} days is within the "
                f"company limit of {standards['deposit_return']['max_days']} days.",
                "No action required."
            )
        elif days is not None:
            add_finding(
                findings,
                "deviation",
                "deposit_return",
                "DEVIATION",
                deposit_return_clause,
                f"The deposit return period of {days:g} days exceeds the "
                f"company limit of {standards['deposit_return']['max_days']} days.",
                "Human review required."
            )
        else:
            add_finding(
                findings,
                "deviation",
                "deposit_return",
                "AMBIGUOUS",
                deposit_return_clause,
                "A deposit return clause exists, but its timeline could not be determined.",
                "Human review required."
            )

    # -----------------------------------------------------
    # 4. Rent increase
    # -----------------------------------------------------

    rent_clause = find_sentence(
        text,
        ["rent", "increase", "escalat"]
    )

    if rent_clause is None:
        add_finding(
            findings,
            "missing",
            "rent_increase",
            "MISSING",
            "",
            "No rent-increase clause was found.",
            "Human review required."
        )
    else:
        percentage = extract_percentage(rent_clause)

        if percentage is None:
            add_finding(
                findings,
                "deviation",
                "rent_increase",
                "AMBIGUOUS",
                rent_clause,
                "A rent-related clause was found, but the permitted increase could not be determined.",
                "Human review required."
            )
        elif percentage <= standards["rent_increase"]["max_percent"]:
            add_finding(
                findings,
                "compliant",
                "rent_increase",
                "COMPLIANT",
                rent_clause,
                f"The stated increase of {percentage:g}% is within the company "
                f"maximum of {standards['rent_increase']['max_percent']}%.",
                "No action required."
            )
        else:
            add_finding(
                findings,
                "deviation",
                "rent_increase",
                "DEVIATION",
                rent_clause,
                f"The stated increase of {percentage:g}% exceeds the company "
                f"maximum of {standards['rent_increase']['max_percent']}%.",
                "Human review required."
            )

    # -----------------------------------------------------
    # 5. Maintenance
    # -----------------------------------------------------

    maintenance_clause = find_sentence(
        text,
        ["maintenance", "repairs", "repair"]
    )

    if maintenance_clause is None:
        add_finding(
            findings,
            "missing",
            "maintenance",
            "MISSING",
            "",
            "No maintenance responsibility clause was found.",
            "Human review required."
        )
    elif "landlord" in maintenance_clause.lower():
        add_finding(
            findings,
            "compliant",
            "maintenance",
            "COMPLIANT",
            maintenance_clause,
            "The agreement assigns maintenance or repair responsibility to the landlord.",
            "No action required."
        )
    else:
        add_finding(
            findings,
            "deviation",
            "maintenance",
            "AMBIGUOUS",
            maintenance_clause,
            "Maintenance is mentioned, but responsibility is not clearly assigned to the landlord.",
            "Human review required."
        )

    # -----------------------------------------------------
    # 6. Subletting
    # -----------------------------------------------------

    subletting_clause = find_sentence(
        text,
        ["sublet", "subletting"]
    )

    if subletting_clause is None:
        add_finding(
            findings,
            "missing",
            "subletting",
            "MISSING",
            "",
            "No subletting clause was found.",
            "Human review required."
        )
    elif (
        "written approval" in subletting_clause.lower()
        or
        "prior written" in subletting_clause.lower()
    ):
        add_finding(
            findings,
            "compliant",
            "subletting",
            "COMPLIANT",
            subletting_clause,
            "Subletting requires written approval.",
            "No action required."
        )
    else:
        add_finding(
            findings,
            "deviation",
            "subletting",
            "DEVIATION",
            subletting_clause,
            "The agreement permits or discusses subletting without clearly requiring written approval.",
            "Human review required."
        )

    # -----------------------------------------------------
    # 7. Late fee
    # -----------------------------------------------------

    late_fee_clause = find_sentence(
        text,
        ["late fee", "late charge", "delayed rent"]
    )

    if late_fee_clause is None:
        add_finding(
            findings,
            "missing",
            "late_fee",
            "MISSING",
            "",
            "No late-fee clause was found.",
            "Human review required."
        )
    else:
        percentage = extract_percentage(late_fee_clause)

        if percentage is None:
            add_finding(
                findings,
                "deviation",
                "late_fee",
                "AMBIGUOUS",
                late_fee_clause,
                "A late-fee clause exists, but its percentage could not be determined.",
                "Human review required."
            )
        elif percentage <= standards["late_fee"]["max_percent"]:
            add_finding(
                findings,
                "compliant",
                "late_fee",
                "COMPLIANT",
                late_fee_clause,
                f"The late fee of {percentage:g}% is within the company maximum "
                f"of {standards['late_fee']['max_percent']}%.",
                "No action required."
            )
        else:
            add_finding(
                findings,
                "deviation",
                "late_fee",
                "DEVIATION",
                late_fee_clause,
                f"The late fee of {percentage:g}% exceeds the company maximum "
                f"of {standards['late_fee']['max_percent']}%.",
                "Human review required."
            )

    # -----------------------------------------------------
    # 8. Early termination
    # -----------------------------------------------------

    termination_clause = find_sentence(
        text,
        ["terminate", "termination"]
    )

    if termination_clause is None:
        add_finding(
            findings,
            "missing",
            "early_termination",
            "MISSING",
            "",
            "No early-termination provision was found.",
            "Human review required."
        )
    elif "sole discretion" in termination_clause.lower():
        add_finding(
            findings,
            "deviation",
            "early_termination",
            "DEVIATION",
            termination_clause,
            "The agreement gives the landlord termination rights at its sole discretion.",
            "Human review required."
        )
    else:
        add_finding(
            findings,
            "compliant",
            "early_termination",
            "COMPLIANT",
            termination_clause,
            "A termination provision is present.",
            "No action required."
        )

    # -----------------------------------------------------
    # 9. Landlord identification
    # -----------------------------------------------------

    landlord_clause = find_sentence(
        text,
        ["landlord"]
    )

    if landlord_clause is None:
        add_finding(
            findings,
            "missing",
            "landlord_identification",
            "MISSING",
            "",
            "The agreement does not clearly identify a landlord.",
            "Human review required."
        )
    else:
        add_finding(
            findings,
            "compliant",
            "landlord_identification",
            "COMPLIANT",
            landlord_clause,
            "A landlord is identified in the agreement.",
            "No action required."
        )

    # -----------------------------------------------------
    # 10. Tenant identification
    # -----------------------------------------------------

    tenant_clause = find_sentence(
        text,
        ["tenant"]
    )

    if tenant_clause is None:
        add_finding(
            findings,
            "missing",
            "tenant_identification",
            "MISSING",
            "",
            "The agreement does not clearly identify a tenant.",
            "Human review required."
        )
    else:
        add_finding(
            findings,
            "compliant",
            "tenant_identification",
            "COMPLIANT",
            tenant_clause,
            "A tenant is identified in the agreement.",
            "No action required."
        )

    # -----------------------------------------------------
    # 11. Lease duration
    # -----------------------------------------------------

    duration_clause = find_sentence(
        text,
        ["lease term", "lease duration", "term shall"]
    )

    if duration_clause is None:
        add_finding(
            findings,
            "missing",
            "lease_duration",
            "MISSING",
            "",
            "No explicit lease duration was found.",
            "Human review required."
        )
    else:
        add_finding(
            findings,
            "compliant",
            "lease_duration",
            "COMPLIANT",
            duration_clause,
            "The agreement explicitly states a lease term.",
            "No action required."
        )

    # -----------------------------------------------------
    # Calculate summary
    # -----------------------------------------------------

    compliant = sum(
        1 for finding in findings
        if finding["category"] == "compliant"
    )

    deviations = sum(
        1 for finding in findings
        if finding["category"] == "deviation"
    )

    missing = sum(
        1 for finding in findings
        if finding["category"] == "missing"
    )

    if deviations == 0 and missing == 0:
        overall_status = "COMPLIANT"
    else:
        overall_status = "REQUIRES REVIEW"

    # -----------------------------------------------------
    # Calculate severity-based risk
    # -----------------------------------------------------

    severity_counts = {
        "critical": 0,
        "high": 0,
        "medium": 0,
        "low": 0
    }

    risk_points = 0

    for finding in findings:

        severity, points = calculate_severity(finding)

        finding["severity"] = severity
        finding["risk_points"] = points

        if severity.lower() in severity_counts:
            severity_counts[severity.lower()] += 1

        risk_points += points

    total_checks = len(findings)

    max_possible_risk = total_checks * 4

    if max_possible_risk > 0:
        risk_score = round(
            (risk_points / max_possible_risk) * 100
        )
    else:
        risk_score = 0

    # Determine overall risk level
    if risk_score >= 60:
        risk_level = "HIGH RISK"
    elif risk_score >= 30:
        risk_level = "MEDIUM RISK"
    elif risk_score > 0:
        risk_level = "LOW RISK"
    else:
        risk_level = "NO MATERIAL RISK"

    return {
        "overall_status": overall_status,

        "summary": {
            "compliant": compliant,
            "deviations": deviations,
            "missing": missing,
            "total_checks": total_checks
        },

        "risk": {
            "score": risk_score,
            "level": risk_level,
            "points": risk_points,
            "severity_counts": severity_counts
        },

        "findings": findings
    }