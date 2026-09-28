Tu travailles dans le repository `agentic-workflow`.

Le système possède déjà un workflow SDD avec :

```text
user intent
→ specification
→ architecture
→ planning
→ implementation
→ QA
→ review
```

Je souhaite maintenant enrichir conceptuellement le SDD.

IMPORTANT :

Le but n’est PAS simplement d’ajouter les mots :

```text
ontology
semantics
taxonomy
topology
```

dans la specification.

Ces notions sont insuffisantes seules.

L’objectif est d’introduire une **modélisation explicite du problem space**, suffisamment rigoureuse pour que les décisions d’architecture, d’implémentation et de test soient dérivées d’un même modèle mental cohérent.

---

# 1. Problème à résoudre

Aujourd’hui un système agentique peut parfaitement :

```text
understand a requirement locally
produce a plausible architecture
write correct-looking code
write passing tests
```

tout en ayant construit une mauvaise représentation du problème.

La cause fondamentale peut être située très en amont :

```text
wrong concepts
wrong identity assumptions
wrong relationships
wrong state model
wrong invariants
wrong interpretation of unknown information
wrong abstraction/granularity
```

Dans ce cas, chaque étape aval peut être localement excellente mais globalement incorrecte.

Le SDD doit donc traiter explicitement :

> How is the problem world being modeled before the solution is designed?

---

# 2. Fundamental distinction

Introduire explicitement la séparation :

```text
PROBLEM SPACE
≠
SOLUTION SPACE
```

## Problem Space

Décrit :

```text
what exists
what it means
how things relate
how identity is preserved
what states can exist
what events can happen
what transitions are valid
what must remain true
what is known
what is assumed
what is unknown
```

## Solution Space

Décrit :

```text
modules
services
APIs
data structures
databases
queues
runtime topology
deployment
implementation
```

Le SDD établit d’abord le Problem Space.

Architect traduit ensuite ce modèle vers le Solution Space.

Architect MUST NOT silently redefine the Problem Space for implementation convenience.

---

# 3. Core conceptual model

Le SDD doit pouvoir raisonner explicitement sur les concepts suivants.

Ils ne sont pas tous obligatoires dans chaque specification.

Ils constituent le vocabulaire conceptuel disponible.

---

# 4. Ontology

Définition :

```text
Ontology
= what kinds of things, properties and relationships
  are considered to exist in the modeled domain.
```

L’ontologie répond :

```text
What kinds of things exist?
What distinctions matter?
Which relations are meaningful?
```

Exemple :

```text
Customer
Subscription
Invoice
Payment

Customer owns Subscription
Subscription produces Invoice
Invoice is settled by Payment
```

IMPORTANT :

L’ontologie est une abstraction du monde adaptée au problème.

Elle n’est pas nécessairement une description universellement vraie du réel.

Elle introduit volontairement un inductive bias.

---

# 5. Semantics

Définition :

```text
Semantics
= the precise meaning assigned to concepts,
  properties, relations, states and events.
```

Exemple :

```text
owns(Customer, Subscription)
```

doit avoir une signification précise.

Ne pas accepter des concepts dont la signification dépend implicitement du contexte.

Le SDD doit identifier les ambiguïtés sémantiques lorsque leur résolution influence le comportement.

---

# 6. Identity

Ajouter explicitement :

```text
identity
```

Différence fondamentale :

```text
IDENTITY
≠
STATE
```

Une entité peut changer d’état tout en restant la même entité.

Le modèle doit pouvoir exprimer :

```text
What makes this thing the same thing over time?
```

Exemple :

```text
Subscription identity
≠
subscription status
```

Cette distinction évite énormément d’erreurs de modélisation.

---

# 7. Granularity

Ajouter explicitement :

```text
granularity
```

Le problème doit être modélisé au niveau de détail nécessaire au raisonnement.

Exemple :

```text
Address as string
```

peut être suffisant.

Mais si le système doit raisonner sur :

```text
country
region
municipality
postal code
```

alors `Address` doit probablement devenir un concept structuré.

Le SDD doit éviter :

```text
over-modeling
```

et :

```text
under-modeling
```

Le niveau de granularité doit être justifié par les comportements/questions du système.

---

# 8. Taxonomy

Définition :

```text
Taxonomy
= classification / is-a hierarchy inside the ontology.
```

Exemple :

```text
PaymentMethod
├── Card
├── BankTransfer
└── Wallet
```

IMPORTANT :

