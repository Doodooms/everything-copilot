---
name: deep-research
description: "WHAT: Synthesize evidence for a bounded question across multiple sources while preserving provenance and uncertainty. USE FOR: cross-source research, technical comparisons, or decisions needing more than one evidence workflow. DO NOT USE FOR: a single narrow GitHub, scholarly-paper, or version-specific documentation lookup; implementation or decision ownership."
user-invocable: false
metadata:
  creation-date: 2026-09-24
  creator: Doodooms
---

<definitions>

- **research objective**: The named question or decision and the artifact/revision it supports.
- **child packet**: The bounded objective, relevant inputs, constraints, expected result fields, and exact resume point sent to one source-specific skill.
- **validated evidence**: A child result whose status, expected fields, source identity, evidence location, and applicability have been checked before synthesis.

</definitions>

<rules>

- MUST preserve the requesting agent, supported artifact/revision, source identity, exact URL or repository permalink, version/commit/date where relevant, evidence location, applicability, fact-versus-inference status, and uncertainty.
- MUST load and execute only the source-specific skill workflows required by the finite question; each selected child is loaded at most once.
- A skill is a packaged workflow, not a deterministic tool call or a separate agent. The current Researcher loads and executes each selected child workflow, then resumes this parent workflow.
- MUST pass a bounded child packet, validate its explicit return, and return to the declared parent resume point.
- MUST stop or return `partial`/`failed` on a malformed, missing, or failed child result; MUST NOT infer success from a tool trace.
- MUST NOT create recursive skill calls, unbounded retry loops, arbitrary source quotas, or fixed recency requirements.
- SHOULD stop once the evidence is sufficient for the named decision; preserve disagreement rather than smoothing it away.
- MAY use #tool:web or #tool:browser for a relevant general-source question not handled by a focused child skill.

</rules>

<admission>

## ACCEPT

- A bounded research question needing synthesis across multiple evidence classes or independent source types.
- A technical comparison requiring at least two applicable evidence workflows, or an explicit broad research request with a decision or artifact to support.

## REJECT

- A single narrow GitHub evidence question → `github-evidence-research`.
- A single scholarly-paper question → `paper-research`.
- A single version-specific API, SDK, language, or product-documentation question → `versioned-documentation-research`.
- Product decisions, code changes, QA, or final acceptance → the owning custom agent through `orchestrate`.

For REJECT, return exactly:

```json
{"status":"rejected","skill":"deep-research","reason":"<concise reason>","routing":"<route or null>"}
```

</admission>

<workflow>

## Step 1 - Bound the research objective.

1. Confirm the question, requesting agent, supported artifact/revision, decision criteria, constraints, and exact parent resume point from the incoming request; use explicit assumptions only for non-material omissions.
2. Classify the finite evidence classes needed. Reject a single-source request that belongs to one focused skill; do not add sources solely to make the task appear comprehensive.
3. For this multi-phase workflow, use #tool:todo to create one native todo for objective/source planning, one for evidence collection and validation, and one for synthesis and return.
4. When authoring or materially repairing this package, consult the [original specification](./references/original-spec.md) as provenance only.

## Step 2 - Compose the selected evidence workflows.

1. When focused research procedures are needed, load the [composition contract](./references/composition.md), prepare the bounded context, and select each matching source-class workflow from the loaded `research` domain in the finite order declared there.
   - Select only the [github-evidence-research](../../workflows/github-evidence-research.md), [paper-research](../../workflows/paper-research.md), or [versioned-documentation-research](../../workflows/versioned-documentation-research.md) workflow when its admission matches the source class.
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
