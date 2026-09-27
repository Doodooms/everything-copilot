---
id: memory
description: Orient, retrieve, or persist approved durable context in an available memory vault.
invoke_for:
- Start-of-session orientation from an explicitly available project memory vault
- Retrieve relevant durable context when current evidence is unclear
- Persist a significant approved decision or learning to the designated vault
avoid_for:
- Replace canonical task/specification state, create an unapproved vault, or persist private prompts
references:
  - ../references/memory/assets/vault-templates.md
  - ../references/memory/references/memory.md
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
## Step 1 - Orient from the approved vault.

1. DO consume the assigned `risk_level`; use only an explicitly available, approved memory vault.
2. Read its index first, then current active state and only the relevant decision, learning, glossary, or blocker notes.
3. Retrieve in order: active state, relevant decisions, learnings, glossary, then blockers. Follow backlinks only when they answer a current question, and stop after two hops.
4. If no vault or approved memory capability is available, report that limitation; do not create a competing store. Consult the [VS Code memory integration notes](../references/memory/references/memory.md) only when the selected host is VS Code and verify they still match the installed version.
5. Before relying on a retrieved note, check its stated source path/revision or observation date against current evidence. Mark it stale when that source has changed; do not silently rewrite the note or treat it as canonical task state.

## Step 2 - Retrieve or persist the minimum useful context.

1. Keep canonical task, specification, and decision ownership in their designated artifacts; cite memory notes by path or ID.
2. Persist only when the user explicitly authorizes the write and the host offers an approved memory capability. Do not create a vault, write files directly, or promote repository facts into user-wide memory without that authorization.
3. Use the matching [vault template](../references/memory/assets/vault-templates.md) for an approved note and include provenance sufficient to recheck it later: source path or reference, source revision or observation date, and the claim or decision derived from it.
4. DO update the vault index when a supported write adds or materially changes an indexed note; MUST NOT persist private prompt text or unsupported claims.

## Step 3 - Return the memory handoff.

1. Report the notes consulted or changed, their source freshness, the relevant context delta, unresolved blockers, and any unavailable capability.
2. Do not claim a read, write, or durable save that was not observed.
</workflow>
