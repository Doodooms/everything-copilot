Globalement, je trouve la structure **très solide**. Tes agents ont maintenant de vraies frontières d’autorité, et on voit nettement ton principe `Agent = WHO`, `Skill = HOW`. Je ne changerais pas les 9 rôles pour l’instant. En revanche, je ferais **quatre corrections architecturales assez importantes**, dont deux peuvent aussi expliquer directement ton explosion de tokens.

## 1. Le principal défaut conceptuel : Architect possède encore trop du Problem Space

C’est maintenant incohérent avec l’évolution récente de ton SDD.

Ton Architect dit encore qu’il définit les « domain semantics » et les invariants, et qu’il maintient le vocabulaire, les relations de données et la sémantique du domaine.  

Et Planner renforce cette conception en déclarant explicitement que les décisions d’« ontology, topology, technology » appartiennent à Architect. 

Or, avec ce qu’on vient de concevoir, je voudrais désormais :

```text
Orchestrator / SDD
        │
        ├── canonical semantics
        ├── concepts
        ├── identity
        ├── relations
        ├── states/events
        ├── invariants
        ├── assumptions/unknowns
        └── use cases
                │
                ▼
            Architect
                │
                ├── technical boundaries
                ├── components
                ├── interfaces
                ├── persistence
                ├── technical topology
                └── technology decisions
```

Donc Architect devrait **consommer et préserver** la sémantique, pas la posséder.

Je modifierais sa mission vers :

```text
WHAT:
Map approved problem-space semantics and requirements
into system architecture, technical topology, boundaries,
interfaces and technology decisions.
```

Et sa règle fondamentale :

```text
MUST preserve canonical domain semantics and invariants.
MUST NOT silently redefine concept identity, meaning,
relations, lifecycle or business invariants.
```

S’il découvre un problème sémantique :

```text
Architect
→ semantic blocker
→ Orchestrator / SDD
```

et non :

```text
Architect
→ silently repairs domain model
```

C’est probablement **la modification la plus importante**.

---

## 2. Ton Orchestrator contient actuellement une contradiction qui peut coûter très cher

Il dit quelque chose que je trouve excellent :

> choisir la plus petite séquence de spécialistes et le niveau d’assurance minimal ; architecture, planning, research, implementation, QA, review, challenge et operations sont des phases conditionnelles. 

Mais juste après :

> l’implementation loop est `implementer -> quality-assurance -> reviewer`. 

Les deux philosophies ne sont pas complètement compatibles.

Si chaque changement de comportement devient :

```text
Implementer
     ↓
QA
     ↓
Reviewer
```

alors tu as déjà **3 appels minimum**, indépendamment de la trivialité du changement.

C’est probablement une partie importante du multiplicateur de coût que tu observes.

Je préférerais :

```text
L0
Implementer
→ deterministic verification
→ convergence

L1
Implementer
→ targeted QA OR lightweight Reviewer depending risk
→ convergence

L2
Implementer
→ QA
→ Reviewer

L3
Implementer
→ QA
→ Reviewer
+ Challenger/security/etc. where applicable
```

Autrement dit :

> `Implementer → QA → Reviewer` doit être le **full assurance loop**, pas forcément le minimal implementation loop.

Ton Orchestrator possède déjà presque toute la bonne architecture pour cela. Il faut simplement pousser jusqu'au bout la notion de `risk-proportional workflow`.

---

# 3. Tu répètes beaucoup de policy dans chaque agent

C’est probablement ton prochain gros gisement de tokens.

Tous tes agents ont quasiment le même bloc :

```text
<risk_assessment>
Assess impact/blast radius...
L0...
L1...
L2...
L3...
Orchestrator owns...
specialists MUST NOT downgrade...
...
</risk_assessment>
```

Architect l'a par exemple explicitement.  QA également.  Reviewer aussi. 

Mais ton propre contrat dit :

```text
Orchestrator owns the recorded level.
Specialists MUST NOT downgrade it.
```

Dans ce cas, pourquoi chaque spécialiste **recalcule-t-il systématiquement le risque** au début de son workflow ?

Je simplifierais en :

### Orchestrator

```text
MUST establish risk_level: L0 | L1 | L2 | L3.
```

### Specialist

```text
Consume the assigned risk level.
MUST escalate when new evidence indicates higher risk.
MUST NOT downgrade it.
```

C'est suffisant.

Tu économises :

