---
id: install-agent-plugin
description: 'Apply the install-agent-plugin method: checking or installing a named
  plugin from a user-approved local or otherwise trusted source.'
invoke_for:
- checking or installing a named plugin from a user-approved local or otherwise trusted
  source
avoid_for:
- arbitrary plugin discovery/download, pack compilation, or implementing pluginctl
references: []
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
## Step 1 - Establish the requested installation.

1. DO consume the assigned `risk_level` inherited from the parent domain skill before applying this procedure; then Confirm the plugin ID, source, requested version or digest, target host/workspace, and whether the user wants inspection, installation, activation, or only validation.
   - Reuse details already approved in the request; ask only for missing trust or target decisions.
   - The installation request itself authorizes the requested installation only; do not infer approval for activation, broader filesystem changes, or unrelated plugins.
   - Read the [recorded source specification](../references/install-agent-plugin/references/original-spec.md) only when provenance is needed; it does not override the current handoff.

## Step 2 - Verify source and package.

1. Use #tool:read to inspect the plugin root's `plugin.json`, expected package structure, and local validation evidence before installation.
   - Verify that the manifest identity matches the request and that every declared local component stays within the trusted package.
   - Use `pluginctl` trust, version/digest, compatibility, and dependency checks when it is available.
   - If trust, digest, host compatibility, or validation evidence cannot be established, stop before mutation and report the missing evidence.
2. Do not fetch or install a plugin from the Internet or another source merely because it is named in a request; the caller must identify and approve the trusted source.

## Step 3 - Install through the supported lifecycle.

1. Use #tool:execute to run the exact bounded `pluginctl` install operation when available, passing only the approved source, version/digest, target, and approval policy.
2. If `pluginctl` is unavailable, use a host-native install procedure only when a local authoritative source or the user supplies the exact supported method.
   - Do not invent host commands or execute an undocumented installer.
   - If no verified host-supported method is available, return a blocker without attempting installation.

## Step 4 - Verify and report state.

1. Use #tool:execute for the verified status operation, or #tool:read for a host-provided status file, and report whether the plugin is available, installed, active, or loaded.
2. If activation or reload is separate or pending, state that explicitly; do not claim the plugin is ready until the host provides evidence.
3. Return the plugin identity/version/digest, source, target, approval basis, commands or host actions used, validation results, state transition, and remaining uncertainty.
</workflow>
