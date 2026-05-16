---
name: test-coverage-review
description: "WHAT: Evaluate whether tests actually protect the changed behavior from regression. USE FOR: reviewing test adequacy after a code change, checking edge-case coverage, validating assertion quality, and identifying meaningful gaps in behavioral coverage. DO NOT USE FOR: raw coverage-percentage reporting, writing the implementation itself, or general style review."
user-invocable: false
metadata:
  creation-date: 2026-05-14
  creator: Doodooms
---

<definitions>

- **behavioral coverage gap** : A missing or weak test that would allow the changed behavior to regress without being detected.

</definitions>

<workflow>

## Step 0 - **CONFIRMATION**

1. USE #tool:read **IMMEDIATELY** on #file:./references/USEFOR.md and **IMMEDIATELY** on #file:./references/DONOTUSEFOR.md to confirm with certainty if this skill should be used.
2. Now read the following rules and workflow steps to understand how the skill works and what it requires for execution.

<rules>

- Review changed behavior first, then judge test adequacy.
- Prefer meaningful assertions and edge cases over noisy test volume.
- Reference support files only at the point of need.

</rules>

## Step 1 - Inspect the changed behavior and the tests that claim to cover it.

1. Use #tool:read on the changed files and the nearest tests for the modified behavior.
2. Use #tool:search to find related execution paths, error handling, and additional test files that may already cover part of the change.
3. Use #tool:read on #file:./references/guide.md only if the coverage-review checklist is still needed.

## Step 2 - Evaluate test strength and identify real gaps.

1. Check the happy path, error paths, and edge cases that matter for the changed behavior.
2. Judge whether the assertions prove outcomes rather than just execution.
3. Separate critical gaps from optional improvements.

## Step 3 - Return the behavioral coverage review.

1. Use #tool:read to verify the final test references and claimed gaps.
2. Return the coverage summary, material gaps, and any convincing positive coverage observations.

</workflow>