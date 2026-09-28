# Objectif

Renforcer `agentic-workflow` sur quatre axes sans augmenter inutilement le nombre de skills ni déplacer les responsabilités entre agents :

```text
A. Utilisation systématique et efficace des skills
B. Conception experte et évaluation de la qualité des tests
C. SDD fondé sur une représentation sémantique explicite
E. Expertise fondamentale de conception d’implémentation
```

Principe transversal :

```text
agent ownership
    ↓
local skill policy
    ↓
appropriate methods
    ↓
tools
```

Une skill augmente la manière dont un agent exerce sa responsabilité.

Elle ne crée pas une nouvelle responsabilité.

---

# A — Local Skill Policy

## 1. Problème

Le système possède déjà de bonnes skills, mais leur existence ne garantit pas leur utilisation.

Aujourd’hui :

```text
agent receives task
    ↓
skill descriptions available
    ↓
model may or may not remember/select them
```

La cible devient :

```text
agent receives task
    ↓
agent-local skill resolution
    ↓
required skills loaded
conditional skills considered
discoverable skills remain available
    ↓
agent performs work
```

IMPORTANT :

```text
NO Orchestrator interception
NO handoff gate
NO separate routing agent
NO additional subagent call
```

La résolution appartient exclusivement à l’agent en cours d’exécution.

---

# 2. Ajouter une `skill_policy` aux agents

Étendre la représentation canonique/IR d’un agent.

Conceptuellement :

```yaml
skill_policy:

  required:
    - skill: tdd
      when: behavior-changing implementation that is testable

  conditional:
    - skill: implementation-design
      when: non-trivial local representation, state, algorithm or complexity decision

    - skill: performance-profiling
      when: an evidenced performance problem is in scope

  discoverable:
    - refactor-cleanup
```

Trois niveaux :

```text
REQUIRED
= the agent MUST load it when the stated condition holds

CONDITIONAL
= explicitly evaluate applicability

DISCOVERABLE
= normal semantic discovery
```

Ne pas inventer davantage de catégories en v1.

---

# 3. Compilation locale dans l’agent

Le compiler transforme cette policy en instructions directement dans l’agent effectif.

Par exemple :

```text
<agent-skills>

Before substantive work, evaluate the following skill policy
against the admitted task.

MUST:
- Load `tdd` for testable behavior-changing implementation.
- Load `test-design` when designing or materially changing tests.

CONSIDER:
- `implementation-design` for non-trivial representation,
  algorithmic, state-management, or complexity decisions.

...
</agent-skills>
```

L’agent exécute lui-même cette résolution.

Aucun autre agent n’intervient.

---

# 4. Placer la skill policy suffisamment tôt

Actuellement les règles sur les skills peuvent être trop éloignées du moment où l’agent commence son raisonnement.

Faire en sorte que l’ordre logique soit approximativement :

```text
definitions
routing
local skill policy
rules
workflow
```

ou intégrer explicitement la résolution des skills au début du workflow local.

Exemple :

```text
Step 0 — Resolve applicable methods.

1. Evaluate the local skill policy.
2. Load every matching REQUIRED skill.
3. Evaluate matching CONDITIONAL skills.
4. Continue with the specialist workflow.
```

Ce Step 0 appartient à l’agent.

Ce n’est pas une phase d’orchestration.

---

# 5. Policies initiales recommandées

## Orchestrator

```text
orchestrate
→ REQUIRED for multi-specialist workflow

spec-driven-development
→ REQUIRED for non-trivial product work

install-agent-plugin
→ CONDITIONAL when a required capability has no active provider
```

## Architect

```text
architecture-design
→ REQUIRED when producing/changing architecture

domain-modeling
→ CONDITIONAL for non-trivial domain semantics

api-design
→ CONDITIONAL for API contract design
```

## Planner

```text
implementation-planning
→ REQUIRED for non-trivial decomposition
```

## Implementer

```text
tdd
→ REQUIRED for testable behavior change

test-design
→ REQUIRED when tests must be designed or materially changed

implementation-design
→ CONDITIONAL for non-trivial implementation structure

refactor-cleanup
→ CONDITIONAL after behavior is correct
```

## Quality Assurance

```text
adversarial-testing
→ REQUIRED for post-implementation falsification

failure-analysis
→ REQUIRED for unknown runtime failure diagnosis

test-quality-review
→ CONDITIONAL when test adequacy is materially in question

security-testing
→ CONDITIONAL for dynamic security scope

performance-profiling
→ CONDITIONAL for evidenced performance scope
```

## Reviewer

