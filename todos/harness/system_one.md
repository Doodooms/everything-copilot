# Objectif

Introduire une nouvelle couche :

```text
Decision Plane
```

chargée des décisions fréquentes, compactes et typées qui ne justifient pas nécessairement un appel à un LLM génératif généraliste.

Cette architecture doit être **indépendante de Jev**.

Jev est le premier backend expérimental, pas le contrat du système.

---

# 1. Séparer trois niveaux de décision

Architecture cible :

```text
                    WORKFLOW STATE
                         │
                         ▼
                  DECISION REQUEST
                         │
             ┌───────────┴───────────┐
             │                       │
       SYSTEM 0                 unresolved
     deterministic                   │
       rules                         ▼
                              SYSTEM 1
                           Decision Model
                          Jev / future backend
                                   │
                         low confidence /
                         unsupported case
                                   │
                                   ▼
                              SYSTEM 2
                          Generative LLM
```

## System 0

Logique exacte :

```text
capability registry
explicit ownership
schema validation
dependency resolution
static rules
```

## System 1

Décisions sémantiques compactes :

```text
classification
routing
yes/no gates
risk scoring
relevance
admission
```

## System 2

Raisonnement génératif complexe :

```text
architecture
planning
implementation
diagnosis
research
review
```

---

# 2. Ne jamais appeler Jev lorsqu’une règle déterministe suffit

Exemple :

```text
TASK required_capability = ml.training
registry owner = ml-engineer
```

Résultat :

```text
ml-engineer
```

Aucun modèle.

À l’inverse :

```text
Does this vague requested change materially require
architecture work?
```

peut être candidat au Decision Plane.

---

# 3. Créer une abstraction `DecisionEngine`

Ne pas exposer Jev directement dans Orchestrator.

Créer un contrat backend-neutral.

Conceptuellement :

```python
DecisionEngine.evaluate(
    state,
    questions,
)
```

Question types internes :

```text
BooleanDecision
ChoiceDecision
ScoreDecision
```

Mappings Jev :

```text
BooleanDecision → Noul
ChoiceDecision  → Choice
ScoreDecision   → Score
```

Le reste du framework ne doit jamais dépendre de ces noms Jev.

---

# 4. Backend interface

Conceptuellement :

```text
DecisionBackend

├── DeterministicBackend
├── JevBackend
├── LLMDecisionBackend
└── future local/open-weight backend
```

Chaque backend annonce :

```text
supported question types
latency class
cost class
availability
model/version
```

---

# 5. Decision Request

Définir un contrat stable :

```yaml
decision:
  id: DEC-*
  type: boolean | choice | score

  purpose: architecture_required

  state:
    ...

  criteria:
    ...

  options:
    ...

  policy:
    confidence_threshold: ...
    fallback: generative
```

Éviter de transmettre tout le contexte conversationnel.

Le Decision Plane reçoit un **state minimal structuré**.

---

# 6. Decision Result

```yaml
decision_result:
  decision_id: DEC-*
  backend: jev
  backend_version: ...
  selected: ...
  probabilities: ...
  confidence: ...
  latency_ms: ...
  fallback_required: false
```

Tous les résultats doivent être auditables.

---

# 7. Policy Engine

Séparer :

```text
prediction
```

de :

```text
action policy
```

Exemple :

```text
Decision Model:
P(architecture_required) = 0.89
```

Puis :

```text
Policy:
if p >= 0.85 → architecture required
if p <= 0.15 → skip
otherwise → System 2 fallback
```

Le modèle ne décide donc pas directement des permissions.

Le code interprète le résultat.

---

# 8. Ne pas hardcoder un seuil universel

Les seuils doivent être définis par décision.

Le coût d’un faux positif et faux négatif diffère entre :

```text
load optional skill?
```

et :

```text
skip security review?
```

Les thresholds doivent être calibrés par eval.

---

# 9. Premier use case : shadow routing

NE PAS donner immédiatement au Decision Plane l’autorité sur le workflow.

Commencer par :

```text
current production decision
             │
             ├── actual workflow
             │
             └── Decision Plane shadow evaluation
```

Il observe sans influencer l’exécution.

---

# 10. Dataset de shadow evaluation

Enregistrer :

```text
minimal state
available choices
current decision
decision-plane result
probabilities
confidence
eventual workflow outcome
human/eval label when available
```

Ne jamais enregistrer inutilement du contexte sensible ou volumineux.

---

# 11. Premier benchmark : agent routing

Candidats :

```text
architect
planner
researcher
implementer
quality-assurance
reviewer
challenger
devops
registered plugin specialists
```

Mais System 0 élimine d’abord les impossibilités.

Exemple :

```text
candidate set after deterministic filtering:
implementer
quality-assurance
```

System 1 décide seulement entre les candidats plausibles.

---

# 12. Deuxième benchmark : workflow gates

Tester en shadow :

```text
architecture_required?
planning_required?
challenger_required?
research_required?
```

Ne pas commencer par des gates de sécurité ou d’acceptation finale.

---

# 13. Skill relevance comme benchmark, pas comme intercepteur

Le Decision Plane peut aussi être évalué sur :

```text
is performance-profiling relevant?
is implementation-design relevant?
is test-quality-review relevant?
```

Mais il ne doit PAS devenir un service obligatoire précédant chaque `skill` call.

La Local Skill Policy de A reste autonome.

Le Decision Plane peut ultérieurement fournir un signal facultatif pour les cas ambigus.

---

# 14. Troisième benchmark : materiality / risk

Exemples :

```text
material_change?
hard_to_reverse?
architecture_consequential?
high_blast_radius?
```

Ces décisions sont intéressantes car elles sont sémantiques mais ont une sortie compacte.

---

# 15. Ne pas déléguer certaines autorités

