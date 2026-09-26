---
id: code-review
description: 'Apply the code-review method: static review of a bounded diff and its
  consequential call sites.'
invoke_for:
- static review of a bounded diff and its consequential call sites
avoid_for:
- implementation, runtime diagnosis, adversarial test execution, dedicated security
  review, or final acceptance
references: []
---

## Step 1 - Establish the review contract.

1. Use #tool:read to inspect the approved requirements, review target, changed-file list, and author/QA evidence.
2. Use #tool:todo to create native todos for major review phases only when the review is multi-phase; do not split each file or finding into a separate todo.
3. Identify review boundaries and required specialist evidence before analyzing implementation details.

## Step 2 - Inspect for material defects.

1. Use #tool:search to trace changed behavior through relevant callers, data boundaries, error handling, and compatibility surfaces.
2. Check correctness, regressions, unsafe fallbacks, maintainability, test evidence, and documentation/operational impact within scope.
3. Route dedicated security, database, performance, or language-specific questions to their corresponding evidence workflow rather than duplicating it.

## Step 3 - Return findings.

1. Order findings by severity and confidence; include exact file/line, concrete impact, evidence, and suggested owner.
2. Separate blockers from optional improvements and state residual risks, examined scope, and missing evidence.
3. Return a concise review handoff; do not claim final approval or modify the change. Use #tool:todo to update todos before returning.
