<<<<<<< HEAD

TRACK_ID=PS05

# LeaseGuard AI

## Evidence-First Lease Agreement Review Assistant

LeaseGuard AI is an AI-assisted lease agreement review system designed for the legal desk of a property management company.

It reviews lease agreements against configurable company standards and produces an evidence-first review report.

The system identifies:

- Clauses that match company standards
- Deviations from acceptable company positions
- Missing required protections
- Severity of findings
- A severity-based risk indicator
- Plain-language explanations using Gemini
- Recommended actions for a human reviewer

LeaseGuard AI does not approve or reject agreements. The deterministic Rule Engine performs the policy checks, Gemini explains the findings, and the human reviewer makes the final decision.

---

# Problem

Property management companies review many lease agreements every month.

Important terms such as security deposits, notice periods, maintenance responsibilities, deposit-return timelines, rent increases, subletting and termination conditions can vary between agreements.

Manual review can be time-consuming and important deviations or missing protections can be overlooked.

LeaseGuard AI helps the legal desk identify these issues consistently by comparing the agreement against configurable company standards and presenting evidence for every finding.

---

# Solution

LeaseGuard AI combines deterministic policy checking with Generative AI.

The system:

1. Accepts a lease agreement as a PDF or lease text.
2. Extracts readable text from the document.
3. Checks the agreement against company standards using a deterministic Rule Engine.
4. Identifies compliant clauses, deviations and missing protections.
5. Quotes the relevant evidence from the lease.
6. Assigns severity and a severity-based risk indicator.
7. Uses Gemini to explain the deterministic findings in plain language.
8. Provides recommended actions for the human reviewer.
9. Leaves the final business or legal decision to the human reviewer.

---

# Core Approach

```text
                 LEASE AGREEMENT
                        |
                        v
                   PDF PARSER
                        |
                        v
              DETERMINISTIC RULE
                    ENGINE
                        |
          +-------------+-------------+
          |             |             |
          v             v             v
       Evidence      Findings      Severity
          |             |             |
          +-------------+-------------+
                        |
                        v
                    GEMINI AI
                 Explanation Layer
                        |
                        v
               Reviewer Guidance
                        |
                        v
                 HUMAN REVIEWER
````

## Key Design Principle

> The Rule Engine determines the finding, Gemini explains it, and the human reviewer makes the final decision.

---

# Features

## 1. Lease Document Input

The application accepts a lease agreement as a PDF.

It extracts readable text from the document before performing the review.

A lease agreement can also be entered as text for testing and demonstration.

---

## 2. Deterministic Policy Review

The Rule Engine compares lease clauses against configurable company standards.

The current configured standards include:

* Security deposit: 1–3 months of rent
* Notice period: 30–60 days
* Deposit return: within 30 days
* Annual rent increase: maximum 5%
* Maintenance responsibility
* Written approval for subletting
* Late fee: maximum 5%
* Early termination conditions
* Landlord identification
* Tenant identification
* Explicit lease duration

These standards are stored separately from the AI explanation layer.

---

## 3. Evidence-First Findings

Every finding is connected to evidence from the lease agreement.

The review displays:

* Evidence from the lease
* Company standard
* Rule Engine assessment
* Finding status
* Severity
* Risk weight

This allows a reviewer to trace the finding back to the agreement instead of relying only on an AI-generated conclusion.

---

## 4. Deviation Detection

LeaseGuard identifies clauses that do not match the configured company standards.

For example:

```text
Lease clause:
Security deposit equal to six months of rent.

Company standard:
Security deposit should be between one and three months.

Result:
DEVIATION
```

The system explains the difference between the agreement and the company position.

---

## 5. Missing Protection Detection

LeaseGuard does not only search for problematic clauses.

It also identifies required protections that are missing from the agreement.

For example:

```text
Check:
Deposit return timeline

Result:
MISSING

