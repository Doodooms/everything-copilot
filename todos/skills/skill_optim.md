# Mission

Implémente dans ce repository un système complet, déterministe et testable pour :

1. mener une **étude d’ablation de l’architecture de routing des Agent Skills VS Code/GitHub Copilot** ;
2. sélectionner une architecture canonique de routing applicable à tous les futurs skills ;
3. générer les futurs skill packages à partir d’un **scaffold déterministe figé** ;
4. faire évoluer `create-skill` pour qu’il utilise ce scaffold ;
5. créer un nouveau skill utilisateur `optimize-skill` ;
6. faire générer par `optimize-skill` un benchmark Waza adversarial et immuable pour un skill donné ;
7. connecter ce benchmark à SkillOpt pour optimiser le contenu sémantique du skill sans modifier son architecture ;
8. comparer finalement le skill initial `S0` au skill optimisé `S*` sur un holdout complexe indépendant.

Ne demande pas de confirmation intermédiaire. Inspecte d’abord le repository existant, réutilise les conventions et scripts déjà présents lorsque cela est pertinent, puis implémente la solution complète.

Ne lance pas automatiquement les expériences LLM coûteuses. Implémente le harness, ses tests déterministes et les commandes permettant à l’utilisateur de lancer les expériences explicitement.

---

# 0. Sources techniques à considérer comme références

Avant d’implémenter les intégrations Waza et SkillOpt :

1. inspecte les versions réellement installées ou installables ;
2. consulte leur `--help` et leur documentation correspondant à cette version ;
3. si documentation et code divergent, considère le code/CLI de la version utilisée comme source de vérité ;
4. n’invente aucun flag ou champ YAML.

Références Waza principales :

* repository `microsoft/waza`
* `site/src/content/docs/reference/cli.mdx`
* `waza-runner/references/EVAL-SPEC.md`
* documentation des graders
* `waza new eval`
* `waza run`
* `waza spec verify`
* `waza tokens`
* graders :

  * `skill_invocation`
  * `behavior`
  * `tool_constraint`
  * `action_sequence`
  * `program`
  * `file`
  * `diff`
  * `prompt`

Attention particulière : les trigger evals doivent mesurer une **invocation réelle du skill**.

Certaines versions/configurations Waza injectent directement le contenu du `SKILL.md` lorsqu’un champ `skill:` est présent dans l’eval. Cela invalide un test de discovery puisque le modèle connaît déjà le corps du skill sans l’avoir invoqué.

Vérifie le mécanisme actuellement supporté par la version utilisée pour obtenir :

```text
agent sees:
    skill name + description

agent does NOT see:
    full SKILL.md body

until:
    actual skill invocation
```

Si la version actuelle expose une option officielle de type summary-only/no-body-injection, utilise-la.

Sinon, utilise uniquement un comportement officiellement supporté par cette version. Ne dépends pas silencieusement d’un workaround obsolète.

Ne considère pas automatiquement le grader Waza `trigger` comme preuve d’une invocation réelle. Pour la phase d’ablation, privilégie les événements observables de type :

```text
skill invocation
tool invocation
workflow-entry sentinel read
```

Références SkillOpt principales :

* repository `microsoft/SkillOpt`
* `docs/index.md`
* `docs/guideline.html`
* `docs/guide/training-loop.md`
* `docs/guide/skill-document.md`
* `docs/guide/new-benchmark.md`
* `docs/reference/api.md`
* `docs/reference/cli.md`
* `docs/guide/configuration.md`

SkillOpt doit être utilisé comme **moteur d’optimisation**, pas comme benchmark universel.

Waza doit être considéré comme **moteur d’évaluation/instrumentation**.

---

# 1. Principes architecturaux non négociables

Le système doit respecter les séparations suivantes :

```text
Waza
    = evaluation / measurement

SkillOpt
    = search / semantic optimization

routing ablation
    = architecture optimization

scaffolder
    = deterministic package structure

validator
    = structural invariants

create-skill
    = semantic authoring of a skill within the frozen structure

optimize-skill
    = benchmark creation + benchmark freezing + SkillOpt orchestration
```

Ne fusionne pas ces responsabilités.

---

# 2. Usage explicite des meta-skills

`create-skill` et `optimize-skill` sont des primitives volontairement invoquées par l’utilisateur.

Ils ne doivent pas entrer en concurrence avec les skills système de GitHub Copilot lors du discovery automatique.

Quand supporté par le runtime courant, configure-les conceptuellement comme :

```yaml
user-invocable: true
disable-model-invocation: true
context: fork
```

