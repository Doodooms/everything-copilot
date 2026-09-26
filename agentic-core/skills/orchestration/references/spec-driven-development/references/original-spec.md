# Mission

Implémente un skill `spec-driven-development` destiné à l’agent `orchestrator`.

Ce skill doit transformer le workflow multi-agent existant en un processus Spec-Driven Development où :

```text
user intent
    ↓
canonical specification
    ↓
architecture when required
    ↓
implementation plan + tasks
    ↓
implementer + TDD
    ↓
QA adversarial falsification
    ↓
reviewer acceptance gate
    ↓
convergence against specification
```

La **specification est la source canonique de l’intention**.

Architecture, plan, tasks, implementation et evidence sont des artefacts dérivés de cette intention.

Ne remplace pas les responsabilités existantes des agents.

Le skill SDD est un **workflow de coordination de l’Orchestrator**, pas un super-agent qui réalise lui-même architecture, planning, implementation, QA ou review.

---

# 1. Sources méthodologiques

Utiliser GitHub Spec Kit comme référence conceptuelle, en particulier :

* `github/spec-kit`
* `docs/index.md`
* `docs/quickstart.md`
* `docs/reference/agentic-sdd.md`
* `docs/guides/evolving-specs.md`

Le workflow Spec Kit actuel est conceptuellement :

```text
Specify
→ Clarify
→ Plan
→ Checklist
→ Tasks
→ Analyze
→ Implement
→ Converge
```

Les quality gates intermédiaires sont facultatifs selon la complexité.

Ne copie pas mécaniquement ses prompts ou sa structure.

Adapte les concepts au système multi-agent existant.

---

# 2. Principe architectural fondamental

Dans ce repository :

```text
SDD
= outer development loop

TDD
= inner implementation loop
```

Donc :

```text
SPECIFICATION
      ↓
ARCHITECTURE
      ↓
PLAN / TASKS
      ↓
IMPLEMENTER
      │
      └── TDD
            red
             ↓
           green
             ↓
          refactor
      ↓
QA
      ↓
REVIEWER
      ↓
CONVERGENCE
```

Ne fusionne jamais SDD et TDD.

`spec-driven-development` appartient à `orchestrator`.

`tdd` appartient à `implementer`.

---

# 3. Responsabilités exactes

Respecter cette séparation.

## Orchestrator

Owns:

```text
user interaction
canonical specification
canonical task state
routing
artifact lifecycle
staleness/invalidation
handoffs
workflow gates
convergence state
Git lifecycle
```

Does NOT own:

```text
architecture decisions
implementation decisions
code
tests
QA
technical review
external technical research
operational implementation
```

---

## Architect

Owns:

```text
system semantics
domain ontology
architecture
component boundaries
data ownership
interfaces
dependency direction
technology/integration decisions
architectural invariants
```

Consumes:

```text
canonical specification
repository evidence
research packets if required
```

Must not rewrite product intent.

---

## Planner

Owns:

```text
implementation decomposition
task graph
dependencies
sequencing
acceptance mapping
validation obligations
delivery risks
```

Consumes:

```text
canonical specification
architecture decisions
repository constraints
```

Must not change architecture or product requirements.

---

## Implementer

Owns:

```text
production implementation
immediate regression tests
TDD loop
focused implementation validation
```

Consumes:

```text
specific task
specification requirements
acceptance criteria
architecture constraints
plan constraints
```

Must not alter the specification to fit the implementation.

---

## QA

Owns:

```text
independent falsification
spec-conformance testing
edge-case discovery
property/fuzz/mutation testing
security testing
performance testing
failure reproduction
failure minimization
test-surface strengthening
```

Consumes the specification independently from the Implementer's interpretation.

QA asks:

```text
Can I produce valid evidence that the implementation violates
the specification or that its tests fail to detect meaningful faults?
```

---

## Reviewer

Owns:

```text
final technical acceptance gate
```

Consumes:

```text
specification
architecture
plan
implementation diff
Implementer validation
QA evidence
remaining risks
```

Reviewer asks:

```text
Is the accumulated evidence sufficient to accept this implementation
as satisfying the specification and repository constraints?
```

Reviewer does NOT redo implementation or QA.

---

## Challenger

Owns independent adversarial review of materialized high-impact decisions.

Possible gates:

```text
high-impact specification
breaking architecture decision
irreversible architecture decision
dangerous migration
high-risk plan
```

The Challenger receives artifacts, not the proposal author's hidden reasoning.

---

## Researcher

Remains a context-isolation primitive.

Any specialist may call Researcher for expensive evidence gathering.

Researcher returns a compact evidence packet.

It never owns an SDD artifact decision.

---

## DevOps