```text
code-review
→ REQUIRED for completed code changes

test-quality-review
→ CONDITIONAL when tests materially support acceptance

security-review
→ REQUIRED for security-sensitive trust boundaries
```

## Challenger

```text
architectural-immune-system
→ REQUIRED for high-impact proposal challenge
```

## DevOps

```text
delivery-operations
→ REQUIRED for operational modifications
```

Researcher can retain mostly conditional research-method selection because the exact research modality is naturally task-dependent.

---

# 6. Static validation de la skill policy

Ajouter au linter :

```text
referenced skill exists
no duplicate policy entry
REQUIRED skill is exposed to the agent
plugin-projected skill is active before reference
no contradictory REQUIRED/DISCOVERABLE classification
conditions are non-empty and human-readable
```

Ne pas essayer de rendre le contenu sémantique de `when:` déterministe.

---

# 7. Runtime telemetry sans handoff

Si le harness expose les tool-call events, enregistrer :

```text
agent
task/run
available skills
skills actually loaded
load order
skill source
```

dans la télémétrie/audit du runtime.

NE PAS obliger l’agent à mettre cette information dans son handoff.

Le handoff reste un contrat métier entre spécialistes.

La télémétrie est une préoccupation du harness.

---

# 8. Evals de skill usage

Créer des scénarios où la skill attendue est connue.

Mesurer :

```text
required_skill_recall
unnecessary_skill_load_rate
task_success
token overhead
```

Exemples :

```text
behavior-changing bug
→ tdd + test-design expected

unknown runtime crash
→ failure-analysis expected

pure formatting cleanup
→ tdd NOT expected

security-sensitive API change
→ Reviewer security-review expected
```

Comparer avant/après Local Skill Policy.

---

# B — Expert Test Design

## 9. Créer une seule nouvelle skill fondamentale : `test-design`

Ne PAS créer :

```text
unit-testing
integration-testing
property-testing
mock-testing
fixture-testing
stateful-testing
...
```

comme skills globales.

Créer :

```text
test-design/
├── SKILL.md
└── references/
    ├── test-levels.md
    ├── equivalence-boundaries.md
    ├── properties-invariants.md
    ├── stateful-testing.md
    ├── test-doubles.md
    ├── integration-contracts.md
    └── concurrency.md
```

Un seul élément de discovery global.

---

# 10. Responsabilité exacte de `test-design`

`test-design` répond à :

> What is the smallest, strongest and most maintainable test surface capable of falsifying the intended contract?

Elle doit couvrir :

```text
observable contract
test oracle
invariants
equivalence classes
boundary conditions
negative space
state transitions
error paths
properties
metamorphic relations when useful
realistic integration boundaries
concurrency when relevant
fixture design
test doubles
failure specificity
implementation coupling
```

---

# 11. Invariants de `test-design`

Inclure notamment :

```text
A red test MUST fail for the intended reason.

Prefer behavioral contracts over implementation details.

Prefer the lowest test level that faithfully observes the contract.

Do not mock a boundary when the real boundary is cheap,
deterministic and materially important to the contract.

A test should have a plausible defect that makes it fail.

Do not assert language/framework guarantees unless the project
specifically wraps or changes those guarantees.

Cover dangerous negative space, not only representative happy paths.

Avoid tests whose primary effect is freezing internal structure.
```

---

# 12. Séparer clairement les responsabilités

```text
tdd
= WHEN/HOW to iterate red → green → refactor

test-design
= WHAT tests provide strong evidence

adversarial-testing
= independently search for counterexamples after implementation

test-quality-review
= assess whether the resulting test surface is actually adequate
```

Ces quatre concepts ne doivent pas se recouvrir.

---

# 13. Faire évoluer `test-coverage-review`

Refactorer progressivement :

```text
test-coverage-review
→ test-quality-review
```

Conserver temporairement un alias/migration si nécessaire.

Le nouveau concept ne doit pas être centré sur line/branch coverage.

Il évalue :

```text
behavioral sensitivity
assertion quality
boundary coverage
negative-path coverage
mutation resistance
test independence
fixture realism
implementation coupling
flakiness risk
maintainability
evidence gaps
```

Coverage quantitative reste une evidence secondaire.

---

# 14. Intégration agents

## Implementer

```text
TDD
+
test-design
```

lorsque l’implémentation nécessite des tests.

## QA

Utilise `test-quality-review` quand elle cherche une faiblesse du test surface.

Elle peut ensuite créer un test QA qui démontre cette faiblesse.

## Reviewer

Utilise `test-quality-review` pour juger la suffisance des preuves.

Reviewer ne crée pas les tests.

---

