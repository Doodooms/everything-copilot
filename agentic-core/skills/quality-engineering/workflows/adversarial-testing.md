---
id: adversarial-testing
description: 'Apply the adversarial-testing method: independent QA, edge cases, integration
  failures, invalid states, and test-surface weakness.'
invoke_for:
- independent QA, edge cases, integration failures, invalid states, and test-surface
  weakness
avoid_for:
- production fixes, architecture decisions, routine implementation tests, static security
  review, or final acceptance
references: []
---
<critical_rules>
- MUST keep work within this subskill’s declared scope and its specific safety or authority constraints.
- MUST NOT replace the parent domain skill’s admission, global routing, or authority boundaries.
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
- MUST NOT replace the parent domain skill’s admission, global routing, or authority boundaries.
- MUST return the result, evidence, remaining unknowns, risks, and status required by this procedure.
</rules>

<workflow>
## Step 1 - Define the falsification surface.

1. DO consume the assigned `risk_level` inherited from the parent domain skill before applying this procedure; then Use #tool:read to inspect the current handoff, specification, relevant architecture decisions, changed files, immediate tests, and Implementer evidence.
2. Use #tool:todo to create or update one native todo for each major QA phase; do not create a todo per assertion or test case.
3. Derive plausible contract violations and select the smallest checks capable of exposing them.

## Step 2 - Execute independent checks.

1. Use #tool:execute to run focused boundary and error-path tests before broad suites; inspect assertions and fixtures for false confidence.
2. Exercise sequencing, integration, persistence, concurrency, compatibility, security, or performance only where applicable.
3. Reproduce and minimize each material failure; use #tool:edit to add durable test-surface protection only when authorized and useful.
4. Stop additional exploration when the correct owner has enough evidence to repair, unless directly related checks are cheap.

## Step 3 - Return the verdict and defect packet.

1. Return `pass`, `fail`, or `blocked`, the tested scope/revision, executed commands, outcomes, and untested risks.
2. For each failure, provide expected/actual behavior, reproduction, evidence, affected IDs, suspected owner, and next action.
3. Route product defects to Implementer, operational defects to DevOps, architecture/specification gaps to their owner, and test-surface defects to QA; use #tool:todo to update QA todos before routing.
</workflow>
