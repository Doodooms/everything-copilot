> **Design/research input — not an approved implementation plan.**

You are working in:

`/home/pm/projets-persos/agentic-workflow`

This repository is being redefined as a:

# Plugin Factory

The repository name may remain `agentic-workflow` for now, but the canonical product concept is Plugin Factory.

Your task is to continue the architectural stabilization already underway and incorporate the multi-harness architecture described below.

This is a foundational design and implementation task.

Do not treat it as a request to simply add support for another CLI.

The objective is to create a small, coherent, portable Agent Plugin composition system that can eventually target the four major coding-agent ecosystems without reducing them to a lowest common denominator.

Do NOT push anything unless explicitly instructed.

Do NOT introduce Substrat.

Do NOT introduce Graphd.

Do NOT design APIs, placeholders, abstractions, adapters, capability providers, runtime concepts, or future integrations specifically for Substrat or Graphd.

Those belong to another workspace.

This repository concerns only:

```text
Plugin Factory
Agent Plugins
plugin composition
semantic binding
portable packaging
harness adaptation
harness validation
evaluation
```

---

# 1. First principle: research before architecture

The coding-agent ecosystem is changing rapidly.

Do not rely exclusively on your pretrained knowledge.

Before finalizing schemas or adapters, inspect:

1. the repository as it currently exists;
2. the locally installed CLI capabilities where available;
3. current official documentation for the target harness;
4. current portable Agent Plugin specifications.

Use official sources preferentially.

For each target ecosystem, establish factual capability information before designing an adapter.

Do not assume that a capability mentioned in this prompt is still exposed in exactly the same way.

Distinguish:

```text
VERIFIED CURRENT FACT
ARCHITECTURAL INFERENCE
PROPOSED FACTORY ABSTRACTION
```

Do not silently convert an inference into a fact.

---

# 2. Canonical identity of the project

Plugin Factory exists to:

```text
define
package
validate
compose
resolve
bind
project
materialize
inspect
evaluate
and eventually optimize
```

independently authored Agent Plugins.

The central problem is:

> How can multiple independently authored Agent Plugins contribute expertise and capabilities to one effective agentic system, while remaining portable across heterogeneous coding-agent harnesses?

The desired properties are:

```text
plugin independence
deterministic composition
late semantic binding
portable canonical semantics
native harness specialization
progressive disclosure
least-privilege tool exposure
reconstructible materialization
observable cost
explainability
```

Plugin Factory is NOT:

```text
a general agent runtime
a replacement for Copilot/Codex/Claude/Antigravity
one giant plugin
a pairwise plugin patching system
a lowest-common-denominator wrapper
```

---

# 3. Keep the existing Plugin Factory ontology

The architecture already being established includes:

```text
Plugin Factory ABI
Agent Plugin
AgentDefinition
AgentContribution
Skill
Workflow
Reference
Policy
Capability
CapabilityProvider
ExtensionPoint
SemanticSelector
Binding
Profile
EffectiveSystem
HarnessExtension
HarnessAdapter
Materialization
```

Preserve the core principles already established.

In particular:

> Plugins declare what they provide and what kind of entity can consume it.

> Consumers declare which stable semantic contracts they satisfy.

> Plugin Factory binds them only after the active plugin set is known.

Generic composition uses:

```text
Contribution
    ↓
Extension Point
    ↓
Semantic Selector
    ↓
candidate effective entities
    ↓
deterministic late binding
    ↓
Effective System
```

A plugin should not need to know concrete agents owned by another plugin.

Do not regress to:

```text
plugin X
→ knows core/orchestrator
→ patches orchestrator file
```

unless X explicitly declares a dependency on the owning plugin and intentionally consumes a stable exported API.

---

# 4. Keep plugin independence

The normal dependency relationship should be:

```text
Plugin A ─┐
Plugin B ─┼── depend on → Plugin Factory ABI
Plugin C ─┘
```

not:

```text
Plugin A → Plugin B internals
Plugin B → Plugin C internals
Plugin C → Plugin A internals
```

Plugins must communicate through:

```text
stable IDs
semantic traits
extension points
capability contracts
declared dependencies
contributions
profiles
```

Never through undocumented file mutation.

Cross-plugin canonical source modification is forbidden.

---

# 5. Keep late semantic binding

For example, a plugin must be able to provide:

```text
skill: some-orchestration-method

consumer selector:
    responsibility = orchestration
```

without knowing that the currently active implementation is named:

```text
agentic-core/orchestrator
```

An effective agent advertises stable semantic traits.

The Factory performs deterministic matching.

Generic plugins depend on semantic contracts.

Concrete agent identities remain implementation details unless deliberately exported.

---

# 6. Keep the core role model

Preserve the nine existing `agentic-core` agents:

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

Do not duplicate them inside every expertise plugin.

Their generic responsibilities remain approximately:

```text
Orchestrator
    coordination / routing / delegation

Architect
    technical solution structure

Planner
    decomposition / sequencing

Researcher
    bounded evidence acquisition

Implementer
    construction

Quality Assurance
    independent diagnosis / falsification

Reviewer
    configured technical acceptance

Challenger
    rare independent attack of high-impact proposals

DevOps
    operational mutation
```

Expertise plugins normally add:

```text
skills
policies
references
capability requirements
agent contributions
```

rather than duplicate generic roles.

---

# 7. Preserve the Software Factory distinction

Continue separating:

```text
agentic-core
    generic agentic governance

software-factory
    software-engineering expertise
```

Software Factory may contribute software-specific expertise to effective agents satisfying traits such as:

```text
architecture
planning
construction
verification
acceptance
operations
```

It should not redefine six copies of core agents merely because those agents participate in software development.

Remember:

```text
new expertise != new agent
```

---

# 8. New key distinction: Ecosystem != Harness != Surface

Make this explicit in the canonical ontology.

These concepts must not be conflated.

## Ecosystem

The vendor/product family.

Examples:

```text
OpenAI
GitHub/Microsoft
Anthropic
Google
```

## Harness

The underlying agent execution/configuration system that interprets skills, tools, agents, policies, hooks, context, and agent behavior.

Examples currently expected to investigate:

