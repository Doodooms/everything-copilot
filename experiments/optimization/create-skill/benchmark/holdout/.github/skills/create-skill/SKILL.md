---
name: create-skill
description: "WHAT: Create or update deterministic VS Code skill packages from a clear specification. USE FOR: authoring, repairing, restructuring, reviewing, and validating a skill and its support files. DO NOT USE FOR: agents, prompts, MCP servers, hooks, benchmark optimization, or general application implementation."
user-invocable: true
context: fork
compatibility: vscode 1.119.0+, github-copilot 1.119.0+
metadata:
  creation-date: 2026-09-22
  creator: Doodooms
license: MIT
---

<definitions>

- **skill package**: A `SKILL.md` definition plus only the support files that its workflow actually consumes.
- **canonical architecture**: The repository-approved package topology and routing contract. Do not redesign it during skill creation.
- **mutable semantic region**: Wording, rules, examples, edge cases, and workflow guidance that may be authored or improved after the scaffold exists.
- **source specification**: The raw user intent, normalized requirements, constraints, and resolved decisions preserved in `references/original-spec.md`.
- **structural validation**: Deterministic checks that run before any expensive model evaluation and reject topology or contract violations.

</definitions>

<rules>

- Preserve the canonical architecture: `inline_workflow`, grouped `ACCEPT`/`REJECT` lists, and the repository-defined rejection contract.
- Keep the package skeleton deterministic. Never invent section topology, routing protocol, workflow placement, or required files during semantic authoring.
- Keep one source of truth per concept. Put executable workflow in `SKILL.md`; add a support file only when a workflow action consumes it.
- Every skill package is self-contained: its `SKILL.md`, support files, and scripts must work from the package without importing workspace modules or assuming repository-relative Python paths. The only external composition allowed is an explicit call to another skill.
- Use structured lists for admission and routing decisions. Use a table only when comparing several independent dimensions; never use ASCII tables for procedural instructions.
- Load support files at the step that needs them. Do not front-load a runtime inventory of references, assets, or scripts.
- Keep the user in the review loop: show the resulting `SKILL.md`, explain unresolved choices, and wait for confirmation before treating the package as ready.
- A direct-user orchestrator is an agent, not a skill. Route its creation or repair to `create-agent`; use the `create-agent` exception for an orchestrator with `user-invocable: true` and `disable-model-invocation: true`. That direct-user exception omits Step 0 because the user invokes the orchestrator directly, and it must not be generalized to other agents.

</rules>

<admission>

## ACCEPT

- Create a new skill package.
- Repair, restructure, normalize, review, or validate an existing skill.
- Update skill-specific templates, references, scripts, or frontmatter.

## REJECT

- Create or edit an agent -> `create-agent`.
- Create or edit the direct-user orchestrator agent -> `create-agent` using its documented no-Step-0 exception; this does not make orchestrator work a `create-skill` task.
- Create or edit a reusable prompt -> `create-prompt`.
- Create or edit an MCP server -> `create-mcp`.
- Optimize an already-created skill or design its evaluation benchmark -> `optimize-skill`.
- Define always-on repository guidance -> repository instructions.
- Implement general product behavior -> the relevant implementation skill.

For REJECT, return exactly:

```json
{"status":"rejected","skill":"create-skill","reason":"<concise reason>","routing":"<route or null>"}
```

</admission>

<workflow>

## Step 1 - Establish the specification

1. Use #tool:read to inspect the current target package when it exists, then use #tool:search to identify the requested repeatable behavior, boundaries, outputs, and acceptance evidence.
   - Reuse complete requirements already present in the request or conversation.
   - Use #tool:vscode/askQuestions with [question payload](./assets/ask_questions.json) to resolve only decisions that remain genuinely missing; consult [question guidance](./references/ask_questions.md) when deciding whether a question is necessary.
   - Do not ask for a second intake when the specification is already complete.

## Step 2 - Persist provenance and scaffold

1. Normalize the accepted request into [the required provenance file](./references/original-spec.md) before writing semantic content.
   - Include raw intent, normalized requirements, explicit constraints, resolved decisions, and provenance date.
2. Read [the skill template](./assets/skill-template.md) and [folder guidance](./assets/folder-template.md) only when deciding how the package will be authored, then use #tool:execute to run [scaffold.py](./scripts/scaffold.py) with the canonical architecture configuration.
   - Preserve `SKILL.md`, `references/original-spec.md`, and only the files required by the canonical configuration.
   - Do not create empty `assets/`, `references/`, or `scripts/` directories merely to satisfy a template.

## Step 3 - Fill the semantic regions

1. Write the frontmatter, definitions, grouped admission lists, routing contract, and inline workflow into the scaffold.
   - Keep `ACCEPT` and `REJECT` decisions before workflow actions.
   - For REJECT, return the structured JSON contract and do not begin the workflow.
   - Keep the first executable workflow action deterministic and directly tied to the accepted request.
2. Add a support file only when it removes real repeated context or supplies a reusable template, guide, asset, or executable check.
   - Reference it from the exact workflow action that consumes it with a relative Markdown link or skill-facing file marker.
   - Use `assets/` for copyable payloads, `references/` for point-of-need guidance, and `scripts/` for domain-specific executable checks.

## Step 4 - Validate the package

1. Use #tool:execute to run [validate.py](./scripts/validate.py); use [lint.py](./scripts/lint.py) when only Markdown and package-content linting is needed. The public scripts share the local [lint engine](./scripts/skill_lint_core.py); none imports workspace code.
   - Fix every structural error before continuing.
   - Resolve warnings that indicate duplicate admission logic, eager support-file loading, stale references, or unresolved placeholders.
2. Review [validation guidance](./references/validation.md) only when validator output needs interpretation, then use [latest docs](./references/latest-docs.md) only when host-version behavior is ambiguous.

## Step 5 - Review with the user

1. Present the completed package and [the final checklist](./references/final-checklist.md) to the user for review.
   - Confirm that the ontology, semantic contract, topology, examples, and rejection behavior match the user's intent.
   - Resolve requested edits collaboratively and rerun structural validation after each substantive change.
2. When the user explicitly requests optimization or benchmark design, hand off to [optimize-skill](../optimize-skill/SKILL.md) with the validated package and preserved provenance.

## Step 6 - Report completion

1. Summarize the created package, preserved provenance, validation commands, review status, and any semantic warnings.
   - Include one representative invocation and the exact files added or changed.

</workflow>