Vérifie les noms/champs exacts dans la documentation VS Code courante avant modification.

La `description` de ces meta-skills doit donc rester concise et descriptive ; elle n’a pas besoin de pratiquer du keyword stuffing destiné au discovery automatique.

Cependant `create-skill` conserve une admission interne, même lorsqu’il est appelé explicitement :

```text
/create-skill ...
        ↓
admission
        ↓
ACCEPT → create skill
REJECT → explain why + suggested routing
```

---

# 3. PHASE 0 — étude d’ablation du routing

## Objectif

Trouver une **architecture de routing canonique**, réutilisable par tous les futurs skills.

Cette phase n’évalue PAS la task completion métier du skill.

Elle évalue uniquement :

```text
discovery
admission
rejection
rerouting
workflow-entry
routing token cost
```

Le workflow réel ne doit jamais être exécuté pendant cette étude.

---

# 4. Variables étudiées pendant l’ablation

Faire l’étude en deux étapes afin d’éviter une explosion combinatoire.

## Phase 0A — organisation du progressive disclosure

Prévoir au minimum les variantes suivantes :

### A — convention simple

```text
description
    ↓
SKILL.md containing workflow
```

### B — admission + workflow inline

```text
description
    ↓
SKILL.md
    ├── definitions
    ├── admission
    ├── routing
    └── workflow
```

### C — admission inline + workflow deferred

```text
description
    ↓
SKILL.md
    ├── definitions
    ├── admission
    └── routing
            ↓ ACCEPT only
       external workflow
```

Ajouter d’autres variantes uniquement si elles testent une hypothèse structurelle réellement différente.

Ne mélange pas encore table/list/routing representation à cette phase.

---

# 5. Phase 0B — représentation de l’admission

Une fois la meilleure organisation du progressive disclosure sélectionnée, garder cette architecture figée et comparer uniquement la représentation de la décision.

Prévoir au minimum :

### A — grouped lists

```markdown
## ACCEPT
- ...
- ...

## REJECT
- ... → route
- ... → route
```

### B — Markdown table

```markdown
| Request | Decision | Route |
|---|---|---|
| ... | ACCEPT | - |
| ... | REJECT | create-agent |
```

### C — éventuellement une troisième forme compacte

Seulement si elle constitue réellement une représentation différente et pertinente.

Toutes les variantes doivent contenir **strictement le même contenu sémantique**.

---

# 6. Panel fixe de skills pour l’ablation

Ne génère pas des skills sémantiquement différents pour chaque architecture.

Créer d’abord un panel fixe d’environ 5 spécifications sémantiques représentatives.

Par exemple :

```text
S1 — skill simple et clairement distinct des voisins
S2 — skill ayant une frontière sémantique proche d’un autre primitive
S3 — skill avec plusieurs tools
S4 — skill dont le workflow réel serait coûteux
S5 — skill avec plusieurs cas REJECT/routing subtils
```

Ces 5 spécifications deviennent des fixtures immuables de l’expérience.

Idéalement, représenter leur contenu sémantique dans un manifeste machine-readable séparé de leur rendu Markdown.

Exemple conceptuel :

```yaml
name: example-skill

description:
  what: ...
  use_for:
    - ...
  do_not_use_for:
    - ...

definitions:
  ...

accept:
  - ...

reject:
  - case: ...
    route: ...

workflow_semantics:
  ...
```

Les architectures candidates doivent être **rendues à partir des mêmes manifests**.

Ne demande pas à un LLM de réinventer chaque skill pour chaque architecture : cela introduirait un facteur confondant.

L’étude doit comparer la structure, pas les capacités de génération du modèle.

---

# 7. Sentinel déterministe de workflow-entry

C’est un invariant essentiel de la Phase 0.

Nous devons savoir de manière observable si :

```text
skill invoked
    ↓
admission accepted
    ↓
agent started entering workflow
```

sans laisser le modèle exécuter le vrai workflow.

Pour cela, chaque fixture de routing-ablation doit contenir un **test-only workflow-entry sentinel**.

Créer par exemple :

```text
references/__routing_probe__.md
```

Le premier acte qu’un skill doit effectuer **après ACCEPT et avant toute vraie action métier** doit être :

```text
read __routing_probe__.md
```

Quand le workflow est inline, la première instruction du workflow doit déclencher cette lecture.

Quand le workflow est deferred, l’admission ACCEPT doit déclencher cette lecture **avant de charger le vrai workflow externe**.

Le contenu du sentinel utilisé uniquement par le harness d’ablation doit imposer quelque chose équivalent à :