* contexte statique ;
* raisonnement redondant ;
* risque de classification contradictoire ;
* tokens générés.

Même logique pour les champs génériques de handoff :

```text
status
agent
changed_files
commit_shas
suggested_next_owner
```

Tu les répètes partout.

Je définirais un **canonical handoff schema** dans le core :

```yaml
handoff:
  status:
  agent:
  consumed_artifacts:
  produced_artifacts:
  evidence:
  changed_files:
  commit_shas:
  risks:
  blockers:
  next_owner:
```

Puis chaque agent ne définit que son extension :

```text
ArchitectHandoff extends Handoff
QA Handoff extends Handoff
ReviewerHandoff extends Handoff
...
```

Conceptuellement, pas nécessairement avec héritage logiciel.

---

# 4. `reasoning-effort: max` partout me semble excessif

Architect, Challenger, DevOps, Implementer, Planner, QA, Researcher et Reviewer sont tous configurés en `max`. Par exemple Architect l'est explicitement.  QA aussi.  Reviewer également. 

Pour ton objectif industriel, je ne pense pas que ce soit la bonne politique par défaut.

Je préférerais quelque chose comme :

```text
Orchestrator
dynamic / medium-high

Architect
high
max only for genuinely difficult architecture

Planner
medium

Implementer
medium/high
max only for hard debugging / algorithmic work

QA
medium/high
max for difficult failure-analysis

Reviewer
medium/high

Challenger
high/max

Researcher
medium
high only for synthesis difficult

DevOps
medium
```

Encore mieux :

```text
reasoning_effort =
f(task complexity, uncertainty, risk)
```

et non :

```text
reasoning_effort =
agent identity
```

Ce serait justement une excellente surface future de ton `HarnessProfile` auto-optimisé.

---

# Sur chacun des agents

### Orchestrator

C’est maintenant le centre architectural le plus abouti du système. J’aime particulièrement que tu aies explicitement écrit que chaque appel doit apporter une **nouvelle décision, un nouvel artefact ou une nouvelle preuve**, et que les handoffs doivent utiliser références/deltas plutôt que recopier l’historique. 

C’est précisément la règle qu’il te faut pour maîtriser les coûts.

Son défaut est plutôt inverse : il commence à porter énormément de mécanique :

```text
SDD
canonical state
staleness
risk
routing
Git lifecycle
handoffs
todos
history
resume recovery
```

Je garderais **l’ownership** dans Orchestrator, mais je déplacerais progressivement la mécanique déterministe vers :

```text
orchestration skill
+
runtime/tools
```

L’agent devrait décider ; le runtime devrait enregistrer, compiler, valider et persister.

---

### Architect

Très bonne frontière avec Implementer/Planner, mais il faut lui retirer l’ownership du semantic/domain model comme expliqué plus haut.

Après cette correction, il devient très propre :

```text
Problem Space
    ↓
Architect
    ↓
Solution Space
```

---

### Planner

Je le trouve très bien borné. Il distingue même correctement `acceptance criterion` de `phase exit criterion`, ce qui évite que Planner réécrive implicitement la SPEC. 

Seulement deux changements :

```text
ontology
```

ne doit plus être attribuée à Architect,

et Planner doit rester **facultatif** pour une tâche atomique.

---

### Implementer

Probablement celui que je modifierais le moins.

La séparation :

```text
Implementer
= production implementation + immediate tests

QA
= independent falsification

Reviewer
= acceptance
```

est très propre. 

Et ton nouveau routing des skills est déjà visible :

```text
software-engineering
→ tdd

quality-engineering
→ test-design
```

avec des conditions explicites. 

C'est exactement la direction qu'on vient de définir.

---

### QA

Je trouve que tu as finalement trouvé la bonne identité pour cet agent.

Il combine :

```text
diagnosis
+
adversarial falsification
+
test-surface ownership
```

sans réparer le code production. 

Et surtout :

```text
stop once the correct owner has actionable evidence
```

est une excellente règle économique. 

Je surveillerais simplement le chevauchement :

```text
QA → test-quality-review
Reviewer → test-quality-review
```

QA devrait **produire l'évidence** sur la faiblesse des tests.

Reviewer devrait surtout déterminer si cette evidence est suffisante, et ne relancer une analyse profonde du test surface que si le risque ou un gap l'exige.

---

### Reviewer

Sa mission est maintenant beaucoup meilleure qu’un simple code reviewer :

