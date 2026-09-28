# GitHub App authorization-boundary test

## Status

**Blocked / not verified.** Do not count the previous negative attempt as a passing authorization-boundary test.

## Evidence already collected

- Positive read access to `Doodooms/everything-copilot/README.md` succeeded using the GitHub MCP tool. Details are in [github-mcp-read-access.md](../../done/2026-09-26/github-mcp-read-access.md).
- The attempted negative target was the literal placeholder `Doodooms/<REPOSITORY_NOT_GRANTED_TO_THE_GITHUB_APP>`.
- `github-mcp-server-get_file_contents` returned:
  `MCP server 'github-mcp-server': failed to resolve git reference: failed to get repository info: GET https://api.github.com/repos/Doodooms/%3CREPOSITORY_NOT_GRANTED_TO_THE_GITHUB_APP%3E: 404 Not Found []`
- Because that repository name was a placeholder and not confirmed to identify an existing repository, the 404 does **not** prove the GitHub App lacks access. The previous `PASS` classification was premature.

## Next action for Codex

1. Use only the GitHub MCP tool `github-mcp-server-get_file_contents`; do not use local files, `git`, `gh`, SSH, curl, web search, or another fallback.
2. Test `README.md` on a real, existing `Doodooms` repository that is known not to be granted to the GitHub App.
3. If no such repository name is supplied or otherwise authoritatively known, stop and request one; do not guess.
4. Report the exact MCP result/error. Mark **PASS** only when access is denied for that known-existing repository; mark **FAIL** if its content is returned.
5. Do not inspect credentials or perform writes.

## Handoff context

- Harness adapter phase 1 is complete; see [harness-adapters-phase1.md](../../done/2026-09-26/harness-adapters-phase1.md).
- Preserve the existing dirty/untracked worktree state. No files were staged or committed for these MCP checks.
