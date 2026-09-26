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

## Step 1 - Enumerate the state contract.

1. Identify externally relevant states, events, allowed transitions, terminal states, and invariants; return ambiguous product meaning to the specification owner.

## Step 2 - Choose a representation.

1. Use [state-model guidance](../references/implementation-design/references/state-machines.md) to compare explicit variants, transition tables, and simpler flags without encoding impossible states.
2. Keep transition effects at the narrowest owner and make invalid transitions explicit where the contract requires it.

## Step 3 - Explain the model.

1. Report valid transitions, preserved invariants, rejected states, and the smallest test surface needed to distinguish an invalid transition.
