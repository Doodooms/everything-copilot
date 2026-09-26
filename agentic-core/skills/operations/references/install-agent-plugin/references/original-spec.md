# Original specification

## Raw intent

`TASK-CORE01` adds the approved `install-agent-plugin` workflow. The skill decides how to handle an explicit plugin installation request; deterministic lifecycle operations belong to `pluginctl`, not to a competing installer or compiler in this skill.

## Normalized requirements

- Confirm the plugin identity, trusted source, version/digest evidence, target host, target workspace, and user authorization before mutation.
- Validate the root manifest and package structure using locally available validation.
- Prefer `pluginctl` for lifecycle operations when it is available; otherwise use only a host-supported installation procedure verified from local authoritative documentation.
- Report installed, active, loaded, and pending-reload states distinctly, with reproducible evidence.

## Constraints

- Do not discover or download arbitrary plugins, install automatically, or infer trust from a name or URL.
- Do not invent host commands or compatibility guarantees.
- Do not compile packs, implement `pluginctl`, or claim that installation activates or reloads a plugin.

## Resolved decisions

- The package lives at `agentic-core/skills/install-agent-plugin/`.
- This is a policy/workflow skill, not a deterministic tool or a second lifecycle implementation.
- A missing trust decision, host capability, validation path, or explicit authorization stops the workflow before mutation.

**Provenance:** `SPEC-EXPERTISE1@3`, `TASK-CORE01`, `REQ-COREPLUGIN1`, `REQ-CORECORRECTIONS1`, `AC-COREPLUGIN1`, `AC-CORECORRECTIONS1`, `ADR-CORE001`, `ADR-CORE004`, and `ADR-CORE007`. Recorded 2026-09-24.
