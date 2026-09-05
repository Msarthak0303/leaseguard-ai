const leaseFile = document.getElementById("leaseFile");
const fileName = document.getElementById("fileName");
const leaseText = document.getElementById("leaseText");

const loadDemoButton = document.getElementById("loadDemo");
const clearTextButton = document.getElementById("clearText");
const reviewButton = document.getElementById("reviewButton");

const loading = document.getElementById("loading");
const resultsContainer = document.getElementById("results");

const overallStatus = document.getElementById("overallStatus");

const compliantCount = document.getElementById("compliantCount");
const deviationCount = document.getElementById("deviationCount");
const missingCount = document.getElementById("missingCount");
const totalCount = document.getElementById("totalCount");

const findingsContainer = document.getElementById("findings");


// ============================================================
// DIFFICULT DEMO LEASE
// ============================================================

const difficultDemo = `
LEASE AGREEMENT

This Lease Agreement is entered into between ABC Properties ("Landlord")
and John Smith ("Tenant").

1. TERM
The lease shall remain in effect for a period of three years.

2. RENT
The monthly rent shall be INR 50,000.

3. SECURITY DEPOSIT
The Tenant shall pay a security deposit equal to six months of rent.

4. RENT INCREASE
The Landlord may increase the rent by 8% every year.

5. NOTICE PERIOD
The Tenant must provide 90 days written notice before termination.

6. MAINTENANCE
The Tenant shall maintain the premises and keep the property in good
condition. The agreement does not clearly specify responsibility for
structural repairs.

7. DEPOSIT RETURN
The agreement does not specify a timeline for returning the security deposit.

8. SUBLETTING
The Tenant may sublet the premises without obtaining written approval
from the Landlord.

9. LATE PAYMENT
A late payment fee of 7% of the monthly rent will apply.

10. EARLY TERMINATION
The Landlord may terminate the agreement at its sole discretion.
The Tenant does not have a clearly defined corresponding termination right.

11. LIABILITY
The Tenant agrees to waive all claims against the Landlord regardless
of the circumstances.

12. PARTIES
Landlord: ABC Properties
Tenant: John Smith
`;


// ============================================================
// LOAD DEMO
// ============================================================

loadDemoButton.addEventListener(
    "click",
    () => {

        leaseText.value =
            difficultDemo;

        fileName.textContent =
            "Difficult demo lease loaded";

        resultsContainer.classList.add(
            "hidden"
        );
    }
);


// ============================================================
// CLEAR
// ============================================================

clearTextButton.addEventListener(
    "click",
    () => {

        leaseText.value = "";

        leaseFile.value = "";

        fileName.textContent =
            "No file selected";

        resultsContainer.classList.add(
            "hidden"
        );

        findingsContainer.innerHTML =
            "";

        removeRiskDashboard();

        compliantCount.textContent =
            "0";

        deviationCount.textContent =
            "0";

        missingCount.textContent =
            "0";

        totalCount.textContent =
            "0";

        overallStatus.textContent =
            "";
    }
);


// ============================================================
// FILE NAME
// ============================================================

leaseFile.addEventListener(
    "change",
    () => {

        if (leaseFile.files.length > 0) {

            fileName.textContent =
                leaseFile.files[0].name;

        } else {

            fileName.textContent =
                "No file selected";
        }
    }
);


// ============================================================
// REVIEW
// ============================================================

reviewButton.addEventListener(
    "click",
    async () => {

        const selectedFile =
            leaseFile.files[0];

        const text =
            leaseText.value.trim();


        if (!selectedFile && !text) {

            alert(
                "Please upload a PDF, paste a lease agreement, or load the demo."
            );

            return;
        }


        setLoading(true);


        try {

            let result;


            if (selectedFile) {

                if (
                    selectedFile.type !== "application/pdf"
                    &&
                    !selectedFile.name
                        .toLowerCase()
                        .endsWith(".pdf")
                ) {

                    alert(
                        "Please select a PDF file."
                    );

                    return;
                }


                const base64 =
                    await fileToBase64(
                        selectedFile
                    );


                result =
                    await reviewPDF(
                        selectedFile.name,
                        base64
                    );

            } else {

                result =
                    await reviewText(
                        text
                    );
            }


            displayResults(
                result
            );

        } catch (error) {

            console.error(error);

            alert(
                "Review failed: " +
                error.message
            );

        } finally {

            setLoading(false);
        }
    }
);


// ============================================================
// TEXT API
// ============================================================

async function reviewText(text) {

    const response =
        await fetch(
            "/api/review",
            {
                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body: JSON.stringify({
                    text: text
                })
            }
        );


    const data =
        await response.json();


    if (!response.ok) {

        throw new Error(
            data.error ||
            "Text review failed."
        );
    }


    return data;
}