```text
Codex
Copilot
Claude Code
Antigravity
```

## Surface

A concrete user or programmatic interface exposing a harness.

Potential examples:

```text
CLI
IDE
desktop application
cloud agent
SDK
managed agent
API
```

The important invariant is:

> A new surface does NOT automatically imply a new HarnessAdapter.

This must be proven from actual semantics.

---

# 9. HarnessBackend != SurfaceBackend

Introduce this distinction conceptually.

Do not necessarily introduce these exact class names unless the implementation benefits.

The Factory should reason approximately as:

```text
Ecosystem
    ↓
HarnessBackend
    ↓
Surface(s)
```

For example, if multiple Google surfaces demonstrably run the same Antigravity harness and share compatible plugin/skill semantics:

```text
Google
  ↓
Antigravity Harness
  ├── CLI
  ├── IDE
  ├── desktop/orchestrator
  └── SDK
```

there should normally be:

```text
one Antigravity semantic adapter
```

plus small surface-specific behavior only where actual differences exist.

Do NOT automatically build:

```text
AntigravityCLIAdapter
AntigravityIDEAdapter
AntigravityDesktopAdapter
AntigravitySDKAdapter
```

if these surfaces share one underlying semantic model.

Conversely, if official evidence demonstrates materially different extension/configuration semantics, model the distinction.

Architecture must follow verified behavior.

---

# 10. Surface capability differences still matter

Shared harness does NOT imply identical operational capability on every surface.

Therefore distinguish:

```text
HarnessSemantics
```

from:

```text
SurfaceCapabilities
```

Example:

```text
Antigravity Harness
    supports skill semantics X

Antigravity CLI
    supports headless execution

Antigravity IDE
    supports IDE-specific interaction

Antigravity SDK
    supports programmatic construction
```

The adapter should reuse common harness semantics while surface capability detection handles operational differences.

Do not duplicate semantic lowering merely because invocation mechanisms differ.

---

# 11. First-generation harness scope

Treat the following four as the intended first-generation interoperability targets:

```text
OpenAI
    → Codex

GitHub/Microsoft
    → Copilot

Anthropic
    → Claude Code

Google
    → Antigravity
```

This is a deliberate scope boundary.

Do not start implementing adapters for:

```text
Cursor
Windsurf
Cline
Roo
Zed
other coding-agent harnesses
```

unless explicitly requested.

The Factory architecture should allow future adapters, but the V1 design should not optimize for every product in existence.

---

# 12. Gemini CLI is not automatically a primary adapter

Research the current official Google position.

Current architectural expectation is that Google's coding-agent strategy is converging around Antigravity.

If current official documentation confirms that Antigravity CLI now represents the relevant Google harness for individual/developer use and shares its underlying harness with other Antigravity surfaces, model:

```text
Google ecosystem
    ↓
AntigravityAdapter
```

rather than automatically creating:

```text
GeminiCLIAdapter
GeminiCodeAssistAdapter
AntigravityAdapter
...
```

If Gemini CLI still requires compatibility for a concrete supported case, treat that as:

```text
legacy / compatibility adapter
```

not the architectural center.

Do not assume this without verifying current official documentation.

---

# 13. Critical research task: reverse-engineer each harness extension model

Before writing an adapter, produce a structured capability inventory for each harness.

For:

```text
Copilot
Codex
Claude Code
Antigravity
```

investigate at minimum:

```text
plugin/package format
manifest format

skills
skill discovery
skill progressive loading

custom agents / subagents
agent-specific prompts
agent tool restrictions
agent model selection
agent reasoning configuration

MCP support
MCP configuration
MCP lifecycle
MCP permissions

hooks
hook events
hook decisions
hook portability

rules/instructions
workspace-level configuration
user-level configuration

tool permissions
tool allowlists/denylists
sandboxing

context configuration
memory
session persistence

non-interactive execution
structured output

worktree/workspace isolation

telemetry / tracing
token/usage reporting

artifacts
verification artifacts

plugin installation
plugin activation
plugin scope
plugin update/removal

native profile/config layering

SDK/programmatic control

multi-agent/subagent orchestration

host-specific extension namespaces

portable Agent Plugin support
```

For each primitive classify:

```text
SUPPORTED
PARTIAL
UNSUPPORTED
HOST_SPECIFIC
UNKNOWN
```

Store evidence/provenance.

Do not encode assumptions.

---

# 14. Build a Harness Capability Matrix

Maintain one canonical machine-readable or easily generated representation conceptually equivalent to:

```text
Capability Matrix
──────────────────────────────────────────────────
Primitive              Copilot Codex Claude Antigravity

portable skills
MCP
custom agents
hooks
sandbox
permissions
structured output
non-interactive mode
SDK
subagents
artifacts
usage reporting
...
```

The exact list should come from research.

The matrix should not itself become the semantic IR.

It exists to inform projection and validation.

---

# 15. Research before lowering

For every new HarnessAdapter:

```text
official documentation
        ↓
native file/config model
        ↓
native lifecycle
        ↓
native capabilities
        ↓
native constraints
        ↓
canonical mapping
        ↓
loss analysis
        ↓
adapter design
```

Do NOT start from:

```text
"How can I convert our YAML into their YAML?"
```

Start from:

```text
"What semantic primitives does this harness actually expose?"
```

This is fundamental.

---

# 16. Do not confuse syntax portability with semantic portability

The Factory must not merely translate file layouts.

For example:

```text
SKILL.md exists in harness A
SKILL.md exists in harness B
```

does NOT prove identical semantics.

Investigate:

```text
discovery timing
admission logic
progressive loading
scope
tool availability
context injection
precedence
conflict rules
lifecycle
```

The adapter maps semantic behavior, not filenames alone.

---

# 17. Investigate Agent Plugins 1.0 before inventing a new universal plugin format

This is now a major architectural requirement.

Current official GitHub and OpenAI documentation indicates meaningful convergence around a portable Agent Plugin format containing at least:

```text
plugin.json
skills/
mcp.json
```

with namespaced host-specific extensions.

Before inventing a proprietary canonical package format, investigate the current Agent Plugins specification in detail.

Answer:

