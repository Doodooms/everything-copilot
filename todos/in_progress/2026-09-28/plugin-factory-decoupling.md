# SPEC-6 — Plugin Factory/Core decoupling

Revision: 1
Status: partial
Risk: L2 — cross-component authoring, validation, composition, and runtime packaging changes.

## Progress

- TASK-6-01: completed; neutral source and Copilot/Codex/Antigravity projections validated.
- TASK-6-02: final QA found `harness_factory.validation.validate_source()` did not pass an explicit agent catalog to `parse_pack()`; the fixture's `researcher` extension was rejected. The bounded direct-API correction threads the caller-supplied catalog through validation and materialization, with no Core discovery or hardcoded default; 29 Harness Factory tests, 39 Pack tests, Ruff, format, and diff checks pass. This terminal task history is preserved.
- TASK-6-04: completed; deterministic AGENTS.md projection through the unique `</risk_assessment>` marker; checked-in output unchanged.
- TASK-6-03: implemented with the existing 0.3.4 runtime-copy fix preserved in normal merge ancestry; Linux installed arbitrary-CWD test and runtime-copy sync pass. Windows was not executed. Core-only and generic Core+Pack work; a distinct Core+SWE pack is absent, and pluginctl remains Core-rooted while standalone expertise works without Core.
- TASK-6-05 initial independent QA attempt found a reproducible Harness Factory defect; after the direct-API correction, the independent retest passed its tested AC-6-2/AC-6-7 paths (`test_harness_factory.py` 29 passed, `test_expertise_framework.py` 39 passed). Reviewer `REVIEW-6-01` then found that CLI and adapter callsites still omitted the explicit catalog and rejected final acceptance. `TASK-6-07` now propagates repeated `--known-agent` values through `validate`, `suite-run`, `prepare`, `smoke`, and `HarnessAdapter.prepare`/`materialize`; its Implementer reports 32 Harness Factory tests and 39 Pack tests passing with Ruff and diff checks. Independent QA `TASK-6-08` passes AC-6-2 and AC-6-7 with those same suite counts and confirms fail-closed omission behavior. Final review `REVIEW-6-02` approves and resolves the remaining catalog-path finding. Previously documented partial composition/platform limits remain unchanged.
- SDD coverage validation still reports stale historical implementation revisions and completed historical tasks without current-revision evidence. These were present before TASK-6-07; the recorded evidence and task history were not retagged or rewritten. The current convergence state remains `gaps_found` for this documented tracking limitation.

## Objective

Remove the two current architectural couplings that prevent a clean future split between Plugin Factory and Agentic Core: Copilot-owned canonical agent sources, and Factory assumptions that Agentic Core is always present. Do not rename the workspace/repository or perform the physical Core/SWE split in this task.

## Requirements

- **REQ-6-1 — Neutral agent source.** The nine Agentic Core agents have one harness-neutral canonical source. Copilot, Codex, and Antigravity artifacts are reproducible target projections. Preserve meaningful existing agent behavior and make unsupported or lossy target fields explicit.
- **REQ-6-2 — Factory inputs.** Generic pack parsing, validation, registry, composition, and compilation do not discover Agentic Core through repository paths or built-in Core agent lists. Required catalogs, validators, targets, and projection settings are explicit inputs or are represented by an existing minimal equivalent.
- **REQ-6-3 — Validation boundary.** Semantic validation is target-neutral. Copilot, Codex, and Antigravity validation belongs to their respective projection adapters. Shared validation rules have one implementation.
- **REQ-6-4 — Composition.** The runtime can represent Core-only, Core+SWE, and Factory/plugin-engineering-only profiles without silently requiring Core. Actual support is demonstrated or reported as partial/blocked with the concrete missing dependency.
- **REQ-6-5 — pluginctl runtime.** Preserve the generated runtime copy of expertise from one canonical source. Installed pluginctl works from an arbitrary CWD without a repository checkout or PYTHONPATH; validate Linux and Windows behavior with available platform evidence.
- **REQ-6-6 — Copilot repository instructions.** Generate .github/copilot-instructions.md deterministically from the shared agent-policy portion of AGENTS.md, preserving the intentional exclusion of later Git and orchestration guidance.
- **REQ-6-7 — Compatibility.** Preserve Expertise Pack schema v1 and its observable behavior. Do not introduce a public agent ABI, mandatory Core-to-Factory dependency, or incompatible pack change.

