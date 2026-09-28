# Mission

Construire une architecture générique d’**Expertise Packs** permettant d’installer à la demande une expertise complète dans `agentic-workflow`, puis utiliser **ML-Eng** comme première implémentation de référence et priorité absolue.

L’objectif final est de pouvoir installer des packs tels que :

```text
ML-Eng
RustDev
Azure
MLOps
DataEngineering
Embedded
SecurityEngineering
...
```

sans charger leurs connaissances, skills, agents ou tools dans les projets qui n’en ont pas besoin.

Le système doit conserver la séparation suivante :

```text
AGENT
= WHO owns a durable responsibility

SKILL
= HOW an agent performs an expert reusable method

MCP TOOL
= WHAT deterministic or external capability can be executed

EXPERTISE PACK
= HOW a coherent domain expertise is packaged, versioned,
  validated, installed and projected onto agents

VERTICAL PACK
= Expertise Pack that additionally contributes one or more
  genuinely new durable agent responsibilities
```

`ML-Eng` doit être traité comme un **Vertical Pack**, car le lifecycle ML possède des responsabilités qui ne se réduisent pas à celles de l’Implementer logiciel classique.

---

# 1. Principe architectural

Ne pas écrire directement un plugin ML-Eng couplé à GitHub Copilot.

Construire d’abord :

```text
Expertise Pack Source
        ↓
Normalized Pack IR
        ↓
Pack Compiler
        │
        ├── Portable Agent Plugin
        │     ├── plugin.json
        │     ├── skills/
        │     └── mcp.json
        │
        ├── Copilot Adapter
        │     └── com.github.copilot/
        │           └── agents/
        │
        └── Codex Adapter
              └── generated agent/config declarations
```

La représentation source du pack est la source de vérité.

Tous les formats clients sont des artefacts compilés.

Ne jamais maintenir manuellement deux copies sémantiquement équivalentes d’un agent pour Copilot et Codex.

---

# 2. Contraintes de compatibilité

Agent Plugins 1.0 définit uniquement comme composants portables :

```text
skills
MCP servers
```

Les agents sont client-specific.

Donc :

```text
skills/
mcp.json
```

constituent le cœur portable d’un pack.

Pour Copilot, générer les agents dans :

```text
com.github.copilot/
└── agents/
```

Pour Codex, générer son format natif actuel d’agents/subagents à partir du même IR.

Avant d’implémenter un adapter client :

```text
1. consulter sa documentation actuelle ;
2. valider son format ;
3. ne jamais inventer un format supposé.
```

---

# 3. Structure générale du subsystem

Créer une infrastructure générique de packs.

Structure conceptuelle :

```text
expertise/
├── schema/
│   ├── pack.schema.json
│   ├── capability.schema.json
│   ├── agent.schema.json
│   ├── projection.schema.json
│   └── policy.schema.json
│
├── compiler/
│   ├── parser/
│   ├── validator/
│   ├── ir/
│   ├── lowering/
│   └── targets/
│       ├── portable-agent-plugin/
│       ├── copilot/
│       └── codex/
│
├── registry/
│   ├── capability_registry.*
│   └── resolver.*
│
├── packs/
│   └── ml-eng/
│
├── tests/
│
└── docs/
```

Adapter les noms à l’architecture réelle du repository.

Ne pas créer un second système de compilation si le repository possède déjà une abstraction appropriée.

---

# 4. Pack IR

Créer une représentation intermédiaire canonique indépendante de Copilot, Codex et MCP.

Exemple conceptuel :

```yaml
pack:
  id: ml-eng
  version: 0.1.0
  type: vertical

  provides:
    capabilities:
      - ml
      - ml.problem-formulation
      - ml.dataset-analysis
      - ml.experiment-design
      - ml.training
      - ml.evaluation
      - ml.error-analysis
      - ml.optimization

  agents:
    contributed:
      - ml-engineer

    extended:
      - architect
      - planner
      - researcher
      - implementer
      - quality-assurance
      - reviewer
      - devops

  skills:
    - ml-problem-formulation
    - dataset-analysis
    - experiment-design
    - model-selection
    - training-design
    - model-evaluation
    - model-error-analysis
    - ml-reproducibility

  mcp_servers:
    - mleng-tools

  policies:
    capability_projection: ...
```

L’IR doit être validé avant tout lowering client-specific.

---

# 5. Manifest source du pack

Créer :

```text
expertise/packs/ml-eng/pack.yaml
```

Schéma recommandé :

