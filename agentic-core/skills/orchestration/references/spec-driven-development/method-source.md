---
name: spec-driven-development
description: "WHAT: Coordinate specification-driven software delivery from user intent through evidence-backed convergence. USE FOR: non-trivial features, material behavior changes, cross-cutting refactors, migrations, API or multi-component changes, and work with material cross-agent drift risk. DO NOT USE FOR: trivial mechanical edits, pure research or documentation, or isolated known-behavior defects where a lightweight workflow is sufficient."
user-invocable: false
metadata:
  creation-date: 2026-09-23
  creator: Doodooms
---

<definitions>

- **canonical specification**: The user-approved, revisioned source of WHAT must be true: requirements, rationales, acceptance criteria, constraints, non-goals, assumptions, and open decisions.
- **derived artifact**: Architecture, plan, task, implementation, validation, QA, or review evidence created from a specific specification revision.
- **material change**: A change to required behavior, acceptance criteria, constraints, non-goals, public contracts, or architecture assumptions.
- **stale artifact**: A derived artifact whose relevant upstream revision changed after it was produced or approved; it MUST NOT be treated as current evidence.
- **convergence**: Reconciliation showing all in-scope requirements and acceptance criteria have current implementation and QA evidence, required gates pass, no blocking finding or stale artifact remains, and Reviewer has approved.
- **SDD / TDD**: SDD is the Orchestrator's outer delivery loop; TDD is the Implementer's inner test-first implementation method.
- **composition packet**: Bounded inputs, constraints, expected return fields, and a precise parent resume point for this skill when called from `orchestrate`.

</definitions>

<rules>

- The Control Plane is the sole durable task root. Use its existing task state and artifacts when connected and required; Agentic Core MUST NOT create a local manifest or history files as a parallel store.
- Use `SPEC-*`, `REQ-*`, `AC-*`, `TASK-*`, `QA-RUN-*`, and `REVIEW-*` only when they are supplied or allocated by the Control Plane for a workflow that depends on them. Standalone local work carries the active user request, relevant context, and observable results in the handoff/session; MUST NOT request or mint these IDs.
- The canonical specification owns product intent. Downstream agents MUST NOT silently alter it; only the Orchestrator may accept a material change, revise the specification, and propagate staleness.
- Architecture, plan, implementation, tests, and evidence are derived artifacts. Durable Control Plane artifacts record the supplied specification revision and relevant IDs they consume. A standalone active handoff/session carries request context and observed outcomes without fabricated IDs or revision references.
- SDD MUST remain risk-proportional. Trivial work, research-only requests, documentation-only requests, and isolated known-behavior defects MAY use the Orchestrator's lightweight route.
- Preserve role ownership: Orchestrator coordinates; Architect decides structure; Planner decomposes; Implementer builds and uses TDD; `quality-assurance` diagnoses and falsifies; Reviewer accepts; Challenger independently challenges material proposals; Researcher supplies evidence; DevOps owns operational changes.
- A QA pass is not Review approval. Reviewer approval MUST be tied to current QA and implementation evidence.
- A material revision MUST invalidate only downstream artifacts affected by that change; when exact impact is uncertain, invalidate conservatively.
- When composed from `orchestrate`, require an explicit `mode` (`specify`, `revise`, or `converge`), return a structured result and control to the supplied parent resume point. MUST NOT treat the child workflow as replacing Orchestrator lifecycle ownership.
- Every successful handoff MUST return `status`, `mode`, the supplied current `SPEC-*` revision when one exists, applicable changed/stale artifact IDs, relevant evidence, open blockers, and exact `resume_point`. Standalone local handoffs describe the request and observable criteria directly without minting IDs. `converge` mode MUST also return `converged | gaps_found` with categorized gaps and owners.

</rules>

<admission>

## ACCEPT

- New features, material behavior changes, cross-cutting refactors, migrations, API changes, multi-component changes, and multi-agent delivery where traceable acceptance and evidence are needed.
- Material changes with several requirements, risks, dependencies, or opportunities for intent drift between specialists.
- Mid-workflow requirement changes that need revisioning, staleness propagation, and targeted revalidation.

## REJECT

- Trivial mechanical edits, formatting-only changes, or obvious one-line maintenance -> return to `orchestrate` for a lightweight workflow.
- Pure research or documentation-only work -> return to `orchestrate` for the relevant specialist or skill.
- Isolated defects with known intended behavior and no specification, architecture, or scope ambiguity -> return to `orchestrate` for the focused Implementer -> QA -> Reviewer path.

For REJECT, return exactly:

```json
{"status":"rejected","skill":"spec-driven-development","reason":"<concise reason>","routing":"orchestrate"}
```

</admission>

<workflow>

## Step 1 - Establish or revise the canonical specification.

