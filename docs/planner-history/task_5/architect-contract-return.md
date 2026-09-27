# Architect return — TASK-5-03F

> **SUPERSEDED.** This handoff adopts the same incorrect peer-package interpretation as architecture r4. The user's latest clarification and the current workflow template/linter define the correct nested subskill contract; see `docs/harness-history/task_5/topology-correction-2026-09-27.md`.

- Attempt: `peer-skill-contract-architect-1`
- Role: installed plugin `architect`
- Return status: `partial`; no source changes and no commits.
- Reason for partial: the Codex subprocess exposed no native skill-loading tool. The Architect read the installed architecture skill source and the assigned evidence, then returned proposals. The Orchestrator reviewed and adopted the applicable decisions in `docs/harness-history/task_5/architecture-skill-topology-r4.md`.

## Adopted decisions

1. **Peer-skill shape:** every domain and method is a complete immediate-child skill package with `SKILL.md`. Methods keep the same canonical Agentic Core sections as domain skills, but put their complete procedure directly in `<workflow>`. Routing remains domain router → selected method skill. `user-invocable` is deliberate invocation metadata, not route metadata. Do not restore nested `workflows/<method>.md` packages.
2. **Shared references:** retain one canonical source in its owning domain and permit only the 32 explicitly enumerated consumer/source pairs for 16 files, in addition to the existing exact MCP pair. Targets resolve under `agentic-core/skills/`; arbitrary paths, symlinks, globs, and undeclared pairs remain rejected. The new list includes `end-to-end → test-levels.md`.
3. **Compact cycle:** retain `smart-compact → token-optimization` as bounded execution composition; change `token-optimization → smart-compact` to context-only `read`; route live context observation/compaction directly to `smart-compact`.
4. **Cross-host body language:** do not rely on `#tool:` or `#file:` markers as a shared execution or file-loading contract. Rewrite them into ordinary active-harness instructions and normal Markdown references without losing procedure behavior; if a required host capability is unavailable, report the missing capability/input and stop as appropriate.

## Evidence and unresolved checks

- The full Architect handoff is `docs/harness-history/task_5/handoffs/TASK-5-03F-architect.md`; the QA evidence is `docs/harness-history/task_5/qa-03a-preflight-summary.md`.
- The current skill template, skill-authoring procedure, materializer, and both host package formats were reviewed. The `expertise/targets/codex.py` adapter exports agent contributions and does not rewrite skill bodies.
- The proposed allowlist and body-language changes still require implementation and the 03C linter/materializer checks. Host tool behavior remains unverified.
- The 18 low-similarity workflow conversions remain subject to source comparison during implementation.
