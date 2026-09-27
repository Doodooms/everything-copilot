---
id: resolving-merge-conflicts
description: 'Apply the resolving-merge-conflicts method: bounded source, test, or
  configuration conflicts where both sides'' intent must be preserved and validated.'
invoke_for:
- bounded source, test, or configuration conflicts where both sides' intent must be
  preserved and validated
avoid_for:
- starting, aborting, continuing, or completing Git lifecycle operations, unrelated
  edits, or resolving a conflict whose intended behavior is unknown
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
## Step 1 - Confirm the conflict boundary.

1. DO consume the assigned `risk_level` inherited from the parent domain skill before applying this procedure; then Use #tool:execute to inspect `git status --short` and confirm the active merge/rebase state and exact unmerged paths.
2. Use #tool:read and #tool:search to read the scoped handoff, requirements, relevant source files, tests, and repository instructions; preserve all unrelated modifications.

## Step 2 - Reconcile both intents.

1. Use #tool:execute and #tool:read to inspect the conflict's base and both sides, plus the relevant commit or task context; distinguish code overlap from incompatible behavior.
2. Use #tool:edit to resolve each authorized file with the smallest content change that preserves compatible intent and satisfies the approved contract.
3. If the sources imply incompatible behavior or missing requirements, stop on that conflict and return the exact decision needed; do not invent a compromise.

## Step 3 - Validate and hand off.

1. Review the resolved diff and confirm that no conflict markers or intended changes were lost.
2. Run the narrowest relevant tests or validators; do not stage, commit, continue, or abort the Git operation.
3. Return the resolved and unresolved paths, source intents preserved, validation results, residual risk, `changed_files`, `commit_shas: []`, and the Orchestrator as the lifecycle owner.
</workflow>
