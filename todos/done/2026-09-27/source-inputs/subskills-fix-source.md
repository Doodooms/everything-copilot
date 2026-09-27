# Source clarification for TASK-5-03A

> **Clarification from the user, 2026-09-27:** Keep domain `SKILL.md` files as the 11 discoverable expertise boundaries, with subdomain expertise subskills nested under each `workflows/`. Each nested subskill must use the canonical skill body structure (`critical_rules`, `general_rules`, `risk_assessment`, `rules`, `workflow`) while remaining workflow metadata/content inside the parent package. This supersedes passages below that call for a much lighter body or omission of those skill sections; it does not authorize peer `SKILL.md` packages or flat global routing.

> Status: preserved source input; implementation and acceptance state are tracked in `../agentic-core-normalization-report.md`, `docs/planner-history/task_5/plan-r10.md`, and `../../../backlog/2026-09-27/agentic-core-normalization-review-gates.md`. This source is not evidence that independent QA or Reviewer accepted the work.

Oui, la direction me paraît nettement meilleure que le catalogue plat de skills. Mais ces exemples montrent aussi exactement où il faut arrêter la récursion.

Le parent `operations` est proche de ce que je viserais : il expose un domaine cohérent, quelques principes communs, puis route vers seulement quatre procédures spécialisées (`delivery-operations`, `verification-loop`, `install-agent-plugin`, `documentation-sync`).  C’est bien le modèle :

```text
Agent
  ↓
operations
  ↓
workflow spécialisé
  ↓
references/assets
```

En revanche, tes `workflow_name.md` ajoutent actuellement un étage supplémentaire. Par exemple `delivery-operations.md` ne contient quasiment pas la méthode : il valide son admission puis charge `../references/delivery-operations/method-source.md` comme « internal subskill ».  Même structure pour `documentation-sync`.

Conceptuellement tu as donc réellement :

```text
operations/SKILL.md
    ↓
workflows/delivery-operations.md
    ↓
references/delivery-operations/method-source.md
    ↓
support files éventuels
```

alors que ton intention était :

```text
operations/SKILL.md
    ↓
workflows/delivery-operations.md   ← le vrai sous-skill
    ↓
references/assets
```

Je choisirais clairement la deuxième.

## Le workflow doit être le sous-skill

Je ferais de `delivery-operations.md` lui-même l’unité d’expertise spécialisée :

```yaml
---
id: delivery-operations
description: >
  Apply safe delivery and runtime changes in an existing environment.
invoke_for:
  - approved CI/CD changes
  - packaging
  - deployment configuration
  - release automation
  - observability
avoid_for:
  - product implementation
  - architecture decisions
references:
  - ../references/delivery-operations/rollback.md
  - ../references/delivery-operations/deployment-safety.md
---

# Procedure

## 1. Establish operational state
...

## 2. Select the smallest reversible mutation
...

## 3. Validate
...

## 4. Produce operational evidence
...
```

Les références deviennent alors de vraies références :

```text
rollback.md
kubernetes.md
github-actions.md
deployment-safety.md
observability.md
```

c’est-à-dire de la **connaissance chargée lorsque le workflow en a besoin**, et non une autre procédure cachée.

Autrement dit :

> si `method-source.md` contient le comportement que le modèle doit suivre, son contenu appartient au workflow.

Si `method-source.md` contient des connaissances, exemples, heuristiques ou tables détaillées, alors il appartient bien aux références.

Je supprimerais donc probablement le champ :

```yaml
subskills:
  - ../references/.../method-source.md
```

au niveau des workflows.

Il brouille ta taxonomie.

---

## Tu as aussi une double admission inutile

Le parent `operations` demande déjà :

> assess risk and select only a matching workflow.

Puis chaque workflow recommence :

> assess the task risk and confirm `invoke_for` / `avoid_for`.

Ça donne :

```text
Agent
→ evaluate skill admission

operations
→ evaluate workflow admission + risk

verification-loop
→ evaluate workflow admission + risk AGAIN
```

Je réduirais à :

