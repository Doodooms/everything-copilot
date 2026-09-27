---
id: github-evidence-research
description: 'Apply the github-evidence-research method: public or explicitly authorized
  repository archaeology, code/release history, and issue or PR context.'
invoke_for:
- public or explicitly authorized repository archaeology, code/release history, and
  issue or PR context
avoid_for:
- local execution-path tracing, implementation, repository mutation, or broad cross-source
  synthesis
references: []
---
<critical_rules>
- MUST keep work within this subskill’s declared scope and its specific safety or authority constraints.
- MUST NOT replace the parent domain skill’s admission, global routing, or authority boundaries.
</critical_rules>

<general_rules>
- SHOULD load listed references only at the procedure step that needs them.
- MAY report unavailable evidence or unresolved decisions as unknown.
</general_rules>

<risk_assessment>
Consume the Orchestrator-assigned `risk_level` through the parent domain skill; MUST NOT reclassify or downgrade it. SHOULD escalate only when new evidence materially increases risk. Scale evidence depth, not authority or approvals.
</risk_assessment>

<rules>
- MUST follow this selected subskill only within its declared procedure and scope.
- MUST NOT replace the parent domain skill’s admission, global routing, or authority boundaries.
- MUST return the result, evidence, remaining unknowns, risks, and status required by this procedure.
</rules>

<workflow>
## Step 1 - Resolve repository and revision.

1. DO consume the assigned `risk_level` inherited from the parent domain skill before applying this procedure; then For App-scoped repositories, use the Core plugin's `github-mcp-server` MCP tools; the host launches the official stdio server in a dedicated Docker container. If the tools are missing or access is denied, report the exact error and stop that evidence request; do not fall back to local Git/GH credentials.
2. Confirm the repository identity and the exact question; use #tool:mcp_github_mcp_se_search_repositories only to disambiguate an unspecified public repository.
3. Pin the relevant branch, commit, release, issue, or pull request before drawing conclusions.
   - Use #tool:mcp_github_mcp_se_get_commit or #tool:mcp_github_mcp_se_list_commits or #tool:mcp_github_mcp_se_list_releases to identify stable revision evidence.
   - If access, repository identity, or revision cannot be resolved, return `partial` with the missing fact; do not silently switch targets.
4. When authoring or materially repairing this package, consult the [original specification](../references/github-evidence-research/references/original-spec.md) as provenance only.

## Step 2 - Retrieve and assess evidence.

1. Use #tool:mcp_github_mcp_se_search_code to locate candidate code, then use #tool:mcp_github_mcp_se_get_file_contents with the pinned revision to inspect the authoritative content.
2. For discussion context, use #tool:mcp_github_mcp_se_search_issues and #tool:mcp_github_mcp_se_issue_read and #tool:mcp_github_mcp_se_search_pull_requests and #tool:mcp_github_mcp_se_pull_request_read to gather context; label discussion as discussion, not shipped behavior.
3. Record the exact source URL/permalink, repository, SHA/ref, path and line range or resource number, observation date, and whether each finding is fact or inference.

## Step 3 - Return the evidence packet.

1. Return `status: success | partial | failed`, the research question and supported artifact/revision, concise findings, sources/permalinks, revision identifiers, applicability, uncertainty, and decision implications.
2. Stop when the named question is answered or when missing evidence blocks a reliable answer; do not pad the packet with unrelated repository history.
</workflow>
