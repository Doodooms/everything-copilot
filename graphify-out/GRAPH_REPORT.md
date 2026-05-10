# Graph Report - .  (2026-05-10)

## Corpus Check
- 88 files · ~70,182 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 390 nodes · 558 edges · 37 communities (33 shown, 4 thin omitted)
- Extraction: 99% EXTRACTED · 0% INFERRED · 1% AMBIGUOUS · INFERRED: 2 edges (avg confidence: 0.86)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 6|Community 6]]
- [[_COMMUNITY_Community 7|Community 7]]
- [[_COMMUNITY_Community 8|Community 8]]
- [[_COMMUNITY_Community 9|Community 9]]
- [[_COMMUNITY_Community 10|Community 10]]
- [[_COMMUNITY_Community 11|Community 11]]
- [[_COMMUNITY_Community 12|Community 12]]
- [[_COMMUNITY_Community 13|Community 13]]
- [[_COMMUNITY_Community 14|Community 14]]
- [[_COMMUNITY_Community 15|Community 15]]
- [[_COMMUNITY_Community 16|Community 16]]
- [[_COMMUNITY_Community 17|Community 17]]
- [[_COMMUNITY_Community 18|Community 18]]
- [[_COMMUNITY_Community 19|Community 19]]
- [[_COMMUNITY_Community 20|Community 20]]
- [[_COMMUNITY_Community 21|Community 21]]
- [[_COMMUNITY_Community 22|Community 22]]
- [[_COMMUNITY_Community 23|Community 23]]
- [[_COMMUNITY_Community 24|Community 24]]
- [[_COMMUNITY_Community 25|Community 25]]
- [[_COMMUNITY_Community 26|Community 26]]
- [[_COMMUNITY_Community 27|Community 27]]
- [[_COMMUNITY_Community 28|Community 28]]
- [[_COMMUNITY_Community 29|Community 29]]
- [[_COMMUNITY_Community 30|Community 30]]
- [[_COMMUNITY_Community 31|Community 31]]
- [[_COMMUNITY_Community 32|Community 32]]
- [[_COMMUNITY_Community 33|Community 33]]
- [[_COMMUNITY_Community 34|Community 34]]
- [[_COMMUNITY_Community 35|Community 35]]
- [[_COMMUNITY_Community 36|Community 36]]

## God Nodes (most connected - your core abstractions)
1. `Build Error Resolver Agent` - 16 edges
2. `Rust Reviewer Agent` - 15 edges
3. `Architect Agent` - 14 edges
4. `Go Reviewer Agent` - 14 edges
5. `validate()` - 13 edges
6. `create-skill SKILL` - 13 edges
7. `Silent Failure Hunter Agent` - 12 edges
8. `Orchestrator Skill` - 12 edges
9. `create-mcp SKILL` - 11 edges
10. `Planner Agent` - 10 edges

## Surprising Connections (you probably didn't know these)
- `agentic-workflow Repository` --includes layer--> `Native VS Code/Copilot Layer`  [EXTRACTED]
  README.md → .github/PLAN.md
- `agentic-workflow Repository` --includes layer--> `Custom Agents Layer`  [EXTRACTED]
  README.md → .github/PLAN.md
- `agentic-workflow Repository` --includes layer--> `Scoped Instructions Layer`  [EXTRACTED]
  README.md → .github/PLAN.md
- `Copilot Tool Snapshot extension` --registers--> `Agentic Workflow: Export Copilot Tool Snapshot`  [EXTRACTED]
  tools/copilot-tool-snapshot/extension.js → tools/copilot-tool-snapshot/README.md
- `Agentic Workflow: Check Copilot Tool Name` --checks via snapshot--> `VS Code language model tools`  [INFERRED]
  tools/copilot-tool-snapshot/README.md → tools/copilot-tool-snapshot/extension.js

## Communities (37 total, 4 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.0
Nodes (52): Architect Agent, Build Error Resolver Agent, Code Reviewer Agent, Go Reviewer Agent, Rust Reviewer Agent, Silent Failure Hunter Agent, cargo check, cargo clippy -- -D warnings (+44 more)

### Community 1 - "Community 1"
Cohesion: 0.0
Nodes (27): Agent Creation Task, Custom Agent File Locations, Agent Frontmatter, Agent Loop, Agent Memory System, Agent Template, Agent Tool Aliases, Agents Reference (+19 more)