```text
Can Agent Plugins 1.0 be our canonical source package format?

Which Factory semantics are already represented?

Which Factory semantics are missing?

Can missing Factory semantics live in a namespaced extension?

Which components are intentionally host-specific?

Which clients currently consume the portable fields?
```

Strongly prefer:

```text
existing open/portable standard
+
Plugin Factory semantic extensions
```

over:

```text
entirely new incompatible package standard
```

when technically sound.

---

# 18. Separate Portable Package from Effective System IR

Even if Agent Plugins becomes the canonical source package format, do NOT confuse:

```text
Source Plugin Package
```

with:

```text
Effective System
```

The source package describes one independently authored plugin.

The Effective System is the derived result of composing many plugins.

Therefore:

```text
Agent Plugin package
        ↓
Factory validation
        ↓
Plugin composition
        ↓
late semantic binding
        ↓
capability resolution
        ↓
Effective System
        ↓
Harness projection
```

Agent Plugins may solve PACKAGE portability.

Plugin Factory still solves COMPOSITION.

---

# 19. Namespaced host extensions are first-class

The portable model should preserve native harness functionality through namespaced extensions.

Conceptually:

```text
canonical plugin semantics
│
├── portable:
│     skills
│     MCP
│     metadata
│
└── extensions:
      com.github.copilot
      com.openai
      com.anthropic
      com.google.antigravity
```

The actual namespaces must follow existing standards where defined.

Do not invent alternate namespaces if official ones already exist.

Research each ecosystem.

---

# 20. Do not flatten advanced harness features

A semantic feature available only in one harness must not be discarded simply because other harnesses cannot express it.

For example, if a harness has a native capability such as:

```text
special custom agents
native hook decisions
special reasoning controls
native sandbox modes
artifacts
special subagent semantics
host memory
```

preserve it under the appropriate host-specific extension.

Then the adapter may report for another harness:

```text
UNSUPPORTED
PARTIAL
NO_EQUIVALENT
```

Do not silently degrade behavior.

---

# 21. Projection must report loss

Define or prepare a projection diagnostic model.

A projection should be able to produce information equivalent to:

```text
projection:
    target: codex

    exact:
        - skill X
        - MCP Y

    lowered:
        - policy A -> native rule B

    unsupported:
        - copilot-specific feature Z

    approximated:
        - semantic feature Q

    warnings:
        - ...
```

A successful serialization is not necessarily a semantically successful projection.

---

# 22. Semantic fidelity levels

Consider a small projection fidelity vocabulary.

For example:

```text
EXACT
NATIVE_EQUIVALENT
LOWERED
APPROXIMATED
UNSUPPORTED
```

Do not necessarily use these exact names.

The important property is that loss is explicit.

This becomes useful for:

```text
validation
testing
cross-harness comparisons
plugin portability reports
```

---

# 23. Adapter architecture

The target architecture should approximately be:

```text
Canonical Agent Plugins
           │
           ▼
     Plugin Factory
           │
           ├── dependency resolution
           ├── contribution registry
           ├── semantic binding
           ├── capability resolution
           └── profile decisions
           │
           ▼
     Effective System
           │
       HarnessAdapter
           │
 ┌─────────┼───────────┬──────────────┐
 ▼         ▼           ▼              ▼
Copilot   Codex    Claude Code    Antigravity
```

Do not duplicate canonical plugin content into four manually maintained source plugins.

---

# 24. Adapter responsibility

A HarnessAdapter owns translation from Effective System semantics into one harness.

Possible responsibilities:

```text
detect harness/version

detect supported primitives

lower semantic entities

apply host-specific extensions

construct native plugin/config/profile state

resolve native paths

map capability permissions

configure MCP exposure

configure skills

configure agents/subagents

configure hooks

validate resulting projection

run static conformance checks

report unsupported/lossy mappings
```

It must NOT:

```text
redefine plugin semantics
mutate source plugins
invent missing semantic ownership
silently select ambiguous contributions
```

---

# 25. Keep adapter code thin

Do not move composition logic into adapters.

Bad:

```text
CopilotAdapter decides which plugin skill belongs to which agent

CodexAdapter independently makes the same decision
```

This causes divergence.

Correct:

```text
Plugin Factory Semantic Binder
    decides binding once

Effective System
    contains resolved binding

HarnessAdapter
    only represents that binding natively
```

This is critical.

---

# 26. Canonical decisions happen before projection

The following decisions belong BEFORE HarnessAdapter:

```text
active plugins
plugin versions
dependencies
agent contribution binding
skill binding
policy binding
capability requirements
capability provider selection
ownership conflicts
profile overrides
```

The adapter receives a resolved semantic system.

It should not redo them.

---

# 27. Harness-native decisions remain in adapters

The following may legitimately remain host-specific:

```text
native file locations
native plugin metadata
native hooks syntax
native permissions syntax
native agent format
native MCP config syntax
native CLI invocation
native sandbox mapping
native workspace scoping
native session flags
```

This distinction should be explicit.

---

# 28. Google / Antigravity architecture

Research current official Antigravity documentation carefully.

The current expected model to validate is:

```text
Google ecosystem
       ↓
Antigravity shared harness
       ↓
multiple surfaces
```

Potential surfaces include, subject to current verification:

```text
Antigravity CLI
Antigravity IDE
Antigravity desktop/orchestrator
Antigravity SDK
managed/programmatic agent surfaces
```

If current documentation confirms shared harness semantics, implement ONE semantic AntigravityAdapter.

Represent surface-specific invocation/capability differences separately.

---

# 29. Antigravity primitives worth studying for Plugin Factory

Do not implement them blindly.

Study whether Antigravity currently exposes concepts corresponding to:

```text
Skills
MCP
Hooks
subagents
workspaces
sandbox policies
artifacts
sessions
trajectory persistence
telemetry
tool interception
tool policy
programmatic SDK control
```

For each primitive determine:

```text
is this package configuration?
runtime configuration?
surface behavior?
SDK-only?
portable?
host-specific?
```

Do not mix runtime concepts into Plugin Factory simply because Antigravity exposes them.

The Factory needs only enough information to package/project plugin semantics.

---

