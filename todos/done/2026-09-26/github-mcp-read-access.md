# GitHub MCP read-access check

## Result

- Read `README.md` from `Doodooms/everything-copilot` using `github-mcp-server-get_file_contents`.
- The GitHub MCP request succeeded; file SHA: `64ceb4596960d4bc138885679b0b6d4d8593dd45`.
- This confirms the active MCP authorization can read this repository. The tool response does not identify the principal, so it does not independently prove that the GitHub App, rather than another configured identity, supplied the authorization.
- No writes, local Git/GH/SSH/curl fallback, or credential inspection were performed.

