---
name: create-skill
description: "WHAT: Create or update deterministic VS Code skills with explicit tool and file references. USE FOR: creating or repairing skills, removing duplicate skill logic, tightening support-file loading, or updating skill frontmatter and validation conventions. DO NOT USE FOR: agents, prompts, MCP servers, or general coding tasks."
user-invocable: false
context: fork
compatibility: vscode 1.119.0+, github-copilot 1.119.0+
metadata: 
  creation-date: 2026-05-09
  creator: Doodooms
license: MIT
---

<definitions>

- **skill** : A package of repeatable workflow guidance that a workspace agent can route to and execute. It consists of a `SKILL.md` file with YAML frontmatter and markdown content, plus any number of support files under `assets/`, `references/`, and `scripts/` that are cited from `SKILL.md`.

- **agent** : A process that can execute deterministic workflows, use tools, and read and write files. Agents can invoke skills when they detect a relevant context or receive an explicit user request.

- **prompt** : A reusable text snippet that an agent can conditionally include in its context when invoking a skill or executing a workflow step. Prompts are not deterministic guidance; they are suggestions or examples that the agent may choose to use.

- **tool** : An action the agent can take that has an effect outside of its own internal state. Tools include things like reading a file, executing code, asking the user a question, or invoking another agent. Each tool has a specific syntax for how it is cited from `SKILL.md` and how it is invoked by the agent.

- **mcp server** : A local or remote service that implements the MCP protocol to expose tools, memory, and other capabilities to agents. A skill may depend on certain tools being available from the MCP server, and it should cite those tools with their skill-facing aliases.

- **workflow** : A sequence of deterministic steps that an agent must execute to accomplish a task. A workflow does not contain behavioral instructions ("you are", "your mission is").

- **skill-facing tool** : an accessible tool for a skill via the syntax `#tool:<tool_name>`. It is a simplified alias (e.g., "read") that hides the internal technical name of the tool (e.g., "copilot_readFile"). The mapping is managed by the Copilot agent layer.

- **support file** : A file located in assets/, references/, or scripts/ that is referenced from SKILL.md. It is never loaded automatically; it must be explicitly cited on the workflow line that consumes it.

</definitions>

<workflow>

## Step 0 - **CONFIRMATION**

1. USE #tool:read **IMMEDIATELY** on #file:./references/confirmation-matrix.md to confirm with **certainty** if this skill should be used.
2. **If and ONLY if** you are **certain**, read the following rules and workflow steps to understand how the skill works and what it requires for execution.

<rules>

- A skill describes **HOW** to execute a repeatable workflow. Keep implementation detail in referenced assets or scripts **ONLY** when a workflow step actually needs them.

- Give each file in the skill folder one responsibility. `SKILL.md` **MUST** own workflow, `assets/` own copyable templates or payloads, `references/` own human guidance consulted at a specific step, and `scripts/` own executable checks.

- There **MUST** be one source of truth per concept. If a rule, matrix, or checklist already lives in one section or support file, later steps **MUST** point to that canonical location instead of restating it.

- Use ASCII tables or matrices for contrastive choices such as primitive selection, scope, access mode, and use or do-not-use boundaries. Keep procedural workflow in markdown headings plus ordered `1.` actions, and place narrow sub-checks or exceptions under those actions as `-` bullets when that reads cleaner than extra top-level items.

- Use skill-facing `#tool:` names **ONLY**. Valid names come from the workspace agent tool layer and namespaced tools exposed there, for example `read`, `search`, `agent`, `execute`, `web`, `browser`, `todo`, and `vscode/askQuestions`.

- If a skill relies on behavior that is unavailable in older VS Code or GitHub Copilot builds, it **MUST** declare a `compatibility` frontmatter field.

- `metadata` is a required workspace convention for authorship and provenance. `license` is optional. Neither replaces a precise `description` or `compatibility` field.

- A workspace skill **MUST** be a complete package: `SKILL.md`, `assets/`, `references/`, and `scripts/`. If one piece is missing, the skill package is incomplete.

- Reference `#file:` **ONLY** at the point of need. **NEVER** front-load support files or tool lists in a `Runtime Inputs` section.

- Every runtime-relevant file under `assets/`, `references/`, and `scripts/` **MUST** still be referenced from `SKILL.md`, but **ONLY** on the workflow line that consumes it.

- Active `#tool:` and `#file:` markers **MUST ONLY** appear in frontmatter-bearing definition files such as `SKILL.md`, `.agent.md`, and `.prompt.md`. In support markdown files under `assets/` or `references/`, **USE** markdown links for files and plain or inline-coded tool names.

- Keep `#file:` references relative and free of trailing punctuation.

</rules>

