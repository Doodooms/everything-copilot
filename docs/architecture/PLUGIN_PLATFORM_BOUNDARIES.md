# Plugin Platform ownership and projection

This is the active ownership decision for the Plugin Platform convergence, effective 2026-10-03. It clarifies the current architecture without rewriting historical implementation reports.

## Repository boundaries

- `factory/` owns deterministic, content-neutral plugin parsing, validation, projection, packaging, and provenance. Its projectors accept an explicit source plugin path and must not contain plugin business content or hardcoded machine paths.
- `agentic-core/` is the canonical self-hosted Agent Plugin. It owns portable Agentic Core agents, skills (including `plugin-engineering`), MCP definitions, and the packaged runtime compatibility surfaces required to run standalone.
- `expertise/` and `harness_factory/` remain distinct tools with their existing responsibilities. Expertise Pack IR and target compilers are not a substitute for full Agent Plugin projection.
- The build dependency points from Factory to Agentic Core: Factory projects the source plugin. Agentic Core runtime code does not import Factory at runtime.

The Codex and Copilot compatibility entrypoints packaged in Agentic Core remain while the standalone consumers require them and tests exercise them. Their existence does not transfer projector ownership back from Factory. Replace or remove a packaged runtime copy only after reproduction, provenance comparison, and consumer tests prove the replacement.

## Projection and semantic changes

Reprojection rebuilds target files from an unchanged canonical plugin when projector code or parameters change. It does not optimize or semantically edit the source plugin. Optimization is a separate workflow: analyze a canonical plugin, propose and approve semantic changes, update its source, validate it, then rebuild target projections and evaluate the changed behavior.

Codex, Copilot, and Claude have different native capabilities. Projectors must preserve equivalent behavior, mark adaptations, and report dropped or unsupported semantics. Projection provenance is emitted outside target-native manifests and identifies the plugin, target, projector, parameters, exact content digest, and source commit only when that commit accurately represents the projected tree.

`agentic-core/agents/*.md` are canonical portable agent sources. `agentic-core/com.github.copilot/agents/` and generated Codex/Claude trees are target representations. The target projector is the editable source for those representations; generated output is rebuilt and compared, not manually maintained.

## Local work and durable coordination

Workspace-local authoring, building, validating, and testing use the repository's tools directly. A local workflow that does not depend on Control Plane state does not ask for a manifest, harness history, Task history, or allowed absolute paths. When a concrete workflow does depend on durable Task/Attempt state, the connected Control Plane owns that state; Agentic Core does not manufacture local files as its substitute.

## Historical evidence

[`CHECKOUT_INDEPENDENT_PROJECTIONS.md`](./CHECKOUT_INDEPENDENT_PROJECTIONS.md) records the earlier packaged-projector implementation and its observed test results. Its evidence remains historical; its old ownership statements are superseded by this decision.