```text
taxonomy
⊂ ontology
```

Une ontologie contient beaucoup plus que des `is-a`.

---

# 9. Relations

Le modèle doit expliciter les relations significatives.

Exemple :

```text
Customer owns Subscription
Invoice belongs_to Subscription
Payment settles Invoice
```

Pour une relation matérielle, considérer si nécessaire :

```text
direction
cardinality
temporality
ownership
optional/required participation
```

---

# 10. Mereology

Ajouter la distinction :

```text
is-a
≠
part-of
```

La méréologie modélise les relations partie/tout.

Exemple :

```text
Wheel part_of Car
```

n’est pas :

```text
Wheel is_a Car
```

Cette distinction doit être disponible lorsque le domaine contient des compositions significatives.

---

# 11. Semantic topology

Définir :

```text
Semantic topology
= graph structure formed by domain concepts and their relations.
```

Exemple :

```text
Customer
   │ owns
   ▼
Subscription
   │ generates
   ▼
Invoice
   │ settled_by
   ▼
Payment
```

IMPORTANT :

```text
semantic topology
≠
technical topology
```

Technical topology reste sous responsabilité Architect.

---

# 12. State

Définition :

```text
State
= values and relations considered true for a concept/entity
  at a given logical time.
```

Exemple :

```text
Subscription.status = active
Subscription.owner = Customer-123
```

---

# 13. Event

Définition :

```text
Event
= something that happens and may cause a state transition.
```

Exemple :

```text
PaymentSucceeded
SubscriptionCancelled
OrderShipped
```

Ne pas confondre :

```text
state
```

et :

```text
event
```

---

# 14. Transition

Définir :

```text
state_before
+
event/action
→
state_after
```

Les transitions importantes doivent pouvoir exprimer :

```text
preconditions
effects
failure conditions
```

---

# 15. Lifecycle / State machine

Lorsqu’un concept possède un lifecycle significatif, le modèle peut décrire :

```text
possible states
valid transitions
invalid transitions
terminal states
```

Exemple :

```text
trial
→ active
→ suspended
→ cancelled
```

---

# 16. Invariants

Définition :

```text
Invariant
= condition that must hold for every valid relevant state.
```

Exemple :

```text
A cancelled subscription cannot generate
a future billing period.
```

Les invariants doivent devenir des concepts first-class du SDD.

Ils constituent une source majeure pour :

```text
architecture constraints
implementation contracts
test properties
QA falsification
review acceptance
```

---

# 17. Preconditions and Postconditions

Les opérations importantes peuvent avoir :

```text
preconditions
operation/event
postconditions
```

Exemple :

```text
CancelSubscription
```

Precondition :

```text
subscription is cancellable
```

Postcondition :

```text
subscription.status = cancelled
future renewal disabled
```

---

# 18. Contracts

Définir :

```text
Contract
=
preconditions
+
postconditions
+
invariants
+
failure semantics
```

Les contrats décrivent les frontières comportementales.

Ils doivent pouvoir alimenter directement le testing.

---

# 19. Temporality

Le modèle doit pouvoir distinguer :

```text
current fact
historical fact
future expected state
valid-from
valid-until
observation time
```

Lorsque cela importe.

Ne pas représenter comme intemporel quelque chose dont la vérité dépend du temps.

---

# 20. Causality

Distinguer :

```text
A precedes B
```

de :

```text
A causes B
```

et de :

```text
A is required by B
```

Ne pas introduire de causalité implicite sans justification.

Le SDD peut représenter des relations causales lorsque leur distinction influence le comportement attendu.

---

# 21. Modality

Lorsque pertinent, distinguer :

```text
actual
possible
required
forbidden
```

Exemple :

```text
A cancelled subscription currently cannot renew.
```

vs :

```text
A subscription may be suspended.
```

vs :

```text
Every active subscription must have an owner.
```

Cela permet de distinguer état réel, possibilités et contraintes.

---

# 22. Epistemic model

C’est une partie critique.

Distinguer :

```text
WORLD STATE
```

de :

```text
WHAT THE SYSTEM CURRENTLY KNOWS ABOUT THE WORLD
```

Le SDD doit pouvoir représenter au minimum :

```text
FACT
ASSUMPTION
HYPOTHESIS
UNKNOWN
DECISION
```

Exemple :

```yaml
- id: ASM-003
  type: assumption
  statement: >
    A customer can have only one active subscription.
  source: inferred-from-request
  status: unconfirmed
```