```text
ROUTING_EVAL_WORKFLOW_ENTRY

This file is an evaluation sentinel.

Its successful read proves that admission accepted the request and execution crossed the workflow-entry boundary.

STOP IMMEDIATELY.

Do not invoke another tool.
Do not read the real workflow.
Do not modify files.
Do not continue execution.

Return exactly:
ROUTING_EVAL_ACCEPTED
```

Ce sentinel est uniquement un instrument expérimental.

Il ne doit PAS devenir une lecture inutile dans les skills de production une fois l’architecture sélectionnée.

Le harness doit pouvoir l’ajouter aux fixtures d’ablation sans polluer le scaffold final.

---

# 8. Pourquoi le sentinel doit être placé avant le vrai workflow

Pour une architecture avec workflow inline :

```text
SKILL.md already loaded
    ↓
ACCEPT
    ↓
read sentinel
    ↓
STOP
```

Le coût de tokens du workflow inline a déjà été payé lorsque `SKILL.md` est chargé.

Pour une architecture avec workflow deferred :

```text
SKILL.md routing loaded
    ↓
ACCEPT
    ↓
read sentinel
    ↓
STOP
```

Le vrai `workflow.md` n’est jamais chargé pendant l’ablation.

Cela permet de mesurer correctement :

```text
routing context cost
```

et la différence de coût introduite par le progressive disclosure.

Pour rendre la comparaison juste, les variantes inline et deferred doivent contenir un workflow sémantique/payload représentatif de taille équivalente.

Le workflow inline peut donc contenir après le sentinel le même payload qui se trouverait dans le fichier externe de la variante deferred.

Il ne sera jamais exécuté, mais son coût de contexte sera réel.

---

# 9. États à distinguer pendant l’évaluation du routing

Le harness doit reconstruire explicitement les états suivants.

## True positive complet

```text
prompt should use skill
skill invoked
admission ACCEPT
sentinel read
no workflow action after sentinel
```

## False negative discovery

```text
prompt should use skill
skill never invoked
```

## False positive discovery récupéré par admission

```text
prompt should NOT use skill
skill invoked
admission REJECT
sentinel NOT read
correct routing returned if deterministic
```

Ce cas doit être considéré comme :

```text
discovery failure
but
admission recovery success
```

Ne le confonds pas avec un échec end-to-end total.

## False positive final

```text
prompt should NOT use skill
skill invoked
sentinel read
```

C’est une erreur critique de routing.

## Correct negative

```text
prompt should NOT use skill
skill not invoked
```

## Rejection correctement routée

```text
REJECT
+
suggested_route == expected route
```

## Rejection sans route déterministe

Autoriser :

```json
{
  "status": "rejected",
  "routing": null
}
```

si le skill sait qu’il doit refuser mais ne peut pas déterminer localement la destination.

---

# 10. Contrat de retour des REJECT

Standardiser le résultat de rejet des skills expérimentaux et futurs skills qui utilisent cette convention.

Conceptuellement :

```json
{
  "status": "rejected",
  "skill": "<skill-name>",
  "reason": "<concise reason>",
  "routing": "<suggested route or null>"
}
```

Le skill suggère une route.

Le parent/master reste responsable de la décision globale.

---

# 11. Métriques Phase 0

Implémente les métriques suivantes.

## Discovery metrics

```text
discovery_precision
discovery_recall
discovery_f1
discovery_false_positive_rate
discovery_false_negative_rate
```

## Admission metrics

```text
admission_accept_precision
admission_accept_recall
false_positive_recovery_rate
false_positive_final_rate
```

## Routing metrics

```text
reject_route_accuracy
reject_without_route_rate
```

## Workflow boundary metrics

```text
expected_workflow_entry_rate
unexpected_workflow_entry_rate
workflow_entry_after_reject = MUST BE 0
post_sentinel_tool_calls = MUST BE 0
```

## Efficiency

```text
mean_tokens_until_terminal_routing_decision
median_tokens_until_terminal_routing_decision
p95_tokens_until_terminal_routing_decision
mean_tool_calls_until_terminal_routing_decision
```

Si Waza expose directement ces valeurs, réutilise-les.

Sinon calcule-les à partir de ses résultats/traces avec un script d’analyse local.

Ne mesure pas la qualité du workflow métier à cette phase.

---

# 12. Trials de routing

Contrairement aux task-completion evals futures, les tests de routing sont peu coûteux.

Rendre configurable :

```text
trials_per_task
```

Choisir une valeur raisonnable > 1 pour la Phase 0, par exemple 5 par défaut si le budget local le permet.

Le runner doit accepter :

