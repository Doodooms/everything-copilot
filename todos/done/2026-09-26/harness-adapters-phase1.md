# Agent Plugin Factory — harness adapters, phase 1

Scope: add the smallest deterministic multi-harness integration layer around existing Expertise Pack targets. Keep adapters outside canonical plugin sources.

## Audit findings

- Existing `expertise/targets/copilot.py` and `codex.py` compile host projections; `pluginctl` manages pack trust, activation, composition, materialization, and rollback. Neither provides CLI execution, capability detection, or isolated harness runs.
- Copilot CLI `1.0.88` and Codex CLI `0.157.1` are installed. Copilot supports local plugin directories, non-interactive prompts, usage output, read-tool allowlists, and MCP controls. Codex supports project-local plugin marketplaces, `exec --json`, `--ephemeral`, `--ignore-user-config`, and a read-only sandbox; it has no direct `--plugin-dir` or observed dollar-cost cap.
- Existing Waza routing experiments are separate from these CLI adapters; do not run their benchmark matrix or SkillOpt.
- Preserve all pre-existing local modifications and user work. Do not push.

## Completion evidence

- Implemented `harness_factory/` capability detection, static target validation/materialization, Copilot/Codex adapters, the CLI, isolated per-run worktrees, strict ownership markers, exact status transitions, read-only cross-harness request validation, and normalized transcript-free result records.
- `tests/test_harness_factory.py` now has 24 passing deterministic tests. This includes regression coverage for validators resolved from the pinned plugin root and Copilot's actual usage-file schema.
- Static Copilot and Codex target validation of `agentic-core` pass: Copilot sees 9 agent definitions and 10 skills; Codex sees 10 skills and no Codex sidecars. Existing support-file warnings remain (73 Copilot, 74 Codex, including the expected Copilot-agent/Codex-sidecar mismatch).
- The first full-Core Copilot smoke exposed a validator-root bug: the factory ran the active checkout's validator against files in a detached pinned worktree, so the packaged Orchestrator's `github/*` permission was compared to the wrong canonical path. The factory now prefers validators inside the pinned plugin; a focused regression test covers this.
- A real Copilot Core-plugin smoke then passed against base `5c6dcd401e9a0d115e79c19f02de96ffed694686`, with MCP servers disabled, only `glob`, `grep`, and `view` allowed, `write`/`shell` denied, custom instructions disabled, and a 30-credit cap. Both process and exact-output assertions passed in 4,789 ms. Copilot recorded one premium request. Its usage file reports 5,284 input tokens, 22 output tokens, 2,919 cache-read tokens, 2,285 cache-write tokens, and 0 reasoning tokens.
- The smoke initially serialized token usage as `unknown` because the parser only accepted a synthetic `token_usage` shape. The parser now handles Copilot's `modelMetrics` format; a regression test and a no-model reparse of the actual smoke artifact confirmed the counts above. No second model invocation was needed.
- A real Codex 0.157.1 adapter smoke with an isolated local plugin and skill, no MCP servers, passed. It reported 19,242 input tokens, 10 output tokens, and 5,613 ms. The full `agentic-core` package was not run on Codex: it declares `context7` and `semgrep`, and the adapter correctly refuses plugins with MCP servers because this Codex version exposes no observed per-plugin MCP disable control.
- Copilot's full Core smoke and an isolated minimal Copilot plugin smoke both passed. The Core smoke is the primary evidence; the minimal smoke was run earlier while diagnosing the validator mismatch.
- No files were staged or committed, and no push was made. The created temporary harness worktrees were inspected and explicitly cleaned; unrelated dirty state was preserved.

## Exact validation commands

- `PYTHONDONTWRITEBYTECODE=1 /home/pm/projets-persos/agentic-workflow/.venv/bin/python -m unittest discover -s tests -p 'test_harness_factory.py' -v` — 24 tests passed.
- `PYTHONDONTWRITEBYTECODE=1 /home/pm/projets-persos/agentic-workflow/.venv/bin/python -m harness_factory detect` — Copilot 1.0.88 and Codex 0.157.1 detected; the observed Codex capability limits above remain.
- `PYTHONDONTWRITEBYTECODE=1 /home/pm/projets-persos/agentic-workflow/.venv/bin/python -m harness_factory validate --target copilot --source-root agentic-core` — passed, with existing support-file warnings.
- `PYTHONDONTWRITEBYTECODE=1 /home/pm/projets-persos/agentic-workflow/.venv/bin/python -m harness_factory validate --target codex --source-root agentic-core` — passed, with existing support-file and target-specific warnings.
- `PYTHONDONTWRITEBYTECODE=1 /home/pm/projets-persos/agentic-workflow/.venv/bin/python -m harness_factory smoke --harness copilot --repo-root /home/pm/projets-persos/agentic-workflow --state-root /tmp/harness-factory-copilot-core-smoke.diWuNm --base-revision HEAD --source agentic-core --owner live-smoke --max-ai-credits 30 --timeout-seconds 90` — passed, run `34daee0cff93406ea7c65878b3cb61df`; its usage file was reparsed after the parser fix without another model request.
- Codex live adapter smoke — passed with the local marketplace/skill fixture and reported 19,242 input and 10 output tokens; `agentic-core` was not used because of its declared MCP servers.

## Residual risks

- The Copilot smoke is a bounded integration check, not a context-cost benchmark; it disables custom instructions and MCP servers and restricts tools. Do not compare its 5,284 input tokens directly with an unrestricted invocation.
- Codex dollar cost remains unknown, Codex's direct development command remains unavailable without `--plugin-dir`, and full Core-on-Codex runtime compatibility remains unverified while Core declares MCP servers.
- Canonical validation still emits pre-existing support-file warnings. They were reported, not changed, because repairing skill topology is outside this phase.
