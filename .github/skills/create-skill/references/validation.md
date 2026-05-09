# Skill validation checklist

Purpose
- Human-facing checklist describing the automatic checks performed by `scripts/validate_skill.py` and what authors should verify before publishing a skill.

How to use
- Run `python scripts/validate_skill.py .` from the skill folder (requires `typer`, `pyyaml`).
- Fix items marked ERROR first, then address WARNINGS if they matter for your workflow.

1) Files & layout
- [ ] `SKILL.md` exists at the skill root.
- [ ] `assets/` exists and contains at least one template (e.g. `skill-template.md`).
- [ ] `references/` exists and contains documentation (URIs, ask_questions guidance).
- [ ] `scripts/` exists (optional). If present, `scripts/validate_skill.py` should be runnable locally.

2) Frontmatter (YAML in top of `SKILL.md`)
- [ ] YAML frontmatter present and parseable.
- [ ] Required keys: `name` (string), `description` (string), `user-invocable` (bool).
- [ ] Optional recommended keys: `argument-hint`, `disable-model-invocation`.
- [ ] `name` matches the folder name and follows kebab-case (regex: `^[a-z0-9-]{1,64}$`).
- [ ] `description` <= 1024 characters.

3) Content constraints
- [ ] `SKILL.md` length <= 500 lines (prefer concise; use `references/` for heavy docs).
- [ ] Key sections present: Description, rules, workflow (or equivalent steps).
- [ ] Avoid implementation details (no runnable scripts embedded as instructions).
- [ ] `#tool:` references present where the skill needs external tools (e.g., `#tool:vscode/askQuestions`).
- [ ] `#file:` references use relative paths and point to files that exist (best-effort).

4) File-reference policy
- [ ] `#file:` paths should be one level deep where possible (e.g., `./assets/foo.md`, `./references/bar.md`) — keeps progressive loading predictable.
- [ ] No absolute or external repository paths inside `#file:`.

5) Assets & examples
- [ ] `assets/skill-template.md` (or equivalent) provides a working copy-paste example.
- [ ] If you require structured input, `assets/ask_questions.json` exists (machine template) AND `references/ask_questions.md` explains intent + examples for humans.

6) Tools & permissions
- [ ] Document which tools the skill expects `#tool:<name>` (e.g., `#tool:vscode/askQuestions`) inside the SKILL body where you instruct agents to use them.
- [ ] Remind integrators to include the corresponding `tools:` entry in any `.agent.md` that will run this skill (example below).

7) Naming, style & discoverability
- [ ] Include trigger phrases / “When to use” (help discovery).
- [ ] Provide at least one example invocation or sample `vscode_askQuestions` payload in `assets/` or `references/`.

8) Validation script expectations (if present)
- [ ] `scripts/validate_skill.py` runs without error and returns non-zero on fatal validation errors.
- [ ] The script prints ERRORS and WARNINGS clearly for editors to fix.

9) Audit & documentation
- [ ] Add a short `references/validation.md` (this file) explaining checks and the quick fix steps.
- [ ] Keep a `references/URIs.md` with primary external references (docs, style guides).

Common quick-fixes
- Missing frontmatter → add minimal YAML with `name`, `description`, `user-invocable`.
- Name mismatch → change `name` or rename folder to kebab-case.
- Missing assets → copy `assets/skill-template.md` into `assets/`.
- No `#tool:` where needed → add `#tool:vscode/askQuestions` in procedure step.

Status codes used by the validator
- ERROR: must fix before publishing.
- WARNING: recommended fix; not required.

(End of checklist)