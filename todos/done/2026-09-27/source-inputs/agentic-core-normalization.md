# Agentic Core normalization and Codex installation

**Status:** implementation slice concluded; overall task remains partial pending independent QA and Reviewer. See [completion report](../agentic-core-normalization-report.md) and [review-gate backlog](../../../backlog/2026-09-27/agentic-core-normalization-review-gates.md).
**Owner:** root Orchestrator
**Risk:** L2
**Specification:** `SPEC-AGENTIC-CORE-NORMALIZATION@2` (revision 2)

## Objective

Put the `agentic-core` plugin and its workspace tracking in order before resuming the separate `cost-eval-opt` task. Keep 11 domain expertise packages as the top-level skill entrypoints and each complete subdomain procedure under its domain's `workflows/` directory. Preserve domain-to-selected-subskill progressive disclosure. Verify the complete Codex installation, including custom agents in Codex's supported agent directory.

## Requirements

- **REQ-1 — Domain skills and subskills.** Keep the 11 domain expertise packages as the only top-level/discoverable skills. Each domain contains subdomain expertise subskills under `workflows/`. Every nested subskill uses workflow metadata and the same canonical body structure as a skill (`critical_rules`, `general_rules`, `risk_assessment`, `rules`, and `workflow`), with its complete specialized procedure inside `workflow`. It remains inside its parent domain package and is not a separate Agent Skill package. Preserve progressive disclosure from the selected domain skill to one relevant subskill.
- **REQ-2 — MCP authoring skills.** `create-mcp` and `create-mcp-rust` provide complementary, validated guidance with no copied procedure; common transport and security rules are shared through explicit composition or references.
- **REQ-3 — Package hygiene.** Remove stale generated scratch artifacts from the plugin source while preserving files that are consumed or required by runtime checks.
- **REQ-4 — Session coordination.** Add a safe method for coordinating distinct sessions in one harness, including the difference between a queued message and a consumed/answered message. Sending a message remains separately authorized by the user.
- **REQ-5 — Complete Codex projection.** Keep the native Agent Plugin installation for skills and MCP, and project the nine core agent roles into valid Codex custom-agent TOML at `CODEX_HOME/agents` (or `~/.codex/agents`) through the existing Codex adapter. Preserve supported model and reasoning settings; omit Copilot-only controls with their limitations documented.
- **REQ-6 — Accurate todo state.** Link active work, completed reports, blocked inputs, and deferred backlog without marking partial or blocked requests as done. Keep `task_3` and its canonical files owned by the other session.

## Acceptance criteria

- **AC-1:** The plugin exposes exactly the 11 domain skills as top-level skill entrypoints. Their 59 subskills remain under the owning `workflows/` directories and each passes canonical body structure, complete-procedure, metadata, and reference checks. Each domain router can select a relevant subskill. No subskill has a peer `skills/<id>/SKILL.md` package or adds a third taxonomy level.
- **AC-2:** The two MCP authoring skills pass package validation, share common guidance without duplicating it, and retain the Rust-specific `rmcp` constraints.
- **AC-3:** Plugin-source scratch files are removed or have an identified runtime owner; target builds do not include temporary routing data.
- **AC-4:** Same-harness session coordination documents read-only status inspection, authorization before contact, queue/receipt distinctions, and bounded handoff/resume behavior.
- **AC-5:** Codex has the plugin enabled and all nine projected custom agents are valid `.toml` files in the documented Codex agent directory; a fresh Codex process can resolve the QA role or records the exact host limitation.
- **AC-6:** `todos/README.md` accurately maps the workstreams and existing source/report files; `cost-eval-opt` remains separate from this cleanup task and resumes only after the current task's owned changes converge.

## Constraints and non-goals

- Do not migrate workflows into peer `SKILL.md` packages; preserve the domain → selected workflow subskill disclosure path.
- Do not modify `docs/harness-history/task_3/`, `docs/tasks-history/task_3.jsonl`, or the `harness_factory/` implementation owned by the other session.
- Do not send or queue a message to another Codex session without explicit user authorization.
- The original task brief prohibited Git lifecycle actions. The later user checkpoint explicitly authorized scoped local commits and a root `.gitignore`; that later instruction governs this checkpoint. Preserve all task_3 and uncertain files.
- Use the plugin's existing codex projection code; do not add a second agent-format converter.
- Do not run a costly behavioral benchmark as part of plugin cleanup.

