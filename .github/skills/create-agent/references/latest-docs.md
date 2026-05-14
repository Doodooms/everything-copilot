# Latest Custom Agent Docs

## Purpose

- Use this file when the repository examples or your memory might be older than the current VS Code custom-agent surface.
- Use [validation](./validation.md) for repository-specific contract fixes. This file is only the upstream-doc summary.

## When to use this file

- You need to confirm current custom-agent frontmatter fields or defaults.
- You need to check current workspace file locations, tool-list behavior, or subagent rules.
- You need to confirm whether handoffs, hooks, `target`, or organization-level discovery are part of the current upstream surface.

## Current official sources

- VS Code custom agents docs: https://code.visualstudio.com/docs/copilot/customization/custom-agents
- VS Code subagents docs: https://code.visualstudio.com/docs/copilot/agents/subagents
- VS Code agent tools docs: https://code.visualstudio.com/docs/copilot/agents/agent-tools
- VS Code customization overview: https://code.visualstudio.com/docs/copilot/customization/overview

## Notes confirmed while editing this skill

- Workspace custom agents are documented under `.github/agents/`, with `.claude/agents/` also supported for Claude-format agent files.
- The upstream custom-agent file uses `.agent.md` plus Markdown body instructions.
- Upstream frontmatter supports fields such as `description`, `name`, `argument-hint`, `tools`, `agents`, `model`, `user-invocable`, `disable-model-invocation`, `target`, `handoffs`, and preview `hooks`.
- Upstream docs split picker visibility from subagent eligibility through `user-invocable` and `disable-model-invocation`, and mark `infer` as deprecated.
- If an agent specifies `agents`, the `agent` tool must also be present for delegation to work.
- The body can reference files with markdown links and tools with `#tool:<tool-name>` syntax.
- Upstream docs note that unavailable tools are ignored, even though this repository deliberately validates tool names and keeps tool lists narrow.

## Re-check triggers

- Re-check before adding `handoffs`, preview `hooks`, or a non-default `target`.
- Re-check when delegation, nested subagents, or organization-level agents are part of the task.
- Re-check when an upstream example appears to contradict the local validation contract.