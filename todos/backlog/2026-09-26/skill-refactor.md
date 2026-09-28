# Progressive Disclosure Hierarchy in Agentic Workflow - Skill refactorisation

Tu travailles dans le repository `agentic-workflow`.

Le système possède déjà :

* des agents canoniques ;
* des skills existantes ;
* des Expertise Packs / Agent Plugins en cours d’intégration ;
* une architecture de progressive disclosure basée sur `SKILL.md` ;
* des règles de routing et d’admission ;
* des validators/evals lorsque disponibles.

## Mission

Refactorer l’architecture des skills pour introduire une **progressive disclosure hiérarchique** :

```text
Agent Plugin
    ↓
Agent
    ↓
Skill
    ↓
Workflow
    ↓
Reference / Asset / Tool
```

L’objectif est de réduire drastiquement le nombre de skills directement visibles par chaque agent tout en augmentant la profondeur de l’expertise disponible.

Le système ne doit plus tendre vers :

```text
1 procédure spécialisée
→ 1 skill globalement discoverable
```

mais vers :

```text
1 subdomain cohérent
→ 1 skill discoverable
    → plusieurs workflows spécialisés internes
        → références/assets spécialisés
```

Le modèle de responsabilité devient :

```text
AGENT PLUGIN
= bounded reusable expertise domain / organizational capability

AGENT
= durable responsibility owner inside that domain

SKILL
= discoverable subdomain interface / method family

WORKFLOW
= specialized procedure inside a skill

REFERENCE
= deep declarative knowledge supporting a workflow

TOOL
= executable/deterministic capability
```

---

# 1. Principe fondamental

Chaque niveau ne doit connaître que le niveau immédiatement inférieur nécessaire.

Exemple :

```text
Implementer
does NOT need to know every testing specialty.

Implementer only knows:
→ testing

testing knows:
→ regression
→ property-based
→ integration
→ stateful
→ concurrency
→ quality-review

concurrency workflow knows:
→ synchronization/race-condition references
→ relevant tools
```

Donc :

```text
Agent
→ coarse domain routing

Skill
→ specialized workflow routing

Workflow
→ precise execution procedure

Reference
→ detailed knowledge
```

---

# 2. Problème actuel à résoudre

Aujourd’hui, un agent peut avoir trop de skills visibles :

```text
unit-testing
integration-testing
property-testing
stateful-testing
test-coverage-review
language-review
database-audit
...
```

Cela produit :

```text
large discovery catalog
attention competition
weak skill recall
duplicated admission logic
agents needing to know too many specialties
higher prompt/context cost
```

Le système cible doit réduire le breadth au niveau agent.

Typiquement :

```text
2–4 primary skills per agent
```

plus quelques capabilities conditionnelles fournies par plugins.

Ne PAS transformer cet objectif en règle rigide si un agent nécessite davantage de domaines distincts.

---

# 3. Ne pas créer une skill monolithique

Une high-level skill n’est PAS un énorme `SKILL.md`.

Elle doit être une **interface de subdomain légère**.

Structure cible :

```text
testing/
├── SKILL.md
├── workflows/
│   ├── regression.md
│   ├── property-based.md
│   ├── integration.md
│   ├── stateful.md
│   ├── concurrency.md
│   └── quality-review.md
│
├── references/
│   ├── oracles.md
│   ├── invariants.md
│   ├── boundaries.md
│   ├── generators.md
│   ├── synchronization.md
│   └── mutation-testing.md
│
└── assets/
```

Le `SKILL.md` doit principalement contenir :

```text
purpose
shared ontology
shared invariants/principles
workflow routing
loading rules
```

La connaissance lourde doit rester sous `workflows/`, `references/`, `assets/`.

---

# 4. Maximum depth

Limiter volontairement le graphe de progressive disclosure à :

```text
Agent
→ Skill
→ Workflow
→ Reference / Asset / Tool
```

MUST NOT créer :

