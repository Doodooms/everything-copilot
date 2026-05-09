---
name: search-first
description: "Research-before-coding workflow. Search for existing tools, libraries, and patterns before writing custom code. Prevents reinventing the wheel and reduces dependency bloat. Invokes the researcher agent for non-trivial decisions. Derived from Everything Claude Code (https://github.com/affaan-m/everything-claude-code)."
user-invocable: false
---

# Search-First -- Research Before You Code

Systematizes the "search for existing solutions before implementing" workflow.
Before writing any utility, helper, or custom integration: search first.

## When to Activate

- Starting a new feature that likely has existing solutions
- Adding a dependency or integration
- When the user asks "add X functionality" and you are about to write code
- Before creating a new utility, helper, or abstraction
- Before spinning up an MCP server -- one may already exist

## Workflow

```
1. NEED ANALYSIS
   Define what functionality is needed
   Identify language/framework constraints
        |
2. PARALLEL SEARCH
   +-- Package registry (npm / PyPI / crates.io / pkg.go.dev)
   +-- MCP server catalog
   +-- .github/skills/ (existing workspace skills)
   +-- GitHub code search for maintained OSS
        |
3. EVALUATE
   Score candidates (functionality, maintenance, community, docs, license, deps)
        |
4. DECIDE
   +-- Adopt   (exact match, well-maintained, MIT/Apache)
   +-- Extend  (partial match, write thin wrapper)
   +-- Compose (multiple weak matches, combine 2-3 small packages)
   +-- Build   (nothing suitable, write custom informed by research)
        |
5. IMPLEMENT
   Install package / configure MCP / write minimal custom code
```

## Decision Matrix

| Signal | Action |
|--------|--------|
| Exact match, well-maintained, MIT/Apache | Adopt -- install and use directly |
| Partial match, good foundation | Extend -- install + write thin wrapper |
| Multiple weak matches | Compose -- combine 2-3 small packages |
| Nothing suitable found | Build -- write custom, but informed by research |

## How to Use

### Quick Mode (inline, for simple decisions)

Before writing a utility, mentally check:

0. Does this already exist in the repo? Search with grep_search or semantic_search first.
1. Is this a common problem? Search the package registry.
2. Is there an MCP server for this? Check `.vscode/mcp.json` and search.
3. Is there a skill for this? Check `.github/skills/`.
4. Is there a maintained OSS implementation? Search GitHub.

### Full Mode (for significant decisions)

For non-trivial functionality, launch the researcher subagent:

```
Task for researcher agent:
  Research existing tools for: [DESCRIPTION]
  Language/framework: [LANG]
  Constraints: [ANY CONSTRAINTS]
  Search: npm/PyPI/crates, MCP servers, existing workspace skills, GitHub
  Return: Structured comparison table with recommendation and decision (Adopt/Extend/Build)
```

## Search Shortcuts by Category

### Development Tooling
- Linting: `eslint`, `ruff`, `textlint`, `markdownlint`
- Formatting: `prettier`, `black`, `gofmt`
- Testing: `jest`, `pytest`, `go test`
- Pre-commit hooks: `husky`, `lint-staged`, `pre-commit`

### AI/LLM Integration
- Claude SDK: check Context7 for latest docs
- Prompt management: check MCP servers first
- Document processing: `unstructured`, `pdfplumber`, `mammoth`

### Data and APIs
- HTTP clients: `httpx` (Python), `ky`/`got` (Node)
- Validation: `zod` (TypeScript), `pydantic` (Python), `serde` (Rust)
- Database: check for MCP servers first

### Content and Publishing
- Markdown processing: `remark`, `unified`, `markdown-it`
- Image optimization: `sharp`, `imagemin`

### CLI Tools
- CLI frameworks: `typer` (Python), `click` (Python), `commander` (Node)
- Argument parsing: argparse (Python stdlib), `clap` (Rust)

## Integration Points

### With planner agent
The planner should invoke search-first before Phase 1 (Architecture Review):
- Researcher identifies available tools
- Planner incorporates them into the implementation plan
- Avoids reinventing the wheel in the plan

### With research agent
Delegate full research mode to the research agent for non-trivial decisions.
Return a structured comparison with a final recommendation.

### With iterative-retrieval skill
Combine for progressive discovery:
- Cycle 1: Broad search (package registry, MCP catalog)
- Cycle 2: Evaluate top candidates in detail
- Cycle 3: Test compatibility with project constraints

## Examples

### Example 1: Dead link checking
```
Need: Check markdown files for broken links
Search: npm "markdown dead link checker"
Found: textlint-rule-no-dead-link (score: 9/10)
Decision: ADOPT -- npm install textlint-rule-no-dead-link
Result: Zero custom code, battle-tested solution
```

### Example 2: HTTP client with retry
```
Need: Resilient HTTP client with retries and timeout handling
Search: npm "http client retry", PyPI "httpx retry"
Found: got (Node) with retry plugin, httpx (Python) with built-in retry
Decision: ADOPT -- use httpx directly with retry config
Result: Zero custom code, production-proven library
```

### Example 3: Config file linting
```
Need: Validate project config files against a schema
Search: npm "config linter schema", "json schema validator cli"
Found: ajv-cli (score: 8/10)
Decision: ADOPT + EXTEND -- install ajv-cli, write project-specific schema
Result: 1 package + 1 schema file, no custom validation logic
```

## Anti-Patterns

- **Jumping to code**: Writing a utility without checking if one exists
- **Ignoring MCP**: Not checking if an MCP server already provides the capability
- **Over-customizing**: Wrapping a library so heavily it loses its benefits
- **Dependency bloat**: Installing a massive package for one small feature (check size)
- **License blindness**: Installing a package with an incompatible license