# Prototype shapes

Choose one form from the question. Keep the artifact runnable with the repository's existing tooling or as a small standalone file; avoid adding a framework or persistent storage solely for the prototype.

## State or logic question

- Model the behavior with a small reducer, state transition table, or pure functions.
- Show the current state in domain language after each action.
- Include the happy path and only the edge cases that distinguish the competing interpretations.
- Keep UI controls as a thin shell around the behavior being evaluated.

## UI or interaction question

- Compare a small number of meaningfully different structures using the same data and task.
- Keep the demo clearly separate from a production route unless that route change is explicitly approved and safely gated for development.
- Avoid real backend mutations; use read-only or local sample data.
- Make the differences and evaluation question obvious to the viewer.

## Handoff

The durable output is the answer to the question and the evidence that supports it. Preserve the prototype only when the approved task explicitly requires an artifact; otherwise leave it out of production paths and return it for the Orchestrator's lifecycle decision.
