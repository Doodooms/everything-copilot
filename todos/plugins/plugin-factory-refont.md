---
kind: design_input
status: researched
disposition: partially_adopted
derived_work: []
---

> **Design/research input — not an approved implementation plan.**

You are resuming work on the repository:

`/home/pm/projets-persos/agentic-workflow`

This repository is approaching an important architectural stabilization point.

The objective of this task is NOT to add another layer of features.

The objective is to redefine the repository around a coherent ontology and architecture so that future Agent Plugins can remain independently authored, composed safely, projected to different harnesses, and evaluated without creating hidden cross-plugin dependencies.

Treat this as a foundational architecture/refactoring task.

Do not push anything unless explicitly instructed.

Do not introduce or design unrelated future systems in this workspace.

Specifically:

- do NOT introduce Substrat;
- do NOT introduce Graphd;
- do NOT design placeholders, APIs, abstractions, providers, adapters, schemas, or compatibility hacks specifically for either of them;
- do NOT use them as justification for speculative abstractions.

They belong to another workspace.

The architecture designed here should be generally extensible, but it must be justified only by the actual Plugin Factory problem.

---

# 0. Fundamental objective

The repository currently named `agentic-workflow` should now be understood conceptually as:

# Plugin Factory

The Plugin Factory exists to:

```text
define
package
validate
compose
resolve
bind
project
materialize
evaluate
and eventually optimize
```

reusable Agent Plugins across heterogeneous agent harnesses.

Its central problem is:

> How can independently authored Agent Plugins contribute agents, expertise, skills, policies, tools, capabilities, and harness-specific features to one effective agentic system without knowing or mutating each other?

The architecture must therefore optimize for:

```text
independent plugin authorship
+
deterministic composition
+
late binding
+
explicit conflicts
+
progressive disclosure
+
harness-specific expressiveness
+
reconstructible materialization
+
cost-aware execution
```

The Plugin Factory is NOT itself a general agent runtime.

The Plugin Factory is NOT one giant Agent Plugin.

The Plugin Factory is NOT a collection of scripts that patch one plugin into another.

The Plugin Factory is the composition system.

---

# 1. Start by inspecting reality

Before modifying architecture or files, inspect the repository as it actually exists now.

Do not assume old plans are still authoritative.

Inspect at minimum:

```text
git status
current branch
HEAD
tracked modifications
untracked modifications
ignored/generated artifacts where relevant

repository root
README
architecture docs
todo/done/planning artifacts

agentic-core/
plugin manifests
pluginctl
profiles
resolution/composition code
materialization code

agents
skills
workflows
references
MCP declarations

Copilot-specific integration
Codex-specific integration

tests
benchmarks
experiments
measurement infrastructure
```

Pay particular attention to existing work related to:

```text
agentic-core packaging
plugin activation
plugin resolution
effective profiles
host materialization
Copilot projection
Codex projection
hierarchical skills
risk policies
evidence reuse
cross-harness execution
```

Preserve all user work.

Do NOT:

```text
git reset --hard
git clean
delete unknown local files
overwrite user modifications
checkout over local changes
```

Separate clearly:

```text
canonical source
generated state
cache
benchmark output
temporary materialization
user-authored uncommitted work
```

If uncertain whether something is disposable, preserve it.

---

# 2. Canonical architecture

The conceptual architecture should become:

```text
                    PLUGIN FACTORY

              ┌──────────────────────┐
              │ Plugin Factory ABI   │
              │                      │
              │ schemas              │
              │ contracts            │
              │ extension points     │
              │ semantic traits      │
              │ capabilities         │
              │ binding semantics    │
              └──────────┬───────────┘
                         │
                         │ shared contract only
                         │
       ┌─────────────────┼─────────────────┐
       │                 │                 │
       ▼                 ▼                 ▼
  Agent Plugin A    Agent Plugin B    Agent Plugin C
       │                 │                 │
       └─────────────────┼─────────────────┘
                         │
                         ▼
               Contribution Registry
                         │
                         ▼
                Dependency Resolution
                         │
                         ▼
                  Semantic Binding
                         │
                         ▼
                 Effective System
                         │
              ┌──────────┴──────────┐
              ▼                     ▼
       Copilot Projection      Codex Projection
              │                     │
              ▼                     ▼
      native Copilot state    native Codex state
```

This architecture must not assume that plugins know each other.

The normal case must be:

```text
Plugin
    depends on
Plugin Factory contracts
```

NOT:

```text
Plugin A
    knows implementation details of
Plugin B
```

Explicit plugin-to-plugin dependencies remain allowed when they are genuinely intentional.

Hidden coupling is not allowed.

---

# 3. Core independence principle

Establish this as a canonical invariant:

> Plugins declare what they provide and what kind of consumer can use it.

> Consumers declare which stable semantic contracts they satisfy.

> The Plugin Factory binds compatible providers and consumers only after the active plugin set is known.

Therefore generic plugin composition must use:

```text
Contribution
    ↓
Extension Point
    ↓
Semantic Selector
    ↓
Candidate effective entities
    ↓
Deterministic Binding
    ↓
Effective System
```

and NOT:

```text
Plugin
    ↓
hardcoded external agent name
    ↓
modify another plugin
```

This is the architectural concept of:

# late semantic binding

Make this concept explicit in architecture documentation.

---

# 4. Plugin Factory ABI

Introduce or formalize a minimal stable Plugin Factory ABI.

"ABI" here means the stable semantic contract through which independently authored plugins can interoperate.

It does NOT necessarily mean a native binary ABI.

The Plugin Factory ABI should eventually define the canonical contracts for concepts such as:

```text
Plugin
AgentDefinition
AgentContribution
Skill
Workflow
Policy
Capability
CapabilityProvider
ExtensionPoint
SemanticSelector
Binding
Profile
HarnessExtension
Materialization
```

Do not create every schema immediately merely because it appears in this list.

First inspect what already exists.

Reuse existing concepts where sound.