```text
Skill
→ Workflow
→ Subworkflow
→ Sub-subworkflow
→ ...
```

Les workflows peuvent charger plusieurs références.

Les workflows ne doivent pas constituer un nouveau runtime récursif.

---

# 5. Direction unique

La navigation doit être essentiellement descendante :

```text
Plugin
↓
Agent
↓
Skill
↓
Workflow
↓
Reference / Asset / Tool
```

Éviter :

```text
workflow → another skill
workflow → unrelated workflow
reference → routing
cyclic workflow graph
```

Les interactions transverses doivent passer par les responsabilités normales de l’agent ou par des concepts partagés.

---

# 6. Skill = interface de subdomain

Une skill haut niveau doit répondre à :

```text
What broad expertise domain does this agent need now?
```

Exemples :

```text
testing
implementation-design
architecture-design
domain-modeling
research
failure-analysis
adversarial-analysis
delivery-operations
```

Les noms exacts doivent être déterminés après audit de l’existant.

Ne pas fusionner arbitrairement des skills uniquement pour réduire leur nombre.

Une fusion est justifiée seulement lorsque :

```text
the skills share a coherent ontology
share foundational principles
operate within the same subdomain
mainly differ by specialized procedure
can be cleanly routed after loading the parent skill
```

---

# 7. Workflow = specialized procedure

Un workflow interne répond à :

```text
Which specialized procedure applies inside this already-selected subdomain?
```

Exemple :

```text
testing
    ↓
concurrency-testing
```

ou :

```text
implementation-design
    ↓
state-modeling
```

Le workflow peut être relativement détaillé.

Il n’est PAS enregistré comme skill auprès du harness.

Il ne doit donc PAS apparaître dans le catalogue global de skills.

---

# 8. Workflow metadata

Créer un format léger et statiquement validable pour les workflows.

Exemple conceptuel :

```yaml
---
id: concurrency
description: >
  Design or assess tests for concurrent behavior, races,
  ordering and synchronization failures.

invoke_for:
  - shared mutable state
  - ordering-sensitive behavior
  - race-condition risk
  - synchronization semantics

avoid_for:
  - purely sequential behavior

references:
  - ../references/synchronization.md
  - ../references/concurrency-oracles.md
---
```

Puis le corps contient la procédure.

Les champs exacts peuvent être adaptés au repository.

Préférer un schema minimal.

---

# 9. Pourquoi les workflow metadata existent

Ces metadata doivent servir à :

```text
internal routing
static validation
documentation
eval generation
context-cost inspection
future DecisionEngine integration
```

Elles ne sont pas destinées au harness global.

---

# 10. Skill routing table

Chaque high-level `SKILL.md` doit contenir une table ou structure équivalente explicitant les workflows.

Exemple :

```text
Situation                         Workflow
--------------------------------------------------------
Known defect regression          workflows/regression.md
Stable invariants / huge space    workflows/property-based.md
Cross-component behavior         workflows/integration.md
State machine / lifecycle        workflows/stateful.md
Concurrency / races              workflows/concurrency.md
Review existing suite            workflows/quality-review.md
```

Le skill doit charger uniquement le workflow ou petit nombre de workflows nécessaires.

---

# 11. Skill must already add value

IMPORTANT :

Un `SKILL.md` ne doit PAS être uniquement :

```text
if A read file A
if B read file B
if C read file C
```

Même avant de charger un workflow spécialisé, le parent skill doit améliorer le comportement de l’agent.

Exemple pour `testing` :

```text
test observable contracts
identify the test oracle
cover plausible failure modes
prefer the lowest faithful test level
avoid implementation coupling
treat coverage as evidence, not adequacy
```

Les workflows apportent la spécialisation.

---

# 12. Agent-local routing

Les agents ne doivent plus connaître toutes les spécialités contenues dans leurs skills.

Exemple :

```text
Implementer
```

ne doit pas connaître directement :

```text
property-based
concurrency-testing
stateful-testing
integration-testing
```

Il doit seulement connaître :

