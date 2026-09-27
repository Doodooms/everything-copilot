# Cost evaluation follow-up

## Checkpoint

`task_3` released its local implementation as `partial` on 2026-09-27. The
current owner is **unassigned**; this file records the evidence needed before a
new implementation slice is assigned. The original request remains in
[`todos/harness/cost-eval-opt.md`](../../harness/cost-eval-opt.md), and the
canonical history is in [`docs/harness-history/task_3/manifest.json`](../../../docs/harness-history/task_3/manifest.json).

The r7 plan prohibited tests and Git commits. The user later explicitly
authorized focused validation, task-owned commits, and a partial release to
make the work durable. That newer direction is recorded in the manifest and
task history; the approved experiment budget and safety limits remain in
force.

The updated manifest passes both the Orchestrator manifest validator and the
SDD coverage validator. The task event journal records the release and the
remaining ownership is unassigned. The separate append-only transition ledger
was left intact: its helper rejects a legacy `in_progress` value earlier in
the file and does not permit a repeated `partial` transition; the latest task
status already records `task_3` as partial.

## Criterion status

| Criterion | Status | Evidence or remaining condition |
|---|---|---|
| `AC-COST-1` | PASS | Nine-scenario suite validates; malformed required behavior is rejected locally in a unit test. |
| `AC-COST-2` | PASS | Codex-only target and allowed Copilot-reason policy are covered by a unit test. |
| `AC-COST-3` | BLOCKED | `outputs/evals/baseline-inventory-r7.json` records that no matched flat/hierarchical or old/new routing pair exists. Do not synthesize one. |
| `AC-COST-4` | PARTIAL | The runner refuses before invocation when provider-call limits are unenforceable; a unit test verifies zero calls and a durable blocked artifact. No current adapter can enforce a provider-level call ceiling. |
| `AC-COST-5` | PARTIAL | The blocked artifact validates and reloads. A completed or failed provider-backed run has not been executed. |
| `AC-COST-6` | PARTIAL | The profile interface is implemented, but no provider-backed evaluation of a supplied profile was run. |
| `AC-COST-7` | PARTIAL | Suite, commands, budget policy, and limitations are documented. There are no behavioral benchmark results or matched baselines yet. |
| `AC-COST-8` | PARTIAL | Read-only, one-hop cross-harness request handling has focused tests. Independent QA has not verified the complete boundary. |

## Remaining gates

1. Keep `TASK-COST-05` blocked until a provider-call limit and non-persistent
   plugin/MCP isolation can both be enforced for the selected Codex invocation.
   Do not run a Codex or Copilot smoke before then.
2. Revisit `AC-COST-3` only if a provenance-backed matched baseline pair is
   found or the user changes the comparison requirement.
3. Keep `experiments/routing/` as candidate fixtures. Rendering all six
   candidates passed locally, but no Waza behavioral trial or architecture
   selection occurred.
4. Dispatch independent QA and Reviewer only from a host surface that exposes
   those roles. Focused unit tests and Ruff are not substitutes for either
   gate.
5. Reconcile task state and readiness claims after the applicable evidence
   exists; do not claim full convergence while these gates remain open.

No raw model transcripts, provider results, or generated evaluation corpus
were saved in the repository. The only retained evaluation output is the
intentional machine-readable baseline inventory.