```text
final technical acceptance
```

avec consommation de la SPEC, architecture, diff, tests et QA. 

Et tes limites sont très bonnes : pas d’implémentation, pas de campagne QA bis, pas de rejet sur préférences stylistiques. 

Le seul vrai sujet est **quand l’invoquer**.

Je ne supprimerais surtout pas Reviewer.

Je rendrais son admission réellement dépendante du niveau d'assurance.

---

### Challenger

Je le garderais exactement comme agent séparé.

C'est le meilleur exemple de ton test :

> même sans `context: fork`, ce rôle mérite-t-il une identité indépendante ?

Oui.

Il possède un objectif cognitif explicitement antagoniste :

```text
proposal author
→ construct

Challenger
→ falsify proposal

Reviewer
→ accept/reject completed change
```

Et tu lui interdis correctement de voir le raisonnement privé du proposal author : il doit attaquer l'artefact matérialisé. 

Très bon design.

Il doit simplement rester rare : L2 important / L3, pas workflow normal.

---

### Researcher

C'est potentiellement **un économiseur de tokens**, malgré le coût d’un appel supplémentaire.

Sa mission est précisément d’isoler les investigations coûteuses puis de les compresser agressivement pour éviter que chaque agent recommence la recherche. 

Le risque est que presque tous tes spécialistes puissent l’appeler.

Je renforcerais donc l’interface :

```yaml
research_request:
  exact_question:
  supported_decision:
  evidence_needed:
  stop_condition:
  budget:
```

Interdire implicitement :

```text
"research this topic"
```

et préférer :

```text
"Does library X v4 guarantee property Y required by ADR-003?"
```

---

### DevOps

Très propre depuis que tu as séparé :

```text
MCP implementation → Implementer
MCP hosting/config/deployment → DevOps
```

C'est explicite dans ton agent. 

Je conserverais exactement cette frontière.

Même remarque que pour Implementer : DevOps produit une validation opérationnelle ; QA/Reviewer doivent **réutiliser cette evidence** plutôt que relancer exactement les mêmes commandes.

---

# Donc je garderais bien les 9 agents

Je ne fusionnerais aujourd'hui ni :

```text
Architect + Planner
QA + Reviewer
Reviewer + Challenger
Implementer + DevOps
Researcher + anything
```

Ils correspondent maintenant à neuf intentions cognitives distinctes :

```text
Orchestrator
→ govern

Architect
→ structure solution

Planner
→ sequence

Researcher
→ establish evidence

Implementer
→ construct

QA
→ falsify behavior

Reviewer
→ accept

Challenger
→ falsify proposal

DevOps
→ operate
```

C'est une ontologie de rôles assez propre.

Le problème actuel n'est donc **plus vraiment le nombre d'agents**.

Le problème devient :

```text
when are they activated?
+
how much duplicated policy/context do they receive?
+
what evidence is reused instead of regenerated?
```

Et c'est très cohérent avec notre discussion précédente sur les coûts.

## Les 5 modifications que je ferais maintenant

1. **Sortir la sémantique métier d’Architect** et la faire appartenir au SDD/problem-space model.
2. **Résoudre la contradiction** `conditional phases` vs `Implementer → QA → Reviewer` systématique.
3. **Centraliser les policies répétées** : risk model, generic handoff schema, lifecycle invariants.
4. **Rendre reasoning effort adaptatif**, au lieu de `max` presque partout.
5. **Instrumenter les agents en marginal utility** avant d’en retirer un :

```text
tokens consumed
model calls
unique defects found
unique decisions produced
reused evidence
duplicate evidence
downstream rework prevented
```

À mon avis, tu arrives à un stade où **réécrire encore les rôles eux-mêmes apporterait peu**. Le prochain gain est plutôt de compiler ces bons rôles dans un runtime beaucoup plus parcimonieux : admission conditionnelle, context reconstruction, shared evidence, reasoning budget et progressive disclosure. C'est là que tu peux probablement conserver presque toute la qualité de tes 9 agents tout en réduisant fortement le facteur de coût.

Tu travailles dans `agentic-workflow`.

Je veux effectuer un **refactor ciblé des agents canoniques**, sans modifier inutilement leur nombre ni leurs responsabilités fondamentales.

Les agents actuels sont :

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

Cette taxonomie doit rester stable sauf découverte d'une contradiction majeure.

Le principe fondamental reste :

