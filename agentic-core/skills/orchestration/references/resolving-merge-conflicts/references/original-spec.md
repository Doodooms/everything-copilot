# Original Specification

## Raw intent

Provide a careful procedure for resolving conflicts in an already active merge or rebase by understanding both changes, preserving compatible intent, and validating the result.

## Normalized requirements

- Confirm the active Git operation and exact conflicted files.
- Inspect both sides, their context, and approved behavior before editing.
- Escalate unresolved semantic choices instead of guessing.
- Validate resolved content and return a bounded handoff.

## Constraints and resolved decisions

- The supplied Codex instructions to always resolve, never abort, stage everything, and commit were rejected as unsafe and incompatible with Orchestrator-owned Git lifecycle.
- This skill resolves file content only; it does not begin, abort, stage, commit, or continue a merge/rebase.
- Date: 2026-09-24.
