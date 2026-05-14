# Agentic Workflow -- Authoritative Workspace Plan

<rules>

- Read files in `../useful-agentic-workflow-docs/` first when that directory exists. If it does not exist in the current workspace, use this plan and `README.md` as the bootstrap context.
- This plan is the single source of truth for what exists and what is planned. Update it after every completed task.
- All agents and skills listed here MUST exist as files. Ghost references are forbidden.
- Planned integrations must be marked explicitly as `Planned` or `Watchlist` until their files, config, and docs exist in the workspace.
</rules>

Last updated: 2026-05-11
Status: Active

## Vision

The most complete agentic-workflow framework for GitHub Copilot in VS Code.
Language-agnostic and reusable for any project. Provides a layered system:

- **Layer 1 -- Native VS Code/Copilot**: built-in memory tool, Plan agent, chat checkpoints, Copilot CLI background agents, hooks
- **Layer 2 -- Custom Agents**: specialized personas (Planner, Research, Dev, Quality, Commit, Code Reviewer)
- **Layer 3 -- Skills Library**: orchestration, TDD, security, knowledge graph, impact analysis, creation wizards
- **Layer 4 -- MCP Servers**: ahk (task orchestration state), graphify (documentation graph), gitnexus (impact analysis)
- **Layer 5 -- Scoped Instructions**: file-pattern-specific rules via `.github/instructions/`

Current strategic recommendation for evolving this workspace into `everything-copilot`:

- Keep **GitNexus** as the retained code-impact layer.
- Keep **Graphify on LadybugDB** as the retained documentation and semantic graph layer.
- Keep **AHK (`@cardor/agent-harness-kit`)** as the integrated orchestration backbone for backlog, atomic task claiming, action journal, and health gates.
- Re-evaluate **CodeGraphContext** only after a candidate release returns real symbol data under the deep validation battery.
- Use the committed **Dockerfile** when a reproducible packaged environment is needed for the active workspace surface.
- Treat **Bernstein** and **axiom-graph** as later-stage additions, not first-wave dependencies.

## Core Architecture

```
GitHub Copilot (VS Code)
        |
   [copilot-instructions.md]   -- Always-on global rules
   [.github/instructions/]     -- Scoped rules (per file type/folder)
        |
   [Hooks]                     -- Deterministic lifecycle enforcement
     [.github/hooks/graph-patch.json]
        |
   [Orchestrator Skill]        -- Coordinates multi-agent workflows via manifest
        |
   +--------+--------+--------+--------+
   |        |        |        |        |
Planner  Research   Dev    Quality  Commit
   |                           |
[Skills Library]          [MCP Servers]
graphify                  ahk (tasks/actions/docs)
gitnexus                  graphify (graph.json)
                         gitnexus (impact/context)
tdd-workflow
memory
security-review
verification-loop
search-first
iterative-retrieval
code-quality
create-skill / create-agent
create-hook / create-prompt
troubleshoot
        |
[Copilot CLI]              -- Background agents (long-running, worktree isolation)
```

## Agents