// ============================================================
// PDF API
// ============================================================

async function reviewPDF(
    filename,
    base64
) {

    const response =
        await fetch(
            "/api/upload",
            {
                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body: JSON.stringify({
                    filename: filename,
                    file: base64
                })
            }
        );


    const data =
        await response.json();


    if (!response.ok) {

        throw new Error(
            data.error ||
            "PDF review failed."
        );
    }


    return data;
}


// ============================================================
// FILE TO BASE64
// ============================================================

function fileToBase64(file) {

    return new Promise(
        (resolve, reject) => {

            const reader =
                new FileReader();


            reader.onload =
                () => {

                    const result =
                        reader.result;

                    const base64 =
                        result.split(",")[1];

                    resolve(base64);
                };


            reader.onerror =
                () => {

                    reject(
                        new Error(
                            "Could not read PDF file."
                        )
                    );
                };


            reader.readAsDataURL(
                file
            );
        }
    );
}


// ============================================================
// LOADING
// ============================================================

function setLoading(isLoading) {

    if (isLoading) {

        loading.classList.remove(
            "hidden"
        );

        reviewButton.disabled =
            true;

        reviewButton.textContent =
            "⏳ Reviewing Agreement...";

    } else {

        loading.classList.add(
            "hidden"
        );

        reviewButton.disabled =
            false;

        reviewButton.textContent =
            "🔍 Review Agreement";
    }
}


// ============================================================
// DISPLAY RESULTS
// ============================================================

function displayResults(data) {

    resultsContainer.classList.remove(
        "hidden"
    );


    if (data.error) {

        alert(data.error);

        return;
    }


    const summary =
        data.summary || {};

    const findings =
        data.findings || [];

    const status =
        data.overall_status ||
        "UNKNOWN";


    // --------------------------------------------------------
    // COUNTS
    // --------------------------------------------------------

    compliantCount.textContent =
        summary.compliant || 0;

    deviationCount.textContent =
        summary.deviations || 0;

    missingCount.textContent =
        summary.missing || 0;

    totalCount.textContent =
        summary.total_checks ||
        findings.length ||
        0;


    // --------------------------------------------------------
    // STATUS
    // --------------------------------------------------------

    overallStatus.textContent =
        status.replaceAll(
            "_",
            " "
        );


    if (
        status === "COMPLIANT"
        ||
        status === "CLEAN"
    ) {

        overallStatus.style.background =
            "var(--success-bg)";

        overallStatus.style.color =
            "var(--success-text)";

    } else {

        overallStatus.style.background =
            "var(--danger-bg)";

        overallStatus.style.color =
            "var(--danger-text)";
    }


    // --------------------------------------------------------
    // FINDINGS
    // --------------------------------------------------------

    findingsContainer.innerHTML =
        "";


    if (findings.length === 0) {

        findingsContainer.innerHTML = `
            <div class="finding">

                <h3>
                    No findings available
                </h3>

                <p>
                    No review findings were returned.
                </p>

            </div>
        `;

    } else {

        findings.forEach(
            (finding, index) => {

                addFinding(
                    finding,
                    index
                );
            }
        );
    }


    // --------------------------------------------------------
    // RISK DASHBOARD
    // --------------------------------------------------------

    addRiskDashboard(
        summary,
        findings,
        status,
        data.risk
    );


    resultsContainer.scrollIntoView({
        behavior: "smooth",
        block: "start"
    });
}


// ============================================================
// ADD FINDING
// ============================================================