```yaml
schema_version: 1

id: ml-eng
version: 0.1.0

display_name: ML Engineering
description: >
  Expert capabilities for dataset analysis, experiment design,
  model development, training, evaluation and model artifact
  production.

type: vertical

provides:
  capabilities:
    - ml
    - ml.problem-formulation
    - ml.dataset-analysis
    - ml.data-splitting
    - ml.experiment-design
    - ml.model-selection
    - ml.training
    - ml.evaluation
    - ml.error-analysis
    - ml.reproducibility

requires:
  core_agents:
    - orchestrator
    - architect
    - planner
    - researcher
    - implementer
    - quality-assurance
    - reviewer
    - devops

agents:
  contribute:
    - ml-engineer

  extend:
    - architect
    - planner
    - researcher
    - quality-assurance
    - reviewer
    - devops

portable:
  skills: true
  mcp: true

mcp:
  servers:
    - mleng-tools

security:
  trust_level: local-executable

compatibility:
  agent_plugins: ">=1.0"
```

Le schéma définit la sémantique ; ne pas dépendre de YAML libre non validé.

---

# 6. Pourquoi créer `ml-engineer`

`ml-engineer` doit être un vrai agent parce qu’il possède un lifecycle différent de celui de `implementer`.

L’Implementer construit du comportement logiciel :

```text
TASK
→ code
→ tests
→ validation
```

Le ML Engineer possède :

```text
ML objective
    ↓
dataset
    ↓
split/protocol
    ↓
baseline
    ↓
experiment
    ↓
training
    ↓
evaluation
    ↓
error analysis
    ↓
model selection
    ↓
model artifact
```

Ses artefacts principaux ne sont pas seulement des commits.

Ils incluent :

```text
dataset revision
split revision
experiment ID
training configuration
checkpoint
metrics
baseline
evaluation report
selected model
model artifact
reproducibility evidence
```

C’est une responsabilité durable suffisamment différente pour justifier un agent.

---

# 7. Frontière exacte de `ml-engineer`

L’agent ML Engineer possède :

```text
ML problem formulation
dataset suitability analysis
experimental protocol
baseline strategy
model-family selection within approved architecture
training strategy
loss/metric choices
experiment execution
model evaluation
error analysis
model selection
model artifact handoff
ML reproducibility
```

Il ne possède PAS :

```text
product requirements
global system architecture
generic software implementation
production deployment infrastructure
final acceptance
independent QA
```

Ces responsabilités restent :

```text
Orchestrator
Architect
Implementer
DevOps
Reviewer
Quality Assurance
```

---

# 8. Interaction Architect ↔ ML Engineer

Ne pas laisser `ml-engineer` devenir un Architect bis.

Architect décide par exemple :

```text
batch inference vs online inference
model/service boundaries
data ownership
feature pipeline boundaries
storage contracts
serving interfaces
training/serving topology
```

ML Engineer décide par exemple :

```text
classification vs regression formulation
ConvNeXt vs ViT family
loss function
augmentation strategy
optimizer
training schedule
evaluation metrics
sampling strategy
```

Règle :

```text
SYSTEM SHAPE
→ Architect

MODEL/EXPERIMENT SHAPE
→ ML Engineer
```

Lorsque la décision ML modifie significativement l’architecture système :

```text
ML Engineer
→ Orchestrator
→ Architect
```

---

# 9. Interaction Implementer ↔ ML Engineer

ML Engineer peut modifier :

```text
training code
evaluation code
dataset transforms
model definitions
experiment configuration
ML-specific utilities
```

Implementer reste propriétaire de :

```text
product APIs
business logic
generic services
UI
non-ML application code
integration code outside ML ownership
```

Lorsqu’une feature nécessite :

```text
model
+
product integration
```

le plan peut créer :

```text
TASK-ML-*
→ ml-engineer

TASK-SW-*
→ implementer
```

Les artefacts doivent rester séparés.

---

# 10. Interaction QA ↔ ML Engineer

QA ne doit pas simplement vérifier :

```text
training script runs
```

QA doit pouvoir falsifier les claims ML.

Exemples :

```text
data leakage
split contamination
metric misuse
class imbalance failure
distribution shift sensitivity
seed instability
overfitting
evaluation contamination
threshold instability
performance regression
model export mismatch
inference discrepancy
```

ML Engineer produit les claims.

QA tente de les casser.

---

# 11. Interaction Reviewer ↔ ML Engineer

Reviewer reste la gate finale.

Il consomme :

```text
ML objective
dataset revision
experiment protocol
baseline
selected metrics
experiment evidence
QA findings
model artifact
reproducibility evidence
```

Le Reviewer ne refait pas les expériences.

Il évalue la suffisance des preuves.

---

# 12. Skills ML-Eng v1

Ne pas commencer avec 30 skills.

Créer un noyau de skills orthogonales.

## `ml-problem-formulation`

Responsabilité :

```text
business/product objective
→ ML formulation
```

Doit traiter :

```text
target definition
classification/regression/ranking/etc.
cost asymmetry
prediction unit
decision threshold
label semantics
deployment constraints affecting formulation
```

---

## `dataset-analysis`

Responsabilité :

```text
understand whether the available data can support the ML objective
```

Inclure :

