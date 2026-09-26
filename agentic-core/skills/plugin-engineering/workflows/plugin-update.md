---
id: plugin-update
description: Extend or repair an existing Expertise Pack while preserving its source
  and compatibility contract.
invoke_for:
- update an existing pack capability
- repair a pack manifest, contribution, projection, or target declaration
avoid_for:
- scaffold a new pack
references:
  - ../references/create-plugin/references/plugin-contract.md
  - ../references/create-plugin/references/skill-composition.md
---

## Step 1 - Inspect the current pack.

1. Read the pack's `pack.yaml`, version policy, requested contributions, and consumed files; consult the [pack contract](../references/create-plugin/references/plugin-contract.md).
2. Preserve its ID, source of truth, declared compatibility, and unrelated contributions; DO NOT scaffold over an existing pack.

## Step 2 - Apply the approved change.

1. Modify only the requested capability and use the existing authoring skill for any required skill or agent contribution.
2. Keep skills, agent contributions, MCP tool catalogs, and projections consistent; use exact published MCP tool names and preserve the [composition DAGs](../references/create-plugin/references/skill-composition.md).
3. MUST NOT add an agent, skill, or server merely to mirror a capability that fits an existing owner.
