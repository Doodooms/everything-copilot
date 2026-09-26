# Shared Agent Ontology

Use this as the canonical vocabulary when authoring agents in the software-delivery lifecycle. Copy only definitions that constrain the agent's decisions, routing, or handoff; do not duplicate the entire glossary in every profile.

## Specification and requirements

- **specification**: The canonical, revisioned statement of required behavior, rationale, constraints, acceptance criteria, non-goals, assumptions, and unresolved user decisions.
- **spec revision**: An immutable version of a specification, identified as `SPEC-<id>@rev<N>`; every downstream artifact records the revision it consumed.
- **requirement**: A stable, identifiable statement of required behavior or property, identified as `REQ-<id>`.
- **acceptance criterion**: A spec-owned, falsifiable observable condition demonstrating one or more requirements, identified as `AC-<id>` and linked to its parent requirement IDs.
- **constraint**: A mandatory boundary on solution choices or execution.
- **non-goal**: Explicitly excluded behavior or scope; it MUST NOT be implemented without a specification revision.
- **open decision**: A user-owned ambiguity whose resolution materially changes behavior, scope, architecture, risk, or acceptance.

## Architecture and delivery

- **architecture decision**: A structural or technical choice for satisfying the specification, identified as `ADR-<id>` and linked to affected requirements.
- **architectural invariant**: A property or boundary that implementation and downstream artifacts must preserve.
- **implementation plan**: A dependency-aware sequence of phases and bounded tasks that maps approved requirements and acceptance criteria to delivery work without changing their meaning.
- **task**: A bounded implementation unit derived from approved requirements, architecture, and plan, identified as `TASK-<id>` and linked to relevant `REQ-*`, `AC-*`, and `ADR-*` IDs.
- **phase exit criterion**: A delivery-local condition proving that a plan phase is complete; it supplements but MUST NOT redefine product acceptance criteria.
- **dependency**: A required decision, artifact, capability, or completed task that must precede another artifact or task.
- **material change**: A change to required behavior, acceptance, constraints, non-goals, public contracts, or architecture assumptions that may invalidate downstream artifacts.
- **stale artifact**: A derived artifact whose recorded upstream revision no longer matches a material source change; it MUST be reconciled before use as authoritative evidence.

## Verification and decisions

- **validation**: Execution of a named check against a stated criterion; validation alone is not proof unless its result and scope are recorded.
- **verification evidence**: A reproducible result tied to artifact IDs/revisions, commands or method, environment, observed outcome, and limitations.
- **implementation evidence**: Reproducible code/test results tied to a task, specification revision, and applicable requirement/acceptance IDs.
- **defect packet**: An actionable counterexample linking affected `REQ-*`/`AC-*` IDs to expected and actual behavior, reproduction, evidence, environment, and suspected owner.
- **QA pass**: No material violation was found within the adversarial scope actually exercised; this is not final acceptance.
- **review approval**: The Reviewer's evidence-based judgment that the completed change conforms to the current specification and architecture with adequate QA and residual-risk evidence.
- **convergence**: The Orchestrator's reconciliation state where requirements are covered, tasks complete, current acceptance evidence exists, required gates pass, no blocker or stale artifact remains, and no unrequested material change is present.
- **handoff packet**: The minimal, explicit inputs, IDs/revisions, constraints, expected result, and return fields needed for one owner to act without relying on hidden conversation context.
- **supported artifact**: The exact `SPEC-*`, `REQ-*`, `AC-*`, `ADR-*`, `TASK-*`, defect, or decision whose resolution requires a research result.
- **TDD**: The Implementer's inner test-first loop of RED, GREEN, and behavior-preserving refactor; it does not define product acceptance or replace the outer SDD gates.