```text
dataset structure
label distribution
duplicates
missingness
class imbalance
sampling bias
temporal structure
group structure
potential leakage
data quality
coverage
```

---

## `data-split-design`

Responsabilité :

```text
design statistically valid train/validation/test separation
```

Inclure :

```text
IID split
group split
temporal split
entity leakage
near duplicates
stratification
cross-validation
holdout policy
```

Cette skill est suffisamment critique pour être séparée de dataset-analysis.

---

## `experiment-design`

Responsabilité :

```text
construct a falsifiable experiment
```

Inclure :

```text
hypothesis
baseline
controlled variables
metrics
comparison protocol
seed strategy
resource budget
stopping criteria
ablation strategy
```

---

## `model-selection`

Responsabilité :

```text
select model families using dataset/task inductive biases
```

Ne pas transformer cette skill en catalogue de modèles.

Elle doit raisonner sur :

```text
data regime
inductive biases
invariances/equivariances
latency
memory
deployment constraints
label volume
pretraining availability
```

---

## `training-design`

Responsabilité :

```text
training objective and optimization protocol
```

Inclure :

```text
loss
optimizer
scheduler
regularization
augmentation
batching
sampling
mixed precision
checkpointing
early stopping
```

---

## `model-evaluation`

Responsabilité :

```text
determine whether model evidence supports the claimed objective
```

Inclure :

```text
metrics
confidence intervals when appropriate
threshold analysis
per-slice metrics
calibration
robustness
baseline comparison
statistical uncertainty
```

---

## `model-error-analysis`

Responsabilité :

```text
convert model failures into actionable hypotheses
```

Inclure :

```text
slice analysis
confusion/error taxonomy
hard examples
embedding inspection when relevant
label issues
distributional patterns
failure clustering
```

---

## `ml-reproducibility`

Responsabilité :

```text
ensure another run can reconstruct the result
```

Inclure :

```text
code revision
dataset revision
config
seed
environment
dependency versions
hardware
checkpoint
metrics
artifact lineage
```

---

# 13. Skills ML-Eng v2 — ne pas implémenter immédiatement

Prévoir l’architecture pour :

```text
hyperparameter-optimization
model-compression
knowledge-distillation
quantization
pruning
inference-optimization
self-supervised-learning
foundation-model-adaptation
active-learning
uncertainty-estimation
embedding-analysis
feature-engineering
```

Ne les créer que lorsqu’un besoin réel démontre qu’elles ne tiennent plus proprement dans les skills v1.

---

# 14. Sous-packs spécialisés futurs

Ne pas mettre Computer Vision, NLP, tabular, recommender systems, etc. directement dans ML-Eng v1.

Prévoir :

```text
ml-eng
    │
    ├── cv
    ├── nlp
    ├── tabular
    ├── time-series
    └── recommender
```

Exemple futur :

```text
ML-CV Expertise Pack
```

dépend de :

```text
ml-eng
```

et fournit :

```text
image-augmentation-design
vision-backbone-selection
object-detection
segmentation
geometric-registration
vision-ssl
vision-distillation
```

Ainsi ML-Eng reste canonique.

---

# 15. MCP `mleng-tools`

Créer un serveur MCP local :

```text
mleng-tools
```

Le serveur expose uniquement des opérations déterministes ou des accès structurés.

Il ne doit pas devenir un deuxième agent.

Ne jamais créer :

```text
ml.expert_advice(prompt)
```

qui renvoie simplement du texte généré.

---

# 16. Outils MCP v1

Prioriser des tools qui augmentent réellement les capacités de l’agent.

## Environment

```text
ml.env.inspect
```

Retour structuré :

```text
Python
CUDA
cuDNN
PyTorch/TensorFlow/JAX versions
available accelerators
CPU/GPU details
memory
relevant environment flags
```

---

## Dataset

```text
ml.dataset.inspect
```

Retour :

```text
shape
schema
dtypes
label distribution
missing values
duplicates
basic statistics
group/time metadata when supplied
```

Ne pas charger automatiquement tout un dataset énorme.

Supporter sampling.

---

## Split audit

```text
ml.split.audit
```

Détecter :

```text
overlap
duplicate leakage
group leakage
temporal leakage
label imbalance
split inconsistency
```

---

## Experiment metadata

```text
ml.experiment.inspect
ml.experiment.compare
```

Comparer plusieurs résultats de manière structurée.

---

## Metrics

```text
ml.metrics.compute
ml.metrics.compare
```

Support initial :

```text
classification
regression
```

Éviter une taxonomie gigantesque v1.

---

## Model inspection

```text
ml.model.inspect
```

Retour possible :

```text
parameter count
trainable count
input/output shapes
module summary
checkpoint metadata
device/dtype
```

---

## Model profiling

```text
ml.model.profile
```

Mesurer :

```text
latency
memory
throughput
parameter count
FLOPs when reliable
```

Ne pas inventer de FLOPs si la méthode ne peut pas les calculer correctement.

