---
id: refactor-cleanup
description: 'Apply the refactor-cleanup method: safe cleanup after implementation,
  duplicate removal, dead-code elimination, and behavior-preserving refactors.'
invoke_for:
- safe cleanup after implementation, duplicate removal, dead-code elimination, and
  behavior-preserving refactors
avoid_for:
- feature delivery, speculative rewrites, or optimization without evidence
references: []
---

## Step 0 - **CONFIRMATION**

1. USE #tool:read **IMMEDIATELY** on #file:../references/refactor-cleanup/references/USEFOR.md ([when to use](../references/refactor-cleanup/references/USEFOR.md)) and **IMMEDIATELY** on #file:../references/refactor-cleanup/references/DONOTUSEFOR.md ([when not to use](../references/refactor-cleanup/references/DONOTUSEFOR.md)) to confirm with certainty if this skill should be used.
2. Now read the following rules and workflow steps to understand how the skill works and what it requires for execution.

<rules>

- Preserve intended behavior while cleaning structure.
- Prefer small, reviewable cleanup slices over broad rewrites.
- Reference support files only at the point of need.

</rules>

## Step 1 - Identify the cleanup candidate and its current behavior.

1. Use #tool:read on the target files, nearby tests, and existing behavior anchor.
2. Use #tool:search to locate duplicate logic, dead branches, unused helpers, or repeated patterns.
3. Use #tool:read on #file:../references/refactor-cleanup/references/guide.md ([cleanup guide](../references/refactor-cleanup/references/guide.md)) only if the cleanup checklist is still needed.

## Step 2 - Apply the smallest behavior-preserving cleanup plan.

1. Decide which code is truly dead, duplicated, or unnecessarily complex.
2. Keep the refactor local and avoid mixing it with new behavior.
3. Preserve or improve the surrounding test safety net.

## Step 3 - Validate the cleanup result.

1. Use #tool:execute on the narrowest test or build check that proves the behavior is unchanged.
2. Return the cleanup scope, preserved behavior, and any follow-up slices that should stay separate.
