# Task 7 Implementation Plan (r1)

## Plan inputs

- Specification: `SPEC-PLUGIN-FACTORY-RENAME`, revision 1, from `docs/harness-history/task_7/manifest.json`.
- Architecture: `docs/architecture/CHECKOUT_INDEPENDENT_PROJECTIONS.md`; no new architecture decision is required by the manifest.
- Assigned risk: **L2** (consume as assigned; do not downgrade).
- Base: `af1fd1d849a1c42c9052a6ab929bca7d4a220ef7`.
- Isolated worktree: `/tmp/agentic-workflow-plugin-factory-rename`.
- Branch: `chore/plugin-factory-repository-rename`.
- Scope: active canonical product identity and future repository locator only. The exact frozen constraints and non-goals remain in the specification.

## Acceptance criteria mapping

Statements below are copied verbatim from the task manifest; this plan does not change them.

- **AC-RENAME-IDENTITY** — “The root README names Plugin Factory, the active ChatGPT Work handoff locator is Doodooms/plugin-factory, and the Agentic Core description identifies Plugin Factory as the enclosing product where applicable.”
- **AC-RENAME-PROVENANCE** — “Historical references to Doodooms/everything-copilot remain where they record prior repository identity or evidence; the Agentic Core package ID and directory remain unchanged.”
- **AC-RENAME-PROJECTION** — “The Antigravity projection generated from the canonical skill contains the intended future locator, and existing deterministic projection checks pass.”
- **AC-RENAME-VALIDATION** — “Focused Agentic Core source, checkout-independent projection, Antigravity projection, package validation, Ruff/format, and diff checks pass as applicable.”
- **AC-RENAME-LOCAL-COMMIT** — “The local branch begins at af1fd1d849a1c42c9052a6ab929bca7d4a220ef7 and contains a reviewed local commit; no push, PR, origin update, GitHub rename, or settings change occurs.”

## Dependency graph and phases

```text
TASK-7.1 Active identity patch
       └── TASK-7.2 Focused validation
               └── TASK-7.3 Independent QA
                       └── TASK-7.4 Independent Reviewer
                               └── TASK-7.5 Local commit by Orchestrator
```

### Phase 1 — Active identity patch

**TASK-7.1 — Implement the frozen identity update**

- Owner: Implementer; Orchestrator owns integration and lifecycle decisions.
- Inputs: SPEC r1, this plan, the exact base/worktree/branch above.
- Allowed source files, only as applicable:
  - `README.md` — update the active product-facing title/description to Plugin Factory; retain Agentic Core as the packaged internal layer.
  - `agentic-core/plugin.json` — update only the human-facing description, since it currently calls the enclosing product “Agentic Workflow”; preserve `name: agentic-core`, version, directory, and other unrelated metadata.
  - `agentic-core/skills/orchestration/workflows/chatgpt-work-handoff.md` — change the future handoff locator to `Doodooms/plugin-factory`.
  - `docs/architecture/CHECKOUT_INDEPENDENT_PROJECTIONS.md` — retain the old slug as a truthful historical observation and clarify its time/context; do not silently rewrite the study as though the old locator had never existed.
  - `tests/test_checkout_independent_projections.py` — add a behavioral assertion against the generated Antigravity skill artifact proving it includes `Doodooms/plugin-factory` when projected from the canonical skill.
- Do not hand-edit generated projections. The existing projector is the generation path; no checked-in generated artifact is anticipated from current repository layout.
- Dependencies: exact canonical base and assigned isolated branch are present; manifest spec status is ready.
- Product acceptance mapping: AC-RENAME-IDENTITY, AC-RENAME-PROVENANCE, AC-RENAME-PROJECTION.
- Phase exit checks:
  1. Diff is limited to the listed files that are necessary.
  2. Active README, handoff, and applicable package description name the intended identity/locator.
  3. Historical provenance remains understandable and accurate; package ID/directory remain `agentic-core`.
  4. Projection regression assertion checks observable projected content, not projector internals.

### Phase 2 — Focused validation

**TASK-7.2 — Validate sources, projections, packaging metadata, and style**