---

## Artifact inspection

```text
ml.artifact.inspect
```

Pour :

```text
checkpoint
ONNX
TorchScript
OpenVINO
metadata
```

---

# 17. Outils dangereux ou coûteux

Ne PAS exposer initialement un tool générique :

```text
ml.train(...)
```

capable de lancer arbitrairement des entraînements coûteux.

Préférer v1 :

```text
inspect
validate
profile
compare
audit
```

Les trainings continuent à être exécutés via le contexte contrôlé du workspace.

Si `training.launch` est ajouté plus tard :

```text
explicit resource limits
explicit command/config
approval gate
timeout
GPU count
cost/resource policy
artifact destination
```

doivent être obligatoires.

---

# 18. Providers ML externes

Ne pas coupler le core ML-Eng à MLflow ou Weights & Biases.

Définir une interface provider :

```text
experiment_tracking
model_registry
dataset_registry
compute_backend
```

Puis adaptateurs optionnels :

```text
MLflow
Weights & Biases
Azure ML
SageMaker
Vertex AI
```

ML-Eng doit fonctionner sans eux.

---

# 19. Capability Registry

Créer un registry global.

Chaque pack déclare :

```text
provides
requires
conflicts
version
security profile
```

Exemple :

```yaml
id: ml-eng

provides:
  - ml
  - ml.training
  - ml.evaluation
  - ml.dataset-analysis

requires:
  - core.spec-driven-development

optional:
  - mlflow
  - wandb
```

---

# 20. Capability Resolver

L’Orchestrator ne doit pas décider :

```text
install ml-eng
```

à partir d’un nom arbitraire.

Les phases amont déclarent des capabilities.

Exemple Architect :

```yaml
required_capabilities:
  - ml
  - ml.training
  - ml.evaluation
```

Le resolver fait :

```text
ml.training
    ↓
registry
    ↓
ml-eng@0.1.0
```

Puis l’Orchestrator peut activer le pack approuvé.

---

# 21. Installation vs activation

Séparer :

```text
installed
```

de :

```text
active
```

Un pack peut être installé localement mais non actif pour la session/projet.

L’activation doit produire une capability projection.

---

# 22. Capability Projection

Chaque agent ne voit que le sous-ensemble pertinent.

Exemple ML-Eng :

```yaml
projections:

  orchestrator:
    capabilities:
      - ml
    skills: []

  architect:
    skills:
      - ml-problem-formulation
      - model-selection

  planner:
    skills:
      - experiment-design

  researcher:
    skills:
      - ml-research

  ml-engineer:
    skills:
      - ml-problem-formulation
      - dataset-analysis
      - data-split-design
      - experiment-design
      - model-selection
      - training-design
      - model-evaluation
      - model-error-analysis
      - ml-reproducibility

    tools:
      - ml.env.inspect
      - ml.dataset.inspect
      - ml.split.audit
      - ml.experiment.inspect
      - ml.experiment.compare
      - ml.metrics.compute
      - ml.metrics.compare
      - ml.model.inspect
      - ml.model.profile
      - ml.artifact.inspect

  quality-assurance:
    skills:
      - dataset-analysis
      - data-split-design
      - model-evaluation
      - ml-reproducibility

    tools:
      - ml.dataset.inspect
      - ml.split.audit
      - ml.metrics.compute
      - ml.metrics.compare
      - ml.artifact.inspect

  reviewer:
    skills:
      - model-evaluation
      - ml-reproducibility

  devops:
    skills: []
```

Ne pas exposer automatiquement tous les tools à tous les agents.

---

# 23. Nouveau `ml-engineer.agent`

Créer une définition source indépendante du client.

Exemple :

```text
expertise/packs/ml-eng/agents/ml-engineer.agent.yaml
```

Ne pas écrire directement le Markdown Copilot comme source de vérité.

---

# 24. Ontologie de `ml-engineer`

Les definitions doivent être réellement sémantiques.

Inclure au minimum :

```text
ML objective
dataset revision
label
feature
data split
data leakage
baseline
experiment
hypothesis
training run
evaluation protocol
metric
checkpoint
model artifact
model selection
reproducibility evidence
```

Éviter :

```text
focused role
routing refusal
```

qui ne sont pas des concepts de domaine.

---

# 25. Routing `ml-engineer`

ACCEPT :

```text
ML problem formulation
dataset suitability
split design
experiment design
model-family selection
training strategy
model evaluation
error analysis
model selection
model artifact production
```

REJECT :

```text
product requirement ambiguity
→ orchestrator

system architecture
→ architect

generic delivery planning
→ planner

non-ML product implementation
→ implementer

independent falsification
→ quality-assurance

final acceptance
→ reviewer

production ML infrastructure
→ devops / future MLOps pack
```

---

# 26. Artifact model ML

Créer des IDs stables.

Exemple :