Owns operational changes derived from the approved specification/plan:

```text
CI/CD
packaging
deployment
runtime configuration
release
observability
```

---

# 4. Canonical semantic model

Introduce explicit shared definitions.

Do not put generic dictionary definitions everywhere.

Definitions must affect interpretation, routing, skill discovery, or handoff semantics.

At minimum establish canonical meanings for:

```text
specification
requirement
acceptance criterion
constraint
non-goal
open decision

architecture decision
architectural invariant

implementation plan
task
dependency

validation
verification evidence
QA pass
review approval

material change
stale artifact
convergence
```

Recommended meanings:

## Specification

The canonical statement of:

```text
WHAT must be true
WHY it is required
observable requirements
constraints
acceptance criteria
non-goals
user-owned unresolved decisions
```

It should avoid implementation details unless they are themselves explicit requirements.

---

## Requirement

A stable, identifiable statement of required behavior or property.

Assign a stable ID:

```text
REQ-001
REQ-002
...
```

---

## Acceptance criterion

A falsifiable observable condition demonstrating satisfaction of one or more requirements.

Assign:

```text
AC-001
AC-002
...
```

Every acceptance criterion must reference its parent requirement(s).

---

## Architecture decision

A structural or technical decision defining HOW the system can satisfy the specification without becoming an implementation task.

Example ID:

```text
ADR-001
```

---

## Task

A bounded implementation unit derived from:

```text
requirements
+
architecture
+
plan
```

Every task should reference relevant:

```text
REQ-*
AC-*
ADR-*
```

---

## Validation

Execution of an evidence-producing check against a stated criterion.

---

## QA pass

No material violation was discovered within the adversarial scope actually exercised.

It does NOT mean final acceptance.

---

## Review approval

The Reviewer judges that specification conformance, implementation quality, QA evidence, residual risk, and repository constraints justify acceptance.

---

## Material change

A change that alters:

```text
required behavior
acceptance criteria
constraints
non-goals
architecture assumptions
public contract
```

Material changes may invalidate downstream artifacts.

---

## Stale artifact

An artifact whose upstream source changed materially after the artifact was produced or approved.

A stale artifact must not be treated as authoritative until reconciled.

---

## Convergence

The state where:

```text
all in-scope requirements are mapped
all required tasks are complete
all required acceptance criteria have evidence
QA has no unresolved material failure
Reviewer has approved
no required downstream artifact is stale
no blocking finding remains
```

---

# 5. Create the skill package

Create:

```text
.github/skills/spec-driven-development/
```

Follow the repository's current skill architecture and whatever canonical skill scaffolding already exists.

Do not invent a second skill architecture.

Conceptually the package needs:

```text
spec-driven-development/
├── SKILL.md
├── references/
│   ├── specification-workflow.md
│   ├── artifact-lifecycle.md
│   ├── convergence.md
│   └── handoff-contracts.md
├── assets/
│   └── specification-template.md
└── scripts/
    └── validate_sdd_state.py
```

Adjust exact paths to repository conventions.

Avoid unnecessary files.

---

# 6. SKILL.md responsibility

`SKILL.md` should remain relatively compact.

Its primary content should be:

```text
frontmatter
definitions
admission/routing
workflow overview
hard invariants
references loaded at point of need
```

Do not put all SDD methodology inline if progressive disclosure allows it to live in referenced support files.

---

# 7. Skill frontmatter

This is an Orchestrator capability, not primarily a user slash-command.

Prefer conceptually:

```yaml
name: spec-driven-development
description: "Coordinate specification-driven software delivery from canonical requirements through architecture, planning, implementation, QA, review, and convergence."
user-invocable: false
```

Do not hard-code unsupported frontmatter.

Validate against the current VS Code Agent Skills version.

The current VS Code Agent Skills mechanism supports project skill directories, progressive resource loading, `user-invocable`, `disable-model-invocation`, and optional forked contexts.

This SDD skill should normally run inline in the Orchestrator context because it governs the Orchestrator's persistent task state.

Do NOT use `context: fork` for the entire SDD workflow unless repository experimentation proves that desirable.

Research and other expensive isolated work belong in specialist subagents.

---

# 8. Admission / routing of SDD

The skill must not force full SDD ceremony onto every change.

## ACCEPT

Use SDD for work such as:

```text
new feature
material behavior change
cross-cutting refactor
migration
API change
multi-component change
user-visible workflow change
multi-agent delivery
work with several acceptance criteria
work where intent could drift across agents
```

## REJECT / lightweight path

Do not force full SDD for:

```text
trivial mechanical edit
formatting-only change
obvious one-line maintenance
pure research request
pure documentation request
already-isolated tiny defect where full specification adds no value
```

