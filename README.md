TRACK_ID=PS05

# LeaseGuard AI

Evidence-First Lease Agreement Review Assistant

## Problem

Lease agreements contain important financial, operational, and legal terms. Manual review can be slow and inconsistent, especially when agreements contain unusual clauses, missing protections, or terms outside company policy.

LeaseGuard AI helps a human reviewer identify these issues quickly.

## Solution

LeaseGuard AI reviews a lease agreement against predefined company standards.

The system:

1. Extracts the lease text.
2. Checks important clauses using a deterministic Rule Engine.
3. Identifies compliant clauses.
4. Detects deviations from company standards.
5. Detects missing required protections.
6. Shows the exact lease evidence for every finding.
7. Uses Gemini to explain the findings in plain language.
8. Assigns severity and an internal risk indicator.
9. Gives the human reviewer a recommended action.
10. Keeps the human reviewer as the final decision maker.

## Core Architecture

Lease PDF or Text

↓

Text Parser

↓

Clause and Evidence Extraction

↓

Company Standards

↓

Deterministic Rule Engine

↓

Gemini Explanation Layer

↓

Risk and Severity Assessment

↓

Human Review Report

## Key Features

### PDF and Text Input

Users can upload a PDF lease agreement or paste the agreement text directly.

### Deterministic Rule Engine

Important compliance decisions are made using Python rules instead of allowing the language model to decide whether a clause passes or fails.

### Compliance Detection

The system identifies clauses that match company standards.

### Deviation Detection

The system identifies clauses that differ from company standards.

### Missing Protection Detection

The system also checks whether required protections are completely absent from the agreement.

### Evidence-First Findings

Every finding contains the relevant lease evidence.

The reviewer can see:

- Lease evidence
- Company standard
- Deterministic rule
- Finding status
- Severity
- Risk points
- Gemini explanation
- Recommended reviewer action

### Risk and Severity

Findings are classified as:

- Critical
- High
- Medium
- Low

The system also calculates an internal risk indicator based on the severity of findings.

This is not a legal risk score.

### Gemini Explanation

Gemini is used as an explanation layer.

The Rule Engine determines the finding.

Gemini explains the finding.

The human reviewer makes the final decision.

### Human-in-the-Loop

LeaseGuard AI does not approve or reject agreements automatically.

It assists the reviewer by identifying issues and providing evidence.

## Company Standards

The current demo company policy contains the following example standards:

| Clause | Company Standard |
| --- | --- |
| Security Deposit | 1 to 3 months rent |
| Notice Period | 30 to 60 days |
| Deposit Return | Within 30 days |
| Rent Increase | Maximum 5 percent annually |
| Maintenance | Required responsibility clause |
| Subletting | Written approval required |
| Late Fee | Maximum 5 percent |
| Early Termination | Required |
| Landlord Identification | Required |
| Tenant Identification | Required |
| Lease Duration | Required |

These standards are stored in:

data/company_standards.json

## Technology Stack

Backend:

- Python
- Python HTTP Server
- pypdf

AI:

- Google Gemini API
- Gemini Flash
- Gemini embeddings can be integrated for future retrieval improvements

Frontend:

- HTML
- CSS
- JavaScript

Storage:

- Local JSON data
- Local sample lease documents

## Project Structure

leaseguard-ai/

    app.py

    requirements.txt

    README.md

    data/

        company_standards.json

        sample_leases/

            clean_lease.txt

            difficult_lease.txt

    src/

        parser.py

        rules.py

        reviewer.py

        gemini_client.py

    frontend/

        index.html

        style.css

        app.js

## Generated Data and Documents

The repository includes generated demonstration data:

- Company standards
- Clean lease example
- Difficult lease example

These files allow the application to be tested immediately after installation.

## Running the Project

Requirements:

- Python 3.11 or compatible Python version
- Gemini API key

Set the Gemini API key as an environment variable.

Windows PowerShell:

    $env:GEMINI_API_KEY="YOUR_GEMINI_API_KEY"

Install dependencies:

    pip install -r requirements.txt

Start the application:

    python app.py

Open:

    http://localhost:8000

## Demo Workflow

1. Open LeaseGuard AI.
2. Upload a lease PDF or paste lease text.
3. Click Review Agreement.
4. The Rule Engine evaluates the agreement.
5. The dashboard displays compliant clauses, deviations, and missing protections.
6. Review the evidence for each finding.
7. Read Gemini's explanation.
8. Follow the recommended reviewer action.
9. Make the final decision as a human reviewer.

The difficult demo lease is included in:

data/sample_leases/difficult_lease.txt

## Design Decisions

### Why a Rule Engine?

Important policy decisions should be deterministic.

This reduces the chance of an AI model changing a compliance decision.

### Why Gemini?

Gemini provides natural-language explanations that make deterministic findings easier for reviewers to understand.

### Why Evidence First?

Legal review requires traceability.

Every finding should be connected to evidence from the agreement rather than being based on an unsupported AI statement.

### Why Human Review?

LeaseGuard AI is an assistant, not an autonomous legal decision maker.

The final decision remains with the human reviewer.

## Grounding and Safety

Gemini receives the deterministic findings and their supporting evidence.

The AI prompt instructs Gemini to:

- Use only the provided evidence.
- Never invent clauses or facts.
- Never change the deterministic finding.
- Explain missing protections as missing.
- Explain deviations using the lease evidence and company standard.
- Avoid legal advice.
- Escalate to the human reviewer when evidence is insufficient.

If Gemini is unavailable or its response cannot be safely interpreted, the deterministic Rule Engine remains available for human review.

## Error Handling

The application handles:

- Empty lease text
- Invalid JSON requests
- Invalid PDF data
- Oversized PDF files
- PDFs without readable text
- Missing Gemini API key
- Gemini API failures
- Gemini quota exhaustion
- Invalid Gemini responses

## Limitations

This is a hackathon prototype.

It is not a replacement for legal counsel.

The company standards used in the demonstration are example policy values and should be replaced with organization-specific policies before production use.

Scanned image-only PDFs currently require OCR support for reliable text extraction.

## Future Improvements

Potential improvements include:

- OCR for scanned agreements
- More advanced clause extraction
- Local vector retrieval using Gemini embeddings
- More company policy categories
- Clause-level confidence scoring
- Reviewer feedback and audit history
- Exportable review reports
- Multi-document comparison
- Version tracking for company standards


## Final Statement

LeaseGuard AI is designed around one principle:

The Rule Engine determines the finding.

Gemini explains the finding.

The human reviewer makes the final decision.