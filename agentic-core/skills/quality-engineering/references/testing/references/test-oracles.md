# Test oracles

Define an independent expected result from the contract before choosing assertions.

- Prefer externally observable output, persisted state, or a stable public interaction.
- Use expected values that DO NOT repeat the implementation's calculation.
- A useful test must distinguish correct behavior from at least one plausible defect.
- When the contract is ambiguous, return the ambiguity to its specification owner instead of encoding an assumption.