# 15. Eval de qualité des tests

Construire un petit benchmark interne avec :

```text
correct implementation
seeded defective implementations
hidden edge cases
mutants
```

Demander au système de concevoir les tests.

Mesurer :

```text
defect detection rate
mutation kill rate where practical
hidden-case detection
false assumptions introduced by mocks
brittleness
test count
execution cost
```

Comparer :

```text
baseline
vs
TDD only
vs
TDD + test-design
```

C’est cette évaluation qui doit déterminer si la skill apporte réellement quelque chose.

---

# C — Semantic / Ontology-Aware SDD

## 16. Ne pas créer un second système de spécification

Étendre le SDD actuel.

La canonical specification reste la source de vérité.

Ajouter un bloc optionnel :

```yaml
semantic_model:
  concepts: []
  relations: []
  states: {}
  events: []
  invariants: []
  terminology: []
```

Ne créer un artefact `DOMAIN-*` séparé que si la complexité future le justifie réellement.

---

# 17. Définir précisément ce qui appartient au SDD

Le SDD possède les **semantics du problème** :

```text
canonical concepts
meaning
identity where product-relevant
relationships
states
events
behavioral invariants
canonical terminology
```

Il répond :

```text
What exists?
What does it mean?
How are concepts related?
What states can exist?
What domain transitions/events matter?
What must never be violated?
```

---

# 18. Distinguer deux topologies

Le mot `topology` doit être désambiguïsé.

## Semantic topology — SDD

```text
graph of concepts and domain relationships
```

Exemple :

```text
Customer
  └── owns → Subscription
                 └── produces → Invoice
```

## Technical/system topology — Architect

```text
modules
services
processes
databases
queues
dependency direction
deployment/runtime boundaries
```

Le SDD ne doit PAS décider la topologie technique.

---

# 19. Admission du semantic model

Ne pas produire une ontologie pour chaque changement.

Activer lorsque la demande introduit ou modifie :

```text
domain concepts
entity relationships
lifecycle/state model
business invariants
canonical terminology
cross-component meaning
ambiguous domain language
```

Pour un changement trivial :

```text
semantic_model omitted
```

---

# 20. Réutiliser `domain-modeling`

Avant de créer une nouvelle skill, inspecter la skill existante `domain-modeling`.

Préférer la faire évoluer pour supporter deux contextes :

```text
SPECIFICATION MODE
→ extract and normalize product/domain semantics

ARCHITECTURE MODE
→ map canonical semantics into architectural boundaries
  without changing their meaning
```

Ainsi une seule skill globale couvre le sujet.

---

# 21. Modifier la frontière Architect / SDD

Après cette évolution :

```text
SDD / Orchestrator
= owns canonical product semantics in specification

Architect
= consumes those semantics and decides structural realization
```

Architect peut identifier :

```text
ambiguity
missing invariant
semantic contradiction
```

mais MUST return it to Orchestrator rather than silently rewriting the canonical semantic model.

---

# 22. Semantic traceability

Permettre aux exigences et décisions de référencer des concepts/invariants.

Exemple :

```yaml
requirements:
  - id: REQ-004
    concepts:
      - Subscription
    invariants:
      - INV-002
```

Puis :

```text
SPEC semantics
→ REQ
→ ADR
→ TASK
→ TEST
```

Ne pas rendre tous ces liens obligatoires immédiatement.

Commencer sur les décisions matérielles seulement.

---

# 23. Staleness

Étendre le calcul de staleness.

Exemple :

```text
INV-002 changes
    ↓
ADR using INV-002 becomes potentially stale
    ↓
tasks/tests derived from ADR become potentially stale
```

Utiliser la dependency graph existante.

Ne pas construire un deuxième moteur de dépendances.

---

# 24. `semantic.validate`

Créer éventuellement un tool déterministe minimal :

```text
semantic.validate
```

Il peut vérifier :

```text
duplicate concept IDs
unknown relation endpoints
unknown state references
duplicate canonical terms
dangling invariant references
invalid semantic IDs
```

Il NE décide PAS :

```text
whether the ontology is conceptually correct
whether the business invariant is appropriate
```

Ces questions restent du raisonnement.

---

# 25. Evals semantic SDD

Créer des cas où un mauvais modèle conceptuel produit ensuite de mauvais plans.

Exemples :

```text
same entity described under two names
implicit many-to-many relation
state transition omitted
business invariant hidden in prose
event confused with state
domain relation confused with technical dependency
```

Comparer :

```text
current SDD
vs
semantic-aware SDD
```

Mesurer notamment :

