```yaml
---
name: <agent-name>              # REQUIRED. Lowercase + hyphens only, 1-64 chars.
description: "What: <one-sentence summary of this agent's unique purpose and capabilities>. When to use: <trigger phrases or scenarios that should cause the orchestrator to load this agent as a subagent.>"
model: Claude Sonnet 4.6 (copilot)
tools: [tool1, tool2, ...]  # OPTIONAL. List of tool aliases this agent requires. Omit for no tools.
agents: [agent1, agent2, ...]  # OPTIONAL. List of other agents this agent may call as subagents. Omit for none.
github: {
  permissions: {
    pull-requests: write, issues: write
    }
}
hooks: 
  SessionStart:
    - type: command
      command: "a command to run at the start of every session, for example to initialize context or load relevant files"
---
```