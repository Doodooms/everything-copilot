# Pack Authoring Inputs

Fill the fields before scaffolding. Keep each capability narrow enough to project only the required skills, agents, and MCP servers.

```yaml
pack:
  id: [pack-id]
  type: [horizontal-or-vertical]
  name: [human-readable-name]
  version: [semver]
  description: [one-sentence-purpose]
  publisher: [publisher]
  source: [canonical-source]
  targets:
    - portable
    - copilot
    - codex

capability:
  id: [capability-id]
  description: [capability-purpose]

starter_skill:
  id: [skill-id]
  description: [skill-admission-description]

project_to_core_agents:
  - [agent-id]

optional:
  agent_contributions:
    - [agent-id]
  mcp_servers:
    - id: [mcp-server-id]
      capabilities:
        - [capability-id]
      permissions:
        - [permission]
      tools:
        - [exact-tool-name-from-tools-list]
```

For a starter source tree under the current repository root:

```sh
PYTHONDONTWRITEBYTECODE=1 ./.venv/bin/python -m expertise scaffold [pack-id] \
  --type [horizontal-or-vertical] \
  --name "[human-readable-name]" \
  --description "[one-sentence-purpose]" \
  --capability [capability-id] \
  --skill-id [skill-id] \
  --skill-description "[skill-admission-description]" \
  --publisher "[publisher]" \
  --source "[canonical-source]" \
  --project-to [agent-id] \
  --target portable \
  --target copilot \
  --target codex
```

Repeat `--project-to` for each core agent and omit it when the pack does not extend core agents. Repeat `--target` only for the targets the pack promises to support.