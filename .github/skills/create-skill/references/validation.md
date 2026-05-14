# Skill validation guide

## Purpose

- Explains what `scripts/validate_skill.py` checks and how to fix its output.
- `scripts/validate_skill.py` now uses the shared Markdown and template linter at `scripts/customization_lint.py` for the structural checks, then applies skill-specific catalog validation on top.
- Use [skill-template.md](../assets/skill-template.md) for the canonical bad and good examples that correspond to the checks below.

## When to use this file

- Read it after validation fails or when you need to understand what the validator enforces.
- In this repository, run the validator with `./.venv/bin/python .github/skills/create-skill/scripts/validate_skill.py --skill-dir <skill_folder>`.
- For the fast create-* feedback loop, run `uv run python scripts/customization_lint.py create-surfaces --root .` or `npm run lint:create-surfaces`.
- If `.venv` does not exist yet, or if dependencies changed, run `uv sync` from the repository root before running the validator.

## Automatic checks

- `SKILL.md` exists at the skill root.
- YAML frontmatter parses and contains `name`, `description`, and `user-invocable`.
- A frontmatter `name` that differs from the folder name is reported.
- `context` without `compatibility` is reported because version-gated behavior should declare explicit compatibility bounds.
- Missing `<rules>` or `<workflow>` blocks are reported.
- Canonical template assets such as [skill-template.md](../assets/skill-template.md) and `agent-template.md` are checked for the exact leading `yaml` then `markdown` fence split and their fixed section order.
- `SKILL.md` longer than 500 lines is reported.
- Missing or empty `assets/` or `references/` is reported.
- Unresolved template leftovers such as `<what this skill does>`, `./references/<guide>.md`, or `./assets/<questions>.json` are reported.
- Non-frontmatter markdown files are checked for active `#tool:` or `#file:` markers outside fenced code blocks.
- `#tool:` markers are parsed, checked for trailing punctuation, and validated against the workspace skill-tool alias catalog.
- Wrong-layer raw tool names such as `copilot_readFile`, `run_in_terminal`, or `vscode_askQuestions` fail validation and include alias suggestions.
- If `.vscode/copilot-tools.snapshot.json` is missing, validation warns and falls back to installed extension manifests. For live discovery, use the chat `Configure Tools...` button or the `copilot-tool-snapshot` commands.
- `#file:` markers are parsed, checked for trailing punctuation, and best-effort checked for existence.
- Every file under `assets/`, `references/`, and `scripts/` **MUST** be referenced from `SKILL.md`.
- Canonical create-surface skills such as `create-skill`, `create-agent`, `create-prompt`, and `create-mcp` must include a non-empty `scripts/` directory with executable validation or automation.
- Duplicate normalized markdown headings are reported.
- A `## Runtime Inputs` section is reported because it front-loads support files instead of referencing them at point of need.
- Every `## Step X - ...` block inside `<workflow>` must start with an ordered `1.` action and keep runtime instructions inside numbered items instead of bare prose.
- `SKILL.md` must not keep more than 20 non-empty content lines after `</workflow>`; long matrices, checklists, setup guides, and reference appendices belong in `assets/` or `references/`.
- Early context-only workflow steps that batch 3 or more support-file reads before the first real action step are reported as potential front-loading.
- When a concept is repeated in both `SKILL.md` and a support markdown file, validation warns so one file can remain the canonical source.

## Fix patterns

- Missing frontmatter key -> add the missing key to the YAML header.
- Name mismatch -> rename the folder or change the `name` field so they match.
- `context` without `compatibility` -> add a `compatibility` field with the minimum VS Code and GitHub Copilot versions you have actually verified.
- Missing `.venv` or missing validator dependencies -> run `uv sync` from the repository root, then rerun the validator.
- Missing `<rules>` or `<workflow>` -> restore the canonical structure from [skill-template.md](../assets/skill-template.md).
- Template asset wrapper drift -> restore the exact `yaml` fence, `markdown` fence, and canonical section order from the matching template asset before changing any example content.
- Template leftovers such as `<what this skill does>` or `./references/<guide>.md` -> replace them with concrete wording and real file paths before publishing.
- Active `#file:` in a support markdown file -> replace it with a markdown link such as `[file](./path)` or `[file](../path)`.
- Active `#tool:` in a support markdown file -> replace it with plain prose or inline code such as `vscode/askQuestions`.
- Unknown or wrong-layer `#tool:` -> replace it with the skill-facing alias or namespaced tool accepted by the workspace.
- Snapshot warning -> refresh `.vscode/copilot-tools.snapshot.json` with `Agentic Workflow: Export Copilot Tool Snapshot`, check a candidate name with `Agentic Workflow: Check Copilot Tool Name`, or inspect the live UI with the chat `Configure Tools...` button.
- Unreferenced support file -> cite the file on the workflow step that consumes it.
- Missing `scripts/` on a canonical create-surface skill -> add a real validator or automation helper under `scripts/` and reference it from the workflow step that executes it.
- Excessive `#file:` usage for candidate or future inputs -> replace those references with markdown links and keep `#file:` only on the step that immediately consumes the file.
- `Runtime Inputs` warning -> move each `#file:` reference to the step where the agent actually needs that file.
- Plain-text step body -> rewrite the step so it starts with `1. ...` and keep the remaining runtime instructions inside ordered items, using nested `-` bullets only as supporting detail.
- Excessive post-workflow appendix -> move the repeated reference material into `assets/` or `references/`, keep only the workflow contract in `SKILL.md`, and leave no more than 20 non-empty content lines after `</workflow>`.
- Duplicate concept warning -> choose one canonical location, usually the support file, then replace the repeated `SKILL.md` prose with a short pointer to that file.
- Potential front-loading warning -> replace grouped early `#tool:read` calls with markdown links and move each actual `#tool:read` to the later step that truly consumes that support file.
- Trailing punctuation after `#file:` or `#tool:` -> rewrite the sentence so the reference stands alone.
- Duplicate headings -> merge the sections or rename one so only one canonical heading remains.

## Workspace notes

- `compatibility` is strongly recommended whenever a skill depends on version-gated behavior.
- `metadata` and `license` are optional local annotations; keep them concise if you use them.
- `## WHEN TO USE`, `## WHEN NOT TO USE`, and short `<definitions>` can help post-load routing, but the frontmatter `description` remains the main discovery surface.

## Status codes

- **ERROR**: **MUST** fix before publishing.
- **WARNING**: structural problem or quality issue that should usually be corrected.