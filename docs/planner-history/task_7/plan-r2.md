# Task 7 Implementation Plan (r2)

This append-only revision supersedes `plan-r1.md` because the approved specification advanced to r2 and the task ledger requires schema-valid `TASK-*` identifiers. It preserves r1's gates, boundaries, and lifecycle while incorporating the additional active repository-root instruction.

## Plan inputs

- Specification: `SPEC-PLUGIN-FACTORY-RENAME`, revision 2, in `docs/harness-history/task_7/manifest.json`.
- Architecture: `docs/architecture/CHECKOUT_INDEPENDENT_PROJECTIONS.md`; architecture phase remains not required.
- Assigned risk: **L2**, consumed without downgrade.
- Exact base: `af1fd1d849a1c42c9052a6ab929bca7d4a220ef7`.
- Isolated worktree: `/tmp/agentic-workflow-plugin-factory-rename`.
- Branch: `chore/plugin-factory-repository-rename`.
- Objective and scope: only active canonical product identity and future repository locator references, as defined by SPEC r2.

## Acceptance criteria mapping

Statements are copied verbatim from the r2 manifest; this plan does not redefine them.

- **AC-RENAME-IDENTITY** — “The root README names Plugin Factory, the active ChatGPT Work handoff locator is Doodooms/plugin-factory, the Agentic Core description identifies Plugin Factory as the enclosing product where applicable, and the direct plugin-authoring repository-root instruction uses Plugin Factory.”
- **AC-RENAME-PROVENANCE** — “Historical references to Doodooms/everything-copilot remain where they record prior repository identity or evidence; the Agentic Core package ID and directory remain unchanged.”
- **AC-RENAME-PROJECTION** — “The Antigravity projection generated from the canonical skill contains the intended future locator, and existing deterministic projection checks pass.”
- **AC-RENAME-VALIDATION** — “Focused Agentic Core source, checkout-independent projection, Antigravity projection, package validation, Ruff/format, and diff checks pass as applicable.”
- **AC-RENAME-LOCAL-COMMIT** — “The local branch begins at af1fd1d849a1c42c9052a6ab929bca7d4a220ef7 and contains a reviewed local commit; no push, PR, origin update, GitHub rename, or settings change occurs.”

## Dependency graph

```text
TASK-7-01 Active identity patch
       └── TASK-7-02 Focused validation
               └── TASK-7-03 Independent QA
                       └── TASK-7-04 Independent Reviewer
                               └── TASK-7-05 Orchestrator local commit
```

## Phases and tasks

### Phase 1 — Active identity patch

**TASK-7-01 — Update only the frozen active identity surfaces**

- Owner: Implementer. Orchestrator retains integration, gate, and lifecycle ownership.
- Inputs: SPEC r2, this plan, exact base/worktree/branch above.
- Allowed files, only where necessary:
  - `README.md`: identify the active product as Plugin Factory; retain Agentic Core as the internal package/layer.
  - `agentic-core/plugin.json`: update only the human-facing description, which currently calls the enclosing product “Agentic Workflow”; preserve package `name: agentic-core`, version, and metadata otherwise.
  - `agentic-core/skills/orchestration/workflows/chatgpt-work-handoff.md`: change the active future repository locator to `Doodooms/plugin-factory`.
  - `agentic-core/skills/plugin-engineering/references/create-plugin/references/plugin-contract.md`: change the direct authoring instruction “Agentic Workflow repository root” to “Plugin Factory repository root”; preserve the rest of the authoring contract.
  - `docs/architecture/CHECKOUT_INDEPENDENT_PROJECTIONS.md`: retain the old slug as a truthful historical observation and clarify its time/context rather than erasing or retrospectively rewriting that evidence.
  - `tests/test_agentic_core_sources.py`: add a focused assertion for the active direct authoring repository-root identity in the canonical source.
  - `tests/test_checkout_independent_projections.py`: assert the generated Antigravity skill artifact includes `Doodooms/plugin-factory`, validating projected observable content.
- Do not hand-edit generated projections. The canonical skill is projected through existing projector code; no checked-in generated artifact is anticipated.
- Dependencies: exact canonical base and isolated branch exist; SPEC r2 is ready.
- Acceptance mapping: AC-RENAME-IDENTITY, AC-RENAME-PROVENANCE, AC-RENAME-PROJECTION.
- Phase exit checks:
  1. Diff contains only necessary files from the allowed list.
  2. README, handoff, applicable plugin description, and authoring instruction state the approved active identity.
  3. Old repository identity remains where historically truthful; package ID and directory remain `agentic-core`.
  4. Tests assert current canonical-source and projected behavior, not implementation details.

### Phase 2 — Focused source, projection, package, and style validation

