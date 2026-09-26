# Original Specification

## Raw intent

Add a focused Researcher capability for library, SDK, API, and product documentation that matches the version actually used by the task.

## Normalized requirements

- Resolve the product/package and exact version from the approved request, repository manifest, lockfile, or target code.
- Prefer official, version-matched documentation and record the exact page, section, and URL.
- Use release notes or changelogs to explain differences when exact-version documentation is unavailable.
- Mark the nearest-version fallback and its compatibility uncertainty explicitly; do not silently substitute `latest`.
- Return only behavior and compatibility evidence relevant to the named question.

## Constraints

- Research only; do not edit product code or documentation.
- Do not treat search snippets or an unversioned page as exact-version evidence.
- Do not implement, modify, stage, or commit repository content.

## Resolved decisions

- Package name: `versioned-documentation-research`.
- Owner: the existing evidence-only Researcher agent.
- Search and source inspection use the available `web` and `browser` tools.
- Date: 2026-09-24.
