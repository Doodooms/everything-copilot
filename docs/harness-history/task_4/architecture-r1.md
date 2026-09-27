# Architecture brief — task_4 / SPEC-CORE-ENHANCEMENTS@1

## Decision

Keep the existing plugin boundaries and add the smallest procedures/interfaces inside them:

1. `multi-harness` owns cross-harness budget-aware work assignment and safe session/context handoff. Add `smart-compact` and `harness-distribution` as two immediate workflows. `context-management` remains the owner of local prompt projection estimates and durable context records; the new workflow links to that estimator rather than claiming it measures a live session.
2. The active host's documented status surface is the source of live values: Codex `/status`; Copilot `/context` for live context window and `/usage` for session usage. Account dashboards are fallbacks for plan-cycle budget data. A query about another active session requires that harness's explicit supported session path; do not inspect private session databases. The current session tool catalog cannot query those surfaces.
3. Use JSON Schema Draft 2020-12 as the canonical, language-neutral interface for handoff envelopes, orchestration events, task transitions, and manifests. Put schemas and a local `uv`-runnable validator in the orchestration skill. Validate objects before the helper persists them and validate a handoff before the receiver advances. JSON Schema was chosen over Pydantic models as the source of truth because Copilot, Codex, and future harnesses can consume the same contract; Python `jsonschema` provides the local validation implementation.
4. A handoff distinguishes a Git object ID (`commit_shas`, 40/64 hex) from an artifact digest (`sha256`, 64 hex). With a repository path, the validator resolves each claimed commit and verifies its changed-path coverage and each artifact digest. If no commit was authorized/created, the envelope requires a `commit_status` and reason; empty SHAs are not silently interpreted as an authoritative commit.
5. Rust MCP guidance is an immediate `plugin-engineering` workflow selected by the existing MCP authoring entry point. It uses `rmcp`, only enables features required by the selected transport, and starts with upstream official examples rather than maintaining a second standalone MCP skill.
6. Todo intake remains separate from assigned work. `todos/README.md` becomes the index; intake stays in category folders, active assignments/plans use date folders, and completed source records and reports go under dated `done` folders.

## Evidence and tradeoffs

- Existing `context-management` already owns local-only estimates, and `multi-harness` already owns Copilot/Codex communication. Splitting those responsibilities avoids either adding provider-quota logic to a token estimator or duplicating session-contact policy.
- Existing `orchestrator.py` writes JSONL events and manifests but checks only a subset of their structure. One versioned contract and validator cover the exact structures crossing agent/task boundaries without importing an external agent runtime.
- The current MCP authoring flow is one entry point under `plugin-engineering`; a Rust-specific child workflow preserves one router while correcting the old monolithic examples.
- Exact resource values can vary by plan, model, host, and freshness. The skill therefore records source/time/status and treats missing data as `unknown`; it does not scrape credentials, calculate false cross-provider equivalences, or promise a recurring timer.

## Assumptions and non-goals

- A host-provided status result can be read by the active harness when it supports the documented command. This architecture does not add a quota API client or remote account access.
- Resource snapshots are transient by default; durable records store the routing decision and source/time but omit exact personal allowance values unless the caller explicitly needs them.
- No external project or MCP server is added as a core dependency. Candidate projects remain references/providers/benchmarks until a measured requirement justifies adoption.
- No change is made to `task_3`, `harness_factory`, its tests, the pre-existing dirty agent definitions, or repository Git lifecycle.

## Rejected alternatives

- One combined context/quota estimator was rejected: current context occupancy, provider allowance, and billing usage have different units, sources, and reset lifecycles.
- Pydantic-only contracts were rejected as canonical because they make Python the protocol authority even though exchanges cross harnesses; JSON Schema plus a Python validator retains typed validation while remaining portable.
- Importing external agent runtimes or persistent-memory products was rejected without a workload and measured comparison.

## Status

This is the Orchestrator's local architecture decision because the host returned `agent type is currently not available` for the Architect specialist. No architecture specialist ran and no independent architecture approval is claimed.