```text
testing
```

et savoir quand charger `testing`.

---

# 13. Mandatory broad-domain admission

Certains broad-domain skills doivent être explicitement requis dans les agents.

Exemple conceptuel :

```text
Implementer

IF behavior-changing implementation
→ MUST use tdd

IF tests are created or materially modified
→ MUST use testing

IF a non-trivial local representation, algorithm,
state or synchronization decision is required
→ MUST/SHOULD use implementation-design
```

QA :

```text
IF independently falsifying completed behavior
→ MUST use adversarial-analysis

IF test adequacy is under evaluation
→ MUST use testing

IF unexplained runtime failure is being diagnosed
→ MUST use failure-analysis
```

Le routing précis vers les workflows appartient ensuite à la skill.

---

# 14. Ne pas centraliser le routing de skills dans Orchestrator

MUST NOT créer :

```text
Orchestrator
→ decide exact skills
→ handoff skills
→ specialist
```

La sélection de subdomain appartient à l’agent propriétaire.

L’Orchestrator route :

```text
work → agent
```

L’agent route :

```text
work → skill
```

La skill route :

```text
work → workflow
```

---

# 15. Agent responsibilities remain stable

Cette refonte ne doit PAS changer le principe :

```text
Agent = WHO owns the responsibility
Skill = HOW work in a subdomain is performed
```

Ne pas créer un nouvel agent uniquement parce qu’un workflow est sophistiqué.

Ne pas créer une skill uniquement parce qu’une référence est importante.

---

# 16. Important distinction: problem concept vs workflow

Ne pas classer naïvement toute expertise par mot-clé.

Exemple :

```text
concurrency
```

n’est pas nécessairement une seule skill ou un seul workflow.

Cela peut apparaître dans plusieurs subdomains :

```text
implementation-design/workflows/concurrency-design.md

testing/workflows/concurrency.md

failure-analysis/workflows/concurrency-failure.md
```

avec des références partagées si pertinent.

Les workflows sont définis par :

```text
subdomain × specialized problem
```

et non uniquement par un mot-clé.

---

# 17. Shared references

Permettre la réutilisation contrôlée de références lorsque plusieurs skills utilisent une même connaissance.

Exemple :

```text
references/concurrency/
├── memory-models.md
├── synchronization.md
├── race-conditions.md
└── ordering.md
```

Peut être consommé par :

```text
implementation-design
testing
failure-analysis
```

Éviter la duplication de connaissances.

Mais ne pas créer un système de dependencies sophistiqué sans besoin.

---

# 18. Agent Plugin = bounded expertise domain

Formaliser dans la documentation :

```text
Agent Plugin
= bounded reusable expertise domain / organizational capability
```

Dans de nombreux cas cela peut correspondre conceptuellement à un département.

Exemples verticaux :

```text
Software Engineering
ML Engineering
Research
HR
Legal
Finance
Security
```

Mais ne pas rendre le mot « department » obligatoire dans le schema.

---

# 19. Vertical vs Horizontal Agent Plugins

Préserver la distinction :

```text
VERTICAL PLUGIN

introduces a coherent domain
may contribute agents
may contribute domain skills
may contribute domain tools

Examples:
ML-Eng
Research
HR
Legal
```

et :

```text
HORIZONTAL PLUGIN

cross-cutting expertise augmentation
usually does not introduce a new durable responsibility owner

Examples:
PythonDev
RustDev
Database
ScientificPython
Cloud/AWS
```

---

# 20. `agentic-core`

Pour l’instant conserver :

```text
agentic-core
=
organizational runtime/kernel
+
baseline software-engineering domain
```

NE PAS séparer maintenant :

```text
Agentic Kernel
Software Engineering Plugin
```

même si cette séparation pourrait devenir pertinente plus tard.

Documenter éventuellement cette possibilité comme future evolution.

---

# 21. Progressive disclosure target

Le contexte doit évoluer approximativement comme :