### Community 2 - "Community 2"
Cohesion: 0.0
Nodes (26): Commit Agent, Dev Agent, Planner Agent, Quality Agent, Research Agent, Authoritative Research, Commit Message, Model Context (+18 more)

### Community 3 - "Community 3"
Cohesion: 0.0
Nodes (22): uv sync, Copilot Instructions, Authoritative Workspace Plan, README, Local .venv Environment, JSON, Markdown, XML (+14 more)

### Community 4 - "Community 4"
Cohesion: 0.0
Nodes (19): add_toolset_member(), build_tool_suggestions(), build_toolset_names(), contains_runtime_inputs_heading(), find_workspace_root(), has_block_tag(), iter_code_fence_filtered_lines(), iter_extension_manifest_paths() (+11 more)

### Community 5 - "Community 5"
Cohesion: 0.0
Nodes (12): activate(), addToolSetMember(), buildToolSets(), collectToolSnapshot(), delay(), findSuggestions(), getLanguageModelTools(), refreshSnapshotsForWorkspace() (+4 more)

### Community 6 - "Community 6"
Cohesion: 0.0
Nodes (19): Graphify Copilot Workflow, Graphify Durable Outputs, GitNexus, GitNexus Context Tool, GitNexus Detect Changes Tool, GitNexus Impact Tool, Graph Fragment JSON Schema, Graphify (+11 more)

### Community 7 - "Community 7"
Cohesion: 0.0
Nodes (16): Agent Skills, vscode/askQuestions Tool, Compatibility Bounds, Custom Instructions, Forked Context, VS Code Skill Package, Skill-Facing Tool References, SKILL.md Template (+8 more)

### Community 8 - "Community 8"
Cohesion: 0.0
Nodes (15): Copilot CLI, Delegate Return Contract, Manifest, Orchestration Audit Record, Plan Index, Repo Structure Block, Research Agent, Worktree Isolation (+7 more)

### Community 9 - "Community 9"
Cohesion: 0.0
Nodes (15): API Design Skill, API Pagination, API Rate Limiting, API Versioning, Backend Patterns Skill, Cache-Aside Pattern, Coding Standards Scope, Coding Standards Skill (+7 more)

### Community 10 - "Community 10"
Cohesion: 0.0
Nodes (14): Code Architect Agent, Code Explorer Agent, Doc Updater Agent, PR Test Analyzer Agent, Behavioral Test Coverage, Build Sequence, Code Exploration, Codemap Generation (+6 more)

### Community 11 - "Community 11"
Cohesion: 0.0
Nodes (13): Go, VS Code mcp.json Configuration, Official MCP SDK References, MCP Server, Node.js, Python, Rust, stdio Transport (+5 more)

### Community 12 - "Community 12"
Cohesion: 0.0
Nodes (11): Build Verification phase, Diff Review phase, gitnexus detect_changes, Lint Check phase, security-review skill, Security Scan phase, tdd-workflow skill, Test Suite phase (+3 more)

### Community 13 - "Community 13"
Cohesion: 0.0
Nodes (7): create_manifest_if_missing(), generate_next_task_id(), Orchestrator helper API moved into the orchestrator skill.  Provides lightweig, Generate a simple incremental task id by scanning the orchestration     history, If `manifest` is not a dict, generate a minimal manifest object.      The gene, validate_manifest(), validate_payload()

### Community 14 - "Community 14"
Cohesion: 0.0
Nodes (9): Bybit Authentication, Bybit Auto Update, Structured Operation Confirmation, Bybit Environment Modes, Bybit Module Router, Bybit Official Skill Documentation, Bybit Security Rules, Bybit Trading Skill (+1 more)

### Community 15 - "Community 15"
Cohesion: 0.0
Nodes (9): Agentic Workflow: Check Copilot Tool Name, Copilot Tool Snapshot extension, .vscode/copilot-tools.snapshot.json, Derived tool sets, Agentic Workflow: Export Copilot Tool Snapshot, Installed extension manifest scan, create-skill validator, Tool registry stabilization (+1 more)