# 30. Learn from Antigravity's progressive skill loading

One concept from Antigravity is especially relevant to the Factory:

> large static instruction/tool surfaces create tool/context bloat.

Preserve the Factory's existing progressive-disclosure architecture.

Do not interpret plugin activation as prompt injection.

Continue distinguishing:

```text
installed
active
available
compatible
bound
loaded
invoked
```

For skills specifically:

```text
DISCOVERABLE
BOUND
EAGER
```

EAGER must remain exceptional.

---

# 31. Native progressive loading should be preferred

If a harness natively supports relevant/on-demand skill discovery, use it.

Do not emulate progressive loading by eagerly concatenating all skill bodies.

The adapter should exploit the harness-native mechanism where semantic fidelity is acceptable.

If a harness lacks the mechanism, use the smallest reasonable lowering and report the difference.

---

# 32. Claude Code architecture

Research Claude Code's current official extension model.

Expected areas to investigate include:

```text
plugins
skills
agents/subagents
hooks
MCP
rules
permissions
project/user scopes
worktrees
non-interactive execution
structured output
SDK/programmatic invocation
memory
```

Do not assume Claude's meanings are identical to Copilot merely because some directory names resemble one another.

Map semantics explicitly.

---

# 33. Copilot architecture

Research and preserve Copilot-specific strengths.

Current repository development has already used advanced Copilot capabilities.

Do not degrade them for portability.

Investigate current support for:

```text
Agent Plugins
custom agents
skills
hooks
MCP
LSP where relevant
reasoning effort
models
permissions
tool exposure
plugin directories
plugin scopes
non-interactive mode
JSON output
usage output
dynamic retrieval
memory
subagent/fleet/orchestration behavior
```

Only model fields needed by Plugin Factory.

Do not mirror the entire Copilot CLI API into canonical IR.

---

# 34. Codex architecture

Codex is already installed and authenticated locally.

Its non-interactive execution works.

Inspect the actual installed CLI before designing projection.

Known local capabilities should be verified using:

```text
codex --help
codex exec --help
codex plugin ...
codex mcp ...
codex features ...
```

Investigate:

```text
portable plugins
skills
MCP
hooks if supported
profiles
sandbox
worktree execution
structured JSONL
output schemas
ephemeral runs
config layering
agent capabilities
```

Again, do not make Codex syntax canonical.

---

# 35. Use current local binaries as evidence

For Copilot and Codex, local installed binaries are valuable evidence.

Record:

```text
CLI version
supported commands
flags
plugin commands
MCP commands
structured output support
sandbox/worktree controls
```

Do not assume documentation and installed version are identical.

If behavior differs:

```text
document installed-version behavior
document current-doc behavior
avoid claiming unsupported functionality
```

---

# 36. Version-aware adapters

Harness capabilities change.

Therefore HarnessAdapter behavior should be capable of reasoning about:

```text
harness identity
harness version
detected capability set
```

Do not scatter:

```text
if version > X
```

through every plugin.

Version compatibility belongs to harness adaptation.

Plugins should remain mostly unaware of host versions.

---

# 37. Capability detection over assumptions

Prefer:

```text
detect()
```

over:

```text
assume()
```

Conceptually an adapter may expose:

```text
HarnessCapabilities
```

including:

```text
skills
custom_agents
MCP
hooks
non_interactive
structured_output
sandbox
worktrees
usage_metrics
native_plugin_format
SDK
...
```

Do not overbuild this structure.

Only model fields that materially affect projection or validation.

---

# 38. Surface profiles

If multiple surfaces of one harness require different operational configuration, represent them as surface profiles rather than entirely different semantic adapters.

Conceptually:

```text
AntigravityAdapter

surface profiles:
    cli
    ide
    desktop
    sdk
```

Likewise, other ecosystems may expose:

```text
CLI
IDE
cloud
SDK
```

Do not assume this pattern applies uniformly.

Use evidence.

---

# 39. Source package should remain self-contained

Each Agent Plugin should contain its own portable material and its own host-specific extensions/assets.

A target conceptual layout may become:

```text
my-plugin/
│
├── plugin.json
├── README.md
│
├── skills/
├── mcp.json
│
├── references/
├── assets/
│
├── contributions/
│
└── host-specific extensions
      ├── Copilot
      ├── Codex
      ├── Claude
      └── Antigravity
```

However:

DO NOT force custom directories if Agent Plugins or a host specification already defines standard namespaced locations.

Prefer standards.

---

# 40. Plugin-specific adapter assets vs Factory adapter implementation

Keep the distinction:

```text
Factory
    owns generic HarnessAdapter implementation

Plugin
    owns plugin-specific native assets/extensions
```

For example a plugin may include a Copilot-specific custom agent definition.

That does not justify putting a separate Copilot compiler inside the plugin.

The Factory CopilotAdapter interprets the plugin's host extension.

---

# 41. Avoid N × M integration explosion

Never build:

```text
plugin-A-to-copilot-custom-script
plugin-A-to-codex-custom-script
plugin-A-to-plugin-B-script
plugin-B-to-copilot-custom-script
...
```

The desired complexity is approximately:

```text
N plugins
+
M harness adapters
```

not:

```text
N × N × M
```

The stable Plugin Factory ABI is what makes this possible.

---

# 42. Portable primitives and host-specific primitives

Classify every plugin primitive as one of:

```text
PORTABLE
PORTABLE_WITH_HOST_EXTENSIONS
HOST_SPECIFIC
```

For example, after research:

```text
Skill
    may be portable

MCP declaration
    may be portable

special custom-agent field
    may be host-specific

special lifecycle hook
    may require host extension
```

Do not assume classification.

Derive it from standards and official docs.

---

# 43. Shared terminology

Use stable terminology throughout documentation and code.

Recommended distinctions:

```text
Plugin
    independently authored source package

Contribution
    semantic addition supplied by a plugin

EffectiveSystem
    fully resolved composition

Harness
    agent execution/configuration model

Surface
    interface exposing a harness

HarnessAdapter
    semantic projector for one harness

SurfaceProfile
    operational specialization of one harness surface

HostExtension
    namespaced host-specific source metadata

Materialization
    generated native host state
```

