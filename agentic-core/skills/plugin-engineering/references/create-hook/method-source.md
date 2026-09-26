---
name: create-hook
description: "Create a hook (.json) to enforce policy or automate agent lifecycle events. Use when: blocking certain tool calls, injecting context at session start, running formatters after file edits, requiring approval before destructive operations."
user-invocable: false
disable-model-invocation: true
---

# Create Hook

Hooks enforce deterministic behavior at agent lifecycle events.
Unlike instructions (which guide the model), hooks run shell commands and can BLOCK operations.

## When to Use Hooks

- Block or gate specific tool calls (e.g., prevent `rm -rf`, require confirmation before `git push`)
- Inject context at session start (e.g., load project status, remind of active tasks)
- Run formatters automatically after file edits
- Log or audit tool calls for compliance

## Hooks vs Instructions

| | Instructions | Hooks |
|---|---|---|
| Mechanism | Model guidance (probabilistic) | Shell command (deterministic) |
| Can BLOCK | No | Yes |
| Use for | Style, conventions, preferences | Enforcement, automation, safety |

## Location

Hooks live in `.github/hooks/` as JSON files.

## Hook Schema

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "type": "command",
        "command": "python .github/hooks/check-command.py",
        "windows": "python .github\\hooks\\check-command.py",
        "timeout": 10
      }
    ]
  }
}
```

### Events

| Event | When it fires |
|-------|--------------|
| `PreToolUse` | Before a tool call executes -- can block it |
| `PostToolUse` | After a tool call completes |
| `SessionStart` | When a new chat session begins |
| `Stop` | When the agent finishes responding |

### Script behavior

- Exit code `0`: allow the operation to continue
- Exit code `1` (or non-zero): block the operation; stderr is shown to the model

## Extract from Conversation

Review the conversation. If the user has been expressing concerns like:
- "Don't run this command without asking"
- "Always check before doing X"
- "Inject this context at the start"
- "Run the formatter after edits"

Extract:
- What action should be gated or automated?
- Which event triggers it? (`PreToolUse`, `PostToolUse`, `SessionStart`)
- Does it need a companion shell script?

## Clarify if Needed

If the need is not clear, ask:
- What event triggers this hook?
- Should it block, warn, inject context, or automate?
- Does it apply to all tools or a specific one?

## Iterate

1. Draft the hook JSON in `.github/hooks/` and any companion script.
2. Test: trigger the relevant event and verify the hook fires.
3. Refine script exit codes and error messages for clarity.
4. Once finalized, summarize what the hook enforces and propose related hooks.

## Example: Block Dangerous Commands

`.github/hooks/safety.json`:
```json
{
  "hooks": {
    "PreToolUse": [
      {
        "type": "command",
        "command": "python .github/hooks/block-dangerous.py",
        "windows": "python .github\\hooks\\block-dangerous.py",
        "timeout": 10
      }
    ]
  }
}
```

`.github/hooks/scripts/block-dangerous.sh`:
```bash
#!/bin/bash
# $TOOL_INPUT contains the command being run
COMMAND="$1"
if echo "$COMMAND" | grep -qE 'rm\s+-rf|git push --force'; then
  echo "BLOCKED: Dangerous command requires manual confirmation." >&2
  exit 1
fi
exit 0
```

## Example: Inject Context at Session Start

`.github/hooks/session-context.json`:
```json
{
  "hooks": {
    "SessionStart": [
      {
        "type": "command",
        "command": "python .github/hooks/inject-context.py",
        "windows": "python .github\\hooks\\inject-context.py",
        "timeout": 10
      }
    ]
  }
}
```

## Reference

- Official docs: https://code.visualstudio.com/docs/copilot/customization/hooks
