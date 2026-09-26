# Specialist Handoff Contracts

Every packet contains only the task slice, current artifact IDs/revisions, assigned `risk_level`, selected required gates, relevant evidence, constraints, expected return fields, and exact next resume point. The canonical task state is the source of truth; specialists MUST NOT infer missing facts from hidden conversation history or downgrade assigned risk.

## Ownership and required traceability

- **Architect** receives specification revision, relevant `REQ-*`/`AC-*`, approved semantic IDs, repository evidence, and constraints; returns technical `ADR-*`, architectural invariants, alternatives, and unresolved blockers. It MUST NOT redefine problem-space semantics.
- **Challenger** receives a materialized specification/architecture/plan proposal and its evidence; returns counterarguments, failure modes, reversibility, and disconfirming checks without making the final decision.
- **Planner** receives current spec and any required architecture revisions; returns phases and `TASK-*` only when decomposition adds value, with REQ/AC/ADR links, dependencies, separate phase exit criteria, validation obligations, and assigned risk. It maps but MUST NOT redefine spec-owned AC or semantic IDs.
- **Implementer** receives one approved `TASK-*` plus relevant spec/architecture/semantic slices, assigned risk, validation obligations, and reusable evidence IDs; returns changed files, implementation revision, validation evidence (check, command, subject revision, environment, result, producer), and deviations. It uses TDD as an inner method and returns spec mismatches to the Orchestrator.
- **quality-assurance** receives the current specification independently, implementation revision, fresh validation evidence, assigned risk, and changed surfaces only when QA is a required gate; returns `QA-RUN-*`, verdict, falsification scope/method, `REQ-*`/`AC-*` coverage, defect packets, and residual risk. A pass is not acceptance.
- **Reviewer** receives current spec, required architecture/plan/task state, implementation evidence, passing QA run when required, defect history, security-review findings when required, and assigned risk; returns `REVIEW-*`, verdict, revision references, evidence sufficiency, findings, and owners. It reuses fresh evidence rather than repeating identical checks.
- **Researcher** receives one exact, bounded evidence question, `requested_by`, `supports_artifact` with revision, needed source class, and a stop condition; returns only sourced facts, versions, uncertainty, and decision implications without deciding the artifact.
- **DevOps** receives approved operational `TASK-*`, specification revision, applicable REQ/AC, and operational validation obligations; returns changed surfaces, operational evidence, rollout/rollback risks, and environment limitations.

## Failure and resume

- A specialist MUST return `blocked` when upstream intent, architecture, or evidence is materially inconsistent; it MUST NOT repair upstream truth silently.
- QA failures return to the Orchestrator as defect packets, then to the owner established by evidence; QA repeats against the corrected implementation revision.
- Reviewer rejection returns to the Orchestrator for owner-based routing and only the necessary downstream gates.
- The Orchestrator updates canonical state after each return and passes only the required refreshed slice to the next specialist.

## use_case: risk_required_implementation_qa_review

```mermaid
flowchart TD
    before["SDD: prepare TASK packet"]
    implementation["Implementer: implement with TDD"]
    qa["quality-assurance: QA-RUN when required"]
    qa_gate{"QA verdict"}
    fix_owner["Orchestrator: route defect packet to evidenced owner"]
    correction["Implementer or correct owner: new implementation revision"]
    qa_retry["quality-assurance: new QA-RUN"]
    reviewer["Reviewer: REVIEW when required, on current QA-RUN"]
    after["SDD: resume convergence reconciliation"]
    before --> implementation --> qa --> qa_gate
    qa_gate -->|fail| fix_owner --> correction --> qa_retry --> reviewer
    qa_gate -->|pass| reviewer
    reviewer --> after
```

This is the required-gate path when independent QA and final Review are selected. Lower-risk tasks may omit a gate only when the Orchestrator records that it is not required. The fix path is one remediation attempt with distinct nodes; further attempts use new revision-specific nodes.