Return control to the Orchestrator so it can select the minimal workflow.

---

# 9. Specification artifact

Do not create a competing specification system if the Orchestrator already has a task manifest.

Inspect the existing orchestration data model first.

Extend the existing canonical task state rather than creating parallel truth.

A task/feature should have one canonical specification artifact or specification section.

Recommended logical schema:

```yaml
specification:
  id: SPEC-...
  revision: 1
  status: draft | ready | blocked

  objective: ...

  user_intent: ...

  requirements:
    - id: REQ-001
      statement: ...
      rationale: ...
      priority: must | should | could

  acceptance_criteria:
    - id: AC-001
      requirements: [REQ-001]
      statement: ...

  constraints:
    - ...

  non_goals:
    - ...

  open_decisions:
    - ...

  assumptions:
    - ...
```

The actual serialization may be Markdown with structured headings if that better fits the repository.

Prefer human-readable Markdown plus deterministic parsing only where necessary.

---

# 10. Specification workflow

Implement this phase before architecture/planning.

## Step A — Extract

From the user request derive:

```text
objective
observable behavior
requirements
constraints
non-goals
acceptance criteria
known assumptions
open decisions
```

Do not invent unresolved user-owned decisions.

---

## Step B — Clarify

Ask the user only when an unresolved decision materially changes:

```text
product behavior
scope
architecture possibilities
acceptance criteria
risk
```

Do not ask about decisions safely derivable from repository conventions or technical evidence.

---

## Step C — Normalize

Assign stable IDs:

```text
REQ-*
AC-*
```

Ensure each criterion is falsifiable where practical.

---

## Step D — Validate specification quality

Check:

```text
requirements are not contradictory
acceptance criteria cover required behavior
acceptance criteria are observable
implementation details are not masquerading as requirements
non-goals are explicit when scope boundaries matter
open user decisions are not silently resolved
```

Do not dispatch architecture or planning while specification status is `blocked`.

---

# 11. Specification revision model

The spec is a living contract.

Any material requirement change MUST update the canonical specification first.

Process:

```text
material change discovered
      ↓
Orchestrator receives change
      ↓
update specification
      ↓
increment revision
      ↓
compute downstream impact
      ↓
mark impacted artifacts stale
      ↓
re-run owning phases
```

Never allow:

```text
implementation changes behavior
      ↓
spec silently left behind
```

---

# 12. Provenance

Record:

```text
spec revision
source user request
clarifications
timestamp/revision metadata according to repo conventions
```

Do not overwrite history if existing orchestration conventions support versioned/audited state.

Preserve enough provenance to explain why a requirement exists.

---

# 13. Architecture phase

After specification is `ready`, determine whether architectural work is required.

If no:

```text
architecture_status = not_required
```

If yes:

```text
Orchestrator
    ↓
Architect
```

Architect receives:

```text
spec revision
relevant REQ IDs
relevant AC IDs
repository context
existing architecture
constraints
```

Architect must output decisions traceable back to the spec.

Architecture artifacts should include:

```text
decision IDs
affected requirements
invariants
interfaces
boundaries
tradeoffs
assumptions
open architectural issues
```

The Architect must not change requirements.

If architecture reveals an impossible or contradictory requirement:

```text
Architect
→ blocker
→ Orchestrator
→ specification resolution
```

---

# 14. Challenger architecture gate

For high-impact/breaking/irreversible decisions:

```text
Architect
    ↓
materialized architecture proposal
    ↓
Orchestrator
    ↓
Challenger
```

Challenger receives:

```text
spec
proposal
constraints
supporting evidence
```

not the Architect's hidden reasoning.

The resulting challenge packet returns to:

```text
Orchestrator
→ Architect / user decision owner
```

Do not allow Challenger to make the final architecture decision.

---

# 15. Planning phase

Planner receives:

```text
spec revision
architecture revision/status
requirements
acceptance criteria
architecture decisions
repository constraints
```

Planner creates:

```text
ordered phases
tasks
dependencies
implementation targets
validation obligations
QA expectations
rollout/rollback considerations
```

Each task must reference relevant IDs.

Example:

```yaml
task:
  id: TASK-003
  requirements: [REQ-002]
  acceptance_criteria: [AC-003, AC-004]
  architecture_decisions: [ADR-001]
  depends_on: [TASK-001]
  owner: implementer
```

Avoid orphan tasks.

Every implementation task must explain what requirement it serves.

---

# 16. Plan consistency analysis

Before implementation, perform a cheap consistency gate.

Check:

```text
every MUST requirement has coverage
every acceptance criterion maps to planned work or existing behavior
every task maps to a requirement
architecture decisions required by tasks exist
task dependencies are resolvable
no task implements explicitly non-goal behavior
no stale architecture artifact is being consumed
```

Prefer deterministic scripts where possible.

This corresponds conceptually to Spec Kit's `analyze` phase but must respect this repository's agent boundaries.

The Orchestrator may perform structural consistency checks.

It must not perform technical architecture/review work itself.

---

# 17. Implementer handoff

Each implementation handoff must contain the smallest sufficient context:

```text
task ID
spec revision
relevant REQ IDs
relevant AC IDs
relevant ADR IDs
allowed scope/files/components
dependencies
validation obligations
known risks
```

Do not dump the full historical workflow into every agent context when unnecessary.

---

# 18. TDD integration

The Implementer should use a `tdd` skill for behavior changes where TDD is practical.

Expected inner loop:

```text
select acceptance behavior
      ↓
write/strengthen failing test
      ↓
confirm meaningful failure
      ↓
minimal implementation
      ↓
confirm pass
      ↓
refactor without changing behavior
      ↓
focused validation
```

Tests should reference or conceptually map to the relevant acceptance criterion.

Do not require one test per criterion mechanically.

The objective is traceability, not bureaucratic test naming.

---

# 19. Implementation constraints

Implementer may not resolve mismatches by editing upstream intent.

Forbidden:

```text
implementation difficult
→ weaken acceptance criterion

existing architecture inconvenient
→ silently ignore architecture decision

test fails
→ rewrite requirement
```

Instead:

```text
return blocker/deviation
→ Orchestrator
→ correct owner
```

---

# 20. QA phase

After Implementer completes a task/phase:

```text
Implementer
    ↓
QA
```

QA must receive the specification independently.

Its purpose is NOT:

```text
confirm Implementer's tests pass
```

Its purpose is:

```text
try to falsify specification conformance
```

QA strategy should derive attacks from:

```text
requirements
acceptance criteria
architecture invariants
implementation diff
existing tests
Implementer validation
risk profile
```

---

# 21. QA capabilities

QA may use skills such as:

```text
spec-conformance-testing
adversarial-testing
edge-case-generation
property-based-testing
fuzz-testing
mutation-testing
security-testing
performance-testing
integration-testing
failure-reproduction
failure-minimization
```

Only invoke specialized skills when relevant.

---

# 22. QA failure flow

When QA finds a material failure:

```text
QA
    ↓
defect packet
    ↓
Orchestrator
```

Defect packet:

```text
affected REQ/AC
expected behavior
actual behavior
minimal reproduction
command/environment
evidence
test assets
suspected ownership
```

Orchestrator routes to the correct owner.

Usually:

```text
Implementer
```

but possibly:

```text
Planner
Architect
DevOps
user/specification
```

depending on cause.

Then:

```text
owner fixes
→ QA again
```

---

# 23. Reviewer phase

Only invoke Reviewer after QA returns `pass`.

Reviewer evaluates accumulated evidence rather than repeating QA.

Required evidence:

```text
current spec revision
architecture decisions
plan/task state
implementation diff
Implementer validation
QA verdict
QA tests/evidence
resolved defect history
remaining risks
```

Reviewer verdict:

```text
approve
reject
blocked
```

---

# 24. Reviewer rejection flow

Do not hard-code:

```text
review reject → implementer
```

Instead:

```text
Reviewer finding
      ↓
suggested owner
      ↓
Orchestrator
      ↓
correct specialist
```

Examples:

```text
implementation defect → Implementer

test inadequacy → QA or Implementer

architecture violation → Architect

plan gap → Planner

spec ambiguity → Orchestrator/user

runtime/release issue → DevOps
```

After correction, repeat only the required downstream gates.

---

# 25. Convergence phase

Implement SDD convergence in the Orchestrator skill.

Important:

The Orchestrator must NOT independently inspect code and decide technical correctness.

Convergence is reconciliation of authoritative artifacts and specialist evidence.

Compute whether:

```text
all active requirements have coverage
all required tasks are complete
all acceptance criteria have evidence
all architecture decisions consumed are current
no downstream artifact is stale
QA has passed required surfaces
Reviewer approved required surfaces
no blocker remains
no unrequested material implementation remains
```

Outcome:

```text
CONVERGED
```

or:

```text
GAPS_FOUND
```

---

# 26. Gap categories

Classify convergence gaps.

Suggested categories:

```text
missing
partial
contradicts
unrequested
stale
blocked
```

Meaning:

```text
missing
= required behavior/work absent

partial
= requirement only partly satisfied

contradicts
= implementation/evidence conflicts with canonical intent

unrequested
= material behavior added without specification support

stale
= evidence/artifact predates material upstream change

blocked
= required proof cannot currently be obtained
```