```text
Agent
→ Does this broad skill apply?

Skill
→ Which workflow(s) apply?

Workflow
→ execute procedure
```

Le workflow peut conserver une garde légère :

```text
If the supplied task no longer satisfies this workflow's
preconditions, return a routing mismatch.
```

mais il ne doit pas refaire toute la classification.

Et comme on en parlait juste avant, **le risk level devrait idéalement être fourni par l'Orchestrator**, puis seulement escaladé si une nouvelle preuve l'exige. Le parent `operations` répète encore actuellement tout le modèle L0–L3.

À terme :

```text
handoff.risk = L2

Agent:
consume L2

Skill:
adapt procedure to L2

Workflow:
execute under L2 obligations
```

pas trois estimations indépendantes.

---

# Tes workflows sont suffisamment légers pour devenir d'excellents « headers de spécialité »

Les metadata sont en revanche très utiles :

```yaml
id:
description:
invoke_for:
avoid_for:
references:
```

Je les garderais.

Par exemple `verification-loop` distingue déjà très proprement son domaine de TDD : il sert à valider build/types/lint/tests/security/readiness, et exclut explicitement l'implémentation ainsi que RED-GREEN-REFACTOR.

C'est exactement ce dont aura besoin ton futur router :

```text
Task state
+
workflow metadata
        ↓
LLM now
DecisionEngine/Jev later
        ↓
verification-loop
```

Donc je séparerais :

```text
WORKFLOW METADATA
= routing surface

WORKFLOW BODY
= procedure

REFERENCES
= knowledge
```

Cette séparation est très propre.

---

# Je vois cependant un autre problème intéressant : tous les sous-skills ne méritent probablement pas ce statut

Dans ton second groupe, j'ai :

```text
commit-message
implementation-planning
orchestrate
resolving-merge-conflicts
spec-driven-development
```

Je ne vois pas dans les fichiers reçus le `SKILL.md` parent correspondant à ce second package, mais ces fichiers semblent clairement former ton domaine `orchestration`.

Et là je ferais déjà un petit audit de granularité.

`implementation-planning` est clairement une méthode substantielle : decomposition en phases, ownership, scope, sequencing et validation.

`spec-driven-development` aussi : son admission couvre features non triviales, changements comportementaux matériels, migrations, APIs et cross-agent drift.

`orchestrate` également : multi-agent delivery + traceable handoffs.

`resolving-merge-conflicts` a également une véritable procédure spécialisée, avec une frontière nette entre résolution du contenu et Git lifecycle.

Mais `commit-message` me paraît beaucoup plus douteux comme workflow de premier rang. Il sert uniquement à finaliser un message depuis un diff déjà validé.

Il pourrait probablement devenir :

```text
orchestration/
  references/
    commit-message.md
```

ou même une petite capability déterministe/prompt utility.

Pourquoi ? Parce qu'il ne constitue pas vraiment un nouveau **mode de raisonnement spécialisé**.

C'est un bon critère général :

> Un workflow mérite d'exister lorsqu'il modifie réellement la procédure cognitive à suivre, pas simplement parce qu'une ancienne skill doit trouver une nouvelle maison.

C'est important pendant ta migration : **ne transforme pas mécaniquement chaque ancienne skill en workflow**.

---

# Je garderais donc une taxonomie très stricte

Pour moi, ton architecture devrait maintenant être :

```text
Agent Plugin
│
├── Agent
│
│   └── knows 2–4 broad Skills
│
├── Skill
│   │
│   ├── SKILL.md
│   │    ├── domain purpose
│   │    ├── shared principles
│   │    └── workflow routing
│   │
│   ├── workflows/
│   │    ├── foo.md       ← actual subskill
│   │    ├── bar.md
│   │    └── baz.md
│   │
│   ├── references/
│   │    ├── concepts.md
│   │    ├── heuristics.md
│   │    └── examples.md
│   │
│   └── assets/
│
└── MCP
```

Avec exactement trois niveaux cognitifs :