```text
Agent = WHO owns a durable responsibility
Skill = HOW that responsibility is performed
Workflow = specialized procedure inside a skill
Tool = executable capability
```

L'objectif de ce changement est de :

1. corriger la frontière `Problem Space → Solution Space` ;
2. rendre réellement le workflow proportionnel au risque ;
3. réduire les policies et raisonnements redondants entre agents ;
4. améliorer la réutilisation d'evidence ;
5. réduire le coût en tokens sans affaiblir les frontières d'autorité.

---

# 1. Preserve the nine-agent ontology

Ne pas fusionner les agents actuels.

Leur intention reste :

```text
Orchestrator
→ govern and coordinate

Architect
→ design the technical solution structure

Planner
→ decompose and sequence delivery

Researcher
→ establish isolated evidence

Implementer
→ construct

Quality Assurance
→ diagnose and falsify behavior

Reviewer
→ final technical acceptance

Challenger
→ independently falsify high-impact proposals

DevOps
→ mutate operational surfaces
```

Ne pas transformer cette tâche en redesign général des rôles.

---

# 2. Correct the Problem Space / Solution Space boundary

Le principal problème conceptuel actuel est que `architect` possède encore des responsabilités telles que :

```text
domain semantics
domain vocabulary
domain invariants
ontology
```

Cette ownership doit être déplacée en amont vers le SDD / canonical specification.

Le modèle cible est :

```text
USER INTENT
    ↓
ORCHESTRATOR / SDD
    ↓
PROBLEM SPACE
    ├── canonical terminology
    ├── concepts
    ├── identity
    ├── relations
    ├── states
    ├── events
    ├── transitions
    ├── business/domain invariants
    ├── contracts
    ├── assumptions
    └── unknowns
    ↓
CANONICAL SPECIFICATION
    ↓
ARCHITECT
    ↓
SOLUTION SPACE
    ├── components
    ├── technical boundaries
    ├── interfaces
    ├── dependency direction
    ├── persistence
    ├── runtime topology
    ├── integrations
    └── technology choices
```

## Architect

Refactor Architect so that it:

```text
CONSUMES canonical domain semantics
PRESERVES canonical domain semantics
MAPS them into technical architecture
```

Architect MUST NOT silently redefine:

```text
concept meaning
identity
business/domain relations
domain lifecycle
business invariants
canonical terminology
```

If architecture work discovers a semantic ambiguity or contradiction:

```text
Architect
→ return semantic/specification blocker
→ Orchestrator / SDD
```

Architect may still define **technical invariants** and architectural constraints.

Distinguish clearly:

```text
domain invariant
→ specification / problem space

architectural invariant
→ Architect / solution space
```

Update Architect's:

```text
description
definitions
routing
responsibilities
constraints
output contract
workflow
skill policy
```

accordingly.

Do NOT merely replace the word `domain` with `technical`; make the ownership boundary coherent.

---

# 3. Correct Planner references to ontology/domain semantics

Planner currently treats ontology/domain/topology decisions as Architect ownership.

Refactor this distinction.

Planner MUST NOT define:

```text
product/domain semantics
ontology
identity
business invariants
technical architecture
```

But routing should distinguish:

```text
problem-space semantic gap
→ Orchestrator / SDD

solution-space structural gap
→ Architect
```

Planner remains responsible only for:

```text
task decomposition
dependency mapping
sequencing
phase boundaries
owners
validation obligations
rollback/delivery concerns
```

Preserve the distinction:

```text
spec acceptance criterion
≠
plan phase exit criterion
```

---

# 4. Make assurance genuinely risk-proportional

The current architecture correctly says that:

```text
architecture
planning
research
implementation
QA
review
challenge
operations
```

are conditional phases.

Make this true operationally.

Do NOT hard-code:

```text
every implementation
→ Implementer
→ QA
→ Reviewer
```

as an unconditional pipeline.

Define conceptually:

```text
L0 — isolated / reversible / trivial
L1 — scoped behavior
L2 — material / multi-component
L3 — high-impact / security-sensitive / hard-to-reverse
```

Then allow the Orchestrator to select the **smallest sufficient assurance path**.

Conceptual examples:

```text
L0:
Implementer
→ focused deterministic verification
→ convergence
```

```text
L1:
Implementer
→ focused verification
→ targeted QA or lightweight acceptance when actually justified
```

```text
L2:
Implementer
→ QA
→ Reviewer
```

