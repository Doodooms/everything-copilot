# Architecture Design Guide

Use this guide when the workflow needs a reminder of the legacy architecture-design responsibilities.

- Start from existing repository patterns before inventing new abstractions.
- Identify cohesive responsibilities, interfaces, dependencies, and build order per module.
- Capture only the tradeoffs that materially affect the design choice.
- Make risks, assumptions, and non-goals explicit.
- Keep the brief implementable, not theoretical.
- For existing architecture, use repeated change, duplicated decisions, caller complexity, defects, and test difficulty as evidence; file size alone is not a design defect.
- A smaller interface is useful only when it hides coherent behavior and reduces caller knowledge. Do not create a seam merely to add a fake, wrapper, or future option.
- Compare the proposed structure with the current one: what behavior moves behind the interface, what callers stop coordinating, and where contract tests should observe results.