Avoid using:

```text
provider
backend
adapter
host
surface
harness
```

interchangeably.

If existing code uses different names, establish explicit definitions.

---

# 44. Do not introduce "Provider" ambiguously

The word `provider` is already useful for:

```text
CapabilityProvider
```

Therefore avoid also using it casually to mean:

```text
OpenAI
Google
Anthropic
```

unless namespaced clearly.

Prefer:

```text
Ecosystem
Harness
Surface
CapabilityProvider
```

to reduce ambiguity.

---

# 45. Canonical package vs canonical semantic IR

Keep these separate:

```text
Canonical Source Package
    authored by plugin developer

Effective Semantic IR / EffectiveSystem
    derived by Factory
```

The source package should preferably align with existing Agent Plugin standards.

The EffectiveSystem may remain Factory-specific because it represents multi-plugin composition that portable package formats do not necessarily model.

---

# 46. EffectiveSystem must preserve host extensions

Do not discard host-specific source information during composition.

For example:

```text
EffectiveSystem
│
├── canonical semantics
│
└── host_extensions
    ├── copilot
    ├── codex
    ├── claude
    └── antigravity
```

Only relevant extensions need to survive.

Do not inject all host-specific content into model context.

This is compiler data.

---

# 47. Think like a compiler

Plugin Factory should increasingly resemble a compiler/package composition system:

```text
Source Plugins
      ↓
parse
      ↓
validate
      ↓
resolve dependencies
      ↓
collect contributions
      ↓
semantic bind
      ↓
resolve capabilities
      ↓
EffectiveSystem IR
      ↓
target-specific lowering
      ↓
Harness-native materialization
```

This is preferable to treating Factory as a pile of install scripts.

---

# 48. Use compiler concepts carefully

Useful concepts:

```text
source package
semantic validation
IR
lowering
target
projection
diagnostics
provenance
```

Do not overcomplicate the implementation with compiler theory where simple Python/data structures suffice.

The conceptual analogy is valuable primarily because it clarifies responsibility boundaries.

---

# 49. Harness adapters are compiler backends

Conceptually:

```text
CopilotAdapter
CodexAdapter
ClaudeCodeAdapter
AntigravityAdapter
```

are target backends.

They consume resolved semantic state.

They do not determine source meaning.

This gives:

```text
front-end
    plugin parsing / validation

middle-end
    composition / binding / capability resolution

back-end
    harness lowering / materialization
```

Use this mental model when deciding ownership.

---

# 50. Do not confuse HarnessAdapter with model adapter

A harness may use multiple models.

Model identity is orthogonal to harness identity.

For example, do not assume:

```text
Copilot == one model
Antigravity == one Gemini model
```

The Factory primarily targets harness semantics.

Model selection may be a host capability/policy.

Keep:

```text
Harness
Model
```

separate.

---

# 51. Do not confuse MCP with harness

MCP is an extension/tool protocol.

It is not the harness.

A harness may expose MCP.

A plugin may package MCP configuration.

A capability may be implemented through an MCP server.

Maintain:

```text
Capability
    semantic operation

CapabilityProvider
    implementation

MCP
    possible provider transport/interface

Harness
    execution/configuration environment
```

---

# 52. Hooks are not universally equivalent

Hooks deserve their own semantic audit.

Different harnesses may expose events at different lifecycle points or permit different actions.

Before attempting portable hooks, build:

```text
Hook Event Matrix
```

For example:

```text
session start
session end
before tool
after tool
permission decision
prompt submission
subagent lifecycle
...
```

Classify equivalents carefully.

Do not create a fake universal hook contract that loses critical differences.

---

# 53. Portable hook semantics only where real intersection exists

If some hook semantics are genuinely common, model them canonically.

Otherwise preserve host-specific hooks.

Prefer:

```text
small truthful portable core
+
host extensions
```

over:

```text
large misleading abstraction
```

---

# 54. Agents/subagents require the same treatment

Build an Agent Capability Matrix.

Investigate:

```text
custom agent definition
isolated context
tool selection
model selection
reasoning level
memory
nested agent spawning
parallelism
return contract
agent-specific skills
agent-specific policies
```

Do not assume `agent` means the same thing in every harness.

---

# 55. Preserve semantic role ownership independently from native agent support

The Factory's `AgentDefinition` is semantic.

A target harness may represent it as:

```text
native custom agent
subagent profile
prompt fragment
skill
runtime configuration
```

depending on host capabilities.

The adapter should explicitly report fidelity.

Do not redefine the canonical agent merely to match the target.

---

# 56. Harness conformance tests

Create adapter conformance tests.

A HarnessAdapter should be testable against a canonical fixture containing:

```text
plugin metadata
skill
agent
agent contribution
MCP capability
policy
host extension
```

Then test:

```text
parsing
lowering
materialization
validation
loss reporting
round-independent determinism where applicable
```

Do not depend only on expensive live LLM tests.

---

# 57. Validation levels

Keep three validation levels.

## L0 — static

No model invocation.

Examples:

```text
schema validation
file structure
manifest validity
references
binding
capability resolution
adapter lowering
native config syntax
```

## L1 — harness smoke

Minimal live invocation.

Examples:

```text
plugin loads
skill visible
MCP exposed
agent visible when applicable
```

## L2 — behavioral

Model-driven behavior.

Examples:

```text
skill routing
agent routing
workflow behavior
tool use
cost
quality
```

Use L0 heavily.

Use L1 sparingly.

Use L2 only when semantic behavior cannot be established statically.

---

# 58. Codex-first evaluation policy remains valid

The local environment has more available Codex quota than Copilot quota.

Preserve the existing cost policy:

```text
static checks
    → deterministic/local

large behavioral corpus
    → preferably Codex

optimization experiments
    → preferably Codex

Copilot-specific conformance
    → Copilot

Claude-specific conformance
    → Claude when available

Antigravity-specific conformance
    → Antigravity when available

cross-harness sample
    → smallest representative subset on every target
```

Do not burn scarce harness quota merely to prove harness-independent behavior.

---

# 59. Do not install Claude/Antigravity blindly