```text
L3:
required specialist sequence
→ QA
→ Reviewer
+ Challenger / Security / Research / Architecture where justified
```

These are conceptual examples, not mandatory exact routing tables.

The essential rule is:

> Do not invoke an agent merely because it exists in the canonical workflow.

Invoke it only when:

```text
its owned decision
its independent evidence
or its acceptance gate
```

is materially required.

Preserve strict gates where risk requires them.

---

# 5. Do not weaken Reviewer or QA ownership

This optimization MUST NOT collapse:

```text
Implementer
QA
Reviewer
```

into one cognitive role.

Their distinction remains:

```text
Implementer
→ creates implementation evidence

QA
→ independently seeks counterexamples / diagnoses failures

Reviewer
→ judges total evidence and final technical acceptance
```

The change is about **admission**, not responsibility.

Reviewer should remain mandatory wherever configured assurance policy requires independent final acceptance.

QA remains mandatory wherever independent falsification is materially required.

---

# 6. Centralize risk ownership

Currently specialists repeatedly perform essentially the same complete risk classification.

Refactor toward:

```text
Orchestrator
→ owns and records risk_level
```

Specialist handoff includes:

```yaml
risk_level: L0 | L1 | L2 | L3
```

Specialists:

```text
MUST consume assigned risk
MUST NOT downgrade it
SHOULD escalate when new evidence indicates higher risk
```

They SHOULD NOT independently redo the full classification by default.

Replace specialist workflow instructions such as:

```text
Assess the task using <risk_assessment>
```

with something closer to:

```text
Consume the assigned risk level and assess whether new evidence
requires escalation.
```

Do not duplicate the complete L0–L3 definition in every agent if the harness/plugin architecture can provide it reliably as shared policy.

---

# 7. Centralize shared policy only when deterministic

Audit repeated content across agents, especially:

```text
risk definitions
generic handoff fields
Git lifecycle invariants
status vocabulary
commit_shas behavior
changed_files behavior
generic evidence rules
specialist escalation rules
```

Prefer one canonical shared definition when the current Agent Plugin/compiler/harness can guarantee its injection.

Possible concepts:

```text
CanonicalRiskPolicy
CanonicalHandoffContract
CanonicalLifecyclePolicy
```

BUT:

Do NOT replace critical local instructions with references that the runtime may fail to load.

Rule:

```text
If shared policy is deterministically injected
→ centralize it.

If not
→ keep the critical local invariant,
  but remove unnecessary explanatory duplication.
```

Correctness beats deduplication.

---

# 8. Canonical handoff contract

Where practical, normalize common handoff fields conceptually as:

```yaml
handoff:
  status:
  agent:

  consumed_artifacts: []
  produced_artifacts: []

  evidence: []

  changed_files: []
  commit_shas: []

  risks: []
  blockers: []

  suggested_next_owner:
```

Then retain agent-specific extensions.

Examples:

```text
Architect
→ ADRs / architecture constraints

Planner
→ phases / TASK IDs / dependencies

Implementer
→ implementation evidence

QA
→ verdict / defect packets

Reviewer
→ acceptance verdict / findings
```

Do not force every agent to explain the generic schema repeatedly if it is already enforced structurally.

---

# 9. Artifact communication over conversational communication

Strengthen this invariant across the system:

> Agents communicate through durable artifacts, references, deltas and evidence — not duplicated conversational history.

Handoffs SHOULD contain:

```text
artifact IDs
revision IDs
evidence IDs
changed surfaces
new decisions
blockers
deltas
```

rather than reproducing previous context.

Preserve and strengthen the Orchestrator rule:

> Every model invocation must add a distinct decision, artifact, or evidence result.

Avoid:

```text
Agent A summarizes artifact
→ Agent B summarizes summary
→ Agent C summarizes summary again
```

Prefer:

```text
Agent A
→ writes/refers to canonical artifact

Agent B
→ consumes relevant slice directly
```

---

# 10. Evidence reuse

Introduce/strengthen the rule:

```text
VERIFY ONCE
REUSE WHILE FRESH
```

Implementer, DevOps, QA and Reviewer should not automatically rerun identical checks.

A validation result should carry enough identity/provenance to determine whether it remains usable:

```text
subject revision
code revision / commit
command/check
environment where relevant
result
producer
```

Conceptual behavior:

```text
fresh sufficient evidence
→ reuse

stale evidence
→ rerun

different falsification question
→ run additional check
```

