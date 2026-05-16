---
name: create-prompt
description: 'Create a reusable prompt file (.prompt.md) for a common task.'
user-invocable: false
disable-model-invocation: true
---

Related skill: `create-agent` for agent work. Do not load stale `agent-customization` guidance here; this skill stays scoped to `.prompt.md` authoring.

Guide the user to create a `.prompt.md`.

## Extract from Conversation
First, review the conversation history. If the user has been working on a repeatable task pattern (e.g., explaining code, generating tests, refactoring), generalize that into a reusable prompt. Extract:
- The core task being performed repeatedly
- Any implicit inputs (selected code, file type, context)
- The desired output format or style

## Clarify if Needed
If no clear pattern emerges from the conversation, clarify:
- What task should this prompt help with?
- Should it take arguments or use fixed context?
- Workspace-scoped or personal?

## Iterate
1. Draft the prompt and save it.
2. Identify the most ambiguous or weak parts and ask about those.
3. Once finalized, summarize what the prompt does, suggest example invocations, and propose related customizations to create next.

Remember to follow the prompt authoring template and principles for reusable `.prompt.md` files, not agent-specific guidance.
