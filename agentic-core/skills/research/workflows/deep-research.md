---
id: deep-research
description: 'Apply the deep-research method: cross-source research, technical comparisons,
  or decisions needing more than one evidence workflow.'
invoke_for:
- cross-source research, technical comparisons, or decisions needing more than one
  evidence workflow
avoid_for:
- a single narrow GitHub, scholarly-paper, or version-specific documentation lookup;
  implementation or decision ownership
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
## Step 1 - Bound the research objective.

1. DO consume the assigned `risk_level` inherited from the parent domain skill before applying this procedure; then Confirm the question, requesting agent, supported artifact/revision, decision criteria, constraints, and exact parent resume point from the incoming request; use explicit assumptions only for non-material omissions.
2. Classify the finite evidence classes needed. Reject a single-source request that belongs to one focused skill; do not add sources solely to make the task appear comprehensive.
3. For this multi-phase workflow, use #tool:todo to create one native todo for objective/source planning, one for evidence collection and validation, and one for synthesis and return.
4. When authoring or materially repairing this package, consult the [original specification](../references/deep-research/references/original-spec.md) as provenance only.

## Step 2 - Compose the selected evidence workflows.

1. When focused procedures are needed, load the [composition contract](../references/deep-research/references/composition.md), prepare bounded context, and select only source-class workflows in the finite order declared there: `github-evidence-research`, `paper-research`, or `versioned-documentation-research`.
   - Execute each selected workflow in the current Researcher context; workflow selection is not a finding or success result.
   - Each child packet MUST contain `objective`, `inputs`, `constraints`, `expected_output`, and `resume_point`.
   - Expected output MUST include `status`, findings, exact source links/identifiers, evidence location, applicability, and uncertainty.
2. After each child workflow returns, verify the status and required fields before advancing. On `partial`, preserve the gap; on `rejected`, `failed`, missing fields, or malformed output, stop composition and report the route or failure explicitly.
3. For any remaining general-source claim, use only the available #tool:web or #tool:browser workflow and record the exact source URLs and evidence. Do not assume Firecrawl, Exa, `fetch_webpage`, shell execution, or research subagents.

## Step 3 - Synthesize and resume.

1. Synthesize only validated evidence relevant to the objective; cite material claims, retain source disagreements, and distinguish facts from inference and recommendation.
2. Return `status: success | partial | failed`, the objective and supported artifact/revision, findings and source metadata, applicability, uncertainty, decision implications, blockers, and the incoming `resume_point` unchanged.
3. Complete the native todos from evidence, then stop. Researcher validates this packet and resumes at its declared analysis step; the original caller retains decision ownership.
</workflow>
