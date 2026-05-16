---
name: orchestrator
description: "Orchestrator skill: coordinate the 9-agent developer workflow; persist manifests and audits; enforce plan_index-first contract."
user-invocable: false
---

# Orchestrator Skill

Purpose:
- Coordinate multi-agent workflows across Orchestrator, Planner, Researcher, Implementer, Code Reviewer, Debugger, Documentalist, Sec Auditor, and Devops.
- Persist authoritative manifests to `.github/tasks/` and audit records to `.github/plan_history/`.
- Provide a machine-friendly `manifest` to guide subagents.

# AHK Integration Contract

When the `ahk` MCP server is connected in the workspace, the Orchestrator uses AHK as the operational task ledger while preserving the existing strategic and audit layers.

- `PLAN.md` remains the strategic source of truth.
- `.github/tasks/` and `.github/plan_history/` remain the orchestration audit trail.
- AHK owns operational task state, atomic claiming, action journaling, and health gates.

Expected AHK usage pattern when available:

1. Locate the operational task in AHK with `tasks.get`.
2. Create it with `tasks.add` if the approved manifest has no matching operational task yet.
3. Claim it with `tasks.claim` when execution actually begins.
4. Open an action with `actions.start` before substantive implementation work.
5. Record progress with `actions.write`, `actions.record_file`, and `actions.record_tool` during implementation and validation.
6. Close the action with `actions.complete` when the step is done.

The Orchestrator must not let AHK replace `PLAN.md` or the persisted manifest history. AHK is the operational execution surface, not the strategic planning surface.

# Plan Index Policy
- The manifest MUST include a `plan_index` (compact references into the plan, plus a repo-structure block at plan start).
- Subagents will use `plan_index` to determine repository files to inspect, so make sure it is accurate and up-to-date.

# Manifest schema (summary)
- `id`, `title`, `description`
- `change_type`: `patch` | `full_content`
- `plan_index`: object — compact mapping of plan sections and a repo-structure block
- `test_commands`, `apply_policy`, `risk_level`, `approve_required`
- For `patch` include `patches` array; for `full_content` include `full_content` map

Full schema reference: #file:./references/manifest_schema.md
Working examples: #file:./assets/example_manifest_patch.yaml and #file:./assets/example_manifest_full_content.yaml

# Manifest generation & Plan presentation

- The Orchestrator must **always** generate a manifest. Generated ids are simple monotonic
	identifiers in the form `task_1`, `task_2`, ... produced by scanning
	`.github/plan_history/` for prior task ids and incrementing. Generated
	manifests are minimal by design and MUST be presented to the user for
	review using the Plan presentation style described below before dispatch.

- The Orchestrator will not persist or dispatch an auto-generated manifest
	without either explicit user confirmation or an affirmative programmatic
	confirmation (for example via a structured `approve_required` field).

- Generated manifests include a placeholder `plan_index` (empty `repo_structure`
	and `sections`) so that subagents can be offered a default, but the
	Orchestrator will proactively surface the plan and request the missing
	plan-index details using #tool:vscode/askQuestions when necessary.

# Research invocation rules (when Orchestrator should call Researcher)

The Orchestrator decides whether to call the Researcher agent according to
deterministic rules:

- CALL Researcher when any of the following are true:
	- `requires_research: true` in the manifest
	- `risk_level` is `high`
	- `change_type` is `full_content`
	- `plan_index` is missing, empty, or insufficient to identify impacted files
	- the manifest references external services, connectors, or URLs

- CONSIDER calling Researcher when:
	- `risk_level` is `medium` and the manifest touches unfamiliar modules
	- the manifest omits `test_commands` or verification steps

When Researcher is invoked, the Orchestrator will provide a targeted `plan_index`
and a short query string describing what to research; Researcher outputs are
consumed programmatically (see Research Output Contract) and attached to the
orchestration record.

# Plan presentation style (authoritative plan delivered to users)

Plans must be presented to the user in a compact, human-readable form. Use
the following structure (no code blocks):

Title: {Title (2-10 words)}

TL;DR: {one-line summary — what, why, and recommended approach}

Steps:
1. {brief implementation step; annotate dependencies or parallelism}
2. {next step}

Relevant files:
- `path/to/file.py` — what to modify or reuse (reference specific functions)

Verification:
1. {specific commands or tests to run and expected outcomes}

Decisions:
- {explicit assumptions and scope inclusions/exclusions}

Further considerations:
1. {clarifying question with recommended options}

The Orchestrator must present the plan textually in this format to the user
and then use #tool:vscode/askQuestions to collect any missing decisions needed to
finalize the manifest. Do not end the plan with an unstructured blocking
question; use #tool:vscode/askQuestions to gather structured answers.

# Patch guardrails and full-content flow
- Use `patches` for ≤3 files and small deterministic edits.
- Use `full_content` for larger refactors; create a branch and PR as described by the manifest.

# Audit
- Persist full orchestration records to `.github/plan_history/<task_id>.orchestration.json`.

# Delegation Rules (explicit)

When the manifest delegates work (for example to `copilot_cli`), the Orchestrator enforces explicit, auditable rules about when phases must run, when they can be skipped, and what delegates must return.

- Research phase is MANDATORY when any of the following are true:
	- `change_type` is `full_content`.
	- `risk_level` is `high`.
	- The `plan_index` indicates changes to infrastructure, external integrations, or connectors (e.g., paths like `infra/`, `connectors/`, or `integration/`).
	- The manifest sets `requires_research: true`.

- Research may be SKIPPED only when ALL the following are true:
	- `change_type` is `patch` and `risk_level` is `low`.
	- The manifest explicitly includes a `skipped_phases` entry documenting the skip (see schema) with `phase: Research`, `reason`, `recorded_by`, and `timestamp`.
	- The manifest author or delegate provides a short `skip_rationale` and, when available, references to prior audit records that justify the skip.

