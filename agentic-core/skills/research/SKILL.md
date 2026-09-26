---
name: research
description: "WHAT: Gather and synthesize traceable repository or external technical evidence for a bounded decision. USE FOR: execution-path exploration, standards and version research, GitHub history, scholarly evidence, compatibility, or multi-source comparisons. DO NOT USE FOR: implementation, product decisions, planning ownership, QA verdicts, or final acceptance."
user-invocable: false
metadata:
  creation-date: 2026-09-26
  creator: Doodooms
license: MIT
---

<critical_rules>

- MUST distinguish verified facts, inference, and uncertainty and include traceable sources for material claims.
- MUST NOT modify repository artifacts or take the requesting agent's decision authority.

</critical_rules>

<general_rules>

- SHOULD return the smallest evidence packet that can change the supported decision or action.

</general_rules>

<risk_assessment>

Consume the Orchestrator-assigned `risk_level`; MUST NOT reclassify or downgrade it. SHOULD escalate only when new evidence materially increases impact, exposure, uncertainty, or irreversibility. Risk scales evidence depth, not authority or approvals.

</risk_assessment>

<rules>

- Research provides evidence; architecture, planning, implementation, QA, review, and operations decisions remain with their owners.
- DO verify primary sources and versions when they affect applicability; do not preload unrelated research methods.

</rules>

<workflow>

## Step 1 - Consume risk and choose an evidence procedure.

1. DO consume the assigned `risk_level`, then select only a matching workflow:
   - [code-exploration](./workflows/code-exploration.md) to trace local entry points, execution paths, or dependencies.
   - [deep-research](./workflows/deep-research.md) for bounded multi-source synthesis.
   - [github-evidence-research](./workflows/github-evidence-research.md) for repository, commit, release, issue, or PR evidence.
   - [paper-research](./workflows/paper-research.md) for scholarly evidence and study limitations.
   - [versioned-documentation-research](./workflows/versioned-documentation-research.md) for version-specific documentation and compatibility.

## Step 2 - Verify only decision-relevant evidence.

1. Load only the selected method and primary sources needed to answer the supplied question; do not substitute generic background for evidence.

## Step 3 - Return a compact research packet.

1. Report verified findings, sources/versions, uncertainty, decision implications, and the supported artifact; do not make the caller's decision.

</workflow>
