---
name: iterative-retrieval
description: "Pattern for progressively refining context retrieval for multi-agent workflows. Solves the subagent context problem: agents don't know what context they need until they start working. Use when spawning subagents, building multi-agent pipelines, or when 'context too large' failures occur. Derived from Everything Claude Code (https://github.com/affaan-m/everything-claude-code)."
user-invocable: false
---

# Iterative Retrieval Pattern

Solves the context problem in multi-agent workflows where subagents do not know
what context they need until they start working.

## When to Activate

- Spawning subagents that need codebase context they cannot predict upfront
- Building multi-agent workflows where context is progressively refined
- Encountering "context too large" or "missing context" failures in agent tasks
- Designing retrieval pipelines for code exploration
- Optimizing token usage in agent orchestration

## The Problem

Subagents are spawned with limited context. They do not know:
- Which files contain relevant code
- What patterns exist in the codebase
- What terminology the project uses

Standard approaches fail:
- **Send everything**: Exceeds context limits
- **Send nothing**: Agent lacks critical information
- **Guess what is needed**: Often wrong

## The Solution: 4-Phase Retrieval Loop

```
+-- DISPATCH --+      +-- EVALUATE --+
| Broad search |----->| Score files   |
+-- ----------+      +-- -----------+
        ^                   |
        |                   v
+-- LOOP ----+      +-- REFINE ----+
| Repeat if  |<-----| Update query  |
| more needed|      | based on gaps |
+-- ---------+      +-- -----------+

Max 3 cycles, then proceed with best context
```

### Phase 1 -- DISPATCH

Start with a broad, high-level query:

```
Initial search:
  patterns: ["src/**", "lib/**"]
  keywords: ["authentication", "user", "session"]
  excludes: ["*.test.*", "*.spec.*", "vendor/"]
```

Use semantic_search and grep_search in parallel. Collect candidate files.

### Phase 2 -- EVALUATE

Assess each retrieved file for relevance to the task:

Scoring:
- **High (0.8-1.0)**: Directly implements target functionality
- **Medium (0.5-0.7)**: Contains related patterns or types
- **Low (0.2-0.4)**: Tangentially related
- **None (0-0.2)**: Not relevant, exclude

For each file, also identify:
- Why it is relevant (or not)
- What context is still missing

### Phase 3 -- REFINE

Update search criteria based on evaluation:
- Add new patterns discovered in high-relevance files
- Add terminology found in the codebase (projects use project-specific names)
- Exclude confirmed irrelevant paths
- Target specific gaps in current understanding

### Phase 4 -- LOOP (max 3 cycles)

Repeat with refined criteria until one of:
- 3+ high-relevance files found AND no critical gaps
- 3 cycles reached (proceed with best available context)

Return files with relevance >= 0.7.

## Practical Examples

### Example 1: Bug Fix Context
```
Task: "Fix the authentication token expiry bug"

Cycle 1:
  Search: "token", "auth", "expiry" in src/**
  Found: auth.py (0.9), tokens.py (0.8), user.py (0.3)
  Refine: Add "refresh", "jwt" keywords; exclude user.py

Cycle 2:
  Search: refined terms
  Found: session_manager.py (0.95), jwt_utils.py (0.85)
  Result: Sufficient context (auth.py, tokens.py, session_manager.py, jwt_utils.py)
```

### Example 2: Feature Implementation
```
Task: "Add rate limiting to API endpoints"

Cycle 1:
  Search: "rate", "limit", "api" in routes/**
  Found: No matches -- codebase uses "throttle" terminology
  Refine: Add "throttle", "middleware" keywords

Cycle 2:
  Search: refined terms
  Found: throttle.py (0.9), middleware/__init__.py (0.7)
  Refine: Need router patterns

Cycle 3:
  Search: "router", "flask|fastapi|express" patterns
  Found: app.py (0.8) with route setup
  Result: throttle.py, middleware/__init__.py, app.py
```

## Integration with Agent Prompts

When constructing a prompt for a subagent, include this retrieval instruction:

```
When retrieving context for this task:
1. Start with broad keyword search across relevant directories
2. Evaluate each file's relevance on a 0-1 scale
3. Identify what context is still missing
4. Refine search criteria and repeat (max 3 cycles)
5. Load only files with relevance >= 0.7
6. Stop when you have 3+ high-relevance files with no critical gaps
```

## Best Practices

1. **Start broad, narrow progressively** -- Do not over-specify initial queries
2. **Learn codebase terminology** -- First cycle often reveals naming conventions
3. **Track what is missing** -- Explicit gap identification drives refinement
4. **Stop at "good enough"** -- 3 high-relevance files beats 10 mediocre ones
5. **Exclude confidently** -- Low-relevance files rarely become relevant
6. **Parallelize initial search** -- Run semantic_search and grep_search in parallel

## Relationship to Other Skills

- **graphify**: Build a knowledge graph first, then use iterative-retrieval for
  precise node traversal
- **gitnexus**: Use context and query tools instead of file search when the index
  is available -- they already encode relevance
- **orchestrator**: Use this pattern when dispatching subagents to ensure they
  receive targeted, sufficient context without exceeding limits