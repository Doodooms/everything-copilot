# Architecture brief — task_4 / SPEC-CORE-ENHANCEMENTS@2

## Decision

Keep the existing plugin boundaries and extend the nearest owner with small, portable procedures:

1. `multi-harness` owns evidence-based context compaction and provider work placement. `context-management` owns local estimates, retrieval, and durable memory. Exact active-session telemetry remains host-reported; provider allowance and billing units remain separate.
2. Context records distinguish raw history, active context, and durable memory. Retrieval state is `available`, `retrieved`, or `expanded`; a source can support a claim only after retrieval. Durable notes carry enough source/revision or observation-date provenance to detect staleness.
3. JSON Schema Draft 2020-12 is the language-neutral contract for handoffs, manifests and their persisted wrapper, orchestration events, and task transitions. A local `uv`-managed `jsonschema` validator checks structure and, when a repository is supplied, resolves Git objects and artifact SHA-256 digests. Git object IDs remain distinct from file-content digests.
4. Rust MCP authoring is a child workflow of the existing MCP authoring route. It selects APIs from the pinned `rmcp` version and matching official examples, and avoids unmeasured performance claims.
5. Research gains `existing-solution-research` for substantial new abstractions where standards or existing projects could change build-versus-reuse. It reports evidence and classification but leaves the decision with Architecture/Orchestration.
6. The architecture ideas file's skill-routing, testing, implementation-design, optimization, runtime-governance, security, provider, and diagram proposals are mapped to existing capabilities or explicit backlog triggers. Do not add a second plugin/runtime, copy external corpora, or create speculative provider integrations.
7. `todos/README.md` becomes the index; intake remains in topic folders, current assignments use dated `in_progress`, and reviewed sources plus reports move to dated `done`.

## Evidence and tradeoffs

- Existing `context-management` already separates local token projection from hosted values; the retrieval-state and freshness rules strengthen that design without making repository size a proxy for active context.
- `implementation-design`, `test-design`, skill validation, skill optimization, security, orchestration, and dependency-aware SDD invalidation already cover several architecture-file proposals. Extending those owners avoids duplicate skills.
- Existing persisted manifests are wrappers, so validating only their inner `manifest` object leaves envelope identity/status unchecked. A dedicated wrapper schema closes that gap.
- JSON Schema remains canonical because packets cross harnesses; the Python helper is an implementation of that portable contract rather than a second source of field definitions.
- Candidate tools are assessed as references, benchmarks, or conditional providers. No unmeasured external code or runtime is added to core.

## Assumptions and non-goals

- Host status surfaces can be used only by the active host when supported; this session cannot query another session's private context or quota.
- The research workflow does not clone, install, or execute candidate projects.
- Existing pre-schema history is historical input and will not be rewritten in bulk.
- This task does not alter the separate harness-evaluation workstream or unrelated dirty files.

## Status

This is the Orchestrator's local architecture decision. The host rejected the Architect specialist type as unavailable; no architecture specialist or independent reviewer ran.