1. Read the Orchestrator-provided composition packet and its `mode`; stop as `blocked` if the mode or other genuinely required inputs are missing. A Control Plane task-state artifact is required only when the concrete workflow depends on durable task history.
   - In `specify` mode, normalize the initial request and return the spec object to the parent before architecture, planning, branch creation, or implementation dispatch.
   - In `revise` mode, update the approved specification revision, propagate affected-artifact staleness, and return control before any downstream specialist resumes.
   - In `converge` mode, use only supplied current Control Plane task context, when present, and specialist evidence; execute Step 4 and return without redispatching specialists.
   - Use supplied Control Plane task state as the source of current intent when present. Otherwise use the request and current handoff/session for a workflow that does not depend on durable task state.
   - If no Control Plane task record exists, return the normalized specification object to the Orchestrator in the handoff/session and continue without creating a local task root or asking for history paths.
   - Use [the artifact lifecycle](./references/artifact-lifecycle.md) to interpret supplied Control Plane artifact revisions and legacy exchange fields.
   - When authoring or materially repairing this skill package, consult its [preserved source specification](./references/original-spec.md) as provenance, not as a live task specification.
2. Extract objective, user intent, in-scope requirements, rationales, constraints, non-goals, acceptance criteria, assumptions, and open decisions.
   - Load [the specification workflow](./references/specification-workflow.md) and [the specification template](./assets/specification-template.md) at this step.
   - Use #tool:vscode/askQuestions only for user-owned decisions that materially alter behavior, scope, acceptance, architecture options, or risk.
3. For a Control Plane-backed workflow that allocates specification artifacts, consume its `SPEC-*`, `REQ-*`, and `AC-*` IDs and ensure each `AC-*` references existing `REQ-*` IDs. Otherwise keep the normalized request, required behaviors, and falsifiable observations together in the active handoff/session without assigning identifiers.
   - Set status to `blocked` while a required user decision remains unresolved; do not dispatch downstream work from a blocked specification.
   - For a material change, increment the specification revision before dispatch and propagate staleness before any derived artifact is reused.
4. In `specify` or `revise` composition mode, return the updated specification and affected supplied/allocated artifact IDs now; for standalone work return its request context and behavior statements without IDs. Do not run Steps 2-4 before the parent resumes.

## Step 2 - Derive current architecture and an executable plan.

1. Decide whether architecture work is required; set architecture status to `not_required` only when existing boundaries satisfy the current specification.
2. When required, dispatch Architect with #tool:agent and the supplied specification revision and relevant IDs when available, repository evidence, constraints, and expected decisions.
   - Dispatch Challenger with #tool:agent on the materialized proposal only for high-impact, breaking, irreversible, or materially risky decisions.
3. Dispatch Planner with #tool:agent when sequencing or decomposition is needed; provide current specification and architecture context and any supplied revisions/IDs.
   - Planner maps supplied spec-owned `AC-*` to phases/tasks and defines separate phase exit criteria; for standalone work it maps the behavior statements directly and MUST NOT invent identifiers or redefine product acceptance.
4. Check traceability, resolvable task dependencies, scope/non-goal consistency, and artifact freshness before implementation. Load [handoff contracts](./references/handoff-contracts.md) for the precise specialist packets and return fields.

## Step 3 - Run implementation, QA, and review gates.

1. Dispatch Implementer with #tool:agent and the smallest task slice, supplied `SPEC-*` revision and relevant `REQ-*`/`AC-*`/`ADR-*` when present, otherwise the active request/context, scope, dependencies, and validation obligations.
   - Implementer uses `tdd` as its inner loop for testable behavior changes; SDD MUST NOT duplicate or replace that method.
2. Dispatch `quality-assurance` with #tool:agent and the current specification independently of the Implementer's interpretation; select diagnostic investigation for an observed unknown failure and adversarial verification for completed behavior.
   - QA failures return through the Orchestrator as defect packets and route to the evidenced owner; repeat only the affected implementation and QA gates.
3. Dispatch Reviewer with #tool:agent only after required QA passes; Reviewer performs final technical acceptance and loads `security-review` for static trust-boundary analysis when the changed surface requires it.
   - Reviewer rejection returns through the Orchestrator to the owner identified by evidence; it MUST NOT default every finding to Implementer.

## Step 4 - Reconcile convergence and return to the parent.

1. Reconcile supplied current revisions and ID-based requirement/criterion/task coverage when available; otherwise compare the active request and observable behavior statements with implementation evidence, QA/review results, blockers, and stale artifacts using [the convergence contract](./references/convergence.md).
2. When the workflow has a supplied Control Plane state artifact in the validator's supported exchange format, run the deterministic [SDD state validator](./scripts/validate_sdd_state.py) on that artifact using #tool:execute and the command below.
   - `PYTHONDONTWRITEBYTECODE=1 python scripts/validate_sdd_state.py <supplied-state-artifact>`
   - Agent Skills resolves the packaged script path relative to this skill's root; see the [official script-path guidance](https://agentskills.io/skill-creation/using-scripts). If no task state is needed or supplied, reconcile the current handoff/session and local evidence instead; do not request an absolute local history path.
   - Use `--coverage` to emit the traceability matrix; use `--invalidate <source>` only when a material upstream revision has changed.
3. If gaps remain, classify them and return to the Orchestrator with the owning specialist, evidence, and precise next gate; do not claim convergence.
4. On convergence, return the structured SDD handoff to `orchestrate` at the packet's `resume_point`, preserving task/branch/PR/merge/cleanup lifecycle ownership in the parent.

</workflow>