function addFinding(
    finding,
    index
) {

    const statusText =
        String(
            finding.status ||
            "UNKNOWN"
        );


    const severityText =
        String(
            finding.severity ||
            "UNKNOWN"
        );


    const riskPoints =
        Number(
            finding.risk_points ||
            0
        );


    let badgeClass =
        "badge-missing";


    const upperStatus =
        statusText.toUpperCase();


    if (
        upperStatus.includes(
            "COMPLIANT"
        )
    ) {

        badgeClass =
            "badge-compliant";

    } else if (
        upperStatus.includes(
            "DEVIATION"
        )
    ) {

        badgeClass =
            "badge-deviation";

    } else if (
        upperStatus.includes(
            "MISSING"
        )
    ) {

        badgeClass =
            "badge-missing";
    }


    const isCompliant =
        severityText.toUpperCase() ===
        "COMPLIANT";


    const findingElement =
        document.createElement(
            "div"
        );


    findingElement.className =
        "finding professional-finding";


    findingElement.innerHTML = `

        <div class="finding-header">

            <div>

                <span class="finding-number">
                    Finding ${index + 1}
                </span>

                <h3>
                    ${escapeHtml(
                        finding.check ||
                        "Agreement Check"
                    )}
                </h3>

            </div>


            <div class="finding-badges">

                <span class="badge ${badgeClass}">
                    ${escapeHtml(
                        statusText
                    )}
                </span>


                ${
                    !isCompliant
                    ?
                    `
                        <span class="severity-badge">
                            ${escapeHtml(
                                severityText
                            )}
                        </span>
                    `
                    :
                    ""
                }

            </div>

        </div>


        ${
            !isCompliant
            ?
            `
                <div class="risk-weight">
                    Risk Weight:
                    ${riskPoints}
                </div>
            `
            :
            ""
        }


        <div class="evidence">

            <strong>
                📌 Evidence from Lease
            </strong>

            <div class="evidence-text">

                ${
                    escapeHtml(
                        finding.evidence ||
                        "No direct clause evidence available."
                    )
                }

            </div>

        </div>


        <div class="standard-box">

            <strong>
                🏢 Company Standard
            </strong>

            <div>

                ${
                    escapeHtml(
                        finding.expected ||
                        "No company standard specified."
                    )
                }

            </div>

        </div>


        <div class="rule-box">

            <strong>
                ⚙️ Rule Engine Assessment
            </strong>

            <div>

                ${
                    escapeHtml(
                        finding.explanation ||
                        "No deterministic explanation available."
                    )
                }

            </div>

        </div>


        <div class="ai-section">

            <div class="ai-title">
                🤖 Gemini AI Analysis
            </div>


            <div class="ai-response">

                ${
                    escapeHtml(
                        finding.ai_explanation ||
                        "AI analysis not available."
                    )
                }

            </div>


            ${
                finding.ai_risk
                ?
                `
                    <div style="
                        margin-top: 12px;
                        padding-top: 12px;
                        border-top: 1px solid rgba(124,58,237,0.15);
                    ">

                        <strong>
                            Risk Context
                        </strong>

                        <div style="
                            margin-top: 5px;
                        ">

                            ${escapeHtml(
                                finding.ai_risk
                            )}

                        </div>

                    </div>
                `
                :
                ""
            }


            ${
                finding.ai_confidence
                ?
                `
                    <div style="
                        margin-top: 10px;
                        font-size: 12px;
                        font-weight: 700;
                    ">

                        Confidence:
                        ${escapeHtml(
                            finding.ai_confidence
                        )}

                    </div>
                `
                :
                ""
            }


            <span class="ai-status">

                ${escapeHtml(
                    finding.ai_status ||
                    "AI STATUS UNKNOWN"
                )}

            </span>

        </div>


        <div class="reviewer-action">

            <strong>
                👤 Recommended Reviewer Action
            </strong>

            <div>

                ${
                    escapeHtml(
                        finding.ai_reviewer_action ||
                        getReviewerAction(
                            finding
                        )
                    )
                }

            </div>

        </div>


        <div class="human-review">

            <span>
                ⚠️
            </span>

            <div>

                <strong>
                    Human Review Required
                </strong>

                <br>

                LeaseGuard AI assists the reviewer.
                This finding must be verified before
                any final business or legal decision.

            </div>

        </div>

    `;


    // --------------------------------------------------------
    // SPECIAL QUOTA FALLBACK
    // --------------------------------------------------------

    if (
        finding.ai_status ===
        "AI QUOTA EXHAUSTED"
    ) {

        const aiSection =
            findingElement.querySelector(
                ".ai-section"
            );


        if (aiSection) {

            aiSection.classList.add(
                "ai-unavailable"
            );


            aiSection.innerHTML = `

                <div class="ai-title">
                    🧠 Gemini AI
                </div>

                <div style="
                    font-weight: 700;
                    color: #92400e;
                    margin-bottom: 7px;
                ">

                    Gemini quota temporarily exhausted

                </div>

                <div class="ai-response">

                    The Gemini API quota is currently
                    unavailable. No AI-generated conclusion
                    is being presented.

                    <br><br>

                    <strong>
                        Rule Engine Active
                    </strong>

                    <br>

                    LeaseGuard's deterministic checks,
                    clause evidence, severity and risk
                    assessment remain active and available
                    for human review.

                </div>

                <span class="ai-status"
                    style="
                        background: #fef3c7;
                        color: #92400e;
                    "
                >
                    RULE ENGINE ACTIVE
                </span>

            `;
        }
    }


    findingsContainer.appendChild(
        findingElement
    );
}


// ============================================================
// REVIEWER ACTION
// ============================================================