The architecture should nevertheless make clear which concepts belong to the stable Plugin Factory contract.

Plugins may depend on this ABI.

They should not need to depend on other plugin implementations for generic composition.

---

# 5. Agent Plugin ontology

Stop modeling a plugin merely as:

```text
Plugin
├── Agents
├── Skills
└── MCP
```

The conceptual model should instead be:

```text
AgentPlugin
│
├── Identity
├── Metadata
├── Dependencies
│
├── Contributions
│   ├── AgentDefinitions
│   ├── AgentContributions
│   ├── Skills
│   ├── Policies
│   └── CapabilityRequirements
│
├── CapabilityProviders
│
├── Resources
│   ├── workflows
│   ├── references
│   └── assets
│
├── HarnessExtensions
│
├── AdapterAssets
│
└── Validation / Tests
```

A plugin contributes to an effective system.

It does not automatically own a complete standalone hierarchy of agents.

---

# 6. Plugins must be self-contained

A plugin must contain everything necessary to understand and project that plugin, subject only to stable Plugin Factory APIs/contracts and declared dependencies.

Do not rely on arbitrary adaptation scripts stored somewhere else in the repository.

A target conceptual structure may resemble:

```text
plugin-name/
│
├── README.md
├── plugin manifest
│
├── agents/
│   ├── definitions/
│   └── contributions/
│
├── skills/
├── workflows/
├── references/
├── capabilities/
├── mcp/
│
├── adapters/
│   ├── copilot/
│   ├── codex/
│   └── future/
│
└── tests/
```

This is not permission to force this exact directory tree if the current host specifications suggest a better representation.

The important invariant is:

> Plugin-specific knowledge required for adaptation belongs with the plugin.

But:

> Global composition logic belongs to the Plugin Factory.

Therefore:

```text
plugin-local adapter assets
    YES

plugin-local global composition engine
    NO
```

---

# 7. Agentic Core

Preserve the nine current core agents:

```text
orchestrator
architect
planner
researcher
implementer
quality-assurance
reviewer
challenger
devops
```

They remain valuable.

Do not fuse them.

Their stable conceptual responsibilities remain:

```text
Orchestrator
    govern, route, coordinate, own workflow-level decisions

Architect
    map approved problem-space semantics into technical solution structure

Planner
    decompose and sequence delivery

Researcher
    establish isolated evidence for a bounded question

Implementer
    construct approved changes

Quality Assurance
    diagnose and independently falsify behavior where required

Reviewer
    perform configured final technical acceptance

Challenger
    independently attack high-impact proposals

DevOps
    mutate operational/deployment surfaces
```

However, reinterpret them as core role implementations rather than a universal API every other plugin must reference directly.

---

# 8. Core agents are not the public cross-plugin API

This distinction is critical.

Do NOT make:

```text
agentic-core/orchestrator
agentic-core/implementer
agentic-core/reviewer
```

the primary generic extension API for all plugins.

Instead, plugins should normally target stable semantic contracts.

The public composition API should be based on concepts such as:

```text
responsibility traits
authority traits
domain traits
extension points
capability contracts
binding rules
```

The concrete agents are implementations that satisfy these contracts.

Example:

```text
agentic-core/orchestrator
```

may advertise:

```text
responsibility:
    orchestration
    coordination
    routing

authority:
    delegation
```

A generic plugin must be able to contribute orchestration expertise without knowing that the concrete agent is named `orchestrator`.

---

# 9. Semantic traits

Introduce a small semantic trait vocabulary as part of the Plugin Factory composition contract.

Do NOT create hundreds of fine-grained traits.

Start from only the distinctions that are needed to solve actual current composition problems.

A reasonable initial responsibility vocabulary may include:

```text
orchestration
architecture
planning
research
construction
verification
acceptance
operations
```

Potential authority traits may include:

```text
may-delegate
may-mutate-product
may-mutate-operations
may-accept
```

Potential domain qualifiers may eventually include things such as:

```text
software
```

but do not build a giant universal domain ontology prematurely.

Important distinction:

```text
Role
    organizational ownership identity

Trait
    semantic characteristic relevant for composition

Skill
    specialized method

Capability
    executable operation or external ability
```

These are not interchangeable.

---

# 10. Generic plugin contributions must target semantics, not names

For generic composition, do NOT require:

```yaml
target:
  agent: orchestrator
```

Prefer a conceptual contribution such as:

```yaml
extension_point: agent/skill

selector:
  responsibility:
    all:
      - orchestration

payload:
  skill: some-plugin/some-orchestration-skill
```

The providing plugin does not need to know which agent exists.

The consuming agent advertises its semantic traits.

The Plugin Factory resolves the binding after composition.

Example:

```text
skill contribution
requires:
    orchestration

             ↓

semantic binder

             ↓

effective entity advertises:
    orchestration

             ↓

binding produced
```

No plugin source file is modified.

---

# 11. Explicit dependencies remain legitimate

Do not interpret plugin independence as "plugins may never depend on each other".

There are three acceptable coupling levels.

## Generic semantic composition

Preferred whenever appropriate:

```text
requires trait:
    orchestration
```

No plugin dependency.

## Contract dependency

A plugin may require a stable contract or feature family:

```text
requires contract:
    software-development
```

if such a contract eventually exists.

## Explicit plugin dependency

A plugin that intentionally extends a specific plugin may declare:

```text
requires plugin:
    software-factory
```

This is acceptable.

The important rules are:

```text
dependencies must be explicit
implementation coupling must be avoided
file mutation across plugin boundaries is forbidden
```

A plugin with an explicit dependency MAY target stable public IDs exported by that dependency.

A plugin without that dependency should use semantic binding.

---

# 12. Extension points

Introduce the notion of stable extension point classes.

Examples conceptually:

```text
agent/skill
agent/policy
agent/capability
agent/context
system/policy
system/capability-provider
```

Do not create extension point classes merely for completeness.