```text
Skill
= What subdomain am I entering?

Workflow
= What specialized procedure should I use?

Reference
= What additional knowledge does that procedure need?
```

Et **pas** :

```text
Skill
→ Workflow
→ Internal subskill
→ Reference
```

---

## Je modifierais également légèrement le parent `SKILL.md`

Actuellement `operations` dit essentiellement :

```text
common rules
→ select workflow
→ apply operation
→ return evidence
```

C'est déjà bon.

Mais je lui donnerais une petite **ontology du domaine**, afin qu'il aide effectivement le modèle avant même le routing :

```text
Operational mutation
≠ product implementation

hosting/configuration
≠ server implementation

verification
≠ implementation

observed deployment state
≠ assumed deployment state

documentation truth
must follow verified behavior
```

Tu as déjà commencé avec :

> configuration/hosting is distinct from MCP server implementation code.

J'en mettrais quelques-uns comme ça, très peu.

Cela fait du parent une véritable **interface cognitive du domaine**, et pas seulement un index de fichiers.

---

# Je pense que ton modèle final est même plus propre que « skill contenant plusieurs skills »

Je changerais légèrement la formulation mentale.

Pas :

```text
Skill
contains hidden Skills
```

mais :

```text
Skill
= subdomain expertise boundary

Workflow
= procedural specialization of that expertise
```

Parce que sinon tu vas être tenté de faire hériter aux workflows de toute la complexité d'un `SKILL.md` :

```text
full routing
full rules
full definitions
full risk
full output contract
...
```

et tu reconstruiras exactement ton ancien système un niveau plus bas.

Le workflow doit être **beaucoup plus léger qu'une ancienne skill** parce que beaucoup de choses sont déjà établies :

```text
agent ownership known
domain known
risk known
broad admission known
authority known
```

Il ne reste qu'à fournir la méthode spécialisée.

C'est là que tu vas réellement gagner en tokens.

---

## Donc mon verdict sur cette refonte

La hiérarchie est bonne. Le `operations/SKILL.md` est déjà un bon exemple de ce que doit devenir ton niveau high-level. Mais tes workflows ressemblent encore trop à des **adaptateurs de compatibilité vers les anciennes skills**, plutôt qu'à leur forme finale.

Je ferais cette dernière migration :

```text
OLD

SKILL.md
   ↓
workflow.md
   ↓
method-source.md   ← old skill copied here
   ↓
support references


TARGET

SKILL.md
   ↓
workflow.md        ← distilled actual procedure
   ↓
references         ← only deep knowledge/examples/support
```

Et lors de la migration de chaque ancienne skill, je poserais trois questions :

```text
Does it represent a distinct subdomain?
→ top-level Skill

Does it represent a distinct procedure inside a known subdomain?
→ Workflow

Is it mostly knowledge, rules, examples or implementation detail?
→ Reference

Is it trivial/deterministic enough not to require a reasoning method?
→ Tool / utility / remove
```

C'est à ce stade que ta nouvelle architecture peut réellement commencer à **réduire** le coût contextuel au lieu de simplement cacher le même volume de texte derrière davantage de fichiers.

Tu travailles dans `agentic-workflow`.

La refonte actuelle des skills introduit cette hiérarchie :

```text
Agent
→ high-level Skill
→ Workflow
→ References / Assets / Tools
```

Les high-level skills représentent un sous-domaine d'expertise discoverable par le harness.

Les fichiers `workflows/*.md` représentent les procédures spécialisées internes à ce domaine et jouent conceptuellement le rôle de **subskills non exposées au runtime global**.

Je veux maintenant corriger deux défauts apparus pendant la migration des anciennes skills.

# 1. Supprimer le niveau artificiel `workflow → method-source`

La structure actuelle ressemble souvent à :

```text
SKILL.md
→ workflows/foo.md
→ references/foo/method-source.md
→ support files
```

`workflows/foo.md` ne contient alors pratiquement que :

```text
confirm admission
→ load method-source.md
→ follow it
```

C'est un niveau de progressive disclosure inutile.

La structure cible est :

