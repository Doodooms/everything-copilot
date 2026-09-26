# Original Specification

## Raw intent

Add a focused Researcher capability for scholarly papers and research literature, preserving source status and methodological limitations.

## Normalized requirements

- Search for the primary paper record and a stable identifier or canonical source URL.
- Record title, authors, publication year, venue, DOI or preprint identifier, and the version examined when available.
- Distinguish peer-reviewed publication, preprint, working paper, and other publication states without inferring review status from citations or venue reputation.
- Inspect methods, sample, results, limitations, and applicability to the requested claim.
- Return claim-level citations, uncertainty, and fact-versus-inference distinctions.

## Constraints

- Prefer primary publisher, repository, or author sources over summaries.
- Do not overstate causality, generalizability, or consensus.
- Do not implement, modify, stage, or commit repository content.
- Do not impose an arbitrary paper or source-count quota.

## Resolved decisions

- Package name: `paper-research`.
- Owner: the existing evidence-only Researcher agent.
- Search and source inspection use the available `web` and `browser` tools.
- Date: 2026-09-24.