Reviewer should primarily consume existing evidence rather than reproducing QA.

QA should only rerun Implementer checks when independent execution is itself necessary or existing evidence is insufficient.

---

# 11. QA / Reviewer overlap

Audit overlap around:

```text
test-quality-review
security
performance
verification
```

Target distinction:

```text
QA
→ produces independent runtime/adversarial evidence
→ may modify QA-owned test surfaces

Reviewer
→ evaluates evidence sufficiency
→ performs static acceptance analysis where required
→ does not recreate a full QA campaign
```

For `test-quality-review`, define conditions so the same deep analysis is not automatically executed twice.

Preserve Reviewer authority.

---

# 12. Challenger must remain rare and independent

Preserve Challenger as a separate agent.

Its admission should remain focused on:

```text
high-impact architecture
breaking change
hard-to-reverse migration
high uncertainty
major governance/workflow decisions
```

It must not become a default phase.

Maintain:

```text
proposal author
→ construct

Challenger
→ attack materialized proposal

decision owner
→ decide
```

Challenger MUST continue judging the artifact rather than relying on the author's hidden reasoning.

---

# 13. Researcher must be budgeted and question-driven

Researcher is useful because it isolates high-token investigation.

Strengthen admission so Researcher receives a narrow evidence question.

Prefer handoffs conceptually like:

```yaml
research_request:
  requested_by: architect

  exact_question: >
    Does library X version Y guarantee property Z?

  supports_artifact:
    id: ADR-003

  evidence_needed:
    - authoritative documentation
    - exact supported versions

  stop_condition: >
    enough evidence exists to decide ADR-003
```

Avoid:

```text
Research this whole topic.
```

Researcher should continue returning a compact evidence packet rather than broad background exposition.

---

# 14. Reasoning effort

Audit the current use of:

```yaml
reasoning-effort: max
```

across nearly all specialists.

Do not assume every invocation deserves maximum reasoning.

Preferred architecture:

```text
reasoning effort
≈ function(task complexity, uncertainty, risk)
```

If the current harness supports dynamic/profile-level reasoning effort, move this decision toward the Harness Profile / runtime policy.

If it does NOT support dynamic effort reliably, choose more economical static defaults by role and preserve escalation through an appropriate higher-cost profile/model where supported.

Do not invent unsupported host features.

Document what the current harness actually permits.

Do not reduce reasoning effort blindly without eval evidence.

---

# 15. Suggested static defaults only if needed

If the host requires static values and no existing eval contradicts this, consider approximately:

```text
Architect
→ high

Challenger
→ high/max

Planner
→ medium

Researcher
→ medium/high depending task

Implementer
→ high

Quality Assurance
→ high

Reviewer
→ high

DevOps
→ medium/high
```

These are hypotheses to evaluate, NOT mandatory values.

Prefer measured optimization over arbitrary tuning.

---

# 16. Do not duplicate semantic modeling inside Architect

If an existing:

```text
semantic-modeling
domain-modeling
spec-driven-development
```

workflow already implements the richer Problem Space model, reuse it.

Do not create a second semantic model system.

Canonical ownership should remain:

```text
Orchestrator / SDD
→ canonical problem-space semantics

Architect
→ technical projection
```

Update any skills routing that contradicts this boundary.

---

# 17. Agent descriptions matter

Update each agent's short `description` where necessary because these descriptions are part of routing/discovery.

They should clearly encode:

```text
WHAT
INVOKE FOR
DO NOT INVOKE FOR
```

Particularly correct Architect so it no longer advertises ownership of canonical domain semantics.

Keep descriptions compact and discriminative.

---

# 18. Preserve good existing boundaries

Do not regress these existing distinctions:

```text
MCP server implementation
→ Implementer

MCP hosting/configuration/deployment
→ DevOps
```

```text
unknown runtime diagnosis
→ QA
```

```text
static/design security acceptance
→ Reviewer where required
```

```text
Git branch/worktree/PR/merge lifecycle
→ Orchestrator
```

```text
focused specialist modification commit
→ modifying specialist where current policy authorizes it
```

Do not broaden these roles accidentally.

---

# 19. Context reconstruction

Where agent instructions currently imply reading broad state, prefer:

```text
task-specific canonical slice
+
relevant artifact references
+
relevant code slice
+
selected skills
```

over inherited conversational history.

Conceptually:

```text
Context(agent, task)
=
minimum relevant state reconstructed from canonical artifacts
```

