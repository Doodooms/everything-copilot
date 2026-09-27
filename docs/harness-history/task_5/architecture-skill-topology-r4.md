# Agentic Core skill topology

> **SUPERSEDED by architecture r6.** This document records the mistaken interpretation that the 57 workflow subskills should become 57 additional top-level skill packages. The current contract is in `architecture-skill-topology-r6.md`; see `topology-correction-2026-09-27.md`. Do not use r4's peer-package topology or its package-specific decisions as implementation instructions.

- Revision: 4 (clarifies complete peer-skill structure; adds `ADR-ACN-005` and `ADR-ACN-006`; revisions 1–3 are preserved in prior artifacts).
- Specification: `SPEC-AGENTIC-CORE-NORMALIZATION@1`.
- Requirements: `REQ-1`.
- Acceptance criteria: `AC-1`.
- Risk: `L2` (assigned by the Orchestrator).
- Architecture owner: Architect role `skill_topology`.
- Handoff status: Architect returned partial, read-only; no files changed by the Architect. The missing native skill loader was reported; the Architect read the installed source instructions and supplied evidence-backed proposals.
- Decision status: adopted by the Orchestrator after reviewing the Architect proposal, current source contract, user clarification, and official host package documentation. Host runtime behavior remains unverified.

## Decisions

### ADR-ACN-001 — Domain and method packages are peer skills

Keep one canonical source tree in `agentic-core/skills/`. Every domain router and every routed method must be a complete skill package with its own `SKILL.md` and any support files that the skill consumes. The domain skill routes to a method by its stable skill ID through the host's skill-loading mechanism. A method skill contains its complete procedure; deliberate peer-skill composition is governed by ADR-ACN-004 and does not add a taxonomy/package layer.

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

### ADR-ACN-003 — Share MCP authoring support from one domain-owned reference

Keep common transport and security guidance at `agentic-core/skills/plugin-engineering/references/create-mcp/common-transport-security.md`. The complete peer method packages `create-mcp` and `create-mcp-rust` may reference only this exact sibling-package support file using `../plugin-engineering/references/create-mcp/common-transport-security.md`.

This is point-of-need shared support, not another method skill or a route from one method to another. The package linter must allow this exact source/target pair only, resolve the target beneath the plugin `skills/` root, reject symlinks and other package escapes, and verify the target appears in the materialized native profile. Keep Rust/`rmcp` details in the Rust package. Do not expand the native materializer to arbitrary plugin-root files.

The Architect found the native plugin materializer gathers files under each peer skill package but not arbitrary plugin-root references, while the portable Expertise Pack target copies declared package files only. This ADR applies to native `agentic-core` skill packages; independently projecting these methods into a portable pack would require a separate support projection decision.

**Host assumption to validate:** Codex and Copilot must follow the explicit sibling-package Markdown reference after installation. Repository behavior alone does not prove that both hosts will load the referenced file. QA and final dual-host validation must check the materialized source and host behavior. The architecture decision does not authorize weakening arbitrary path containment.

### ADR-ACN-004 — Preserve typed procedural composition between peer skills

The two-stage **taxonomy** is domain → selected entry skill. A complete entry skill may conditionally compose another complete peer skill when its procedure requires it; this is execution composition, not a nested package/domain layer. Preserve bounded sequential composition such as `deep-research` selecting source-specific research methods, and conditional specialization such as `create-mcp` → `create-mcp-rust`.

Declare skill relationships in a human-readable, machine-parseable `## Skill relationships` table in the relevant `SKILL.md` body, not in custom frontmatter. Use only these edge types:

- `route`: domain router selects an entry method skill.
- `compose`: source method conditionally executes another complete peer skill as part of its procedure.
- `read`: source method reads a paired/prerequisite skill for context without executing its procedure; reciprocal cross-harness reads belong here.
- `support`: a local or ADR-ACN-003 shared support-file reference, validated by the file-path policy rather than the execution graph.

Every edge names one stable target skill ID; `compose` declares the condition/order needed by the source procedure. Lint must verify target existence, immediate-child package location, unique IDs, and consistency with the source instructions. Detect undeclared executable composition, missing targets, and cycles in the executable `compose` subgraph. Validate `read` targets as existence/read dependencies only; do not recursively execute them. `support` links are excluded from routing and remain subject to package containment, symlink rejection, and ADR-ACN-003's exact exception.