Reason:
No required deposit return timeline was identified
in the agreement.
```

Silence in the agreement is therefore treated as a finding rather than being ignored.

---

## 6. Severity Classification

Findings are assigned severity based on their configured policy importance.

The system uses:

* Critical
* High
* Medium
* Low

Severity is used to help the reviewer prioritize findings.

---

## 7. Severity-Based Risk Indicator

LeaseGuard provides an internal severity-based risk indicator.

The dashboard displays:

* Overall risk indicator
* Risk level
* Critical findings
* High findings
* Medium findings
* Low findings
* Total issues

The risk indicator is intended for internal review prioritization.

It is not a legal validity score or a prediction of legal outcomes.

---

## 8. Gemini AI Explanation

Gemini is used as an explanation layer.

The deterministic findings are provided to Gemini so it can produce:

* Plain-language explanations
* Practical risk context
* Recommended reviewer actions
* Confidence level

Gemini does not determine whether a clause is compliant.

The Rule Engine remains responsible for the policy evaluation.

---

## 9. Human-in-the-Loop Review

LeaseGuard AI does not approve or reject lease agreements.

The system flags and explains issues for a human reviewer.

The reviewer remains responsible for the final business or legal decision.

```text
AI assists the reviewer.
Human review remains the final decision.
```

---

## 10. Graceful AI Failure Handling

If Gemini becomes temporarily unavailable or its API quota is exhausted, LeaseGuard does not stop the deterministic policy review.

The Rule Engine continues to provide:

* Policy findings
* Evidence
* Severity
* Risk assessment

AI-generated explanations are not presented when Gemini cannot safely provide them.

This keeps the core review workflow available even when the AI explanation layer is unavailable.

---

# Technology Stack

## Backend

* Python
* Python HTTP Server
* pypdf

## AI

* Google Gemini API
* Gemini model for natural-language explanation

## Frontend

* HTML
* CSS
* JavaScript

The frontend is served directly by the Python application.

No separate frontend server or build command is required.

---

# Project Architecture

```text
leaseguard-ai/
│
├── app.py
├── requirements.txt
├── README.md
│
├── src/
│   ├── parser.py
│   ├── rules.py
│   ├── reviewer.py
│   └── gemini_client.py
│
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── app.js
│
└── data/
    ├── company_standards.json
    └── sample_leases/
        ├── clean_lease.txt
        └── difficult_lease.txt
```

---

# Generated Data and Documents

No external dataset is provided for this problem statement.

LeaseGuard AI uses its own small set of company standards and sample lease documents.

## Company Standards

File:

```text
data/company_standards.json
```

This file contains the configurable company policy positions used by the deterministic Rule Engine.

Examples include:

* Acceptable security deposit range
* Acceptable notice period
* Deposit return timeline
* Maximum rent increase
* Maintenance responsibility
* Subletting requirements
* Late fee limit
* Early termination requirements
* Required party identification
* Required lease duration

---

## Sample Lease Documents

### Clean Lease

File:

```text
data/sample_leases/clean_lease.txt
```

This document is designed to match the configured company standards and demonstrate a clean review result.

### Difficult Lease

File:

```text
data/sample_leases/difficult_lease.txt
```

This document contains multiple deviations and missing protections and is used to demonstrate the review workflow.

---

# How to Run

## Requirements

Python 3.11 or a compatible Python environment.

## 1. Install Dependencies

From the repository root:

```bash
pip install -r requirements.txt
```

## 2. Configure Gemini API Key

The Gemini API key must be provided through the `GEMINI_API_KEY` environment variable.

### Windows PowerShell

```powershell
$env:GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
```

### Linux / macOS

```bash
export GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
```

The API key must never be committed to the repository.

## 3. Start the Application

From the repository root:

```bash
python app.py
```

The application starts at:

```text
http://localhost:8000
```

No second terminal, separate frontend server or build command is required.

---

# Demo Workflow

The application demonstrates both a normal case and a difficult case.

## Normal Case

A lease agreement matching the configured company standards is reviewed.

The expected result is a clean review without material deviations.

The system should clearly show that no unnecessary issues are being flagged.

---

## Difficult Case

The difficult lease demonstrates several types of issues, including:

* Excessive security deposit
* Rent increase above the company limit
* Notice period outside the configured range
* Ambiguous maintenance responsibility
* Missing deposit return timeline
* Subletting without required written approval
* Excessive late fee
* Broad early termination rights

For each issue, LeaseGuard provides evidence from the agreement and compares it with the configured company standard.

The dashboard then helps the reviewer prioritize findings based on severity.

---

# Example Review Flow

```text
Upload Lease
     |
     v