Only introduce extension points exercised by current architecture.

A contribution should conceptually answer:

```text
WHERE can this contribute?
WHAT kind of consumer is compatible?
WHAT is being contributed?
WHAT cardinality is expected?
IS the binding required?
```

For example:

```yaml
contribution:
  extension_point: agent/skill

  selector:
    responsibility:
      all:
        - orchestration

  cardinality: many

  required: false

  payload:
    skill: some-plugin/orchestration-method
```

Again, adapt syntax to repository conventions rather than copying this example mechanically.

---

# 13. Deterministic semantic binding

The semantic binder must be deterministic.

Do NOT use an LLM to guess plugin bindings.

A binding selector must produce deterministic candidate matching.

Support explicit cardinality semantics where needed, such as conceptually:

```text
exactly-one
zero-or-one
one-or-more
many
```

Expected behavior:

```text
exactly-one + 0 matches
    → error

exactly-one + 1 match
    → bind

exactly-one + 2 matches
    → ambiguity error

many + N matches
    → bind to all compatible targets
```

Do not silently pick the first candidate.

Do not rely on filesystem/plugin ordering for semantic conflict resolution.

---

# 14. Profiles resolve intentional ambiguity

A Plugin should describe compatibility.

A Profile should describe a concrete composition.

If semantic binding produces multiple legitimate candidates and the contribution requires a single target, the Plugin Factory must not guess.

Instead, allow explicit profile-level resolution.

Conceptually:

```text
Plugin
    declares compatibility

Factory
    discovers candidates

Profile
    selects concrete target when necessary
```

This makes the Profile a first-class configuration concept.

A profile is not canonical plugin source.

It is the concrete composition of a set of plugin contributions for an intended environment.

---

# 15. AgentDefinition vs AgentContribution

Replace the previous simplistic cross-plugin `AgentExtension` concept with a more general contribution model.

Use terminology appropriate to the repository, but maintain this semantic distinction:

## AgentDefinition

Defines a concrete agent and its ownership/responsibility contract.

Exactly one plugin owns that definition.

## AgentContribution

Adds compatible expertise/policies/skills/capability requirements to an effective agent through stable extension/binding contracts.

Zero or more plugins may contribute.

Therefore:

```text
AgentDefinition
    exactly one defining owner

AgentContributions
    zero to many contributors
```

An AgentContribution must not silently redefine:

```text
ownership
forbidden responsibilities
authority boundaries
acceptance authority
mutation authority
```

unless a deliberately supported override mechanism exists.

Do not introduce such an override mechanism unless actually required.

Prefer rejecting semantic conflicts.

---

# 16. Software Factory

Establish or prepare a separate conceptual plugin:

```text
software-factory
```

Do not mechanically move everything immediately.

First classify existing `agentic-core` content.

The key distinction is:

```text
agentic-core
    defines generic agentic roles/governance

software-factory
    contributes software-engineering expertise
```

Software Factory should NOT redefine copies of:

```text
Architect
Planner
Implementer
QA
Reviewer
DevOps
```

simply because software development uses those roles.

Instead, it should contribute expertise through semantic contracts.

Conceptually:

```text
software-factory
│
├── skills
│   ├── software-architecture
│   ├── implementation-design
│   ├── implementation-planning
│   ├── tdd
│   ├── test-design
│   ├── debugging
│   ├── code-review
│   ├── dependency-selection
│   ├── delivery
│   └── software-documentation
│
├── agent contributions
│
├── software-specific policies
│
└── capability requirements
```

For example, a TDD skill might target:

```text
responsibility:
    construction

domain/context:
    software
```

rather than:

```text
agentic-core/implementer
```

The exact domain mechanism must be designed carefully and only as far as current use cases require.

Do not over-engineer domain traits.

---

# 17. Classification rule for expertise

Use this conceptual rule consistently:

```text
WHO owns durable responsibility
    → Agent / Role

HOW specialized work is performed
    → Skill

WHAT executable operation exists
    → Capability / Tool

WHAT specialized procedure implements a skill
    → Workflow

WHAT declarative knowledge supports execution
    → Reference

WHAT plugin adds expertise to a compatible entity
    → Contribution
```

A new domain does NOT imply a new agent.

A new skill does NOT imply a new agent.

A new MCP does NOT imply a new agent.

Create new agents only for meaningful ownership/authority/context boundaries.

---

# 18. Dynamic skill composition

The current architecture must no longer assume that each agent source file contains its final static skill list.

Installing or activating another plugin may make new skills available to already-defined agents.

Therefore distinguish:

```text
skill ownership
skill installation
skill availability
skill binding
skill loading
skill execution
```

These states must not collapse.

Introduce or formalize three useful exposure classes:

```text
DISCOVERABLE
BOUND
EAGER
```

## DISCOVERABLE

The skill exists in the effective catalogue and can be considered by routing.

## BOUND

The skill is semantically relevant/authorized for one or more effective agents.

## EAGER

The skill content is injected immediately into the agent context.

EAGER should be rare.

Do not confuse:

```text
bound
```

with:

```text
fully loaded into prompt
```

A bound skill should normally remain progressively disclosed until required.

---

# 19. Preserve hierarchical skill architecture

Preserve the intended hierarchy:

```text
Agent
    ↓
Skill
    ↓
Workflow
    ↓
Reference / Asset / Tool
```

Do not recreate:

```text
Workflow
    ↓
internal subskill
    ↓
method-source
```

A Workflow should contain the actual specialized procedure.

References contain supporting declarative knowledge.

The parent Skill performs domain-level routing.

Workflow selection performs method-level routing.

Avoid duplicated full admission logic at each level.

---

# 20. Skill routing after plugin composition

An Effective Agent should conceptually receive a compact catalogue of compatible skills.

Do not concatenate full skill contents.

Target behavior:

```text
Effective Agent
       ↓
compact relevant skill catalogue
       ↓
routing
       ↓
selected skill
       ↓
selected workflow
       ↓
required references/tools
```

