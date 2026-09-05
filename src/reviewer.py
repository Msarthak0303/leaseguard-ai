import json

from .rules import review_lease
from .gemini_client import ask_gemini


def build_ai_prompt(lease_text, findings):
    findings_json = json.dumps(
        findings,
        ensure_ascii=False,
        indent=2
    )

    return f"""
You are an AI assistant helping a human reviewer analyze a lease agreement.

Your job is to EXPLAIN deterministic findings.
You are NOT the rule engine.

STRICT GROUNDING RULES:

1. Treat EACH finding as completely independent.

2. For a finding, use ONLY:
   - that finding's evidence
   - that finding's expected company standard
   - that finding's deterministic explanation
   - that finding's status
   - the lease text only to understand the quoted evidence

3. NEVER mix evidence from one finding with another finding.

4. NEVER discuss a different clause than the one identified by
   the finding.

5. NEVER invent a clause, number, date, amount, party, right,
   obligation, or fact.

6. NEVER change the deterministic status.

7. If the finding is MISSING, explain that the required protection
   was not found in the lease.

8. If the finding is a DEVIATION, explicitly explain:
   - what the lease says
   - what the company standard expects
   - why they differ

9. If the finding is COMPLIANT, explain briefly why the evidence
   matches the company standard.

10. Every explanation MUST refer directly to the provided evidence.

11. If the evidence is insufficient, say:
    "The available evidence is insufficient to determine this."

12. Do NOT approve or reject the lease.

13. Do NOT provide legal advice.

14. The human reviewer makes the final decision.

15. Keep each explanation concise and practical.

LEASE TEXT:
{lease_text}

DETERMINISTIC FINDINGS:
{findings_json}

IMPORTANT:

The findings above are already evaluated by the deterministic
Rule Engine.

Your task is ONLY to provide supporting explanations.

For EACH finding, return exactly one AI result.

Return ONLY valid JSON in this format:

{{
  "findings": [
    {{
      "finding_index": 0,
      "ai_explanation": "Explain ONLY this finding using its evidence.",
      "risk": "Explain ONLY the practical concern created by this finding.",
      "reviewer_action": "Tell the human reviewer exactly what should be verified for this finding.",
      "confidence": "HIGH"
    }}
  ]
}}

OUTPUT RULES:

- finding_index MUST match the original finding index.
- Start indexing from 0.
- Return one result for every finding.
- Do not skip findings.
- Do not reorder findings.
- confidence must be exactly HIGH, MEDIUM, or LOW.
- Do not include markdown.
- Do not include ``` fences.
- Return JSON only.
"""


def parse_ai_response(response_text):
    if not response_text:
        return {}

    text = response_text.strip()

    # Remove markdown code fences if Gemini adds them
    if text.startswith("```"):
        lines = text.splitlines()

        if lines:
            lines = lines[1:]

        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]

        text = "\n".join(lines).strip()

    # First attempt: direct JSON parsing
    try:
        return json.loads(text)

    except json.JSONDecodeError:
        pass

    # Second attempt: extract JSON object from surrounding text
    start = text.find("{")
    end = text.rfind("}")

    if start != -1 and end != -1 and end > start:
        try:
            return json.loads(
                text[start:end + 1]
            )

        except json.JSONDecodeError:
            pass

    return {}