| Agent        | File                           | Purpose                              |
|--------------|-------------------------------|--------------------------------------|
| Orchestrator | skill: orchestrator/SKILL.md  | Coordinate Research->Dev->QA->Commit |
| Planner      | agents/planner.agent.md       | Phased implementation plans          |
| Research     | agents/research.agent.md      | Gather docs, APIs, repo insights     |
| Dev          | agents/dev.agent.md           | Implement tasks from manifest        |
| Quality      | agents/quality.agent.md       | Validate implementations via tests   |
| Commit       | agents/commit.agent.md        | Precise conventional commit messages |
| Code Reviewer      | agents/code-reviewer.agent.md          | Security, quality, maintainability   |
| Architect          | agents/architect.agent.md              | System design, ADRs, scalability     |
| Code Architect     | agents/code-architect.agent.md         | Codebase-grounded implementation blueprints |
| Code Explorer      | agents/code-explorer.agent.md          | Execution-path and dependency mapping |
| TDD Guide          | agents/tdd-guide.agent.md              | TDD specialist, RED-GREEN-REFACTOR   |
| Refactor Cleaner   | agents/refactor-cleaner.agent.md       | Dead code cleanup, consolidation     |
| Build Error Resolver| agents/build-error-resolver.agent.md  | Fix build/type errors, minimal diffs |
| Security Reviewer  | agents/security-reviewer.agent.md      | OWASP Top 10 vulnerability detection |
| Database Reviewer  | agents/database-reviewer.agent.md      | PostgreSQL review specialist         |
| Silent Failure Hunter | agents/silent-failure-hunter.agent.md | Reliability and error-propagation review |
| PR Test Analyzer   | agents/pr-test-analyzer.agent.md       | Behavioral test coverage review      |
| E2E Runner         | agents/e2e-runner.agent.md             | Critical user-journey end-to-end testing |
| Performance Optimizer| agents/performance-optimizer.agent.md| Profiling, bundle, query, memory     |
| Doc Updater        | agents/doc-updater.agent.md            | Codemaps and documentation sync      |
| TypeScript Reviewer| agents/typescript-reviewer.agent.md    | TS/JS code review specialist         |
| Python Reviewer    | agents/python-reviewer.agent.md        | Python code review specialist        |
| Go Reviewer        | agents/go-reviewer.agent.md            | Go code review specialist            |
| Rust Reviewer      | agents/rust-reviewer.agent.md          | Rust safety and patterns reviewer    |

## Skills Library

| Skill              | Directory                      | When to use                             |
|--------------------|--------------------------------|-----------------------------------------|
| graphify           | skills/graphify/               | Knowledge graph exploration             |
| gitnexus           | skills/gitnexus/               | Architecture impact analysis            |
| tdd-workflow       | skills/tdd-workflow/           | RED-GREEN-REFACTOR with checkpoints     |
| memory             | skills/memory/                 | Orient-Work-Persist session rhythm      |
| security-review    | skills/security-review/        | OWASP Top 10 audit before merge         |
| code-quality       | skills/code-quality/           | Static analysis, lint, type checking    |
| orchestrator       | skills/orchestrator/           | Multi-agent manifest coordination       |
| verification-loop  | skills/verification-loop/      | Pre-PR gate: build+types+lint+tests     |
| search-first       | skills/search-first/           | Research before writing custom code     |
| iterative-retrieval| skills/iterative-retrieval/    | Progressive context for multi-agent     |
| troubleshoot       | skills/troubleshoot/           | Debug why skills/agents did not load    |
| create-skill       | skills/create-skill/           | Create new SKILL.md files               |
| create-agent       | skills/create-agent/           | Create new agent definitions            |
| create-hook        | skills/create-hook/            | Create .github/hooks/ policy files      |
| create-mcp         | skills/create-mcp/             | Create MCP server integrations          |
| create-prompt      | skills/create-prompt/          | Create .prompt.md files                 |
| coding-standards   | skills/coding-standards/       | Baseline cross-project code conventions |
| strategic-compact  | skills/strategic-compact/      | Context compaction at task boundaries   |
| deep-research      | skills/deep-research/          | Multi-source cited research reports     |
| eval-harness       | skills/eval-harness/           | EDD pass@k evaluation framework         |
| e2e-testing        | skills/e2e-testing/            | Playwright E2E patterns and config      |
| api-design         | skills/api-design/             | REST API conventions and checklist      |
| frontend-patterns  | skills/frontend-patterns/      | React/Next.js component patterns        |
| backend-patterns   | skills/backend-patterns/       | Backend architecture patterns           |
| mcp-server-patterns| skills/mcp-server-patterns/    | Build MCP servers with Node/TS SDK      |

## Support Directories

| Path                  | Purpose                                        |
|-----------------------|------------------------------------------------|
| `.github/instructions/` | Scoped `.instructions.md` files               |
| `.github/tasks/`        | Generated manifests and task payloads         |
| `.github/plan_history/` | Orchestration audit trail and plan snapshots  |
| `.harness/`             | AHK operational backlog, SQLite state, and markdown fallback |
| `.memory/`              | Optional vault scaffold used by the memory skill |