The composition system should therefore be able to answer:

```text
Which skills are installed?
Which are compatible with this effective agent?
Which are mandatory for this operation?
Which remain merely discoverable?
Which need eager loading?
```

without modifying canonical agent source.

---

# 21. Mandatory contributions

Distinguish carefully between:

```text
required available
required selected
required eager
```

## required available

The capability or skill must exist for the effective system to be valid.

## required selected

The skill/policy must be used for a certain operation/condition.

## required eager

Its content must always be loaded into context.

`required eager` should be extremely rare because it directly increases context cost.

Prefer short policies/contracts over full eager-loaded skills.

---

# 22. Capabilities

Separate abstract capability from concrete provider/tool.

Conceptually:

```text
Capability
    = semantic operation

CapabilityProvider
    = implementation exposing it

Tool
    = harness/runtime executable surface
```

Example:

```text
capability://code/search
```

might be implemented by one or more concrete providers.

Plugins should preferably depend on capabilities rather than MCP server names.

Do not encode:

```text
requires:
    some-specific-mcp-tool-name
```

when the real dependency is semantic.

---

# 23. Capability lifecycle

Distinguish:

```text
provided
resolved
authorized
exposed
invoked
```

These are separate states.

Likewise:

```text
MCP installed
!=
MCP available to every agent
```

and:

```text
tool available
!=
tool authorized
```

and:

```text
tool authorized
!=
tool injected into model context
```

This distinction is critical for:

```text
security
least privilege
token efficiency
harness portability
observability
```

---

# 24. Capability binding

Agents or contributions should express semantic capability requirements.

Example conceptually:

```yaml
requires:
  capabilities:
    - code/search
    - test/run
```

Then:

```text
Capability Resolver
       ↓
Provider
       ↓
Harness projection
       ↓
Concrete tool
```

A required capability with no provider should fail clearly.

Multiple providers must not be resolved nondeterministically.

Use explicit resolution rules/profile pins where necessary.

---

# 25. Resolver architecture

The Plugin Factory legitimately requires deterministic resolution infrastructure.

Do not avoid this because it feels like "extra machinery".

However, separate responsibilities clearly.

Conceptually:

```text
Dependency Resolver
    resolves plugin/package dependencies

Capability Resolver
    resolves abstract capabilities to providers

Semantic Binder
    binds contributions to compatible effective entities

Harness Projector
    translates effective semantics to native host representation
```

These may initially be implemented inside one compact module/tool if that is simpler.

Do not create four services merely because four conceptual responsibilities exist.

Keep conceptual boundaries clear even if physical implementation remains small.

---

# 26. Deterministic composition pipeline

Target conceptual flow:

```text
1. load source plugin manifests

2. validate plugin structure

3. resolve plugin dependencies

4. collect contributions

5. construct candidate entity registry

6. evaluate semantic selectors

7. resolve deterministic bindings

8. detect:
       ownership conflicts
       unresolved required bindings
       ambiguous bindings
       capability conflicts
       invalid contribution types
       incompatible plugin versions

9. resolve capabilities/providers

10. apply explicit profile decisions

11. construct Effective System

12. apply target harness extensions

13. materialize target harness representation

14. validate materialization
```

No LLM is required for this composition path.

---

# 27. Effective System

Use an explicit concept for the fully resolved semantic system.

The exact filename/serialization is implementation-dependent.

Conceptually:

```text
EffectiveSystem
│
├── active plugins
├── effective agents
│   ├── defining source
│   ├── semantic traits
│   ├── contributions
│   ├── bound skills
│   ├── policies
│   └── capability permissions
│
├── skill catalogue
├── workflows
├── capabilities
├── providers
├── system policies
├── unresolved optional contributions
└── provenance
```

Every derived element should ideally retain provenance.

Example:

```text
EffectiveAgent.skill X
    came from:
        plugin B
        contribution Y
        binding Z
```

This will become important for debugging composition.

---

# 28. Do not force a lowest-common-denominator IR

Copilot and Codex are not equivalent.

Do not destroy Copilot-specific capabilities merely because Codex lacks a direct equivalent.

The architecture must support:

```text
Canonical Semantic Definition
        +
Harness-Specific Extensions
```

not:

```text
intersection(Copilot, Codex)
```

For example conceptually:

```yaml
canonical:
  agent:
    responsibilities: ...
    skills: ...
    capabilities: ...

extensions:
  com.github.copilot:
    ...

  com.openai.codex:
    ...
```

Do not invent fields blindly.

Inspect the installed harnesses and current official/native plugin formats before finalizing schemas.

Preserve host-specific semantics when meaningful.

---

# 29. Harness adapters

A Harness Adapter translates the Effective System to the actual native representation supported by a harness.

Conceptually:

```text
Effective System
      ↓
Harness Adapter
      ↓
Native Harness Projection
```

Adapters must not redefine canonical plugin semantics.

Their responsibilities may include:

```text
capability detection
format translation
native metadata projection
native agent generation
skill projection
MCP projection
permission projection
materialization
validation
```

An adapter may report:

```text
SUPPORTED
UNSUPPORTED
PARTIAL
HOST_SPECIFIC
```

rather than silently discarding unsupported semantics.

---

# 30. Plugin-local adapter assets

A plugin may contain adapter resources required specifically to represent that plugin in a harness.

For example:

```text
plugin/adapters/copilot/
plugin/adapters/codex/
```

These resources belong to the plugin because otherwise the plugin is not self-contained.

However:

```text
plugin-specific adapter assets
```

must be interpreted by:

```text
the global Harness Adapter contract
```

The plugin must not independently rewrite arbitrary global harness state.

---

# 31. Canonical state vs materialized state

Establish this invariant explicitly:

> Harness-specific materialization is disposable.

Canonical state must live in:

```text
source plugins
factory configuration
profiles
lock/resolution metadata where appropriate
```

NOT only in:

```text
~/.codex/...
~/.copilot/...
generated profile directories
temporary harness state
```

The following conceptual operation must always be possible:

```text
delete generated harness projection
        ↓
materialize again
        ↓
same effective behavior
```

subject to intentionally non-deterministic external factors.

---

# 32. Avoid global user-state mutation where possible

For development, testing, and benchmarking, prefer:

```text
temporary materialization
project-local materialization
explicit plugin directory
explicit profile
managed worktree
ephemeral execution
```

when supported.

Do not make routine validation depend on modifying persistent global user configuration unnecessarily.

Permanent installation may still be supported as a separate explicit operation.

---

# 33. Plugin lifecycle

Preserve or formalize lifecycle states such as:

```text
AVAILABLE
INSTALLED
ACTIVE
RESOLVED
MATERIALIZED
```

Do not collapse them.

Important:

```text
installed
!=
active

active
!=
bound

bound
!=
materialized

materialized
!=
executed
```

A plugin may be installed without affecting the current effective system.

---

# 34. Profiles

Treat Profile as an intentional composition layer.

A Profile may define:

```text
active plugin set
plugin versions
binding overrides
provider selections
harness target
model/budget preferences
policy configuration
```

Do not put canonical plugin semantics into a Profile.

Plugins describe reusable possibilities.

Profiles choose a concrete system composition.

---

# 35. Locking and reproducibility

Inspect whether existing lock/profile mechanisms already exist.

Where useful, preserve enough information to reproduce a resolved composition:

```text
plugin identity
plugin version
source
digest if appropriate
active state
provider resolutions
explicit binding decisions
effective system hash
target harness
```

Do not introduce a complex package manager unless current needs require it.

Prefer extending existing `pluginctl` architecture if sound.

---

# 36. pluginctl

Inspect `pluginctl` before creating any new resolver/installer/compiler.

Determine which responsibilities it already has.

Classify existing functionality into:

```text
package discovery
installation
activation
dependency resolution
profile composition
validation
materialization
rollback
host projection
```

Then decide whether `pluginctl` should evolve into the deterministic Plugin Factory CLI.

Avoid parallel tools that solve the same problem.

A likely long-term conceptual model is:

```text
pluginctl
    install
    activate
    deactivate
    resolve
    validate
    materialize
    inspect
```

But do not add commands unnecessarily if equivalents already exist.

---

# 37. Conflict model

Make conflicts explicit and deterministic.

Examples that should fail rather than silently resolve:

```text
two plugins both claiming defining ownership of same canonical entity

required contribution with zero compatible targets

exactly-one contribution with multiple targets

required capability with no provider

multiple providers with no deterministic selection policy

incompatible plugin versions

contribution attempts to weaken forbidden authority contract

plugin attempts to mutate another plugin's canonical source

duplicate canonical IDs with incompatible meaning
```

Do not use:

```text
first plugin wins
last plugin wins
filesystem order wins
installation order wins
```

for semantic conflicts.

Harness-native precedence rules must not become canonical Plugin Factory semantics.

---

# 38. Cross-plugin modification is forbidden

A plugin installer must never do something equivalent to:

```text
open another plugin's agent file
append skill
rewrite another manifest
patch another plugin's MCP list
```

Composition must happen in derived/effective state.

Canonical plugin sources remain immutable relative to other plugins.

---

# 39. Core role ownership

The nine core agents remain owned by `agentic-core`.

But external plugins should normally see them through semantic contracts.

This allows future replacement/refactoring.

For example:

```text
agentic-core/orchestrator
```

could theoretically be renamed or structurally replaced later while preserving:

```text
responsibility: orchestration
authority: may-delegate
```

Generic plugins should continue working.

This is one of the main reasons semantic binding exists.

---

# 40. Preserve Problem Space / Solution Space architecture

Keep the previously established distinction.

```text
USER / PRODUCT INTENT
        ↓
PROBLEM SPACE
        │
        ├── requirements
        ├── semantic/domain model
        ├── use cases
        ├── assumptions
        ├── unknowns
        └── domain invariants
        ↓
CANONICAL SPECIFICATION
        ↓
SOLUTION SPACE
        │
        ├── architecture
        ├── components
        ├── interfaces
        ├── technical topology
        └── technical decisions
        ↓
IMPLEMENTATION
```

The Architect maps approved problem semantics into technical structure.

The Architect does not silently become owner of canonical domain semantics.

---

# 41. Preserve core agent ownership boundaries

Maintain these distinctions.

## Orchestrator

Owns workflow-level coordination, risk routing, delegation, and convergence.

## Architect

Owns technical solution structure.

## Planner

Owns decomposition and sequencing, not canonical requirements.

## Researcher

Owns bounded evidence acquisition.

## Implementer

Owns production construction and immediate implementation-level verification.

## QA

Owns independent diagnosis/falsification where required.

## Reviewer

Owns configured final technical acceptance.

## Challenger

Owns rare independent attack of materialized high-impact proposals.

## DevOps

Owns operational mutation/configuration/deployment surfaces.

Do not let plugin composition blur these ownership boundaries.

---

# 42. Preserve risk-proportional assurance

Do not impose a fixed universal:

```text
Implementer
→ QA
→ Reviewer
```

pipeline.

Assurance remains conditional.

Conceptually:

```text
low risk
    deterministic verification may be sufficient

moderate risk
    focused verification / targeted QA

high risk
    QA + Reviewer

very high impact
    additional specialist/challenger where justified
```

Orchestrator owns the selected assurance level.

Specialists consume assigned risk and may escalate based on new evidence.

They should not independently recompute the whole risk model each time.

---

# 43. Reviewer / QA distinction

Preserve:

```text
QA
    creates independent falsification evidence

Reviewer
    judges whether required evidence is sufficient
```

Do not duplicate successful verification unnecessarily.

Correct any wording equivalent to:

```text
Reviewer always requires QA
```

The correct principle is:

> A selected Reviewer gate requires all evidence mandated by the configured assurance policy; when independent QA is required, its evidence must be current.

---

# 44. Evidence is first-class

The Plugin Factory evaluation architecture should treat evidence as reusable structured output.

Conceptually:

```text
Evidence
├── producer
├── operation
├── artifact revision
├── environment
├── timestamp
├── result
└── provenance
```

Do not repeatedly rerun expensive validations solely because another agent needs to inspect the same fact.

Generate once where appropriate.

Review/reuse evidence.

Re-run only when:

```text
evidence is stale
environment changed
artifact revision changed
independent execution is itself required
evidence quality is insufficient
```

---

# 45. Context cost is an architectural constraint

Plugin composition can cause catastrophic prompt growth if treated naively.

Explicitly preserve:

```text
installed != active
active != relevant
relevant != bound
bound != loaded
loaded != invoked
```

Each stage should narrow the surface.

The desired context pipeline is:

```text
installed plugins
      ↓
active plugins
      ↓
effective contributions
      ↓
agent-compatible contributions
      ↓
compact metadata
      ↓
selected skill/workflow
      ↓
required deep content
```

Do not concatenate all plugin documentation, skills, tools, and MCP instructions into every agent context.

---

# 46. Plugin cost accounting

Composition should be observable enough that future evaluation can measure the marginal cost of plugins.

Where practical, retain or prepare metrics for:

```text
active plugins
skills visible
skills loaded
references loaded
tools exposed
MCP servers loaded
model calls
input tokens
output tokens
tool calls
validation calls
duplicate work
elapsed time
task success
```

Do not build the full optimization engine now.

But do not design an architecture that makes these measurements impossible.

---

# 47. Multi-harness architecture

Both Copilot and Codex must remain first-class targets.

Do not assume equivalent feature sets.

Current high-level rule:

```text
one development task
    → one modifying harness owner

other harness
    → bounded validator/evaluator when explicitly invoked
```

Avoid concurrent mutation of the same checkout by both harnesses.

Prefer isolated worktrees/temp state where appropriate.

Do not implement recursive harness delegation.

---

# 48. Harness capability detection

Do not hardcode assumptions where actual host capabilities can be detected.

A harness adapter should conceptually know whether the target supports features such as:

```text
plugin installation
custom agents
skills
MCP
structured output
non-interactive execution
model selection
sandboxing
worktrees
usage metrics
host-specific extension metadata
```

Represent unsupported capabilities explicitly.

Do not pretend a semantic projection succeeded if important behavior was discarded.

---

# 49. Copilot-specific features

Do not remove or weaken useful Copilot features merely to achieve syntactic parity with Codex.

If a concept is genuinely Copilot-specific:

```text
preserve it in a namespaced harness extension
```

rather than moving it into generic semantics or deleting it.

Do the same for Codex-specific features.

Canonical semantics should represent meaning.

Harness extensions should represent host-specific realization.

---

# 50. README requirements

Update the main README so a new contributor can understand the project without reading historical plans.

It should explain:

```text
what Plugin Factory is

what an Agent Plugin is

what agentic-core is

what software-factory is

why plugins are independent

what the Plugin Factory ABI is

what semantic traits are

what an extension point is

what a contribution is

what late semantic binding means

how capabilities differ from tools

how skills become dynamically available

why agents do not own immutable final skill lists

what a Profile is

what an Effective System is

how harness-specific extensions work

what is canonical vs generated

how Copilot and Codex projections differ
```

Prefer diagrams over verbose prose where useful.

---

# 51. Architecture documentation

Create or update one authoritative architecture document rather than scattering competing definitions across many plans.

Historical notes may remain historical, but make clear which architecture is canonical.

The canonical document should include at least:

```text
Ontology
Plugin Factory ABI
Plugin boundaries
Agent definitions
Agent contributions
Traits
Extension points
Semantic binding
Capabilities/providers
Profiles
Effective System
Harness projections
Materialization
Conflict rules
Canonical/generated state
```

Avoid redundant architecture documents saying slightly different things.

---

# 52. Existing planning artifacts

Inspect TODOs and `done/` documents.

Do not automatically execute old plans if they contradict the new ontology.

Classify relevant planning items into:

```text
still valid
valid but needs reinterpretation
superseded
completed
obsolete
```

Do not delete historical planning unless clearly generated/disposable.

---

# 53. Migration strategy

Do not perform a giant rewrite.

Use a staged migration.

Recommended conceptual sequence:

```text
A. audit current model

B. formalize canonical ontology

C. establish Plugin Factory ABI boundaries

D. classify current agentic-core contents

E. define semantic traits minimally

F. define Contribution + Extension Point semantics

G. introduce deterministic semantic binding

H. migrate one real existing cross-cutting case

I. separate software-specific expertise where justified

J. adapt Effective System representation

K. update harness projections

L. add validation scenarios
```

Each step should keep the repository usable.

---

# 54. Use real cases to validate abstractions

Do NOT build generic mechanisms without a real use case.

Use current repository needs as the forcing functions.

Examples:

```text
software-specific skill contributes to construction-capable agent

software review skill contributes to acceptance/review-capable agent

software architecture expertise contributes to architecture-capable agent

plugin introduces a capability provider used by compatible skills

Copilot projection preserves Copilot-specific metadata

Codex projection handles the same canonical semantic contribution differently
```

Do not invent hypothetical future systems solely to justify the framework.

---

# 55. Minimal semantic vocabulary

Be very conservative.

Prefer:

```text
8 useful stable semantic traits
```

over:

```text
80 speculative traits
```

A trait should exist only if it materially changes composition behavior.

Apply the same semantic modeling principle already used elsewhere:

> Model a distinction only when losing it could affect reasoning, behavior, validation, or future change.

---

# 56. No semantic matching by natural-language similarity

Do not implement:

```text
embedding search
LLM matching
fuzzy semantic routing
```

for plugin composition.

The binding layer must use explicit structured contracts.

