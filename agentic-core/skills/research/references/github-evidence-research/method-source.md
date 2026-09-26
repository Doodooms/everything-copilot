---
name: github-evidence-research
description: "WHAT: Gather revision-pinned evidence from GitHub repositories, commits, releases, issues, and pull requests. USE FOR: public or explicitly authorized repository archaeology, code/release history, and issue or PR context. DO NOT USE FOR: local execution-path tracing, implementation, repository mutation, or broad cross-source synthesis."
user-invocable: false
metadata:
  creation-date: 2026-09-24
  creator: Doodooms
---

<definitions>

- **repository identity**: The canonical GitHub owner and repository confirmed for the evidence request.
- **pinned evidence**: Repository content tied to an immutable commit SHA, or discussion/release evidence tied to its exact GitHub resource.

</definitions>

<rules>

- MUST research only public or explicitly authorized repositories.
- MUST use the locally available read-only GitHub tools; MUST NOT use shell execution, credentials, write tools, or mutation APIs.
- MUST pin code and release claims to a commit SHA or exact release/tag and cite a direct permalink with path and line range where available.
- MUST distinguish shipped code from issue/PR discussion, user claims, inference, and recommendation.
- MUST state unresolved repository, revision, access, or provenance uncertainty; MUST NOT treat a search snippet as verified evidence.
- SHOULD prefer the target repository's source and release artifacts over secondary summaries.

</rules>

<admission>

## ACCEPT

- A bounded question about a named GitHub repository's code, history, releases, issues, or pull requests.
- Repository evidence needed to support a specified decision, requirement, acceptance criterion, task, or technical claim.

## REJECT

- Local workspace behavior or call-path tracing → `code-exploration`.
- Broad synthesis across GitHub and other evidence classes → `deep-research`.
- Code changes or repository mutations → `implementer` or `orchestrate`, as appropriate.
- A private repository without explicit authorization or access → `researcher` for clarification before any access attempt.

For REJECT, return exactly:

```json
{"status":"rejected","skill":"github-evidence-research","reason":"<concise reason>","routing":"<route or null>"}
```

</admission>

<workflow>

## Step 1 - Resolve repository and revision.

1. Confirm the repository identity and the exact question; use #tool:mcp_github_mcp_se_search_repositories only to disambiguate an unspecified public repository.
2. Pin the relevant branch, commit, release, issue, or pull request before drawing conclusions.
   - Use #tool:mcp_github_mcp_se_get_commit or #tool:mcp_github_mcp_se_list_commits or #tool:mcp_github_mcp_se_list_releases to identify stable revision evidence.
   - If access, repository identity, or revision cannot be resolved, return `partial` with the missing fact; do not silently switch targets.
3. When authoring or materially repairing this package, consult the [original specification](./references/original-spec.md) as provenance only.

## Step 2 - Retrieve and assess evidence.

1. Use #tool:mcp_github_mcp_se_search_code to locate candidate code, then use #tool:mcp_github_mcp_se_get_file_contents with the pinned revision to inspect the authoritative content.
2. For discussion context, use #tool:mcp_github_mcp_se_search_issues and #tool:mcp_github_mcp_se_issue_read and #tool:mcp_github_mcp_se_search_pull_requests and #tool:mcp_github_mcp_se_pull_request_read; label discussion as discussion, not shipped behavior.
3. Record the exact source URL/permalink, repository, SHA/ref, path and line range or resource number, observation date, and whether each finding is fact or inference.

## Step 3 - Return the evidence packet.

1. Return `status: success | partial | failed`, the research question and supported artifact/revision, concise findings, sources/permalinks, revision identifiers, applicability, uncertainty, and decision implications.
2. Stop when the named question is answered or when missing evidence blocks a reliable answer; do not pad the packet with unrelated repository history.

</workflow>