## MCP Servers (.vscode/mcp.json)

| Server    | Command                          | Key Tools                                         |
|-----------|----------------------------------|---------------------------------------------------|
| ahk       | npx --no-install ahk serve       | tasks.get, tasks.claim, actions.start, actions.write, actions.complete, docs.search |
| graphify  | uv run python scripts/atomic_index.py serve-graphify --db-path .graphify/lbug | query_graph, get_node, get_neighbors, shortest_path |
| gitnexus  | npx @duytransipher/gitnexus@latest mcp | impact, context, detect_changes, rename            |

Preferred for this repository: run `/graphify .` in Copilot Chat to build `graphify-out/graph.json` and `graphify-out/GRAPH_REPORT.md` with GitHub Copilot as the semantic extractor. Use headless `uv run graphify extract . --backend <backend>` only when explicit backend credentials are available.

AHK is configured locally via `package.json`, `agent-harness-kit.config.ts`, `health.sh`, `.harness/feature_list.json`, and the manual `.vscode/mcp.json` registration above. It uses the AHK package's `claude-code` provider mode only to satisfy the package schema, but provider-materialized files are intentionally excluded from the tracked repository surface and blocked by the health gate.

CodeGraphContext is not part of the active MCP surface. Deep validation against the 0.4.7 candidate found successful indexing with zero extracted symbols and inconsistent backend-selection behavior, so future revalidation is tracked as backlog work instead of an active integration.

## Strategic Integration Priorities

These priorities describe the recommended implementation order for the `everything-copilot` program. They are planning records, not claims that the integrations already exist.

| Priority | Component | Role in target platform | Status | Notes |
|----------|-----------|-------------------------|--------|-------|
| 1 | AHK (`@cardor/agent-harness-kit`) | Orchestration backbone: backlog, atomic task claiming, action journal, health gate, dashboard, local MCP task tools | Active | Integrated local MCP server and Copilot-facing runtime files; provider materializations are intentionally excluded |
| 2 | CodeGraphContext | Live code graph with automatic refresh and MCP-facing graph queries | Planned | Candidate only; 0.4.7 failed deep validation and is not registered in the active workspace MCP surface |
| 3 | GitNexus | Code impact analysis, symbol relationships, blast-radius reasoning | Active | Retained core layer |
| 4 | Graphify + LadybugDB + SQLite FTS5 | Documentation graph, semantic retrieval, prompt and skill knowledge graph, raw-text retrieval | Active | LadybugDB remains the primary graph store; `.graphify/docs-fts.db` adds local raw-text retrieval |
| 5 | Docker portability | Reproducible environment and onboarding support | Active | Dockerfile now packages the validated active workspace surface |
| 6 | Bernstein | Possible future orchestration upgrade or expansion path | Watchlist | Evaluate after AHK and CodeGraphContext |
| 7 | axiom-graph | Possible later addition for stale documentation and code-doc drift checks | Watchlist | Targeted follow-up, not core first wave |

## Memory System

Three complementary tiers:

### Tier 1 -- Built-in VS Code Memory Tool (backend)

The built-in memory tool stores notes in three scopes. The custom `memory` skill uses this as its backend.
Enable with `github.copilot.chat.tools.memory.enabled` (on by default).

| Scope      | Path               | Persists | Use for                              |
|------------|--------------------|----------|--------------------------------------|
| User       | `/memories/`       | Always   | Preferences, patterns, commands      |
| Repository | `/memories/repo/`  | Per repo | Conventions, build commands, ADRs    |
| Session    | `/memories/session/`| Session | In-progress plans, working notes     |

### Tier 2 -- Custom Memory Skill (orchestration layer)

The `memory` skill wraps the built-in tool with a structured Orient-Work-Persist rhythm
and the `.memory/` vault pattern for richer organization:

```
.memory/
  INDEX.md      -- Read FIRST every session (vocabulary seed)
  active/       -- Current session state
  decisions/    -- ADR-style architecture decisions
  learnings/    -- Extracted patterns and lessons
  glossary/     -- Domain terms
  blockers/     -- Open questions and constraints
```

