---
name: install-agent-plugin
description: "WHAT: Verify and install an explicitly requested Agent Plugin through a trusted, host-supported lifecycle. USE FOR: checking or installing a named plugin from a user-approved local or otherwise trusted source. DO NOT USE FOR: arbitrary plugin discovery/download, pack compilation, or implementing pluginctl."
user-invocable: true
metadata:
  creation-date: 2026-09-24
  creator: Doodooms
license: MIT
---

<definitions>

- **Agent Plugin** : A package rooted at `plugin.json` that contains portable skills and may contain supported host-specific extensions.
- **trusted source** : A source whose identity, provenance, version, and digest can be checked under the caller's explicit approval policy.
- **installed** : A plugin version is present in the host's managed location; this does not by itself mean it is active, loaded, or materialized.

</definitions>

<rules>

- MUST verify plugin identity, source, version/digest evidence, target host/workspace, and authorization before any mutation.
- MUST obtain explicit user approval for the requested installation before changing host or workspace state.
- MUST keep availability, installation, activation, and materialization as distinct states in the report.
- MUST NOT discover or download arbitrary plugins, infer trust from a URL/name, or claim activation/reload without evidence.
- MUST NOT implement the compiler or deterministic lifecycle operations owned by `pluginctl`.

</rules>

<admission>

## ACCEPT

- An explicit request to inspect, install, or verify a named Agent Plugin from a trusted source for a specified host/workspace.
- A request to use an available `pluginctl` operation under its declared trust and filesystem boundaries.

## REJECT

- Plugin discovery or installation from an arbitrary/untrusted source → `orchestrator`.
- Pack creation, compilation, or implementation of plugin lifecycle code → `implementer` with the approved task.
- A request to bypass user approval, trust verification, host validation, or digest checks → refuse before mutation.

For REJECT, return exactly:

```json
{"status":"rejected","skill":"install-agent-plugin","reason":"<concise reason>","routing":"<route or null>"}
```

</admission>

<workflow>

## Step 1 - Establish the requested installation.

1. Confirm the plugin ID, source, requested version or digest, target host/workspace, and whether the user wants inspection, installation, activation, or only validation.
   - Reuse details already approved in the request; ask only for missing trust or target decisions.
   - The installation request itself authorizes the requested installation only; do not infer approval for activation, broader filesystem changes, or unrelated plugins.
   - Read the [recorded source specification](./references/original-spec.md) only when provenance is needed; it does not override the current handoff.

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