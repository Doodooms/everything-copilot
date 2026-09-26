---
name: versioned-documentation-research
description: "WHAT: Find authoritative technical documentation matched to the version used by a codebase or task. USE FOR: library, SDK, API, language, and product behavior or compatibility questions tied to a version. DO NOT USE FOR: GitHub source/history research, scholarly evidence, implementation, or unversioned claims presented as exact."
user-invocable: false
metadata:
  creation-date: 2026-09-24
  creator: Doodooms
---

<definitions>

- **target version**: The exact package, API, language, or product version the approved task uses or asks about.
- **version-matched evidence**: An official documentation page or release artifact that explicitly applies to the target version.

</definitions>

<rules>

- MUST establish the target product and version from the approved task or repository manifest, lockfile, or call site before making version-specific claims.
- MUST prefer official, version-matched documentation and cite the exact URL, page/section, and version.
- SHOULD use Context7 to locate and query library documentation when its server is available; MUST verify version-sensitive claims against the official source it identifies.
- MUST use release notes or changelogs to establish behavior changes when the exact-version reference page is unavailable.
- MUST label `latest`, adjacent-version, or third-party documentation as a fallback and state its applicability uncertainty; MUST NOT silently substitute it.
- MUST distinguish documentation statements from observed repository usage and inference.
- MUST NOT edit product code or documentation.

</rules>

<admission>

## ACCEPT

- A bounded library, SDK, API, language, or product question whose answer depends on a specific version or documented release behavior.
- Compatibility or migration evidence needed by a named task, requirement, acceptance criterion, or decision.

## REJECT

- GitHub code, commit, issue, release, or pull-request evidence → `github-evidence-research`.
- Scholarly research evidence → `paper-research`.
- Broad synthesis across several evidence classes → `deep-research`.
- Product behavior change or documentation edit → `implementer` or `documentation-sync`, as appropriate.

For REJECT, return exactly:

```json
{"status":"rejected","skill":"versioned-documentation-research","reason":"<concise reason>","routing":"<route or null>"}
```

</admission>

<workflow>

## Step 1 - Resolve the target product and version.

1. Read the approved question and inspect the relevant project manifest, lockfile, or usage site with #tool:read or #tool:search when the repository is available.
2. Record the product/package, target version, API surface, runtime/platform constraints, and supported artifact or decision.
   - If the version is not available and materially changes the answer, return `partial` with the missing version; do not assume `latest`.
3. When authoring or materially repairing this package, consult the [original specification](./references/original-spec.md) as provenance only.

## Step 2 - Inspect authoritative, version-matched sources.

1. When available, use #tool:mcp_context7_resolve_library_id to resolve the canonical library, then #tool:mcp_context7_query_docs with the target version and narrow API question.
2. Use #tool:web to locate and #tool:browser to inspect the official versioned page or release source identified by Context7; Context7 snippets alone are not sufficient evidence.
3. If Context7 is unavailable, has no exact version, or returns no traceable official source, use the official documentation and release history directly and label any version fallback.
4. Record the exact URL, product/version, page/section, observation date, relevant statement or example, platform applicability, and any fallback or contradiction.

## Step 3 - Return version-scoped findings.

1. Return `status: success | partial | failed`, the supported question/artifact, concise findings, exact version and source links, evidence location, applicability, fact-versus-inference distinction, and uncertainty.
2. Stop when the required documented behavior or compatibility fact is established; do not generalize beyond the cited version.

</workflow>