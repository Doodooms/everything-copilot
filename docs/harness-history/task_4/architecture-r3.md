# Architecture decision — task_4, revision 3

- Specification: `SPEC-CORE-ENHANCEMENTS@4`.
- Risk: `L2`.
- Status: `ready`.

## Context

The task improves portable agent workflows, context and quota decisions, cross-harness messages, MCP authoring guidance, and durable task tracking. Harness session state, provider quotas, credentials, and tool execution remain controlled by each host. The current `agentic-core` plugin supplies shared instructions, host adapters, and deterministic local validators.

## Decision — ADR-CORE1

Keep the canonical local plugin and thin Copilot/Codex adapters. Keep machine-readable exchange contracts in versioned JSON Schema and validate them at send, receive, and persistence boundaries. Use local scripts for checks that require repository state, such as resolving a Git commit or verifying an artifact digest. Keep semantic SDD validation as a companion check over the structured manifest extension. Require a fresh host-reported destination budget before a cross-harness CLI call.

The source file `todos/agents/agent_architect_ideas.md` is a repository-review brief, not a set of implementation proposals. Its review questions were applied to the bounded plugin changes here; they do not authorize changes in the separate harness evaluation.

## Alternatives considered

- **Python-only Pydantic models:** could add local typing but would not replace a language-neutral exchange contract; generating or maintaining both would add drift risk.
- **A central runtime or tool-call gateway:** might enforce host-independent rules, but would duplicate host permissions and introduce deployment, credential, and maintenance surfaces without a demonstrated requirement.
- **Current plugin plus local corrections:** preserves portability and existing owners while repairing demonstrated contract and workflow defects. Selected.

## Consequences

- `validate_exchange.py` resolves normal commits and merge commits (against the first parent), verifies commit path claims and artifact digests, and validates event structures before the manifest can advance.
- `validate_sdd_state.py` checks IDs, traceability, gate state, and convergence on the same canonical manifest. The outer manifest schema accepts the optional SDD extension while preserving task_3's current manifest shapes.
- Live quotas and session state remain observations from the owning CLI. Unknown, exhausted, or stale destination budget blocks cross-harness contact.
- No external runtime, credentials, or product dependency is added. The host's GitHub App environment remains separately configured.