```text
DATASET-*
SPLIT-*
EXP-*
RUN-*
MODEL-*
EVAL-*
```

Ils complètent :

```text
SPEC-*
REQ-*
AC-*
ADR-*
TASK-*
QA-RUN-*
REVIEW-*
```

Exemple :

```text
TASK-014
→ EXP-006
→ RUN-031
→ MODEL-009
→ EVAL-012
```

---

# 27. Experiment Contract

Un experiment doit être matérialisé.

Schéma conceptuel :

```yaml
experiment:
  id: EXP-006

  hypothesis: ...

  dataset: DATASET-002
  split: SPLIT-003

  baseline: MODEL-001

  model_family: ...

  controlled_variables: ...

  varied_variables: ...

  metrics:
    - ...

  seeds:
    - ...

  resource_budget: ...

  success_criteria:
    - ...

  stopping_criteria:
    - ...
```

Éviter les experiments implicites uniquement décrits dans le contexte LLM.

---

# 28. Run Contract

Chaque training run doit pouvoir être reconstruit.

```yaml
run:
  id: RUN-031

  experiment: EXP-006

  code_revision: ...
  dataset_revision: ...
  split_revision: ...

  config: ...

  environment: ...

  seed: ...

  hardware: ...

  checkpoint: ...

  metrics: ...
```

---

# 29. Model Artifact Contract

Un modèle sélectionné doit produire :

```yaml
model:
  id: MODEL-009

  originating_run: RUN-031

  checkpoint: ...

  preprocessing: ...

  input_contract: ...

  output_contract: ...

  evaluation: EVAL-012

  limitations: ...

  deployment_constraints: ...
```

---

# 30. Integration avec SDD

Le workflow devient :

```text
USER
 ↓
ORCHESTRATOR
 ↓
SPEC-DRIVEN-DEVELOPMENT
 ↓
ARCHITECT
 ↓
PLANNER
 ↓
ML-ENGINEER
 ├── dataset
 ├── experiments
 ├── training
 ├── evaluation
 └── model artifact
 ↓
QUALITY ASSURANCE
 ↓
REVIEWER
 ↓
CONVERGENCE
```

Lorsque le modèle doit être intégré dans un produit :

```text
ML-ENGINEER
    ↓ model artifact

IMPLEMENTER
    ↓ software integration

QA
    ↓ system falsification

REVIEWER
```

---

# 31. Planification hybride

Planner doit pouvoir créer :

```text
TASK-ML-001 → ml-engineer
TASK-SW-002 → implementer
TASK-OPS-003 → devops
```

avec dépendances :

```text
TASK-ML-001
      ↓
TASK-SW-002
      ↓
TASK-OPS-003
```

Le plan ne doit pas supposer que toutes les tâches sont des tâches de coding.

---

# 32. ML QA

Étendre le QA existant grâce au pack.

Ne pas créer `ml-qa-agent` en v1.

Les skills ML spécialisent le QA canonique.

QA doit pouvoir chercher :

```text
data leakage
split leakage
invalid metric
evaluation leakage
seed instability
overfitting
calibration issues
slice regressions
model export mismatch
preprocessing mismatch
non-deterministic regressions
inference/training discrepancy
```

---

# 33. ML Reviewer

Ne pas créer `ml-reviewer`.

Reviewer canonique + ML-Eng skills doit suffire.

Reviewer doit évaluer :

```text
problem formulation validity
dataset/split validity
experiment validity
baseline adequacy
metric appropriateness
evaluation sufficiency
reproducibility
artifact lineage
known limitations
```

sans exécuter lui-même l’expérimentation.

---

# 34. MLOps n’est pas ML-Eng v1

Ne pas mettre dans ML-Eng :

```text
model serving infrastructure
GPU autoscaling
model registry promotion
shadow deployments
A/B deployment
drift monitoring
automatic retraining
feature store operations
```

Ces sujets appartiendront à :

```text
MLOps Expertise Pack
```

qui pourra initialement étendre DevOps.

Créer un agent `mlops-engineer` seulement si son lifecycle finit par justifier une responsabilité propre.

---

# 35. Compiler target : Portable Agent Plugin

Le compiler doit produire :

```text
dist/ml-eng/portable/
├── plugin.json
├── skills/
│   ├── ml-problem-formulation/
│   ├── dataset-analysis/
│   ├── data-split-design/
│   ├── experiment-design/
│   ├── model-selection/
│   ├── training-design/
│   ├── model-evaluation/
│   ├── model-error-analysis/
│   └── ml-reproducibility/
│
└── mcp.json
```

Respecter exactement Agent Plugins 1.0.

Pas d’agents portables inventés.

---

# 36. Compiler target : Copilot

Produire :

```text
dist/ml-eng/copilot/
├── plugin.json
├── skills/
├── mcp.json
└── com.github.copilot/
    └── agents/
        └── ml-engineer.agent.md
```

