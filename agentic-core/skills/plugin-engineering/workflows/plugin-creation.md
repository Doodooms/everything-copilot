---
id: plugin-creation
description: Scaffold and compose a new bounded Expertise Pack from an approved capability
  request.
invoke_for:
- create a new Expertise Pack
- scaffold a new pack with selected skills, agent contributions, or MCP integrations
avoid_for:
- modify an existing pack
references:
  - ../references/create-plugin/references/plugin-contract.md
  - ../references/create-plugin/references/skill-composition.md
---

## Step 1 - Define and scaffold the pack.

1. Read the [pack contract](../references/create-plugin/references/plugin-contract.md) and [pack options template](../references/create-plugin/assets/pack-options-template.md); confirm the unique ID, capability boundary, type, publisher/source, first skill, target set, and required projections.
   - Only when maintaining `create-plugin` itself, consult its [original specification](../references/create-plugin/references/original-spec.md) and [scaffold configuration](../references/create-plugin/assets/scaffold-config.json).
2. From the repository root, run `PYTHONDONTWRITEBYTECODE=1 ./.venv/bin/python -m expertise scaffold [pack-id]` with explicit `--type`, `--name`, `--description`, `--capability`, `--skill-id`, `--skill-description`, `--publisher`, `--source`, `--target`, and only required `--project-to` options.
   - The canonical CLI creates the source manifest and starter skill. If it is unavailable or rejects the input, stop and report the exact diagnostic; MUST NOT hand-write a substitute.

## Step 2 - Compose only required contributions.

1. For each required skill, compose the `skill-authoring` procedure with the [child handoff template](../references/create-plugin/assets/child-handoff-template.md), a pack-owned output path, bounded requirements, expected validation, and exact parent resume point.
2. Add an agent contribution only when the capability needs a durable persona; compose the `agent-authoring` procedure with its exact pack path and only cataloged, projected MCP tool names.
3. Add an MCP declaration only for a required deterministic tool capability; route new server code to Implementer using `create-mcp`, or project an existing server from its authoritative tool catalog. Route host configuration, installation, and deployment to DevOps.
4. Integrate successful returns in `pack.yaml`; preserve the [composition DAGs](../references/create-plugin/references/skill-composition.md), validate each child result, and MUST NOT create workspace duplicates.
