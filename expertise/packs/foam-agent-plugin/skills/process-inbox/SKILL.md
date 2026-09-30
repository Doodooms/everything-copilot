---
name: process-inbox
description: Explicitly process Foam Inbox entries independently and verify durable notes before consuming entries.
---

# Process Inbox

Run only when the user explicitly asks to process Foam Inbox content. Never schedule, watch for, or ingest Inbox entries automatically.

## Procedure

1. Read the Inbox resource and identify its entries without changing it. Treat each entry as an independent unit; keep its exact source text and available provenance in working context.
2. Classify each entry. Delegate an idea to `materialize-idea` or a cited/source item to `capture-source` when appropriate. Ask the user when its meaning or destination is materially unclear; do not invent certainty.
3. For every destination note, use Foam MCP operations directly. Since `create_resource` has no initial-content argument, create the note, write its full content with `update_resource`, then read it back with `read_resource` and verify the durable content and provenance.
4. Only after that readback succeeds may the corresponding Inbox entry be consumed. Consume one verified entry at a time and preserve its source text/provenance in the durable note. If verification fails, leave that entry in the Inbox and report the failure.
5. Report processed, left untouched, ambiguous, and failed entries separately. Do not create Control objects, promote Intent, or imply that notes changed Control state.

## Boundaries

- Do not bulk-process unrelated entries or alter an entry before its destination is verified.
- Do not delete or consume entries merely because a destination was attempted.
- Keep ordinary Foam CRUD, query, and graph actions as direct MCP primitives.
