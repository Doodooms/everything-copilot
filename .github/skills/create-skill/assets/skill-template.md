```yaml
---
name: skill-name              # REQUIRED. Lowercase + hyphens only, 1-64 chars. MUST match parent folder name exactly — any deviation = silent load failure, no error shown.
description: 'WHAT: <what this skill does>. USE FOR: <trigger phrases or scenarios that should cause the agent to load this skill>. DO NOT USE FOR: <nearby tasks that should route elsewhere>' # REQUIRED. The primary discovery surface for the skill. Should be precise and comprehensive enough to guide agent routing without further context. Use the "WHAT:", "USE FOR:", and "DO NOT USE FOR:" structure to clearly delineate the skill's purpose, triggers, and boundaries. 1024 CHARS MAX.
user-invocable: false          # ALWAYS false — skills are agent-only, never called by humans via slash commands.
metadata:                   # REQUIRED workspace-local annotation block.
    creation-date: YYYY-MM-DD
    creator: UserName
# context: fork               # UNCOMMENT only if the skill reads many files or runs a lengthy multi-step investigation. Keeps intermediate steps out of the parent context; only the final result is returned. OMIT for short, focused skills that produce an inline edit or direct answer.
# compatibility: vscode 1.119.0+, github-copilot 1.119.0+ # REQUIRED when the skill relies on version-gated or editor-specific behavior unavailable in older builds.
# license: MIT                # Optional workspace-local annotation.
---
```

```markdown
<definitions>

- **definition** : A reusable concept or rule that the workflow references. It lives in a `<definitions>` block near the top of the file so the agent can find it when it needs to apply that concept or rule.

</definitions>

<workflow>

## Step 0 - **CONFIRMATION**

1. USE #tool:read **IMMEDIATELY** on #file:./references/USEFOR.md and **IMMEDIATELY** on #file:./references/DONOTUSEFOR.md to confirm with **certainty** if this skill should be used.
2. Now read the following rules and workflow steps to understand how the skill works and what it requires for execution.

<rules>

- There **MUST** be one source of truth per concept.
- Name the exact `#tool:` each workflow step requires.
- Reference support files **ONLY** on the step that uses them.

</rules>

## Step 1 - <inspect or prepare>

1. <describe what this step must inspect or prepare before later work can be correct>.
2. Use #tool:read on #file:./references/<guide>.md **ONLY** if this step needs that guide.

## Step 2 - <ask or decide>

1. <describe the missing decision, ambiguity, or structured input this step resolves>.
2. Use #tool:vscode/askQuestions on #file:./assets/<questions>.json **ONLY** if structured input is still missing.

## Step 3 - <validate or execute>

1. <describe the concrete outcome this validation or execution step must produce before the workflow can finish>.
2. Use #tool:execute on the narrowest validation command for the skill output.
3. Reference #file:./scripts/<validator>.py **ONLY** if the validator lives inside the skill folder.

</workflow>

```

## Authoring Notes

- `SKILL.md` **MUST** own workflow. **DO NOT** copy the same checklist or policy into multiple files.
- Keep each workflow step descriptive. If several actions must occur in order inside one step, use an ordered list instead of a single vague sentence.
- `assets/` store copyable templates or machine-readable payloads.
- `references/` store human guidance that the workflow loads only when needed.
- `scripts/` store executable checks or automation.
- **NEVER** add `## Runtime Inputs`. Cite each file and tool at the step that consumes it.
- Prefer markdown links such as `[guide](./references/guide.md)` when the workflow is only naming a candidate, optional, or future file. Use `#file:` only when the current step must consume that file immediately.
- **NEVER** batch 3 or more candidate support-file reads in an early context step. Use markdown links to show the files exist, then defer each `#tool:read` to the point-of-need step.
- Outside the generated definition snippets, support markdown files **MUST** use markdown links for files and plain or inline-coded tool names. Active `#tool:` and `#file:` markers **MUST ONLY** appear in frontmatter-bearing skill, agent, or prompt bodies.
- Support markdown files should keep lightweight hierarchy: one `#` title plus short `##` sections when the doc covers multiple concerns. Prefer `## Purpose`, `## When to use this file`, `## How to use it`, `## Fix patterns`, and `## Status codes` over bare labels.
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
description: "WHAT: Debug failing third-party API integrations. USE FOR: tracing request or response mismatches, auth failures, or retry behavior. DO NOT USE FOR: general backend refactors, database work, or unrelated test setup."
user-invocable: false
---
```
```markdown

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

## Choosing `#file:` versus markdown links

Bad:

```markdown
## Step 1 - Inspect options

Use #file:./references/guide-a.md to note the canonical guidance.
Use #file:./references/guide-b.md as an alternative.
```

Good:

```markdown
## Step 1 - Inspect options

Review [guide A](./references/guide-a.md) and [guide B](./references/guide-b.md) to decide which file matters.

## Step 3 - Draft

Use #tool:read on #file:./references/guide-a.md only if the draft needs guide A right now.
```

## Early-context front-loading example

Bad:

```markdown
## Step 1 - Gather references

Use #tool:read on #file:./references/guide-a.md before planning.
Use #tool:read on #file:./references/guide-b.md before planning.
Use #tool:read on #file:./assets/checklist.md before planning.
```

Good:

```markdown
## Step 1 - Gather context

Review [guide A](./references/guide-a.md), [guide B](./references/guide-b.md), and [checklist](./assets/checklist.md) to decide which file is relevant.

## Step 3 - Draft

Use #tool:read on #file:./references/guide-a.md only if the workflow needs guide A.
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
