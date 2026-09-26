---
id: code-exploration
description: 'Apply the code-exploration method: entry-point tracing, execution-path
  mapping, dependency discovery, and identifying the safest local change surface in
  unfamiliar code.'
invoke_for:
- entry-point tracing, execution-path mapping, dependency discovery, and identifying
  the safest local change surface in unfamiliar code
avoid_for:
- broad architecture design, direct implementation, security auditing, or documentation
  updates
references: []
---

## Step 0 - **CONFIRMATION**

1. USE #tool:read **IMMEDIATELY** on #file:../references/code-exploration/references/USEFOR.md ([when to use](../references/code-exploration/references/USEFOR.md)) and **IMMEDIATELY** on #file:../references/code-exploration/references/DONOTUSEFOR.md ([when not to use](../references/code-exploration/references/DONOTUSEFOR.md)) to confirm with certainty if this skill should be used.
2. Now read the following rules and workflow steps to understand how the skill works and what it requires for execution.

<rules>

- Start from the narrowest concrete anchor available.
- Map only the controlling path needed for the requested work.
- Reference support files only at the point of need.

</rules>

## Step 1 - Find the controlling entry point.

1. Use #tool:search to locate the concrete trigger, handler, route, command, or failing test closest to the requested behavior.
2. Use #tool:read on the anchor files and immediate neighbors that control the behavior.
3. Use #tool:read on #file:../references/code-exploration/references/guide.md ([exploration guide](../references/code-exploration/references/guide.md)) only if the exploration checklist is still needed.

## Step 2 - Trace the execution path and dependencies.

1. Use #tool:read to follow the control flow from the entry point to the state change or result.
2. Use #tool:search to locate related call sites, shared symbols, and adjacent tests when they affect the path.
3. Distinguish orchestration code from the logic that actually decides behavior.

## Step 3 - Return the execution map.

1. Return the entry point, key files, dependency boundaries, and recommended first edit surface.
2. State traps, hidden side effects, or unresolved branches only when they affect likely changes.