## Step 1 - Inspect the current skill state

1. Inspect the current skill package before you draft changes.
  - If the target skill already exists, use #tool:read on its current `SKILL.md` first.
  - Read only the already-known support files that still define live behavior.
2. Narrow the change surface only when it is still unclear.
  - If overlap, stale references, or dead support files are unclear, use #tool:agent with a read-only exploration agent to locate them.
  - Stop once you can name the files that actually need edits.
3. Confirm host requirements only for live ambiguities.
  - Use #tool:read on #file:./references/latest-docs.md only when current VS Code skill requirements matter to the draft.
  - If the request is still ambiguous after Step 0 confirmation, use #tool:read on #file:./references/decision-matrices.md only for primitive, scope, or access-mode choices that remain unclear.

## Step 2 - Capture missing workflow information

1. Reuse the workflow already present in the conversation when it is complete.
  - Extract the repeatable steps, decisions, and outputs directly from the existing request.
  - Do **NOT** ask for facts that are already fixed by the conversation.
2. Load guidance and the questionnaire only when behavior-changing details are missing.
  - Use #tool:read on #file:./references/ask_questions.md and #file:./assets/ask_questions.json only when structured input is still needed.
  - Include required MCP servers, workspace tools, local scripts, or external services in that intake if they change how the skill must be authored.
  - Then use #tool:vscode/askQuestions to collect only the missing answers.
3. Keep one intake path.
  - **DO NOT** both derive the workflow from history and run the questionnaire.

## Step 3 - Draft the skill package

1. Load the canonical scaffolds before you write the target package.
  - Use #tool:read on #file:./assets/skill-template.md when writing the target `SKILL.md`.
  - Use #tool:read on #file:./assets/folder-template.md when deciding which support files belong under `assets/`, `references/`, and `scripts/`.
2. Set frontmatter deliberately before you expand the body.
  - Keep `description` as the primary discovery surface.
  - Add `compatibility` for version-gated behavior, keep `metadata` because this workspace requires it, and treat `license` as optional.
3. Assign one canonical home for each reusable concept before writing full prose.
  - Keep executable workflow in `SKILL.md`.
  - Put matrices, checklists, and setup guidance in support files only when a workflow line actually consumes them.
4. Compare the draft against the bad and good examples before validation.
  - Use the examples in #file:./assets/skill-template.md to catch vague discovery text, split routing, front-loaded references, or support-doc marker leaks.

## Step 4 - Check references while drafting

1. Check tool references before you validate.
  - Ensure every `#tool:` names a skill-facing workspace tool or namespaced tool that actually exists.
  - Treat the examples in this skill as examples, **NOT** a closed list.
2. Check file references at the same time.
  - Ensure every runtime-relevant support file is referenced from `SKILL.md` at point of need with `#file:` or `[link](./...)`.
  - Use `#file:` for immediate consumption and markdown links for optional reading.
3. Check support-document hygiene.
  - Ensure support markdown files **NEVER** contain active `#tool:` or `#file:` markers.
  - **USE** markdown links there for files and plain or inline-coded tool names.
4. Collapse duplicate guidance before it spreads.
  - If extra routing help is still needed after the frontmatter `description`, keep it in one dense support surface or a short `<definitions>` block.
  - If a section starts repeating policy already defined elsewhere, replace the repeated prose with a short pointer to the canonical section or file.

## Step 5 - Validate

1. Run the local validator first.
  - Use #tool:execute to run #file:./scripts/validate_skill.py with the repository interpreter: `./.venv/bin/python .github/skills/create-skill/scripts/validate_skill.py --skill-dir <skill_folder>`.
  - The validator and its lint core both live under this skill's own `scripts/` directory. Repo-level wrappers may call them, but they are not the source of truth.
2. Refresh the environment only if validation prerequisites are missing.
  - If `.venv` does not exist yet, or if dependencies changed, run `uv sync` from the repository root before validating.
3. Load the fix guide only when the output needs interpretation.
  - If validation returns tool, file, or structure issues, use #tool:read on #file:./references/validation.md and apply the matching fix.
  - If the validator behavior itself needs inspection, review [skill lint core](./scripts/skill_lint_core.py) at this step.
4. Run the final local audit after script validation.
  - Use #tool:read on #file:./references/final-checklist.md and resolve every unchecked item or state why it does not apply.
5. Treat errors and warnings deliberately.
  - Fix **ALL** ERRORs before proceeding.
  - Address WARNINGs when they indicate duplicated structure, eager file loading, or stale support files.

## Step 6 - Finalize

1. Summarize the finished skill package.
  - State what the skill produces.
  - State which support files it depends on.
  - Give one example invocation that should load it.

</workflow>
