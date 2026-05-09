---
name: create-agent
description: "Create a custom agent (.agent.md) for a specific job. Use when: defining a new specialist agent, restricting tool access for a persona, building a subagent for orchestration."
user-invocable: false
disable-model-invocation: true
---

# Create Agent

Guide the user to create a `.agent.md` in `.github/agents/`.

## Extract from Conversation

Review the conversation history. If the user has been using the agent in a specialized way
(restricting tools, following a specific persona, focusing on certain file types), extract:
- The specialized role or persona being assumed
- Tool preferences (which to use, which to avoid)
- The domain or job scope

## Clarify if Needed

If no clear specialization emerges, ask:
- What job should this agent do?
- When should it be picked over the default agent?
- Which tools should it use (or avoid)?

## Iterate

1. Draft the agent file and save it to `.github/agents/<name>.agent.md`.
2. Identify the most ambiguous or weak parts and ask about those.
3. Once finalized, summarize what the agent does, suggest example prompts to try it, and propose
   related customizations to create next.

## Reference: Agent Frontmatter



```yaml
---
description: "<required>"    # For agent picker and subagent discovery
name: "Agent Name"           # Optional, defaults to filename
tools: [search, web]         # Optional: aliases, MCP (<server>/*), extension tools
model: "Claude Sonnet 4"     # Optional, uses picker default; supports array for fallback
agents: [agent1, agent2]     # Optional, restrict allowed subagents by name (omit = all, [] = none)
user-invocable: false        # Optional, hide from picker for subagent-only routing
disable-model-invocation: false  # Optional, prevent subagent invocation (default: false)
handoffs: [...]              # Optional, transitions to other agents
---
```

### Invocation Control

| Attribute | Default | Effect |
|-----------|---------|--------|
| `user-invocable: false` | `true` | Hide from agent picker, only accessible as subagent |
| `disable-model-invocation: true` | `false` | Prevent other agents from invoking as subagent |

### Model Fallback

```yaml
model: ['Claude Sonnet 4.5 (copilot)', 'GPT-5 (copilot)']  # First available model is used
```

## Tools

Sources: built-in aliases, specific tools, MCP servers (`<server>/*`), extension tools.

**Special**: `[]` = no tools, omit = defaults. Body reference: `#tool:<name>`

### Tool Aliases

| Alias | Purpose |
|-------|---------|
| `execute` | Run shell commands |
| `read` | Read file contents |
| `edit` | Edit files |
| `search` | Search files or text |
| `agent` | Invoke custom agents as subagents |
| `web` | Fetch URLs and web search |
| `todo` | Manage task lists |

### Common Patterns

```yaml
tools: [read, search]             # Read-only research
tools: [myserver/*]               # MCP server only
tools: [read, edit, search]       # No terminal access
tools: []                         # Conversational only
```

To discover available tools, check your current tool list or use `#tool:` syntax in the body to reference specific tools.

## Template

```markdown
---
description: "{Use when... trigger phrases for subagent discovery}"
tools: [{minimal set of tool aliases}]
user-invocable: false
---
You are a specialist at {specific task}. Your job is to {clear purpose}.

## Constraints
- DO NOT {thing this agent should never do}
- DO NOT {another restriction}
- ONLY {the one thing this agent does}

## Approach
1. {Step one of how this agent works}
2. {Step two}
3. {Step three}

## Output Format
{Exactly what this agent should return}
```

## Invocation

- **Manual**: Agent selector in chat
- **Subagent**: Parent agent delegates based on `description` match (when `infer` allows)

## Core Principles

1. **Single role**: One persona with focused responsibilities per agent
2. **Minimal tools**: Only include what the role needs—excess tools dilute focus
3. **Clear boundaries**: Define what the agent should NOT do
4. **Keyword-rich description**: Include trigger words so parent agents know when to delegate

## Anti-patterns

- **Swiss-army agents**: Too many tools, tries to do everything
- **Vague descriptions**: "A helpful agent" doesn't guide delegation—be specific
- **Role confusion**: Description doesn't match body persona
- **Circular handoffs**: A -> B -> A without progress criteria