```text
SKILL.md
→ workflows/foo.md
→ references / assets / tools
```

Le fichier :

```text
workflows/foo.md
```

DOIT devenir lui-même la véritable procédure spécialisée.

Autrement dit :

```text
Workflow
= actual specialized procedure

Reference
= supporting knowledge
```

et non :

```text
Workflow
= wrapper around another hidden procedure
```

## Migration

Pour chaque workflow actuellement associé à :

```text
references/<workflow>/method-source.md
```

inspecte le contenu de `method-source.md`.

Déplace/distille dans `workflows/<workflow>.md` tout ce qui constitue :

```text
procedure
decision process
ordered steps
method-specific rules
method-specific execution logic
```

Conserve sous `references/` uniquement ce qui constitue réellement :

```text
deep knowledge
background concepts
heuristics
examples
tables
framework-specific guidance
supporting material
```

Supprime ensuite l'indirection `method-source.md` lorsqu'elle n'a plus de raison d'exister.

Ne conserve PAS artificiellement une ancienne skill entière comme reference uniquement pour faciliter la migration.

## Workflow format cible

Un workflow doit approximativement avoir :

```yaml
---
id: foo
description: >
  Concise semantic description of the specialized procedure.

invoke_for:
  - ...

avoid_for:
  - ...

references:
  - ../references/...
---
```

puis directement :

```markdown
# Procedure

## Step 1
...

## Step 2
...

## Step 3
...
```

Les metadata servent au routing.

Le body contient la méthode.

Les references apportent uniquement du contexte spécialisé supplémentaire.

Supprimer le champ `subskills` s'il ne sert qu'à pointer vers `method-source.md`.

# 2. Supprimer la double admission et la double évaluation du risque

La responsabilité de routing doit être hiérarchique :

```text
Agent
→ selects broad Skill

Skill
→ selects specialized Workflow

Workflow
→ executes
```

Le workflow ne doit pas refaire entièrement le travail de routing déjà effectué par son parent.

Actuellement, plusieurs workflows commencent conceptuellement par :

```text
assess risk
confirm invoke_for
confirm avoid_for
route elsewhere if needed
```

alors que le parent `SKILL.md` a déjà :

```text
assessed the domain
selected the workflow
```

Cela crée :

```text
duplicated reasoning
duplicated tokens
possible routing disagreement
unnecessary ceremony
```

## Nouvelle responsabilité

### Agent

Décide :

```text
Does this broad expertise domain apply?
```

### Parent `SKILL.md`

Décide :

```text
Which workflow(s) inside this domain apply?
```

en utilisant les metadata :

```text
description
invoke_for
avoid_for
```

### Workflow

Suppose que son admission a déjà été résolue et exécute directement sa procédure.

Il peut conserver uniquement une garde minimale du type :

```text
If newly discovered evidence makes this procedure materially
inapplicable, stop and return a routing mismatch.
```

Il ne doit PAS refaire systématiquement toute l'admission.

# 3. Risk ownership

Ne fais plus recalculer indépendamment le même niveau de risque à chaque couche.

Le niveau de risque doit normalement être fourni par le workflow agentique / Orchestrator :

```text
risk_level: L0 | L1 | L2 | L3
```

Le spécialiste et ses skills :

```text
consume the assigned risk
adapt evidence/verification depth accordingly
MUST NOT downgrade it
MAY escalate when new evidence reveals higher risk
```

Ils ne doivent pas recommencer systématiquement une classification complète.

Donc retirer des workflows spécialisés les étapes génériques du type :

```text
Assess task risk...
```

lorsqu'elles répètent simplement la policy déjà établie.

Le parent skill peut lui aussi être simplifié si le risque lui est déjà transmis.

# 4. Preserve workflow metadata

IMPORTANT : conserver les metadata :

```text
id
description
invoke_for
avoid_for
references
```

Elles sont utiles pour :

```text
LLM workflow routing
static validation
future DecisionEngine/Jev routing
evals
documentation
```

Mais :

```text
metadata
≠ execution ceremony
```