```text
--trials N
```

afin de pouvoir augmenter la confiance sur les cas ambigus.

Les résultats doivent agréger :

```text
mean
variance/std where relevant
success frequency
```

---

# 13. Waza Phase 0

Utiliser Waza comme instrumentation réelle.

Préférer des graders qui observent des événements :

```text
skill_invocation
tool_constraint
behavior
action_sequence
program
```

Les tests de discovery doivent vérifier l’invocation réelle du skill.

Les tests d’admission doivent détecter :

```text
sentinel read
or
rejection output
```

Le harness doit pouvoir vérifier qu’aucun outil métier n’a été appelé après le sentinel.

Si Waza ne permet pas nativement d’exprimer exactement une métrique nécessaire, ajouter un `program` grader ou un post-processing script.

Ne modifie pas Waza lui-même pour des besoins spécifiques si un adapter local suffit.

---

# 14. Isolation expérimentale

Les skills expérimentaux ne doivent pas polluer le catalogue normal du repository.

Les manifests et templates d’ablation restent dans le repository.

Le runner doit matérialiser chaque candidat dans un workspace temporaire isolé.

Conceptuellement :

```text
routing-ablation/
├── specs/
├── architectures/
├── runner/
└── results/

runtime:
temporary-workspace/
└── skills/
    └── candidate skill(s)
```

Évite de placer 20 variantes de skills directement sous `.github/skills/`.

---

# 15. Sélection de l’architecture gagnante

Ne sélectionne PAS simplement la moyenne d’un score pondéré opaque.

Utilise des contraintes.

Exemple conceptuel :

```text
final false-positive rate <= threshold
admission recovery >= threshold
routing accuracy >= threshold
workflow_entry_after_reject == 0
```

Parmi les architectures qui passent les contraintes :

```text
maximize routing quality
then minimize routing token cost
```

Rendre les seuils configurables.

Produire un rapport comparatif machine-readable et humain :

```text
results.json
results.md
```

avec chaque architecture × chaque skill × métriques agrégées.

---

# 16. Architecture canonique

Une fois une architecture gagnante sélectionnée, le système doit pouvoir matérialiser une configuration canonique persistante.

Par exemple :

```text
config/canonical-skill-architecture.yaml
```

Elle doit décrire uniquement des choix structurels, par exemple :

```yaml
progressive_disclosure: deferred_workflow
admission_representation: accept_reject_lists
definitions_before_admission: true
workflow_location: references/workflow.md
rejection_contract: v1
```

Ne pré-remplis pas artificiellement un gagnant sans résultats.

Le script de sélection peut écrire ce fichier après validation explicite ou générer une proposition que l’utilisateur choisit d’appliquer.

---

# 17. Scaffolder déterministe

Implémente un script central du type :

```text
create_skill_draft.py
```

Il lit l’architecture canonique et génère :

```text
<skill-name>/
├── SKILL.md
├── references/
├── assets/
└── scripts/
```

plus uniquement les fichiers réellement imposés par l’architecture canonique.

Le scaffold doit contenir les sections structurelles définitives et seulement des placeholders sémantiques.

Exemple conceptuel :

```text
<DESCRIPTION>
<DEFINITIONS>
<ACCEPT_RULES>
<REJECT_RULES>
<WORKFLOW_STEP_1>
...
```

L’agent n’est plus autorisé à réinventer :

```text
section topology
routing protocol
folder topology
workflow placement
```

---

# 18. Original specification provenance

Chaque skill créé par `create-skill` doit conserver sa spécification source.

Créer une ressource dédiée, de préférence :

```text
references/original-spec.md
```

si cela respecte les conventions existantes.

Elle doit enregistrer au minimum :

```text
raw/original user intent where appropriate
normalized accepted specification
important explicit constraints
resolved decisions made during create-skill
date/provenance if already part of repo conventions
```

Le but est que `optimize-skill` puisse optimiser le skill par rapport à la demande source et non uniquement par rapport aux affirmations actuelles du skill.

Cette ressource fait partie de la provenance du skill.

---

# 19. Validator structurel

Créer/refondre le validator de skill autour de l’architecture canonique.

Il doit vérifier notamment :

```text
valid frontmatter
canonical section topology
canonical routing structure
canonical workflow placement
required files
valid relative references
valid tool/file markers where applicable
no unresolved scaffold placeholders
original-spec exists
no forbidden scaffold mutation
```

La validation doit distinguer :

```text
STRUCTURAL ERROR
SEMANTIC WARNING
```

SkillOpt ne doit jamais pouvoir compenser une erreur structurelle par un meilleur score comportemental.

