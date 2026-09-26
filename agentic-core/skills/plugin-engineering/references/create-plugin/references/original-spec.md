# Original Specification

Provenance date: 2026-09-25

## Raw intent

Build the remaining plugin-creation workflow so new expertise can be packaged as Agent Plugins and adapted for VS Code GitHub Copilot and Codex. Use the approved architecture and the four plugin/MCP design documents discussed in the conversation. MCP servers provide deterministic integrations; skills remain packaged workflows and MUST NOT be converted into one-tool-per-skill APIs.

## Normalized requirements

- Treat an Expertise Pack as the canonical source for reusable plugin expertise; project-specific behavior stays in the consuming workspace.
- Provide a low-friction, validated authoring workflow using the existing `expertise scaffold`, `expertise validate`, `expertise test`, and `expertise build` commands.
- Support horizontal and vertical packs, capability projection, optional agent contributions, skills, optional MCP servers, explicit trust, and portable, Copilot, and Codex targets.
- Use native skill composition with bounded inputs, explicit returned data, result validation, and a precise parent resume point.
- Describe host-specific output honestly: Codex agent TOML files are sidecars that require separate placement; do not imply that the plugin automatically installs them as active Codex agents.
- Keep MCP tools least-privilege and assign them only to agents whose work needs them where the host enforces per-agent projection; for Codex's current plugin-wide MCP scope, disclose and allow all plugin agents access as explicitly approved by the user. Keep secrets out of checked-in MCP configuration.
- Pin the Context7 and Semgrep MCP package versions; use the host-provided read-only GitHub integration rather than introducing credentials or a second GitHub server.
- Do not begin the deferred P1-P4 work.

## Constraints and resolved decisions

- Reuse the current pack schema, IR, parser, validator, resolver, and target compilers; do not create a competing manifest or installer.
- Skills are workflows, not deterministic tools. MCP servers expose deterministic operations.
- A pack without agents or MCP servers remains valid; only add those contributions when required by its capability.
- The user authorized end-to-end implementation and requested an efficient, iterative approach.

## Discovered compatibility gap

Codex's official subagent documentation says custom-agent files can include `mcp_servers`, and its MCP reference documents `enabled_tools`; however, the current open-source role application only projects bounded overrides and its regression test asserts that a role cannot change the parent's `mcp_servers`. The current adapter emits only `name`, `description`, and `developer_instructions`, so this implementation cannot safely claim a per-agent MCP allowlist. Per the user's decision, Codex builds keep MCP configuration at plugin scope and expose all packaged MCP tools to all agents; this wider access MUST be disclosed and must be suitable for the full agent audience.

## Acceptance

- The authoring skill and templates explain the canonical pack structure, composition contract, MCP projection, and Copilot/Codex target limits.
- A fresh pack can be scaffolded and all declared targets can be validated, smoke-compiled, and built from one source.
- The core plugin declares pinned, no-secret Context7 and Semgrep servers; Copilot agent tool allowlists and corresponding research/security workflows use only relevant MCP operations, while Codex's global MCP scope is disclosed.
- Focused framework, pluginctl, linter, and skill package checks pass; generated outputs are validated without committing or staging changes.