Une assumption MUST NOT silently become an invariant.

---

# 23. False ≠ Unknown

Introduire explicitement :

```text
false
≠
unknown
```

L’absence d’une information ne doit pas automatiquement être interprétée comme sa négation.

Lorsque pertinent, considérer :

```text
known true
known false
unknown
not applicable
```

---

# 24. Provenance

Une assertion importante peut avoir :

```text
source
evidence
confidence
timestamp
status
```

La provenance est particulièrement importante lorsque plusieurs sources peuvent être contradictoires.

---

# 25. Open-world vs closed-world assumptions

Ne pas imposer un modèle universel.

Le SDD doit simplement rendre explicite lorsque la logique suppose :

```text
absence = false
```

ou :

```text
absence = unknown
```

si cette distinction influence le comportement.

---

# 26. Context and reference

Le modèle doit pouvoir détecter les expressions dont le sens dépend implicitement du contexte :

```text
current
this
owner
active
local
available
```

Quand cela devient matériel, résoudre explicitement :

```text
time
actor
location
scope
referent
```

---

# 27. Canonical terminology

Créer un vocabulaire canonique du domaine lorsque nécessaire.

Exemple :

```yaml
terminology:
  - term: Customer
    meaning: ...
    aliases:
      - client
```

Éviter que :

```text
Customer
Client
Account Holder
User
```

désignent accidentellement la même chose dans différentes parties de la specification.

---

# 28. Conceptual consistency

Le modèle sémantique doit chercher à maintenir :

```text
consistent identity
consistent terminology
consistent relation meaning
consistent lifecycle
consistent invariants
```

Une specification peut être syntaxiquement valide mais sémantiquement incohérente.

---

# 29. Representation vs World

Introduire comme principe fondamental :

> MODEL ≠ WORLD

Et :

> SCHEMA ≠ ONTOLOGY

Et :

> DATA ≠ KNOWLEDGE OF REALITY

Les artefacts du SDD sont des modèles du problème.

Ils ne doivent jamais être traités comme le problème lui-même.

---

# 30. Canonical semantic model

Étendre la canonical specification avec un bloc optionnel conceptuellement proche de :

```yaml
semantic_model:

  terminology: []

  concepts:
    - id: CONCEPT-001
      name: Subscription
      meaning: ...
      identity: ...
      granularity: ...

  taxonomy: []

  relations:
    - id: REL-001
      source: Customer
      relation: owns
      target: Subscription
      cardinality: "1:N"
      meaning: ...

  composition: []

  states: {}

  events: []

  transitions: []

  invariants:
    - id: INV-001
      statement: ...

  contracts: []

  assumptions: []

  hypotheses: []

  unknowns: []

  decisions: []

  provenance: []
```

IMPORTANT :

NE PAS rendre tous ces champs obligatoires.

Ce schema doit être sparse et progressive.

Le modèle utilise seulement les dimensions nécessaires au domaine.

---

# 31. Semantic model admission

Un semantic model substantiel est requis lorsque le changement introduit ou modifie :

```text
domain concepts
identity
meaning
relationships
cardinalities
lifecycle
state transitions
business invariants
canonical terminology
cross-component domain semantics
important uncertainty
```

Pour une modification triviale :

```text
semantic_model omitted
```

ou minimal.

---

# 32. Semantic modeling skill

Créer/refactorer une high-level skill :

```text
semantic-modeling
```

Ne pas construire un énorme `SKILL.md`.

Utiliser la nouvelle architecture hiérarchique des skills.

Structure conceptuelle :

```text
semantic-modeling/
├── SKILL.md
├── workflows/
│   ├── concept-modeling.md
│   ├── identity-and-granularity.md
│   ├── taxonomy-and-relations.md
│   ├── state-event-transition.md
│   ├── invariants-and-contracts.md
│   ├── temporal-modeling.md
│   ├── epistemic-modeling.md
│   └── semantic-audit.md
│
└── references/
    ├── ontology.md
    ├── semantics.md
    ├── mereology.md
    ├── modality.md
    ├── causality.md
    ├── epistemology.md
    └── open-vs-closed-world.md
```

Ne créer que les workflows réellement utiles.

---

# 33. `SKILL.md` responsibility

Le parent `semantic-modeling` contient :

```text
shared fundamental distinctions
problem-space modeling objective
workflow routing
common semantic invariants
```

Il doit notamment rappeler :