### Tier 3 -- Copilot Memory (optional, GitHub-hosted)

GitHub-hosted cross-agent memory: shared between Copilot CLI, code review, and cloud agents.
Enable in GitHub settings + `github.copilot.chat.copilotMemory.enabled` in VS Code.
Repository-scoped, auto-expires after 28 days. Best for team workflows.

## Hooks (.github/hooks/)

Hooks enforce deterministic policies at lifecycle events. Exit code 0 = allow, non-zero = block.

| File           | Event       | Purpose                                |
|----------------|-------------|----------------------------------------|
| graph-patch.json | PostToolUse, SubagentStop, Stop | Patch Graphify continuously after mutating tool calls, reconcile when subagents stop, and reconcile once more at agent stop |

Use the `create-hook` skill to add new hook policies.

## Scoped Instructions (.github/instructions/)

File-pattern-specific rules that supplement `copilot-instructions.md`.
Use VS Code `/instructions` or add the files directly in `.github/instructions/`.

Examples to create:
- `agent-files.instructions.md` -- rules for editing `.agent.md` / `SKILL.md` files
- `python.instructions.md` -- Python-specific conventions

## Workflow: How to Use This Framework

### For a new project

1. Copy `.github/` into the project root.
2. Bootstrap local Python tooling with `uv sync`.
3. Install local Node dependencies with `npm install` when the project uses AHK.
4. In Copilot Chat, run `/graphify .` to build the initial knowledge graph.
5. Start the MCP servers (see `.vscode/mcp.json`).
6. Update `.github/PLAN.md` to reflect project-specific goals.
7. Invoke `memory` skill Orient phase to seed context.

### For implementing a feature (interactive)

1. Open Copilot Chat, invoke the orchestrator prompt (`#prompt:orchestrator.prompt.md`).
2. Orchestrator reads PLAN.md and produces a manifest; review and approve.
3. When the `ahk` MCP server is connected, the Orchestrator uses AHK as the operational task ledger: locate or add the task, claim it when execution begins, and record actions during implementation and validation.
4. Planner produces a phased plan; Orchestrator dispatches to Research/Dev/Quality/Commit.
5. Use chat checkpoints to rewind if the agent goes off track.
6. After completion: run `memory` Persist phase to capture learnings.

### For implementing a feature (background / long-running)

1. Start interactively with a local agent to clarify scope and produce a plan.
2. Hand off to Copilot CLI: open Session Target dropdown -> Copilot CLI.
3. Choose worktree isolation (recommended) to keep changes isolated until review.
4. Monitor progress from the Chat sessions list; intervene via chat when needed.
5. Review the worktree diff, merge when satisfied.

### For exploring an unfamiliar codebase

1. If the graph is missing or stale, run `/graphify .` in Copilot Chat.
2. Invoke `graphify` skill -- reads GRAPH_REPORT.md, surfaces god nodes.
3. Invoke `gitnexus` skill -- runs `context` on key symbols.
4. Reference `#file:graphify-out/GRAPH_REPORT.md` in chat for architecture questions.

### For TDD development

1. Invoke `tdd-workflow` skill.
2. Follow: Write Journeys -> RED -> checkpoint -> GREEN -> checkpoint -> REFACTOR -> coverage gate.
3. Run `security-review` skill before merge.
4. Run `verification-loop` skill before opening a PR.

### For memory management

1. Start session: `memory` skill Orient phase.
2. End session: `memory` skill Persist phase.
3. Promote patterns: session -> repo -> user memory.

### When Copilot behaves unexpectedly

1. Invoke `troubleshoot` skill.
2. Point it at `{{VSCODE_TARGET_SESSION_LOG}}` (current session debug log).
3. Check for name-mismatch (folder name != `name:` in frontmatter).

## Conventions