```text
INITIAL CONTEXT

Agent
+ 2–4 skill metadata
```

puis :

```text
DOMAIN CONTEXT

Agent
+ selected SKILL.md
+ workflow index
```

puis :

```text
SPECIALIST CONTEXT

Agent
+ selected skill
+ selected workflow
```

puis uniquement si nécessaire :

```text
DEEP CONTEXT

+ exact references/assets
```

À chaque étape, le modèle reçoit seulement le contexte nécessaire à la prochaine décision.

---

# 22. Design objective

Optimiser :

```text
attention routing quality
skill recall
workflow selection precision
context size
token cost
task quality
```

Le but n’est pas uniquement de réduire le nombre de fichiers.

---

# 23. Migration strategy

NE PAS migrer immédiatement toutes les skills.

Commencer par un domaine pilote.

Le domaine pilote recommandé est :

```text
testing
```

car :

```text
multiple existing related skills likely exist
routing cases are clear
quality is measurable
progressive disclosure benefit is large
tests are central to TDD quality
```

---

# 24. Audit initial obligatoire

Avant modification, inventorier toutes les skills existantes.

Pour chacune, classifier :

```text
KEEP AS TOP-LEVEL SKILL

MERGE INTO HIGH-LEVEL SKILL AS WORKFLOW

CONVERT TO REFERENCE

KEEP SEPARATE BECAUSE DIFFERENT COGNITIVE PURPOSE

UTILITY / TOOL CANDIDATE
```

Ne pas modifier encore le système pendant cet audit.

Produire une proposition avant migration.

---

# 25. Audit criteria

Une skill reste top-level si :

```text
it represents a distinct expertise/method family
it has significantly different admission
it changes the model's cognitive mode
it owns substantial shared principles
it cannot naturally be discovered after entering another subdomain
```

Une skill devient workflow si :

```text
it shares the same broad domain
it mainly changes procedure
the parent skill can reliably discover it
its metadata can be removed from global discovery without losing coarse routing
```

Une skill devient reference si :

```text
it mainly contains declarative knowledge
it has no meaningful independent workflow
it should only be loaded after another procedure requires it
```

---

# 26. Testing pilot

Inspecter notamment les existing concepts equivalent to:

```text
tdd
e2e-testing
test-coverage-review
test-quality-review if created
testing-related QA methods
property-based concepts
integration testing
```

Do NOT automatically merge TDD.

Expected conceptual distinction:

```text
TDD
= development lifecycle

Testing
= test expertise subdomain

Adversarial analysis/testing
= independent falsification mindset
```

These may remain distinct top-level skills.

---

# 27. Proposed testing structure

Build only if supported by audit:

```text
testing/
├── SKILL.md
├── workflows/
│   ├── regression.md
│   ├── property-based.md
│   ├── integration.md
│   ├── stateful.md
│   ├── concurrency.md
│   ├── end-to-end.md
│   └── quality-review.md
│
└── references/
    ├── test-oracles.md
    ├── invariants.md
    ├── boundary-analysis.md
    ├── test-doubles.md
    ├── mutation-testing.md
    └── ...
```

Adapt based on existing repo content.

Do not create empty speculative workflows.

---

# 28. Implementer after pilot

Target conceptually:

```text
Implementer

top-level methodological skills:
- tdd
- testing
- implementation-design
- refactor-cleanup
...
```

The exact set depends on audit.

Do not enforce an arbitrary count.

---

# 29. QA after pilot

Potentially:

```text
QA

- adversarial-analysis
- failure-analysis
- testing
- security-testing
...
```

Again, preserve genuinely distinct cognitive modes.

---

# 30. Reviewer after pilot

Potentially:

```text
Reviewer

- code-review
- testing
- security-review
...
```

`testing` may use `quality-review` internally.

Do not move final acceptance responsibility into testing.

---

# 31. Second pilot: `implementation-design`

After testing is validated, implement:

```text
implementation-design/
├── SKILL.md
├── workflows/
│   ├── representation-selection.md
│   ├── algorithm-selection.md
│   ├── state-modeling.md
│   └── concurrency-design.md
│
└── references/
    ├── data-structures.md
    ├── algorithmic-complexity.md
    ├── design-patterns.md
    └── concurrency-primitives.md
```

Core rule:

```text
Start from constraints and invariants.
Do NOT start from a named pattern.
```

---

# 32. Workflow loading semantics

The parent skill should instruct the model to:

```text
1. Identify which workflow(s) match the current problem.
2. Load only those workflows.
3. Follow their procedure.
4. Load referenced knowledge only when required.
5. Do not preload every workflow/reference.
```

A single task may require more than one workflow when justified.

Avoid arbitrary `exactly one workflow` constraints.

---

# 33. Static workflow validation

Extend the skill linter/compiler to validate:

```text
workflow IDs unique within skill
referenced workflow files exist
referenced references exist
no cyclic workflow references
no illegal upward routing
frontmatter/schema valid
no duplicate workflow IDs
routing table references known workflows
```

---

# 34. Context budget inspection

Add analysis tooling capable of reporting:

```text
top-level skill metadata size
SKILL.md size
workflow size
references potentially loaded
maximum possible path cost
typical path cost
```

Example:

```text
Implementer
→ testing
→ concurrency
→ synchronization reference

total estimated chars/tokens: ...
```

This is important.

Progressive disclosure is useful only if real context cost improves.

---

# 35. Evals: flat vs hierarchical

Create an eval comparing:

```text
BASELINE
existing flat skill catalog

VS

HIERARCHICAL
high-level skills + workflows
```

Use representative tasks.

Measure:

```text
correct high-level skill selected
correct workflow selected
required skill recall
incorrect skill load rate
workflow precision
task quality
tokens consumed
files loaded
time/latency where measurable
```

---

# 36. Hidden-specialty eval

Explicitly test the concern that motivated this architecture.

Example:

```text
QA finds a concurrency defect.

Implementer receives:
"Fix race causing stale cache values under concurrent updates."
```

The Implementer should:

```text
identify testing as relevant
load testing
discover concurrency workflow
load concurrency workflow
produce appropriate regression/testing strategy
```

The agent does NOT need `concurrency-testing` in its initial catalog.

This scenario must be included in evaluation.

---

# 37. Discoverability failure test

Create adversarial cases where:

```text
workflow exists
but broad parent skill is not obviously triggered
```

If this occurs repeatedly, do NOT blindly add workflow keywords to the top-level skill description.

Instead evaluate whether:

```text
the workflow belongs under the wrong parent skill
the parent skill admission is too narrow
the workflow should actually be top-level
the agent's local MUST rule is insufficient
```

Do not optimize discovery through keyword stuffing.

---

# 38. Skill descriptions

High-level skill descriptions must remain concise but broad enough to identify the subdomain.

Example:

```yaml
name: testing

description: >
  Design, implement and assess evidence-producing tests across
  regression, property-based, stateful, concurrent, integration
  and end-to-end behavior. Use whenever tests are created,
  materially changed or their adequacy is evaluated.
```

Do not enumerate every future workflow indefinitely.

Describe the conceptual coverage.

---

# 39. Avoid keyword-routing architecture

Routing should rely primarily on semantics.

MUST NOT build:

```text
if prompt contains "race"
→ concurrency.md
```

Static semantic trigger descriptions are acceptable.

Hard-coded keyword routers are not.

---

# 40. Future DecisionEngine compatibility

Design workflow metadata so a future DecisionEngine can consume it.

Potential future pipeline:

```text
Agent
↓
available high-level skill metadata
↓
DecisionEngine
↓
candidate skills
↓
LLM
↓
SKILL.md
↓
available workflow metadata
↓
LLM or future DecisionEngine
↓
workflow
```

But DO NOT implement the DecisionEngine in this task.

No Jev integration in this implementation.

Only make the schemas compatible with future external routing.

---

