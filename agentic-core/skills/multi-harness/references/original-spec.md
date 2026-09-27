# Multi-harness skill original specification

## Objective

Create a harness-agnostic `multi-harness` skill for safe, bounded communication between GitHub Copilot CLI and Codex CLI, leaving room for another harness later.

## Requirements

- Package the skill in `agentic-core/skills/multi-harness/`.
- Provide exactly two immediate workflows: `workflows/copilot.md` and `workflows/codex.md`.
- The Copilot workflow MUST read the Codex workflow before communicating with Codex.
- The Codex workflow MUST read the Copilot workflow before communicating with Copilot.
- Document only locally verified CLI capabilities; distinguish queue acknowledgement from a consumed message or reply.
- Use exact session identity, concise deltas, and explicit read-only/no-edit instructions for status requests.
- Do not resume or interrupt an existing session unless the user explicitly authorizes it.
- Do not assume agents share private prompts, memory, or live status; verify through the receiving harness or report uncertainty.
- Add the skill to the Core plugin and make the Orchestrator use it for cross-harness coordination.
- Run one bounded Copilot CLI invocation of the Copilot workflow and one bounded Codex CLI interaction/read of the paired workflow.

## Constraints and non-goals

- Do not add a third harness implementation now.
- Do not create recursive automatic Copilot↔Codex calls.
- Do not inspect credentials or perform repository writes through a communication test.
- Preserve the existing role and repository-lifecycle boundaries.

## Amendment A1 — context and resource workflows (2026-09-27)

The original two communication workflows remain paired and retain their read-before-contact rule. The skill now also owns two separate, non-contact procedures: `workflows/smart-compact.md` for host-reported context observations and phase-safe compaction, and `workflows/harness-distribution.md` for observed provider budgets and work placement. This amendment supersedes the original “exactly two immediate workflows” packaging constraint: current routing exposes four immediate workflows, while only the Copilot/Codex pair may send cross-harness messages. Neither new procedure adds a timer, quota API, account switch, or automatic session contact.
