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
<critical_rules>
- MUST keep work within this subskill’s declared scope and its specific safety or authority constraints.
- MUST NOT replace the parent domain skill’s admission, global routing, or authority boundaries.
</critical_rules>

<general_rules>
- SHOULD load listed references only at the procedure step that needs them.
- MAY report unavailable evidence or unresolved decisions as unknown.
</general_rules>

<risk_assessment>
Consume the Orchestrator-assigned `risk_level` through the parent domain skill; MUST NOT reclassify or downgrade it. SHOULD escalate only when new evidence materially increases risk. Scale evidence depth, not authority or approvals.
</risk_assessment>

<rules>
- MUST follow this selected subskill only within its declared procedure and scope.
- MUST NOT replace the parent domain skill’s admission, global routing, or authority boundaries.
- MUST return the result, evidence, remaining unknowns, risks, and status required by this procedure.
</rules>

<workflow>
## Step 1 - Inspect the current pack.

1. DO consume the assigned `risk_level` inherited from the parent domain skill before applying this procedure; then Read the pack's `pack.yaml`, version policy, requested contributions, and consumed files; consult the [pack contract](../references/create-plugin/references/plugin-contract.md).
2. Preserve its ID, source of truth, declared compatibility, and unrelated contributions; DO NOT scaffold over an existing pack.

## Step 2 - Apply the approved change.

1. Modify only the requested capability and use the existing authoring skill for any required skill or agent contribution.
2. Keep skills, agent contributions, MCP tool catalogs, and projections consistent; use exact published MCP tool names and preserve the [composition DAGs](../references/create-plugin/references/skill-composition.md).
3. MUST NOT add an agent, skill, or server merely to mirror a capability that fits an existing owner.

## Step 3 - Validate, build, and return.

1. From the repository root, use #tool:execute with `uv run --project <repository-root> python -m expertise validate [pack-id]` and `uv run --project <repository-root> python -m expertise test [pack-id]`.
2. Build every declared target with `uv run --project <repository-root> python -m expertise build [pack-id] --target [target]`; inspect diagnostics and exact output paths.
3. Return the pack ID/version, updated capability, compatibility impact, validation/build evidence, changed paths, unresolved risks, and next action. MUST NOT install, activate, stage, commit, or open a PR unless the handoff separately authorizes it.
</workflow>