```text
identity ≠ state
state ≠ event
entity ≠ value
is-a ≠ part-of
false ≠ unknown
ontology ≠ schema
semantic topology ≠ technical topology
assumption ≠ invariant
model ≠ world
```

---

# 34. Orchestrator integration

Orchestrator reste propriétaire de la canonical specification.

Pour du travail domain-nontrivial :

```text
MUST establish or update canonical domain semantics
before allowing solution-space decisions to solidify.
```

Orchestrator peut utiliser :

```text
semantic-modeling
```

pendant la phase SDD.

Ne pas créer immédiatement un nouvel agent.

---

# 35. Architect boundary

Architect reçoit le semantic model comme input canonique.

Architect peut :

```text
map concepts to boundaries
choose representations
choose services/modules
choose persistence strategy
design APIs
design technical topology
```

Mais MUST NOT silently change :

```text
concept meaning
identity
business relations
lifecycle semantics
invariants
confirmed terminology
```

Si le modèle semble incorrect ou incomplet :

```text
return semantic blocker
→ Orchestrator/specification
```

---

# 36. Planner boundary

Planner consomme :

```text
requirements
acceptance criteria
semantic dependencies
architecture decisions
```

Il ne redéfinit pas le semantic model.

Les tasks peuvent référencer :

```text
concept IDs
invariant IDs
contract IDs
```

lorsque cela apporte une vraie traceability.

---

# 37. Implementer boundary

Implementer doit préserver :

```text
semantic contracts
invariants
identity semantics
state-transition semantics
```

Il ne doit pas introduire une nouvelle sémantique produit par commodité d’implémentation.

---

# 38. Testing integration

Le semantic model doit être une source directe de test design.

Mappings typiques :

```text
Invariant
→ property/invariant test

State machine
→ stateful/model-based testing

Precondition/Postcondition
→ contract tests

Use case
→ acceptance/integration/e2e scenario

Cardinality
→ boundary/property testing

Forbidden transition
→ negative test

Unknown/ambiguous assumption
→ should NOT become test oracle until resolved
```

Cette intégration doit être documentée.

---

# 39. QA integration

QA utilise le semantic model pour chercher des contre-exemples.

Exemples :

```text
Can an invariant be violated?
Can an invalid transition occur?
Can identity accidentally split or merge?
Can an assumption be treated as fact?
Can an unknown state be interpreted as false?
```

QA ne redéfinit pas la sémantique.

---

# 40. Reviewer integration

Reviewer vérifie maintenant deux choses distinctes :

```text
implementation correctness
+
semantic preservation
```

Il doit pouvoir détecter :

```text
implementation contradicts invariant
architecture changed lifecycle semantics
test suite validates implementation details but not domain contract
assumption silently became behavior
```

---

# 41. Use Cases

Les use cases appartiennent au Problem Space.

Ils doivent pouvoir décrire :

```text
actor
goal
preconditions
main flow
alternative flows
failure flows
postconditions
affected concepts
events
invariants
```

Ils sont une vue comportementale du semantic model.

Ne pas faire des use cases la source de vérité indépendante du semantic model.

---

# 42. UML and diagrams

UML, Mermaid, PlantUML etc. sont des **views**.

Ils ne sont PAS la canonical source.

Conceptuellement :

```text
Canonical Semantic Model
        ↓
projection
        ↓
Concept Diagram
State Diagram
Use Case Diagram
Sequence Diagram
```

ou :

```text
Architecture Model
        ↓
projection
        ↓
Component Diagram
Technical Sequence Diagram
Deployment Diagram
```

Les diagrammes doivent autant que possible être dérivables/régénérables.

---

# 43. Diagram ownership depends on abstraction level

Do not assign ownership based only on UML diagram type.

Example:

```text
domain state diagram
→ Problem Space / SDD

internal object state diagram
→ Architect/Implementer
```

Similarly:

```text
business sequence
→ semantic/use-case modeling

technical component sequence
→ Architect
```

---

# 44. Semantic validation tool

Créer éventuellement un tool déterministe :

```text
semantic.validate
```

Il peut vérifier :

```text
duplicate concept IDs
dangling relation endpoints
unknown concept references
invalid state references
invalid transition references
unknown invariant references
duplicate terminology
contradictory alias declarations
invalid cardinality syntax
```

Il MUST NOT décider :

```text
whether the ontology is conceptually correct
whether an invariant is a good business rule
whether identity was modeled at the right abstraction
```

Ces décisions nécessitent du raisonnement.

---