Toute violation structurelle doit invalider immédiatement un candidat.

---

# 20. Protection du scaffold pendant SkillOpt

Une fois l’architecture figée, SkillOpt optimise uniquement le contenu sémantique autorisé.

Il peut optimiser par exemple :

```text
wording
rules
examples
edge cases
workflow guidance
ordering inside mutable regions
semantic distinctions
```

Il ne peut pas modifier :

```text
frontmatter schema
routing topology
section topology
workflow placement
rejection JSON contract
required files
immutable markers
canonical scaffold
```

Implémente un contrôle déterministe.

Une possibilité :

```text
scaffold manifest
+
structural parser
+
candidate validator
```

Le validator s’exécute **avant** toute évaluation LLM coûteuse.

Si un candidat SkillOpt viole la structure :

```text
reject candidate immediately
do not pay for full Waza rollout
```

---

# 21. Adapter `create-skill`

Refondre `create-skill` pour suivre ce processus :

```text
explicit invocation
    ↓
read/understand request
    ↓
admission
    ↓
REJECT → structured result + routing
or
ACCEPT
    ↓
normalize specification
    ↓
persist original-spec
    ↓
run deterministic scaffolder
    ↓
fill mutable semantic regions
    ↓
generate necessary references/assets/scripts
    ↓
run structural validator
    ↓
final summary
```

Ne laisse plus `create-skill` inventer librement le package skeleton.

---

# 22. Nouveau skill `optimize-skill`

Créer :

```text
agentic-core/skills/optimize-skill/
```

Ce skill doit être explicitement user-invocable et, si supporté, non model-invocable.

Il doit utiliser `context: fork` car son workflow sera long.

Il ne doit PAS exister de skill séparé `create-skill-eval`.

La création du benchmark fait partie du workflow interne de `optimize-skill`.

---

# 23. Responsabilité de `optimize-skill`

Workflow conceptuel :

```text
1. Resolve target skill.
2. Read target SKILL.md.
3. Read target original-spec.
4. Validate canonical scaffold.
5. Check whether frozen benchmark already exists.
6. If absent, create benchmark adversarially.
7. Validate benchmark.
8. Freeze benchmark.
9. Run baseline S0.
10. Configure SkillOpt.
11. Optimize on train + selection.
12. Validate every candidate structurally.
13. Keep best candidate S*.
14. Run final holdout comparison.
15. Produce optimization report.
```

---

# 24. Création du benchmark : principe adversarial

Quand `optimize-skill` crée l’évaluation, sa mission n’est pas :

```text
prove that the skill works
```

mais :

```text
construct the strongest reasonable evaluation suite capable of falsifying the claim that this skill correctly satisfies its original specification
```

L’évaluation doit chercher :

```text
edge cases
near-miss inputs
ambiguous inputs
missing information
incorrect tool choices
wrong sequencing
partial task completion
unnecessary actions
forbidden mutations
over-eager behavior
under-specified behavior
failure recovery
cost explosions
```

Les tests doivent provenir :

```text
original-spec
+
actual skill
+
workspace/runtime constraints
```

Pas uniquement du texte du skill.

---

# 25. Suite Waza générée une seule fois

`optimize-skill` peut utiliser :

```text
waza new eval
```

comme scaffold initial si cela aide.

Mais ce scaffold générique n’est pas suffisant.

Le workflow doit l’enrichir en benchmark spécifique de task completion.

Créer une structure cohérente avec la version actuelle de Waza, par exemple conceptuellement :

```text
eval/
├── eval.yaml
├── train/
│   └── tasks...
├── selection/
│   └── tasks...
├── holdout/
│   └── one-complex-task...
├── graders/
└── fixtures/
```

Adapte les noms exacts au schéma supporté.

---

# 26. Benchmark immuable

Une fois généré et validé :

```text
FREEZE IT
```

Ne jamais régénérer ou modifier l’évaluation pendant la campagne SkillOpt.

Toutes les variantes :

```text
S0
S1
S2
...
S*
```

doivent être évaluées contre exactement les mêmes tâches, fixtures et graders.

Créer un lock/digest déterministe du benchmark.

Par exemple :

```text
benchmark.lock.json
```

avec SHA-256 des fichiers pertinents.

Avant et après chaque phase d’optimisation, vérifier que le digest est inchangé.

Toute modification du benchmark pendant l’optimisation doit faire échouer le run.

---

# 27. Splits

Utiliser trois surfaces logiques :

## train

Utilisé par SkillOpt pour :

```text
rollouts
trajectory analysis
reflection
candidate generation
```

