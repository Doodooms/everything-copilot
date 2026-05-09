# GitNexus MCP Server Setup for VS Code

## Prerequisites

- VS Code 1.99+ (MCP support added April 2025)
- Node.js 18+

## Add to .vscode/mcp.json

The `.vscode/mcp.json` file in this repo already contains the entry.
If adding manually:

```json
{
  "servers": {
    "gitnexus": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "gitnexus@latest", "mcp"],
      "env": {}
    }
  }
}
```

## Bootstrap the index

```
# Index the current repo:
npx gitnexus analyze

# Skip auto-written AGENTS.md (use copilot-instructions.md instead):
npx gitnexus analyze --skip-agents-md

# Generate per-cluster skills (port to .github/skills/ afterwards):
npx gitnexus analyze --skills
```

## Verify MCP server is running

Open VS Code command palette: `MCP: List Servers`
gitnexus should appear as connected.

In Copilot Chat, type `@gitnexus` or use the tool picker to access:
- `context`, `impact`, `query`, `detect_changes`, `rename`, etc.

## Refresh index

```
# After significant code changes:
npx gitnexus analyze --incremental

# Full reindex (takes longer, use after major refactors):
npx gitnexus analyze
```

## License

PolyForm Noncommercial: free for personal/research/non-commercial use.
Commercial license: contact founders@akonlabs.com
