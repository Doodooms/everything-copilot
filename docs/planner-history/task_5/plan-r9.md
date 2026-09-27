# Implementation plan — task_5, revision 9

> Superseded by plan r10 for the subskill content structure. Preserve r9 as history for the restored 11-domain / nested-workflow topology and its remaining delivery gates.

- Specification: `SPEC-AGENTIC-CORE-NORMALIZATION@2`, revision 2.
- Architecture: `docs/harness-history/task_5/architecture-skill-topology-r5.md`.
- Correction record: `docs/harness-history/task_5/topology-correction-2026-09-27.md`.
- Current workflow inventory: `docs/planner-history/task_5/workflow-subskill-inventory.md` (59 procedures: the prior 57-entry map, `chatgpt-work-handoff`, and same-harness session coordination).
- Risk: `L2`; owner: root Orchestrator.
- Status: approved for implementation. `TASK-5-03A` remains active and requires a new, correctly scoped attempt.
- Supersedes plan r8. It preserves the user's original requirements and corrects the mistaken peer-package interpretation.

## Target structure

- 11 domain expertise skill packages remain under `agentic-core/skills/<domain>/`.
- 59 complete subdomain procedures remain under their owning `workflows/` directories.
- Each nested subskill follows the workflow-template metadata and stepwise procedure structure, and remains selectable through its domain skill.
- No separate top-level `SKILL.md` is created for a workflow subskill.
- The new same-harness communication procedure is added as another `multi-harness/workflows/` subskill.

## Task DAG

| Task | Owner | Dependencies | State | Scope and exit check |
|---|---|---|---|---|
| `TASK-5-01` Codex agent projection/install | Orchestrator + Operations | — | Complete | Nine custom roles installed under the supported Codex agent directory; QA role resolution recorded. |
| `TASK-5-02` Domain/subskill topology | Orchestrator from user direction | — | Corrected in r5 | Only 11 domain packages are discoverable; selected complete subskills remain in domain `workflows/`. |
| `TASK-5-03H` Correct the mistaken peer-package regression | Orchestrator | User clarification | Complete | Quarantined only the 57 generated peer copies; corrected the spec, architecture, plan, inventory, workspace instruction restoration, and stale method-source route. The source test passes. |
| `TASK-5-03A` Audit and repair 58 nested workflow subskills | Implementer; one bounded attempt | `TASK-5-02` | In progress | Validate each current source in place against the workflow template/linter; repair actual structure, procedure, or reference defects without promoting methods to standalone skills. Preserve all unrelated worktree changes. |
| `TASK-5-03B` Verify domain routers and references | Implementer | `TASK-5-03A` | Ready | All 11 domain routers link to the correct nested workflows; agent references route through domain entrypoints; no route targets quarantined peer packages. |
| `TASK-5-05B` Complete MCP authoring and read-only GitHub launch | Implementer | `TASK-5-03A` | In progress; implementation and startup check recorded, final gate waits for 03A | Keep `create-mcp` and `create-mcp-rust` as nested sibling workflows; no copied procedure; common guidance has one source; launcher uses user's `stdio --read-only` invocation, runtime env, and read-only PEM mount. |
| `TASK-5-06` Add same-harness session subskill | Implementer | `TASK-5-03A` | In progress | Add `same-harness-session-coordination.md` under `multi-harness/workflows/`; distinguish read-only status, explicit authorization, queued/consumed/answered, and bounded handoff/resume. Do not contact sessions. |
| `TASK-5-03C` Codify nested subskill authoring, validation, and projection | Implementer | `TASK-5-03B`, `TASK-5-05B`, `TASK-5-06` | Planned | Update tests/docs/materializer only where needed to assert the 11+59 topology, workflow completeness, contained references, and two-stage routing. Do not make all workflows independent discoverable packages. |
| `TASK-5-03D` Independent QA, then Reviewer | Quality Assurance, then Reviewer | `TASK-5-03A`, `TASK-5-03B`, `TASK-5-03C`, `TASK-5-05B`, `TASK-5-06` | Planned | QA independently falsifies source workflow completeness, routes, references, host claims, MCP launcher behavior and session safety. Reviewer traces AC-1–AC-6 to evidence. |
| `TASK-5-04` Verified plugin scratch cleanup | Orchestrator + Operations | — | Complete | Previously verified generated plugin scratch artifacts removed; keep unrelated caches untouched. |
| `TASK-5-05A` MCP shared-guidance design | Architect; Orchestrator rechecks paths | `TASK-5-02` | Complete; path check in 05B | Keep one source for shared guidance; 05B verifies both nested workflow references resolve within the parent domain package. |
| `TASK-5-05` MCP authoring subskills | Orchestrator | `TASK-5-05B` | In progress | Parent status remains active until MCP authoring and read-only launch checks converge. |
| `TASK-5-07` Refresh and verify both hosts | DevOps | `TASK-5-03D`, `TASK-5-04`, `TASK-5-05`, `TASK-5-06` | Planned | Refresh caches and verify 11 domain entrypoints, selected nested workflow resolution, nine Codex agents, and read-only GitHub MCP initialization in a fresh process. |
| `TASK-5-08` Todo audit and convergence | Orchestrator | `TASK-5-07` | Planned | Correct done/in-progress/backlog records and resume `cost-eval-opt` only after task_5's owned work converges. |

The previous `TASK-5-03E` typed peer-skill relationship decision and `TASK-5-03F`/`03G` handoffs are historical; their peer-package assumptions do not gate r9. Preserve their event history and mark the affected artifacts superseded. Review any useful method-composition behavior directly in the original nested sources during 03A.

## Validation and acceptance gates

- Inventory exactly 11 top-level domain `SKILL.md` entrypoints and 59 current nested subskills, including TASK-5-06; do not add a top-level entrypoint for a workflow.
- Run the existing domain and workflow validators against nested source files. Verify each workflow has required metadata, a full procedure, and resolvable references within its owning domain package. Do not apply the standalone skill validator to workflow files.
- Check all domain router links and method references resolve; source routes do not refer to the quarantined peer directories.
- Review content changes against source procedures; do not reuse the previous QA's peer-copy similarity scores or peer-relative link findings as source-workflow verdicts.
- Recheck MCP guidance and launcher behavior against current source and the user's supplied command. Never open or print the PEM.
- Run focused source/materializer tests and independent QA after implementation, then Reviewer. Host runtime claims require a fresh host check; source validation alone is not host proof.
- The installed custom QA and Architect roles are present in `~/.codex/agents`, but the current headless `codex exec` subprocess exposed no custom-role dispatch tool. The role probe produced an empty agent wait and no handoff. Do not substitute a base agent or claim independent review; retry those gates through a Codex host surface that actually exposes the installed roles.
- Keep `task_3`, `docs/harness-history/task_3/`, `docs/tasks-history/task_3.jsonl`, and `harness_factory/` untouched. No commit, reset, clean, or cross-session message.

## Acceptance mapping

- **AC-1 / REQ-1:** 03A, 03B, 03C, 03D, 07.
- **AC-2 / REQ-2:** 05B, 03C, 03D, 07.
- **AC-3 / REQ-3:** 04, 03D, 07.
- **AC-4 / REQ-4:** 06, 03D.
- **AC-5 / REQ-5:** 01, 07.
- **AC-6 / REQ-6:** 08.

## Next action

Continue `TASK-5-03A` against the 59 nested workflow files and r5, with exact scope limited to workflow subskills and their owning domain references. Run QA after that bounded implementation and dependent routing/MCP/session work; do not claim completion from the earlier peer-copy audit.