---

# 27. Convergence loop

If gaps exist:

```text
convergence
    ↓
classify gap
    ↓
route to owning specialist
    ↓
update tasks/state
    ↓
execute required work
    ↓
QA
    ↓
Reviewer
    ↓
convergence again
```

Continue until:

```text
CONVERGED
```

or an unresolved blocker requires user input.

---

# 28. Staleness dependency graph

Represent logical dependencies:

```text
SPEC
  ↓
ARCHITECTURE
  ↓
PLAN
  ↓
TASKS
  ↓
IMPLEMENTATION
  ↓
QA EVIDENCE
  ↓
REVIEW EVIDENCE
```

This does not mean every change invalidates everything.

Implement dependency-aware invalidation.

For v1, conservative invalidation is acceptable if exact impact cannot be proven.

Examples:

```text
REQ changed
→ affected architecture/plan/tasks/evidence become stale

architecture decision changed
→ affected plan/tasks/implementation evidence become stale

plan sequencing changed without behavior change
→ implementation may remain valid but plan/task state changes

test-only QA improvement
→ spec/architecture/plan remain valid
```

---

# 29. Stable IDs and revisions

Use stable IDs so agents can communicate compactly.

Examples:

```text
SPEC-001@rev3

REQ-004

AC-007

ADR-002

TASK-013

DEFECT-004

QA-RUN-005

REVIEW-003
```

Do not create IDs simply for cosmetic bureaucracy.

IDs should improve:

```text
traceability
handoffs
dependency mapping
auditability
context compression
```

---

# 30. Canonical task state

Extend the Orchestrator's existing canonical task state.

Recommended conceptual structure:

```yaml
task:
  id: ...

spec:
  id: ...
  revision: ...
  status: ...

architecture:
  status: not_required | pending | ready | stale | blocked
  revision: ...

plan:
  status: pending | ready | stale | blocked
  revision: ...

tasks:
  total: ...
  completed: ...
  blocked: ...

implementation:
  status: ...

qa:
  status: pending | pass | fail | blocked

review:
  status: pending | approve | reject | blocked

convergence:
  status: pending | gaps_found | converged

open_findings: []

stale_artifacts: []

next_owner: ...
```

Reuse existing manifest/state formats rather than creating a duplicate if possible.

---

# 31. Artifact location

Inspect current Orchestrator support files first.

There must be ONE task root.

Do NOT create simultaneously:

```text
.github/sdd/
.github/plans/
.github/plan_history/
some other manifest store
```

unless repository architecture explicitly requires them.

If `.github/plan_history/<task-id>/` is already the canonical task location, extend it.

Conceptually:

```text
<task-root>/
├── spec.md
├── architecture.md         # optional
├── plan.md
├── state.*
├── evidence/
│   ├── implementation/
│   ├── qa/
│   └── review/
└── audit/
```

Adapt to existing contracts.

---

# 32. Deterministic validator

Create or extend a validator for SDD artifacts.

Example:

```text
scripts/validate_sdd_state.py
```

It should detect at minimum:

```text
duplicate IDs
missing requirement IDs
acceptance criteria referencing missing requirements
tasks referencing missing REQ/AC/ADR
completed tasks with missing required evidence
QA pass against stale implementation revision
review approval against stale QA evidence
converged state with open blockers
converged state with stale artifacts
unresolved required open decisions
```

Prefer deterministic validation over LLM reasoning for structural properties.

---

# 33. Coverage matrix

Generate a machine-readable or derivable matrix:

```text
REQ
 ↕
AC
 ↕
TASK
 ↕
implementation evidence
 ↕
QA evidence
 ↕
review status
```

Example:

```text
REQ-001
 ├─ AC-001
 │   ├─ TASK-003
 │   ├─ impl evidence
 │   └─ QA evidence
 └─ AC-002
     ├─ TASK-004
     └─ QA evidence
```

Use this matrix during convergence.

---

# 34. Material requirement changes during implementation

Implement this invariant:

```text
NO downstream agent may silently change the specification.
```

When Implementer/QA/Reviewer discovers that the spec should change:

```text
specialist
    ↓
return finding
    ↓
Orchestrator
    ↓
user clarification when needed
    ↓
spec revision
    ↓
staleness propagation
```

---

# 35. Agent definitions refactor

The current agent files use `<definitions>` inconsistently.

Refactor definitions so they provide actual ontological/semantic concepts relevant to:

```text
agent interpretation
agent routing
skill discovery
neighbor responsibility boundaries
```

Do NOT define:

```text
focused role
routing refusal
```

merely as procedural aliases.

Use definitions to establish domain meaning.

