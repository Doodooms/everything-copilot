# Curated VS Code skill notes

Use this file only to confirm upstream VS Code behavior that still matters for local authoring.

Upstream reference: [Agent Skills documentation](https://code.visualstudio.com/docs/copilot/customization/agent-skills)

## Upstream facts that still matter

- Discovery starts from YAML frontmatter, especially `name` and `description`.
- The `SKILL.md` body loads only after the skill is selected.
- Extra files load only when `SKILL.md` references them.
- Upstream treats `name` and `description` as required and `user-invocable`, `disable-model-invocation`, and `context` as optional.

## Local authoring rules in this repository

- Default workspace location: `.github/skills/<name>/`.
- `description` should use `WHAT`, `USE FOR`, and `DO NOT USE FOR`.
- `metadata` is required here even though upstream treats it as optional.
- Package shape is conditional here: see [folder-template.md](../assets/folder-template.md) and add support directories only when the workflow has real point-of-need content for them.
- Resolve scope and primitive selection inside the numbered workflow when the request leaves them genuinely unclear.
- Run the validator first, then the [final checklist](./final-checklist.md).

## Why this matters for token efficiency

- Keep `SKILL.md` focused on executable workflow.
- Keep non-mandatory routing, matrices, and checklists in support files so they load only when needed.
- Do not split one decision surface across multiple support files.

## Common failure modes

- Folder name and `name` mismatch.
- Vague `description` that does not expose routing keywords.
- Front-loaded reads before the file is actually needed.
- Active `#tool:` or `#file:` markers in support markdown.
- Repeating the same package rule, routing rule, or matrix in multiple files.
