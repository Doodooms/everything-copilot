---
name: paper-research
description: "WHAT: Evaluate scholarly papers and research literature for a bounded technical or scientific claim. USE FOR: evidence from journal/conference papers, preprints, working papers, methods, results, and limitations. DO NOT USE FOR: repository history, versioned API documentation, implementation, or broad synthesis across unrelated evidence classes."
user-invocable: false
metadata:
  creation-date: 2026-09-24
  creator: Doodooms
---

<definitions>

- **publication state**: The paper's evidenced status, such as peer-reviewed publication, preprint, working paper, or other public manuscript.
- **paper version**: The exact published or repository-hosted version examined, identified by DOI, stable URL, version number, or revision date.

</definitions>

<rules>

- MUST identify the primary paper record and version examined; SHOULD prefer publisher, DOI registry, recognized repository, or author-hosted source.
- MUST distinguish peer-reviewed publication from preprint or working-paper status using explicit evidence; citation count, venue reputation, and search ranking are not proof of peer review.
- MUST represent methods, population/sample, measured outcome, limitations, and applicability accurately.
- MUST separate reported results from inference and MUST NOT overstate causality, consensus, or generalizability.
- MUST cite the source for each material claim and expose missing full text or unresolved publication status.
- SHOULD retrieve only as much source material as needed to assess the named claim; no fixed paper or source-count quota applies.

</rules>

<admission>

## ACCEPT

- A bounded question about the evidence, method, result, or limitation of scholarly research.
- A literature comparison supporting a named technical, scientific, or standards-related decision.

## REJECT

- GitHub repository/code/history evidence → `github-evidence-research`.
- Versioned library, SDK, API, or product documentation → `versioned-documentation-research`.
- Broad multi-source evidence synthesis → `deep-research`.
- Implementation or product decisions → `implementer` or `orchestrate`, as appropriate.

For REJECT, return exactly:

```json
{"status":"rejected","skill":"paper-research","reason":"<concise reason>","routing":"<route or null>"}
```

</admission>

<workflow>

## Step 1 - Define the research claim.

1. Extract the specific claim or decision the paper evidence must inform, including the population, context, outcome, or comparison that materially limits applicability.
2. Use #tool:web to locate candidate primary records and #tool:browser to inspect the relevant paper or repository page.
3. When authoring or materially repairing this package, consult the [original specification](./references/original-spec.md) as provenance only.

## Step 2 - Verify publication and methodological evidence.

1. Confirm the title, authors, year, DOI or stable identifier, venue, publication state, and exact version/date examined.
2. Inspect the relevant methods and results, not only a search snippet or abstract, when the claim depends on study design or quantitative evidence.
3. Capture the reported population, method, measured outcome, limitations, conflicts or uncertainty, and any material disagreement with other primary sources.
   - If full text, review status, or a needed methodological detail is unavailable, mark the result `partial`; do not infer it.

## Step 3 - Return a claim-linked evidence packet.

1. Return `status: success | partial | failed`, the supported question/artifact, claim-level findings, source citation/URL and version, publication state, relevant method/result, applicability, fact-versus-inference distinction, and uncertainty.
2. Stop when the named claim is supported or its evidence gap is explicit; do not turn a focused question into an unbounded literature survey.

</workflow>