# TASK-5-03A preflight QA findings

> **Historical audit of an erroneous intermediate tree; not valid QA evidence for the nested workflow subskills.** The 57 peer packages audited here were generated from a mistaken topology and have been moved out of the plugin tree. Their package-level failures and the validator diagnosis do not establish defects in the 57 original `workflows/*.md` files. Re-audit those source files against the workflow template and workflow validator under architecture r6 and plan r10.

- QA run: `QA-RUN-TASK-5-03A-20260927-01`.
- This is the Orchestrator's durable summary of the read-only QA handoff; the agent made no changes.
- Verdict: **fail**. The 57-package inventory passes, but the conversion is not ready to advance.
- The audit was conducted against `main` at base `5c6dcd401e9a0d115e79c19f02de96ffed694686`. Local `master` is its ancestor, not a conflicting branch.

## Inventory and content checks

- Source map rows: 58, consisting of 57 existing methods and one future `TASK-5-06` method. The existing IDs are unique.
- Existing method target packages: 57/57 present. `TASK-5-06` target is absent as expected.
- Direct-child `SKILL.md` packages: 68 total (57 method skills plus 11 domain skills).
- Every method file has a frontmatter delimiter, matching `name`, and non-empty `description`.
- A mechanical source/body comparison found 39 packages with sequence similarity at least 0.93; 18 were below that threshold or had line-count differences. This is triage, not a semantic-equivalence verdict; review those 18 against their source methods.
- The existing validator returned exit 3 for all 57. Its **nested workflow placement assumptions** are obsolete for these direct-child method skills. The current skill-authoring template still defines the required skill-level structure; each peer `SKILL.md` must meet that same structure while keeping the method procedure directly in its `<workflow>` section. Do not move methods back beneath `workflows/`.
- No repository test suite or installed-host invocation was run.

## Broken or mis-scoped package references

The scan found 25 unresolved package-relative links in 12 skills:

| Skill | Line(s) and unresolved target(s) |
|---|---|
| `agent-authoring` | 44: `../references/create-agent/scripts/agent_lint_core.py` |
| `agent-validation` | 23: `../references/create-agent/references/validation.md`; 24: `../references/create-agent/scripts/agent_lint_core.py`; 28: `../references/create-agent/references/final-checklist.md` |
| `plugin-creation` | 22: `../references/create-plugin/references/plugin-contract.md`; 32: `../references/create-plugin/references/skill-composition.md` |
| `plugin-update` | 15: `../references/create-plugin/references/plugin-contract.md`; 21: `../references/create-plugin/references/skill-composition.md` |
| `skill-authoring` | 76: `../references/create-skill/scripts/validate.py` |
| `skill-maintenance` | 30: `../references/create-skill/references/skill-composition.md`; 34: `../references/create-skill/scripts/validate.py`, `../references/create-skill/references/validation.md`; 36: `../references/create-skill/references/final-checklist.md` |
| `test-design` | 18: `../references/testing/references/test-oracles.md`, `../references/testing/references/equivalence-boundaries.md`; 23: `../references/testing/references/test-levels.md`; 24: `../references/testing/references/test-doubles.md` |
| `test-quality-review` | 17: `../references/testing/references/test-oracles.md`; 22: `../references/testing/references/equivalence-boundaries.md`, `../references/testing/references/test-doubles.md` |
| `algorithm-selection` | 19: `../references/implementation-design/references/data-structures.md` |
| `concurrency-design` | 20: `../references/implementation-design/references/state-machines.md` |
| `representation-selection` | 19: `../references/implementation-design/references/data-structures.md` |
| `state-modeling` | 18: `../references/implementation-design/references/state-machines.md` |

The source files still exist beneath the original domain references. There are 32 unresolved `support` declarations for 16 distinct shared source files. The shared-resource ownership/materialization rule needs an explicit Orchestrator/Architect decision before rewriting these paths.

`create-mcp/SKILL.md` also invokes its local validator using the source-domain path `agentic-core/skills/plugin-engineering/./references/create-mcp/scripts/validate_mcp.sh`, while its linked validator is in the method package. Correct the command to the actual package-local path.

## Host-specific body instructions

There are 150 `#tool:`/`#file:` markers across 36 packages. No host runtime was invoked to prove those markers work. The specifically host-qualified `#tool:vscode/askQuestions` appears in `create-mcp`; the other markers also require a Codex/Copilot compatibility decision rather than blind deletion.

Affected methods: `architecture-design`, `token-optimization`, `codex`, `copilot`, `delivery-operations`, `documentation-sync`, `install-agent-plugin`, `verification-loop`, `commit-message`, `implementation-planning`, `orchestrate`, `resolving-merge-conflicts`, `create-mcp`, `optimize-skill`, `adversarial-testing`, `code-review`, `failure-analysis`, `language-review`, `code-exploration`, `deep-research`, `github-evidence-research`, `paper-research`, `versioned-documentation-research`, `database-audit`, `security-review`, `security-testing`, `algorithm-selection`, `performance-profiling`, `prototype`, `refactor-cleanup`, and `tdd`.

## Procedure and relationship defects

- `codex/SKILL.md`'s body instructs reading `codex` itself, while its `read` edge targets `copilot`.
- `copilot/SKILL.md`'s body instructs reading `copilot` itself, while its `read` edge targets `codex`.
- Both bodies malformed the `harness-distribution` reference as inline code.
- `token-optimization` composes `smart-compact`, and `smart-compact` composes `token-optimization`. This is a prohibited `compose` cycle under ADR-ACN-004 and plan r7.
- Relationship tables contain 151 edges: 21 `compose`, 3 `read`, 127 `support`; no `route` edges, as expected before TASK-5-03B.
- `create-mcp` and `create-mcp-rust` each contain a complete procedure, and `create-mcp` declares the conditional Rust composition. `create-mcp` still contains unverified host directives and a wrong validator command. Step numbering jumps from 1 to 3 in both source and target; this is inherited source content.

## Support-file inventory

- 95 resolved `support` edges point to 95 package-local files, with 95 distinct content hashes.
- 32 unresolved declarations identify 16 distinct common source files spanning agent authoring/validation, plugin creation/update, skill authoring/maintenance, testing, and implementation-design methods.
- The existing ADR-ACN-003 selects one exact shared MCP reference exception. It does not decide these additional shared resources. Do not expand the allowlist or copy shared content until that policy is reconciled.

## Validation method and limits

- The QA agent used read-only inventory, frontmatter/body comparison, relative-link scanning, relationship/support target scanning, and the existing validator across all 57 methods.
- `.venv/bin/python` was used with `PYTHONDONTWRITEBYTECODE=1`. `uv run --no-sync python -` could not start because it could not acquire its lock/create a temporary file on the read-only filesystem.
- No runtime host invocation, full semantic sentence-by-sentence review of all procedures, or test suite was run. The supplied handoff named `SPEC-AGENTIC-CORE-NORMALIZATION@1`, but the canonical specification document was not included in its packet.
- Next owners: Architect for the shared-support/skill-contract boundary; Implementer for content, links, host directives, pair reads, and cycle fixes; Reviewer retains final acceptance.
