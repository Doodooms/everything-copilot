# Implementation plan — task_5, revision 1

> **SUPERSEDED by plan r10 and architecture r6.** Historical record only; the current structure is 11 domain `SKILL.md` entrypoints with complete subskills under their owning `workflows/` directories. Do not implement peer skill packages from any earlier plan.

- Specification: `SPEC-AGENTIC-CORE-NORMALIZATION@1`.
- Base revision: `5c6dcd401e9a0d115e79c19f02de96ffed694686`.
- Assigned risk: `L2`.
- Owner: root Orchestrator.
- Status: in progress.

## Phases

| Phase | Output | Exit condition |
|---|---|---|
| 1. Codex agent projection | Reuse `expertise/targets/codex.py` to generate Codex-supported role files and install them under the active `CODEX_HOME/agents`; document unsupported Copilot-only controls. | All nine files parse as TOML, match canonical source names/instructions, install idempotently, and are visible after a fresh process reload or have a recorded host blocker. |
| 2. Skill topology | Convert routed workflows into complete skill packages; update parent routing and recursive Codex/Copilot discovery/materialization while preserving domain taxonomy. | Every route resolves to one complete skill package in both intended harness projections and focused structural checks pass. |
| 3. MCP authoring | Rework `create-mcp` and `create-mcp-rust` as complementary skills with one shared contract. | Both pass package validation; common guidance has a single owner and Rust advice remains version-grounded. |
| 4. Source cleanup and session coordination | Remove only proven generated scratch files; add same-harness session status/contact/handoff rules from the attached research note. | No orphan temporary plugin files remain; the skill distinguishes status, queue acceptance, consumption, and reply; no message is sent without authorization. |
| 5. Todo audit and convergence | Reconcile `todos/README.md`, done reports, backlog sources, task_3 boundary, and this task's evidence. | Every file marked done has a report/evidence link; blocked, partial, and unassigned work remains outside `done/`; exact next owner is recorded. |

## Dependencies and gates

- Phase 1 unblocks a new Codex process from loading the QA custom role; current-session role availability is not assumed.
- Phase 2 changes plugin packaging, validation, and harness discovery; require implementation validation and independent QA if a Codex QA agent becomes loadable.
- The workflow/content changes are owned by the Orchestrator implementation slice because no host-supported specialist role is currently selectable in this session. Use the plugin's `plugin-engineering` workflow directly and record this delegation limitation.
- Do not modify or message the task_3 session. The attached `codex-session-communication.md` is evidence for designing the method, not authorization to contact that session.

## Selected and skipped work

- Selected: package/source research, Codex agent installation, plugin authoring, focused validation, QA after reload if supported, todo crosswalk.
- Skipped: full cost evaluation, Copilot model calls, contacting/resuming the task_3 session, unrelated workspace cache cleanup, Git lifecycle actions.
