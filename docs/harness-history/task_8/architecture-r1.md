# Architecture r1 — Plugin Factory Pilot A

- Specification: `SPEC-PLUGIN-FACTORY-PILOT-A@1`
- Risk: `L2`
- Base: `5ab9d0e7a1e4a7da467237e22e12b1149da76145`
- Owner: Orchestrator, adopting Architect evidence and resolving the remaining
  role and event-observation decisions for deterministic Stage 0.

## Adopted boundaries

1. `migration-readiness` is a vertical Expertise Pack. Existing
   `expertise.parser.parse_pack` and `expertise.targets.compile_target` own
   validation and projection. The Pack contributes four independent agents:
   - `migration-readiness-coordinator`: organize evidence and synthesize the
     bounded assessment;
   - `schema-compatibility-reviewer`: old/new schema, client-version and
     coexistence compatibility;
   - `data-integrity-reviewer`: backfill, invariants, constraints, reconciliation
     and validation evidence;
   - `rollout-readiness-reviewer`: rollout ordering, dependency readiness,
     rollback and forward-recovery feasibility.
2. A single canonical routing JSON spec owns exactly twelve prompt/oracle
   cases. Waza task data is generated from it and is never independently edited.
3. Keep Harness Factory's existing `HarnessRunManager` Git top-level and commit
   invariant. A disposable local-only seed repository contains the generated
   Codex plugin and Pack-owned agent sidecars; the existing Codex project plugin
   configuration context remains responsible for marketplace/config material.
   The temporary seed has no remote and lives outside the canonical source.
4. Budget requirements are declarative. Harness invocation count can be
   enforced by the local scheduler; Codex provider model-call count cannot.
   Existing profiles requiring provider-call enforcement remain fail-closed.
   Do not add an input boolean that asserts enforcement.

## Codex evidence boundary

Local executable: `codex-cli 0.158.0` (`codex --version`). Local
`codex exec --help` exposes `--json`, which emits JSONL.

The versioned Codex source for `rust-v0.158.0` defines `ThreadItemDetails` with
`CollabToolCall` and a `CollabToolCallItem` containing `tool`,
`sender_thread_id`, `receiver_thread_ids`, `prompt`, `agents_states`, and
`status`; it has no named Pack-agent field. Its core `skills.rs` code increments
`codex.skill.injected` with a `skill` attribute and `invoke_type` for explicit
skill injection. These are transport/source contracts, not proof that the
installed CLI exports all relevant telemetry for this plugin. Runtime capture
must be separately verified during a later authorized trial.

Consequences for Pilot A:

- A recognized `codex.skill.injected` metric carrying
  `skill=migration-readiness` is positive route evidence. Missing or
  unrecognized skill evidence is `unknown`; it is not treated as a negative.
- A completed `collab_tool_call` for `spawn_agent` with a receiver thread ID
  proves a delegation event occurred and may be associated to the enclosing
  harness run/case. The current exec payload cannot name which reviewer role
  was invoked; record the role as `unknown` rather than infer it from prompt
  text, expected structure or final response.
- Codex does not emit a dedicated skill-invocation item in its `exec --json`
  model in this version. Waza/synthetic event types are not accepted as Codex
  runtime evidence.
- Runtime route discovery, named specialist attribution and sidecar discovery
  remain `NOT_RUNTIME_TESTED` in Stage 0. No model invocation is part of this
  task.

## Sources

- Local CLI: `codex-cli 0.158.0`; `codex exec --help` (read-only inspection).
- Upstream versioned source: [Codex exec event models at rust-v0.158.0](https://github.com/openai/codex/blob/rust-v0.158.0/codex-rs/exec/src/exec_events.rs).
- Upstream versioned source: [Codex core skill telemetry at rust-v0.158.0](https://github.com/openai/codex/blob/rust-v0.158.0/codex-rs/core/src/skills.rs).
- Repository seams: `harness_factory/adapters.py`,
  `harness_factory/evaluation.py`, `harness_factory/runs.py`,
  `skill_harness/routing.py`, `expertise/parser.py`,
  `expertise/targets/codex.py`.

## Explicit exclusions

No external GitHub target repository, no Substrat testbed, no shared checkout,
no Codex model trial, no Waza model evaluation, no SkillOpt, no generic routing
framework, no Core SWE extraction, and no PR merge.
