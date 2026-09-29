---
kind: work_brief
status: researched
disposition: partially_adopted
derived_work:
  - docs/harness-history/task_3/manifest.json
  - docs/tasks-history/task_3.jsonl
  - harness_factory/
  - tests/test_harness_factory.py
  - experiments/harness-evals/
  - experiments/routing/
  - outputs/evals/baseline-inventory-r7.json
  - todos/backlog/2026-09-27/cost-eval-opt-followups.md
  - docs/harness-history/task_5/events.jsonl
---

# Phase 2

La phase précédente a établi une infrastructure multi-harness Copilot/Codex avec isolation des runs et cross-validation contrôlée.

Ta mission est maintenant d'ajouter la couche d'évaluation comportementale.

Cette phase doit utiliser **Codex comme harness principal pour les évaluations coûteuses**, car le budget disponible y est significativement plus important.

GitHub Copilot doit être utilisé avec parcimonie.

# 1. Cost policy

Adopter cette politique par défaut :

```text
Static checks
→ deterministic/local

Heavy behavioral benchmark
→ Codex

Optimization experiments
→ Codex

Large repeated eval corpus
→ Codex

Copilot-specific conformance
→ Copilot

Copilot smoke tests
→ Copilot

Cross-harness comparison
→ Codex + minimal required Copilot sample
```

Ne jamais lancer le même gros corpus sur Copilot par défaut.

# 2. Copilot budget is scarce

Toute invocation Copilot dans les evals doit avoir une justification explicite :

```yaml
reason:
  copilot_specific_behavior
  portability_sample
  regression_confirmation
  host_specific_agent_behavior
```

MUST NOT utiliser Copilot uniquement parce que les tests existent.

# 3. Build a Harness Conformance / Behavioral Suite

Structurer les scénarios de façon harness-neutral lorsque possible.

Types initiaux :

```text
skill discovery
skill routing
workflow routing
agent routing
plugin loading
MCP exposure
risk-proportional routing
evidence reuse
cross-harness materialization
```

Chaque scénario doit avoir :

```yaml
id:
category:

fixture:
base_revision:

prompt:

expected:
required:
forbidden:
optional:

metrics:
```

# 4. Establish baselines

Créer des baselines pour comparer :

```text
flat skills
vs
hierarchical skills
```

et, lorsque les artefacts existent :

```text
old routing behavior
vs
new risk-proportional behavior
```

Mesurer au minimum quand disponible :

```text
task success
required-skill recall
false skill loads
workflow selection
agent calls
model calls
input tokens
output tokens
tool calls
latency
duplicate checks
evidence reuse
```

Unknown reste unknown.

# 5. Codex-first execution

Les gros benchmarks doivent pouvoir être lancés explicitement sur Codex uniquement.

Conceptuellement :

```text
pluginctl eval run <suite> --target codex
```

et :

```text
pluginctl eval compare <suite> --targets codex,copilot
```

La comparaison Copilot ne doit utiliser qu'un échantillon pertinent sauf demande explicite.

# 6. Cross-harness validation

Quand Copilot développe une modification affectant Codex :

```text
Copilot
→ isolated Codex validation
```

Quand Codex développe une modification affectant Copilot :

```text
Codex
→ isolated Copilot validation
```

Mais toujours :

```text
validator != development owner
```

et :

```text
validator cannot recursively delegate
```

# 7. Evaluation artifacts

Chaque run doit produire un artefact durable, machine-readable.

Exemple :

```yaml
eval_run:
  id:
  suite:
  harness:
  model:
  base_revision:
  plugin_profile:

  results:
  metrics:
  failures:

  token_usage:
  latency:

  raw_artifacts:
```

Ne mets pas les résultats uniquement dans du Markdown.

Markdown peut être une projection humaine.

# 8. Differential evaluation

Introduire progressivement :

```text
same fixture
same prompt
same expected behavior
```

puis comparer :

```text
Codex
vs
Copilot
```

L'objectif n'est PAS de déterminer un "meilleur modèle".

L'objectif est :

```text
detect harness-specific assumptions
detect portability failures
detect routing differences
detect context-cost differences
```

# 9. Benchmark budgets

Supporter des budgets explicites :

```yaml
budget:
  max_runs:
  max_model_calls:
  max_tokens_if_known:
  max_failures_before_stop:
```

Fail fast pour :

```text
broken materialization
broken plugin load
schema error
systematic routing failure
```

Ne gaspille pas de quota sur des scénarios condamnés.

# 10. Prepare for future SkillOpt

Ne l'implémente PAS encore.

Mais les evals doivent pouvoir servir plus tard comme fonction d'évaluation pour :

```text
SkillOpt
GEPA
custom optimizer
self-evolving harness
```

Donc séparer :

```text
candidate generation
```

de :

```text
evaluation
```

L'evaluator doit pouvoir prendre une variante de plugin/profile et produire des métriques sans connaître comment cette variante a été créée.

# 11. Final deliverable

Retourner :

1. suites créées;
2. baselines disponibles;
3. commandes Codex-first;
4. points où Copilot reste obligatoire;
5. règles budgétaires;
6. résultats des petits smoke/eval tests nécessaires;
7. NE PAS lancer encore une optimisation massive;
8. indiquer exactement ce qui est prêt pour la phase self-improvement.

Stop après cette phase.