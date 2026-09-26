---
id: skill-authoring
description: Create one self-contained skill package from an approved capability.
invoke_for:
- create and scaffold a new skill package
avoid_for:
- maintain or validate an existing package
references:
  - ../references/create-skill/references/ask_questions.md
  - ../references/create-skill/references/skill-composition.md
  - ../references/create-skill/references/validation.md
  - ../references/create-skill/references/latest-docs.md
  - ../references/create-skill/references/authoring-patterns.md
  - ../references/create-skill/references/final-checklist.md
---

<admission>

## ACCEPT

- Create and scaffold a new skill package from an approved capability.
- Author its immediate workflows and the support files those workflows consume.
- Update authoring assets or validators as required to create the approved package.

## REJECT

- Repair, restructure, review, or validate an existing skill -> `plugin-engineering`'s `skill-maintenance` workflow.
- Create or edit an agent -> `plugin-engineering`'s `agent-authoring` workflow.
- Create or edit the direct-user Orchestrator -> `plugin-engineering`'s `agent-authoring` workflow.
- Create or edit a reusable prompt -> `orchestrate` for lightweight routing.
- Implement or repair MCP server code -> Implementer with `plugin-engineering`'s `create-mcp` workflow.
- Measure a skill context projection -> `context-management`'s `token-optimization` workflow.
- Optimize an existing skill or design its evaluation benchmark -> `plugin-engineering`'s `optimize-skill` workflow.
- Define always-on repository guidance -> repository instructions.
- Implement general product behavior -> the relevant implementation workflow.

For REJECT, return exactly:

```json
{"status":"rejected","skill":"create-skill","reason":"<concise reason>","routing":"<route or null>"}
```

</admission>

## Step 0 - Confirm the authoring target.

1. Inspect the requested package path and preserve existing user work; stop before scaffolding over a non-empty destination.

## Step 1 - Establish the package contract.

1. DO consume the assigned `risk_level`; inspect the request and target and use [the question payload](../references/create-skill/assets/ask_questions.json) only for material gaps.
2. Capture the accepted capability contract in `[spec_file]` outside `[skill_dir]`; the scaffold copies it into the package.

## Step 2 - Scaffold and author.

1. Resolve `[spec_file]`, `[skill_dir]`, this package's [scaffold.py](../references/create-skill/scripts/scaffold.py), and its [skill-scaffold.json](../references/create-skill/assets/skill-scaffold.json) configuration to absolute paths. Run the script directly with that config:
   `PYTHONDONTWRITEBYTECODE=1 python [absolute-scaffold.py-path] --config [absolute-skill-scaffold.json-path] --output [skill_dir] --original-spec [spec_file] --validate`
2. Fill the [skill](../references/create-skill/assets/skill-template.md) and optional [workflow](../references/create-skill/assets/workflow-template.md) templates; replace every square-bracketed value.
   - Consult the [package shape](../references/create-skill/assets/folder-template.md) only when deciding which support directories the accepted workflow needs.
   - Keep `<critical_rules>`, `<general_rules>`, and `<risk_assessment>` separate. Use `MUST`/`MUST NOT` for invariants, `SHOULD`/`SHOULD NOT` for preferences, `MAY` for optional behavior, and `DO`/`DO NOT` for local actions.
   - Step 1 consumes the assigned level; risk changes evidence depth, never authority or approval requirements.
   - Consult [authoring patterns](../references/create-skill/references/authoring-patterns.md) only when workflow structure, support-file placement, or composition remains unclear.
3. For composition, follow `skill-composition`.

## Step 3 - Validate and return.

1. Run [validate.py](../references/create-skill/scripts/validate.py) by its resolved absolute path: `PYTHONDONTWRITEBYTECODE=1 python [absolute-validate.py-path] --skill-dir [skill_dir]`. Fix structural errors; use [lint.py](../references/create-skill/scripts/lint.py) only for content checks.
2. Consult `validation` or `latest-docs` only when unclear. Load `context-management` and select `token-optimization` for `SKILL.md`, each selected workflow, and available tool schemas; exclude generic references.
3. Return the package, evidence, estimate/method, unresolved decisions, and risks; use `final-checklist`.
