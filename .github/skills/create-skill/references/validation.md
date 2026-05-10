# Skill validation guide

Purpose
- Explains what `scripts/validate_skill.py` checks and how to fix its output.
- Use [skill-template.md](../assets/skill-template.md) for the canonical bad and good examples that correspond to the checks below.

When to use this file
- Read it after validation fails or when you need to understand what the validator enforces.
- In this repository, run the validator with `./.venv/bin/python .github/skills/create-skill/scripts/validate_skill.py --skill-dir <skill_folder>`.
- If `.venv` does not exist yet, or if dependencies changed, run `uv sync` from the repository root before running the validator.

Automatic checks
- `SKILL.md` exists at the skill root.
- YAML frontmatter parses and contains `name`, `description`, and `user-invocable`.
- A frontmatter `name` that differs from the folder name is reported.
- `context` without `compatibility` is reported because version-gated behavior should declare explicit compatibility bounds.
- Missing `<rules>` or `<workflow>` blocks are reported.
- `SKILL.md` longer than 500 lines is reported.
- Missing or empty `assets/` or `references/` is reported.
- Unresolved template leftovers such as `<what this skill does>`, `./references/<guide>.md`, or `./assets/<questions>.json` are reported.
- Non-frontmatter markdown files are checked for active `#tool:` or `#file:` markers outside fenced code blocks.
- `#tool:` markers are parsed, checked for trailing punctuation, and validated against the workspace skill-tool alias catalog.
- Wrong-layer raw tool names such as `copilot_readFile`, `run_in_terminal`, or `vscode_askQuestions` fail validation and include alias suggestions.
- `#file:` markers are parsed, checked for trailing punctuation, and best-effort checked for existence.
- Every file under `assets/`, `references/`, and `scripts/` **MUST** be referenced from `SKILL.md`.
- Duplicate normalized markdown headings are reported.
- A `## Runtime Inputs` section is reported because it front-loads support files instead of referencing them at point of need.

Fix patterns
- Missing frontmatter key -> add the missing key to the YAML header.
- Name mismatch -> rename the folder or change the `name` field so they match.
- `context` without `compatibility` -> add a `compatibility` field with the minimum VS Code and GitHub Copilot versions you have actually verified.
- Missing `.venv` or missing validator dependencies -> run `uv sync` from the repository root, then rerun the validator.
- Missing `<rules>` or `<workflow>` -> restore the canonical structure from [skill-template.md](../assets/skill-template.md).
- Template leftovers such as `<what this skill does>` or `./references/<guide>.md` -> replace them with concrete wording and real file paths before publishing.
- Active `#file:` in a support markdown file -> replace it with a markdown link such as `[file](./path)` or `[file](../path)`.
- Active `#tool:` in a support markdown file -> replace it with plain prose or inline code such as `vscode/askQuestions`.
- Unknown or wrong-layer `#tool:` -> replace it with the skill-facing alias or namespaced tool accepted by the workspace.
- Unreferenced support file -> cite the file on the workflow step that consumes it.
- `Runtime Inputs` warning -> move each `#file:` reference to the step where the agent actually needs that file.
- Trailing punctuation after `#file:` or `#tool:` -> rewrite the sentence so the reference stands alone.
- Duplicate headings -> merge the sections or rename one so only one canonical heading remains.

Workspace notes
- `compatibility` is strongly recommended whenever a skill depends on version-gated behavior.
- `metadata` and `license` are optional local annotations; keep them concise if you use them.
- `## WHEN TO USE`, `## WHEN NOT TO USE`, and short `<definitions>` can help post-load routing, but the frontmatter `description` remains the main discovery surface.

Status codes
- ERROR: **MUST** fix before publishing.
- WARNING: structural problem or quality issue that should usually be corrected.