Le `.agent.md` est généré à partir de l’agent IR.

Il doit respecter les conventions des agents existants :

```text
frontmatter
definitions
routing
rules
agent-skills
workflow
```

---

# 37. Compiler target : Codex

Créer un adapter indépendant.

À partir du même agent IR, générer la configuration custom-agent/subagent actuellement supportée par Codex.

Le compiler doit mapper :

```text
name
description
model policy
reasoning policy
instructions
tool/capability projection
```

vers le format Codex réel.

Ne pas faire de ce format un contrat interne.

---

# 38. Client Adapter Interface

Créer une abstraction :

```text
TargetCompiler
```

avec conceptuellement :

```text
validate_support(pack_ir)
compile_portable_components(pack_ir)
compile_agents(pack_ir)
compile_client_extensions(pack_ir)
emit_manifest(pack_ir)
```

Les adapters ne doivent pas contenir la sémantique ML.

Ils ne font que lowering.

---

# 39. Versioning

Chaque pack doit avoir :

```text
pack version
schema version
skill versions if necessary
MCP server version
compatibility metadata
```

Utiliser semver.

Un changement breaking de capability contract doit augmenter la version majeure.

---

# 40. Lockfile

Créer un lockfile projet :

```text
expertise.lock
```

Exemple :

```yaml
packs:
  ml-eng:
    version: 0.3.1
    digest: ...
    source: ...

capabilities:
  ml.training:
    provider: ml-eng
```

Objectifs :

```text
reproducibility
auditability
deterministic activation
supply-chain integrity
```

---

# 41. Trust model

Ne jamais permettre :

```text
Orchestrator searches Internet
→ downloads arbitrary MCP
→ executes it
```

Séparer :

```text
discovery
installation
approval
activation
```

L’Orchestrator peut automatiquement activer un pack déjà approuvé.

Une nouvelle installation doit passer par une policy explicite.

---

# 42. Permission model

Les capabilities doivent être projetées selon le principe du moindre privilège.

Exemple :

```text
ml-engineer
→ dataset read
→ experiment execution
→ model artifact write

reviewer
→ read-only model/evidence inspection

quality-assurance
→ test/evaluation execution
→ QA artifact write

architect
→ read-only ML context
```

---

# 43. MCP schemas

Chaque tool doit avoir :

```text
narrow purpose
strict input schema
strict output schema
bounded side effects
explicit errors
```

Éviter :

```text
ml.run(command: string)
```

Préférer :

```text
ml.model.profile(...)
ml.split.audit(...)
```

Les tools arbitraires shell-like détruisent l’intérêt du MCP.

---

# 44. MCP result provenance

Chaque résultat doit pouvoir inclure :

```text
tool version
timestamp
workspace revision
dataset revision
environment
input digest
output digest
warnings
```

Particulièrement important en ML.

---

# 45. Evals du pack ML-Eng

Le pack ne doit pas être considéré bon parce qu’il semble expert.

Créer des evals.

Catégories :

```text
routing
problem formulation
data leakage
experiment design
model selection
evaluation validity
reproducibility
tool selection
context efficiency
```

---

# 46. Routing evals

Tester que :

```text
"design temporal validation split"
→ ml-engineer

"build REST endpoint around selected model"
→ implementer

"choose online vs batch inference architecture"
→ architect

"try to expose leakage in the evaluation"
→ quality-assurance

"deploy model with autoscaling"
→ devops / future MLOps

"review whether experiment evidence justifies acceptance"
→ reviewer
```

---

# 47. Skill routing evals

Exemples :

```text
"Which metric should we use?"
→ model-evaluation

"How should this dataset be split?"
→ data-split-design

"ConvNeXt or ViT?"
→ model-selection

"Why is validation performance unstable?"
→ model-error-analysis / experiment-design depending evidence

"What training objective?"
→ training-design
```

Mesurer les false triggers.

---

# 48. Expertise evals

Créer des cas réellement difficiles.

Par exemple :

```text
duplicate leakage across product IDs

temporal leakage

wrong metric under severe imbalance

threshold selected on test set

baseline missing

HPO performed against test set

seed-sensitive claimed improvement

confounded augmentation ablation

distribution shift hidden by aggregate metric

model improvement smaller than run variance
```

Le pack doit améliorer significativement les décisions par rapport aux agents canoniques seuls.

---

# 49. A/B baseline

Évaluer :

```text
BASELINE
canonical agent only

vs

ML-ENG
canonical agent + expertise pack
```

Comparer :

```text
task correctness
domain-error rate
routing correctness
tool-call correctness
token usage
unnecessary context
factual hallucination
evidence quality
```

---

# 50. Context-budget eval

Mesurer explicitement :

```text
tokens loaded before ML-Eng activation
tokens loaded after activation
skill descriptions visible
tool schemas visible
unused capability exposure
```

Le pack échoue architecturalement s’il pollue significativement les agents non concernés.