Extract Agreement Text
     |
     v
Check Company Standards
     |
     v
Identify:
  - Compliant clauses
  - Deviations
  - Missing protections
     |
     v
Show Exact Evidence
     |
     v
Assign Severity
     |
     v
Calculate Risk Indicator
     |
     v
Gemini Explains Findings
     |
     v
Reviewer Verifies Findings
     |
     v
Human Makes Final Decision
```

---

# Design Decisions

## Why a Deterministic Rule Engine?

Some lease policy checks are based on explicit company positions and numerical thresholds.

Examples include:

* Deposit ranges
* Notice-period ranges
* Maximum rent increases
* Late-fee limits
* Required protections

These checks should be predictable and reproducible.

Therefore, the Rule Engine performs the actual company-policy evaluation.

---

## Why Gemini?

Gemini is used where natural-language generation provides value.

It helps transform deterministic findings into concise explanations that are easier for a human reviewer to understand.

Gemini provides:

* Explanation
* Risk context
* Reviewer-oriented guidance
* Confidence

It does not override the Rule Engine.

---

## Why Human Review?

Lease agreements can contain ambiguous language and business-specific considerations.

Therefore, LeaseGuard AI assists the reviewer rather than making the final legal or business decision.

The system flags and explains.

The human reviewer decides.

---

# Evidence and Grounding

LeaseGuard follows an evidence-first approach.

The Rule Engine produces findings based on the agreement and configured company standards.

The AI explanation layer receives the deterministic findings and their supporting evidence.

The system is designed so that AI-generated explanations do not replace the underlying evidence.

When sufficient information is not available, the system should avoid inventing a clause, number, date, amount, obligation or other contract fact.

---

# Error Handling

The application handles common input and AI failures gracefully.

Examples include:

* Empty lease input
* Invalid JSON requests
* Invalid PDF data
* Non-PDF uploads
* PDFs larger than the supported size
* PDFs without readable text
* Gemini API errors
* Gemini quota exhaustion
* Invalid Gemini JSON responses

When Gemini is unavailable, the deterministic Rule Engine remains available for human review.

---

# Limitations

The current prototype focuses on a defined set of lease-policy checks.

It is not a replacement for professional legal advice or legal review.

Scanned or image-only PDFs without readable text may require OCR before analysis.

The configured company standards are demonstration policies and should be replaced with organization-approved standards in a production deployment.

The severity-based risk indicator is an internal prioritization mechanism and should not be interpreted as a legal validity score.

---

# Future Improvements

Potential future improvements include:

* OCR support for scanned lease documents
* More configurable company policy rules
* Clause-level document highlighting
* Versioned company standards
* Reviewer approval and audit history
* Multi-company policy configurations
* More sophisticated clause extraction
* Local vector retrieval over larger policy libraries
* Authentication and role-based access
* Enterprise document management integration

---

# Demo Video

Demo video:

PASTE_YOUR_DEMO_VIDEO_LINK_HERE

---

# Final Statement

LeaseGuard AI is built around a simple evidence-first workflow:

> **The Rule Engine determines the finding. Gemini explains it. The human reviewer decides.**

LeaseGuard AI helps legal operations teams review lease agreements faster, more consistently and with traceable evidence while keeping the final decision with a human reviewer.

````

### Do this now ❤️

**VS Code → `README.md` → select all → paste the entire content above → Save.**

Then only change:

```text
PASTE_YOUR_DEMO_VIDEO_LINK_HERE
````

to your actual demo video link.

=======
# leaseguard-ai
>>>>>>> 93113cf3dfa42d1884d7671fc62f705a6591a37d