Le Decision Plane ne devient PAS propriétaire de :

```text
Reviewer final approval
QA verdict
security acceptance
architecture decisions
product requirements
production modifications
```

Il peut fournir un signal.

L’agent responsable conserve l’autorité.

---

# 16. Eval architecture

Créer un dataset versionné :

```text
decision-evals/
├── agent-routing/
├── workflow-gates/
├── materiality/
└── skill-relevance/
```

Chaque exemple contient :

```text
state
question
valid options
ground truth / reference
cost of false positive
cost of false negative
```

---

# 17. Métriques

Mesurer au minimum :

```text
accuracy
macro F1 where relevant
false-negative rate
false-positive rate
calibration
abstention/fallback rate
latency
cost
stability across repeated calls
```

Pour les décisions à risques asymétriques :

```text
expected decision cost
```

est plus important que l’accuracy brute.

---

# 18. Calibration

Pour une décision binaire, mesurer la relation :

```text
predicted probability
vs
observed correctness/frequency
```

Utiliser :

```text
reliability diagram
Brier score
ECE if appropriate
```

Le but est de pouvoir utiliser rationnellement des thresholds.

---

# 19. Shadow criteria avant production

Ne pas activer un use case avant d’avoir démontré :

```text
acceptable decision quality
acceptable calibration
meaningful latency/cost benefit
stable behavior
safe fallback
```

sur ton propre corpus.

Les résultats publiés du fournisseur ne remplacent pas cette validation.

---

# 20. Progressive authority

Déployer par niveaux :

```text
LEVEL 0
shadow only

LEVEL 1
recommendation only

LEVEL 2
autonomous decision on low-risk branches
with fallback

LEVEL 3
broader autonomous routing
after evidence
```

Ne pas sauter directement au niveau 3.

---

# 21. Fallback

Chaque type de décision possède une policy.

Exemple :

```text
high confidence
→ use System 1 decision

ambiguous
→ generative LLM

backend unavailable
→ generative LLM or deterministic safe default

invalid response
→ fail closed / fallback according to decision class
```

Jev outage ne doit jamais casser tout `agentic-workflow`.

---

# 22. Batching / parallel questions

L’abstraction doit permettre plusieurs questions indépendantes sur le même state :

```text
architecture_required?
planner_required?
challenger_required?
material_change?
```

en une seule requête backend lorsque celui-ci le permet.

Mais garder les résultats logiquement indépendants.

---

# 23. Observability

Créer un event log distinct :

```text
DECISION_REQUEST
DECISION_RESULT
DECISION_FALLBACK
DECISION_OVERRIDE
```

Avec :

```text
decision ID
purpose
backend
model version
latency
cost
confidence
selected result
fallback
```

Ne pas polluer les specialist handoffs.

---

# 24. Reproducibility

Les décisions probabilistes ne seront pas forcément bitwise reproductibles.

La reproductibilité signifie ici :

```text
same decision schema
same backend/model version
same policy
same thresholds
same evaluation dataset
recorded original output
```

Ne pas confondre avec déterminisme.

---

# 25. Security / trust

Le backend reçoit uniquement le state nécessaire.

Ajouter :

```text
decision data classification
allowed backend
redaction policy
```

Certains états pourront exiger :

```text
local backend only
```

dans le futur.

---

# 26. Jev adapter

Implémenter Jev uniquement comme :

```text
decision/backends/jev
```

Il traduit :

```text
BooleanDecision
ChoiceDecision
ScoreDecision
```

vers son API puis normalise les résultats.

Aucune logique de workflow dans l’adapter.

---

# 27. LLM fallback adapter

Implémenter également un backend génératif conforme au même contrat.

Cela permet des A/B :

```text
Jev
vs
current Luna routing
vs
larger reasoning model
```

sur exactement les mêmes questions.

---

# 28. Pas de MCP obligatoire

Je ne ferais pas nécessairement du Decision Plane un MCP au départ.

S’il appartient directement au runtime/harness :

```text
internal library/service
```

est plus simple.

Exposer un MCP seulement si plusieurs processus/clients doivent réellement partager cette capability.

---

# 29. Ordre d’implémentation

```text
1. Define Decision Plane ontology.
2. Define backend-neutral question/result schemas.
3. Define policy/fallback schema.
4. Implement deterministic backend.
5. Implement generative-LLM baseline backend.
6. Implement event telemetry.
7. Build versioned routing eval dataset.
8. Implement Jev adapter.
9. Run offline eval.
10. Run shadow agent-routing evaluation.
11. Analyze calibration/cost/latency.
12. Add workflow-gate shadow evaluation.
13. Add materiality/risk shadow evaluation.
14. Define per-decision thresholds from evidence.
15. Enable one low-risk decision in recommendation mode.
16. Compare outcomes.
17. Enable autonomous low-risk routing only if justified.
18. Keep expanding decision coverage based on measured ROI.
```

---

# 30. First production candidate

Le premier use case autonome devrait être quelque chose de facilement recoverable.

Par exemple :

```text
select among already-valid candidate specialists
```

après System 0 filtering.

Pas :

```text
skip Reviewer
skip security review
declare convergence
```

---

# 31. Definition of Done v1

Le Decision Plane v1 est terminé lorsque :

```text
framework is backend-independent
Jev is only one adapter
deterministic rules remain preferred when sufficient
System 1 decisions have explicit schemas
probabilities are separated from action policies
fallback is always available
routing can run in shadow mode
decision events are auditable
eval dataset exists
calibration is measured
one low-risk use case can be enabled independently
Jev failure cannot break the canonical workflow
```

La v1 ne doit PAS chercher à remplacer l’intelligence générative des agents.

Son but est seulement d’extraire les petites décisions répétitives et structurables vers une primitive plus adaptée.