def apply_ai_results(findings, ai_data):
    ai_findings = ai_data.get(
        "findings",
        []
    )

    if not isinstance(
        ai_findings,
        list
    ):
        return findings

    for ai_item in ai_findings:

        if not isinstance(
            ai_item,
            dict
        ):
            continue

        try:
            index = int(
                ai_item.get(
                    "finding_index",
                    -1
                )
            )

        except (
            TypeError,
            ValueError
        ):
            continue

        # Ignore invalid finding indexes
        if (
            index < 0
            or index >= len(findings)
        ):
            continue

        finding = findings[index]

        # AI explanation
        finding["ai_explanation"] = str(
            ai_item.get(
                "ai_explanation",
                "No AI explanation was returned."
            )
        )

        # AI risk context
        finding["ai_risk"] = str(
            ai_item.get(
                "risk",
                "No additional AI risk explanation was returned."
            )
        )

        # Recommended reviewer action
        finding["ai_reviewer_action"] = str(
            ai_item.get(
                "reviewer_action",
                "Verify this finding before making a final decision."
            )
        )

        # Confidence
        confidence = str(
            ai_item.get(
                "confidence",
                "MEDIUM"
            )
        ).upper()

        if confidence not in {
            "HIGH",
            "MEDIUM",
            "LOW"
        }:
            confidence = "MEDIUM"

        finding["ai_confidence"] = confidence

        finding["ai_status"] = "AI ANALYZED"

    return findings


def enrich_findings_with_ai(
    lease_text,
    findings
):
    """
    Send the complete lease and deterministic findings
    to Gemini in ONE request.

    Gemini only explains the findings.
    The deterministic Rule Engine remains responsible
    for compliance decisions.
    """

    if not findings:
        return findings

    try:

        print(
            "GEMINI: Starting lease-wide analysis..."
        )

        prompt = build_ai_prompt(
            lease_text,
            findings
        )

        # ONE Gemini request for the complete lease
        ai_response = ask_gemini(
            prompt
        )

        ai_data = parse_ai_response(
            ai_response
        )

        if not ai_data:

            print(
                "GEMINI ERROR: Invalid JSON response."
            )

            for finding in findings:

                finding["ai_explanation"] = (
                    "Gemini returned a response "
                    "that could not be safely interpreted."
                )

                finding["ai_status"] = (
                    "AI RESPONSE INVALID"
                )

            return findings

        findings = apply_ai_results(
            findings,
            ai_data
        )

        # Detect findings Gemini failed to explain
        for finding in findings:

            if "ai_explanation" not in finding:

                finding["ai_explanation"] = (
                    "Gemini did not return an explanation "
                    "for this finding."
                )

                finding["ai_status"] = (
                    "AI RESPONSE INCOMPLETE"
                )

        print(
            "GEMINI: Lease-wide analysis completed."
        )

    except Exception as exc:

        error_text = str(exc)

        print(
            "GEMINI ERROR:",
            repr(exc)
        )

        # Gemini quota/rate-limit handling
        if (
            "429" in error_text
            or "RESOURCE_EXHAUSTED" in error_text
            or "quota" in error_text.lower()
        ):

            message = (
                "Gemini analysis is temporarily unavailable "
                "because the API quota has been exhausted."
            )

            status = (
                "AI QUOTA EXHAUSTED"
            )

        else:

            message = (
                "Gemini analysis is temporarily unavailable. "
                "The deterministic Rule Engine remains active "
                "for human review."
            )

            status = (
                "AI UNAVAILABLE"
            )

        for finding in findings:

            finding["ai_explanation"] = message

            finding["ai_status"] = status

            finding["ai_error"] = error_text

    return findings


def review_text(lease_text):

    if (
        not lease_text
        or not lease_text.strip()
    ):

        return {
            "overall_status": "ERROR",

            "summary": {
                "compliant": 0,
                "deviations": 0,
                "missing": 0,
                "total_checks": 0
            },

            "findings": [],

            "error": (
                "No lease agreement text was provided."
            )
        }

    # ============================================================
    # STEP 1: DETERMINISTIC RULE ENGINE
    # ============================================================

    result = review_lease(
        lease_text
    )

    findings = result.get(
        "findings",
        []
    )

    # ============================================================
    # STEP 2: GEMINI AI EXPLANATION
    # ============================================================

    # Gemini does NOT decide compliance.
    # Gemini only explains the deterministic findings.

    findings = enrich_findings_with_ai(
        lease_text,
        findings
    )

    # ============================================================
    # STEP 3: FINAL RESULT
    # ============================================================

    result["findings"] = findings

    return result