- Any other specialist phase (Planner, Implementer, Code Reviewer, Debugger, Documentalist, Sec Auditor, Devops, or commit-message) may be skipped only with the same explicit recording in `skipped_phases` and a clear `reason`. The Orchestrator will persist this to the audit record and raise a flag in the orchestration summary.

Note: These rules are policy — the Orchestrator will validate that required phases were not skipped for high-risk or full-content changes and will refuse to auto-apply changes if mandatory phases are missing.

# Assumptions & Uncertainty Handling

To make planning deterministic and auditable, manifests MAY include structured `assumptions` and `uncertainties` fields.

- `assumptions`: explicit statements the plan depends on (example: "Assumes Azure SDK behavior as of 2025-12-01"). Use structured objects with `id`, `description`, `made_by`, and `date` to make these machine-readable.
- `uncertainties`: explicit fragile points and known unknowns (example: "External API rate limits may affect deploy step"). Each entry SHOULD include `id`, `description`, `impact`, and `mitigation`.

The Orchestrator persists `assumptions` and `uncertainties` to the orchestration audit. Reviewers MUST evaluate uncertainties during Research or Quality phases and document mitigation steps in the audit record.

# Delegate Return Contract (strengthened)

Delegates invoked by the Orchestrator MUST return a structured JSON object. The Orchestrator treats the returned `status` field as authoritative and will NOT silently interpret missing or partial information as success.

Minimal required delegate return fields (summary):

- `status`: one of `success`, `partial`, or `failed` (REQUIRED).
- `branch_name`, `commit_shas`, `worktree_path` (if applicable), `pr_url`/`pr_number`.
- `test_results`: structured object with `exit_code`, `summary`, and optional artifact/log links.
- `deviations`: array enumerating any deviations from the manifest/plan (file, description, impact, suggested_fix).
- `timestamp` and optional `notes`.

Semantics and Orchestrator behavior:
- `success`: continue the orchestration flow (next phase) per manifest `apply_policy`.
- `partial`: the Orchestrator MUST NOT auto-merge. It SHOULD escalate or request correction, and run configured remediation steps depending on `risk_level`.
- `failed`: the Orchestrator MUST halt automated progression, persist the failure in the audit, and surface the response to operators.

Delegates MUST explicitly document any deviations. The Orchestrator will record deviations in `.github/plan_history/<task_id>.orchestration.json` and use them when deciding whether to continue or to require human review.

# Audit and Skipped Phases

The Orchestrator's audit record MUST include:

- the original `manifest` including any `assumptions` / `uncertainties`;
- `skipped_phases` entries if any phases were intentionally skipped (with `phase`, `reason`, `recorded_by`, `timestamp`);
- the full delegate return object (including `status`, `deviations`, `test_results`, and artifacts);
- decisions taken by the Orchestrator in response to delegate `status` (continue/escalate/hold), and timestamps for those decisions.

This explicit recording guarantees that any decision to skip or shorten a phase is auditable and traceable.

## Resources

- Manifest schema & guidelines: `references/manifest_schema.md`
- Example manifests: `assets/examples/example_manifest_patch.yaml`, `assets/examples/example_manifest_full_content.yaml`
- Plan-index example: `assets/plan_index_example.md`
- Scripts: `scripts/generate_plan_index.py` (helper to generate a compact `plan_index` from a plan file)

## Optional containerized run-tests (for target repos with Docker)

The repository previously contained a `.github/scripts/` folder with OS-specific
helpers for building a reproducible development Docker image, running tests
inside an ephemeral container, and saving images. That folder was removed and
the helper logic was moved under the `orchestrator` skill so agents can import
or reuse it programmatically.

Manifest contract for delegates
--------------------------------
Delegates (such as `copilot_cli`) that produce a worktree and/or open a PR
should include the following fields in the returned `manifest` so the
Orchestrator and auditors can locate and verify the work:

- `worktree_path` (string): absolute path to the created worktree
- `branch` (string): branch name in the worktree
- `commit_shas` (array[string]): commit SHAs created by the delegate
- `pr_url` (string|null): URL of the created PR, if any
- `pr_number` (int|null): PR number, if any

Run-tests (reference pseudocode)
--------------------------------
Agents can reproduce the original `run_tests_docker.sh` behavior by:

```
# compute env hash from Dockerfile + pyproject.toml + uv.lock
HASH_INPUT=""
for f in Dockerfile pyproject.toml uv.lock; do
	if [[ -f "$f" ]]; then
		HASH_INPUT+=$(sha256sum "$f" | awk '{print $1}')
	else
		HASH_INPUT+="missing:$f"
	fi
done
ENV_HASH=$(printf "%s" "$HASH_INPUT" | sha256sum | cut -d' ' -f1)
IMAGE_NAME="classification-dev:${ENV_HASH}"

# build dev image if missing
if ! docker image inspect "$IMAGE_NAME" >/dev/null 2>&1; then
	docker build --progress=plain --target dev -t "$IMAGE_NAME" -f Dockerfile .
fi

# run tests in ephemeral container
docker run --rm "$IMAGE_NAME"
```

Save-image (reference)
----------------------
To save a built image for reviewers:

```
OUTDIR=artifacts
mkdir -p "$OUTDIR"
OUTFILE="$OUTDIR/${IMAGE_NAME//:/_}.tar"
docker save -o "$OUTFILE" "$IMAGE_NAME"
```

Notes: prefer programmatic invocation of `docker build`/`docker run` from
delegates and agents instead of relying on repo-local scripts.