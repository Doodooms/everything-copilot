---
name: troubleshoot
description: "Investigate unexpected chat agent behavior by analyzing direct debug logs in JSONL files. Use when users ask why something happened, why a request was slow, why tools or subagents were used or skipped, or why instructions/skills/agents did not load."
user-invocable: false
---

# Troubleshoot

## Purpose

Investigates and explains unexpected chat agent behavior using direct debug log files.

Use for questions like:
- Why did this request take so long?
- Why was a tool or subagent called?
- Why did a skill/instruction/agent file not load?
- Why was a tool call blocked or failed?
- Why did the model not follow expectations?

Base all conclusions on evidence from logs. Do not guess.

## Data Source

Target session log directory: `{{VSCODE_TARGET_SESSION_LOG}}`

Log files written by Copilot Chat:

```
debug-logs/<sessionId>/
  main.jsonl                              -- always start here; primary conversation log
  models.json                             -- (optional) available models at session start
  system_prompt_0.json                    -- (optional) full system prompt sent to model
  system_prompt_1.json                    -- (optional) written if model changes mid-session
  tools_0.json                            -- (optional) tool definitions sent to model
  runSubagent-<agentName>-<uuid>.jsonl    -- (optional) subagent tool calls and LLM requests
  searchSubagent-<uuid>.jsonl             -- (optional) search subagent work
```

Always read `main.jsonl` first. Child files appear only when those operations occurred.
`main.jsonl` contains `child_session_ref` entries that link to each child file by name.

When investigating what the model was told, read the `system_prompt_*.json` file referenced
by a `system_prompt_ref` entry in `main.jsonl`. It contains the full untruncated prompt.

## Event Type Reference

Each line is a JSON object. Common fields: `ts` (epoch ms), `dur` (duration ms),
`type`, `name`, `spanId`, `parentSpanId`, `status` (ok|error), `attrs`.

### discovery -- customization file loading

```jsonl
{"ts":...,"type":"discovery","name":"Load Skills","status":"ok","attrs":{"details":"Resolved 6 skills | loaded: [tdd-workflow, security-review] | skipped: testing2 (name-mismatch)"}}
```

Key attrs: `details` shows folder paths, loaded items, and skip reasons with exact cause.

### tool_call -- tool invocation

```jsonl
{"ts":...,"type":"tool_call","name":"run_in_terminal","status":"error","attrs":{"args":"...","result":"ERROR: ...","error":"..."}}
```

Key attrs: `args` (tool input), `result` (output or error text), `error` (if status=error).

### llm_request -- model round-trip

```jsonl
{"ts":...,"type":"llm_request","name":"chat:gpt-4o","status":"ok","attrs":{"model":"gpt-4o","inputTokens":15025,"outputTokens":126,"ttft":1987,"systemPromptFile":"system_prompt_0.json"}}
```

Key attrs: `model`, `inputTokens`, `outputTokens`, `ttft` (time to first token ms),
`systemPromptFile` (reference to system prompt file), `error` (when failed).

### user_message / agent_response -- user input and model output

Key attrs: `content` (user message), `response` (model output as JSON array).

### turn_start / turn_end -- tool-calling loop boundaries

Use `turnId` to count loop iterations and group events per turn.

### session_start -- session metadata

Key attrs: `copilotVersion`, `vscodeVersion`.

## Investigation Workflow

<investigation-rules>

1. **Identify log file** -- Use the `{{VSCODE_TARGET_SESSION_LOG}}` variable. Start with `main.jsonl`.
2. **Triage via terminal** -- Use `run_in_terminal` with PowerShell (Windows):
3. **Read only relevant slices** -- Never read entire log files (can be tens of MB). Search first, then `read_file` for targeted line ranges.
4. **Correlate via spanId/parentSpanId** -- Events form a tree: user_message -> llm_request -> tool_call.
5. **Determine root cause** -- Pick most likely cause from evidence. State confidence.
6. **Provide remediation** -- Concrete next steps only, no speculation.

</investigation-rules>

## PowerShell Search Commands (Windows)

```powershell
# Find errors
Select-String '"status":"error"' "$env:APPDATA\Code\User\workspaceStorage\*\GitHub.copilot-chat\debug-logs\*\main.jsonl"

# Find discovery events (skill/agent/instruction loading)
Select-String '"type":"discovery"' <logPath>

# Find slow events with Node.js
node -e "require('fs').readFileSync('<logPath>','utf8').split('\n').filter(Boolean).map(JSON.parse).filter(e=>e.dur>5000).forEach(e=>console.log(JSON.stringify({type:e.type,name:e.name,dur:e.dur})))"

# Count events by type
node -e "const l=require('fs').readFileSync('<logPath>','utf8').split('\n').filter(Boolean).map(JSON.parse);const c={};l.forEach(e=>c[e.type]=(c[e.type]||0)+1);Object.entries(c).sort((a,b)=>b[1]-a[1]).forEach(([t,n])=>console.log(n,t))"

# Find user messages
node -e "require('fs').readFileSync('<logPath>','utf8').split('\n').filter(Boolean).map(JSON.parse).filter(e=>e.type==='user_message').forEach(e=>console.log(e.attrs.content))"

# Check file size before loading
(Get-Item '<logPath>').Length
```

<warning>
Never use `grep_search` for log files -- it only searches workspace files.
Always use `run_in_terminal` with PowerShell or Node.js for log files.
Never read entire log files with `read_file` -- check size first, then read targeted line ranges.
</warning>

## Common Root Causes

### Skill/Agent did not load

Check `discovery` events for `name-mismatch`, `not-found`, or `frontmatter-error`.

Most common causes:
- Folder name does not match `name:` field in YAML frontmatter
- YAML frontmatter has unescaped colon in a value (quote the description)
- YAML frontmatter is NOT at line 1 of the file (tabs instead of spaces, content above `---`)
- `user-invocable: false` and user typed it as a slash command

Fix pattern:

| | Value |
|---|---|
| Folder name | `my-skill` |
| Name in SKILL.md | `my-skill2` |
| Fix | Change `name: my-skill2` to `name: my-skill`, OR rename the folder |

After fixing, start a new chat session to force reload.

### Instruction not applied

- Check `system_prompt_0.json` -- is the instruction text present in the system prompt?
- If not: `applyTo` glob pattern may not match the current file type
- `applyTo: "**"` is always included but uses context budget on every request

### Request was slow

Check `llm_request` events with high `dur`. Common causes:
- High `inputTokens` (context too large)
- `ttft` high but `outputTokens` low (model thinking / first token delay)
- Multiple sequential tool calls (parallelization opportunity)

### Tool call failed

Check `tool_call` events with `"status":"error"`. The `error` field contains the exact message.

## Network Issues

If you suspect authentication or network problems, run:

```
copilot_runVscodeCommand: github.copilot.debug.collectDiagnostics
```

The command returns a full diagnostics report including auth status, network checks,
and proxy configuration.

## Response Guidelines

- State what happened and why (root cause), key evidence, and concrete next steps.
- Do not narrate the investigation process.
- Do not reference internal log field names (spanId, JSONL, etc.) to the user.
- Quote specific error messages verbatim. Do not paste entire log entries.
- Use a table when showing a name mismatch or comparing multiple values.

## References

- Custom instructions: https://code.visualstudio.com/docs/copilot/customization/custom-instructions
- Custom agents: https://code.visualstudio.com/docs/copilot/customization/custom-agents
- Hooks: https://code.visualstudio.com/docs/copilot/customization/hooks
- Copilot Issues wiki: https://github.com/microsoft/vscode/wiki/Copilot-Issues
