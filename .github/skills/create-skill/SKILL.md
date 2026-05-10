---
name: create-skill
description: "What: Create or update deterministic VS Code skills with explicit tool and file references. When to use: creating or repairing skills, removing duplicate skill logic, tightening support-file loading, or updating skill frontmatter and validation conventions. Do not use for agents, prompts, MCP servers, or general coding tasks."
user-invocable: false
context: fork
compatibility: vscode 1.119.0+, github-copilot 1.119.0+
metadata: 
  creation-date: 2026-05-09
  creator: Doodooms
license: MIT
---
## WHEN TO USE

- Migrating a skill away from legacy tool or file-reference syntax.
- Auditing an existing skill folder for dead support files or duplicated guidance.
- Standardizing a skill so support files load only at point of need.
- Adding or tightening validator rules for skill authoring.

## WHEN **NOT** TO USE
- Creating or editing a custom agent, prompt, or MCP server instead of a skill.
- General coding or debugging tasks that do not change skill authoring behavior.
- One-off documentation edits that do not affect skill loading, routing, or validation.
- Runtime tool-registry investigation when no skill package is being authored.

<definitions>

- **workflow** : A sequence of deterministic steps that an agent must execute to accomplish a task. A workflow does not contain behavioral instructions ("you are", "your mission is").

- **skill-facing tool** : an accessible tool for a skill via the syntax `#tool:<tool_name>`. It is a simplified alias (e.g., "read") that hides the internal technical name of the tool (e.g., "copilot_readFile"). The mapping is managed by the Copilot agent layer.

- **support file** : A file located in assets/, references/, or scripts/ that is referenced from SKILL.md. It is never loaded automatically; it must be explicitly cited on the workflow line that consumes it.

</definitions>

<rules>

- A skill describes **HOW** to execute a repeatable workflow. Keep implementation detail in referenced assets or scripts **ONLY** when a workflow step actually needs them.

- Give each file in the skill folder one responsibility. `SKILL.md` **MUST** own workflow, `assets/` own copyable templates or payloads, `references/` own human guidance consulted at a specific step, and `scripts/` own executable checks.

- There **MUST** be one source of truth per concept. If a rule, matrix, or checklist already lives in one section or support file, later steps **MUST** point to that canonical location instead of restating it.

- Use skill-facing `#tool:` names **ONLY**. Valid names come from the workspace agent tool layer and namespaced tools exposed there, for example `read`, `search`, `agent`, `execute`, `web`, `browser`, `todo`, and `vscode/askQuestions`.

- If a skill relies on behavior that is unavailable in older VS Code or GitHub Copilot builds, it **MUST** declare a `compatibility` frontmatter field.

- `metadata` and `license` are optional workspace conventions. They **MAY** be used for authorship or provenance, but they do **NOT** replace a precise `description` or `compatibility` field.

- Reference `#file:` **ONLY** at the point of need. **NEVER** front-load support files or tool lists in a `Runtime Inputs` section.

- Every runtime-relevant file under `assets/`, `references/`, and `scripts/` **MUST** still be referenced from `SKILL.md`, but **ONLY** on the workflow line that consumes it.

- Active `#tool:` and `#file:` markers **MUST ONLY** appear in frontmatter-bearing definition files such as `SKILL.md`, `.agent.md`, and `.prompt.md`. In support markdown files under `assets/` or `references/`, **USE** markdown links for files and plain or inline-coded tool names.

- Keep `#file:` references relative and free of trailing punctuation.

</rules>

<workflow>

## Step 1 - Inspect the current skill state

If the target skill already exists, use #tool:read on its current `SKILL.md` and on any already-known support files that define current behavior.
If the affected surface is unclear, use #tool:agent with a read-only exploration agent to locate stale references, duplicated guidance, and support files that are no longer used.
Use #tool:read on #file:./references/latest-docs.md before drafting when you need to confirm current VS Code skill requirements.

## Step 2 - Capture missing workflow information

If the conversation already contains a repeatable workflow, extract the steps, decisions, and outputs directly from it.
Otherwise, use #tool:read on #file:./references/ask_questions.md and #file:./assets/ask_questions.json and then use #tool:vscode/askQuestions to collect only the missing structured answers.
**DO NOT** both derive the workflow from history and run the questionnaire.

## Step 3 - Draft the skill package

Use #tool:read on #file:./assets/skill-template.md when writing the target `SKILL.md`.
Use #tool:read on #file:./assets/folder-template.md when deciding which support files belong under `assets/`, `references/`, and `scripts/`.
Set frontmatter deliberately: `description` remains the primary discovery surface, `compatibility` is required for version-gated features, and `metadata` or `license` are optional workspace-local annotations.
Assign exactly one canonical home for each reusable concept before writing full prose.
Compare the draft against the bad and good examples in #file:./assets/skill-template.md before you validate it.
When a support file is needed, cite it on the workflow line that consumes it instead of preloading it in a global list.

## Step 4 - Check references while drafting

Ensure every `#tool:` names a skill-facing workspace tool or namespaced tool actually available to the workspace. Treat the examples in this skill as examples, **NOT** a closed list.
Ensure every runtime-relevant support file is referenced from `SKILL.md` at point of need with `#file:` or `[link](./...)`.
Ensure support markdown files **NEVER** contain active `#tool:` or `#file:` markers. **USE** markdown links there for files and plain or inline-coded tool names.
Use `## WHEN TO USE`, `## WHEN NOT TO USE`, and short `<definitions>` blocks when they sharpen routing or clarify terms, but keep them brief. They help after the skill is loaded; the frontmatter `description` still drives initial discovery.
If a section starts repeating policy already defined elsewhere, replace the repeated prose with a short pointer to the canonical section or file.

## Step 5 - Validate

Use #tool:execute to run #file:./scripts/validate_skill.py with the repository interpreter: `./.venv/bin/python .github/skills/create-skill/scripts/validate_skill.py --skill-dir <skill_folder>`.
If `.venv` does not exist yet, or if dependencies changed, run `uv sync` from the repository root before validating.
If validation returns tool, file, or structure issues, use #tool:read on #file:./references/validation.md and apply the matching fix.
Fix **ALL** ERRORs before proceeding. Address WARNINGs when they indicate duplicated structure, eager file loading, or stale support files.

## Step 6 - Finalize

Summarize what the skill produces, which support files it depends on, and one example invocation.

</workflow>
