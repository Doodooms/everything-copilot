---
kind: design_input
status: researched
disposition: deferred
derived_work: []
---

> **Design/research input — not an approved implementation plan.**

# Phase 3

Le système dispose maintenant :

```text
Agent Plugin Factory
+ Copilot adapter
+ Codex adapter
+ isolated harness runs
+ behavioral eval suites
+ machine-readable metrics
+ Codex-first heavy benchmark execution
```

Construis maintenant le socle d'un système capable de s'évaluer et de proposer ses propres améliorations.

IMPORTANT :

Cette première version MUST NOT auto-promote arbitrary mutations.

Target:

```text
observe
→ diagnose
→ propose
→ evaluate
→ report
```

NOT:

```text
observe
→ rewrite canonical source automatically
```

# 1. Evaluation feedback loop

Construire :

```text
RUNS
 ↓
structured traces
 ↓
failure / inefficiency detection
 ↓
candidate improvement proposal
 ↓
isolated candidate profile/plugin
 ↓
Codex-heavy evaluation
 ↓
comparison
 ↓
promotion recommendation
```

# 2. Failure signatures

Créer une représentation structurée des échecs :

```yaml
failure_signature:
  observed_failure:
  expected_behavior:
  causal_mechanism:
  affected_surface:

  classification:
    harness
    skill
    workflow
    tool
    model
    specification
    environment
    unknown

  evidence:
```

Ne pas traiter tout échec comme problème de prompt.

# 3. Mutation surfaces

Commencer uniquement avec des surfaces relativement sûres :

```text
skill description
workflow routing metadata
context policy
budget
reasoning profile
tool exposure
verification policy
```

Canonical agent ownership and semantic architecture remain protected.

# 4. Bounded mutation

Une proposition doit être :

```text
grounded
minimal
one hypothesis
measurable
reversible
```

Pas de réécriture générale.

# 5. Codex as optimization compute

Les opérations coûteuses futures telles que :

```text
candidate evaluation
large benchmark sweeps
SkillOpt
GEPA-like optimization
ablation
```

doivent cibler Codex par défaut lorsque techniquement possible.

Copilot ne sert qu'aux validations nécessitant réellement son harness.

# 6. Candidate isolation

Chaque candidat doit être évalué sans modifier la source canonique.

Conceptuellement :

```text
Canonical Plugin
      ↓
Candidate Overlay
      ↓
Materialized Candidate Profile
      ↓
Eval
```

# 7. Promotion gate

Comparer au baseline.

Ne pas optimiser uniquement le pass rate.

Considérer :

```text
correctness
routing recall
false loads
tokens
latency
tool calls
duplicate work
evidence reuse
complexity
```

Une amélioration qui gagne 0.2% mais multiplie les tokens par 3 n'est pas automatiquement meilleure.

# 8. Preservation contracts

Ajouter des comportements qu'une optimisation ne doit pas casser.

Exemples :

```text
trivial task avoids full SDD
Architect does not own domain semantics
QA does not repair production code
Reviewer does not rerun full QA
Challenger remains conditional
specialists preserve ownership boundaries
```

# 9. Shadow mode

Toute nouvelle optimisation automatique commence en :

```text
shadow
```

Elle produit :

```text
what it would have changed
expected effect
measured candidate result
```

mais ne modifie pas automatiquement le profil actif.

# 10. Future optimizer interface

Préparer une interface backend-neutral permettant plus tard :

```text
SkillOpt
GEPA
LLM proposer
deterministic optimizer
```

sans coupler les evals à un optimizer spécifique.

# 11. Lineage

Chaque candidat doit connaître :

```text
parent
mutation
evidence
evaluation
status
```

afin de permettre audit et rollback.

# 12. Non-goals

Ne pas encore :

```text
auto-modify canonical agents
auto-promote high-risk mutations
allow unbounded self-recursion
build graphd
start Substrat
build a generic AGI loop
```

# 13. Final deliverable

Retourner :

1. trace/eval architecture;
2. FailureSignature representation;
3. mutation representation;
4. candidate isolation;
5. Codex-first evaluator integration;
6. promotion gate;
7. preservation contracts;
8. shadow-mode flow;
9. backend interface for future SkillOpt;
10. smallest experiment proving the loop end-to-end.

Stop before enabling autonomous promotion.
