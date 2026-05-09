# SKILL.md Format

```yaml
---
name: skill-name              # REQUIRED. Lowercase + hyphens only, 1-64 chars. MUST match parent folder name exactly — any deviation = silent load failure, no error shown.
description: 'What: <what this skill does>. When to use: <trigger phrases or scenarios that should cause the agent to load this skill>'
user-invocable: false          # ALWAYS false — skills are agent-only, never called by humans via slash commands.
disable-model-invocation: false # ALWAYS false — agent must be able to auto-load this skill based on context relevance.
# context: fork               # UNCOMMENT only if the skill reads many files or runs a lengthy multi-step investigation. Keeps intermediate steps out of the parent context; only the final result is returned. OMIT for short, focused skills that produce an inline edit or direct answer.
# compatibility: vscode 1.99+ # UNCOMMENT only if the skill relies on features introduced in a specific version (e.g., context:fork requires vscode 1.99+). Format: "vscode X.Y+, github-copilot X.Y+". OMIT if the skill uses only core SKILL.md fields available in all versions.
---
```

```markdown

<rules>

- Rules that guide the execution of the skill. For example, if the skill is about debugging, a rule could be "Always start by reproducing the issue and gathering logs before making any code changes."
</rules>
<workflow>

- High-level detailed procedure
</workflow>

## Helpers to guide through the usage of the skill.
```
