---
id: spec-driven-development
description: Normalize material user intent into a canonical specification, derive only necessary solution artifacts, and reconcile risk-required evidence.
invoke_for:
  - material behavior changes, cross-cutting refactors, migrations, APIs, or multi-component work where intent or evidence may drift
  - material requirement changes that need revisioning and targeted staleness propagation
avoid_for:
  - trivial mechanical edits, pure research or documentation, and isolated known-behavior defects with an established lightweight route
references:
  - ../references/spec-driven-development/references/artifact-lifecycle.md
  - ../references/spec-driven-development/references/specification-workflow.md
  - ../references/spec-driven-development/references/handoff-contracts.md
  - ../references/spec-driven-development/references/convergence.md
  - ../references/spec-driven-development/assets/specification-template.md
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
## Step 1 - Establish or revise the canonical problem definition.

1. Read the Orchestrator composition packet, current manifest/state, explicit `mode` (`specify`, `revise`, or `converge`), assigned `risk_level`, and exact parent `resume_point`; return `blocked` if required inputs are missing.
2. In `specify` or `revise` mode, normalize the objective, user intent, requirements, rationale, constraints, non-goals, acceptance criteria, assumptions, and open user decisions. Use the [specification workflow](../references/spec-driven-development/references/specification-workflow.md) and [specification template](../references/spec-driven-development/assets/specification-template.md).
3. For material domain changes, establish the sparse `SPEC.semantic_model` before architecture hardens. Load `semantic-modeling` and select `problem-space` only when meaning, identity, relations, lifecycle, invariants, or epistemic status affects the requirements; do not require it for trivial or non-semantic work.
4. Assign stable `SPEC-*`, `REQ-*`, and `AC-*` IDs. Each `AC-*` MUST reference existing `REQ-*` IDs and a falsifiable observation where practical. Link semantic IDs only where material; do not force every semantic item into traceability.
5. Keep the Orchestrator-assigned `risk_level` and selected `required_gates` in the canonical manifest, not in product requirements. Specialists MUST NOT downgrade risk; evidence may justify escalation. Risk changes assurance depth, never authority or configured approvals.
6. Set the specification to `blocked` while a required user-owned decision is unresolved. For material changes, increment its revision and mark only affected downstream artifacts stale; use [the artifact lifecycle](../references/spec-driven-development/references/artifact-lifecycle.md).
7. In `specify` or `revise` mode, return the proposed/current specification and affected artifact IDs now; do not derive architecture, planning, or implementation before the Orchestrator resumes at the supplied point. If no task record exists, return the normalized specification for the Orchestrator's one canonical manifest; do not create another task root.
8. In `converge` mode, use only the supplied current state and evidence; proceed directly to Step 4 without redispatching specialists.

## Step 2 - Derive only necessary solution and delivery artifacts.

1. Require Architect only for a material solution-space decision (for example component boundary, public interface, persistence shape, integration, dependency direction, or migration architecture). Architect consumes canonical problem semantics and MUST return semantic gaps to the Orchestrator rather than redefining them.
2. Require Challenger only when independent falsification of a materialized high-impact, breaking, hard-to-reverse, or materially uncertain proposal can change the decision.
3. Require Planner only when dependencies, multiple owners, sequencing, phased rollout, or decomposition materially improve execution; an atomic slice MAY set plan status to `not_required`.
4. Planner maps specification-owned acceptance criteria to tasks and defines separate phase exit criteria; it MUST NOT redefine product acceptance. Check traceability, resolvable acyclic dependencies, scope, and artifact freshness before implementation.
5. Load [handoff contracts](../references/spec-driven-development/references/handoff-contracts.md) only when preparing specialist packets. Pass bounded artifact references and deltas, not repeated conversation history.

## Step 3 - Run only selected implementation and assurance gates.

1. Dispatch Implementer for approved code/configuration changes with the smallest task slice, current SPEC/REQ/AC/ADR IDs, constraints, and validation obligations. Implementer uses `tdd` as its inner loop and records checks with command, subject code revision, environment, result, and producer.
2. Reuse fresh sufficient validation evidence when the code revision, check target, and relevant environment are unchanged. QA reruns only when independent execution is required or evidence is insufficient; a distinct falsification question justifies an additional check.
3. Dispatch `quality-assurance` only when `qa` is in `required_gates`; it independently falsifies the current behavior and may diagnose unknown runtime failures. QA failures return as defect packets to the evidence-indicated owner; repeat only affected gates.
4. Dispatch Reviewer only when `review` is in `required_gates`, and only after every required prerequisite passes. Reviewer consumes current implementation and QA evidence, performs final technical acceptance, and MUST NOT repeat a full QA campaign. Load `security-review` only when the changed trust boundary requires static/design analysis.
5. A skipped specialist or gate MUST have a recorded reason. No phase is required merely because an agent exists; each invocation must add a distinct decision, artifact, independent evidence, or configured acceptance result.

## Step 4 - Reconcile current convergence and return to the parent.

1. Reconcile current SPEC revision, REQ/AC coverage, affected semantic IDs, selected architecture/plan/implementation/QA/review gates, implementation evidence, blockers, and staleness using the [convergence contract](../references/spec-driven-development/references/convergence.md).
2. Run the packaged [SDD state validator](../references/spec-driven-development/scripts/validate_sdd_state.py) against the canonical manifest/state:
   `PYTHONDONTWRITEBYTECODE=1 python ../references/spec-driven-development/scripts/validate_sdd_state.py <absolute-task-state-path>`
   Use `--coverage` for the traceability matrix and `--invalidate <source>` only when a material upstream revision changed.
3. If gaps remain, return their categories, evidence, owner, and smallest next gate; do not claim convergence. On convergence, return the structured handoff to `orchestrate` at the supplied `resume_point`, leaving branch, worktree, PR, merge, and cleanup lifecycle with the parent.
</workflow>
