---
id: skill-maintenance
description: Repair, restructure, review, or validate an existing skill package without
  replacing its provenance.
invoke_for:
- repair or restructure an existing skill
- review or validate a skill package
- update a skill's workflows or support files
avoid_for:
- author a new package from scratch
references:
  - ../references/create-skill/references/validation.md
  - ../references/create-skill/references/latest-docs.md
  - ../references/create-skill/references/final-checklist.md
  - ../references/create-skill/references/skill-composition.md
  - ../references/create-skill/references/original-spec.md
---

## Step 1 - Inspect the current package and approved scope.

1. DO consume the assigned `risk_level`; read the target `SKILL.md`, its provenance, selected workflows, and only relevant support files.
   - Read this package's [original specification](../references/create-skill/references/original-spec.md) only when maintaining `create-skill` itself.
2. Preserve established behavior outside scope; DO NOT scaffold over the package or rewrite `references/original-spec.md` without an approved intent change.

## Step 2 - Make the smallest coherent package change.

1. Keep critical invariants, general preferences, risk policy, and admission in `SKILL.md`; put each distinct procedure directly into an immediate `workflows/[id].md` child.
2. Replace square-bracketed fillable values, link each workflow from the parent, and add support files only when a selected step consumes them.
   - Do not add nested workflow metadata or place a procedure under `references/`; references contain supporting knowledge only.
   - For composed skills, use the [composition contract](../references/create-skill/references/skill-composition.md); MUST NOT turn a workflow into an MCP tool.

## Step 3 - Validate and report.

1. From the repository root, run `PYTHONDONTWRITEBYTECODE=1 ./.venv/bin/python agentic-core/skills/plugin-engineering/references/create-skill/scripts/validate.py --skill-dir [skill-dir]` with the [validator](../references/create-skill/scripts/validate.py) and an absolute `[skill-dir]`; use the [validation guide](../references/create-skill/references/validation.md) only for unclear diagnostics.
2. Measure the `SKILL.md`, expected selected workflows, and available tool schemas with `context-management`'s `token-optimization` workflow; exclude generic references and DO NOT load every workflow for the estimate.
3. Complete the [final checklist](../references/create-skill/references/final-checklist.md), present the diff for user review, and report findings or unresolved intent.
   - Inspect [skill_lint_core.py](../references/create-skill/scripts/skill_lint_core.py) only when public validator behavior needs diagnosis.
