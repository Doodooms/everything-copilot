# Test levels

Choose the lowest level that still observes the behavior and boundary named by the contract.

- Use a unit-level check for deterministic local logic with a clear interface.
- Use an integration check when persistence, a protocol, or a component boundary is material to the behavior.
- Use a browser or end-to-end check only when the full user journey or rendered interaction is part of the contract.
- MUST NOT replace a cheap, deterministic, materially important real boundary with a mock.
