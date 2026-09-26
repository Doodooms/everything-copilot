# Original Specification

## Raw intent

Add a focused Researcher capability for evidence gathering on GitHub, distinct from local code-path exploration and broad multi-source synthesis.

## Normalized requirements

- Resolve the canonical owner/repository and the requested evidence question.
- Use GitHub's available read-only repository, commit, release, issue, pull-request, and code-search tools.
- Pin findings to a commit, release/tag, issue, or pull-request revision and give a direct source location.
- Distinguish observed repository evidence from issue discussion, inference, and recommendation.
- Return concise findings with applicability, uncertainty, and source provenance.

## Constraints

- Research only public or explicitly authorized repositories.
- Do not use `execute`, credentials, or GitHub mutation capabilities.
- Do not implement, modify, stage, or commit repository content.
- Do not treat a search result or issue comment alone as proof of shipped behavior.

## Resolved decisions

- Package name: `github-evidence-research`.
- Owner: the existing evidence-only Researcher agent.
- Tool boundary: exact, locally available GitHub MCP read operations; no private-GitHub integration is added.
- Date: 2026-09-24.
