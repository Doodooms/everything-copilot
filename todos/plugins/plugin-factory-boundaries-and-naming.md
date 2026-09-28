---
kind: idea
status: intake
disposition: pending
derived_work: []
---

# Plugin Factory — naming, canonical boundaries and plugin decomposition

## Context

The repository has progressively evolved from an experiment around agentic workflows and GitHub Copilot into a more general system for authoring, validating, packaging and projecting portable agentic capabilities.

The current names and repository boundaries still reflect earlier stages of that evolution:

- repository: `everything-copilot`;
- broader project/workspace terminology: `agentic-workflow`;
- canonical plugin/content source: `agentic-core`;
- software-engineering capabilities and Plugin Factory capabilities are currently partly colocated.

This is not necessarily wrong historically, but the naming and ownership boundaries should eventually represent the architecture that now exists.

This document is an idea input only. It does not authorize a rename or repository migration.

## Naming direction

Consider converging the public project identity toward:

```text
Plugin Factory
```

Potential future renames:

```text
agentic-workflow
→ plugin-factory

everything-copilot
→ plugin-factory
```

The repository should no longer imply that GitHub Copilot is the canonical execution environment if the same canonical content can target:

- Copilot;
- Codex;
- ChatGPT;
- Work;
- Antigravity;
- future external harnesses.

Copilot becomes one projection/target rather than the identity of the system.

## Open decision: `agentic-core`

Do not rename `agentic-core` automatically.

Two plausible models remain.

### Option A — retain `agentic-core`

```text
plugin-factory repository
    │
    └── agentic-core
         canonical agentic source
```

Advantages:

- clearly distinguishes the factory/product from its canonical content;
- `agentic-core` remains the harness-neutral source from which projections are generated;
- avoids using the same name for repository, build system and canonical content.

Conceptually:

```text
Plugin Factory
= tooling and system

Agentic Core
= canonical source consumed by the factory
```

### Option B — rename canonical plugin to `plugin-factory`

This would make sense only if the canonical plugin and the factory itself are intentionally the same product boundary.

Risk:

```text
plugin-factory repository
plugin-factory plugin
plugin-factory tooling
plugin-factory source
```

may blur responsibilities instead of clarifying them.

## Current preference to investigate

Prefer keeping:

```text
Plugin Factory
    ↓
Agentic Core
```

unless a later architecture audit demonstrates that these are genuinely one responsibility.

Do not decide this from naming aesthetics alone.

## Separate Plugin Factory capabilities from SWE capabilities

The current canonical plugin contains at least two conceptual families:

```text
Plugin Factory / agentic infrastructure
    - create/update skills
    - create/update agents
    - create/update MCP
    - projection/package workflows
    - harness compatibility
    - orchestration primitives related to plugin construction

Software Engineering
    - implementation workflows
    - TDD
    - debugging
    - quality engineering
    - security engineering
    - architecture/review practices
    - development operations
```

These should eventually become separate plugins if the runtime/plugin model supports composing them cleanly.

Candidate model:

```text
agentic-core / plugin-factory plugin
    ↓
construction and orchestration of agentic capabilities

swe-plugin
    ↓
software-development expertise and workflows
```

A coding harness may install both:

```text
Plugin Factory
+
SWE Plugin
```

A non-coding harness or another product may install only the subset it requires.

## Important constraint

Do not split files merely because two conceptual groups can be named.

Before performing the split, validate:

- dependency direction;
- shared primitives;
- whether one plugin requires the other;
- package/projection behavior;
- installation semantics;
- skill discovery;
- cross-plugin references;
- versioning;
- whether circular dependencies appear.

The target should be explicit composition, not arbitrary physical separation.

## Canonical-source principle

Harness-specific filesystem layouts must not become canonical source locations.

The canonical project should not depend on manually authored copies under:

```text
.github/
.codex/
<other harness-specific directories>
```

Harness-specific representations should be generated/projected from the canonical source.

Desired model:

```text
Agentic Core / canonical plugins
          │
          ▼
      Plugin Factory
          │
     projection/package
          │
   ┌──────┼────────┐
   ▼      ▼        ▼
Copilot  Codex   other harness
   │      │
.github/ .codex/
if the target harness requires them
```

Therefore:

> Harness-specific directories may exist as generated or installation-time projections in target environments, but they must not become independent canonical sources that require manual synchronization.

## Runtime installation

Prefer installation/runtime integration that:

1. detects the target harness and its documented capabilities;
2. generates only the required representation;
3. installs or exposes the plugin using the harness-native mechanism;
4. preserves provenance to the canonical source;
5. can reconstruct generated files deterministically;
6. avoids manually maintained harness-specific duplicates.

## Questions for future research

- Should the repository itself become `plugin-factory`?
- Should `agentic-core` retain its current name?
- What exact responsibilities belong to the factory versus canonical plugin content?
- What is the minimal clean boundary between Plugin Factory and `swe-plugin`?
- How are shared skills/references expressed without plugin coupling?
- Should orchestration primitives belong to Plugin Factory, SWE, or a separate reusable plugin?
- Which `.github/` files are genuinely repository infrastructure rather than Copilot projections?
- Which harness-specific files can be generated entirely at install/projection time?

## Non-goals

This idea does not authorize:

- immediate repository rename;
- immediate package rename;
- immediate plugin split;
- deletion of `.github/`;
- compatibility shims;
- migration of current active work.

The next step should be an architecture audit followed by a human naming/boundary checkpoint.