```text
requirement ambiguity detected
semantic contradictions
architecture reopen rate
implementation rework
test misunderstanding
traceability quality
```

---

# E — `implementation-design`

## 26. Une seule skill

Créer :

```text
implementation-design
```

Pas :

```text
data-structures
algorithms
design-patterns
complexity
```

comme quatre skills globales.

Structure :

```text
implementation-design/
├── SKILL.md
└── references/
    ├── data-structures.md
    ├── algorithms-complexity.md
    ├── design-patterns.md
    ├── state-machines.md
    └── concurrency-primitives.md
```

---

# 27. Mission

La skill aide l’Implementer à choisir la structure locale la plus simple satisfaisant les contraintes.

Méthode :

```text
1. Identify invariants.
2. Identify required operations.
3. Identify access/mutation patterns.
4. Identify complexity constraints.
5. Identify ordering/state/concurrency requirements.
6. Select the simplest representation satisfying them.
7. Only then consider a named pattern.
```

Règle centrale :

```text
DO NOT begin with a design pattern.

Begin with constraints, invariants and operations.
```

---

# 28. Data structures

La référence couvre la sélection selon :

```text
lookup
ordering
insertion/removal
iteration
uniqueness
priority
graph relations
memory
mutation
concurrency
```

Pas un cours encyclopédique.

Le modèle connaît déjà les structures.

La skill lui impose une meilleure méthode de sélection.

---

# 29. Algorithms

Même principe.

Faire raisonner sur :

```text
input size
expected complexity
worst-case behavior
memory complexity
incremental vs batch
online vs offline
exact vs approximate
determinism
parallelism
```

Ne pas encourager l’optimisation algorithmique lorsque les contraintes ne la nécessitent pas.

---

# 30. Design patterns

Présenter les patterns comme un vocabulaire de solutions, jamais comme une cible.

Règle :

```text
Use a named pattern only when it simplifies a recurring force
already demonstrated by the problem.
```

Éviter :

```text
pattern for the sake of architecture
factory around a single constructor
strategy with one strategy
repository wrapping trivial persistence
visitor without an actual traversal/extensibility problem
```

---

# 31. Admission locale

Chez Implementer :

```text
implementation-design
→ CONDITIONAL
```

Déclencheurs :

```text
non-trivial state model
important representation choice
algorithmic complexity
graph/tree/index structure
concurrency synchronization
multiple credible implementation structures
local design likely to affect maintainability/performance
```

Ne pas charger pour du glue code banal.

---

# 32. Reviewer

Reviewer peut charger `implementation-design` conditionnellement lorsqu’un choix local de structure est lui-même un risque matériel.

Ne pas en faire une skill REQUIRED du Reviewer.

Architect ne doit normalement pas l’utiliser : ses décisions sont couvertes par `architecture-design`.

---

# 33. Evals

Créer des tâches où plusieurs solutions sont fonctionnellement correctes mais diffèrent structurellement.

Exemples :

```text
linear scan vs indexed lookup
list vs set/map
state flags vs state machine
nested conditionals vs strategy/table dispatch
recursive vs iterative traversal
shared mutable state vs queue/message passing
```

Mesurer :

```text
correctness
unnecessary abstraction
complexity appropriateness
maintainability
performance where relevant
```

---

# Ordre d’implémentation

Implémenter :

```text
1. Local Skill Policy schema/IR.
2. Compiler rendering into agents.
3. Static skill-policy validation.
4. Skill invocation telemetry if harness supports it.
5. Skill-usage eval harness.

6. test-design.
7. test-quality-review migration.
8. Agent policy integration for testing.
9. Test-quality eval corpus.

10. Extend SDD specification schema with optional semantic_model.
11. Refactor/reuse domain-modeling.
12. Clarify SDD/Architect semantic ownership.
13. Add semantic.validate if useful.
14. Integrate semantic changes into staleness.
15. Semantic-SDD evals.

16. implementation-design.
17. Progressive references.
18. Implementer/Reviewer conditional admission.
19. Implementation-design evals.
```

Do not start by expanding the total number of skills.

The desired result is **fewer, deeper skills that are selected more reliably**.

---

# Definition of Done

A/B/C/E are complete when:

```text
essential skills are locally and reliably selected by their owning agent
no handoff is introduced for skill selection
skill invocation can be measured independently of specialist handoffs
test quality improves on adversarial/hidden defects
coverage is no longer treated as a sufficient proxy for test quality
specifications can represent non-trivial domain semantics explicitly
semantic changes participate in staleness
technical topology remains Architect-owned
implementation-design improves structural choices without encouraging pattern overuse
global skill-discovery noise remains tightly bounded
```