---

# 36. Introduce `<routing>`

Replace `Step 0 - CONFIRMATION` progressively with:

```xml
<routing>

## ACCEPT
...

## REJECT
...

</routing>
```

`<routing>` executes semantically before the workflow.

The workflow starts only after local admission accepts the task.

Definitions come BEFORE routing.

Canonical ordering:

```text
frontmatter

<definitions>
...
</definitions>

<routing>
...
</routing>

<role>
...
</role>

<rules>
...
</rules>

<workflow>
...
</workflow>
```

Adapt exact markup to existing lint conventions if necessary.

---

# 37. Orchestrator changes

Modify Orchestrator definitions to include concepts such as:

```text
canonical specification
requirement
acceptance criterion
canonical task state
material change
stale artifact
handoff
convergence
```

Add explicit ownership:

```text
Orchestrator owns SDD lifecycle.
```

Add SDD skill invocation for non-trivial feature/change workflows.

Replace:

```text
normalize user's intent into a falsifiable specification
```

with an explicit call/use of the `spec-driven-development` skill.

Add invariants:

```text
spec revision before downstream change
staleness propagation
evidence traceability
convergence required before completion
```

---

# 38. Architect changes

Definitions should include:

```text
architecture
ontology
semantic invariant
component boundary
integration boundary
technology decision
architecture decision
```

Routing ACCEPT:

```text
structural system decisions
domain semantics
topology
boundaries
technology decisions
architecture-affecting migrations
```

Routing REJECT examples:

```text
missing product requirement → Orchestrator
delivery sequencing → Planner
code mutation → Implementer
falsification → QA
acceptance → Reviewer
```

Architecture outputs must reference:

```text
spec revision
relevant REQ/AC IDs
```

Architect cannot alter spec.

---

# 39. Planner changes

Definitions:

```text
implementation plan
task
dependency
acceptance mapping
validation obligation
delivery phase
```

Routing ACCEPT:

```text
sequencing
decomposition
dependencies
task creation
validation planning
```

Routing REJECT:

```text
product intent → Orchestrator
architecture → Architect
implementation → Implementer
falsification → QA
acceptance → Reviewer
```

Every plan/task must trace to spec IDs.

---

# 40. Implementer changes

Definitions:

```text
implementation
TDD
regression test
implementation evidence
defect packet
approved scope
```

Explicitly define TDD as implementation method, not acceptance process.

Implementer must consume:

```text
spec revision
task ID
REQ/AC IDs
architecture constraints
```

It must return evidence against those IDs.

If implementation exposes a spec/architecture mismatch:

```text
STOP
→ return blocker
```

---

# 41. QA changes

Definitions:

```text
falsification
spec conformance
test adequacy
counterexample
defect
defect packet
QA pass
test surface
```

QA should explicitly prioritize:

```text
SPEC
over
Implementer's interpretation of SPEC
```

Add `spec-conformance-testing` as a primary skill concept.

QA results must identify affected:

```text
REQ
AC
```

when possible.

---

# 42. Reviewer changes

Definitions:

```text
technical acceptance
material finding
review approval
review rejection
residual risk
evidence sufficiency
```

Reviewer is the final technical gate.

It does not own product acceptance decisions that remain user-owned.

Review verdict must reference current:

```text
spec revision
QA run/evidence
implementation revision
```

A stale QA run cannot justify approval.

---

# 43. Challenger changes

Definitions:

```text
challenge
material proposal
assumption
failure mode
reversibility
disconfirming evidence
```

Allow challenge gates at:

```text
high-impact spec
architecture
plan
migration
breaking change
```

Do NOT invoke Challenger after every trivial decision.

---

# 44. Researcher changes

Definitions:

```text
research question
authoritative evidence
primary source
uncertainty
compatibility fact
research packet
```

Each research handoff should record what SDD artifact/question requested it.

Example:

```text
supports ADR-003
```

Researcher never modifies specification or architecture directly.

---

# 45. DevOps changes

Definitions:

```text
operational surface
deployment
runtime configuration
release
observability
rollback
operational evidence
```

Operational tasks should reference:

```text
TASK
REQ/AC where applicable
```

DevOps changes may require subsequent QA/Reviewer gates depending on risk.

---

# 46. TDD skill integration

If no TDD skill exists, create it separately.

Do NOT embed its entire methodology into the SDD skill.

Expected ownership:

```text
spec-driven-development
→ Orchestrator

tdd
→ Implementer
```

The SDD skill may state that implementation should use the repository-appropriate TDD capability where applicable.

---

# 47. QA skills

Do not put every testing method into `qa.agent.md`.

Prefer independent skills:

```text
spec-conformance-testing
adversarial-testing
property-based-testing
fuzz-testing
mutation-testing
security-testing
performance-testing
integration-testing
failure-reproduction
failure-minimization
```

QA definitions should prime these concepts semantically.

---

# 48. Reviewer skills

Likewise keep special review methodologies as skills:

```text
security-review
performance-review
API-compatibility-review
migration-review
language-specific-review
maintainability-review
```

Reviewer remains the owner of acceptance.

---

# 49. Documentation

Do not recreate a Documenter agent.

Documentation should remain a skill/capability executed by the appropriate modifying specialist when required by the plan.

However SDD must track:

```text
documentation impact
```

as part of task completion when documentation is necessary to satisfy the repository's truth.

---

# 50. Security

Do not recreate a dedicated security-audit agent.

Security exists at two distinct layers:

```text
QA
→ adversarial security testing

Reviewer
→ security review / trust-boundary inspection
```

The Orchestrator may require both for security-sensitive changes.

---

# 51. Bug handling

Do not force every bug through full SDD.

For unknown failure:

```text
Orchestrator
→ QA
→ reproduce/minimize
→ defect packet
```

If resulting correction is small and requirements are already known:

```text
Implementer
→ QA
→ Reviewer
```

If investigation reveals requirement/architecture changes:

```text
enter/re-enter SDD
```

---

# 52. Trivial change fast path

Implement a fast path for low-complexity work.

Example:

```text
small scoped maintenance
known desired behavior
no architecture impact
single clear acceptance criterion
```

The Orchestrator may create a lightweight specification and skip:

```text
Architect
Planner
Challenger
```

Then:

```text
Implementer
→ QA if risk warrants
→ Reviewer
```

SDD must reduce ambiguity, not create ceremony for its own sake.

---

# 53. Large features

For changes too large for one coherent spec/task context, support hierarchical decomposition.

Conceptually:

```text
parent specification
    ↓
sub-feature specs
    ↓
independent implementation loops
```

Do NOT implement this complexity unless existing workflows need it immediately.

Design IDs and references so it remains possible later.

---

# 54. Context minimization

Every specialist handoff should contain only:

```text
required spec slice
relevant architecture slice
relevant tasks
relevant evidence
current repository state
```

Do not repeatedly inject all historical artifacts.

The canonical state exists precisely so the Orchestrator can construct minimal context slices.

---

# 55. Source-of-truth hierarchy

Establish explicitly:

```text
user-approved intent
      ↓
canonical specification
      ↓
architecture
      ↓
plan/tasks
      ↓
implementation
      ↓
tests/evidence
```

When downstream reality conflicts with upstream intent:

```text
do NOT silently rewrite upstream truth
```

Escalate to its owner.

---

# 56. Completion invariant

The Orchestrator may declare SDD work complete only when:

```text
spec status = ready
required architecture current
required plan/tasks current
required tasks complete
required QA = pass
required Reviewer = approve
no blocking findings
no stale required artifacts
convergence = converged
repository lifecycle state recorded
```

---

# 57. Deterministic tests

Add tests for the SDD infrastructure without calling an LLM.

At minimum test:

```text
stable ID validation
requirement/AC references
task traceability
duplicate IDs
missing references
staleness propagation
spec revision invalidation
QA evidence revision compatibility
review evidence revision compatibility
convergence with gaps
invalid false convergence
valid convergence
```

---

# 58. Agent routing tests

Add/update routing fixtures for every changed agent.

Test near-boundary examples such as:

```text
"choose Kafka vs NATS"
→ Architect

"sequence the Kafka migration"
→ Planner

"implement TASK-004"
→ Implementer

"try to break the new consumer semantics"
→ QA

"decide whether evidence is sufficient to merge"
→ Reviewer

"look up current Kafka compatibility guarantees"
→ Researcher

"challenge the irreversible migration proposal"
→ Challenger

"change deployment rollout configuration"
→ DevOps
```

Also test incorrect Orchestrator routing and verify local agent rejection suggests the correct owner.

---

# 59. Semantic definitions tests

Because `<definitions>` are intended to improve local interpretation and routing, create evaluation cases around semantically adjacent terms.

Examples:

```text
architecture vs plan
validation vs QA pass
QA pass vs review approval
requirement vs implementation detail
failure reproduction vs implementation
security testing vs security review
```

These should later be candidates for Waza-based routing evaluation.

---

# 60. Implementation order

Implement in this order:

