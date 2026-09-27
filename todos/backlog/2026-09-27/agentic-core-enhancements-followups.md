# Follow-ups — agentic-core enhancements

Task `task_4` implementation is complete under `SPEC-CORE-ENHANCEMENTS@4`; this list records only blocked host observations and work that has an explicit future trigger. None of these items is an in-progress implementation slice. See the [completion report](../../done/2026-09-27/agentic-core-enhancements-report.md).

## Host-dependent checks

- **HF-CLI-SMOKE-01 — Successful Copilot/Codex response.** The Copilot CLI reported its monthly quota exhausted before a model response. Recheck the destination harness budget using `harness-distribution` after its provider reports availability, then make at most one bounded request. Do not guess or resume an existing session.
- **HF-COPILOT-PACKAGING-01 — Marketplace-based refresh.** Copilot installed version `0.3.3` from the local path successfully, but warned that direct local-path installs are deprecated. Before the next refresh, move to a supported marketplace install path if this Copilot CLI provides one; the current installation works.
- **HF-CONTEXT-01 — Live context observations.** Capture active-session token use only from the host's supported `/context` or `/status` surface with its source and observation time. Keep missing fields `unknown`; do not inspect private session data or add polling.
- **HF-GITHUB-APP-ENV-01 — GitHub MCP host setup.** The plugin's GitHub MCP process needs host-provided GitHub App environment variables, which were unset in this shell. Configure them only through the host's approved secret/environment mechanism if GitHub MCP use is required.
- **HF-QA-ROLE-01 — Custom QA agent.** The host did not expose the `quality-assurance` agent type. Focused local checks and a separate read-only Codex CLI review were completed; retry a custom independent QA pass only when the host provides that role.

## Architecture work with explicit triggers

- **IDEA-SKILL-HYGIENE-01:** Define a representative skill-load benchmark, measurable fan-out/size metrics, and an actionable threshold before implementing a hygiene score.
- **IDEA-MEMORY-DAG-01:** Reopen automated stale-note propagation when an approved memory store exposes stable note provenance and source revisions.
- **IDEA-RUNTIME-POLICY-01:** Reopen a shared policy gateway only when a named host/tool operation, enforcement point, policy owner, and audit need exist.
- **IDEA-OPTIMIZER-01:** Evaluate an external optimizer only with a frozen benchmark and holdout, semantic/size gates, lineage, cost ceiling, and a human promotion owner. Preserve the separate active `task_3` evaluation.
- External providers or media capabilities need a concrete product task, representative inputs, deployment constraints, and a measured baseline before adoption.

## Preserved parallel work

`task_3` / `harness_factory` remains active in the other session. Keep its source and canonical task ledger unchanged; that session may consume the refreshed plugin after its host starts a new session.