# 41. Future multi-label routing

Do not assume only one skill can apply.

A future router may produce:

```text
tdd                   0.99
testing               0.96
implementation-design 0.76
```

Likewise one skill may select multiple workflows.

Design metadata accordingly.

---

# 42. Relationship with Agent Plugins

Agent Plugins should expose high-level skills, not all internal workflows.

Example:

```text
ML-Eng
│
├── ml-engineer
│
├── experimentation
│   ├── baseline-design
│   ├── ablation
│   ├── scaling-study
│   └── hpo
│
├── model-evaluation
│   ├── threshold-selection
│   ├── calibration
│   ├── subgroup-analysis
│   └── error-analysis
│
└── tools
```

The harness should discover:

```text
experimentation
model-evaluation
```

not every internal workflow.

---

# 43. Organizational model

Document the conceptual analogy:

```text
Agent Plugin
≈ bounded organizational capability / department-like domain

Agent
≈ role with authority/responsibility

Skill
≈ professional subdomain/method family

Workflow
≈ specialized procedure

Reference
≈ domain knowledge

Tool
≈ instrument
```

Treat this as a conceptual model, not a literal simulation of human organizations.

The architecture must optimize LLM behavior, not imitate humans for its own sake.

---

# 44. LLM-specific design principle

The system should optimize:

> At each step, provide the smallest context that makes the next decision easy and reliable.

Do NOT optimize for biological realism.

LLMs differ from humans in:

```text
context-window competition
instruction-position sensitivity
cheap exact procedural reload
limited persistent working memory
tool-call availability
token/context cost
```

Design specifically for those properties.

---

# 45. Boundary of abstractions

Changes should propagate as follows:

```text
Agent changes
→ responsibility changed

Skill changes
→ subdomain method/shared principles changed

Workflow changes
→ specialized procedure changed

Reference changes
→ detailed domain knowledge changed
```

Adding a specialized testing method should normally NOT require modifying:

```text
Implementer
QA
Reviewer
Orchestrator
```

It should require only:

```text
testing/workflows/new-method.md
+
testing/SKILL.md routing/index update
```

---

# 46. Do not over-generalize immediately

Do not refactor every current skill family at once.

Required migration sequence:

```text
1. Audit all existing skills.
2. Define migration candidates.
3. Implement workflow schema + validators.
4. Implement testing as first hierarchical skill.
5. Update relevant agent broad-domain routing.
6. Run flat-vs-hierarchical eval.
7. Fix discovery/routing issues.
8. Implement implementation-design.
9. Re-evaluate.
10. Only then propose other skill-family migrations.
```

---

# 47. Candidate future families

Do not implement automatically, but audit possible candidates such as:

```text
code-review
research
security
delivery-operations
domain-modeling
failure-analysis
```

For each, determine whether existing skills should remain separate or become workflows.

Do not force uniformity.

---

# 48. Skills that should remain separate when cognitive intent differs

Example:

```text
testing
```

and:

```text
adversarial-analysis
```

may both interact with tests but have different purposes:

```text
testing
→ construct strong evidence

adversarial-analysis
→ actively search for counterexamples
```

Do not merge purely because their artifacts overlap.

Likewise:

```text
TDD
→ development lifecycle

testing
→ test-design expertise
```

should probably remain separate unless evals strongly show otherwise.

---

# 49. No duplicated expertise

When migrating a low-level skill to workflow form:

```text
old skill
→ workflow
```

ensure the same full procedure is not left duplicated in both places.

Support aliases/deprecation only when necessary for compatibility.

---

# 50. Backward compatibility

If existing agents/plugins reference a skill being migrated:

```text
detect references
update declaratively
validate generated agents
```

Avoid silent breakage.

If compatibility shims are required, mark them deprecated and removable.

---

# 51. Provenance

The effective configuration should be able to explain:

```text
Implementer
→ testing
   source: agentic-core

testing
→ concurrency workflow
   source: agentic-core/testing

reference
→ synchronization
```