- Language-agnostic: no framework assumptions. Skills describe process, not implementation.
- ASCII only: no emojis, no special characters in code, agent, or skill files.
- English: all docs and code in English.
- Search before edit: always semantic_search + grep_search before modifying any file.
- Context engineering: load only what is needed per LLM call (Karpathy principle).
- XML for instructions, Markdown for output, JSON for tool calls (see copilot-instructions.md).
- Docker: optional for target projects that are already containerized; not required for this repo itself.

## Implementation Roadmap

### Workspace Backlog

| Phase | Item                                             | Status      |
|-------|--------------------------------------------------|-------------|
| P1    | Create `.github/instructions/` scoped files      | Scaffolded  |
| P1    | Update `memory` SKILL.md to reference built-in tool | Planned  |
| P1    | Strip Docker mandate from `copilot-instructions.md` | Completed |
| P2    | Import `code-architect` agent                    | Completed   |
| P2    | Import `code-explorer` agent                     | Completed   |
| P2    | Import `database-reviewer` agent                 | Completed   |
| P2    | Import `silent-failure-hunter` agent             | Completed   |
| P2    | Import `pr-test-analyzer` agent                  | Completed   |
| P2    | Import `e2e-runner` agent                        | Completed   |
| P2    | Add Copilot CLI handoff guidance to orchestrator prompt | Planned |
| P2    | Add more hooks (PreToolUse: format check, SessionStart: memory orient) | Planned |
| P3    | Document Copilot Memory setup guide              | Planned     |

### Everything-Copilot Program

| Phase | Item | Status | Outcome |
|-------|------|--------|---------|
| EC0 | Codify strategic tool ranking in PLAN, README, and repo memory | Completed | Source-of-truth docs reflect the adopted direction |
| EC1 | Integrate AHK as the orchestration backbone | Completed | Shared backlog, atomic task claiming, action journal, health gate, dashboard, MCP task tools |
| EC2 | Adapt orchestrator, memory, and workflow docs around the AHK task lifecycle | Completed | AHK is part of the documented operating model instead of an isolated add-on |
| EC3 | Deep-validate CodeGraphContext before integration | Completed | 0.4.7 candidate failed symbol-extraction validation and was quarantined from the active workspace surface |
| EC4 | Define clean coexistence boundaries across AHK, GitNexus, and Graphify while quarantining unstable candidates | Completed | PLAN and README now describe only the active tool boundaries and track CodeGraphContext as future revalidation work |
| EC5 | Add Docker portability support for the validated active workspace surface | Completed | Dockerfile now builds uv, npm, the pinned dependencies, and the repository health gate in one reproducible image |
| EC6 | Evaluate Bernstein as a possible future orchestration upgrade | Watchlist | Revisit only after EC1-EC5 are stable |
| EC7 | Evaluate axiom-graph for doc drift and stale documentation checks | Watchlist | Optional targeted addition after core platform is stable |

## External Tool Sources

| Tool                    | Repo                                          | License             |
|-------------------------|-----------------------------------------------|---------------------|
| Agent Harness Kit (AHK) | github.com/enmanuelmag/agent-harness-kit      | MIT                 |
| Graphify                | github.com/safishamsi/graphify                | MIT                 |
| GitNexus                | github.com/abhigyanpatwari/GitNexus           | PolyForm Noncommercial |
| Everything Claude Code  | github.com/affaan-m/everything-claude-code    | See repo            |
| Hermes Agent            | github.com/NousResearch/hermes-agent          | MIT                 |
| Obsidian vault patterns | github.com/swarmclawai/swarmvault             | See repo            |
| Karpathy principles     | karpathy.bearblog.dev                         | Public domain       |

## Task History

| Task ID | Title                                         | Status    |
|---------|-----------------------------------------------|-----------|
| task_1  | Rewrite PLAN.md + define capabilities roadmap | Completed |
| task_2  | Create photovoltaic France launch pack        | Completed |
| task_3  | Define everything-copilot strategic integration roadmap | Completed |
| task_4  | Integrate AHK into the workspace MCP and workflow stack | Completed |
| task_5  | Deep-validate the CodeGraphContext candidate and quarantine it from the active workspace surface | Completed |
| task_6  | Stabilize the active workspace surface and add Docker packaging | Completed |
