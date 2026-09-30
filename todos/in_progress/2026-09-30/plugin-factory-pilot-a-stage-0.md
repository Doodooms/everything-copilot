# Plugin Factory Pilot A — deterministic Stage 0

Status: blocked on authorized GitHub App publication
Task record: `docs/harness-history/task_8/manifest.json`
Specification: `SPEC-PLUGIN-FACTORY-PILOT-A@1`
Base: `develop@5ab9d0e7a1e4a7da467237e22e12b1149da76145`
Branch: `feat/plugin-factory-pilot-a-migration-readiness`

Implement the local `migration-readiness` vertical Expertise Pack and only the
Codex/Harness Factory plumbing required to make its later bounded routing
experiment reproducible. Stage 0 is deterministic and local. It does not run
Codex model trials, Waza model evaluation, or SkillOpt.

## Requirements

- `REQ-PA-PACK`: Add Pack-owned coordinator, three migration-readiness reviewer
  roles, and a migration-readiness skill with only consumed support resources.
  It is cognition-only and independent from Core SWE cognition.
- `REQ-PA-ROUTING`: Store exactly 12 frozen routing cases in one canonical
  routing spec (six positive and six negative); derive the Waza representation
  from it and record the corpus digest.
- `REQ-PA-OBSERVATION`: Observe skill invocation and Pack specialist delegation
  only from recognized Codex runtime events; preserve `unknown` where events do
  not support a conclusion and retain current TDD routing behavior.
- `REQ-PA-ISOLATION`: Build and materialize the Codex plugin into an isolated
  local scratch project with project-local agents/configuration and no unrelated
  plugin/MCP state or external GitHub target repository.
- `REQ-PA-BUDGET`: Enforce the experiment's 24 harness invocations as 12 cases
  × 2 arms, one per case/arm, sequentially, with no retries and explicit
  failure-stop. Provider model calls remain optional telemetry or `unknown`;
  model turns/tokens/latency are measurements. Keep unsupported required budget
  dimensions fail-closed and do not weaken existing profiles silently.
- `REQ-PA-STAGE0`: Complete deterministic Pack, projection, event observer,
  isolation, profile, and reproducibility checks before any future model run.
- `REQ-PA-LIFECYCLE`: Keep implementation local to this isolated Plugin Factory
  worktree; run QA and Reviewer; publish a semantic feature branch and PR to
  `develop` without merging, using only the authorized GitHub App path.

## Acceptance criteria

- `AC-PA-PACK`: `migration-readiness` validates and compiles to Codex; its
  manifest declares no MCP, database, SQL/code execution, or provider mutation;
  its Pack agents and skill remain Pack-owned.
- `AC-PA-ROUTING`: One canonical 12-case corpus has six positive cases with
  expected route `migration-readiness` and six negatives meaning “not this
  skill”; negatives have no invented route IDs. A stable digest is recorded,
  and Waza data is generated from this source. Frozen corpus digest:
  `8581b32eb37d09114dd63ba4da0a0ed4c57f1847a5920aaf195735528af84df7`.
- `AC-PA-OBSERVATION`: Fixture tests distinguish recognized invocation,
  recognized non-invocation, and missing/unrecognized evidence; delegation
  records event-derived Pack-owned roles and run/case association or `unknown`.
  No conclusion is inferred from final response prose.
- `AC-PA-ISOLATION`: A temporary local project contains only the generated
  Pilot A plugin, project-local Codex agent sidecars, and isolated marketplace
  config; runtime setup uses only the local scratch project and requires no external repository or service.
- `AC-PA-BUDGET`: The later profile permits exactly 24 sequential harness
  invocations with zero retries and a stop-on-failure policy. It does not claim
  provider model-call enforcement; existing profiles that require unsupported
  dimensions still fail before invocation.
- `AC-PA-METRICS`: The later result contract records requested/observed routes,
  completion checks, harness invocations, optional provider calls, model turns,
  reported tokens/latency, delegation events, validation failures, package and
  repository digests, and event/transcript reference. Standard FP rate and the
  legacy discovery rate are reported separately.
- `AC-PA-STATIC`: All Stage 0 checks are deterministic, reproducible, and pass;
  zero Codex model trials, Waza model runs, and SkillOpt runs occur.
- `AC-PA-RELEASE`: Current-revision independent QA and Reviewer evidence exists;
  a local commit and semantic PR target `develop`; the PR remains unmerged.

## Pilot A runtime experiment policy

These thresholds apply only to the later, unoptimized Pilot A experiment; they
are not general Plugin Factory policy and are not Stage 0 pass criteria:

- Routing: at least 5/6 positive cases invoke `migration-readiness`, and 0/6
  negative cases invoke it.
