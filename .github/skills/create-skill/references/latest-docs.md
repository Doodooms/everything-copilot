# Latest Agent Skills Docs

## Purpose

- Use this file when the repository examples or your memory might be older than the current VS Code Agent Skills surface.
- Use [validation](./validation.md) for repository-specific contract fixes. This file is only the upstream-doc summary.

## When to use this file

- You need to confirm the current upstream skill frontmatter fields or default behaviors.
- You need to check current skill discovery, slash-command, or progressive-loading behavior.
- You need to confirm official skill locations, plugin packaging, or the current `context: fork` guidance.

## Current official sources

- VS Code Agent Skills docs: https://code.visualstudio.com/docs/copilot/customization/agent-skills
- VS Code customization overview: https://code.visualstudio.com/docs/copilot/customization/overview
- Agent Skills specification: https://agentskills.io/specification
- VS Code agent plugins docs: https://code.visualstudio.com/docs/copilot/customization/agent-plugins

## Notes confirmed while editing this skill

- Valid upstream skill frontmatter includes `name` and `description` as required fields, plus optional `argument-hint`, `user-invocable`, `disable-model-invocation`, and `context`.
- The skill `name` must match the parent folder name, use lowercase letters, numbers, and hyphens only, and invalid names fail silently.
- `description` is the upstream discovery surface and should explain both what the skill does and when to use it.
- `user-invocable` defaults to `true`, while `disable-model-invocation` defaults to `false`.
- `context: fork` remains experimental and is intended for larger workflows whose intermediate work should stay out of the parent context.
- VS Code documents progressive loading: discovery from frontmatter first, then `SKILL.md`, then only the files referenced from the skill body.
- Workspace skill discovery includes `.github/skills/`, `.claude/skills/`, and `.agents/skills/`, with optional extra locations via `chat.agentSkillsLocations`.
- Extension-contributed skills still require the directory name to match the `name` field.

## Re-check triggers

- Re-check before adding or relying on a newer frontmatter field.
- Re-check before using `context: fork` as a hard requirement.
- Re-check when plugin packaging or alternative skill locations are part of the task.
