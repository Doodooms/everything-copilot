---
kind: idea
status: intake
disposition: pending
derived_work: []
---

# Chat-led multi-harness Control-Plane and remote development workflow

## Goal

Converge toward a development workflow where the human primarily communicates with Chat.

The human should not need to manually transfer prompts, reports, commit SHAs or task context between:

- Chat;
- Work;
- Codex;
- Copilot;
- future harnesses;
- multiple sessions of the same harness.

Target experience:

```text
Human
  │
  ▼
Chat
decision / architecture / checkpoints
  │
  ▼
Control-Plane
durable tasks / attempts / events / artifacts
  │
  ├── Work
  ├── Codex
  ├── Copilot
  └── future harnesses
```

The harnesses remain replaceable execution surfaces.

## Desired daily workflow

A useful target scenario is remote asynchronous development from a phone.

Example:

```text
morning
Human → Chat
"continue project X with the approved next task"

Chat
→ creates/updates durable task
→ dispatches Work
→ Work orchestrates appropriate execution backend(s)

during the day
Work / Codex
→ execute
→ validate
→ commit
→ publish
→ record evidence

lunch
Human → Chat
→ receives concise checkpoint
→ approves/reorients if required

evening
Human → Chat
→ reviews accumulated results
→ architecture checkpoint
→ selects next work
```

The user should not have to operate individual harness sessions except for diagnostics or exceptional cases.

## Human-facing handoff format

Routine execution reports should be very small.

For completed modifying work, Chat generally needs:

```text
status
task ID
commit SHA(s)
changed files
validation summary
PR / artifact reference
blockers or decisions requiring human input
```

Full transcripts should remain available as provenance but should not be copied into every handoff.

Desired normal report:

```text
TASK-123: READY

commits:
- abcdef123...

changed:
- src/...
- tests/...

validation:
- focused tests: PASS
- QA: PASS

PR:
- #42

decision_required:
- none
```

Chat can inspect the referenced commit/PR when deeper understanding is required.

## Durable coordination

Do not use conversation history as the coordination mechanism.

The Control-Plane should own durable state such as:

```text
Run
Task
Attempt
Event
Artifact
Lease
Provenance
```

A Task is logical.

An Attempt is one execution:

```text
TASK-42
  ├── ATTEMPT-1 → Work cloud
  ├── ATTEMPT-2 → Codex local
  └── ATTEMPT-3 → future backend
```

Harness/backend belongs to the Attempt, not the Task.

Sessions and threads are temporary implementation details.

## Shared ticket/task interface

A useful conceptual interface is a ticket-like protocol shared by Chat and Work.

This does not necessarily mean GitHub Issues.

The minimum shared object could contain:

```text
task_id
specification_ref
state
priority
dependencies
approved_scope
required_capabilities
attempts
artifacts
commit_shas
validation_evidence
blockers
next_action
human_checkpoint
```

Chat creates/changes intent.

Work claims executable tasks.

Workers publish Attempt results.

Chat consumes compact durable results.

This removes manual copy/paste.

## Communication model

Prefer:

```text
Chat
→ durable task/event

Work
→ reads task
→ executes/orchestrates
→ writes attempt/events/artifacts

Chat
→ observes state
→ makes next decision
```

over:

```text
Chat session
→ manually copied prompt
→ Work session
→ manually copied report
→ Chat
```

Direct harness-to-harness communication may still exist, but durable Control-Plane state should remain authoritative.

## Git as durable modification provenance

For repository modifications:

```text
working tree
= temporary execution state

focused commit SHA
= durable modification handoff

PR
= collaboration/review surface
```

A modifying task should not report successful delivery with only uncommitted files.

Normal lifecycle:

```text
approved task
→ isolated branch/worktree
→ implementation
→ validation
→ focused immutable commit
→ publication
→ PR
→ compact handoff to Chat
```

Chat should usually need only SHA + changed files + evidence summary to reconstruct the rest.

## Work must follow Agentic Core

