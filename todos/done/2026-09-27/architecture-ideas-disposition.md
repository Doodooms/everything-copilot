# Architecture review disposition

Reviewed input: [`agent_architect_ideas.md`](./agent_architect_ideas.md), 2026-09-27.

## What the input contains

The source is a review brief asking for an independent, repository-wide architecture, security, and code review. It defines review questions and a required report format; it does not contain prioritized architecture proposals. This task used it as review-method input and did not treat the brief as a separate instruction to audit unrelated repository areas.

## Bounded review scope

The review covered task_4's specification and history, the `agentic-core` manifest and relevant skills, the handoff schemas and validator, the Orchestrator persistence helper, and the Copilot/Codex communication procedures. `task_3` / `harness_factory` remained outside scope and unchanged.

The plugin currently keeps canonical agents, skills, and MCP guidance in one local package, with host-specific adapters and explicit procedures. Machine-readable handoffs use portable JSON Schema contracts; local Python scripts validate repository-specific claims and persist orchestration state. Host session identity, quota, and authentication remain owned by each harness.

## Architecture assessment

**Adjust the current architecture.** The plugin and thin host-adapter boundary fit the task: they keep shared expertise portable while leaving live session state and credentials with their hosts. Replacing this with a central runtime or tool gateway would add deployment, permission, and maintenance surfaces without a demonstrated enforcement need. Pydantic could improve Python-local typing, but it would not replace the language-neutral exchange contract and would introduce a second source or generation step. The existing schemas plus local validator are the smaller fit. The optional SDD fields now share the canonical manifest envelope, and the current `task_3` manifest passes that outer schema without edits to its source or ledger.

The review found bounded contract defects that did merit fixes:

- Merge commit path verification now compares the merge result with its first parent, with that policy documented for handoff producers and receivers.
- An event marked `commit_status: created` must include at least one `commit_shas` entry.
- `write_orchestration_record` now builds and validates its complete event before persisting the manifest, so malformed specialist returns cannot advance the manifest.
- Direct Copilot/Codex communication workflows now require a fresh destination-harness budget check before CLI contact.

These corrections stay within existing package boundaries. The formal decision and SDD boundary are recorded in [architecture-r3](../../../docs/harness-history/task_4/architecture-r3.md). No performance-sensitive service or external dependency was introduced.

## Uncertainty and follow-up

Provider quota and session telemetry are host-reported and time-sensitive. Copilot's monthly quota was exhausted during the attempted interaction, so a successful model response could not be observed. The GitHub MCP server also needs host-provided GitHub App environment variables that were absent in this shell; credentials were neither inspected nor changed. Focused local checks passed, but the host could not provide a custom independent QA agent. These constraints and the exact resume conditions are in the [task follow-ups](../../backlog/2026-09-27/agentic-core-enhancements-followups.md).

No actionable architecture proposal could be extracted from the supplied review brief itself. The source and this disposition are preserved together in `todos/done/2026-09-27/`.
