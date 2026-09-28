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
## Step 0 - Confirm the authoring target.

1. DO consume the assigned `risk_level` inherited from the parent domain skill before applying this procedure; then Inspect the requested package path and preserve existing user work; stop before scaffolding over a non-empty destination.

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
   - Apply [authoring patterns](../references/create-skill/references/authoring-patterns.md) to classify each piece of content as routing, procedure, expertise, reusable artifact, or deterministic check. Keep `SKILL.md` and the procedure small by linking the selected step to rich lazy-loaded support where needed.
   - Use compact GOOD/BAD examples when they resolve a plausible ambiguity; do not impose example or reference counts. Preserve useful expertise from existing sources and revalidate versioned material before carrying it forward.
3. For composition, follow `skill-composition`.

## Step 3 - Validate and return.

1. Run [validate.py](../references/create-skill/scripts/validate.py) by its resolved absolute path: `PYTHONDONTWRITEBYTECODE=1 python [absolute-validate.py-path] --skill-dir [skill_dir]`. Fix structural errors; use [lint.py](../references/create-skill/scripts/lint.py) only for content checks.
2. Consult `validation` or `latest-docs` only when unclear. Load `context-management` and select `token-optimization` for `SKILL.md`, each selected workflow, and available tool schemas; exclude generic references.
3. Return the package, evidence, estimate/method, unresolved decisions, and risks; use `final-checklist`.
</workflow>