If Claude Code or Antigravity are not currently installed/authenticated:

do not automatically install them unless required and safe.

First complete:

```text
documentation research
adapter contract
static fixture
capability model
```

Then report what live validation would require.

The user may choose when to install/authenticate additional harnesses.

---

# 60. Materialization remains disposable

For all harnesses:

```text
canonical source
        ↓
EffectiveSystem
        ↓
HarnessAdapter
        ↓
generated native state
```

Generated state is disposable.

Deleting:

```text
generated Copilot profile
generated Codex profile
generated Claude config
generated Antigravity config
```

must not delete canonical plugin semantics.

Re-materialization should reconstruct state.

---

# 61. Avoid global configuration mutation during development

Prefer:

```text
temporary directories
worktrees
explicit plugin paths
explicit config paths
ephemeral runs
project-local state
```

where hosts allow them.

Global mutation such as:

```text
~/.copilot
~/.codex
~/.claude
Google user configuration
```

should be explicit and separated from tests whenever possible.

---

# 62. Adapter installation is not plugin installation

Distinguish:

```text
Plugin installed in Factory store

Plugin active in Profile

EffectiveSystem generated

Harness projection generated

Projection installed/activated in native host
```

Do not collapse these lifecycle steps.

This is necessary for deterministic testing.

---

# 63. Harness-specific validation state

Track something conceptually similar to:

```text
ProjectionStatus

NOT_MATERIALIZED
MATERIALIZED
VALIDATED_STATIC
SMOKE_VERIFIED
BEHAVIOR_VERIFIED
FAILED
UNSUPPORTED
```

Do not claim:

```text
works on Antigravity
```

because an Antigravity folder was generated.

---

# 64. Preserve provenance

For every generated host artifact, it should be possible to determine:

```text
source plugin
source contribution
EffectiveSystem revision/hash
HarnessAdapter version
target harness
target version
profile
```

This makes debugging portable composition feasible.

---

# 65. Explain host-specific decisions

Factory inspection tooling should eventually answer:

```text
Why was this generated?

Which plugin contributed it?

Which semantic binding caused it?

Which host extension influenced it?

Why was this primitive lowered differently on Codex?

Why is it unsupported on Claude?

Why is this shared across Antigravity surfaces?
```

Do not hide adapter decisions.

---

# 66. Antigravity SDK is evidence about architecture, not a Factory dependency

If research confirms that Google exposes an SDK around the same Antigravity harness, treat that as strong evidence that:

```text
surface != harness
```

and that Antigravity can be modeled at the harness level.

Do NOT add the Antigravity SDK as a required dependency of Plugin Factory simply because it exists.

Use it only if/when live integration requires it.

---

# 67. Artifacts, subagents, telemetry: learn, do not absorb blindly

Antigravity and other harnesses may expose interesting concepts such as:

```text
artifacts
dynamic subagents
trajectory state
telemetry
scheduled tasks
multi-workspace projects
```

These are valuable research inputs.

But this workspace is Plugin Factory.

Do not absorb runtime concepts into the Factory unless they materially affect:

```text
plugin definition
plugin composition
host projection
host validation
evaluation
```

Record interesting runtime ideas separately if needed, but do not scope-creep.

---

# 68. First implementation goal is NOT four full adapters

Do not attempt to fully implement all four harnesses immediately.

A better sequence is:

```text
1. understand all four enough to avoid a bad abstraction

2. stabilize canonical package + EffectiveSystem boundaries

3. make Copilot adapter correct

4. make Codex adapter correct

5. define Claude adapter contract from verified docs

6. define Antigravity adapter contract from verified docs

7. implement additional live adapters when environment is available
```

The four-harness research informs architecture now.

It does not require four complete implementations now.

---

# 69. Use Copilot + Codex as reference implementations

Because both are currently installed/authenticated, use them as the first real proof that:

```text
one canonical plugin composition
```

can become:

```text
two native harness projections
```

without:

```text
duplicated plugin source
semantic drift
manual patch scripts
```

The core proof should be:

```text
same Source Plugins
same Profile
same EffectiveSystem
        │
        ├── Copilot lowering
        └── Codex lowering
```

with explicit host-specific extensions where needed.

---

# 70. Agent Plugins standard compatibility test

Create a specific architectural investigation.

Determine whether Plugin Factory can structure its canonical plugin package as:

```text
Agent Plugins compatible package
+
Factory-specific semantic extension
+
host-specific extensions
```

Conceptually:

```text
plugin.json
skills/
mcp.json

extensions:
    plugin-factory: ...
    com.github.copilot: ...
    com.openai: ...
    ...
```

Only use extension namespaces permitted by the standard.

Do not invent invalid schema content.

If the standard cannot represent Factory metadata directly, investigate sidecar metadata while keeping the portable plugin valid.

Document the tradeoff.

---

# 71. Do not fork standards unnecessarily

Decision order:

```text
1. standard primitive
2. standard extension mechanism
3. compatible sidecar metadata
4. Factory-specific format only if necessary
```

This principle should guide package design.

---

# 72. Distinguish packaging interoperability from semantic interoperability

A package being installable in two harnesses is not enough.

Plugin Factory should ultimately measure:

```text
package compatibility
projection compatibility
semantic fidelity
behavioral portability
```

These are different.

For example:

```text
skill file accepted by both hosts
```

is package compatibility.

Whether both hosts route and execute that skill similarly is behavioral portability.

Do not conflate them.

---

# 73. Future portability report

Prepare the architecture so the Factory could eventually produce:

```text
plugin portability report

Copilot
    package: supported
    skills: exact
    agents: native
    hooks: native
    capability X: native

Codex
    package: supported
    skills: exact
    agent Y: lowered
    hook Z: unsupported

Claude Code
    ...

Antigravity
    ...
```

Do not build a polished UI now.

Ensure the data model can support the explanation.

---

# 74. Keep Plugin Factory ABI very small

Do not respond to multi-harness complexity by creating a giant universal ontology.

The Factory ABI should contain only distinctions required for stable composition.

Avoid reproducing every host setting.

Host settings belong in host extensions.

Canonical semantics should remain small.

---

# 75. Core portability principle

