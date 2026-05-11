<MANDATORY-RULES>

- Only use ASCII-safe characters (NO EMOJIS, NO SPECIAL CHARACTERS).
- Prefer project-local environments or configured containers when available. Do not require Docker for this workflow repository itself.
- Any CLI implementation must always be implemented in Python with Typer.
- This repository's local Python tooling is declared in `pyproject.toml` and locked in `uv.lock`. The current Python dependencies include `graphifyy`, `ladybug`, `mcp`, `pyyaml`, and `typer`.
- Before running repository Python scripts or validators, ensure the project environment is synced with `uv sync` from the repository root.
- For graphify on markdown-heavy repositories without external backend credentials, use the workspace `/graphify` prompt as the user-facing entrypoint; it must delegate to the canonical `graphify` skill workflow. Use headless `uv run graphify extract --backend ...` only when explicit backend credentials are configured.
- Before creating or modifying any skill folder under `.github/skills/`, invoke the `create-skill` skill.
- Never assume `.venv` or those Python libraries are already installed.
- Be precise, explicit, and deterministic.
- Language: English
- Search before edit: always run semantic_search + grep_search before modifying any file.
- Context engineering: load only what is needed for the current LLM call (Karpathy principle).
- Language convention: XML for instructions/rules/constraints (you->LLM), Markdown for human output (LLM->human), JSON for tool calls and strict output formats.

</MANDATORY-RULES>

# General Instructions

- You can disagree with the user, but you must always argue.
- If information is missing or ambiguous, ask before acting.
- Never silently relax constraints or ignore failures.
- Prefer explicit errors over assumptions.

# Workspace Architecture

Authoritative plan: #file:./PLAN.md

## Agents Available

- @planner (agents/planner.agent.md) -- phased implementation plans, risk annotation
- @research (agents/research.agent.md) -- API docs, repo insights, technical spikes
- @dev (agents/dev.agent.md) -- implementation from manifest, patch-style edits
- @quality (agents/quality.agent.md) -- validation, test runs, invariant checks
- @commit (agents/commit.agent.md) -- precise conventional commit messages
- @code-reviewer (agents/code-reviewer.agent.md) -- code review: security, quality, maintainability
- @architect (agents/architect.agent.md) -- system design, ADRs, scalability decisions
- @code-architect (agents/code-architect.agent.md) -- codebase-grounded implementation blueprints
- @code-explorer (agents/code-explorer.agent.md) -- execution-path and dependency mapping before changes
- @tdd-guide (agents/tdd-guide.agent.md) -- TDD specialist: RED-GREEN-REFACTOR enforcement
- @refactor-cleaner (agents/refactor-cleaner.agent.md) -- dead code cleanup and consolidation
- @build-error-resolver (agents/build-error-resolver.agent.md) -- fix build/type errors, minimal diffs
- @security-reviewer (agents/security-reviewer.agent.md) -- OWASP Top 10 vulnerability detection
- @database-reviewer (agents/database-reviewer.agent.md) -- PostgreSQL query, schema, and safety review
- @silent-failure-hunter (agents/silent-failure-hunter.agent.md) -- swallowed-error and reliability review
- @pr-test-analyzer (agents/pr-test-analyzer.agent.md) -- PR test coverage quality and gap analysis
- @e2e-runner (agents/e2e-runner.agent.md) -- end-to-end journey testing and flaky-test control
- @performance-optimizer (agents/performance-optimizer.agent.md) -- profiling, bundle, DB query, memory
- @doc-updater (agents/doc-updater.agent.md) -- codemaps and documentation sync
- @typescript-reviewer (agents/typescript-reviewer.agent.md) -- TypeScript/JavaScript code reviewer
- @python-reviewer (agents/python-reviewer.agent.md) -- Python code reviewer (PEP 8, type hints, security)
- @go-reviewer (agents/go-reviewer.agent.md) -- Go code reviewer (idiomatic Go, concurrency, errors)
- @rust-reviewer (agents/rust-reviewer.agent.md) -- Rust code reviewer (safety, ownership, lifetimes)

## Skills Available

