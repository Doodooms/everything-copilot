# Original Specification

## Raw intent

Use evidence-based RED-GREEN-REFACTOR to change executable behavior against an approved acceptance criterion.

## Normalized requirements

- Establish the repository's test boundary and observable acceptance criterion.
- Prove a valid RED before production changes, achieve GREEN with the same target, and refactor only after GREEN.
- Use behavior-focused tests through the relevant interface and test doubles only where they preserve the contract being evaluated.
- Run project quality gates; use coverage when project policy or changed behavior makes it useful.

## Subsequent user-directed refinements

- The imported Codex test notes were used to improve test-seam, independent-expectation, and external-boundary-double guidance; their examples and host metadata were not copied.
- Removed the universal 80% coverage requirement because it was not tied to project policy or observable behavior. Coverage is evidence for unexercised paths, not a stand-alone acceptance criterion.
- Removed the absent `references/__routing_probe__.md` gate; it could block valid TDD work without contributing test evidence.
- Date: 2026-09-24.
