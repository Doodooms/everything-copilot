---
name: strategic-compact
description: "Guides strategic context management at logical task boundaries rather than relying on arbitrary compaction. Use when: approaching context limits, switching task phases, or after completing a major milestone. Derived from Everything Claude Code (https://github.com/affaan-m/everything-claude-code)."
---

# Strategic Context Management

Recommends starting a fresh session at logical task boundaries rather than
continuing in an overloaded context window, preserving coherent working memory
through task phases.

## When to Activate

- Running long sessions approaching context limits
- Working on multi-phase tasks (research -> plan -> implement -> test)
- Switching between unrelated tasks within the same session
- After completing a major milestone and starting new work
- When responses become less coherent (context pressure)

## Why Strategic Session Management?

Auto-compaction triggers at arbitrary points:
- Often mid-task, losing important context
- No awareness of logical task boundaries
- Can interrupt complex multi-step operations

Strategic resets at logical boundaries:
- **After exploration, before execution** -- compact research context, keep implementation plan
- **After completing a milestone** -- fresh start for next phase
- **Before major context shifts** -- clear exploration context before a different task

## Compaction Decision Guide

| Phase Transition | Reset? | Why |
|-----------------|--------|-----|
| Research -> Planning | YES | Research context is bulky; plan is the distilled output |
| Planning -> Implementation | YES | Plan is saved to PLAN.md; free up context for code |
| Implementation -> Testing | MAYBE | Keep if tests reference recent code; reset if switching focus |
| Debugging -> Next feature | YES | Debug traces pollute context for unrelated work |
| Mid-implementation | NO | Losing variable names, file paths, and partial state is costly |
| After a failed approach | YES | Clear dead-end reasoning before trying a new approach |

## What Survives a Session Reset

Understanding what persists helps you reset with confidence:

| Persists | Lost |
|----------|------|
| `.github/copilot-instructions.md` | Intermediate reasoning and analysis |
| Repository memory (`/memories/repo/`) | File contents previously read |
| Session memory (`/memories/session/`) | Multi-step conversation context |
| Git state (commits, branches) | Tool call history |
| Files on disk (PLAN.md, task manifests) | Nuanced preferences stated verbally |

## Best Practices

<context-management-rules>
1. **Reset after planning** -- Once a plan is finalized in PLAN.md or a task manifest, start a new session for implementation.
2. **Reset after debugging** -- Clear error-resolution context before continuing to the next feature.
3. **Never reset mid-implementation** -- Preserve context for related changes in the same file group.
4. **Write before resetting** -- Save critical context to `/memories/session/` or update PLAN.md before ending the session.
5. **Use session memory** -- Store key decisions and working state in `/memories/session/` so the next session can orient quickly.
6. **Orient at session start** -- Read `.memory/INDEX.md` (if present) and `/memories/session/` files at the start of each new session.
</context-management-rules>

## VS Code Workflow

In VS Code with GitHub Copilot:
- **Start a new chat session** to compact context
- Save critical working state to `/memories/session/` first
- The next session picks up from git state + memory files + PLAN.md
- Reference `#file:.github/PLAN.md` at the start of the new session to re-orient
