---
id: paper-research
description: 'Apply the paper-research method: evidence from journal/conference papers,
  preprints, working papers, methods, results, and limitations.'
invoke_for:
- evidence from journal/conference papers, preprints, working papers, methods, results,
  and limitations
avoid_for:
- repository history, versioned API documentation, implementation, or broad synthesis
  across unrelated evidence classes
references: []
---

## Step 1 - Define the research claim.

1. Extract the specific claim or decision the paper evidence must inform, including the population, context, outcome, or comparison that materially limits applicability.
2. Use #tool:web to locate candidate primary records and #tool:browser to inspect the relevant paper or repository page.
3. When authoring or materially repairing this package, consult the [original specification](../references/paper-research/references/original-spec.md) as provenance only.

## Step 2 - Verify publication and methodological evidence.

1. Confirm the title, authors, year, DOI or stable identifier, venue, publication state, and exact version/date examined.
2. Inspect the relevant methods and results, not only a search snippet or abstract, when the claim depends on study design or quantitative evidence.
3. Capture the reported population, method, measured outcome, limitations, conflicts or uncertainty, and any material disagreement with other primary sources.
   - If full text, review status, or a needed methodological detail is unavailable, mark the result `partial`; do not infer it.

## Step 3 - Return a claim-linked evidence packet.

1. Return `status: success | partial | failed`, the supported question/artifact, claim-level findings, source citation/URL and version, publication state, relevant method/result, applicability, fact-versus-inference distinction, and uncertainty.
2. Stop when the named claim is supported or its evidence gap is explicit; do not turn a focused question into an unbounded literature survey.
