# Original specification

Create one discoverable `testing` subdomain whose shared method improves test oracles, test-level selection, boundary analysis, test-double choices, and behavioral sensitivity. Keep `tdd` as the RED-GREEN-REFACTOR lifecycle and `adversarial-testing` as independent post-implementation falsification.

Route only three evidence-backed procedures: test design, browser/end-to-end testing, and review of an existing test surface. Do not add speculative property-based, integration, stateful, or concurrency workflow files; extend the catalogue only when a concrete procedure and evidence justify it.

The former `test-coverage-review` and `e2e-testing` packages supplied the review and browser-testing material. The latter identified its source as Everything Claude Code (<https://github.com/affaan-m/everything-claude-code>); this package retains only adapted testing principles, not its long illustrative code/configuration examples.

The package's canonical architecture is one skill → immediate workflows → point-of-need references. No separate globally discoverable `test-design`, `test-quality-review`, or `e2e-testing` skill is introduced.
