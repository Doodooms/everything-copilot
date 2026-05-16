---
name: failure-analysis
description: "WHAT: Reproduce failures, isolate root causes, and choose the narrowest evidence-backed repair path. USE FOR: failing builds, test failures, runtime defects, swallowed errors, dangerous fallbacks, and reliability investigation. DO NOT USE FOR: new feature implementation, broad refactoring, general code review, or documentation-only work."
user-invocable: false
metadata:
  creation-date: 2026-05-14
  creator: Doodooms
---

<definitions>

- **failure chain** : The concrete sequence from trigger to symptom to root cause, including any hidden fallback or lost error signal.

</definitions>

<workflow>

## Step 0 - **CONFIRMATION**

1. USE #tool:read **IMMEDIATELY** on #file:./references/USEFOR.md and **IMMEDIATELY** on #file:./references/DONOTUSEFOR.md to confirm with certainty if this skill should be used.
2. Now read the following rules and workflow steps to understand how the skill works and what it requires for execution.

<rules>

- Confirm the failure with the narrowest possible check before proposing a fix.
- Prefer root-cause evidence over symptom-level speculation.
- Reference support files only at the point of need.

</rules>

## Step 1 - Collect the concrete failure evidence.

1. Use #tool:read on the failing command output, stack trace, log, or reproducer first.
2. Use #tool:search to locate the owning code path, nearby tests, and error-handling surfaces.
3. Use #tool:read on #file:./references/guide.md only if the failure-analysis checklist is still needed.

## Step 2 - Isolate the root cause and choose the repair path.

1. Use #tool:execute on the narrowest failing command or test that proves the issue.
2. Trace swallowed errors, hidden fallbacks, or configuration drift until the root cause is explicit.
3. Define the smallest repair that addresses the confirmed cause without broad refactoring.

## Step 3 - Validate the repair path or diagnosis.

1. Use #tool:execute to rerun the focused check after the repair or after the diagnosis is instrumented.
2. Return the failure chain, root cause, repair direction, and any remaining uncertainty.

</workflow>