Use this rule when deciding where a field belongs:

> If changing harness should not change the meaning of the field, it is a candidate for canonical semantics.

> If the field only exists because a particular harness exposes a feature or syntax, it belongs in that harness extension.

Examples:

```text
responsibility=construction
    canonical

skill binding
    canonical

Copilot-only reasoning field
    Copilot extension

Codex sandbox flag
    Codex extension

Antigravity SDK-specific config
    Antigravity extension
```

---

# 76. No silent semantic synthesis

If a target host lacks a concept:

do not invent a fake equivalent merely so projection succeeds.

Return:

```text
unsupported
partial
approximation
```

and let policy decide whether projection is acceptable.

---

# 77. Projection policy

Prepare for two projection policies:

```text
strict
best-effort
```

## strict

Fail when required semantics cannot be represented.

## best-effort

Materialize representable semantics and emit explicit diagnostics.

Do not silently make best-effort the default for critical plugin behavior.

---

# 78. Required vs optional host semantics

A plugin may eventually declare:

```text
required semantic feature
optional enhancement
host-specific enhancement
```

For example, a host extension may be optional.

A capability necessary for plugin correctness may be required.

Projection must distinguish them.

---

# 79. Keep evaluation harness-neutral

Behavioral evaluation scenarios should be described independently from host invocation whenever possible.

Example:

```text
scenario:
    given plugin X
    task Y
    expected semantic behavior Z
```

Then:

```text
CopilotRunner
CodexRunner
ClaudeRunner
AntigravityRunner
```

execute the same scenario.

Avoid encoding:

```text
run `copilot ...`
```

inside the canonical scenario definition.

---

# 80. Keep HarnessRunner separate from HarnessAdapter

This is an important distinction.

## HarnessAdapter

Transforms configuration/plugin semantics.

## HarnessRunner

Executes scenarios through the harness.

Conceptually:

```text
HarnessAdapter
    compile/materialize

HarnessRunner
    invoke/observe
```

Do not conflate them.

This helps testing and evaluation.

---

# 81. SurfaceRunner may be useful

When one harness has several surfaces, runners may legitimately differ:

```text
AntigravityAdapter
    one semantic adapter

AntigravityCLIRunner
AntigravitySDKRunner
```

if invocation differs.

Likewise other harnesses may have:

```text
CLI runner
cloud runner
SDK runner
```

This is much cleaner than duplicating adapters.

Only introduce these classes if required by real implementation.

---

# 82. The key type distinction becomes

Conceptually:

```text
HarnessAdapter
    semantic lowering

HarnessRunner
    execution interface

Surface
    concrete invocation environment
```

This should be documented.

---

# 83. Measurement must identify harness AND surface

A run record should eventually be able to say:

```text
harness: antigravity
surface: cli

or

harness: antigravity
surface: sdk
```

rather than treating them as unrelated systems.

This will make cross-surface comparison possible.

---

# 84. Cross-harness evaluation

The same plugin/profile should eventually be testable as:

```text
EffectiveSystem
      │
      ├── Copilot
      ├── Codex
      ├── Claude Code
      └── Antigravity
```

Measure:

```text
semantic fidelity
task success
routing correctness
tokens
latency
tool calls
context load
failures
```

Only where metrics are actually available.

Unknown values remain UNKNOWN.

Never fabricate comparable token accounting when hosts expose different accounting models.

---

# 85. Keep quotas distinct from tokens

Where host subscription quotas exist:

```text
token usage
```

and:

```text
subscription quota consumption
```

are distinct measurements.

Do not treat quota consumption as equivalent to tokens.

Record separately where accessible.

---

# 86. Tool/context bloat remains a primary metric

A trivial harness invocation should not unnecessarily load every plugin/tool/MCP.

For each projection, eventually measure:

```text
plugins active
skills visible
skills loaded
MCP servers loaded
tools exposed
tool schema tokens
system/context tokens
```

This is one of the main reasons for progressive Plugin Factory composition.

---

# 87. Plugin activation must remain selective

Do not implement:

```text
install plugin
    ⇒ inject everything
```

Instead preserve:

```text
AVAILABLE
INSTALLED
ACTIVE
BOUND
MATERIALIZED
```

and runtime loading distinctions.

---

# 88. Current work order

Proceed approximately in this order.

## Phase A — Inspect current repository

Establish current facts.

## Phase B — Verify portable Agent Plugin standards

Investigate Agent Plugins 1.0 and host extension mechanisms.

## Phase C — Research four harnesses

Build capability matrix from official sources.

## Phase D — Refine canonical ontology

Add:

```text
Ecosystem
Harness
Surface
HarnessAdapter
HarnessRunner
HostExtension
projection fidelity
```

only as required.

## Phase E — Review existing package format

Determine what should remain portable standard versus Factory-specific metadata.

## Phase F — Stabilize EffectiveSystem

Ensure it preserves semantic composition and host extensions.

## Phase G — Refine Copilot lowering

Use native features rather than lowest-common-denominator behavior.

## Phase H — Refine Codex lowering

Use native features appropriately.

## Phase I — Static Claude Code adapter specification

Use verified official semantics.

## Phase J — Static Antigravity adapter specification

Use verified shared-harness semantics.

## Phase K — Conformance tests

Ensure adapters cannot silently lose required semantics.

---

# 89. Do not rewrite before producing research artifact

Before substantial adapter refactoring, create a concise authoritative analysis containing:

```text
CURRENT PORTABLE STANDARD

COPILOT NATIVE MODEL

CODEX NATIVE MODEL

CLAUDE CODE NATIVE MODEL

ANTIGRAVITY NATIVE MODEL

COMMON PORTABLE PRIMITIVES

HOST-SPECIFIC PRIMITIVES

HARNESS VS SURFACE MAP

PROPOSED FACTORY BOUNDARY

PROJECTION GAPS

RECOMMENDED IMPLEMENTATION SEQUENCE
```

This prevents speculative implementation.

---

# 90. Research artifact must cite sources

For every volatile harness capability include:

```text
source URL
source title
access/check date
```

Prefer current official documentation.

Do not base architecture-critical behavior solely on:

```text
blog posts from third parties
Stack Overflow
Reddit
old GitHub issues
memory
```

Those may supplement but not define canonical behavior.

---

# 91. Preserve current working mechanisms where sound

Do not rewrite `pluginctl`, profile resolution, or materialization simply because new terminology is cleaner.

Audit them.

Map existing mechanisms to new ontology.

Classify each as:

```text
correct and reusable
correct but misnamed
partially correct
too host-coupled
obsolete
```

Prefer migration over replacement.

---

# 92. Existing Copilot/Codex work should become first proof

The immediate engineering milestone should be:

```text
one source plugin composition
        ↓
one EffectiveSystem
        ↓
Copilot-native projection
        +
Codex-native projection
```

without source duplication.

Once this is sound, Claude Code and Antigravity can become additional targets.

---

# 93. No manual cross-harness scripts after every plugin change

A plugin activation/change should conceptually cause:

```text
PluginSet changes
      ↓
Factory resolve
      ↓
EffectiveSystem hash changes
      ↓
affected projections become stale
      ↓
materialize requested targets
```

not:

```text
./fix-copilot.sh
./fix-codex.sh
./fix-claude.sh
./fix-google.sh
```

Harness adaptation is deterministic Factory behavior.

---

# 94. Incremental rebuild later, correctness first

Do not prematurely implement sophisticated incremental compilation.

Initially:

```text
resolve cleanly
materialize deterministically
```

is enough.

However preserve stable hashes/provenance so incremental rebuilds can later determine which projections are stale.

---

# 95. No LLM in deterministic compilation

The following must remain deterministic:

```text
manifest parsing
schema validation
plugin dependency resolution
semantic trait matching
binding cardinality
capability resolution
projection selection
file generation
staleness calculation
```

LLMs may help:

```text
author plugins
review portability
suggest mappings
evaluate behavior
```

but must not define canonical compile semantics.

---

# 96. Architectural invariants

Treat these as candidate canonical invariants and validate them against implementation.

1. Plugins are independently authored.

2. Generic plugins depend on Plugin Factory contracts, not peer implementations.

3. Cross-plugin dependencies must be explicit.

4. Cross-plugin canonical source mutation is forbidden.

5. Generic contributions bind through semantic contracts.

6. Binding is deterministic.

7. Ambiguity is explicit.

8. Agent source files do not contain the final global skill surface.

9. Installed != active != bound != loaded.

10. Capability provision != authorization != exposure != invocation.

11. Portable semantics and host-specific extensions coexist.

12. Harness != Surface.

13. One shared harness should normally have one semantic adapter.

14. Surface-specific invocation does not require duplicating semantic lowering.

15. Source Plugin != EffectiveSystem.

16. EffectiveSystem != Harness Materialization.

17. Harness materializations are disposable.

18. HarnessAdapter != HarnessRunner.

19. Host-native strengths must not be discarded for portability.

20. Projection loss must be explicit.

21. Existing standards are preferred over proprietary reinvention.

22. Deterministic work does not require an LLM.

---

# 97. Non-goals

Do NOT:

```text
introduce Substrat
introduce Graphd

design runtime orchestration infrastructure

build a universal runtime

implement every coding-agent harness

support every IDE

create a giant semantic ontology

mirror every CLI flag in canonical IR

duplicate source plugins per harness

create pairwise plugin adapters

silently discard host-specific behavior

treat user surfaces as separate harnesses without evidence

rewrite the entire repository

push changes
```

---

# 98. Testing requirements

Add or update deterministic tests covering at least:

```text
source plugin parses independently

two independent plugins compose

semantic late binding works

ambiguous binding fails clearly

profile resolves intentional ambiguity

capability provider resolution is deterministic

host extension survives EffectiveSystem construction

host extension does not leak into unrelated adapter

Copilot lowering preserves Copilot extension

Codex lowering preserves Codex extension

unsupported semantic feature produces diagnostic

strict projection rejects missing required semantic feature

best-effort projection records degradation

materialization is reconstructible

plugin source remains unchanged after projection

adapter result does not depend on plugin installation order

surface choice does not alter canonical semantics

one harness with two surfaces reuses semantic adapter

HarnessRunner invocation configuration does not mutate EffectiveSystem
```

Add live tests only where justified.

---

# 99. Required architecture report

At the end provide:

```text
CURRENT REPOSITORY STATE

CURRENT PORTABLE PLUGIN STANDARD

PLUGIN FACTORY ONTOLOGY

PLUGIN FACTORY ABI

SOURCE PACKAGE MODEL

EFFECTIVE SYSTEM MODEL

ECOSYSTEM / HARNESS / SURFACE MODEL

HARNESS CAPABILITY MATRIX

COPILOT FINDINGS

CODEX FINDINGS

CLAUDE CODE FINDINGS

ANTIGRAVITY FINDINGS

PORTABLE PRIMITIVES

HOST-SPECIFIC PRIMITIVES

ADAPTER ARCHITECTURE

RUNNER ARCHITECTURE

PROJECTION FIDELITY MODEL

CHANGES MADE

FILES CHANGED

TESTS EXECUTED

EVIDENCE

UNRESOLVED QUESTIONS

NEXT SMALLEST COHERENT SLICE
```

Do not claim support that was not verified.

---

# 100. Final success criterion

The Plugin Factory architecture is healthy when the following statement is true:

> An independently authored Agent Plugin can describe its portable expertise and explicit host-specific enhancements without knowing which other plugins are installed or which concrete agents those plugins define.

Then:

```text
Plugin Factory
```

can deterministically:

```text
compose plugins
resolve dependencies
perform semantic late binding
resolve capabilities
construct one EffectiveSystem
```

and project that same EffectiveSystem toward:

```text
Copilot
Codex
Claude Code
Antigravity
```

while:

```text
preserving native harness capabilities
reporting semantic loss
avoiding duplicated plugin sources
keeping harness-generated state disposable
```

The goal is not maximum abstraction.

The goal is the smallest architecture that gives us:

```text
independent plugins
+
deterministic composition
+
semantic portability
+
native harness power
+
future extensibility
```

Build the foundation carefully before adding more plugins or more harness targets.
