# Agent Validation Guide

Purpose

- Explains what `scripts/validate_agent.py` checks and how to fix its output.
- Use [agent-template.md](../assets/agent-template.md) for the canonical self-contained agent example.

When to use this file

- Read it after validation fails or when you need to understand what the validator enforces.
- In this repository, run the validator with `./.venv/bin/python .github/skills/create-agent/scripts/validate_agent.py --agent-file <agent_file>`.
- If `.venv` does not exist yet, or if dependencies changed, run `uv sync` from the repository root before running the validator.

Automatic checks

- YAML frontmatter parses and the body is not empty.
- `description` warnings cover missing `WHAT:`, `USE FOR:`, or `DO NOT USE FOR:` clauses.
- The canonical wrapped agent shape keeps `<definitions>`, `<workflow>`, `## Step 0 - **CONFIRMATION**`, `## Role`, `<rules>`, `## Responsibilities`, `## Constraints`, `## Output Contract`, `## Step 1 - ...`, `## Step 2 - ...`, and `## Step 3 - ...` in order.
- Canonical self-contained Step 0 agents embed `### USE FOR` and `### DO **NOT** USE FOR` inside the `.agent.md` file.
- Canonical agents keep a refusal payload with `status: refused`, `agent`, `reason`, and `suggested_alternative`.
- Wrong-layer or unknown tool names are rejected through the shared workspace tool catalog.
- Unknown allowed subagents are rejected.
- Broad `agent` usage without an explicit `agents:` allowlist is warned.
- Legacy routing-file agents are still recognized, but they warn and must keep valid sibling routing files if they still use that older mode.

Fix patterns

- Missing embedded routing sections -> add `### USE FOR` and `### DO **NOT** USE FOR` under Step 0.
- Old sibling routing references in a new draft -> move the routing bullets into Step 0 and remove the file reads.
- Missing refusal JSON -> add the structured refusal payload in Step 0 or `## Output Contract`.
- Wrong-layer tool name -> replace it with the workspace alias or namespaced tool the validator suggests.
- Broad delegation -> either remove `agent` or add an explicit `agents:` allowlist.
- Unknown allowed subagent -> fix the agent name or create that agent first.

Status codes

- ERROR: must fix before publishing the agent.
- WARNING: the agent will run, but the contract is still broader, older, or less precise than the workspace standard.# Agent validation guide

## Purpose

- Explains what `scripts/validate_agent.py` checks and how to fix its output.
- Use [agent-template.md](../assets/agent-template.md) as the canonical starting point when validation points to structural problems.

## When to use this file

- Read it after generated `.agent.md` validation fails.
- In this repository, run the validator with `./.venv/bin/python .github/skills/create-agent/scripts/validate_agent.py --agent-file <agent_file>`.
- If `.venv` does not exist yet, or if dependencies changed, run `uv sync` from the repository root before validating.

## Automatic checks

- The file ends with `.agent.md`.
- YAML frontmatter parses and the body is not empty.
- `description` exists and is a non-empty string.
- `description` is checked for `WHAT:`, `USE FOR:`, and `DO NOT USE FOR:` guidance because routing weakens when the scope or refusal boundary is implicit.
- Canonical step-based agents are checked for `<definitions>`, a `<workflow>` wrapper, `## Step 0 - **CONFIRMATION**`, `## Role`, a `<rules>` block with `## Responsibilities`, `## Constraints`, `## Output Contract`, and `## Step 1/2/3` in canonical order.
- Canonical step-based agents must read `references/USEFOR.md` plus `references/DONOTUSEFOR.md`, refuse mismatches, and return a JSON refusal payload with `status`, `agent`, `reason`, and `suggested_alternative`.
- Canonical step-based agents must live in a dedicated package directory so `./references/USEFOR.md` and `./references/DONOTUSEFOR.md` resolve per-agent.
- Legacy heading-only agents are still accepted for compatibility, but they are reported as using the older contract.
- `<role>` wrappers are rejected in generated agents.
- Unresolved template placeholders are rejected when angle-bracket drafting text is still present.
- `tools` are checked against the workspace tool catalog, with suggestions for wrong-layer names such as `vscode_askQuestions`.
- `tools`, `agents`, `handoffs`, `hooks`, and `model` use the expected shapes.
- `agents:` requires the `agent` tool.
- `agents:` entries must not reference the current agent and must resolve to existing workspace agent names unless `*` is used intentionally.
- `handoffs[*].agent` targets must resolve to existing workspace agent names and must not point back to the current agent.
- `agent` in `tools` without an `agents:` allowlist is reported as a warning because it grants broad delegation.
- Deprecated `infer` is reported as a warning.
- Descriptions that omit `USE FOR:` or `DO NOT USE FOR:` are reported as warnings because routing becomes weaker.
- Duplicate tools and overly broad tool lists are reported as warnings.
- Files outside `.github/agents/` are reported as warnings because this repository defaults to workspace agents there.
- When `.vscode/copilot-tools.snapshot.json` is missing, validation warns and falls back to installed extension manifests. For live tool discovery, use the chat `Configure Tools...` button or the `copilot-tool-snapshot` commands.

## Fix patterns

- Missing frontmatter -> add the YAML header before the body.
- Empty `description` -> write a concise sentence that states what the agent does and when it should be chosen.
- Missing `WHAT:`, `USE FOR:`, or `DO NOT USE FOR:` -> rewrite `description` so it clearly states the job, the routing triggers, and the refusal boundary.
- Missing Step 0 contract -> restore the canonical structure from [agent-template.md](../assets/agent-template.md): Step 0 confirmation, Role, `<rules>`, then Step 1/2/3.
- Missing routing files -> create `references/USEFOR.md` and `references/DONOTUSEFOR.md` beside the agent file.
- Flat single-file path for a strict Step 0 agent -> move it to `.github/agents/<slug>/<slug>.agent.md` so the routing files live next to the agent.
- Workflow sections out of order -> restore the canonical agent section order from [agent-template.md](../assets/agent-template.md) instead of improvising a new layout.
- Broken `<workflow>` or `<rules>` wrapper -> either remove the partial wrapper or restore the full pair exactly as shown in [agent-template.md](../assets/agent-template.md).
- Missing refusal guidance -> Step 0 or `## Output Contract` must include the JSON refusal payload with `status`, `agent`, `reason`, and `suggested_alternative`.
- `<role>` wrapper -> replace it with the canonical `## Role` heading inside the workflow body.
- Unresolved template placeholder -> replace every angle-bracket drafting instruction with real agent-specific content before finalizing.
- Unknown or wrong-layer tool name -> replace it with a workspace agent-facing tool name accepted by the validator. If the live name is unclear, use the chat `Configure Tools...` button or the `copilot-tool-snapshot` workflow before guessing.
- `agent` without `agents:` -> add an explicit allowlist or remove `agent` from `tools`.
- `agents:` without `agent` in `tools` -> add `agent` to `tools` or remove `agents:`.
- Unknown subagent or handoff target -> point it to an existing `.github/agents/**/<slug>.agent.md` name or remove the reference.
- Self-referencing `agents:` or `handoffs` target -> remove the self-reference and route to another existing agent instead.
- Deprecated `infer` -> replace it with `user-invocable` and `disable-model-invocation`.
- Warning about routing text -> add `USE FOR:` and `DO NOT USE FOR:` clauses to `description`.
- Warning about broad tools -> remove tools the agent does not need.
- Warning about file location -> move the file to `.github/agents/` unless a different scope was explicitly requested.

## Status codes

- **ERROR**: must fix before the agent is ready.
- **WARNING**: quality or routing issue that should usually be corrected.