**TASK-7-02 — Run required focused checks and record outcomes**

- Owner: Implementer; Orchestrator records convergence evidence.
- Dependency: TASK-7-01 complete.
- Acceptance mapping: AC-RENAME-PROJECTION, AC-RENAME-VALIDATION.
- Run from the worktree root:
  - `uv run --no-project --with pytest --with pyyaml pytest -q tests/test_agentic_core_sources.py tests/test_checkout_independent_projections.py tests/test_antigravity_plugin_projection.py`
  - `uv run --no-project --with pyyaml python scripts/project_core_agents.py --check`
  - Validate the Agentic Core package manifest through its existing validator: `uv run --no-project --with pyyaml python -c "import json; from expertise.targets.validation import validate_plugin_manifest; validate_plugin_manifest(json.load(open('agentic-core/plugin.json', encoding='utf-8')))"`
  - `uv run --no-project --with ruff ruff check tests/test_agentic_core_sources.py tests/test_checkout_independent_projections.py`
  - `uv run --no-project --with ruff ruff format --check tests/test_agentic_core_sources.py tests/test_checkout_independent_projections.py`
  - `git diff --check`
- The three focused tests include deterministic Antigravity projection coverage. Do not require Google authentication for projection validity. Use `agy plugin validate` only if the implementation changes something requiring that external CLI check; report absence/auth limits precisely.
- Phase exit checks: all applicable checks pass; unavailable checks are reported as blocked/skipped with cause and are not counted as passes.

### Phase 3 — Independent QA

**TASK-7-03 — Adversarially check the exact validated diff**

- Owner: independent Quality Assurance agent, separate from Implementer.
- Dependency: TASK-7-02 passes and diff remains unchanged.
- Acceptance mapping: AC-RENAME-IDENTITY, AC-RENAME-PROVENANCE, AC-RENAME-PROJECTION, AC-RENAME-VALIDATION.
- Verify active-only identity changes; truthful historical old-slug provenance; stable `agentic-core` package name/directory; generated Antigravity workflow contains the new locator and is reproducible; no Copilot-centric product identity or out-of-scope changes.
- Exit: explicit QA status and evidence for each applicable criterion, with no material unresolved defect. Any fix returns to TASK-7-01 and requires affected validation and QA to repeat.

### Phase 4 — Independent Reviewer

**TASK-7-04 — Review traceability, scope, and gate evidence**

- Owner: independent Reviewer, separate from Implementer and QA.
- Dependency: TASK-7-03 passes on the exact diff.
- Acceptance mapping: AC-RENAME-IDENTITY, AC-RENAME-PROVENANCE, AC-RENAME-PROJECTION, AC-RENAME-VALIDATION, AC-RENAME-LOCAL-COMMIT.
- Verify spec/plan traceability, allowed file scope, validation and QA evidence, history/package preservation, deterministic projection, and no remote lifecycle operations.
- Exit: approval for the exact diff. Requested changes return through validation and QA before Reviewer approval is reconsidered.

### Phase 5 — Reviewed local commit and stop

**TASK-7-05 — Commit locally after all required gates pass**

- Owner: Orchestrator only.
- Dependencies: TASK-7-02 validation, TASK-7-03 QA pass, TASK-7-04 Reviewer approval, all on unchanged content.
- Acceptance mapping: AC-RENAME-LOCAL-COMMIT.
- Stage only reviewed task-owned implementation files and create one focused Conventional Commit on `chore/plugin-factory-repository-rename`. Verify the commit's parent is the exact canonical base and report the local SHA/tree.
- Exit: reviewed local commit exists. Nothing is pushed, no PR is opened, `origin` and GitHub settings/rulesets remain untouched, and the repository is not renamed. Stop for the human rename checkpoint.

## Exclusions

- No GitHub repository rename, push, PR, origin URL update, GitHub settings/ruleset change, or ref cleanup.
- No Substrat changes; no mass rename of `agentic-core` or `agentic-workflow`.
- No rewriting historical task/research/PR/archive evidence, immutable commit metadata, or published SHAs.
- No broad search-and-replace, generated-file hand edits, or unrelated cleanup.

## Risks, assumptions, and next owner

- Assigned risk remains **L2**: identity is updated across canonical metadata, skill instructions, projected behavior, tests, and historical documentation. Local changes are reversible before publication.
- Projection evidence must inspect generated Antigravity skill content, not only the source Markdown.
- Preserve all worktree state and inspect status before implementation/staging; task tracking files are not implementation scope.
- No native todo interface is exposed; manifest/history are the task record and are not modified by this plan.
- Suggested next owner: Implementer for TASK-7-01.

`changed_files: [docs/planner-history/task_7/plan-r2.md]`

`commit_shas: []`
