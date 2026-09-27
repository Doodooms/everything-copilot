# Cost evaluation suite

## Suite and profile

`agentic-core-v0.2.0/suite.json` contains one scenario for each of the nine
initial categories: skill discovery, skill routing, workflow routing, agent
routing, plugin loading, MCP exposure, risk-proportional routing, evidence
reuse, and cross-harness materialization. The suite pins the repository
fixture to revision `5c6dcd401e9a0d115e79c19f02de96ffed694686` and records
unknown or unsupported measurements as `unknown` in run artifacts.

`agentic-core-v0.2.0/profile.json` identifies the installed shared-cache
`agentic-core@agentic-workflow-local` v0.2.0 profile and records the observed
SHA256 values for its multi-harness skill and Codex/Copilot workflows. It is a
reference-only profile descriptor for this attempt. Its current
`source_mode: external` means `suite-run` would copy the cache directory into
the managed workspace and use the local project-plugin path; that is not the
installed-cache/normal-user-config smoke required by plan r7. Do not use this
descriptor for that smoke. The native-cache adapter path remains incomplete.
The smoke is blocked by
plan r7 before model invocation because the current Codex CLI does not expose
an enforceable provider-call cap or a proven non-persistent isolation control
for all enabled plugins and MCP servers.

## Baselines

`outputs/evals/baseline-inventory-r7.json` records the machine-readable search
and its result. No matched flat-versus-hierarchical pair was found. No
old-versus-risk-proportional pair was found either. The unrelated SkillOpt
summary fields do not establish a matched pair. No baseline result was
synthesized, and the single permitted smoke budget is not used to manufacture
one. This leaves `AC-COST-3` as an evidence gap.

## Codex-first interface

The generic suite runner accepts an explicit Codex target and explicit
budgets. A future run using an executable profile should follow this shape,
with unique artifact paths and a profile whose execution mode has been
validated for the intended plugin source:

```sh
uv run python -m harness_factory suite-run \
  --suite experiments/harness-evals/agentic-core-v0.2.0/suite.json \
  --profile <profile.json> \
  --harness codex \
  --repo-root . \
  --state-root <isolated-state-directory> \
  --owner cost-eval \
  --artifact <run-artifact.json> \
  --preflight-artifact <preflight-artifact.json> \
  --max-runs 1 \
  --max-model-calls 1 \
  --max-tokens-if-known 25000 \
  --max-failures-before-stop 1
```

Copilot remains opt-in and requires exactly one justified reason:
`copilot_specific_behavior`, `portability_sample`,
`regression_confirmation`, or `host_specific_agent_behavior`. This attempt
made zero Copilot calls.

The runner stops before another invocation when a configured run or call
budget is exhausted, after the configured failure threshold, and on systemic
materialization, plugin-load, schema, or routing failures. It preserves
unknown token, latency, model-turn, and metric values instead of treating
them as zero. A token budget is checked when usage is known; a Codex turn
count that is unknown or differs from one stops further invocations.

Artifacts distinguish `usage.harness_invocations` from provider-level
`usage.model_calls`. Current adapters do not declare an enforceable provider
call cap, so the runner records a blocked artifact before the first adapter
invocation (`harness_invocations: 0`, `model_calls: 0`). If an invocation is
made by a future cap-enforcing adapter and its provider-call count is not
observable, the artifact preserves `model_calls: "unknown"`; that value is
not evidence that the configured call budget was met.

## Local checkpoint and remaining gates

The following local checks passed on 2026-09-27:

- `uv run --no-project python -m harness_factory suite-validate --suite experiments/harness-evals/agentic-core-v0.2.0/suite.json` — valid; nine scenarios.
- `uvx --with pyyaml --with jsonschema --with typer pytest -q tests/test_harness_factory.py` — 26 passed and six subtests passed.
- Ruff check and format check passed for `harness_factory/` and `tests/test_harness_factory.py`.
- The Codex-first runner test writes and reloads a blocked artifact with zero harness invocations when a trusted provider-call limit is unavailable.

No Codex, Copilot, or MCP invocation was made. No behavioral cost corpus or optimizer was run. The smoke remains blocked before invocation because the current Codex CLI does not provide an enforceable provider-call cap and effective plugin/MCP isolation has not been proven. `AC-COST-3` remains an evidence gap because no matched baseline pair exists. The native-cache profile is reference-only. Independent QA and Reviewer were not dispatched in this host. These gates keep the delivery partial; see [`cost-eval-opt-followups.md`](../../todos/backlog/2026-09-27/cost-eval-opt-followups.md).
