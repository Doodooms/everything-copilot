# Skill validation guide

Purpose
- Explains what `scripts/validate_skill.py` checks and where to look when it fails.
- The validator and its lint core both live in this skill's own `scripts/` directory.
- A repo-level wrapper may call this validator, but this skill package remains the source of truth for skill validation behavior.

When to use this file
- Read it after validation fails.
- In this repository, run `./.venv/bin/python .github/skills/create-skill/scripts/validate_skill.py --skill-dir <skill_folder>`.
- If `.venv` does not exist yet, or if dependencies changed, run `uv sync` from the repository root first.

What the script enforces
- Valid YAML frontmatter with `name`, `description`, and `user-invocable`.
- `name` and folder mismatch warnings.
- `context` without `compatibility` warnings.
- `<workflow>` and `<rules>` presence.
- Ordered `1.` actions at the start of every step block.
- Point-of-need support-file references.
- Active `#tool:` and `#file:` markers only in frontmatter-bearing definition files.
- Template placeholder rejection.
- Oversized post-workflow appendices rejection.

What still needs the final checklist
- Workspace-required `metadata`.
- The stricter local package rule that skills should keep `assets/`, `references/`, and `scripts/` present even when upstream would allow less.
- Conditional `compatibility` when the skill uses `context: fork`, newer tool surfaces, or other version-gated behavior.

Use [final-checklist.md](./final-checklist.md) after script validation to catch those remaining local requirements.

Fast fix map

```text
+--------------------------------------+---------------------------------------------+----------------------------------------------+
| Validator output                      | First place to look                         | Typical repair                               |
+--------------------------------------+---------------------------------------------+----------------------------------------------+
| Missing workflow or rules             | [skill-template](../assets/skill-template.md) | Restore the canonical structure            |
| Plain prose at top of step            | SKILL.md workflow                            | Move the text into the first ordered action  |
| Template leftovers                    | SKILL.md or template asset                   | Replace placeholders with real wording       |
| Wrong-layer tool or file markers      | Support markdown                             | Use markdown links or inline tool names      |
| Unreferenced support file             | SKILL.md                                     | Cite it at the exact point of need           |
| Too much content after </workflow>    | references/ or assets/                       | Move matrices or checklists out of SKILL.md  |
+--------------------------------------+---------------------------------------------+----------------------------------------------+
```

Keep one source of truth per concept. If a package rule, routing rule, or matrix already exists elsewhere in the skill package, point to it instead of rewriting it here.