Codex's current SKILL.md parser accepts standard `name`, `description`, and optional `metadata.short-description` fields; it ignores no custom route schema because none is declared. Keep typed relationships in the Markdown body so both Agent Plugins hosts receive them as skill instructions. GitHub Copilot documents the `SKILL.md` body as the skill definition and immediate-child package layout ([plugin structure](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/plugins-creating)). The two host runtimes must still be checked after installation.

## Limits and risks

- The architecture brief and official Agent Plugins 1.0 contracts establish package discovery layout; they do not claim a full post-migration Copilot interaction has already been tested.
- Moving procedures can break package-relative links, support-file loading, domain-to-method routes, and existing validator fixtures. Reconcile these paths while migrating; do not leave a wrapper that merely links to the old workflow file.
- No repository tests were run by the Architect. Local validation remains a required implementation/QA gate.

## Source handoff

- Architect child rollout: `01a0e202-6702-7093-9218-436cd3027d2f`.
- Copilot installed plugin inventory: `copilot plugin list --json`.
- Copilot installed skill inventory: `copilot skill list --json` (11 plugin skills before migration).
- Codex target: `codex debug prompt-input` and `codex debug models --bundled`.

## Revision 4 decisions and amendments

This revision records the Orchestrator's adopted response to QA run `QA-RUN-TASK-5-03A-20260927-01`, the Architect handoff `TASK-5-03F`, and the user's clarification. `master` is an ancestor of the active `main` branch; no branch merge conflict caused the findings. The previous validator's required nested workflow placement is stale for method peers. The current repository skill template remains the canonical body contract.

### Amendment to ADR-ACN-001 — Complete peer skill package contract

Every domain router and every routed method is a complete, direct-child skill package with a `SKILL.md`. Each method package retains the same canonical Agentic Core skill structure as domain packages: standard frontmatter (`name`, `description`, and the deliberate `user-invocable` setting with current repository metadata), then `<critical_rules>`, `<general_rules>`, `<risk_assessment>`, `<rules>`, and `<workflow>` sections. Put the complete method procedure directly in that method's `<workflow>` section. Its optional references, assets, or scripts stay inside that package unless an exact shared-support relationship is authorized by ADR-ACN-005.

Keep the taxonomy and progressive disclosure at **domain router → selected method skill**. Do not put method skills beneath `workflows/`, add method-level taxonomy folders, or treat peer-skill composition as another taxonomy level. The domain skill keeps its own complete package structure and selects a peer by stable skill ID through the active host's native skill mechanism. `user-invocable` controls explicit invocation only; it is not route metadata.

The old validator may be used to identify diagnostics, but must be redesigned to validate this direct-child peer package contract. It must not force the migration back to nested workflow files.

### ADR-ACN-005 — Exact shared-support consumer/source pairs

Retain one canonical source under its existing owning domain package for shared support knowledge. Permit only the following explicit consumer-to-source pairs in addition to the single MCP pair already allowed by ADR-ACN-003. Resolve every source beneath `agentic-core/skills/`; reject missing files, symlinks, undeclared pairs, traversal, and arbitrary plugin-root access. Materialization must include each referenced resource at the resolved path for every package that declares it. Do not use globs or duplicate these knowledge files as separate canonical sources.

