---
id: architectural-immune-system
description: Challenge materialized proposals for long-term architectural entropy and integrity risks.
invoke_for:
- Material architecture, governance, workflow, or strategy proposals
- Long-horizon stress, abstraction leaks, governance erosion, or identity drift
- Independent systemic challenge before a consequential proposal is committed
avoid_for:
- Basic debugging, simple code review, isolated implementation, or ordinary feature work
references:
  - ../references/architectural-immune-system/lenses-and-report.md
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
## Step 1 - Establish the system context.

1. DO consume the assigned `risk_level`; inspect the current conversation, materialized proposal, approved requirements, system identity, invariants, architecture/governance docs, contracts, boundary definitions, and tests that enforce those boundaries.
2. Prioritize relevant `README.md`, `CLAUDE.md`, `architecture/`, `docs/`, governance, contracts, memory, ADRs, invariants, architecture/layer tests, replay/determinism, workflow, and orchestration materials. Retrieve only task-relevant memory and runtime models; keep context collection bounded to two minutes unless the user asks for broader research.
3. Confirm the minimum context: system identity, core invariants, layer/boundary model, success condition, scale target, and governance model. Ask one concise question at a time and wait when a critical item is missing; if it cannot be supplied, report the gap. Do not invent context or expand into an unbounded audit.

## Step 2 - Frame and extract systemic failure vectors.

1. Use the fixed scenario: the system technically survived 18 months, but its conceptual integrity degraded through normalized exceptions and accumulated compromises.
2. Extract genuine failure vectors across all six mandatory modes: failure analysis, entropy accumulation, governance erosion, scale transitions, identity drift, and long-horizon systemic stress.
3. Focus on abstraction collapse, semantic leakage, hidden coupling, orchestration creep, determinism corruption, runtime inflation, coordination bottlenecks, compatibility debt, replay corruption, policy fragmentation, cognitive overload, and exception accumulation. Do not return only immediate outages or a generic premortem list.

## Step 3 - Run the seven adversarial perspectives.

1. Use the [lens and report guide](../references/architectural-immune-system/lenses-and-report.md) to examine semantic purity, determinism, governance erosion, scale transition, coupling, identity drift, and long-horizon entropy.
2. When the current host exposes authorized specialist dispatch, send one bounded, independent brief per perspective and keep their work isolated until synthesis. Otherwise run seven distinct analysis passes and state that they were not independent agents; never fabricate agent execution or cross-agent independence.
3. Keep each perspective to 500 words maximum. Record a failure narrative, root assumption, entropy vector, normalization path, early warning signals, and concrete hardening strategy. Tie every claim to evidence or label it as a hypothesis.

## Step 4 - Synthesize and rank the challenge.

1. Produce the required synthesis sections from the guide: most likely corruption vector, most dangerous long-horizon failure, hidden architectural assumption, governance weak point, scale inflection point, identity drift trajectory, architectural hardening plan, and permanent immune responses.
2. Rank only material risks. For each finding, state the affected invariant or boundary, degradation mechanism, confidence, horizon, evidence, and smallest decision or mitigation that reduces risk. Map every recommendation to a specific failure vector; avoid generic advice.
3. Return unresolved assumptions and residual uncertainty to the proposal owner. Do not redesign beyond the challenge, implement, or claim approval.

## Step 5 - Produce the audit artifacts.

1. Write `ais-report-[timestamp].html` and `ais-transcript-[timestamp].md` in the approved output location; ask for a location only when repository convention and task scope do not identify one.
2. Follow the guide's report sections and style. Include the executive synthesis, collapse timeline, entropy vectors, perspective findings, governance weaknesses, scale risks, identity drift, hardening plan, and immune responses.
3. Return both artifact paths, evidence versus hypotheses, the dispatch mode used, unresolved context gaps, and the next owner.
</workflow>