## Acceptance criteria

- **AC-6-1** (REQ-6-1): All nine agents project deterministically from one neutral canonical source to Copilot, Codex, and Antigravity. Contract tests compare observable role content and supported metadata across projections.
- **AC-6-2** (REQ-6-2): A Factory test resolves and compiles a supplied pack/catalog without locating an agentic-core directory or importing Core source paths.
- **AC-6-3** (REQ-6-3): Shared semantic validation is callable independently of any target; target adapters report target-specific validation separately, with no Codex-to-Copilot validator dependency.
- **AC-6-4** (REQ-6-4): Tests or explicit evidence classify Core-only, Core+SWE, and Factory/plugin-engineering-only composition accurately. No profile silently gains Core as a default.
- **AC-6-5** (REQ-6-5): The generated pluginctl package runs from an installed layout under arbitrary CWD with PYTHONPATH unset and no source checkout; Linux is executed, and Windows is validated on Windows or clearly marked not executed.
- **AC-6-6** (REQ-6-6): The generator extracts the shared agent-policy portion of AGENTS.md through the closing risk_assessment section; repeated generation is byte-identical to the checked-in .github/copilot-instructions.md.
- **AC-6-7** (REQ-6-7): Existing Pack v1 fixtures and lifecycle tests continue to pass without schema or behavior version changes.

## Constraints and non-goals

- Do not modify control-plane/ or the Remote MCP Gateway worktree.
- Do not rename the workspace or repository.
- Do not move SWE skills or agents (software-engineering, quality-engineering, security, architecture, implementer, quality-assurance, reviewer).
- Do not change the public Expertise Pack v1 contract or add an independently editable duplicate agent source.
- Do not distribute expertise as a separate Python dependency; preserve the generated runtime-copy packaging decision.
- Do not merge or use a GitHub identity other than the configured Agentic Core GitHub App MCP.

## Approved architectural direction

- A private, repository-internal neutral authoring representation for the nine Core agents is acceptable; it is not a new public pack ABI.
- Preserve the public Pack v1 source contract and existing external .agent.md inputs.
- Factory receives explicit catalogs/validators/targets or a minimal existing equivalent; Factory does not special-case Core.
- Runtime projections remain target-specific; harness execution stays outside this task.

## Source

User request attached on 2026-09-28: 01535c67-8dd6-41eb-86bd-d3979ed07b3e.

## Final checkpoint — 2026-09-28

- Final state: PARTIAL. Implementation, independent QA, and Reviewer work are complete; no implementation task is currently assigned. The isolated worktree is retained for remote publication.
- TASK-6-07 code commit: 29dcba926bf971718749e54e8c9efed63813a654 (fix(factory): propagate explicit agent catalogs to harness inputs).
- QA QA-RUN-6-08-A1: PASS for AC-6-2 and AC-6-7; Harness Factory 32 tests and Pack v1 39 tests passed.
- Reviewer REVIEW-6-02: APPROVE; the explicit-catalog finding from REVIEW-6-01 is resolved.
- Final scoped Ruff check/format and git diff --check: PASS.
- SDD coverage remains gaps_found: historical revision mismatches and prior/gate tasks without current-revision implementation evidence remain documented; historical evidence was not retagged.
- Other open gates: no Windows runtime evidence; no distinct SWE pack; pluginctl remains Core-rooted for Factory-only composition.
- Publication is blocked because the current session lacks the approved Agentic Core GitHub MCP. No hosted connector, gh, or user credential path was used. Next action is publish this preserved branch and create the PR with the configured GitHub App MCP.
- The shared checkout was not modified.