- graphify -- knowledge graph over codebase: read graphify-out/GRAPH_REPORT.md first
- gitnexus -- impact analysis: run context + impact before editing shared symbols
- tdd-workflow -- RED-GREEN-REFACTOR with git checkpoints
- memory -- Orient-Work-Persist session rhythm, .memory/ vault management
- security-review -- OWASP Top 10 audit before merge
- orchestrator -- coordinate Research->Dev->QA->Commit workflows
- code-quality -- static analysis, linting, type checking
- create-skill -- create new SKILL.md files
- create-agent -- create new agent definitions
- create-hook -- create hooks for deterministic lifecycle enforcement (.github/hooks/)
- create-prompt -- create reusable .prompt.md files
- search-first -- research existing solutions before writing custom code
- verification-loop -- full quality gate: build+types+lint+tests+security before PR
- iterative-retrieval -- progressive context retrieval for multi-agent workflows
- troubleshoot -- investigate why skills/agents/instructions did not load or behave unexpectedly
- coding-standards -- baseline cross-project conventions: naming, KISS/DRY, TypeScript patterns
- strategic-compact -- context compaction at logical task boundaries
- deep-research -- multi-source research producing cited reports
- eval-harness -- EDD evaluation framework with pass@k and pass^k metrics
- e2e-testing -- Playwright E2E patterns, POM, CI/CD integration, flaky test fixes
- api-design -- REST API conventions, status codes, pagination, rate limiting, versioning
- frontend-patterns -- React/Next.js components, hooks, state management, performance
- backend-patterns -- backend architecture: repository, service layer, caching, auth, RBAC
- mcp-server-patterns -- build MCP servers with Node/TypeScript SDK, tool/resource registration

## MCP Servers

- graphify: query_graph, get_node, get_neighbors, shortest_path
- gitnexus: impact, context, detect_changes, rename, route_map (requires VS Code 1.99+)

## Workspace Layout

- `.github/agents/` -- custom agent definitions (*.agent.md)
- `.github/skills/` -- skill definitions (*/SKILL.md)
- `.github/prompts/` -- reusable prompt files (*.prompt.md)
- `.github/instructions/` -- file-scoped instructions (*.instructions.md)
- `.github/hooks/` -- lifecycle hooks for deterministic enforcement (*.json + scripts/)

## Memory Hierarchy

Start every session: read .memory/INDEX.md (if present) before any other search.
- /memories/session/ -- in-session working notes (cleared after conversation)
- /memories/repo/ -- repo conventions (persistent across sessions)
- /memories/ -- user patterns (persistent across all workspaces)

## Workflow Defaults

1. For new tasks: invoke @planner or orchestrator skill.
2. For codebase exploration: invoke graphify skill, read GRAPH_REPORT.md, and use the workspace `/graphify` prompt when the graph is missing or stale.
3. For pre-refactor analysis: invoke gitnexus skill, run impact + context.
4. For feature implementation: use tdd-workflow skill.
5. Before adding dependencies: use search-first skill.
6. After completing a feature: run verification-loop skill.
7. For pre-merge validation: run security-review skill + quality agent.
8. After any significant session: run memory skill Persist phase.

<LANGUAGE-CONVENTIONS>

## Prompt Engineering Language Split

Three languages, three roles. Never mix them up:

| Language | Role | Where to use |
|----------|------|--------------|
| XML      | Instructions (you -> LLM) | Rules, constraints, gates, handoffs in .agent.md and SKILL.md |
| Markdown | Presentation (LLM -> human) | Descriptive text, step titles, examples for readability |
| JSON     | Structured data (LLM <-> tools) | Tool call formats, strict output schemas, mcp.json |

### Rules for authoring .agent.md and SKILL.md files

- YAML frontmatter: required, keep as-is (VS Code parser requirement)
- Workflow steps and narrative: Markdown headers and prose
- Constraints, gates, rules, handoffs: wrap in XML tags

Example structure for an agent file:

```
---
name: my-agent
---

# My Agent

Narrative description in Markdown.

<constraints>
- Never modify files outside the declared scope.
- Always run tests before committing.
</constraints>

<gates>
- RED gate: test must fail before implementation starts.
- GREEN gate: all tests pass before refactor.
</gates>

<handoffs>
- On success: pass manifest to @dev
- On ambiguity: ask @planner for clarification
</handoffs>
```

### Why XML over nested Markdown headers for instructions

- Explicit close tag: `</constraints>` marks the exact end of a rule block;
  a `##` header in Markdown is ambiguous about where the section ends.
- Extraction-safe: an orchestrator can parse `<gates>` blocks reliably;
  Markdown heading parsing is fragile when content itself contains `#`.
- Attribute-ready: `<rule priority="critical">` is impossible in Markdown.
- Conflict-free: XML tags cannot be confused with content that uses Markdown
  syntax (code blocks, bullet lists, heading levels).

</LANGUAGE-CONVENTIONS>