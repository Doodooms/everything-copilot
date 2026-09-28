# Skill authoring patterns

## Place each kind of content at the right level

The hierarchy is `Agent → Skill → Workflow → Reference / Asset / Script`.

| Layer | Main question | Put here | Keep out |
| --- | --- | --- | --- |
| Agent | Which bounded role owns this work? | Role, authority, handoff contract | Domain procedure duplicated from a skill |
| Skill | Should this skill own the request, and which procedure applies? | Admission, routing, essential shared invariants and authority boundaries | Tutorials, SDK details, long examples, case-specific procedure |
| Workflow | What ordered actions produce the requested result? | Minimal, observable, domain-specific sequence | A second copy of the detailed knowledge needed by one step |
| Reference | How should a selected step be done well? | Patterns, tradeoffs, edge cases, failure modes, rationale, versioned behavior | A separately invocable or hidden procedure |
| Asset | What can be copied and adapted? | Templates, schemas, fixtures, examples, canonical skeletons | Instructions that only explain what to do next |
| Script | What can deterministic machinery verify? | Structural checks, schema/reference validation, generated-output checks | Judgments that require semantic review |

Use the distinction `next action → workflow`, `how to do it well → reference`, `copy/adapt → asset`, and `mechanically verifiable → script`. A reference may be rich; it is the lazy-loaded expertise layer. Keep point-of-need links in the workflow step that consumes each support file.

## Preserve useful knowledge during normalization

Refactoring a skill into workflows MUST preserve useful domain knowledge, examples, assets, and deterministic scripts unless they are obsolete, incorrect, duplicated, or demonstrably unnecessary. Moving procedure out of a monolithic skill is not justification for deleting its supporting expertise.

When moving content, classify it before editing:

- procedure → an immediate workflow;
- domain knowledge, examples, tradeoffs, or failure modes → a targeted reference;
- copyable implementation or configuration → an asset;
- repeatable mechanical invariant → a script.

Inspect relevant history or source material when a migrated skill appears unusually thin. Revalidate historical API, SDK, protocol, and host details against the exact currently supported contract before carrying them forward. Preserve useful concepts while replacing stale examples; keep provenance files as provenance rather than loading them as runtime procedure.

## Use examples to resolve ambiguity

Use examples when they remove ambiguity that prose alone leaves unresolved. Prefer compact GOOD/BAD pairs in lazily loaded references for important behavioral distinctions and plausible failure modes. Put examples in references or assets unless they are essential to admission or routing. Keep each example aligned with the current supported contract and exact API/version; a stale example is worse than no example. Do not remove a useful example merely because its procedure moved into a workflow.

Do not impose example counts, reference counts, or a fixed support-file quota. Add support only when it is useful at a real step. Use real, version-verified code when an API is shown; otherwise make a conceptual contrast explicit and avoid pseudocode that looks like a supported API.

## Keep routing and validation deterministic

- Keep `description` as the global discovery surface; put only shared admission and essential invariants in `SKILL.md`, and each distinct same-domain procedure in an immediate workflow.
- A selected workflow stays concise, ordered, and observable. It points to the exact reference, asset, or script needed at that step rather than front-loading every detail.
- Use `MUST`/`MUST NOT` for invariants, `SHOULD`/`SHOULD NOT` for preferences, `MAY` for optional behavior, and `DO`/`DO NOT` for local actions.
- Use ordered lists for procedure and tables only to compare matching dimensions.
- Use exact `#tool:` and `#file:` markers only in active skill, agent, or prompt bodies. Support Markdown uses ordinary links and tool names.
- For agent/skill composition, pass bounded objective, inputs, constraints, expected output, and resume point; validate the child's return before resuming.
- Prefer deterministic validation for file paths, schemas, links, IDs, and generated output. Keep semantic quality judgments with the reviewer; never enforce arbitrary counts as a substitute.

```text
Weak discovery: API helper.
Useful discovery: WHAT: [domain capability]. USE FOR: [matching work]. DO NOT USE FOR: [adjacent work].
```

```text
GOOD: A step names the evidence to inspect and links to the version-matched reference for implementation detail.
BAD: A workflow repeats every SDK example, or a refactor deletes useful examples without checking their current validity.
```