Work currently does not consistently follow Agentic Core and repository lifecycle without explicit prompting.

Long-term requirement:

> Harness behavior should be installed/projected from canonical Agentic Core policy rather than relying on the human to restate workflow rules.

Work should automatically discover/use:

- role boundaries;
- applicable skills;
- Git lifecycle;
- output contracts;
- canonical task state;
- validation requirements.

The user should not repeatedly instruct Work to commit, return SHAs, or use the correct specialist sequence.

## GitHub connector policy

Chat currently has a native GitHub connector and does not yet have the same plugin access as Work.

For now:

```text
Chat
→ native GitHub connector permitted

Work
→ native hosted GitHub connector should not be part of the canonical execution path
→ use the project-controlled MCP Gateway / GitHub App path
```

Reason:

- avoid two GitHub identities/capability paths;
- prevent Work from accidentally using a hosted connector instead of the project-controlled GitHub App;
- make runtime provenance explicit;
- validate the architecture that future harnesses can share.

This policy can be revisited if Chat later gains the same plugin/Gateway capabilities.

## Local and cloud execution

The target is not necessarily identical physical capabilities everywhere.

The target is a common capability model.

Example:

```text
Task requires:
- workspace.write
- shell.execute
- git.commit

Work cloud:
workspace.write(local-machine) = unavailable

Codex local:
workspace.write = observed
shell.execute = observed
git.commit = observed

router:
→ create Attempt on Codex local
```

Cloud and local backends should expose capabilities through a common vocabulary.

Routing should use observed capabilities and constraints rather than hardcoded provider names.

## Phone-first remote development

The phone should function as a control surface, not as the compute node.

Near-term mode:

```text
phone
→ Chat
→ Work cloud
→ cloud-accessible services
```

Later:

```text
phone
→ Chat
→ Control-Plane
   ├── Work cloud
   ├── Codex cloud
   └── Codex/local execution node
```

A local execution node may be reachable only when the home machine/network is available.

Therefore the scheduler must treat local execution as an optional backend, not an assumed dependency.

If the local Gateway/machine is unreachable:

```text
capability unavailable
```

not silent fallback or false PASS.

## Connectivity limitation

Current local infrastructure may be unavailable while the user's computer has no independent network connection.

This means remote daytime work initially needs to prefer cloud-capable execution.

Potential future options to investigate:

- persistent home/desktop network connectivity;
- secure remote execution relay;
- cloud-hosted execution nodes;
- Codex remote-control capabilities;
- outbound tunnel established by the local machine;
- hybrid scheduler where local-only tasks wait while cloud-safe tasks continue.

Do not weaken security merely to make a local machine reachable.

## Orchestration of Codex by Work

Experimentally validate what Work can actually orchestrate.

Distinguish:

```text
documented
observed
inferred
blocked
untested
```

Questions:

- Can Work launch Codex executions reliably?
- Can it preserve task/attempt identity?
- Can it consume structured results?
- Can it resume or reconnect?
- Can it cancel?
- What survives Work session loss?
- Can Work choose between Codex local/cloud backends?
- Which capabilities are available from mobile-initiated Work?
- How are leases and duplicate attempts prevented?

Do not make session memory authoritative.

## Future user experience

Ideal endpoint:

```text
Human:
"Implement the next approved slice of project X."

Chat:
→ checks canonical project state
→ decides whether checkpoint is needed
→ creates task

Control-Plane:
→ chooses capable backend

Work:
→ supervises execution

Codex:
→ implements

GitHub App:
→ publishes immutable commits / PR

Chat:
→ later reports:
  "Task complete.
   SHA ...
   PR ...
   tests ...
   one decision remains."
```

No manual prompt relay should be required.

## Non-goals

Do not prematurely implement:

- a generic distributed scheduler;
- automatic architecture decisions;
- autonomous merging;
- hidden task creation from raw TODO ideas;
- uncontrolled background self-modification;
- harness memory as durable state.

Build the smallest real cross-harness path first, observe it, then generalize.