Do not add a new retrieval framework unless one already exists or is clearly required.

---

# 20. Conditional Planner and Architect

Make explicit:

Architect is required only when a material solution-space decision exists.

Examples:

```text
new component boundary
public interface change
persistence shape
material integration
migration architecture
dependency-direction change
technology tradeoff
```

Planner is required only when material decomposition/sequencing adds value.

Examples:

```text
multi-phase work
dependency-sensitive work
multiple owners
migration/rollout ordering
significant coordination
```

Atomic scoped work should not invoke either agent simply because they exist.

---

# 21. Observability for future cost optimization

Add or preserve structured telemetry sufficient to evaluate each agent's marginal utility.

Useful fields:

```text
agent invoked
admission reason
input/context tokens if available
output tokens if available
latency
artifacts produced
new decisions produced
new material defects found
evidence reused
evidence duplicated
downstream rework caused/prevented
```

Do not build the full self-optimizing system in this change unless already present.

Just ensure agent behavior can later be measured.

---

# 22. Required audit before editing

Before modifying files:

1. inspect all nine agent definitions;
2. identify repeated policies;
3. identify current risk ownership;
4. identify unconditional vs conditional routing;
5. inspect existing SDD/semantic-modeling integration;
6. inspect whether reasoning effort can actually be dynamic in the target harness;
7. identify any generated/compiler-owned portions that should not be manually edited.

Then make the smallest coherent changes.

---

# 23. Validation scenarios

After changes, validate at least these scenarios.

## Scenario A — trivial implementation

```text
Small local reversible bug fix with known behavior.
```

Expected:

```text
no Architect
no Planner
no Challenger
minimal specialist sequence
focused verification
```

QA/Reviewer only according to configured assurance policy.

---

## Scenario B — domain semantic change

```text
Change the lifecycle meaning of Subscription cancellation.
```

Expected:

```text
Orchestrator / SDD updates semantic model/spec
Architect consumes updated semantics
Architect does not redefine them
```

---

## Scenario C — architecture-only change

```text
Approved semantics require a new component boundary.
```

Expected:

```text
Architect owns technical architecture
does not own product semantics
```

---

## Scenario D — significant implementation

```text
Cross-component behavior change, L2.
```

Expected:

```text
appropriate architecture/planning if required
Implementer
QA
Reviewer
```

---

## Scenario E — high-impact migration

Expected:

```text
L3
Architecture
Planning
Challenger when materially useful
Implementation/Operations
QA
Reviewer
```

---

## Scenario F — known evidence reused

```text
Implementer already produced fresh targeted validation evidence.
```

Expected:

```text
QA/Reviewer consume it
do not blindly rerun identical checks
additional checks only for independent falsification or evidence gaps
```

---

# 24. Non-goals

Do NOT:

```text
create new canonical agents
merge existing agents
implement Jev/DecisionEngine
build a new task database
rewrite all skills
create another semantic-model system
remove QA or Reviewer
weaken security or acceptance gates
assume unsupported dynamic host features
```

---

# 25. Final report

Return:

```text
1. Agent files changed.
2. Problem-space ownership changes.
3. Architect boundary before/after.
4. Planner routing changes.
5. Risk-policy deduplication.
6. Assurance-routing changes.
7. QA/Reviewer overlap reductions.
8. Evidence-reuse changes.
9. Shared handoff/policy changes.
10. Reasoning-effort changes or host limitation.
11. Token/context duplication removed.
12. Validation scenarios executed.
13. Remaining duplicated policy and why it remains.
14. Any behavior deliberately left unchanged.
```

# Fundamental principles

Preserve these invariants:

> Orchestrator governs; specialists own their domain.

> Problem-space semantics belong to SDD, not to technical architecture.

> Architect maps semantics into a solution; it does not silently redefine them.

> The canonical workflow is a graph of conditional responsibilities, not a mandatory procession of every agent.

> Risk determines assurance depth, not authority.

> Specialists inherit risk and escalate it; they do not repeatedly rediscover the same risk classification.

> Independent QA and final Review remain distinct capabilities, but are invoked according to assurance requirements.

> Durable artifacts and evidence should replace conversational duplication.

> Fresh evidence should be reused rather than regenerated.

> Every model invocation must justify a distinct new decision, artifact, or evidence result.

> Optimize context and reasoning cost without weakening responsibility boundaries or correctness.