```text
1. Inspect existing Orchestrator state/manifest contracts.
2. Inspect current skill conventions and validators.
3. Define canonical SDD ontology.
4. Define canonical specification schema/template.
5. Extend canonical task state with SDD lifecycle fields.
6. Implement deterministic state/spec validator.
7. Implement staleness/invalidation logic.
8. Create spec-driven-development skill.
9. Add specification/clarification workflow.
10. Add architecture dispatch contract.
11. Add planning/task traceability contract.
12. Add implementation/TDD handoff contract.
13. Add QA evidence contract.
14. Add Reviewer gate contract.
15. Add convergence logic.
16. Refactor Orchestrator definitions/routing/workflow.
17. Refactor Architect definitions/routing.
18. Refactor Planner definitions/routing.
19. Refactor Implementer definitions/routing.
20. Refactor QA definitions/routing.
21. Refactor Reviewer definitions/routing.
22. Refactor Challenger definitions/routing.
23. Refactor Researcher definitions/routing.
24. Refactor DevOps definitions/routing.
25. Add deterministic tests.
26. Add routing fixtures.
27. Run existing validators/tests.
28. Document exact example workflow.
```

---

# 61. Example target workflow

The implementation should support a scenario like:

```text
USER
"Add multi-tenant project permissions."

ORCHESTRATOR
    ↓
spec-driven-development

SPEC rev1
REQ-001...
REQ-002...
AC-001...
AC-002...

    ↓

ARCHITECT
ADR-001 tenant ownership
ADR-002 permission boundary

    ↓

CHALLENGER
challenge critical authorization model

    ↓

ARCHITECT
final architecture

    ↓

PLANNER
TASK-001 schema
TASK-002 authorization layer
TASK-003 API enforcement
TASK-004 tests

    ↓

IMPLEMENTER
TASK-001 + TDD

    ↓

QA
attempt falsification

    ↓ fail

IMPLEMENTER
fix

    ↓

QA
pass

    ↓

REVIEWER
approve phase

    ↓

next task
...
    ↓

CONVERGENCE

all REQ/AC covered
no stale artifacts
QA pass
review approval

    ↓

ORCHESTRATOR
finalize PR/lifecycle
```

---

# 62. Example requirement change mid-workflow

Support:

```text
USER
"Actually project guests must also be able to comment."
```

Required behavior:

```text
Orchestrator
    ↓
update SPEC rev1 → rev2
    ↓
REQ/AC update
    ↓
mark impacted ADR/plan/tasks/evidence stale
    ↓
Architect if architecture affected
    ↓
Planner updates tasks
    ↓
Implementer
    ↓
QA
    ↓
Reviewer
    ↓
Convergence
```

Forbidden behavior:

```text
Implementer directly adds guest comments
while SPEC remains rev1
```

---

# 63. Example implementation discovery

Support:

```text
Implementer:
"The current storage model makes AC-004 impossible
without violating ADR-002."
```

Required flow:

```text
Implementer → blocked
Orchestrator
    ↓
Architect
    ↓
possibly user/spec clarification
    ↓
new revisions
    ↓
resume implementation
```

No downstream agent should resolve the contradiction silently.

---

# 64. Definition of Done

The implementation is complete only when all of the following are true:

```text
- spec-driven-development skill exists.
- SDD is owned by Orchestrator.
- canonical specification exists in task state.
- requirements and acceptance criteria have stable IDs.
- architecture/plan/tasks can trace to specification.
- material spec changes create revisions.
- downstream staleness is represented.
- Orchestrator cannot converge with stale required artifacts.
- Implementer consumes spec/task identifiers.
- TDD remains an Implementer method.
- QA independently falsifies spec conformance.
- Reviewer remains final technical gate.
- Challenger remains context-independent.
- Researcher remains evidence-only.
- agents use ontological definitions rather than procedural pseudo-definitions.
- Step 0 routing is replaced by explicit routing sections where compatible.
- local agents can reject incorrect Orchestrator routing.
- convergence is based on state + specialist evidence rather than Orchestrator self-review.
- structural validators have deterministic tests.
- no obsolete specialized responsibility is reintroduced as an agent.
```

---

# 65. Final implementation report

When finished, return:

```text
1. Files created.
2. Files modified.
3. Exact SDD artifact/state model.
4. Agent changes.
5. New definitions added per agent.
6. New routing behavior per agent.
7. Deterministic validators/tests added.
8. Skills referenced but not yet implemented.
9. Any incompatibility with current VS Code/Copilot skill syntax.
10. One concrete end-to-end example showing:
    User → Spec → Architect → Planner → Implementer/TDD
    → QA → Reviewer → Convergence.
```

Do not merely produce another design proposal.

Implement everything that can be implemented deterministically without requiring expensive model-evaluation runs.

Do not launch expensive routing/LLM evaluations automatically.

Preserve existing repository conventions and sources of truth whenever they already satisfy these requirements.