---

# 51. Progressive disclosure

Maintenir trois niveaux :

```text
PACK ACTIVATION
only ML projects receive ML-Eng

SKILL DISCOVERY
only skill metadata initially visible

SKILL LOAD
full workflow only when matched

TOOL PROJECTION
only relevant MCP schemas visible to the agent
```

Le système doit préserver ces quatre barrières.

---

# 52. ML-Eng capability projection tests

Tester notamment que :

```text
Reviewer
MUST NOT see training mutation tools.

Architect
MUST NOT see experiment execution tools by default.

QA
MUST NOT see production-code mutation capabilities.

ML Engineer
MUST NOT receive deployment-admin capabilities.

Non-ML Implementer
MUST NOT see ML tools when ML-Eng is inactive.
```

---

# 53. Installation workflow

Créer un workflow déterministe :

```text
resolve pack
    ↓
validate manifest
    ↓
validate signature/digest
    ↓
validate compatibility
    ↓
compile target
    ↓
install portable components
    ↓
install target adapter
    ↓
register capabilities
    ↓
remain inactive until requested
```

---

# 54. Activation workflow

```text
architecture/task requires capability
        ↓
capability resolver
        ↓
approved installed pack found
        ↓
activate pack
        ↓
compute per-agent projections
        ↓
expose skills/tools/agents
        ↓
record activation in task state
```

---

# 55. Deactivation workflow

À la fin :

```text
remove active capability projection
retain installed pack
retain audit/version
```

Ne pas désinstaller automatiquement.

---

# 56. Convergence avec SDD

Le canonical SDD state doit enregistrer :

```text
active expertise packs
pack versions
artifacts produced
ML task IDs
experiment IDs
model IDs
QA evidence
review evidence
```

La convergence ne doit pas être possible si un artefact ML requis est stale.

Exemple :

```text
dataset revision changed
→ SPLIT stale
→ EXP stale
→ MODEL evidence stale
→ REVIEW stale
```

---

# 57. Dependency graph ML

Ajouter conceptuellement :

```text
SPEC
 ↓
ML OBJECTIVE
 ↓
DATASET
 ↓
SPLIT
 ↓
EXPERIMENT
 ↓
RUN
 ↓
MODEL
 ↓
EVALUATION
 ↓
QA
 ↓
REVIEW
```

Les changements amont invalident seulement les descendants concernés.

---

# 58. Documentation automatique du pack

Chaque pack doit générer :

```text
README
capability catalog
agent catalog
skill catalog
tool catalog
permissions
compatibility matrix
```

Ces docs sont dérivées du manifest/IR lorsque possible.

---

# 59. Linting

Créer :

```text
validate_pack.py
```

ou intégrer au linter existant.

Vérifier :

```text
schema validity
duplicate capabilities
missing skills
missing tools
agent references
projection references
unknown capabilities
dependency cycles
invalid client targets
unreachable skills
unexposed required tools
forbidden tool exposure
```

---

# 60. Build command

Prévoir une interface simple :

```text
pack build ml-eng --target copilot
pack build ml-eng --target codex
pack build ml-eng --target portable
```

et :

```text
pack validate ml-eng
pack test ml-eng
```

Le CLI exact dépend de l’architecture existante.

---

# 61. Première milestone

Ne pas essayer de construire tout ML-Eng immédiatement.

Milestone 1 doit prouver :

```text
pack source
→ IR
→ validation
→ Copilot plugin
→ one custom ml-engineer
→ 3 skills
→ 3 MCP tools
→ routing/evals
```

Skills :

```text
ml-problem-formulation
dataset-analysis
experiment-design
```

Tools :

```text
ml.env.inspect
ml.dataset.inspect
ml.split.audit
```

---

# 62. Deuxième milestone

Ajouter :

```text
data-split-design
model-selection
training-design
model-evaluation
```

Tools :

```text
ml.metrics.compute
ml.metrics.compare
ml.model.inspect
```

---

# 63. Troisième milestone

Ajouter :

```text
model-error-analysis
ml-reproducibility
```

Tools :

```text
ml.experiment.inspect
ml.experiment.compare
ml.model.profile
ml.artifact.inspect
```

Puis integration complète SDD.

---

# 64. Quatrième milestone

Implémenter Codex adapter.

Ne le faire qu’après stabilisation de l’IR grâce au target Copilot.

Le but est de prouver que :

```text
same source agent
same skills
same MCP
```

peuvent produire :

```text
Copilot package
Codex package
```

sans duplication sémantique.

---

# 65. Ce qu’il ne faut PAS faire

MUST NOT :

```text
create one MCP server per skill
create one agent per ML subdomain
put all ML knowledge inside ml-engineer.agent
duplicate ML instructions in Copilot and Codex adapters
expose all MCP tools to every agent
auto-install arbitrary Internet MCP servers
make ML-Eng depend on one vendor such as W&B
put MLOps into ML-Eng v1
create CV/NLP-specific knowledge in the generic ML pack
use generic shell tools where narrow structured MCP tools are possible
treat experiment prose as durable state
allow model claims without dataset/split/run provenance
```

