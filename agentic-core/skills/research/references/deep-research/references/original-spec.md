# Original Specification

## Raw intent

Retain `deep-research` as the broad evidence-synthesis workflow and compose focused Researcher capabilities without losing the parent workflow or its caller's task.

## Normalized requirements

- Replace unsupported Firecrawl, Exa, `fetch_webpage`, and research-subagent assumptions with tools actually available to Researcher.
- Route narrow GitHub, paper, and versioned-documentation requests to their focused child skills.
- For broad questions, call only the applicable child skills, passing bounded inputs, explicit expected fields, constraints, and the exact resume point.
- Validate every child status and required field before synthesizing; report partial or failed evidence explicitly.
- Preserve source attribution, disagreement, version/revision, applicability, uncertainty, and decision implications.
- Represent each composed use case as a finite Mermaid DAG with explicit joins and parent resumption.

## Constraints

- Do not impose generic clarification questions, arbitrary source counts, fixed recency windows, or unsupported tool/subagent use.
- Do not change the caller's acceptance criteria or make its product/architecture decision.
- Do not create recursive skill calls or retry loops.

## Resolved decisions

- Keep the package name `deep-research`.
- Parent owner: Researcher; child capabilities: `github-evidence-research`, `paper-research`, and `versioned-documentation-research`.
- The Researcher output contract remains the aggregate research packet.
- Date: 2026-09-24.
