# PROMPT 1 — Expertise Pack `ML-Eng`

Implémente le premier Expertise Pack prioritaire du repository :

```text
ML-Eng
```

Il s’agit d’un **Vertical Pack**, car il introduit une responsabilité durable nouvelle :

```text
ml-engineer
```

## Objectif

Créer un pack extrêmement efficace pour le développement ML général sans ajouter trop de skills ni polluer les agents non-ML.

Le pack doit ajouter :

```text
1 agent
5 skills maximum en v1
quelques tools MCP déterministes à très forte valeur
```

---

## Agent

Ajouter :

```text
ml-engineer
```

Il possède :

```text
ML problem formulation
dataset suitability
split strategy
experiment design
model-family selection
training strategy
evaluation
error analysis
model selection
model artifact production
reproducibility
```

Il ne possède PAS :

```text
product requirements → orchestrator
system architecture → architect
generic software implementation → implementer
independent falsification → quality-assurance
final acceptance → reviewer
production infrastructure → devops
```

Créer :

```text
definitions
routing
rules
agent-skills
workflow
```

selon les conventions des agents canoniques.

---

## Skills v1

Créer uniquement :

```text
ml-problem-formulation
data-split-design
experiment-design
model-evaluation
model-error-analysis
```

Ne PAS créer immédiatement :

```text
HPO
distillation
quantization
compression
SSL
computer vision
MLOps
```

Ces sujets appartiendront à de futures extensions.

---

## Skill 1 — `ml-problem-formulation`

Couvrir :

```text
target definition
prediction unit
classification/regression/ranking/etc.
label semantics
decision threshold
cost asymmetry
deployment constraints influencing formulation
```

---

## Skill 2 — `data-split-design`

Couvrir :

```text
IID split
group split
entity leakage
near-duplicate leakage
temporal split
stratification
cross-validation
holdout integrity
```

---

## Skill 3 — `experiment-design`

Couvrir :

```text
hypothesis
baseline
controlled variables
varied variables
metrics
seeds
ablation
resource budget
stopping criteria
success criteria
```

---

## Skill 4 — `model-evaluation`

Couvrir :

```text
metric selection
per-slice evaluation
threshold analysis
calibration
confidence/uncertainty when relevant
baseline comparison
robustness
test-set hygiene
```

---

## Skill 5 — `model-error-analysis`

Couvrir :

```text
failure taxonomy
slice analysis
hard-example analysis
confusion structure
label issues
distributional patterns
embedding analysis when useful
```

---

## MCP tools v1

Créer un serveur :

```text
mleng-tools
```

Exposer seulement des tools déterministes à forte valeur :

```text
ml.dataset.inspect
ml.split.audit
ml.experiment.compare
ml.metrics.compare
ml.model.inspect
```

Ne PAS créer :

```text
ml.expert_advice
ml.ask_expert
ml.train_anything
```

---

## Capability projection

Exposer uniquement les capabilities nécessaires.

Exemple :

```yaml
ml-engineer:
  skills:
    - ml-problem-formulation
    - data-split-design
    - experiment-design
    - model-evaluation
    - model-error-analysis

  tools:
    - ml.dataset.inspect
    - ml.split.audit
    - ml.experiment.compare
    - ml.metrics.compare
    - ml.model.inspect

quality-assurance:
  skills:
    - data-split-design
    - model-evaluation
    - model-error-analysis

  tools:
    - ml.dataset.inspect
    - ml.split.audit
    - ml.metrics.compare

reviewer:
  skills:
    - model-evaluation

  tools:
    - ml.experiment.compare
    - ml.metrics.compare
```

Ne pas exposer automatiquement ces capabilities aux agents non concernés.

---

## Intégration Orchestrator

Ne pas hardcoder `ml-engineer` directement dans la logique de l’Orchestrator si un agent registry existe ou peut être introduit proprement.

Le pack doit déclarer :

```text
provides capability:
ml
ml.experimentation
ml.evaluation
```

Le registry doit pouvoir résoudre :

```text
ml.experimentation
→ ml-engineer
```

---

## Artifacts

Supporter des IDs stables au minimum pour :

```text
EXP-*
RUN-*
MODEL-*
EVAL-*
```

Ne pas construire un énorme experiment-management system en v1.

---

## Tests

Tester :

```text
ML formulation → ml-engineer
software API around model → implementer
system serving topology → architect
falsify evaluation → quality-assurance
final evidence review → reviewer
```

Mesurer également le contexte visible lorsqu’ML-Eng est inactif.

Objectif :

```text
zero ML-specific noise outside ML workflows
```