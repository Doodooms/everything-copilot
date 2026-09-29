---
id: security-review
description: Perform a static security review of authentication, authorization, input handling, API boundaries, secrets, data exposure, and security evidence.
invoke_for:
- changes affecting authentication, authorization, input handling, API boundaries, secrets, or sensitive data
- static security evidence review before a release or deployment
avoid_for:
- dynamic security testing, production fixes, architecture ownership, or final non-security acceptance or merge decisions
references:
- ../references/security-review/security-controls.md
---
<critical_rules>
- MUST keep work within this subskill's declared scope and its specific safety or authority constraints.
- MUST NOT replace the parent domain skill's admission, global routing, or authority boundaries.
</critical_rules>

<general_rules>
- SHOULD load listed references only at the procedure step that needs them.
- MAY report unavailable evidence or unresolved decisions as unknown.
</general_rules>

<risk_assessment>
Consume the Orchestrator-assigned `risk_level` through the parent domain skill; MUST NOT reclassify or downgrade it. SHOULD escalate only when new evidence materially increases risk. Scale evidence depth, not authority or approvals.
</risk_assessment>

<rules>
- MUST follow this selected subskill only within its declared procedure and scope.
- MUST return the result, evidence, remaining unknowns, risks, and status required by this procedure.
</rules>

<workflow>
## Step 1 - Scope the static review
1. DO consume the assigned `risk_level`; identify changed files, security-relevant dependencies and callers, tests, trust boundaries, sensitive data, and authority flows.
2. Record the review boundary and evidence that cannot be inspected. Do not expand into production fixes, architecture ownership, or a dynamic test campaign.

## Step 2 - Review applicable controls
1. When available and supported, use #tool:mcp_semgrep_semgrep_scan on changed source. Treat alerts as leads to verify, not proof of a defect or of safety; record unavailable scans as unknown.
2. Use [the security controls reference](../references/security-review/security-controls.md) at this step. Assess only controls relevant to the changed surface; use narrow checks and inspect source context for each conclusion.

## Step 3 - Record evidence and findings
1. Mark a control `PASS` only when inspected evidence supports it, `FAIL` when evidence demonstrates a defect, `N/A` with a reason when it does not apply, and `UNKNOWN` when evidence cannot decide it.
2. For each finding, record severity, affected path and line, trust boundary or abuse case, evidence, and concrete remediation direction. Do not promote an unverified scanner alert to a confirmed finding.

## Step 4 - Return the review
1. Return scope, overall status (`pass`, `fail`, `partial`, or `unknown`), checks and evidence, findings, unverified controls, and residual risk.
2. Include deployment-specific controls only when deployment is in scope. Send evidence to the parent Orchestrator or Reviewer; report severity and release impact without making merge or deployment decisions.
</workflow>