| Consumer skill | Exact shared source |
|---|---|
| `agent-authoring` | `../plugin-engineering/references/create-agent/references/final-checklist.md` |
| `agent-validation` | `../plugin-engineering/references/create-agent/references/final-checklist.md` |
| `agent-authoring` | `../plugin-engineering/references/create-agent/references/validation.md` |
| `agent-validation` | `../plugin-engineering/references/create-agent/references/validation.md` |
| `agent-authoring` | `../plugin-engineering/references/create-agent/scripts/agent_lint_core.py` |
| `agent-validation` | `../plugin-engineering/references/create-agent/scripts/agent_lint_core.py` |
| `plugin-creation` | `../plugin-engineering/references/create-plugin/references/plugin-contract.md` |
| `plugin-update` | `../plugin-engineering/references/create-plugin/references/plugin-contract.md` |
| `plugin-creation` | `../plugin-engineering/references/create-plugin/references/skill-composition.md` |
| `plugin-update` | `../plugin-engineering/references/create-plugin/references/skill-composition.md` |
| `skill-authoring` | `../plugin-engineering/references/create-skill/references/final-checklist.md` |
| `skill-maintenance` | `../plugin-engineering/references/create-skill/references/final-checklist.md` |
| `skill-authoring` | `../plugin-engineering/references/create-skill/references/latest-docs.md` |
| `skill-maintenance` | `../plugin-engineering/references/create-skill/references/latest-docs.md` |
| `skill-authoring` | `../plugin-engineering/references/create-skill/references/skill-composition.md` |
| `skill-maintenance` | `../plugin-engineering/references/create-skill/references/skill-composition.md` |
| `skill-authoring` | `../plugin-engineering/references/create-skill/references/validation.md` |
| `skill-maintenance` | `../plugin-engineering/references/create-skill/references/validation.md` |
| `skill-authoring` | `../plugin-engineering/references/create-skill/scripts/validate.py` |
| `skill-maintenance` | `../plugin-engineering/references/create-skill/scripts/validate.py` |
| `test-design` | `../quality-engineering/references/testing/references/test-oracles.md` |
| `test-quality-review` | `../quality-engineering/references/testing/references/test-oracles.md` |
| `test-design` | `../quality-engineering/references/testing/references/equivalence-boundaries.md` |
| `test-quality-review` | `../quality-engineering/references/testing/references/equivalence-boundaries.md` |
| `test-design` | `../quality-engineering/references/testing/references/test-doubles.md` |
| `test-quality-review` | `../quality-engineering/references/testing/references/test-doubles.md` |
| `end-to-end` | `../quality-engineering/references/testing/references/test-levels.md` |
| `test-design` | `../quality-engineering/references/testing/references/test-levels.md` |
| `algorithm-selection` | `../software-engineering/references/implementation-design/references/data-structures.md` |
| `representation-selection` | `../software-engineering/references/implementation-design/references/data-structures.md` |
| `concurrency-design` | `../software-engineering/references/implementation-design/references/state-machines.md` |
| `state-modeling` | `../software-engineering/references/implementation-design/references/state-machines.md` |

The linter and materializer must enforce exactly this consumer/source relation set, including the ADR-ACN-003 MCP pair. This explicit allowlist authorizes selected support files only; it does not authorize sibling workflow execution or general cross-package access.

### Amendment to ADR-ACN-004 — Remove the compact-method execution cycle

Keep `smart-compact → token-optimization` as a bounded `compose` call with an explicit return point. Change `token-optimization → smart-compact` to `read` and describe context consultation only; it must not execute the `smart-compact` procedure. Route live context observation/compaction directly to the `smart-compact` method from its domain router. `compose` remains an execution relation, not an additional taxonomy level, and its graph must be acyclic.

### ADR-ACN-006 — Host-neutral skill body instructions

Do not rely on `#tool:` or `#file:` markers as a cross-host tool invocation or resource-loading contract. Write ordinary instructions that use the active harness's available, permitted native capability; if the required capability is not present, report the gap or stop for the missing input. Use normal relative Markdown links for local support and ADR-ACN-005's exact pairs for approved shared resources. Replace rather than merely delete existing markers so the actual procedure remains intact. For former ask-question directives, request input through the active host's available interface; if there is no such interface, return the unresolved input and wait. Apply this rule to the skill authoring templates, their linter, all domain skills, and all method skills, and verify host behavior only through explicit host runtime tests.

## Adoption evidence and limits

- The user clarified the two-stage taxonomy and direct skill structure in the active conversation.
- `git branch --show-current` returned `main`; `git merge-base master main` returned the `master` commit `3f53074ce678adc5bf37caf0f2a5f8631ecc7b5d`.
- The current `main` skill template and `skill-authoring` method require canonical skill sections; official OpenAI plugin docs describe the general package as a folder with `SKILL.md`, name/description/instructions, and optional resources; official Copilot plugin docs require immediate-child skill directories. These package docs do not by themselves establish runtime tool-marker behavior.
- The Architect's return was partial because no native skill-loading tool was exposed in that subprocess; it read the installed source contract and supplied the decisions above. The Orchestrator independently checked the cited files and adopts the bounded decisions.
- No runtime host behavior has been claimed or tested in this revision.
