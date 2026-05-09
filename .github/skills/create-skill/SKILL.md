---
name: create-skill
description: "What: How to create a skill based on the latest version of vscode and github-copilot. When to use: When the user is following a repeatable process that can be codified into a step-by-step workflow or when the user is asking for creating a new skill."
user-invocable: false
disable-model-invocation: true
---

<rules>

- A skill is a description of **HOW** workflow must be executed, not WHAT to execute. The skill should not include any implementation details, but rather focus on the process, rules, and guidelines for executing a task or workflow.

- Any file in the skill folder that is not referenced via `#file:` or `[link](./path)` in SKILL.md is **never loaded** by the agent. Unreferenced assets are invisible at runtime. The skill must refer precisely which file using one of the following syntaxes:

  - `#file:<file_path>` if the file is immediately **NECESSARY** to use the skill. For example, if the skill needs to reference the PLAN.md file, it should use `#file:../PLAN.md` to refer to the PLAN.md file located in the parent directory.
  
  - `[file](./<relative_file_path>)` if the file is a **SUPPLEMENTARY RESOURCE** that provides additional information or guidance but is not strictly necessary to execute the skill. For example, if the skill includes a test template that can be optionally used, it should reference it as `[test template](./assets/test-template.md)`.
  
- If a tool must be used, the skill must refer precisely which tool use with the syntax `#tool:<tool_name>`. For example, if the skill needs to ask the user a question, it should specify `use #tool:vscode/askQuestions` to refer to the askQuestions tool.

- A skill is NOT a single SKILL.md file, it is a folder containing a SKILL.md and any referenced scripts, assets, or resources needed to execute the workflow, see #file:./assets/skill-template.md for template and best practices.


</rules>

<workflow>

## Step 1 — Check latest guidelines

Start by reviewing the latest guidelines for creating skills in #file:./references/latest-docs.md, this will ensure that you are following the current best practices and requirements for skill creation.
Use #tool:agent/runSubagent with `agent_name: research` to help with redirecting URIs and extracting relevant information from the latest documentation to keep [latest docs](./references/latest-docs.md) up to date with the most recent guidelines.

## Step 2 — Identify the workflow to capture

- **IF** the conversation history contains a clear repeatable process: extract steps, decision points, and quality criteria directly from it.
- **ELSE**: use #tool:vscode/askQuestions with the questions defined in [ask questions](./assets/ask_questions.json).

Do NOT do both. One path or the other.

## Step 3 — Decide frontmatter

Before drafting, answer these questions to set the correct optional fields:
- Does the skill read many files or run a lengthy multi-step investigation? → include `context: fork`
- Does the skill rely on a feature not available in all VS Code versions? → include `compatibility`
- Otherwise: omit both.

## Step 4 — Draft

Follow #file:./assets/skill-template.md for frontmatter and #file:./assets/folder-template.md for file structure.
Iterate: identify the most ambiguous parts, ask targeted questions, refine until complete.

## Step 5 — Validate

Run: `python .github/skills/create-skill/scripts/validate_skill.py <skill_folder>`
Fix all ERRORs before proceeding. Address WARNINGs if relevant.

## Step 6 — Finalize

Summarize: what the skill produces, one example invocation, and propose the next related skill to create.

</workflow>

## Core Principles

1. **Keyword-rich descriptions**: Include trigger words for discovery in description yaml frontmatter.
2. **Progressive loading**: Keep SKILL.md under 200 lines; use reference files
3. **Relative paths**: Always use `./` for skill resources
4. **Self-contained**: Include all procedural knowledge to complete the task

## Anti-patterns

- **Vague descriptions**: "A helpful skill" doesn't enable discovery
- **Monolithic SKILL.md**: Everything in one file instead of references
- **Name mismatch**: Folder name doesn't match `name` field
- **Missing procedures**: Descriptions without step-by-step guidance