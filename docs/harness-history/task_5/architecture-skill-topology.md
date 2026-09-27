# Agentic Core skill topology

> **SUPERSEDED by architecture r6.** Historical decision record only. Subskills are complete procedures nested under the owning domain's `workflows/` directory, use the canonical skill body structure, and are not peer skill packages.

- Specification: `SPEC-AGENTIC-CORE-NORMALIZATION@1`.
- Requirements: `REQ-1`.
- Acceptance criteria: `AC-1`.
- Risk: `L2` (assigned by the Orchestrator).
- Architecture owner: Architect role `skill_topology`.
- Handoff status: successful, read-only; no files changed by the Architect.
- Decision status: adopted by the Orchestrator because it preserves the user's explicit skill contract and matches both host package formats.

## Decisions

### ADR-ACN-001 — Domain and method packages are peer skills

Keep one canonical source tree in `agentic-core/skills/`. Every domain router and every routed method must be a complete skill package with its own `SKILL.md` and any support files that the skill consumes. The domain skill routes to a method by its stable skill ID through the host's skill-loading mechanism. A method skill contains its complete procedure and does not route onward to another method.

### ADR-ACN-002 — Keep every discoverable package at the plugin skill root

Put every skill package in an immediate child directory of `agentic-core/skills/` (`skills/<skill-id>/SKILL.md`). Domain membership is expressed by the domain router and stable method IDs; method packages are not nested under `skills/<domain>/workflows/`.

This layout is supported by both current targets. Codex Agent Plugins 1.0 discovers plugin skill roots and uses direct-child discovery for that manifest format. GitHub Copilot's Agent Plugins 1.0 requires each skill to be an immediate subdirectory of `skills/`, containing `SKILL.md` ([GitHub Copilot plugin structure](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/plugins-creating), [GitHub Copilot plugin reference](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-plugin-reference)).

## Evidence

- `agentic-core/plugin.json` opts into Agent Plugins 1.0. The native Codex plugin is installed and enabled as version `0.3.3`; the Copilot CLI is `1.0.88` and reports the same plugin enabled at `0.3.3`.
- `codex debug prompt-input` exposes the installed Agentic Core skill set to a fresh Codex process. `copilot skill list --json` reports the 11 current domain skills from the installed plugin. The direct-child package rule means the current 57 routed workflow Markdown files are not yet discovered as skills by either Agent Plugins 1.0 host.
- `tests/test_agentic_core_sources.py:255-267` explicitly requires exactly 11 discoverable skills and rejects nested method skill packages. That test enforces the old behavior and must be replaced with inventory and route-edge checks for domain plus method skills.
- `agentic-core/skills/plugin-engineering/references/create-skill/scripts/skill_lint_core.py` validates procedures under a skill's `workflows/` directory, validates references within the owning package, and rejects links outside the immediate workflow directory. `agentic-core/skills/plugin-engineering/references/create-skill/references/validation.md` and `assets/folder-template.md` describe that same old contract.
- `agentic-core/runtime/pluginctl/controller.py` materializes plugin profiles from skill directories that each have a `SKILL.md`; temporary `.workflow-routes.tmp` files are filtered from the emitted profile.
- The generic Expertise Pack pipeline (`expertise/parser.py`, `expertise/validator.py`, `expertise/targets/portable.py`) is separate from the standalone `agentic-core` source tree. Its Copilot and Codex targets reuse the portable pack compiler; they do not compile this core plugin's skill tree.
- The current source contains 57 directly routed workflows with non-empty, globally unique `id` values. These IDs can be the peer skill directory/frontmatter names without adding a second namespace.

## Migration boundary

- Convert each of the 57 routed methods to `agentic-core/skills/<skill-id>/SKILL.md`, preserving its complete procedure and moving or explicitly composing the support resources it consumes.
- Update each domain skill's router and the agent-skill references to load the stable method skill ID. Preserve the two disclosure steps: domain routing first, selected method skill second.
- Redesign the canonical skill linter and source tests to validate complete method packages, unique IDs, package-local support references, and every router edge. Remove assertions that methods must remain under `workflows/` or must not be discoverable.
- Keep `plugin.json`, root `skills/`, and `mcp.json` as the portable host boundaries. Do not add a second skills converter or maintain a `.github/skills` editable copy.
- For installed-host validation, use the native inventories (`copilot skill list` and a new Codex process) and verify all domain and method skill IDs after the plugin cache is updated. Copilot CLI's documentation also provides `/skills list` for interactive verification.

## Limits and risks

- The architecture brief and official Agent Plugins 1.0 contracts establish package discovery layout; they do not claim a full post-migration Copilot interaction has already been tested.
- Moving procedures can break package-relative links, support-file loading, domain-to-method routes, and existing validator fixtures. Reconcile these paths while migrating; do not leave a wrapper that merely links to the old workflow file.
- No repository tests were run by the Architect. Local validation remains a required implementation/QA gate.

## Source handoff

- Architect child rollout: `01a0e202-6702-7093-9218-436cd3027d2f`.
- Copilot installed plugin inventory: `copilot plugin list --json`.
- Copilot installed skill inventory: `copilot skill list --json` (11 plugin skills before migration).
- Codex target: `codex debug prompt-input` and `codex debug models --bundled`.
