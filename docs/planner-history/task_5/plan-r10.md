# Implementation plan — task_5, revision 10

> Supersedes plan r9 only for the clarified subskill content contract; preserve the active work and gates below.

- Specification: `SPEC-AGENTIC-CORE-NORMALIZATION@2`, revision 2.
- Architecture: `docs/harness-history/task_5/architecture-skill-topology-r6.md`.
- Correction record: `docs/harness-history/task_5/topology-correction-2026-09-27.md`.
- Current workflow inventory: `docs/planner-history/task_5/workflow-subskill-inventory.md` (59 procedures: the prior 57-entry map, `chatgpt-work-handoff`, and same-harness session coordination).
- Source disposition audit: `docs/harness-history/task_5/method-source-disposition-r1.md` (33 legacy files mapped; semantic comparison and final disposition remain open).
- Risk: `L2`; owner: root Orchestrator.
- Status: approved for implementation. `TASK-5-03A` remains active and requires a new, correctly scoped attempt.
- Supersedes plan r9 for the newly clarified subskill body shape, while retaining its corrected nested topology.

## Target structure

- 11 domain expertise skill packages remain under `agentic-core/skills/<domain>/`.
- 59 complete subdomain procedures remain under their owning `workflows/` directories.
- Each nested subskill uses workflow metadata and the same canonical body structure as a skill: `<critical_rules>`, `<general_rules>`, `<risk_assessment>`, `<rules>`, and `<workflow>`.
- The subskill's `<workflow>` contains its complete procedure; local rules do not duplicate parent admission/global routing. It remains nested and is selectable only through its domain skill.
- No separate top-level `SKILL.md` is created for a workflow subskill.
- The new same-harness communication procedure is added as another `multi-harness/workflows/` subskill.

## Current authority and historical peer-package artifacts

Implementation authority is the user's latest clarification, specification revision 2, architecture r6, this plan r10, and the live `workflow-subskill-inventory.md`. Earlier plans and handoffs that ask for 57 peer packages are historical records of the mistaken interpretation. In particular, do not execute destinations from `workflow-skill-source-map.md`, `planner-return-raw.md`, `handoffs/TASK-5-03-planner.md`, `handoffs/TASK-5-03A-implementer.md`, or `handoffs/TASK-5-03E-architect.md`; use the nested source files and current inventory. The old peer-package QA summary is not evidence against the nested workflows.

## Task DAG

| Task | Owner | Dependencies | State | Scope and exit check |
|---|---|---|---|---|
| `TASK-5-01` Codex agent projection/install | Orchestrator + Operations | — | Complete | Nine custom roles installed under the supported Codex agent directory; QA role resolution recorded. |
| `TASK-5-02` Domain/subskill topology | Orchestrator from user direction | — | Corrected in r6 | Only 11 domain packages are discoverable; selected complete subskills remain in domain `workflows/`. |
| `TASK-5-03H` Correct the mistaken peer-package regression | Orchestrator | User clarification | Complete | Quarantined only the 57 generated peer copies; corrected the spec, architecture, plan, inventory, workspace instruction restoration, and stale method-source route. The source test passes. |
| `TASK-5-03A` Earlier peer-package migration attempt | Prior Implementer attempt | `TASK-5-02` | Cancelled by the topology correction | This task ID is terminal in the task ledger because the mistaken peer-package attempt was cancelled. Do not reopen it. |
| `TASK-5-03A-R10` Audit and repair 59 nested workflow subskills | Orchestrator | `TASK-5-02` | Complete | All domain validators and source tests pass; all 33 legacy source mappings have body-level semantic review and documented disposition; no subskill is promoted to a standalone package. Provenance files remain pending independent QA. |
| `TASK-5-03B` Verify domain routers and references | Orchestrator | `TASK-5-03A-R10` | Complete | Tests verify every domain router links to all and only its immediate workflows, the inventory is exact, agent references resolve through domain entrypoints, and there are no peer workflow packages. |
| `TASK-5-05B` Complete MCP authoring and read-only GitHub launch | Orchestrator | `TASK-5-03A-R10` | Complete; QA pending | `create-mcp` and `create-mcp-rust` remain nested siblings with one shared reference; the user's `stdio --read-only` launcher completed the recorded initialize/tools-list handshake using a read-only PEM mount. |
| `TASK-5-06` Add same-harness session subskill | Orchestrator | `TASK-5-03A-R10` | Complete; QA pending | The nested workflow documents read-only status, separate authorization before contact, queue/receipt/answer states, and bounded handoff/resume; no session was contacted. |
| `TASK-5-03C` Codify nested subskill authoring, validation, and projection | Orchestrator | `TASK-5-03B`, `TASK-5-05B`, `TASK-5-06` | Complete | Templates, workflow-specific validation, and regression tests assert the 11+59 topology, canonical subskill body structure, reference containment, and domain-to-selected-subskill routing. |
| `TASK-5-03D` Independent QA, then Reviewer | Quality Assurance, then Reviewer | `TASK-5-03A-R10`, `TASK-5-03B`, `TASK-5-03C`, `TASK-5-05B`, `TASK-5-06` | Blocked: this conversation exposes no custom-role dispatch | The installed QA role previously loaded successfully in a fresh Codex subagent process, and the user confirms VS Code agent selection works. This conversation's tool surface has no plugin-role dispatcher; local `codex exec --help` has no direct `--agent` selector. QA must independently falsify workflow completeness, routes, references, host claims, MCP launcher behavior, and session safety; Reviewer then traces AC-1–AC-6. Do not substitute a base agent or claim these reviews ran. |
| `TASK-5-04` Verified plugin scratch cleanup | Orchestrator + Operations | — | Complete | Previously verified generated plugin scratch artifacts removed; keep unrelated caches untouched. |
| `TASK-5-05A` MCP shared-guidance design | Architect; Orchestrator rechecks paths | `TASK-5-02` | Complete; path check in 05B | Keep one source for shared guidance; 05B verifies both nested workflow references resolve within the parent domain package. |
| `TASK-5-05` MCP authoring subskills | Orchestrator | `TASK-5-05B` | In progress; QA pending | Implementation and read-only startup checks are complete; retain the parent task until independent QA/review converge. |
| `TASK-5-07` Refresh and verify both hosts | Operations / Orchestrator | `TASK-5-03D`, `TASK-5-04`, `TASK-5-05`, `TASK-5-06` | Partial | At the user's prior explicit request, reinstalled the local Codex plugin and restored the canonical nine-agent projection; source and cache each have 11 domain skills, 59 workflows, and no peer packages. A fresh Codex process loaded the orchestration skill. The workspace GitHub MCP is configured in `.vscode/mcp.json` and the user confirms it runs normally; the `/tmp` smoke did not test that workspace configuration. Independent QA/Reviewer dispatch remains unavailable in this host context. |
| `TASK-5-08` Todo audit and convergence | Orchestrator | `TASK-5-07` | Planned | Correct done/in-progress/backlog records and resume `cost-eval-opt` only after task_5's owned work converges. |

