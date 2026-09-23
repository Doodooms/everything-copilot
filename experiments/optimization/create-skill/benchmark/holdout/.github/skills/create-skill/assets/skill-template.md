```yaml
---
name: skill-name              # REQUIRED. Lowercase + hyphens only, 1-64 chars. MUST match parent folder name exactly — any deviation = silent load failure, no error shown.
description: 'WHAT: <what this skill does>. USE FOR: <trigger phrases or scenarios that should cause the agent to load this skill>. DO NOT USE FOR: <nearby tasks that should route elsewhere>' # REQUIRED. The primary discovery surface for the skill. Should be precise and comprehensive enough to guide agent routing without further context. Use the "WHAT:", "USE FOR:", and "DO NOT USE FOR:" structure to clearly delineate the skill's purpose, triggers, and boundaries. 1024 CHARS MAX.
user-invocable: true          # Set deliberately. Use true when the skill is intended for direct user invocation.
metadata:                     # REQUIRED in this workspace for authorship and provenance.
    creation-date: YYYY-MM-DD
    creator: UserName
# disable-model-invocation: true # Optional. Use when the skill should run only from a slash command and never auto-load.
# context: fork                  # UNCOMMENT only if the skill reads many files or runs a lengthy multi-step investigation. Keeps intermediate steps out of the parent context; only the final result is returned. OMIT for short, focused skills that produce an inline edit or direct answer.
# compatibility: vscode 1.119.0+, github-copilot 1.119.0+ # REQUIRED when the skill relies on version-gated or editor-specific behavior unavailable in older builds.
# license: MIT                   # Optional workspace-local annotation.
---
```

```markdown
<definitions>

- **ontology** : The concepts and entities that this skill acts on, including their names, boundaries, and relationships.
- **semantic contract** : The intended meaning of the skill's triggers, rules, decisions, outputs, and failure cases.
- **topology** : The structural arrangement of this package, its workflow sections, support files, and references between them.

Definitions must improve the using agent's understanding of the skill's ontology,
semantic contract, and topology. Define the concepts that control decisions in
this skill, not generic terms that merely restate the workflow.

</definitions>

<workflow>

<rules>

- Keep one source of truth per concept.
- Name the exact `#tool:` each workflow step requires.
- Reference support files only on the step that consumes them.
- Keep the main action in `1.` and place sub-checks, exceptions, or examples under it as `-` bullets when that is clearer than another top-level item.

</rules>

## Step 1 - <inspect or prepare>
1. <describe what this step must inspect or prepare before later work can be correct>
    - Use #tool:read on #file:./references/<guide>.md **ONLY** if this action truly needs that guide.
    - If this action has required sub-checks, keep them as `-` bullets under the numbered item instead of inventing another step.
    - Example: "Read the current `SKILL.md`, then note which support files still define live behavior."
2. Add another ordered action only when the step owns a second distinct inspection or preparation task.
    - Example: "Confirm which current docs or templates are still canonical before drafting."

## Step 2 - <ask or decide>
1. <describe the missing decision, ambiguity, or structured input this step resolves>
    - Use #tool:vscode/askQuestions on #file:./assets/<questions>.json **ONLY** if structured input is still missing.
    - If the step branches, use `-` bullets to show the "already known" path and the "still missing" path under the same numbered action.
    - Example: "Reuse the workflow already present in the conversation, or ask only for the fields that remain unknown."
2. Add another ordered action only when the step owns a second distinct decision or intake action.
    - Example: "Stop after one intake path; do **NOT** both infer from history and run the questionnaire."

## Step 3 - <validate or execute>
1. Use #tool:execute on the narrowest validation or execution command for the skill output.
    - <describe the concrete outcome this validation or execution step must produce before the workflow can finish>
    - If the action has prerequisites, checks, or repairs, keep them as `-` bullets under the same numbered item.
    - Example: "Run the local validator, then fix the matching issues before finalizing."
2. Reference #file:./scripts/<validator>.py **ONLY** if the validator lives inside the skill folder.
    - If the step has a follow-up audit or final check, keep it here as a `-` bullet or as a second numbered action only when it is genuinely separate.
    - Example: "After the script passes, review the final checklist before closing the workflow."

</workflow>

