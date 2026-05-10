```yaml
---
name: skill-name              # REQUIRED. Lowercase + hyphens only, 1-64 chars. MUST match parent folder name exactly — any deviation = silent load failure, no error shown.
description: 'What: <what this skill does>. When to use: <trigger phrases or scenarios that should cause the agent to load this skill>. Do not use for: <nearby tasks that should route elsewhere>'
user-invocable: false          # ALWAYS false — skills are agent-only, never called by humans via slash commands.
# context: fork               # UNCOMMENT only if the skill reads many files or runs a lengthy multi-step investigation. Keeps intermediate steps out of the parent context; only the final result is returned. OMIT for short, focused skills that produce an inline edit or direct answer.
# compatibility: vscode 1.119.0+, github-copilot 1.119.0+ # REQUIRED when the skill relies on version-gated or editor-specific behavior unavailable in older builds.
# metadata:                   # OPTIONAL workspace-local annotation block.
#   creation-date: YYYY-MM-DD
#   creator: UserName
# license: MIT                # OPTIONAL workspace-local annotation.
---
```

```markdown

<rules>

- There **MUST** be one source of truth per concept.
- Name the exact `#tool:` each workflow step requires.
- Reference support files **ONLY** on the step that uses them.
</rules>

<workflow>

## Step 1 - <inspect or prepare>
Use #tool:read on #file:./references/<guide>.md **ONLY** if this step needs that guide.

## Step 2 - <ask or decide>
Use #tool:vscode/askQuestions on #file:./assets/<questions>.json **ONLY** if structured input is still missing.

## Step 3 - <validate or execute>
Use #tool:execute on the narrowest validation command for the skill output.
Reference #file:./scripts/<validator>.py **ONLY** if the validator lives inside the skill folder.
</workflow>
```

## Authoring Notes

- `SKILL.md` **MUST** own workflow. **DO NOT** copy the same checklist or policy into multiple files.
- `assets/` store copyable templates or machine-readable payloads.
- `references/` store human guidance that the workflow loads only when needed.
- `scripts/` store executable checks or automation.
- **NEVER** add `## Runtime Inputs`. Cite each file and tool at the step that consumes it.
- Outside the generated definition snippets, support markdown files **MUST** use markdown links for files and plain or inline-coded tool names. Active `#tool:` and `#file:` markers **MUST ONLY** appear in frontmatter-bearing skill, agent, or prompt bodies.
- The frontmatter `description` remains the primary discovery surface. `## WHEN TO USE`, `## WHEN NOT TO USE`, and short `<definitions>` help the agent once the skill is loaded, but they do **NOT** replace a precise description.
- Add `compatibility` whenever the skill depends on version-gated VS Code or Copilot behavior.
- `metadata` and `license` are optional workspace-local annotations for authorship or provenance.
- Use workspace skill-facing tool names. Common examples include `read`, `search`, `agent`, `execute`, `web`, `browser`, `todo`, and `vscode/askQuestions`, but the valid set comes from the workspace tool layer, not this example list.
- If a concept already exists in a support file, point to that file instead of rewriting it in `SKILL.md`.
- If the workflow depends on repository-local Python tooling, document how to bootstrap it. In this repository, use `uv sync` from the repository root so `.venv` matches `pyproject.toml` and `uv.lock`.

## Discovery and routing example

Bad:

```yaml
---
name: api-helper
description: Helpful API skill
user-invocable: false
---
```

Good:

```yaml
---
name: api-helper
description: "What: Debug failing third-party API integrations. When to use: tracing request or response mismatches, auth failures, or retry behavior. Do not use for: general backend refactors, database work, or unrelated test setup."
user-invocable: false
---
```
```markdown
## WHEN TO USE
- Investigating failing API requests or responses.

## WHEN **NOT** TO USE
- Refactoring unrelated backend modules.

<definitions>
- **trace artifact** : A log, payload, or response snapshot used by the workflow.
</definitions>
```

## Duplicate logic example

Bad:

```markdown
## Validation Rules
- Run the validator before finishing.

## Step 4 - Validate
- Run the validator before finishing.
```

Good:

```markdown
## Validation Rules
- Run the validator before finishing.

## Step 4 - Validate
Apply the Validation Rules section above.
```

## Point-of-need reference example

Bad:

```markdown
## Runtime Inputs
- #file:./assets/ask_questions.json
- #file:./references/validation.md
- #file:./scripts/validate_skill.py
```

Good:

```markdown
## Step 2 - Capture missing details
Use #tool:vscode/askQuestions with #file:./assets/ask_questions.json.

## Step 4 - Validate
Use #tool:execute on #file:./scripts/validate_skill.py.
Use #tool:read on #file:./references/validation.md only while fixing validation output.
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
