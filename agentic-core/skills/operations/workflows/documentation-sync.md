---
id: documentation-sync
description: 'Apply the documentation-sync method: planned user/developer documentation
  updates assigned to an implementation task.'
invoke_for:
- planned user/developer documentation updates assigned to an implementation task
avoid_for:
- deciding product intent, researching external documentation, changing product code,
  or speculative documentation cleanup
references: []
---

## Step 1 - Establish source of truth and assigned scope.

1. Read the current specification, assigned plan slice, implementation evidence, and changed-file list; stop with a precise blocker if any required input is missing or stale.
2. Use #tool:search and #tool:read to locate the existing authoritative docs, their owners, and the smallest affected sections.
3. When authoring or materially repairing this package, consult the [original specification](../references/documentation-sync/references/original-spec.md) as provenance only; it does not override the live task.

## Step 2 - Synchronize only verified documentation.

1. Use #tool:edit to update only the assigned documentation sections supported by implementation evidence.
   - Preserve approved terminology, examples, links, and generated-file boundaries.
   - If the docs would need an unsupported product claim or the implementation conflicts with the specification, stop and return the evidence; do not resolve the product decision here.
2. Avoid unrelated cleanup, duplicated instructions, or documentation changes outside the plan.

## Step 3 - Verify and report the documentation change.

1. Use #tool:execute only for existing, relevant documentation checks or examples that can be run safely; report the exact command and result.
2. Return status, changed documentation paths, source behavior/spec revision, checks performed, unresolved gaps, and the next owner. If no documentation change is warranted, explain why and leave files unchanged.