## Resume point

`TASK-5-01`, verified plugin scratch cleanup in `TASK-5-04`, and MCP guidance design in `TASK-5-05A` are recorded complete. Architecture r6 and plan r10 encode the user's topology: 11 discoverable domain skills own 59 complete subskills under `workflows/`; each subskill has workflow metadata and the canonical skill body sections, and is reachable only through its domain router. The 57 historical peer-package copies are quarantined under `/tmp/agentic-core-erroneous-peer-skills-20260927`, outside the plugin and Codex cache.

Source and installed-cache inventories were checked independently. Both source and refreshed Codex cache version 0.3.3 now have 11 domain `SKILL.md` entrypoints, 59 immediate workflow subskills, and no workflow peer packages. Codex CLI confirms the plugin is installed and enabled from the approved local repository. The canonical agent installer restored the stale `orchestrator.toml`; its read-only check verifies all nine agents. All 25 focused source tests and all 11 domain validators pass. The quality validator reports known provenance/support warnings (the 33 method-source files remain as provenance pending independent QA); Ruff check/format and `git diff --check` pass. A new Codex process loaded the installed orchestration domain skill and selected its first procedure.

All six one-to-many and all 27 one-to-one legacy source mappings received body-level semantic review. The four removed Operations wrappers have recorded dispositions. The GitHub MCP `stdio --read-only` initialize/tools-list handshake succeeded with a read-only PEM mount; session coordination is documented and no session was contacted. The user confirms the workspace GitHub MCP runs normally and is configured by `.vscode/mcp.json`. The separate fresh-process smoke was launched from `/tmp`, so it did not load that workspace MCP configuration; its bundled plugin MCP startup log does not describe the workspace server. Nine custom agents are installed. Earlier evidence confirms the QA role loaded in a fresh Codex subagent process, and the user confirms VS Code agent selection works; this conversation exposes no plugin-role dispatcher and local `codex exec --help` has no direct `--agent` selector. QA and Reviewer were not invoked here. Local implementation gates and the plugin cache refresh are complete; independent QA/Reviewer and todo convergence remain. Keep cost-eval-opt and task_3's canonical files untouched until task_5 converges.

## Latest correction (2026-09-27)

The user's latest clarification confirms the intended two-stage taxonomy: only the 11 domain packages are discoverable skills. Their 59 complete subdomain subskills stay in the owning `workflows/` directories, each with workflow metadata and the canonical skill body sections. The selected domain router loads only its relevant subskill; no subskill gets a peer package or global route. The historical “57” refers to the old workflow inventory and to quarantined erroneous copies, not to current discoverable skills.

Verified source and refreshed Codex cache topology: 11 domain `SKILL.md` files, 59 immediate workflow subskills, and zero workflow peer packages in both. The canonical agent installer restored `orchestrator.toml`; its read-only check now verifies all nine agent files. The source test suite passes (25 tests); all 11 domain validators pass with known provenance/support warnings; Ruff check/format and `git diff --check` pass. A fresh Codex process loaded the installed orchestration domain skill. The eval-harness subskill enforces a pre-invocation model-call ceiling and durable machine-readable trial records.

The `method-source-disposition-r1.md` audit records body-level semantic review of all 33 current sources: six one-to-many and all 27 one-to-one mappings. The provenance-bearing files remain in the plugin until QA confirms whether they can move outside the runtime package. Implementation tasks `TASK-5-03A-R10`, `TASK-5-03B/C`, `TASK-5-05B`, and `TASK-5-06` are validated. The local Codex cache and agent projection are refreshed. The user's workspace GitHub MCP is configured separately in `.vscode/mcp.json` and is reported running normally; the `/tmp` plugin smoke did not test it. Independent QA and Reviewer are not dispatchable from this host context; todo convergence remains open.
