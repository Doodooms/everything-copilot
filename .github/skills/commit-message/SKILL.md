---
name: commit-message
description: "WHAT: Produce a factual, auditable commit message from validated changes. USE FOR: finalizing commit text after implementation and validation are complete, summarizing the actual diff, and recording change scope without speculation. DO NOT USE FOR: planning work, writing code, validating logic, or inventing changes that are not present."
user-invocable: false
metadata:
  creation-date: 2026-05-14
  creator: Doodooms
---

<definitions>

- **commit summary** : A concise imperative subject plus supporting bullets that describe only confirmed changes and relevant limitations.

</definitions>

<workflow>

## Step 0 - **CONFIRMATION**

1. USE #tool:read **IMMEDIATELY** on #file:./references/USEFOR.md and **IMMEDIATELY** on #file:./references/DONOTUSEFOR.md to confirm with certainty if this skill should be used.
2. Now read the following rules and workflow steps to understand how the skill works and what it requires for execution.

<rules>

- Describe only validated changes.
- Do not invent intent or future work.
- Reference support files only at the point of need.

</rules>

## Step 1 - Inspect the validated change surface.

1. Use #tool:read on the validated summary, changed files, and relevant diff context.
2. Use #tool:search only if you need to confirm module or symbol names mentioned in the change.
3. Use #tool:read on #file:./references/guide.md only if the commit checklist is still needed.

## Step 2 - Draft the commit summary from confirmed facts.

1. Write a concise imperative subject that matches the actual change.
2. Add bullets for the concrete files, behaviors, or operational surfaces changed.
3. Note limitations or risks only when they were explicitly observed during validation.

## Step 3 - Check that the message stays factual.

1. Use #tool:read on the draft and compare it against the validated change summary.
2. Return only the final commit message content.

</workflow>