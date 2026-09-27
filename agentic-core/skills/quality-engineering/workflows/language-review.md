---
id: language-review
description: 'Apply the language-review method: type-safety review, async and concurrency
  review, idiom checks, ownership and lifetime review, and language-level maintainability
  checks.'
invoke_for:
- type-safety review, async and concurrency review, idiom checks, ownership and lifetime
  review, and language-level maintainability checks
avoid_for:
- generic code review with no language-specific depth, security-only audit, or writing
  code changes
references: []
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
- Apply only the sections relevant to the languages actually changed.
- Prioritize correctness and maintainability over style-only preferences.
- Reference support files only at the point of need.
- MUST return the result, evidence, remaining unknowns, risks, and status required by this procedure.
</rules>

<workflow>
## Step 1 - Identify the changed languages and their critical semantics.

1. DO consume the assigned `risk_level` inherited from the parent domain skill before applying this procedure; then Use #tool:read on the changed files and their nearest tests.
2. Use #tool:search to group the changed surfaces by language and locate relevant interfaces or call sites.
3. Use #tool:read on #file:../references/language-review/references/guide.md ([language review guide](../references/language-review/references/guide.md)) only if the language checklist is still needed.

## Step 2 - Apply the language-specific review checklist.

1. For TypeScript, review type safety, async flow, nullability, and API contract drift.
2. For Python, review typing, runtime import behavior, error handling, and Pythonic structure.
3. For Go and Rust, review concurrency, ownership or lifetime implications, error handling, and idiomatic boundaries.

## Step 3 - Return the language-specific findings.

1. Use #tool:read to verify the final finding locations and examples before returning them.
2. Return only the material language-driven findings or explicitly state that no such findings were identified.
</workflow>
