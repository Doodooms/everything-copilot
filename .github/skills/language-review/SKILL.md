---
name: language-review
description: "WHAT: Apply language-specific review checklists to changed TypeScript, Python, Go, or Rust code. USE FOR: type-safety review, async and concurrency review, idiom checks, ownership and lifetime review, and language-level maintainability checks. DO NOT USE FOR: generic code review with no language-specific depth, security-only audit, or writing code changes."
user-invocable: false
metadata:
  creation-date: 2026-05-14
  creator: Doodooms
---

<definitions>

- **language-specific finding** : A quality or correctness issue that depends on the semantics or idioms of a specific programming language.

</definitions>

<workflow>

## Step 0 - **CONFIRMATION**

1. USE #tool:read **IMMEDIATELY** on #file:./references/USEFOR.md and **IMMEDIATELY** on #file:./references/DONOTUSEFOR.md to confirm with certainty if this skill should be used.
2. Now read the following rules and workflow steps to understand how the skill works and what it requires for execution.

<rules>

- Apply only the sections relevant to the languages actually changed.
- Prioritize correctness and maintainability over style-only preferences.
- Reference support files only at the point of need.

</rules>

## Step 1 - Identify the changed languages and their critical semantics.

1. Use #tool:read on the changed files and their nearest tests.
2. Use #tool:search to group the changed surfaces by language and locate relevant interfaces or call sites.
3. Use #tool:read on #file:./references/guide.md only if the language checklist is still needed.

## Step 2 - Apply the language-specific review checklist.

1. For TypeScript, review type safety, async flow, nullability, and API contract drift.
2. For Python, review typing, runtime import behavior, error handling, and Pythonic structure.
3. For Go and Rust, review concurrency, ownership or lifetime implications, error handling, and idiomatic boundaries.

## Step 3 - Return the language-specific findings.

1. Use #tool:read to verify the final finding locations and examples before returning them.
2. Return only the material language-driven findings or explicitly state that no such findings were identified.

</workflow>