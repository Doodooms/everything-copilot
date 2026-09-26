# State models

Represent valid state and transitions so invalid combinations are difficult to express.

- Enumerate states, events, guards, effects, terminal states, and invariants before selecting syntax.
- Use explicit variants or a transition table when several booleans admit impossible combinations or ordering changes behavior.
- Keep simple values simple; a state machine is not useful when there is no meaningful lifecycle.
- Define how invalid transitions fail when that behavior is externally observable.