# 45. Traceability

Étendre progressivement la traceability :

```text
CONCEPT / INVARIANT / CONTRACT
        ↓
REQ
        ↓
AC
        ↓
ADR
        ↓
TASK
        ↓
TEST / EVIDENCE
```

Ne pas rendre chaque lien obligatoire.

Prioriser les éléments matériels.

---

# 46. Semantic staleness

Une modification sémantique peut invalider des artefacts aval.

Exemple :

```text
INV-004 changes
    ↓
REQ-008 potentially stale
ADR-003 potentially stale
TASK-014 potentially stale
existing tests potentially stale
```

Réutiliser le dependency/staleness graph existant.

Ne pas construire un second système de dependencies.

---

# 47. Semantic diff

Si faisable simplement, définir une notion de changement sémantique :

```text
concept added
concept removed
meaning changed
identity changed
relation changed
cardinality changed
state added/removed
transition changed
invariant changed
assumption confirmed/rejected
```

Cela peut aider le calcul de staleness.

Ne pas construire un moteur complexe en v1.

---

# 48. Business/Product Analysis

Ne pas créer immédiatement un `product-owner` agent.

L’utilisateur reste Product Owner.

Le système ne doit pas décider de manière autonome :

```text
product value
business priority
user preference
strategic tradeoff
```

`semantic-modeling` formalise le problem space.

Il ne remplace pas la décision produit.

---

# 49. Possible future `domain-analyst`

Documenter comme évolution potentielle :

```text
domain-analyst
```

Responsabilité possible :

> Own problem-space formalization without owning product decisions or solution architecture.

Il pourrait posséder :

```text
canonical terminology
domain concepts
relationships
lifecycle
business invariants
use cases
assumptions
unknowns
semantic contradictions
```

Mais NE PAS créer cet agent maintenant.

Commencer par :

```text
Orchestrator + semantic-modeling
```

Créer `domain-analyst` seulement si les evals montrent que cette responsabilité devient :

```text
large
recurrent
context-heavy
artifact-heavy
independently valuable
```

---

# 50. System ontology vs project ontology

Distinguer explicitement :

```text
AGENTIC-WORKFLOW SYSTEM ONTOLOGY
```

qui contient :

```text
Agent
Skill
Workflow
Tool
Capability
Specification
Requirement
Task
Artifact
Evidence
Plugin
...
```

et :

```text
PROJECT / DOMAIN SEMANTIC MODEL
```

qui contient :

```text
Customer
Subscription
Invoice
...
```

Ne jamais mélanger les deux namespaces conceptuels.

---

# 51. Minimal shared semantic foundations

Créer une petite référence canonique commune, par exemple :

```text
references/semantic-foundations.md
```

Elle doit être concise.

Elle contient uniquement les distinctions fondamentales :

```text
model ≠ world
ontology ≠ schema
identity ≠ state
state ≠ event
entity ≠ value
is-a ≠ part-of
false ≠ unknown
fact ≠ assumption
assumption ≠ invariant
semantic topology ≠ technical topology
syntax ≠ semantics
consistency ≠ completeness
problem space ≠ solution space
```

Ne pas injecter un traité philosophique dans tous les agents.

---

# 52. Agent prompt changes must remain small

Do not paste all semantic foundations into every agent.

Add only responsibility-specific constraints.

Example Orchestrator:

```text
For non-trivial domain changes, establish canonical
problem-space semantics before solution-space decisions.
```

Architect:

```text
Consume canonical domain semantics.
Do not silently redefine them.
```

Implementer:

```text
Preserve canonical semantic contracts and invariants.
```

Reviewer:

```text
Verify semantic preservation as part of acceptance.
```

The detailed expertise belongs in `semantic-modeling`.

---

# 53. Evaluation strategy

Create eval cases containing modeling traps.

Examples:

```text
same entity described with two names
identity confused with current state
event confused with state
is-a confused with part-of
missing cardinality
implicit lifecycle transition
assumption silently treated as fact
unknown interpreted as false
temporal fact modeled as timeless
technical dependency mistaken for domain relation
correlation mistaken for causality
over-modeled domain
under-modeled domain
```

Compare:

```text
current SDD
vs
semantic-aware SDD
```

---

# 54. Metrics

Evaluate at least:

```text
semantic ambiguity detected
contradiction detection
requirement stability
architecture reopen rate
implementation rework
test misunderstanding
invariant preservation
traceability quality
context/token overhead
```

