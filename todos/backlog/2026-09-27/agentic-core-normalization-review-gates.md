# Agentic Core normalization: pending independent gates

**Status:** partial; implementation and automated validation are recorded, but the task is not fully accepted.
**Owner:** Orchestrator on a Codex host that can invoke the installed custom roles
**Source task:** `task_5`, plan r10

## Remaining work

- Reconcile `docs/harness-history/task_5/manifest.json` with `validate_sdd_state.py`'s embedded lifecycle model. The canonical `manifest-record` validator passes, while the SDD validator reports stale spec-revision-1 evidence, missing embedded architecture/plan objects, stale ADR references, and the legacy `validation` gate name. Preserve historical evidence in the append-only ledgers; only update current state from evidence that still applies.
- Run the installed Quality Assurance role against the r10 acceptance criteria, workflow topology and routes, MCP authoring guidance and launcher evidence, session coordination safety, Codex host claims, and source-provenance disposition.
- Run the installed Reviewer role after QA and reconcile its findings against AC-1 through AC-6.
- Update the `task_5` manifest and this backlog only from actual handoffs. Keep QA and Reviewer marked blocked/not executed until then.

## Evidence and current limit

The task ledgers report 25 targeted source tests, Ruff checks, manifest validation, 54 task-history transitions, and `git diff --check` as passing. This checkpoint reruns the locally available targeted source tests, Ruff, and current manifest/history validation. Independent QA and Reviewer handoffs were not executed: this conversation's host exposes no custom-role dispatch mechanism, and `codex exec --help` has no `--agent` selector.

The plugin is installed at 0.3.3; source/cache inventory is 11 domain skills plus 59 nested workflows, no peer packages, and nine Codex agent files. A fresh Codex process loaded orchestration. The workspace MCP is user-reported as running via `.vscode/mcp.json`.

## Resume condition

Resume when the host can select the installed `quality-assurance` and `reviewer` agents. Do not substitute a generic agent or record either gate as passed.