The previous `TASK-5-03E` typed peer-skill relationship decision and `TASK-5-03F`/`03G` handoffs are historical; their peer-package assumptions do not gate r10. Preserve their event history and mark the affected artifacts superseded. Review any useful method-composition behavior directly in the original nested sources during 03A.

## Validation and acceptance gates

- Inventory exactly 11 top-level domain `SKILL.md` entrypoints and 59 current nested subskills, including TASK-5-06; do not add a top-level entrypoint for a workflow.
- Verify every nested subskill has workflow metadata and the canonical skill body sections in order, with its complete procedure inside `<workflow>`, and resolvable references within its owning domain package. Extend the workflow-specific validator; do not apply standalone package identity or global skill routing to nested subskills.
- Check all domain router links and method references resolve; source routes do not refer to the quarantined peer directories.
- Review content changes against source procedures; do not reuse the previous QA's peer-copy similarity scores or peer-relative link findings as source-workflow verdicts.
- Recheck MCP guidance and launcher behavior against current source and the user's supplied command. Never open or print the PEM.
- Run focused source/materializer tests and independent QA after implementation, then Reviewer. Host runtime claims require a fresh host check; source validation alone is not host proof.
- The installed custom QA and Architect roles are present in `~/.codex/agents`; prior evidence records the QA role loading successfully in a fresh Codex subagent process, and the user confirms VS Code agent selection works. This active conversation exposes no plugin-role dispatcher, and local `codex exec --help` has no direct `--agent` selector. Do not substitute a base agent or claim independent review; retry those gates through a Codex host surface that actually exposes the installed roles.
- Keep `task_3`, `docs/harness-history/task_3/`, `docs/tasks-history/task_3.jsonl`, and `harness_factory/` untouched. No commit, reset, clean, or cross-session message.

## Acceptance mapping

- **AC-1 / REQ-1:** 03A, 03B, 03C, 03D, 07.
- **AC-2 / REQ-2:** 05B, 03C, 03D, 07.
- **AC-3 / REQ-3:** 04, 03D, 07.
- **AC-4 / REQ-4:** 06, 03D.
- **AC-5 / REQ-5:** 01, 07.
- **AC-6 / REQ-6:** 08.

## Next action

The nested topology, domain routes, 59 subskill structures, MCP startup, same-harness session workflow, and all 33 legacy source comparisons are implemented and locally validated. The local Codex plugin cache and nine-agent projection have been refreshed and verified; a fresh process loads the installed orchestration skill. The user confirms the workspace MCP configured in `.vscode/mcp.json` runs normally. Next, obtain actual plugin QA and Reviewer handoffs through a host that exposes custom-role dispatch and converge the todo index; only then resume the separate task_3 cost-eval-opt ledger. Do not claim convergence without those gates.