## selection

Utilisé pour :

```text
validation gate
candidate accept/reject
```

## holdout

Jamais visible/utilisé pendant :

```text
routing ablation
SkillOpt training
candidate selection
```

Il sert uniquement à la comparaison finale.

---

# 28. Holdout

Le holdout peut volontairement contenir **une seule tâche très complexe**.

Il ne doit pas répéter mécaniquement toutes les petites métriques de train/selection.

Il doit tester un aspect intrinsèque et difficile de la mission du skill.

Le scénario doit idéalement combiner :

```text
realistic workspace
subtle edge cases
ambiguous evidence
multiple valid-looking paths
important constraints
potential failure modes
```

Il agit comme :

```text
final adversarial regression gate
```

et non comme estimateur statistique exhaustif.

---

# 29. Waza pour task completion

Utiliser les graders les plus déterministes possibles.

Priorité :

```text
program/code/file/diff assertions
        >
behavior/tool/action constraints
        >
LLM judge
```

Utiliser un LLM-as-a-judge seulement lorsque la qualité recherchée ne peut pas être vérifiée convenablement de façon déterministe.

Le benchmark doit mesurer :

```text
task completion
workflow adherence
artifact correctness
tool correctness
forbidden actions
efficiency where useful
```

---

# 30. Waza spec coverage

Après création du benchmark, utiliser les capacités de vérification disponibles, notamment :

```text
waza spec verify
```

si elles sont compatibles avec la version installée.

Le benchmark doit couvrir les promesses exécutables pertinentes du skill.

Ne considère pas le benchmark prêt tant que sa couverture n’est pas explicitement vérifiée.

---

# 31. Baseline S0

Avant toute optimisation :

```text
copy/freeze current target skill as S0
```

Exécuter le benchmark initial et sauvegarder :

```text
task results
hard scores
soft scores
tool traces
token usage
workspace artifacts/diffs
grader results
```

S0 ne doit plus changer.

---

# 32. Intégration SkillOpt

Créer une intégration custom pour ce type de benchmark.

SkillOpt doit recevoir :

```text
skill candidate
train tasks
selection tasks
scoring
```

Utiliser l’API/version réellement installée.

La documentation courante expose un `EnvAdapter` custom et des `RolloutResult` normalisés avec notamment :

```text
id
hard
soft
extras
```

Implémente un adapter propre au repository.

Ne duplique pas inutilement la définition du benchmark.

Idéalement :

```text
canonical eval tasks/graders
        ↓
Waza adapter
        ↓
SkillOpt adapter
```

Si la solution la plus fiable consiste à appeler Waza depuis l’adapter SkillOpt et parser son résultat, fais-le d’abord correctement.

L’optimisation de performance de cette intégration pourra venir plus tard.

---

# 33. Mapping du score SkillOpt

Ne réduis pas tout immédiatement à une moyenne arbitraire.

Utilise :

```text
hard
```

pour les conditions obligatoires :

```text
task completed
no forbidden structural mutation
no critical invariant violation
```

et :

```text
soft
```

pour les dimensions graduelles :

```text
quality
efficiency
token usage
unnecessary actions
behavior quality
```

Configurer le validation gate SkillOpt de façon cohérente avec cette séparation.

Le candidat ne doit pas être accepté s’il gagne en efficacité mais casse une contrainte hard.

---

# 34. Holdout et SkillOpt

SkillOpt ne doit PAS consulter le holdout pendant l’entraînement.

Si sa configuration possède une option du type :

```text
eval_test
```

qui lance automatiquement le test final, désactive-la pendant l’optimisation si cela exposerait le holdout.

Le holdout doit être exécuté explicitement après la sélection de `S*`.

---

# 35. SkillOpt structure protection

SkillOpt possède ses propres mécanismes de regions protégées pour certaines fonctionnalités internes.

Ne suppose pas que cela suffit à protéger notre scaffold.

Notre validator canonique reste la source de vérité structurelle.

Avant toute évaluation coûteuse d’un candidat :

```text
candidate
    ↓
structural validation
    ↓ fail
reject immediately
    ↓ pass
run benchmark
```

---

# 36. Comparaison finale

À la fin nous avons au minimum :

```text
S0 = skill initial post-scaffold / pre-SkillOpt
S* = best SkillOpt candidate
```

Prévoir optionnellement :

```text
S_system
```

si l’utilisateur souhaite comparer avec une implémentation système/builtin équivalente.

Les candidats doivent être exécutés :

```text
same task
same initial workspace
same model
same available tools
same configuration
```

---