LLMs may eventually help author plugins or propose bindings.

They must not define canonical deterministic composition semantics.

---

# 57. Provenance

Every effective contribution should ideally retain source information.

For example:

```text
Effective Agent
    base definition:
        agentic-core

    skill contribution:
        software-factory

    policy contribution:
        plugin-X

    capability resolution:
        provider-Y

    binding decision:
        profile/default deterministic rule
```

This is critical for:

```text
debugging
conflict explanation
evaluation
rollback
user trust
```

---

# 58. Explainability

Provide inspection tooling or prepare structures so users can answer questions such as:

```text
Why does this agent have this skill?

Which plugin contributed this policy?

Why was this capability provider selected?

Why is this contribution unbound?

Why did composition fail?

Why does Copilot expose this feature but Codex does not?

What canonical source generated this file?
```

If `pluginctl` already has inspect functionality, build on it.

---

# 59. Error messages

Composition errors should be actionable.

Bad:

```text
resolution failed
```

Good:

```text
Contribution software-factory/foo requires exactly one
consumer satisfying responsibility=construction.

Candidates found:
- agent-A
- agent-B

Resolve explicitly in the selected profile.
```

Or:

```text
Plugin X requires capability code/search.
No active provider satisfies this capability.
```

---

# 60. Security / permissions

Do not assume every plugin-provided capability should automatically be exposed to every effective agent.

Capabilities must respect:

```text
provider availability
agent authority
plugin policy
profile policy
harness constraints
```

A plugin introducing a powerful MCP server does not imply universal tool exposure.

Apply least privilege.

---

# 61. Validation scenarios

Create deterministic tests for the architecture.

At minimum validate the following scenarios.

### Scenario A — Independent generic contribution

A plugin provides a skill targeting:

```text
responsibility=construction
```

The plugin does not depend on agentic-core.

An active compatible agent receives the skill in Effective System.

No canonical agent file is modified.

### Scenario B — No compatible consumer

Optional contribution:

```text
0 matches
→ remains unbound
→ composition valid
```

Required contribution:

```text
0 matches
→ composition error
```

### Scenario C — Ambiguous exactly-one binding

Two compatible consumers exist.

Expected:

```text
composition reports ambiguity
```

No automatic first-match selection.

### Scenario D — Profile resolution

Profile explicitly selects one of multiple compatible targets.

Expected:

```text
binding succeeds deterministically
```

### Scenario E — Multiple contributions

Two independent plugins contribute compatible skills to the same agent.

Expected:

```text
both contributions compose
```

Neither plugin knows the other.

### Scenario F — Ownership conflict

Two plugins attempt to define the same canonical entity.

Expected:

```text
hard conflict
```

### Scenario G — Explicit dependency

Plugin B explicitly depends on Plugin A and targets a public ID exported by A.

Expected:

```text
allowed
```

Missing dependency:

```text
invalid
```

### Scenario H — Capability resolution

Skill requires abstract capability.

One provider exists:

```text
resolve
```

No provider exists and capability required:

```text
fail
```

Multiple providers without deterministic preference:

```text
explicit ambiguity
```

### Scenario I — Skill exposure

Validate distinction between:

```text
discoverable
bound
eager
```

Binding must not imply eager prompt injection.

### Scenario J — Harness-specific extension

Canonical semantic element has a Copilot-specific extension.

Expected:

```text
Copilot projection preserves it
Codex projection does not corrupt canonical semantics
```

Codex may report unsupported/ignored host extension where appropriate.

### Scenario K — Disposable materialization

Delete generated harness materialization.

Re-materialize.

Expected:

```text
canonical plugin sources remain intact
effective projection is reproducible
```

### Scenario L — No cross-plugin source mutation

Installation/activation of Plugin B must not modify canonical source files owned by Plugin A.

---

# 62. Software Factory extraction validation

If software-specific content currently lives in `agentic-core`, classify it carefully before moving.

Use categories:

```text
generic agentic governance
    keep in core

software-specific method
    candidate for software-factory

software-specific reference
    candidate for software-factory

generic role responsibility
    keep in core

harness-specific implementation detail
    adapter / harness extension

deterministic utility
    Factory tool/runtime utility
```

Do not move content merely because its filename sounds software-related.

Preserve actual semantic ownership.

---

# 63. Avoid premature packaging explosion

Do not immediately create:

```text
agentic-core
software-core
software-factory-core
plugin-sdk-core
plugin-runtime-core
composition-core
...
```

Prefer the minimum coherent package set.

At this stage the important conceptual boundaries are approximately:

```text
Plugin Factory
agentic-core
software-factory
harness adapters
```

Physical packaging may evolve after evidence.

---

# 64. Naming

The repository may remain named:

```text
agentic-workflow
```

for now.

Do not rename it unless explicitly instructed.

However, documentation should make clear that the product/domain being implemented is the:

```text
Plugin Factory
```

Avoid allowing the old repository name to drive incorrect ontology.

---

# 65. Known architectural principles to preserve

Preserve these principles from previous work:

```text
Agent = WHO owns durable responsibility

Skill = HOW specialized work is performed

Workflow = specialized procedure hidden inside a Skill

Reference = supporting declarative knowledge

Capability/Tool = executable operation

Artifact over conversation

Reference over repetition

Retrieve over inherit

Verify once and reuse fresh evidence

Installed != active != injected

Risk-proportional assurance

Progressive disclosure

Deterministic operations should not require an LLM

Every expensive model invocation should add distinct value
```

---

# 66. Important conceptual corrections from previous designs

Explicitly avoid these earlier mistakes.

## Mistake 1

```text
Every expertise plugin owns its own complete set of agents
```

Wrong.

Use contributions to compatible agents unless a new ownership boundary genuinely requires a new agent.

## Mistake 2

```text
Plugin contribution targets agentic-core/orchestrator directly
```

Wrong as the generic default.

Use semantic binding unless an explicit dependency intentionally exists.