### Community 16 - "Community 16"
Cohesion: 0.0
Nodes (8): E2E Runner Agent, TDD Guide Agent, 80%+ Test Coverage, Critical User Journeys, Flaky Test Control, Native VS Code Browser Tooling, Red-Green-Refactor Cycle, Test-First Development

### Community 17 - "Community 17"
Cohesion: 0.0
Nodes (8): Copilot Memory, Karpathy LLM OS Architecture, VS Code Memory Tool, Memory Vault, Karpathy LLM OS Principles, Memory in VS Code Agents, Memory Skill, Memory Vault Templates

### Community 18 - "Community 18"
Cohesion: 0.0
Nodes (6): build_plan_index(), extract_fenced(), extract_header_block(), extract_yaml_key(), lines_to_paths(), main()

### Community 19 - "Community 19"
Cohesion: 0.0
Nodes (7): Deep Research Workflow, Exa MCP, fetch_webpage Tool, Firecrawl MCP, Parallel Research Subagents, Research Report, deep-research SKILL

### Community 20 - "Community 20"
Cohesion: 0.0
Nodes (7): Copilot Chat debug log files, grep_search tool, main.jsonl, read_file tool, run_in_terminal tool, system_prompt_*.json files, Troubleshoot skill

### Community 21 - "Community 21"
Cohesion: 0.0
Nodes (6): Artifact Management, CI/CD Integration, Flaky Test Mitigation, Playwright E2E Testing, Page Object Model, e2e-testing SKILL

### Community 22 - "Community 22"
Cohesion: 0.0
Nodes (6): Capability Evals, Eval-Driven Development, Eval Harness, pass@k and pass^k Metrics, Regression Evals, Eval Harness Skill

### Community 23 - "Community 23"
Cohesion: 0.0
Nodes (4): TypeScript Reviewer Agent, Async Correctness, Type Safety, TypeScript and JavaScript Review

### Community 24 - "Community 24"
Cohesion: 0.0
Nodes (4): Security Reviewer Agent, OWASP Top 10 Review, Secrets Detection, security-review Skill

### Community 25 - "Community 25"
Cohesion: 0.0
Nodes (4): Performance Optimizer Agent, Bundle Optimization, Database and Network Optimization, Performance Profiling

### Community 26 - "Community 26"
Cohesion: 0.0
Nodes (3): Python Reviewer Agent, Python Code Review, Static Analysis Tools

### Community 27 - "Community 27"
Cohesion: 0.0
Nodes (3): Database Reviewer Agent, Operational Safety, PostgreSQL Review

### Community 28 - "Community 28"
Cohesion: 0.0
Nodes (3): Refactor Cleaner Agent, Dead Code Cleanup, Reference Verification

### Community 29 - "Community 29"
Cohesion: 0.0
Nodes (3): Agent Customization, Prompt File (.prompt.md), create-prompt SKILL

### Community 30 - "Community 30"
Cohesion: 0.0
Nodes (3): Hook, Instruction, create-hook SKILL

### Community 31 - "Community 31"
Cohesion: 0.0
Nodes (3): Frontend Development Patterns, React and Next.js User Interfaces, Frontend Patterns Skill

### Community 32 - "Community 32"
Cohesion: 0.0
Nodes (3): Quality Agent, RED Gate, TDD Workflow Skill

## Ambiguous Edges - Review These
- `Orchestrator Skill` → `Example Manifest (Patch)`  [AMBIGUOUS]
  .github/skills/orchestrator/SKILL.md · relation: points to example
- `Orchestrator Skill` → `Example Manifest (Full Content)`  [AMBIGUOUS]
  .github/skills/orchestrator/SKILL.md · relation: points to example
- `Example Manifest (Full Content)` → `Manifest Schema Reference`  [AMBIGUOUS]
  .github/skills/orchestrator/references/manifest_schema.md · relation: points to example
- `Example Manifest (Patch)` → `Manifest Schema Reference`  [AMBIGUOUS]
  .github/skills/orchestrator/references/manifest_schema.md · relation: points to example

## Knowledge Gaps
- **141 isolated node(s):** `Orchestrator helper API moved into the orchestrator skill.  Provides lightweig`, `Generate a simple incremental task id by scanning the orchestration     history`, `If `manifest` is not a dict, generate a minimal manifest object.      The gene`, `vscode`, `Local .venv Environment` (+136 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **4 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.