function getReviewerAction(
    finding
) {

    if (finding.reviewer_action) {

        return String(
            finding.reviewer_action
        );
    }


    const status =
        String(
            finding.status ||
            ""
        ).toUpperCase();


    if (
        status.includes(
            "COMPLIANT"
        )
    ) {

        return (
            "Confirm that the clause continues "
            + "to match the current company standard."
        );
    }


    if (
        status.includes(
            "MISSING"
        )
    ) {

        return (
            "Verify whether this protection is required "
            + "and consider adding the missing clause."
        );
    }


    if (
        status.includes(
            "DEVIATION"
        )
    ) {

        return (
            "Review the deviation against the company "
            + "standard and determine whether negotiation "
            + "or escalation is required."
        );
    }


    return (
        "Verify the clause and determine whether "
        + "further legal or business review is required."
    );
}


// ============================================================
// RISK DASHBOARD
// ============================================================

function addRiskDashboard(
    summary,
    findings,
    status,
    risk
) {

    removeRiskDashboard();


    const total =
        Number(
            summary.total_checks ||
            findings.length ||
            1
        );


    const deviations =
        Number(
            summary.deviations ||
            0
        );


    const missing =
        Number(
            summary.missing ||
            0
        );


    const riskData =
        risk || {};


    const riskScore =
        Number(
            riskData.score ||
            0
        );


    const riskLevel =
        riskData.level ||
        "UNKNOWN";


    const severity =
        riskData.severity_counts ||
        {};


    const critical =
        Number(
            severity.critical ||
            0
        );


    const high =
        Number(
            severity.high ||
            0
        );


    const medium =
        Number(
            severity.medium ||
            0
        );


    const low =
        Number(
            severity.low ||
            0
        );


    const issues =
        deviations +
        missing;


    const dashboard =
        document.createElement(
            "div"
        );


    dashboard.id =
        "leaseguardRiskDashboard";


    dashboard.className =
        "risk-dashboard";


    dashboard.innerHTML = `

        <div class="risk-dashboard-title">

            <div>

                <span class="dashboard-label">
                    LEASEGUARD AI
                </span>

                <h2>
                    Agreement Risk Overview
                </h2>

            </div>


            <div class="risk-level">

                ${escapeHtml(
                    riskLevel
                )}

            </div>

        </div>


        <div class="risk-score">

            <div class="score-number">
                ${riskScore}%
            </div>


            <div>

                <strong>
                    Severity-Based Risk Indicator
                </strong>

                <p>
                    Internal policy indicator calculated
                    from the severity of deviations and
                    missing protections.
                </p>

            </div>

        </div>


        <div class="dashboard-stats">

            <div class="dashboard-stat">

                <span>
                    🔴
                </span>

                <strong>
                    ${critical}
                </strong>

                <small>
                    Critical
                </small>

            </div>


            <div class="dashboard-stat">

                <span>
                    🟠
                </span>

                <strong>
                    ${high}
                </strong>

                <small>
                    High
                </small>

            </div>


            <div class="dashboard-stat">

                <span>
                    🟡
                </span>

                <strong>
                    ${medium}
                </strong>

                <small>
                    Medium
                </small>

            </div>


            <div class="dashboard-stat">

                <span>
                    🔵
                </span>

                <strong>
                    ${low}
                </strong>

                <small>
                    Low
                </small>

            </div>

        </div>


        <div class="executive-summary">

            <strong>
                📋 Executive Summary
            </strong>

            <p>

                LeaseGuard identified

                <strong>
                    ${issues}
                </strong>

                potential issue(s) across

                <strong>
                    ${total}
                </strong>

                checks.

                ${
                    issues > 0
                    ?
                    "The agreement should be reviewed before approval."
                    :
                    "No deviations were identified against the configured standards."
                }

            </p>

        </div>


        <div style="
            margin-top: 14px;
            padding: 12px 14px;
            border-radius: 10px;
            background: rgba(255,255,255,0.05);
            color: #cbd5e1;
            font-size: 12px;
        ">

            🛡️ <strong>Evidence-first review:</strong>
            deterministic Rule Engine findings remain the
            source of policy checks. Gemini assists with
            explanations; human review remains final.

        </div>

    `;


    findingsContainer.parentNode.insertBefore(
        dashboard,
        findingsContainer
    );
}


// ============================================================
// REMOVE RISK DASHBOARD
// ============================================================

function removeRiskDashboard() {

    const existing =
        document.getElementById(
            "leaseguardRiskDashboard"
        );


    if (existing) {

        existing.remove();
    }
}


// ============================================================
// ESCAPE HTML
// ============================================================

function escapeHtml(value) {

    if (
        value === null ||
        value === undefined
    ) {

        return "";
    }


    return String(value)
        .replace(
            /&/g,
            "&amp;"
        )
        .replace(
            /</g,
            "&lt;"
        )
        .replace(
            />/g,
            "&gt;"
        )
        .replace(
            /"/g,
            "&quot;"
        )
        .replace(
            /'/g,
            "&#039;"
        );
}