---

# 66. Definition of Done — framework

Le framework Expertise Pack est terminé lorsque :

```text
- pack.yaml has a validated schema
- Pack IR exists and is client-independent
- compiler has target adapters
- portable Agent Plugin output is standards-compliant
- Copilot adapter can emit custom agents
- capability registry works
- capability resolver works
- per-agent projection works
- versioning works
- lockfile works
- activation/deactivation are explicit
- trust policy exists
- deterministic validation exists
- routing eval infrastructure exists
```

---

# 67. Definition of Done — ML-Eng v1

ML-Eng v1 est terminé lorsque :

```text
- ml-engineer is a distinct validated agent
- its routing does not overlap materially with Architect,
  Implementer, QA or Reviewer

- core ML skills exist:
  ml-problem-formulation
  dataset-analysis
  data-split-design
  experiment-design
  model-selection
  training-design
  model-evaluation
  model-error-analysis
  ml-reproducibility

- mleng-tools exposes deterministic ML tools

- tools use strict schemas

- ML artifacts have stable IDs

- experiments are reproducible from durable metadata

- QA can independently falsify ML claims

- Reviewer can evaluate ML evidence

- SDD can track ML artifacts and staleness

- non-ML tasks receive zero unnecessary ML capability exposure

- Copilot package builds successfully

- portable plugin validates against Agent Plugins 1.0

- baseline vs ML-Eng eval demonstrates a real improvement
```

---

# 68. Final architecture cible

```text
                    AGENTIC WORKFLOW CORE
                             │
          ┌──────────────────┼──────────────────┐
          │                  │                  │
     Core Agents        Core Skills         Core Tools
          │                  │                  │
          └──────────────────┼──────────────────┘
                             │
                     Capability Resolver
                             │
                 ┌───────────┴───────────┐
                 │                       │
            Installed Packs         Project State
                 │                       │
                 └───────────┬───────────┘
                             │
                         Activation
                             │
              ┌──────────────┼──────────────┐
              │              │              │
           ML-Eng          RustDev         Azure
              │
       ┌──────┼─────────┐
       │      │         │
   ML Agent  Skills  MCP Tools
       │
       └──────── capability projection ────────┐
                                               │
     Architect  Planner  ML Engineer  QA  Reviewer
```

---

# 69. Ordre d’implémentation obligatoire

Implémenter dans cet ordre :

```text
1. Inspect existing repository compiler/scaffolding abstractions.
2. Define Expertise Pack ontology.
3. Define pack.yaml schema.
4. Define normalized Pack IR.
5. Implement parser.
6. Implement structural validator.
7. Implement capability registry.
8. Implement capability resolver.
9. Implement projection model.
10. Implement portable Agent Plugin target.
11. Implement Copilot target.
12. Scaffold ML-Eng pack.
13. Implement ml-engineer source definition.
14. Implement first three ML skills.
15. Implement mleng-tools MCP skeleton.
16. Implement env.inspect.
17. Implement dataset.inspect.
18. Implement split.audit.
19. Implement routing tests.
20. Implement capability-leakage tests.
21. Build/install ML-Eng for Copilot.
22. Run first baseline vs ML-Eng evaluation.
23. Fix architecture before adding breadth.
24. Add remaining ML v1 skills.
25. Add remaining ML v1 tools.
26. Integrate ML artifact lineage with SDD.
27. Integrate QA and Reviewer ML evidence.
28. Stabilize Pack IR.
29. Implement Codex adapter.
30. Produce end-to-end documentation.
```

Do NOT skip directly to building many ML skills before proving the pack architecture.

---

# 70. Final report attendu

À la fin de l’implémentation, produire :

```text
1. Architecture implemented.
2. Files created/modified.
3. Pack source schema.
4. Pack IR schema.
5. Capability registry design.
6. Resolver design.
7. Projection design.
8. ML-Eng agent definition.
9. ML-Eng skill catalog.
10. ML-Eng MCP tool catalog.
11. Portable output tree.
12. Copilot output tree.
13. Codex support status.
14. Security/trust model.
15. Tests.
16. Eval results.
17. Known limitations.
18. Deferred ML skills.
19. Deferred MLOps capabilities.
20. One complete example:
    user ML request
    → SDD
    → architecture
    → ML-Eng activation
    → ML Engineer
    → experiment
    → model artifact
    → QA
    → Reviewer
    → convergence.
```

Ne pas déclarer l’architecture terminée uniquement parce qu’un plugin peut être installé.

Le critère principal est :

> **ML-Eng doit améliorer fortement les capacités ML de l’agent tout en restant totalement absent du contexte des workflows qui n’en ont pas besoin.**
