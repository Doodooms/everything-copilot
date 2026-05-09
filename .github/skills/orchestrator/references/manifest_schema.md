# Orchestrator manifest schema and guidelines

This reference documents the `manifest` shape, the `plan_index` contract, guardrails for `patch` and `full_content` workflows, delegation requirements, and audit expectations.

## Minimal manifest fields

- `id` (string): unique task id
- `title` (string)
- `description` (string)
- `change_type` (string): `patch` | `full_content`
- `base_branch` (string): branch to merge into (default: `main`)
- `plan_index` (object): compact mapping of plan sections and repo-structure block (see below)
- `test_commands` (array[string])
- `apply_policy` (string): `require_manual` | `auto-merge-on-green` | `auto-apply`
- `risk_level` (string): `low` | `medium` | `high`
- `approve_required` (bool)
 - `assumptions` (array[object], optional): explicit, structured assumptions made during planning. Each entry SHOULD be an object with `id`, `description`, `made_by` (string), and `date` (ISO-8601).
 - `uncertainties` (array[object], optional): known uncertainties or fragile points. Each entry SHOULD include `id`, `description`, `impact` (short summary), and `mitigation` (if known).
 - `skipped_phases` (array[object], optional): when a phase is intentionally skipped the manifest MUST record an entry here. Each entry MUST include `phase` (one of Research|Dev|Quality|Commit), `reason`, `recorded_by`, and `timestamp` (ISO-8601).

### `patch` specifics

- `patches`: array of objects `{ file, patch, summary, test_commands, risk_level }` where `patch` is an apply_patch-style diff string.
- Suggested thresholds: ≤3 files and ≤200 total lines changed.

### `full_content` specifics

- `full_content`: map of `file: new_contents` OR `files`: array of `{ file, source_path }`.
- Provide `branch_name` for the branch to create and `test_commands` to validate the branch.

## `plan_index` contract

The `plan_index` is a compact, machine-friendly object that points into the authoritative plan file (which the Orchestrator attaches to subagents via `#file:<path>`). It must contain at minimum:

- `repo_structure`: array of `{ path, reason? }` entries describing folders and why they're relevant.
- `sections`: array of `{ id, heading, summary?, lines?: [start,end] }` mapping to plan sections referenced by the manifest.

Example `plan_index` snippet:

```yaml
plan_index:
  repo_structure:
    - path: src/datasets
      reason: "dataset loaders + transforms"
    - path: src/models
      reason: "model implementations and heads"
  sections:
    - id: training_contract
      heading: "Training contract"
      summary: "Enforce externally provided COCO splits under annotations/<version>"
```

Subagents MUST rely on `plan_index` (and the attached plan file) to determine which repository files to inspect. Legacy fields (`allowed_files`, `plan_path`, `plan_snapshot`) are deprecated and must not be used.

## Delegation

If a manifest includes a `delegate` section (for Copilot CLI or other implementers), the delegate MUST return a JSON object following the standardized return contract below. The Orchestrator will treat the `status` field as authoritative and will NOT infer success from commits or logs alone.

Required delegate return contract (recommended JSON shape):

```
{
  "status": "success|partial|failed",      # REQUIRED — authoritative status
  "branch_name": "string",
  "commit_shas": ["sha1", "sha2"],
  "worktree_path": "/abs/path/to/worktree",  # optional for remote delegates
  "pr_url": "https://..." | null,
  "pr_number": 123 | null,
  "test_results": {
      "exit_code": 0,
      "summary": "short summary",
      "artifacts": ["path/to/artifact"],
      "logs": "path/or/url/to/logs"
  },
  "deviations": [
      { "file": "src/foo.py", "description": "reason for deviation", "impact": "low|medium|high", "suggested_fix": "..." }
  ],
  "artifacts": ["..."],
  "timestamp": "ISO-8601",
  "notes": "freeform notes"
}
```

Key semantics:

- `status` is authoritative — the Orchestrator MUST NOT infer global success from the presence of commits or a zero exit code alone. Delegates MUST always set `status`.
- `success`: delegate reports that the task completed as planned and tests passed.
- `partial`: delegate completed work but there are deviations (recorded in `deviations`) or some tests failed — Orchestrator SHOULD escalate, request correction, or run additional validation depending on `risk_level`.
- `failed`: delegate could not complete the task; Orchestrator MUST halt the automated flow and record the failure in the audit.

Deviations: delegates MUST enumerate any deviations from the submitted manifest/plan (files changed outside the manifest, skipped tests, environment differences). Each deviation entry should include `file` (if applicable), `description`, `impact`, and `suggested_fix` if available.

Test results: delegates SHOULD include `test_results` with an `exit_code`, `summary`, and links to logs/artifacts. The Orchestrator may still fetch logs or artifacts, but it MUST consult the `status` field first when deciding next actions.

## Audit

The Orchestrator writes `.github/plan_history/<task_id>.orchestration.json` with at minimum: `manifest`, `payloads_sent`, `subagent_responses`, `dry_run_results`, `apply_results`, `approvals`, `timestamps`.

Additional audit requirements:

- If any phase is skipped the `skipped_phases` entries from the manifest MUST be persisted to the orchestration record and must include `recorded_by` and `timestamp`.
- Persist `assumptions` and `uncertainties` from the manifest into the audit record so reviewers can understand planning dependencies and fragile points.
- Persist the full delegate return object (including `status`, `deviations`, and `test_results`) so auditors can reason about partial or failed delegations and trace corrective actions.

## Examples

See `../assets/examples/example_manifest_patch.yaml` and `../assets/examples/example_manifest_full_content.yaml` for working manifest examples.
