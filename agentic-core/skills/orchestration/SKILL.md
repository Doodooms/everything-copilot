---
name: orchestration
description: "WHAT: Coordinate dependency-aware software delivery, canonical task state, specialist handoffs, and repository lifecycle. USE FOR: non-trivial delivery, planning, cross-agent coordination, material changes, migrations, or authorized Git conflict handling. DO NOT USE FOR: architecture decisions, implementation, QA execution, final review, or operational mutations."
user-invocable: true
metadata:
  creation-date: 2026-09-26
  creator: Doodooms
license: MIT
---

<critical_rules>

- MUST preserve approved intent, canonical task state, ownership boundaries, and explicit Git authorization.
- MUST NOT treat a workflow as a tool, delegate beyond authority, or claim convergence without current evidence.

</critical_rules>

<general_rules>

- SHOULD choose the smallest risk-proportional delivery route and reuse fresh evidence.

</general_rules>

<risk_assessment>

Assess impact/blast radius, reversibility, security or data exposure, external contracts, and uncertainty. Use the highest applicable level: **L0** isolated/reversible; **L1** bounded to one component; **L2** cross-component, contract, migration, or material integration; **L3** high-impact, sensitive, destructive, or hard to reverse. Record the assigned `risk_level` and gates; specialists MUST NOT downgrade it and SHOULD escalate only with evidence. Risk scales evidence and coordination only, never authority or approvals.

</risk_assessment>

<rules>

- This domain owns delivery coordination, planning, specification flow, and authorized Git lifecycle; specialist skills do not transfer ownership.
- Every immediate workflow MUST contain its complete procedure; references are supporting knowledge only.

</rules>

<workflow>

## Step 1 - Assess risk and choose a delivery procedure.

1. DO assess task risk using `<risk_assessment>`, then select the narrowest procedure whose `invoke_for` matches and `avoid_for` does not:
   - Record the assigned risk level and required gates in the canonical task state before dispatch.
   - [orchestrate](./workflows/orchestrate.md) for material changes, multi-agent coordination, and handoffs.
   - [spec-driven-development](./workflows/spec-driven-development.md) for non-trivial requirements, cross-component changes, migrations, or convergence.
   - [implementation-planning](./workflows/implementation-planning.md) for dependency-aware phases, tasks, sequencing, and validation.
   - [chatgpt-work-handoff](./workflows/chatgpt-work-handoff.md) when a completed implementation should be surfaced to ChatGPT Work through a GitHub pull request and returned as a discussion summary.
   - [commit-message](./workflows/commit-message.md) after an authorized, validated commit.
   - [resolving-merge-conflicts](./workflows/resolving-merge-conflicts.md) for an authorized active merge/rebase conflict.

## Step 2 - Execute the selected workflow.

1. Follow the selected workflow directly; load only supporting references or assets at their point of use and preserve the supplied scope, task state, role owners, and resume point.

## Step 3 - Return the delivery handoff.

1. Report status, current artifact IDs/revisions, decisions, handoffs, evidence, changed files, risks, blockers, and exact next owner; do not claim completion while a required gate is stale or missing.

</workflow>