# 37. Holdout comparison

Pour le holdout final :

1. créer un workspace initial canonique ;
2. cloner ce workspace pour chaque candidat ;
3. exécuter les candidats indépendamment ;
4. collecter :

   * final output ;
   * workspace diff ;
   * relevant tool trace ;
   * validation results ;
   * relevant artifacts ;
5. anonymiser les candidats ;
6. comparer les résultats.

Pour 2 candidats :

```text
A / B / tie
```

Pour 3 candidats, implémenter une stratégie pairwise/tournament claire sans exposer leur identité réelle au judge.

Ne révèle jamais :

```text
baseline
optimized
system
```

au juge.

---

# 38. LLM-as-a-judge holdout

Pour l’instant utiliser un LLM judge classique.

Ne pas intégrer Jev ou d’autres optimisations spécialisées maintenant.

Le judge doit recevoir :

```text
original specification
holdout task
hard invariants
candidate A evidence
candidate B evidence
explicit rubric
```

La rubrique doit privilégier :

```text
requirement fidelity
correct task completion
workflow correctness
artifact quality
absence of harmful/unnecessary actions
efficiency as secondary criterion
```

Retour :

```text
A
B
TIE
```

plus justification structurée.

---

# 39. `optimize-skill` doit produire un rapport final

Créer un artifact/report contenant au minimum :

```text
target skill
original spec reference
benchmark digest
baseline S0 metrics
SkillOpt configuration
number of optimization iterations
accepted/rejected candidate history
best candidate S*
selection metrics
token deltas
holdout comparison
structural validation status
paths to artifacts/results
```

Ne remplace pas silencieusement le skill original.

Par défaut, produire le candidat optimisé séparément ou demander une adoption explicite au niveau où le workflow actuel du repository le permet.

---

# 40. Dépenses en tokens

Les defaults doivent refléter deux régimes différents.

## Routing ablation

Peu coûteuse :

```text
trials > 1 encouraged
```

car le workflow réel est stoppé au sentinel.

## SkillOpt / task-completion

Très coûteux :

```text
trials = 1 by default
```

sauf configuration explicite contraire.

Ne multiplie pas implicitement les rollouts coûteux.

---

# 41. Tests déterministes à écrire

Avant toute expérimentation LLM, ajouter des tests locaux pour :

```text
semantic manifest rendering
architecture variant rendering
routing sentinel insertion
routing sentinel removal for production scaffold
routing result parsing
metric aggregation
benchmark lock hashing
benchmark mutation detection
scaffold generation
scaffold validation
original-spec persistence
SkillOpt candidate structural rejection
S0/S* workspace cloning
result normalization
```

Ces tests ne doivent nécessiter aucun appel modèle.

---

# 42. Scripts/entrypoints attendus

Adapte les noms aux conventions du repository, mais l’utilisateur doit disposer d’équivalents à :

```text
run_routing_ablation
analyze_routing_ablation
select_canonical_architecture
create_skill_draft
validate_skill
freeze_skill_benchmark
verify_skill_benchmark
run_skill_baseline
run_skillopt
compare_skill_holdout
```

Évite un monolithe Python unique.

Chaque module doit avoir une responsabilité claire.

---

# 43. Résultats Phase 0

Sauvegarder les résultats de manière reproductible.

Exemple conceptuel :

```text
experiments/
└── routing/
    ├── specs/
    ├── architectures/
    ├── runs/
    │   └── <timestamp-or-run-id>/
    │       ├── config.yaml
    │       ├── raw/
    │       ├── metrics.json
    │       └── report.md
    └── canonical-architecture.yaml
```

Ne stocke pas les workspaces temporaires volumineux sauf en mode debug.

---

# 44. Reproductibilité

Chaque run doit enregistrer :

```text
Waza version
SkillOpt version where relevant
VS Code/Copilot assumptions
model id
trials
seed if available
candidate architecture id
skill spec id
benchmark digest
configuration
```

Si la stochasticité du backend ne permet pas un seed effectif, l’indiquer explicitement.

---

# 45. Ne pas sur-engineerer avant les résultats

Implémente l’infrastructure permettant de comparer les architectures.

Ne décide pas à l’avance que :

```text
deferred workflow
```

ou :

```text
ACCEPT/REJECT lists
```

est nécessairement gagnant.

L’expérience doit pouvoir falsifier nos hypothèses.

---

# 46. Invariant central de Phase 0

Le harness doit être capable de répondre précisément à :

```text
Did the model:

1. discover the correct skill?
2. invoke it?
3. accept or reject correctly?
4. route a rejection correctly?
5. cross the workflow boundary?
6. cross it when it should NOT have?
7. how many tokens were consumed before this decision?
```