## Mistake 3

```text
Agent source contains final complete skill list
```

Wrong.

The effective skill surface emerges after plugin composition.

## Mistake 4

```text
Tool installation means all agents should see the tool
```

Wrong.

Provisioning, authorization, exposure, and invocation are separate.

## Mistake 5

```text
Universal IR = lowest common denominator of Copilot and Codex
```

Wrong.

Use canonical semantics plus namespaced harness-specific extensions.

## Mistake 6

```text
Generated ~/.codex or ~/.copilot state is canonical
```

Wrong.

Harness materialization must be reconstructible.

## Mistake 7

```text
Every plugin carries arbitrary scripts that patch the whole system
```

Wrong.

Plugin-local adaptation data is allowed; global composition belongs to the Factory.

## Mistake 8

```text
No plugin may ever depend on another plugin
```

Wrong.

Explicit stable dependencies are acceptable.

Hidden dependencies are not.

---

# 67. Desired final conceptual model

The resulting architecture should be explainable approximately as:

```text
                       Plugin Factory ABI
                              │
                    stable semantic contracts
                              │
          ┌───────────────────┼───────────────────┐
          │                   │                   │
          ▼                   ▼                   ▼
     agentic-core      software-factory      other plugins
          │                   │                   │
          │ agents            │ skills            │ contributions
          │ traits            │ policies          │ capabilities
          │ contracts         │ requirements      │ providers
          └───────────────────┼───────────────────┘
                              │
                              ▼
                     Contribution Registry
                              │
                              ▼
                  Deterministic Composition
                      ├── dependencies
                      ├── semantic binding
                      ├── capabilities
                      └── conflicts
                              │
                              ▼
                       Effective System
                              │
                ┌─────────────┴─────────────┐
                ▼                           ▼
          Copilot Adapter               Codex Adapter
                │                           │
                ▼                           ▼
        Copilot-native state          Codex-native state
```

This is the architectural north star for this repository.

---

# 68. Implementation discipline

Before implementing a new abstraction, answer:

```text
What actual current problem requires it?

Can an existing repository abstraction represent it?

Can the distinction remain conceptual for now?

Does introducing it reduce coupling?

Does it make composition more deterministic?

Does it improve explainability?

Does it reduce future migration cost?

Does it create more machinery than the current problem justifies?
```

Prefer small semantic improvements over large speculative frameworks.

---

# 69. Deliverable phases

Execute the work in explicit phases.

## Phase 1 — Repository audit

Produce a factual inventory of current implementation.

No large changes.

## Phase 2 — Ontology document

Establish the canonical ontology and architecture.

Make contradictions with current implementation explicit.

## Phase 3 — Migration design

Produce the smallest coherent migration from current state.

Identify:

```text
keep
rename
reinterpret
move
replace
delete later
```

Do not delete historical/user artifacts yet.

## Phase 4 — Foundational contracts

Implement only the minimum first-class concepts necessary for:

```text
contributions
semantic selectors
binding
capability resolution
harness extensions
```

Reuse existing infrastructure.

## Phase 5 — Real composition slice

Migrate one real software-factory contribution through the new system.

Prove late semantic binding works without modifying core agent source.

## Phase 6 — Harness projection

Verify Copilot and Codex can consume the resulting effective system without forcing semantic equivalence.

## Phase 7 — Tests

Implement deterministic validation scenarios.

## Phase 8 — Documentation cleanup

Update README and canonical architecture docs.

Mark superseded planning material clearly.

---

# 70. Do not proceed blindly when the repository contradicts this prompt

This prompt defines architectural intent.

The repository defines implementation reality.

When they differ:

```text
inspect
explain discrepancy
preserve useful existing mechanisms
adapt the target intelligently
```

Do not destroy working architecture just to make filenames match this prompt.

If an existing mechanism is superior to the terminology proposed here, preserve the mechanism and document the semantic equivalence.

---

# 71. Final report

At the end provide:

```text
CURRENT STATE

CURRENT ONTOLOGY PROBLEMS

CANONICAL ONTOLOGY ESTABLISHED

PLUGIN FACTORY ABI

PLUGIN COMPOSITION MODEL

SEMANTIC BINDING MODEL

AGENTIC-CORE BOUNDARY

SOFTWARE-FACTORY BOUNDARY

SKILL COMPOSITION MODEL

CAPABILITY MODEL

HARNESS ADAPTATION MODEL

CANONICAL VS GENERATED STATE

CHANGES MADE

FILES CHANGED

TESTS EXECUTED

TEST RESULTS

UNRESOLVED QUESTIONS

REMAINING TECHNICAL DEBT

NEXT SMALLEST COHERENT SLICE
```

For every claim of successful behavior, provide concrete evidence.

Do not claim something is validated merely because configuration exists.

Do not push.

---

# 72. Success criteria

This task is successful when the repository can answer these questions clearly and consistently:

```text
What is Plugin Factory?

What exactly is an Agent Plugin?

What belongs to agentic-core?

What belongs to software-factory?

How can one plugin add expertise to an agent it does not know exists?

How can an agent receive skills introduced after its own plugin was authored?

How are plugin contributions bound without an LLM?

How are ambiguities handled?

When is explicit plugin dependency appropriate?

How are tools abstracted as capabilities?

Why does installing a tool not expose it everywhere?

How does Copilot retain Copilot-specific features?

How does Codex retain Codex-specific features?

What is canonical source?

What is derived Effective System state?

What is disposable harness materialization?

How can a generated installation be reconstructed?

How are conflicts reported?

How can the user inspect why a contribution exists?

How can future plugins remain independently authored?
```

If these questions cannot be answered with precise architecture and tests, continue refining the foundation before adding new product features.

The objective is to leave `agentic-workflow` with a small but extremely coherent Plugin Factory foundation that can support many independent Agent Plugins without hidden coupling, while preserving advanced host-specific functionality and keeping composition deterministic, inspectable, testable, and progressively optimizable.
