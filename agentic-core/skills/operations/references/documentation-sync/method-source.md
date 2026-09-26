---
name: documentation-sync
description: "WHAT: Synchronize repository documentation with approved, verified implementation behavior. USE FOR: planned user/developer documentation updates assigned to an implementation task. DO NOT USE FOR: deciding product intent, researching external documentation, changing product code, or speculative documentation cleanup."
user-invocable: false
metadata:
  creation-date: 2026-09-24
  creator: Doodooms
---

<definitions>

- **approved documentation scope**: The documentation paths or topics assigned by the current plan for the approved task.
- **verified behavior**: Behavior supported by the current specification and implementation evidence, not inferred from an unverified proposal.

</definitions>

<rules>

- MUST consume the current specification revision, plan assignment, implementation evidence, and changed-file list before editing.
- MUST update only existing authoritative documentation relevant to the approved change; preserve the repository's terminology and style.
- MUST NOT change requirements, acceptance criteria, implementation, or public behavior; return a blocker when the implementation and approved specification disagree.
- MUST NOT invent examples, compatibility claims, command results, or version guarantees.
- MUST NOT edit generated output directly; use its source/generator only when explicitly included in scope.
- SHOULD make the smallest documentation change that keeps affected guidance accurate and discoverable.

</rules>

<admission>

## ACCEPT

- A current approved implementation task explicitly assigns a documentation update grounded in verified behavior.
- A documentation consistency pass limited to paths and claims named by the approved task.

## REJECT

- Missing approval, stale specification, or unresolved product intent → `orchestrate`.
- External library/API behavior research → `researcher` with `versioned-documentation-research`.
- Code changes or documentation cleanup outside approved scope → `implementer` or `orchestrate`, as appropriate.

For REJECT, return exactly:

```json
{"status":"rejected","skill":"documentation-sync","reason":"<concise reason>","routing":"<route or null>"}
```

</admission>

<workflow>

## Step 1 - Establish source of truth and assigned scope.

1. Read the current specification, assigned plan slice, implementation evidence, and changed-file list; stop with a precise blocker if any required input is missing or stale.
2. Use #tool:search and #tool:read to locate the existing authoritative docs, their owners, and the smallest affected sections.
3. When authoring or materially repairing this package, consult the [original specification](./references/original-spec.md) as provenance only; it does not override the live task.

## Step 2 - Synchronize only verified documentation.

1. Use #tool:edit to update only the assigned documentation sections supported by implementation evidence.
   - Preserve approved terminology, examples, links, and generated-file boundaries.
   - If the docs would need an unsupported product claim or the implementation conflicts with the specification, stop and return the evidence; do not resolve the product decision here.
2. Avoid unrelated cleanup, duplicated instructions, or documentation changes outside the plan.

## Step 3 - Verify and report the documentation change.

1. Use #tool:execute only for existing, relevant documentation checks or examples that can be run safely; report the exact command and result.
2. Return status, changed documentation paths, source behavior/spec revision, checks performed, unresolved gaps, and the next owner. If no documentation change is warranted, explain why and leave files unchanged.

</workflow>