Plugin-projected skills must preserve plugin provenance.

---

# 52. Testing integration with plugin compiler

Ensure the Agent Plugin / Effective Profile compiler treats:

```text
workflow/
references/
assets/
```

as private content of their parent skill.

They must travel with the skill when materialized.

They must NOT be independently exposed as global skill metadata.

---

# 53. Package portability

A hierarchical skill must still be portable as part of a normal Agent Plugin.

Do not rely on hidden global filesystem paths.

Relative references should resolve within the packaged skill or through explicit shared-reference declarations.

---

# 54. Suggested implementation components

Prefer minimal concepts such as:

```text
SkillManifest
WorkflowManifest
SkillRouterMetadata
SkillValidator
ContextCostInspector
```

Only introduce them if the repository architecture benefits.

Do not create an unnecessary generalized workflow engine.

The workflow files are primarily LLM instructions, not executable state machines.

---

# 55. Non-goals

Do NOT implement in this task:

```text
Jev
DecisionEngine
external skill router
runtime classifier service
workflow execution engine
recursive workflow graphs
automatic ontology learning
public skill marketplace
mass migration of every skill
```

---

# 56. Acceptance criteria — architecture

The implementation is acceptable when:

```text
agents can expose a small number of high-level skills

high-level skills can internally expose multiple specialized workflows

workflows are invisible to global skill discovery

workflow metadata is statically validated

skills remain useful without loading every workflow

references are loaded only as needed

agent prompts no longer need to know every specialized procedure

new workflows can usually be added without modifying agents
```

---

# 57. Acceptance criteria — testing pilot

Given:

```text
Implementer
top-level skills include:
- tdd
- testing
- implementation-design
```

Task:

```text
Fix a race condition causing stale values under concurrent cache updates,
and add regression coverage.
```

Expected:

```text
Implementer recognizes behavior change
→ loads tdd

tests required
→ loads testing

testing identifies concurrency-specific testing needs
→ loads workflows/concurrency.md

non-trivial synchronization/representation decision if applicable
→ implementation-design may be loaded

only relevant references are loaded
```

No global `concurrency-testing` skill is required.

---

# 58. Acceptance criteria — maintainability

Adding:

```text
testing/workflows/metamorphic.md
```

should normally require:

```text
new workflow file
routing/index entry
references if necessary
tests/evals
```

It should NOT require modifying all agents that use testing.

---

# 59. Acceptance criteria — efficiency

Compared with the existing flat architecture, the hierarchical version should aim for:

```text
fewer globally exposed skills
equal or better required-skill recall
equal or better specialized workflow selection
lower initial context/discovery cost
no material loss in final task quality
```

Do not declare success solely because token count decreases.

---

# 60. Final report

At completion return:

```text
1. Existing skill inventory.
2. Classification of each current skill:
   - keep top-level
   - workflow candidate
   - reference candidate
   - tool candidate
3. Hierarchical skill schema.
4. Workflow metadata schema.
5. Validation rules.
6. Testing pilot structure.
7. Existing testing skills migrated/reused.
8. Agent changes made.
9. Progressive-disclosure behavior.
10. Context-cost comparison.
11. Flat-vs-hierarchical eval results.
12. Hidden-specialty/concurrency eval result.
13. implementation-design structure if implemented.
14. Backward-compatibility changes.
15. Plugin compiler/materializer changes.
16. Known routing failures.
17. Skills that should NOT be merged and why.
18. Proposed next skill families, without implementing them.
```

---

# Fundamental rule

When making tradeoffs, preserve this principle:

> Each level should only need enough information to route to the next useful level of expertise.

And:

> Reduce global discovery breadth without reducing available expertise depth.

And:

> The purpose of progressive disclosure is not merely fewer tokens. It is to make every attention-routing decision smaller, better informed and easier for the model.

Do not optimize the architecture for superficial human resemblance.

Optimize it for reliable LLM cognition, low context competition, modular expertise and measurable task quality.
