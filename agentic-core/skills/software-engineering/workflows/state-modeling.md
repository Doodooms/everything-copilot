---
id: state-modeling
description: Model a non-trivial local lifecycle using explicit valid states, events,
  and transitions.
invoke_for:
- lifecycle changes with multiple valid states or transitions
- boolean or nullable flags that admit impossible combinations
- logic whose correctness depends on transition ordering
avoid_for:
- product-domain state semantics not yet specified
- simple values with no lifecycle
references:
  - ../references/implementation-design/references/state-machines.md
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
## Step 1 - Enumerate the state contract.

1. DO consume the assigned `risk_level` inherited from the parent domain skill before applying this procedure; then Identify externally relevant states, events, allowed transitions, terminal states, and invariants; return ambiguous product meaning to the specification owner.

## Step 2 - Choose a representation.

1. Use [state-model guidance](../references/implementation-design/references/state-machines.md) to compare explicit variants, transition tables, and simpler flags without encoding impossible states.
2. Keep transition effects at the narrowest owner and make invalid transitions explicit where the contract requires it.

## Step 3 - Explain the model.

1. Report valid transitions, preserved invariants, rejected states, and the smallest test surface needed to distinguish an invalid transition.
</workflow>