Elles décrivent l'admission ; elles ne nécessitent pas que le workflow la recalcule après avoir été sélectionné.

# 5. Progressive disclosure invariant

La profondeur cognitive maximale cible devient :

```text
Agent
→ Skill
→ Workflow
→ Reference / Asset / Tool
```

MUST NOT reconstruire :

```text
Agent
→ Skill
→ Workflow
→ internal subskill
→ method source
→ reference
```

Le système doit avoir seulement deux décisions sémantiques principales :

```text
Which Skill?
Which Workflow?
```

Après cela, il s'agit essentiellement de retrieval ciblé.

# 6. Important distinction during migration

Ne transforme pas mécaniquement chaque ancienne skill en workflow.

Pour chaque ancien artefact, déterminer :

```text
Distinct expertise subdomain
→ top-level Skill

Distinct procedure within an existing subdomain
→ Workflow

Mostly knowledge / heuristics / examples
→ Reference

Simple deterministic or trivial operation
→ Tool / utility / remove
```

Le but n'est PAS de cacher l'ancien catalogue un niveau plus bas.

Le but est réellement de réduire la complexité cognitive et contextuelle.

# 7. Apply to current packages

Commence par les packages actuellement refondus, notamment les domaines contenant des workflows tels que :

```text
operations:
- delivery-operations
- verification-loop
- install-agent-plugin
- documentation-sync

orchestration:
- orchestrate
- spec-driven-development
- implementation-planning
- resolving-merge-conflicts
- commit-message
```

Pour chaque workflow :

1. inspecter son ancien `method-source.md`;
2. identifier la véritable procédure;
3. l'intégrer directement dans `workflows/<name>.md`;
4. extraire seulement les connaissances profondes en references;
5. supprimer les wrappers inutiles;
6. supprimer les répétitions d'admission/risk assessment;
7. vérifier que le parent Skill reste responsable du workflow routing.

Audite aussi si chaque workflow mérite réellement ce niveau.

Par exemple, un artefact très léger tel que `commit-message` ne doit pas automatiquement rester un workflow simplement parce qu'il était auparavant une skill.

Si sa procédure cognitive est trop faible, proposer une meilleure classification.

# 8. Context-efficiency objective

Cette refonte doit réduire le coût réel d'un chemin typique :

```text
Agent metadata
→ one Skill
→ one Workflow
→ only necessary References
```

Évite toute structure qui oblige à charger successivement plusieurs wrappers avant d'atteindre la véritable expertise.

Principe :

> Every progressive-disclosure layer must add meaningful information needed for the next decision.

Si un fichier ne fait que dire :

```text
load the next file
```

il est probablement inutile.

# 9. Preserve ownership

Cette refonte ne change PAS :

```text
Agent responsibilities
Skill domain ownership
Orchestrator authority
specialist boundaries
acceptance ownership
```

Elle ne concerne que la structure interne et le coût du progressive disclosure.

# 10. Validation

Après migration, vérifier :

```text
SKILL.md can route reliably to workflows

workflow metadata remains statically readable

workflow contains the actual specialized method

references contain only supporting knowledge

no method-source wrapper remains without a concrete justification

workflow does not duplicate parent routing

risk is consumed rather than redundantly recomputed

relative references resolve correctly

no old procedure was accidentally lost
```

Comparer également le nombre de fichiers/tokens nécessaires pour atteindre la méthode effective avant et après migration.

# Final target

```text
High-Level Skill
│
├── shared domain principles
├── workflow routing
│
├── workflows/
│   ├── procedure-a.md
│   ├── procedure-b.md
│   └── procedure-c.md
│
├── references/
│   ├── deep-knowledge-a.md
│   └── framework-specific-guidance.md
│
└── assets/
```

Fundamental rules:

> The workflow is the subskill.

> A reference is knowledge, not another hidden procedural layer.

> Admission belongs to the parent skill; execution belongs to the selected workflow.

> Risk should be inherited and escalated when necessary, not repeatedly recomputed.

> Progressive disclosure should reduce attention complexity, not merely move the same complexity into deeper directories.