Il ne doit PAS répondre à :

```text
Did the actual workflow solve the business task?
```

Cette question appartient à `optimize-skill`.

---

# 47. Invariant central de `optimize-skill`

Le workflow doit être :

```text
target skill + original spec
        ↓
create adversarial benchmark ONCE
        ↓
validate benchmark
        ↓
freeze benchmark
        ↓
baseline S0
        ↓
SkillOpt train/selection
        ↓
S*
        ↓
single final holdout
```

À aucun moment :

```text
SkillOpt candidate
        ↓
regenerate benchmark
```

ne doit être possible.

---

# 48. Mise à jour de la documentation interne

Documente clairement dans le repository :

```text
why Waza is used
why SkillOpt is used
why routing and task completion are optimized separately
why the benchmark is frozen
why the sentinel exists
why routing ablation allows multiple trials
why SkillOpt defaults to one expensive trial
why structure is immutable during semantic optimization
```

Cette documentation doit être concise mais suffisamment précise pour qu’un futur agent ne “simplifie” pas accidentellement l’architecture.

---

# 49. Migration de l’existant

Inspecte le `create-skill` actuel avant de modifier quoi que ce soit.

Réutilise :

```text
existing validator logic
existing templates
existing definitions
existing Waza-related files if any
existing package conventions
existing Python environment / uv setup
```

Supprime ou refactorise uniquement les éléments devenus redondants.

Ne duplique pas les sources de vérité.

---

# 50. Ordre d’implémentation

Implémente dans cet ordre :

```text
A. inspect repository + current create-skill
B. verify Waza/SkillOpt current interfaces
C. implement routing-ablation manifests/renderers
D. implement workflow-entry sentinel harness
E. implement Waza routing eval generation/execution
F. implement metrics + reports
G. implement canonical architecture selection/config
H. implement deterministic scaffolder
I. refactor structural validator
J. persist original-spec from create-skill
K. refactor create-skill to use scaffolder
L. create optimize-skill
M. implement adversarial Waza benchmark generation
N. implement benchmark freeze/lock
O. implement baseline S0 runner
P. implement SkillOpt benchmark adapter
Q. implement structural gate for candidates
R. implement train/selection optimization
S. implement holdout comparison
T. add deterministic tests
U. run local non-LLM tests and validators
V. produce documentation + exact commands for user
```

---

# 51. Definition of Done

Le travail n’est terminé que si :

1. les architectures de routing peuvent être comparées sans exécuter les vrais workflows ;
2. le sentinel donne un signal observable de workflow-entry ;
3. plusieurs trials de routing sont configurables ;
4. les 5 mêmes semantic specs sont utilisées pour toutes les architectures ;
5. un rapport permet de sélectionner une architecture canonique ;
6. un skill scaffold peut être généré déterministiquement depuis cette architecture ;
7. `create-skill` utilise ce scaffold ;
8. chaque skill créé conserve son `original-spec`;
9. `optimize-skill` est user-invocable et orchestre tout le pipeline ;
10. `optimize-skill` crée une suite Waza adversariale une seule fois ;
11. cette suite est gelée et hashée ;
12. SkillOpt utilise `train` et `selection` sans accéder au holdout ;
13. chaque candidat SkillOpt est structurellement validé avant les rollouts coûteux ;
14. S0 est conservé ;
15. S* est produit séparément ;
16. le holdout compare S0/S* de manière anonymisée ;
17. aucun benchmark n’est régénéré pendant l’optimisation ;
18. les tests déterministes passent ;
19. les commandes exactes pour lancer Phase 0 puis `/optimize-skill` sont documentées ;
20. aucune expérience LLM coûteuse n’est lancée automatiquement pendant cette implémentation.

À la fin, donne-moi :

* les fichiers créés/modifiés ;
* l’architecture implémentée ;
* les éventuels écarts imposés par les API réellement disponibles de Waza/SkillOpt ;
* les commandes exactes pour :

  1. lancer la Phase 0A ;
  2. analyser/sélectionner l’architecture ;
  3. lancer Phase 0B ;
  4. figer l’architecture canonique ;
  5. créer un skill avec le nouveau `create-skill` ;
  6. lancer `optimize-skill` sur ce skill ;
  7. inspecter les résultats Waza ;
  8. inspecter les résultats SkillOpt ;
  9. exécuter le holdout final.

N’émets pas simplement un plan : implémente effectivement tout ce qui peut l’être sans lancer les rollouts LLM coûteux.
