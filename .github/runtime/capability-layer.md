# Capability Abstraction Layer

## Purpose

- Capabilities decouple skill workflow intent from concrete MCP provider tool names.
- Skills can express deterministic runtime needs with `capability:<name>` instead of binding authoring directly to one MCP tool.
- The first implementation is deliberately small: explicit registry files, explicit bindings, explicit provider catalogs, offline validation, and deterministic resolution.
- Existing skills and agents are not migrated in this change. The layer is available for future adoption.

## Files

- `.github/capabilities/*.yaml`: provider-agnostic capability contracts.
- `.github/runtime/provider-catalog.yaml`: explicit provider-to-server and provider-to-tool catalog.
- `.github/runtime/capability-bindings.yaml`: deterministic binding registry from capability to provider route.
- `scripts/capability_validator.py`: repo and per-skill validation CLI.
- `scripts/capability_resolver.py`: deterministic runtime resolver CLI.
- `scripts/capability_registry.py`: shared loader, parser, validator, and resolver primitives.

## Capability specification

Each capability file is a stable execution contract, not a provider binding.

```yaml
name: graph.semantic.related
description: Resolve semantically related entities from the workspace graph.
inputs:
  - query
  - scope
outputs:
  - related_entities
  - confidence
determinism:
  resolution: explicit
  fallback: forbidden
  ambiguity: fail
constraints:
  - Bindings must map to one deterministic provider route unless an explicit routing policy is declared.
requires: []
```

Rules:

- Capability names are lowercase dot-separated identifiers.
- Inputs and outputs are snake_case fields.
- `requires` is optional and models future composed-capability dependencies.
- `determinism` is mandatory so the contract states routing expectations explicitly.

## Provider catalog

The capability layer keeps a checked-in provider catalog because `.vscode/mcp.json` declares servers, not tool manifests.

```yaml
providers:
  graphify:
    server: graphify
    tools:
      - query_graph
      - get_node
      - get_neighbors
      - shortest_path
```

This duplication is intentional. It keeps validation offline, deterministic, auditable, and independent of live MCP startup state.

## Binding registry

Bindings connect a capability to one or more provider routes.

Single-route binding:

```yaml
bindings:
  graph.semantic.related:
    routes:
      - provider: graphify
        tool: query_graph
```

Explicit multi-provider binding:

```yaml
bindings:
  graph.semantic.related:
    policy:
      mode: explicit
    routes:
      - provider: graphify
        tool: query_graph
      - provider: gitnexus
        tool: context
```

Priority-routed binding:

```yaml
bindings:
  graph.semantic.related:
    policy:
      mode: priority
    routes:
      - provider: graphify
        tool: query_graph
        priority: 10
      - provider: gitnexus
        tool: context
        priority: 20
```

The resolver never guesses. If multiple routes exist and no valid policy is declared, validation fails.

## Skill syntax

Skills may now reference capabilities directly in workflow prose.

```markdown
1. Use capability:graph.semantic.related to retrieve semantically related graph context.
```

Guidelines:

- Capability markers belong in frontmatter-bearing skill definitions, not in support docs.
- Support docs remain passive and should mention capabilities only in fenced examples or ordinary prose.
- Capability markers are validated mechanically against the registry.

## Deterministic resolution rules

1. Unknown capability references fail validation.
2. Referenced capabilities without bindings fail validation.
3. Bindings pointing to unknown providers fail validation.
4. Bindings pointing to provider tools not declared in the provider catalog fail validation.
5. Provider catalog entries whose `server` is absent from `.vscode/mcp.json` fail validation.
6. Multiple routes without `policy.mode` fail validation.
7. `policy.mode: explicit` requires an explicit provider hint at resolution time.
8. `policy.mode: priority` requires unique integer priorities and selects the lowest priority deterministically.
9. Silent fallback is not supported.
10. Cycles in `requires` fail validation.

## Commands

Validate the full repository capability layer:

```bash
uv run python scripts/capability_validator.py repo --root .
```

Validate one skill's capability references:

```bash
uv run python scripts/capability_validator.py skill --skill-dir .github/skills/some-skill
```

Resolve one capability to its concrete MCP route:

```bash
uv run python scripts/capability_resolver.py resolve --capability graph.semantic.related
```

## Migration examples

Direct provider coupling before:

```markdown
1. Use #tool:graphify/query_graph to retrieve semantically related graph context.
```

Capability-layer form after:

```markdown
1. Use capability:graph.semantic.related to retrieve semantically related graph context.
```

Direct impact-analysis coupling before:

```markdown
1. Use #tool:gitnexus/impact to compute blast radius for the changed symbol.
```

Capability-layer form after:

```markdown
1. Use capability:graph.code.impact-analysis to compute blast radius for the changed symbol.
```

Migration strategy for existing skills:

1. Add the capability definition first.
2. Add the provider catalog entry if the provider is new.
3. Add the binding.
4. Run `scripts/capability_validator.py repo --root .`.
5. Replace the direct provider tool reference in the target `SKILL.md` with the capability marker.
6. Re-run the skill validator and the repo capability validator.

## Risks and tradeoffs

- There is now one more governed surface: capability definitions, provider catalog, and bindings must stay consistent.
- Provider catalogs duplicate MCP tool names, but that cost is lower than making validation depend on live server introspection or runtime heuristics.
- A capability layer can become abstract noise if every provider detail is lifted prematurely. Keep only stable, reusable workflow intents as capabilities.
- Priority routing is deterministic, but it still adds policy surface. Use it only when one route is deliberately preferred and audited.

## Governance implications

- Capability contracts are now first-class repository configuration and should be reviewed like code.
- Health checks validate the capability registry mechanically.
- Skill validation treats capability markers as executable workflow surfaces, not documentation-only prose.
- Because the binding registry is explicit and checked in, provider swaps become auditable config changes instead of hidden prompt edits.

## Future evolution paths

- Local versus cloud routing constraints on routes.
- Provider health checks gated by explicit policy rather than silent fallback.
- Route priorities with deterministic on-unavailable behavior.
- Capability-level caching hints.
- Capability execution telemetry.
- Graph sharding and master-graph versus micrograph routing.
- Wider adoption in prompts or other frontmatter-bearing surfaces after the skill-layer rollout proves stable.