The goal is not to maximize semantic artifact size.

The goal is to reduce downstream misunderstanding.

---

# 55. Sparse modeling principle

Do NOT model everything.

Fundamental rule:

> Model a distinction only when losing that distinction could affect reasoning, behavior, validation or future change.

Avoid ontology inflation.

A semantic model with 10 necessary concepts is better than one with 100 decorative concepts.

---

# 56. Abstraction principle

The semantic model is a purposeful compression of reality.

Therefore:

```text
more detail
≠
better model
```

A better model preserves the distinctions necessary for the intended reasoning while discarding irrelevant detail.

---

# 57. Fundamental design objective

The SDD should progressively answer:

```text
What is the problem?

What kinds of things exist in the problem?

What do those things mean?

How are they related?

What makes them the same thing over time?

What states can exist?

What events change those states?

What must always remain true?

What is known?

What is merely assumed?

What is still unknown?

Only then:

How should the software represent and implement this world?
```

---

# 58. Desired SDD architecture

Target conceptually:

```text
USER / PRODUCT OWNER
        │
        ▼
     INTENT
        │
        ▼
┌───────────────────────────┐
│       PROBLEM SPACE       │
│                           │
│ Requirements              │
│ Semantic Model            │
│ Use Cases / Scenarios     │
│ Assumptions / Unknowns    │
│ Invariants / Contracts    │
└────────────┬──────────────┘
             │
             ▼
      CANONICAL SPEC
             │
             ▼
┌───────────────────────────┐
│      SOLUTION SPACE       │
│                           │
│ Architecture              │
│ ADRs                      │
│ Technical topology        │
└────────────┬──────────────┘
             │
             ▼
          PLAN
             │
             ▼
     IMPLEMENTATION
             │
             ▼
         TEST / QA
             │
             ▼
          REVIEW
```

---

# 59. Do not overformalize

This is still an engineering workflow.

Do NOT introduce:

```text
formal theorem prover
full OWL ontology
general-purpose logic engine
complex knowledge graph requirement
mandatory UML
mandatory domain model for trivial changes
```

unless existing project requirements independently justify them.

The goal is better thinking, not formalism for its own sake.

---

# 60. Implementation sequence

Proceed in this order:

```text
1. Audit current SDD/spec-driven-development skill.
2. Audit current domain-modeling skill.
3. Identify existing ontology/semantics/topology/taxonomy additions.
4. Replace the shallow conceptual model with the richer Problem Space model.
5. Define concise semantic-foundations reference.
6. Define sparse semantic_model schema.
7. Implement/refactor semantic-modeling hierarchical skill.
8. Add only minimal Orchestrator integration.
9. Add Architect semantic-preservation boundary.
10. Add minimal Implementer/Reviewer integration.
11. Add semantic.validate if useful.
12. Connect semantic IDs to existing traceability/staleness model.
13. Add semantic-aware test-design integration.
14. Create eval corpus.
15. Compare against existing SDD.
16. Simplify anything that adds complexity without measurable value.
```

---

# 61. Final report

At completion return:

```text
1. Existing SDD conceptual model found.
2. Weaknesses of current ontology/semantics/topology/taxonomy framing.
3. New Problem Space conceptual model.
4. semantic_model schema.
5. semantic-modeling skill structure.
6. Reuse/refactor of existing domain-modeling skill.
7. semantic-foundations contents.
8. Orchestrator changes.
9. Architect boundary changes.
10. Implementer/QA/Reviewer integration.
11. Use-case handling.
12. UML/diagram handling.
13. semantic.validate behavior.
14. Traceability/staleness integration.
15. Test-design integration.
16. Eval corpus and results.
17. Token/context overhead.
18. Concepts deliberately excluded from v1.
19. Whether a future domain-analyst agent appears justified.
```

---

# Fundamental principles

Preserve these rules:

> Problem-space semantics must be established before solution-space structure is allowed to harden.

> Ontology describes what kinds of things exist in the model; semantics defines what they mean.

> Identity, state, events, relations, invariants and epistemic status are independent dimensions and must not be collapsed accidentally.

> The semantic model is sparse and purpose-driven, not an attempt to reproduce reality in full.

> Architecture maps semantics into technical structures; it does not own the right to silently redefine the domain.

> Tests and QA should derive evidence from semantic contracts and invariants, not only from implementation examples.

> The model is not the world.

The purpose of this refactor is to improve the quality of every downstream decision by improving the representation from which those decisions are derived.