- Completion: at least 5/6 positive cases satisfy their frozen deterministic
  checks; no case may return `READY` when required evidence is explicitly
  absent.
- Specialist behavior: compare observed delegation events with each frozen
  positive case's `expected_specialist_roles`. If event capture is unavailable
  or incomplete, the observation is `unknown`, never `PASS`.

## Approved semantics and constraints

- Assessment results are `READY`, `CONDITIONAL`, or `BLOCKED`, with evidence
  and explicit unknowns. Missing material evidence is not treated as absent
  fact; it can require a conditional or blocked result.
- The skill admits concrete database schema/data migration readiness reviews
  involving compatibility, rollout/recovery, backfill/data integrity, or
  coexistence. It excludes migration-code writing, SQL execution, generic SQL
  explanation, API-only compatibility, live incident diagnosis, performance
  tuning, and database product selection.
- Expected positive route: `migration-readiness`; expected negative meaning:
  “not this skill”.
- Waza is used only for frozen task/spec representation and static/spec checks.
  Codex runtime trials belong to Plugin Factory Harness Factory.
- Harness invocations, provider model calls, and model turns are distinct
  measurements. No caller-forgeable `model_call_limit_enforced` flag is allowed.
- No Agentic Core/SWE extraction, Core SWE agent extension, external target
  repository, Substrat change, model trial, Waza model evaluation, or SkillOpt.
- `/home/pm/projets-persos/plugin-factory` remains untouched. The canonical
  source, generated package, and evaluation scratch project remain local; no
  external runtime-proof repository or GitHub target is part of Pilot A.


## Stage 0 completion checkpoint

Implementation commit: `6f94cd1f4cabde0473d2bebe1cb5e66e50913e17` on `feat/plugin-factory-pilot-a-migration-readiness`.

The canonical Pack validates with content digest
`7475ad69b773d5f2ae3abc3fa7276c4736b4a57e62f3057dcf3f92c95b00b112`.
The frozen case corpus digest is
`8581b32eb37d09114dd63ba4da0a0ed4c57f1847a5920aaf195735528af84df7`.
The generated Codex projection has 11 files and digest
`558b5931839a7af5a0381d1432500168e6acf1b01f6626b46cfaafff46560581`;
two clean builds produced identical trees. The generated Waza static tree
matches its checked-in 13-file representation.

The isolated local Codex scratch project is `/tmp/plugin-factory-pilot-a-codex-scratch-wup9mitg/project` at local commit
`9023977723c318a819947fdeca51cae048da0a2f`. It has no remote, no MCP files, four project-local agent
sidecars, and a clean tree. This repository is not an external target and is
not connected to any runtime-proof service.

Current gates: QA `QA-RUN-PA-STAGE0-20260930-R3` PASS; Reviewer `REVIEW-PA-STAGE0-20260930-R1` APPROVE. Focused
tests: 84 passed, 7 subtests; Ruff check/format and staged diff check PASS.
The `waza` CLI is unavailable; generated Waza YAML is validated through the
repository generator, determinism test, static parsing and tree equivalence.

The 24-invocation ceiling and zero-retry policy apply to one complete schedule.
The durable relaunch reservation is scoped to the caller-provided `--state-root`;
choosing another state root starts a separate ledger. Provider model calls remain
unknown unless trustworthy telemetry is captured. Runtime behavior is
`NOT_RUNTIME_TESTED`.

Publication is blocked: the approved Agentic Core GitHub App mutation path is
not available in this session, and repository policy prohibits the hosted
GitHub connector and user credentials. No branch was pushed and no PR was
created. No Codex model run, Waza model evaluation, or SkillOpt run occurred.

### Later bounded Codex evaluation command

After the Work Pilot A packet supplies approved baseline and candidate profiles,
and after publication/PR gates are resolved, run the following once with a new
artifact and a persistent state root:

```bash
uv run --no-project --with PyYAML --with typer python -m harness_factory pilot-a-run \
  --cases /tmp/plugin-factory-pilot-a/experiments/routing/specs/migration-readiness.json \
  --baseline-profile <approved-baseline.profile.json> \
  --candidate-profile <approved-candidate.profile.json> \
  --repo-root /tmp/plugin-factory-pilot-a-codex-scratch-wup9mitg/project \
  --base-revision 9023977723c318a819947fdeca51cae048da0a2f \
  --canonical-revision 6f94cd1f4cabde0473d2bebe1cb5e66e50913e17 \
  --state-root <new-persistent-local-state-root> \
  --owner pilot-a-stage0 \
  --artifact <new-pilot-a-result.json> \
  --max-harness-invocations 24
```

This command was not run. Its profile paths and authorization remain pending the
Work packet and later explicit bounded-trial checkpoint.
