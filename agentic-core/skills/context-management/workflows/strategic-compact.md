---
id: strategic-compact
description: Preserve task continuity when a logical phase boundary or context limit warrants a fresh session.
invoke_for:
- After a major milestone or before an unrelated phase/context shift
- When context pressure threatens coherent execution
- When a validated plan or task state can support safe session transfer
avoid_for:
- Mid-implementation with valuable live state or tasks that fit the current context
references: []
---

## Step 1 - Check whether a safe phase boundary exists.

1. DO consume the assigned `risk_level`; compact only after a meaningful phase or before a consequential context shift.
2. MUST NOT recommend a reset mid-implementation when live state, unresolved edits, or debugging detail is needed to continue safely.

## Step 2 - Preserve the minimum durable handoff.

1. Record the canonical task/specification/plan references, current repository and Git state, completed decisions, changed paths, validation evidence, blockers, and exact next action in their authorized locations.
2. Keep the handoff factual and compact; do not copy full conversation history or persist private prompt text.

## Step 3 - Resume only through a supported host path.

1. Start or request a fresh session only when the host supports it and the task can resume from the durable handoff.
2. Return the handoff reference and any state that does not persist; do not assume a parent-conversation pointer exists or claim continuity that the host does not provide.