```

## Authoring Notes

- `SKILL.md` **MUST** own workflow. **DO NOT** copy the same checklist or policy into multiple files.
- Workspace skills created here always include `SKILL.md`; add `assets/`, `references/`, or `scripts/` only when the workflow consumes a real file from that directory.
- `assets/` store copyable templates or machine-readable payloads that would otherwise bloat the workflow.
- `references/` store human guidance that the workflow loads only when needed.
- `scripts/` store executable checks or automation specific to the skill's domain, not package self-validation. Every script must be self-contained and runnable from the skill package; it must not import workspace modules. The only allowed external composition is an explicit call to another skill.
- Cite each file and tool at the step that consumes it; do not collect support files in a separate inventory section.
- Keep procedural flow in markdown headings and ordered `1.` actions. Use a structured list when the agent must follow, route, or check items in sequence. Use a Markdown table only when the agent must compare the same independent dimensions across several alternatives.
- Inside a step, keep the main action in `1.` and use `-` bullets for sub-checks, exceptions, or examples when that preserves one clear top-level task.
- Reusable examples, large matrices, checklists, and setup guides belong in support files when they are consumed by a workflow step. Read them at point of need instead of pasting them into the workflow.
- Outside the generated definition snippets, support markdown files **MUST** use markdown links for files and plain or inline-coded tool names. Active `#tool:` and `#file:` markers **MUST ONLY** appear in frontmatter-bearing skill, agent, or prompt bodies.
- The frontmatter `description` remains the primary discovery surface. If extra routing help is still needed, keep it in one dense support file or a short `<definitions>` block instead of splitting the same boundary across multiple files.
- Add `compatibility` whenever the skill depends on version-gated VS Code or Copilot behavior.
- `metadata` is required in this workspace. `license` is optional.
- Use workspace skill-facing tool names. Common examples include `read`, `search`, `agent`, `execute`, `web`, `browser`, `todo`, and `vscode/askQuestions`, but the valid set comes from the workspace tool layer, not this example list.
- If a concept already exists in a support file, point to that file instead of rewriting it in `SKILL.md`.
- If the workflow depends on repository-local Python tooling, document how to bootstrap it. In this repository, use `uv sync` from the repository root so `.venv` matches `pyproject.toml` and `uv.lock`.

## Discovery and routing example

Bad:

```yaml
---
name: api-helper
description: Helpful API skill
---
```

Good:

```yaml
---
name: api-helper
description: "WHAT: Debug failing third-party API integrations. USE FOR: tracing request or response mismatches, auth failures, or retry behavior. DO NOT USE FOR: general backend refactors, database work, or unrelated test setup."
user-invocable: false
metadata:
    creation-date: 2026-05-15
    creator: Example Author
---
```

## Duplicate logic example

Bad:

```markdown
# references/routing-a.md
- Create new skill packages.

# references/routing-b.md
- Do not use for agents or prompts.
```

Good:

```markdown
# references/routing.md
- Create or repair a skill: use this skill.
- Update an existing skill: use this skill.
```

## List versus table example

Use a structured list for ordered actions or a single decision path:

```markdown
1. Read the target skill.
2. Identify the missing behavior.
3. Edit the owning workflow step.
4. Run structural validation.
```

Use a Markdown table when every option must be compared across the same
independent dimensions:

```markdown
| Option | Invocation | Reads files | Produces |
| --- | --- | --- | --- |
| Direct | User request | Target package | Edited skill |
| Background | Automatic match | Narrow context | Guidance |
```

Do not turn a sequence of actions into a table, and do not use a table merely
to make a short routing list look more formal.

## Point-of-need reference example

Bad: collect all support files in a separate inventory section.

```markdown
## Support files
- #file:./assets/ask_questions.json
- #file:./references/final-checklist.md
- #file:./scripts/validate.py
```

Good:

```markdown
## Step 2 - Capture missing details
1. Use #tool:vscode/askQuestions with #file:./assets/ask_questions.json only if structured input is still missing.

## Step 3 - Validate
1. Use #tool:execute on #file:./scripts/validate.py.
2. Use #tool:read on #file:./references/final-checklist.md only after script validation.
3. Use #tool:read on #file:./references/validation.md only while fixing validation output.
```

## Choosing `#file:` versus markdown links

Bad:

```markdown
## Step 1 - Inspect options
1. Use #file:./references/guide-a.md to note the canonical guidance.
```

Good:

```markdown
## Step 1 - Inspect options
1. Review [guide A](./references/guide-a.md) before deciding whether it is needed now.
```

## Early-context front-loading example

Bad:

```markdown
## Step 1 - Gather references
1. Use #tool:read on #file:./references/guide-a.md before planning.
2. Use #tool:read on #file:./references/guide-b.md before planning.
3. Use #tool:read on #file:./assets/checklist.md before planning.
```

Good:

```markdown
## Step 1 - Gather context
1. Review [guide A](./references/guide-a.md), [guide B](./references/guide-b.md), and [checklist](./assets/checklist.md) before deciding what matters.
```

## Support-doc marker example

Bad:

```markdown
# Validation notes
Use #tool:read on #file:./references/validation.md.
```

Good:

```markdown
# Validation notes
See [validation guide](../references/validation.md).
Use the tool `read` only when the SKILL workflow step instructs it.
```