- Owner: Implementer; report exact commands and outcomes to Orchestrator.
- Dependencies: TASK-7.1 diff complete.
- Product acceptance mapping: AC-RENAME-PROJECTION, AC-RENAME-VALIDATION.
- Validation commands from the worktree root:
  - `uv run --no-project --with pytest --with pyyaml pytest -q tests/test_agentic_core_sources.py tests/test_checkout_independent_projections.py tests/test_antigravity_plugin_projection.py`
  - `uv run --no-project --with pyyaml python scripts/project_core_agents.py --check`
  - `python -m json.tool agentic-core/plugin.json`
  - `uv run --no-project --with ruff ruff check tests/test_checkout_independent_projections.py`
  - `uv run --no-project --with ruff ruff format --check tests/test_checkout_independent_projections.py`
  - `git diff --check`
- Notes: the checkout-independent projection test exercises reproducible Antigravity generation from a copied plugin; `agy plugin validate` is not required by ACs for this text-only locator change. If implementation changes the plugin description in a way that requires a distinct manifest schema check, use the repository's available plugin validator and report it; do not infer a pass from JSON syntax alone.
- Phase exit checks: every applicable listed command passes; any unavailable command or external limitation is explicitly reported, and no external authentication is treated as a projection failure/success.

### Phase 3 — Independent QA

**TASK-7.3 — Falsify the implementation against the frozen acceptance criteria**

- Owner: independent Quality Assurance agent, not the Implementer.
- Dependencies: TASK-7.2 passes and the tested diff is unchanged.
- Product acceptance mapping: AC-RENAME-IDENTITY, AC-RENAME-PROVENANCE, AC-RENAME-PROJECTION, AC-RENAME-VALIDATION.
- QA checks: inspect the complete diff and generated Antigravity skill; verify only active identity moved, old name remains where historically truthful, package identity remains `agentic-core`, no Copilot-centric identity was introduced, and projection output can be regenerated deterministically using the focused tests.
- Phase exit checks: QA returns an explicit result with evidence for each applicable criterion and no unresolved material defect. If QA requests a change, return to TASK-7.1, rerun affected validation, and repeat QA on the new diff.

### Phase 4 — Independent Reviewer

**TASK-7.4 — Review scope, compatibility, and evidence**

- Owner: independent Reviewer agent, separate from Implementer and QA.
- Dependencies: TASK-7.3 QA pass on the exact proposed diff.
- Product acceptance mapping: AC-RENAME-IDENTITY, AC-RENAME-PROVENANCE, AC-RENAME-PROJECTION, AC-RENAME-VALIDATION, AC-RENAME-LOCAL-COMMIT.
- Reviewer checks: verify spec/plan traceability, file scope, evidence, preserved historical provenance and package identity, reproducibility, and absence of remote mutations or scope expansion.
- Phase exit checks: Reviewer approves the exact diff and confirms required gates are current. If changes are requested, return through focused validation and QA before review is repeated.

### Phase 5 — Local commit and stop

**TASK-7.5 — Create local reviewed checkpoint**

- Owner: Orchestrator only.
- Dependencies: focused validation pass, independent QA pass, and independent Reviewer approval on the unchanged diff.
- Product acceptance mapping: AC-RENAME-LOCAL-COMMIT.
- Action: stage only the reviewed task-owned files and create one focused local Conventional Commit on `chore/plugin-factory-repository-rename`; verify commit parent is the exact canonical base and worktree status afterward.
- Phase exit checks: local commit exists and records the reviewed content; no push, PR, origin update, GitHub rename, settings/ruleset change, or unrelated file is included. Stop and return the pre-rename checkpoint for the human.

## Explicit exclusions

- No mass rename of `agentic-core` or `agentic-workflow`.
- No rewrite of historical task, research, PR, archive, commit, or published-SHA evidence.
- No Substrat change, repository rename, remote publication, PR, origin update, GitHub setting/ruleset change, or ref cleanup.
- No broad search-and-replace or unrelated cleanup.

## Risks, reversibility, and assumptions

- Risk remains the assigned **L2** because canonical identity and a generated projection contract span source/docs/tests. The patch is locally reversible before publication.
- The existing Antigravity projector projects workflow text from the canonical skill; the regression assertion must target the projected artifact so a source-only assertion cannot mask a broken projection.
- Assume the exact isolated branch/worktree supplied by the Orchestrator remains clean apart from this task's own untracked manifest/history artifacts. Preserve all other state and inspect `git status` before editing/staging.
- There is no exposed native todo interface in this session; the task manifest and task history remain the progress record. This plan does not update either.
- Suggested next owner: Implementer for TASK-7.1.

`changed_files: [docs/planner-history/task_7/plan-r1.md]`

`commit_shas: []`
