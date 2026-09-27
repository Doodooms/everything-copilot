---
id: existing-solution-research
description: Compare existing software or standards with a bounded need before building a substantial new capability.
invoke_for:
- a proposed framework, subsystem, service, or infrastructure capability with plausible existing alternatives
- a build-versus-reuse decision that depends on compatibility, license, maintenance, or operating cost
avoid_for:
- routine local implementation choices already covered by repository code
- broad technology surveys without an approved problem or decision owner
references:
  - ../references/deep-research/references/composition.md
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
## Step 1 - Bound the need and search space.

1. DO consume the assigned `risk_level` inherited from the parent domain skill before applying this procedure; then State the concrete problem, required behavior, constraints, scale, deployment boundary, and decision owner; stop if the need is speculative or lacks an acceptance condition.
2. Inspect existing repository capabilities and standards first. Search only the smallest candidate set likely to change the build-versus-reuse decision.
3. When multiple evidence classes are needed, read the [research composition contract](../references/deep-research/references/composition.md) and select only the matching source procedures; do not load archived `method-source.md` copies.

## Step 2 - Compare candidates with traceable evidence.

1. For each candidate, record the exact repository/release/docs source and observation date; distinguish verified facts from inference and unknowns.
2. Compare functional fit and gaps, license and provenance, maintenance/maturity signals, compatibility, integration surface, transitive services/dependencies, operational and security costs, and expected context/token effects.
3. Prefer official project files, releases, and documentation. Do not clone, install, execute, or add dependencies merely to conduct a feasibility check.

## Step 3 - Return a bounded decision packet.

1. Classify each candidate as `ADOPT`, `ADAPT`, `PROVIDER`, `REFERENCE`, `BENCHMARK`, `WATCH`, or `REJECT`; give one evidence-based reason and an observable trigger for deferred candidates.
2. Return `problem`, `existing_solutions`, `build_vs_reuse`, `recommended_next_action`, evidence links, uncertainty, and the supported artifact/revision. Leave the actual architecture/product choice to its owner.
</workflow>
