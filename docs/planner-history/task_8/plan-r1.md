# Plan r1 — Plugin Factory Pilot A deterministic Stage 0

- Task: `task_8`
- Specification: `SPEC-PLUGIN-FACTORY-PILOT-A@1`
- Risk: `L2`
- Base: `develop@5ab9d0e7a1e4a7da467237e22e12b1149da76145`
- Branch: `feat/plugin-factory-pilot-a-migration-readiness`
- Workspace: `/tmp/plugin-factory-pilot-a`

## Decisions and evidence

1. Pilot A cognition is a vertical Expertise Pack compiled by the existing
   `expertise` source/parser/target pipeline. Its four agents are Pack-owned:
   `migration-readiness-coordinator`, `schema-compatibility-reviewer`,
   `data-integrity-reviewer`, and `rollout-readiness-reviewer`. Their scopes
   follow those names: schema/client-version coexistence; backfill/data
   invariants; deployment ordering and rollback or forward recovery. The
   coordinator synthesizes those evidence streams and returns only
   `READY`, `CONDITIONAL`, or `BLOCKED`, retaining unknowns.
2. `experiments/routing/specs/migration-readiness.json` is the sole canonical
   routing prompt/oracle source. Waza files are deterministic generated views;
   no second hand-maintained prompt set is introduced.
3. Codex CLI `0.158.0` is installed locally. Its `codex exec --json` event
   contract includes `collab_tool_call` items and can expose `spawn_agent`
   receiver thread IDs, but the exec item has no specialist role identifier.
   It does not define a first-class skill-invocation JSONL item. The Codex
   source for this version emits a `codex.skill.injected` OTel counter carrying
   a `skill` attribute for detected explicit skill invocations. The observer
   will accept only documented event/metric payloads, associate them with the
   enclosing run/case, and retain `unknown` when role identity or telemetry is
   absent. It will not infer routes or roles from final response prose,
   expected workflow structure, or guessed event names. No runtime probe is
   allowed in Stage 0.
4. For the bounded pilot profile, `max_runs` maps to one sequential harness
   invocation per case/arm; `max_failures_before_stop=1` stops on the first
   failed result. The profile declares required enforcement dimensions. The
   runner itself can enforce harness invocations, but cannot enforce provider
   model-call counts. Existing profiles that require provider-call enforcement
   remain blocked before invocation. No caller-supplied enforcement boolean is
   accepted.
5. Keep `HarnessRunManager`'s Git-worktree invariant by making a disposable,
   local-only seed Git repository with only the compiled Pack target and
   generated `.codex/agents/` sidecars. Existing Codex project marketplace
   setup remains the activation/configuration owner. The seed has no remote
   and is outside the canonical source checkout.
6. The new repository `Doodooms/substrat-control-runtime-testbed` is excluded
   and is neither a Pilot A target nor evaluation infrastructure.

## Phase plan

| Task | Owner | Scope | Requirements → acceptance | Exit evidence |
|---|---|---|---|---|
| `TASK-8-01` | Architect | Read-only source/contract map | all | Architecture handoff recorded; source/event limits retained |
| `TASK-8-02` | Orchestrator | Resolve role semantics and select evidence boundaries | `REQ-PA-PACK`, `REQ-PA-OBSERVATION` → `AC-PA-PACK`, `AC-PA-OBSERVATION` | This plan records role scopes and precise Codex event limitations |
| `TASK-8-03` | Implementer | Pack source, sole 12-case corpus, generated Waza representation and deterministic generator | `REQ-PA-PACK`, `REQ-PA-ROUTING` → `AC-PA-PACK`, `AC-PA-ROUTING` | Pack validate/test/Codex compile; 6+6 exact; stable corpus digest; generated output equals canonical inputs |
| `TASK-8-04` | Implementer | Pilot-specific Codex event/metric observer, budget requirement contract, and evaluation metrics | `REQ-PA-OBSERVATION`, `REQ-PA-BUDGET` → `AC-PA-OBSERVATION`, `AC-PA-BUDGET`, `AC-PA-METRICS` | Recognized/missing/unrecognized fixtures; explicit unknown role; no prose inference; 24 call bound and legacy fail-closed regression |
| `TASK-8-05` | Implementer | Local scratch project and seed repository materializer | `REQ-PA-ISOLATION`, `REQ-PA-STAGE0` → `AC-PA-ISOLATION`, `AC-PA-STATIC` | Temp payload only; local Git commit; no remote; sidecar/config presence; no unrelated plugin/MCP state |
| `TASK-8-06` | Orchestrator + QA + Reviewer | Integrate, deterministic validation, current-revision independent gates and release handoff | all → `AC-PA-STATIC`, `AC-PA-RELEASE` | Tests/Ruff/diff evidence; actual QA and Reviewer returns; commit and App-path PR attempt, no merge |

## File ownership and validation

- Pack/corpus implementer owns `expertise/packs/migration-readiness/**`,
  `experiments/routing/specs/migration-readiness.json`, a generator and its
  generated Waza view, plus Pack-specific tests.
- Observer/budget implementer owns new Pilot-specific observer code, the
  bounded changes to `harness_factory/evaluation.py`, and isolated tests for
  those contracts. Generic TDD routing behavior must remain unchanged.
- Scratch implementer owns a new Pilot-specific local project materializer
  and isolated tests. Shared `HarnessRunManager` invariants stay unchanged.
- Orchestrator owns task/plan/evidence files, final acceptance and convergence.
- Run `expertise validate migration-readiness`, `expertise test
  migration-readiness`, Codex target compilation and sidecar checks; deterministic
  routing/Waza generation and static verification; observer/budget/scratch
  fixture tests; focused existing Harness Factory/TDD tests; focused Ruff check
  and format; and `git diff --check`.
- Never run Codex model trials, Waza model evaluation, or SkillOpt.
- QA and Reviewer inspect the current final code after focused validation.
- The configured authorized GitHub App MCP is required for remote publication.
  No SSH, user credential, or hosted connector fallback is allowed.

## Known limits

- Runtime skill discovery, exact route outcomes, and specialist-agent names are
  `NOT_RUNTIME_TESTED` in this Stage 0. `collab_tool_call` proves that a
  delegation event occurred when present; the current exec JSON item does not
  identify which named Pack role ran. Missing role attribution stays unknown.
- Codex `codex.skill.injected` metric support is a source-backed schema, not
  proof that the currently installed CLI exports it from `exec` in this local
  project configuration. Stage 0 can validate the parser/config statically;
  only a later approved bounded run can establish runtime delivery.
- Waza CLI availability is checked locally. If absent, generated Waza files
  receive repository-native schema/determinism checks and CLI validation is
  reported blocked/unavailable; no installation or model evaluation is
  introduced by this plan.
- Standard false-positive rate `FP/(FP+TN)` remains distinct from the existing
  `discovery_false_positive_rate` field.
