# Skill validation guide

## Purpose

- Explains what `scripts/validate.py` checks and where to look when it fails.
- The validator and its lint core both live in this skill's own `scripts/` directory.
- A repo-level wrapper may call this validator, but this skill package remains the source of truth for skill validation behavior.

## When to use this file

- Read it after validation fails.
- Run `python scripts/validate.py --skill-dir <skill_folder>` from the package. `lint.py` and `validate.py` use only the package-local lint engine; they do not import repository modules.
- If `.venv` does not exist yet, or if dependencies changed, run `uv sync` from the repository root first.

## What the script enforces

- Valid YAML frontmatter with `name`, `description`, and `user-invocable`.
- `name` and folder mismatch warnings.
- `context` without `compatibility` warnings.
- `<workflow>` and `<rules>` presence.
- Ordered `1.` actions at the start of every step block.
- Point-of-need support-file references.
- Active `#tool:` and `#file:` markers only in frontmatter-bearing definition files.
- Template placeholder rejection.
- Oversized post-workflow appendices rejection.

## What still needs the final checklist

- Workspace-required `metadata`.
- Support directories are conditional. The repository validator checks the required `SKILL.md` structure; skill-local scripts are optional and must verify skill behavior rather than package shape.
- Conditional `compatibility` when the skill uses `context: fork`, newer tool surfaces, or other version-gated behavior.

Use [final-checklist.md](./final-checklist.md) after script validation to catch those remaining local requirements.

## Fast fix map

- **Missing workflow or rules:** restore the current structure from [skill-template](../assets/skill-template.md).
- **Plain prose at the top of a step:** move it into the first ordered action in `SKILL.md`.
- **Template leftovers:** replace placeholders in `SKILL.md` or the template asset with real wording.
- **Wrong-layer tool or file markers:** use Markdown links and inline tool names in support Markdown.
- **Unreferenced support file:** add a relative Markdown link from `SKILL.md` at the workflow action that consumes it.
- **Stale confirmation section or ASCII table:** use the current numbered workflow and structured lists.
- **Too much content after `</workflow>`:** move matrices, checklists, and setup guides into `references/` or `assets/`.

Keep one source of truth per concept. If a package rule, routing rule, or matrix already exists elsewhere in the skill package, point to it instead of rewriting it here.