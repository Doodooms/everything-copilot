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
  - ../references/create-skill/references/authoring-patterns.md
  - ../references/create-skill/references/original-spec.md
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
- MUST return the result, evidence, remaining unknowns, risks, and status required by this procedure.
</rules>

<workflow>
## Step 1 - Inspect the current package and approved scope.

1. DO consume the assigned `risk_level`; read the target `SKILL.md`, relevant provenance, selected workflows, and only relevant support files. Inspect history or source material when a refactor may have discarded useful expertise.
   - Read this package's [original specification](../references/create-skill/references/original-spec.md) only when maintaining `create-skill` itself.
2. Preserve established behavior outside scope; DO NOT scaffold over the package or rewrite `references/original-spec.md` without an approved intent change.

## Step 2 - Make the smallest coherent package change.

1. Apply [the authoring patterns](../references/create-skill/references/authoring-patterns.md) to classify changes as admission/routing, procedure, domain expertise, reusable artifact, or deterministic validation.
2. Keep critical invariants, general preferences, risk policy, and admission in `SKILL.md`; put each distinct procedure directly into an immediate `workflows/[id].md` child.
3. Preserve useful knowledge, examples, assets, and scripts unless they are obsolete, incorrect, duplicated, or demonstrably unnecessary. Revalidate versioned material before moving it into active support.
4. Replace square-bracketed fillable values, link each workflow from the parent, and add support files only when a selected step consumes them.
   - Each immediate subskill keeps its `id`, `description`, `invoke_for`, `avoid_for`, and `references` metadata plus the canonical skill body structure. Do not create another workflow level, a peer `SKILL.md` package, or a global route for that subskill. Put the complete procedure in its `<workflow>` block; references contain supporting knowledge only.
   - For composed skills, use the [composition contract](../references/create-skill/references/skill-composition.md); MUST NOT turn a workflow into an MCP tool.

## Step 3 - Validate and report.

1. From the repository root, run `PYTHONDONTWRITEBYTECODE=1 ./.venv/bin/python agentic-core/skills/plugin-engineering/references/create-skill/scripts/validate.py --skill-dir [skill-dir]` with the [validator](../references/create-skill/scripts/validate.py) and an absolute `[skill-dir]`; use the [validation guide](../references/create-skill/references/validation.md) only for unclear diagnostics.
2. Measure the `SKILL.md`, expected selected workflows, and available tool schemas with `context-management`'s `token-optimization` workflow; exclude generic references and DO NOT load every workflow for the estimate.
3. Complete the [final checklist](../references/create-skill/references/final-checklist.md), present the diff for user review, and report findings or unresolved intent.
   - Inspect [skill_lint_core.py](../references/create-skill/scripts/skill_lint_core.py) only when public validator behavior needs diagnosis.
</workflow>
