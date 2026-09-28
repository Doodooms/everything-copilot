# Mission

Tu travailles dans le repository `agentic-workflow`.

Les Agent Plugins `ML-Eng`, `PythonDev`, `Vision-Eng` et `Inference-Eng` sont déjà en cours d’implémentation ou existent partiellement.

NE les recommence PAS depuis zéro.

Commence par inspecter :

```text
repository actuel
agents canoniques
skills canoniques
Agent Plugins existants
scripts/validators existants
conventions du repository
architecture actuelle de génération/install
```

Puis implémente la nouvelle architecture décrite ci-dessous avec le minimum de duplication et de breaking changes.

---

# 1. Architecture cible

Le système doit désormais distinguer strictement :

```text
AGENTIC-CORE
= Agent Plugin bootstrap standard, installable et utilisable seul

EXPERTISE PACK
= Agent Plugin source apportant expertise, skills, MCP tools
  et éventuellement de nouveaux agents

PLUGIN STORE
= stockage privé des Expertise Packs gérés par agentic-workflow

ACTIVE SET
= plugins sélectionnés pour un workspace

EFFECTIVE IR
= composition résolue du core + plugins actifs + host capabilities

EFFECTIVE PROFILE
= Agent Plugin généré pour le harness courant à partir de l'Effective IR

WORKSPACE CUSTOMIZATIONS
= agents, skills et instructions réellement spécifiques au projet
```

Invariant principal :

> `agentic-core` et les Expertise Packs sont des sources immuables.
> L’Effective Profile est un artefact dérivé, jetable et entièrement reproductible.

---

# 2. `agentic-core` devient un Agent Plugin autonome

`agentic-core` doit être un Agent Plugin standard qui fonctionne immédiatement après son installation.

Sur une machine/projet vierge :

```text
install agentic-core
        ↓
plugin activated
        ↓
Orchestrator available
Architect
Planner
Researcher
Implementer
Quality Assurance
Reviewer
Challenger
DevOps
        ↓
canonical skills available
        ↓
plugin-management capability available
```

Aucune compilation supplémentaire ne doit être nécessaire pour utiliser le workflow canonique seul.

Le plugin doit donc contenir directement :

```text
agentic-core/
├── plugin.json
├── skills/
│   ├── orchestrate/
│   ├── spec-driven-development/
│   ├── install-agent-plugin/
│   └── ...
│
├── mcp.json                     # si nécessaire
│
├── runtime/
│   └── pluginctl/               # ou emplacement équivalent
│
└── com.github.copilot/
    └── agents/
        ├── orchestrator.agent.md
        ├── architect.agent.md
        ├── planner.agent.md
        ├── researcher.agent.md
        ├── implementer.agent.md
        ├── quality-assurance.agent.md
        ├── reviewer.agent.md
        ├── challenger.agent.md
        └── devops.agent.md
```

Adapter les chemins aux conventions réelles du repository.

---

# 3. Ne PAS mettre le compiler dans `install-agent-plugin`

Respecter :

```text
install-agent-plugin
= SKILL

pluginctl
= deterministic implementation
```

La skill décrit :

```text
quand une expertise supplémentaire est nécessaire
quand installer un plugin
trust policy
capability resolution
activation workflow
failure/rollback behavior
```

Elle ne contient PAS le moteur de compilation.

`pluginctl` appartient à l’infrastructure de `agentic-core`.

Conceptuellement :

```text
install-agent-plugin
        ↓
plugin.* tools / pluginctl
        ↓
resolver
compiler
validator
materializer
```

---

# 4. Les Expertise Packs restent des Agent Plugins valides

Exemples :

```text
ML-Eng
PythonDev
Vision-Eng
Inference-Eng
RustDev
...
```

Chaque pack doit rester utilisable comme Agent Plugin autonome lorsqu’un utilisateur l’installe directement.

Mais lorsqu’il est géré par `agentic-workflow`, il devient avant tout un **package source**.

Exemple :

```text
ml-eng/
├── plugin.json
├── skills/
├── mcp.json
├── com.github.copilot/
│   └── agents/
└── com.doodooms.agentic-workflow/
    └── integration.yaml
```

---

# 5. Mode standalone vs managed

Supporter deux modes conceptuels.

## Standalone

Un utilisateur installe directement :

```text
PythonDev
```

Le harness expose normalement les composants du plugin.

## Managed

L’utilisateur possède :

```text
agentic-core
```

`pluginctl` télécharge PythonDev dans son propre store :

```text
Plugin Store
```

mais NE l’enregistre PAS comme plugin actif du harness.

Il le traite comme une source à composer.

C’est obligatoire pour éviter :

```text
PythonDev source plugin visible
+
PythonDev intégré dans Effective Profile
```

et donc une duplication de contexte.

---

# 6. Plugin Store privé

Créer un store privé approprié au système.

Conceptuellement :

```text
~/.agentic-workflow/
├── packs/
│   ├── ml-eng/
│   │   └── <version>/
│   ├── python-dev/
│   └── ...
│
├── profiles/
├── cache/
└── state/
```

Ou utiliser un emplacement client-managed équivalent si le runtime actuel en fournit un approprié.

Ne PAS copier les Expertise Packs gérés dans :

```text
.github/skills
.github/agents
```

du projet.

---

# 7. Les quatre états d’un plugin

Formaliser :

```text
AVAILABLE
↓
INSTALLED
↓
ACTIVE
↓
MATERIALIZED
```

## AVAILABLE

Présent dans le trusted registry.

## INSTALLED

Package validé dans le private plugin store.

Il n’est PAS encore exposé au harness.

## ACTIVE

Sélectionné pour le workspace courant.

Il participe à la résolution de l’Effective IR.

## MATERIALIZED

Ses contributions sont présentes dans l’Effective Profile du harness courant.

Ces états doivent être explicitement représentables et inspectables.

---

# 8. Le core ne doit jamais être patché

MUST NOT modifier les sources canoniques de `agentic-core` pendant :

```text
plugin install
plugin activate
plugin deactivate
plugin upgrade
plugin uninstall
profile materialization
```

Les Expertise Packs MUST NOT modifier directement :

```text
Role
Responsibilities
Constraints
Definitions
Routing
Workflow
Output Contract
```

des agents canoniques.

Après la migration plugin-aware initiale, leurs responsabilités deviennent stables.

---

# 9. Workspace réservé au project-specific

Préserver la distinction :

```text
Agent Plugins
= generic reusable expertise

Workspace
= project-specific customization
```

Le workspace peut continuer à contenir :

```text
.github/agents/
.github/skills/
instructions/
```

mais uniquement pour des éléments réellement project-specific.

Exemples acceptables :

```text
factory-image-conventions
internal-dataset-ingestion
product-data-specialist
internal-release-agent
```

NE PAS y générer une copie des agents canoniques.

NE PAS y générer une copie des Expertise Packs.

---

# 10. Configuration workspace

Créer une configuration légère, par exemple :

```text
.agentic/profile.yaml
.agentic/profile.lock
```

ou réutiliser une abstraction existante.

Exemple :

```yaml
capabilities:
  - python.development
  - ml
  - ml.vision
```

Préférer la déclaration de capabilities plutôt que la déclaration directe de plugins lorsque possible.

Le resolver produit ensuite :

```text
python.development
→ PythonDev

ml
→ ML-Eng

ml.vision
→ Vision-Eng
```

---

# 11. Default profile

Si aucune configuration workspace n’existe :

```text
agentic-core only
```

est le comportement par défaut.

Donc ouvrir n’importe quel repository après installation de `agentic-core` doit continuer à fournir immédiatement le workflow canonique.

---

# 12. Effective IR

Créer une représentation intermédiaire indépendante du harness :

```text
Effective IR
```

Elle contient au minimum :

```text
agents
agent ownership
agent allowlists
skills
skill projections
semantic capabilities
resolved tools
tool projections
plugin provenance
plugin dependencies
host requirements
workspace registered agents
```

Ne PAS faire du `.agent.md` Copilot l’IR interne.

---

# 13. Compilation

La configuration effective doit être une fonction déterministe :

```text
EffectiveIR =
    resolve(
        AgenticCoreVersion,
        ActivePluginSet,
        PluginVersions,
        WorkspaceExtensions,
        HostCapabilities
    )
```

Puis :

```text
EffectiveProfile =
    materialize(
        EffectiveIR,
        TargetHarness
    )
```

L’ordre d’installation ne doit jamais modifier le résultat.

---

# 14. Effective Profile

Pour les harnesses ne supportant pas encore la composition runtime nécessaire, générer un **Effective Profile Agent Plugin**.

Conceptuellement :

```text
~/.agentic-workflow/profiles/<profile-hash>/
├── plugin.json
├── skills/
├── mcp.json
└── com.github.copilot/
    └── agents/
```

Ce profile contient :

```text
full agentic-core runtime surface
+
active expertise contributions
+
contributed agents
+
resolved tools
+
plugin-management/bootstrap capabilities
```

Il doit donc toujours conserver :

```text
orchestrator
install-agent-plugin
pluginctl access
```

afin de pouvoir continuer à gérer les plugins.

---

# 15. Aucun doublon runtime

C’est un invariant critique.

Il ne doit JAMAIS y avoir simultanément dans le même workspace :

```text
agentic-core active
+
Effective Profile containing agentic-core
```

ou :

```text
ML-Eng source active
+
Effective Profile containing ML-Eng
```

La surface runtime doit être exactement l’une des suivantes :

## Core-only mode

```text
agentic-core ENABLED
no Effective Profile
```

## Managed-profile mode

```text
agentic-core source DISABLED for workspace
Expertise Pack sources DISABLED/not host-registered
Effective Profile ENABLED
```

Un seul exemplaire logique de chaque agent/skill doit être visible.

---

# 16. Transition Core → Effective Profile

Lorsqu’un premier Expertise Pack doit devenir actif :

```text
agentic-core active
        ↓
resolve plugin
        ↓
install into private store
        ↓
build Effective IR
        ↓
materialize Effective Profile
        ↓
validate
        ↓
atomically switch runtime
```

Le switch doit conceptuellement produire :

```text
agentic-core runtime OFF
effective-profile runtime ON
```

pour le workspace courant.

---

# 17. Limitation du host

NE PAS supposer qu’un harness permet automatiquement :

```text
runtime plugin registration
workspace activation
hot reload
```

Le Host Materializer doit vérifier les capacités réellement disponibles.

Si le switch ne peut pas être réalisé automatiquement :

```text
materialize profile
→ validate
→ persist desired runtime state
→ return MATERIALIZED_PENDING_ACTIVATION
```

et fournir l’action minimale nécessaire au host.

MUST NOT prétendre que les nouveaux agents/tools sont actifs avant que le harness ne les expose réellement.

MUST NOT laisser core + profile actifs simultanément pour contourner la limitation.

---

# 18. Retour au core-only

Si tous les Expertise Packs sont désactivés :

```text
ActivePluginSet = {}
```

le système doit pouvoir revenir au mode :

```text
agentic-core only
```

sans décompilation.

Faire :

```text
discard current Effective Profile
→ reactivate agentic-core for workspace
```

Les sources du core n’ont jamais été modifiées.

---

# 19. Pas de décompilation

Uninstall/deactivate ne doit jamais calculer l’inverse d’une installation.

MUST NOT :

```text
profile
- lines added by ML-Eng
- tools added by ML-Eng
- skills added by ML-Eng
```

Faire :

```text
desired active set changed
        ↓
resolve from immutable sources
        ↓
build new Effective IR
        ↓
materialize new profile
```

Le précédent profile devient jetable.

---

# 20. Profile hash

Calculer un identifiant déterministe :

```text
profile_hash = hash(
    core_version,
    active_plugin_ids_and_versions,
    provider_resolutions,
    target_harness,
    relevant_host_capabilities,
    relevant_workspace_extensions
)
```

Les profiles peuvent être cachés :

```text
profiles/<hash>/
```

Deux workspaces avec exactement la même composition peuvent réutiliser le même profile lorsque cela est sûr.

---

# 21. Static checking — niveau 1 : Source Package

Créer :

```text
pluginctl check <package>
```

Chaque source package doit être vérifiable indépendamment.

Pour `agentic-core` :

```text
agent frontmatter
skill frontmatter
skill references
agent references
routing syntax
tool declarations
MCP config
IDs
schemas
```

Pour un Expertise Pack :

```text
plugin.json
skills
MCP declaration
integration metadata
contributed agents
capability declarations
```

Le package n’a pas besoin d’être actif pour être vérifié.

---

# 22. Static checking — niveau 2 : Composition

Avant matérialisation, valider l’Effective IR.

Détecter :

```text
duplicate agent IDs
duplicate incompatible skill IDs
missing required capabilities
ambiguous providers
invalid skill projection
invalid tool projection
unknown subagents
ownership conflicts
dependency cycles
forbidden augmentation
permission conflicts
```

Une composition invalide MUST NOT produire un runtime profile actif.

---

# 23. Static checking — niveau 3 : Target

Après materialization :

```text
Effective IR
→ Copilot Agent Plugin
```

valider le résultat concret :

```text
plugin.json valid
mcp.json valid
agent frontmatter valid
all agent IDs resolvable
all skills exist
all concrete tools exist
all allowed subagents exist
no duplicate visible agents
no unresolved capability IDs
no unresolved MCP names
```

Donc :

```text
SOURCE VALIDATION
+
COMPOSITION VALIDATION
+
TARGET VALIDATION
```

forment le checking complet.

---

# 24. Integration metadata

Utiliser une extension namespacée, par exemple :

```text
com.doodooms.agentic-workflow/
└── integration.yaml
```

Elle décrit uniquement la composition spécifique à `agentic-workflow`.

Ne pas dupliquer les metadata déjà présentes dans :

```text
plugin.json
mcp.json
```

---

# 25. Capability-based integration

Les plugins doivent dépendre de capabilities sémantiques.

Exemple :

```text
python.typecheck
github.search-code
ml.dataset.inspect
workspace.read
```

et non des noms physiques :

```text
mcp_foo_bar_xyz
```

Le resolver mappe :

```text
semantic capability
→ provider
→ concrete host tool
```

---

# 26. Capability Registry

Maintenir un registry contenant :

```text
capability ID
provider
provider version
concrete tool
permissions
read/write class
availability
trust level
priority
```

Les providers peuvent provenir :

```text
builtin harness tools
agentic-core MCP
active Expertise Packs
approved external MCP servers
```

Exemple :

```text
workspace.read
→ builtin read

github.search-code
→ GitHub MCP

python.typecheck
→ PythonDev MCP

ml.dataset.inspect
→ ML-Eng MCP
```

---

# 27. Tools provenant d’autres MCP

Un Expertise Pack doit pouvoir demander :

```text
github.search-code
python.typecheck
```

sans être propriétaire de ces tools.

Le resolver doit pouvoir satisfaire ces capabilities depuis :

```text
another active pack
approved external MCP
builtin host tool
```

Cela doit fonctionner sans coupler le plugin au nom physique du serveur.

---

# 28. Provider resolution

Si plusieurs providers satisfont une capability :

```text
explicit workspace pin
→ lockfile provider
→ trusted preferred provider
→ deterministic configured fallback
```

Une ambiguïté non résolue doit produire :

```text
CONFLICT
```

et non un choix LLM improvisé.

---

# 29. Integration autorisée sur les agents core

Par défaut, un plugin ne peut ajouter aux agents canoniques que :

```text
skills
tools/tool capabilities
allowed contributed subagents when necessary
```

Il ne peut PAS modifier :

```text
Role
Responsibilities
Constraints
Definitions
Routing
Workflow
Output Contract
```

Le but est :

```text
same agent responsibility
+
more expertise
+
more instruments
```

---

# 30. `<agent-skills>`

Le compiler peut augmenter la liste effective des skills d’un agent.

Exemple :

```text
Implementer core:
tdd
refactor-cleanup
documentation-sync
```

PythonDev ajoute :

```text
modern-python-development
python-typing
python-performance
```

Effective Implementer :

```text
core skills
UNION
projected plugin skills
```

avec :

```text
deduplication
stable ordering
provenance
```

Ne modifier que la section nécessaire.

---

# 31. Tool frontmatter

Même principe :

```text
core tools
UNION
resolved plugin tool capabilities
```

Les tools ajoutés doivent respecter least privilege.

Exemple :

```text
ML Engineer
→ training/model/data tools

QA
→ audit/compare/test tools

Reviewer
→ read-only evidence/static-analysis tools

Architect
→ inspection tools only
```

---

# 32. Nouveaux agents

Lorsqu’un plugin contribue :

```text
ml-engineer
```

le compiler doit :

```text
validate source agent
register capability ownership
resolve its skills
resolve its tool capabilities
resolve its subagents
include it in Effective Profile
add it to effective Orchestrator allowlist
```

sans patch manuel du core.

---

# 33. Routing canonique

NE PAS patcher dynamiquement `<routing>` des agents canoniques.

Effectuer une seule migration du core pour rendre Orchestrator plugin-aware.

Ajouter conceptuellement la règle générique :

```text
When a registered specialist owns a required capability
more specifically than a canonical generic agent,
route to that registered specialist.
```

L’Orchestrator utilise :

```text
resolve_owner(required_capability)
```

et non :

```text
if ML → ml-engineer
if Rust → rust-engineer
...
```

---

# 34. Planner plugin-aware

Si utile à l’architecture existante, permettre au Planner de produire :

```yaml
task:
  id: TASK-*
  required_capabilities:
    - ml.training
  suggested_owner: ml-engineer
```

Le champ durable est :

```text
required_capabilities
```

Le vrai owner est résolu par l’Orchestrator.

Ne pas rendre cette modification plus invasive que nécessaire.

---

# 35. Workspace project agents

Les agents projet-spécifiques dans :

```text
.github/agents/
```

restent indépendants de l’Effective Profile.

Ils ne doivent PAS être copiés dans le profile.

Mais tous les agents workspace ne deviennent pas automatiquement des subagents de l’Orchestrator.

Prévoir une déclaration explicite légère, par exemple :

```yaml
project_agents:
  product-data-specialist:
    orchestrator_visible: true
    owns:
      - project.product-data
```

Réutiliser une convention existante si possible.

Le compiler peut alors inclure cet ID dans l’allowlist effective de l’Orchestrator sans recopier l’agent.

---

# 36. Workspace skills

Les skills réellement project-specific restent dans :

```text
.github/skills/
```

Elles ne sont pas copiées dans l’Effective Profile.

Ne pas transformer automatiquement toute skill workspace en skill d’un agent core.

---

# 37. Trusted Registry

Créer un registry des Expertise Packs autorisés.

Exemple conceptuel :

```yaml
plugins:

  ml-eng:
    source: ...
    version: ...
    digest: ...
    auto_install: true

    provides:
      - ml
      - ml.training
      - ml.evaluation

  python-dev:
    source: ...
    version: ...
    digest: ...
    auto_install: true
```

---

# 38. Automatic installation

L’Orchestrator peut installer automatiquement un pack uniquement lorsque :

```text
trusted registry entry exists
source/publisher trusted
version allowed
digest/signature valid
core compatibility valid
dependencies resolve
no unresolved conflict
auto_install permitted
```

Les packs first-party approuvés peuvent être installés sans confirmation utilisateur.

NE PAS télécharger/exécuter arbitrairement des plugins trouvés sur Internet.

---

# 39. Detection d’un besoin

Ne pas activer un pack simplement parce qu’une technologie existe dans le repo.

Exemple :

```text
PyTorch detected
```

ne signifie PAS :

```text
activate ML-Eng
Vision-Eng
Inference-Eng
PythonDev
```

La décision vient d’une capability nécessaire à la tâche :

```text
task requires ml.training
→ ML-Eng

task requires ml.vision
→ Vision-Eng

task requires ml.inference
→ Inference-Eng
```

Toujours chercher le plus petit Active Set suffisant.

---

# 40. `install-agent-plugin`

Ajouter cette skill canonique à Orchestrator.

Workflow :

```text
required capability
        ↓
active capability registry
        ↓
provider exists?
   yes → continue
   no
        ↓
trusted registry
        ↓
approved provider?
        ↓
install package into private store
        ↓
validate source
        ↓
mark active for workspace
        ↓
resolve Effective IR
        ↓
materialize target profile
        ↓
validate target
        ↓
switch runtime safely
        ↓
resume workflow
```

---

# 41. `pluginctl`

Fournir une interface simple.

Conceptuellement :

```text
pluginctl check
pluginctl resolve
pluginctl install
pluginctl activate
pluginctl deactivate
pluginctl materialize
pluginctl inspect
pluginctl uninstall
pluginctl rollback
```

Le nombre exact de commandes peut être réduit.

Préférer une petite API cohérente.

---

# 42. Install ≠ activate ≠ materialize

`install` :

```text
fetch
verify
store
```

`activate` :

```text
update desired workspace Active Set
```

`materialize` :

```text
resolve Effective IR
generate target profile
validate
switch host runtime if possible
```

Ne jamais fusionner implicitement ces concepts dans le state model.

---

# 43. Lockfiles

Maintenir :

```text
workspace desired state
+
resolved lock
```

Exemple :

```yaml
core:
  version: ...

plugins:
  ml-eng:
    version: ...
    digest: ...
    active: true

  python-dev:
    version: ...
    digest: ...
    active: true

providers:
  ml.training: ml-eng
  python.typecheck: python-dev

effective_profile:
  hash: ...
  target: copilot
```

---

# 44. Installation transactionnelle

Une installation/activation doit être transactionnelle :

```text
resolve
↓
download staging
↓
verify
↓
source validation
↓
dependency resolution
↓
candidate lock state
↓
Effective IR
↓
composition validation
↓
target materialization staging
↓
target validation
↓
runtime switch
↓
commit desired/lock state
```

En cas d’échec :

```text
previous runtime remains active
```

---

# 45. Profiles immuables

Un profile déterminé par un hash ne doit pas être patché en place.

Si la composition change :

```text
old hash
→ new hash
→ new profile
```

L’ancien profile peut être supprimé plus tard comme cache.

---

# 46. Rollback

Rollback signifie :

```text
restore previous desired/locked state
→ rematerialize/reuse previous profile
→ switch runtime
```

Pas :

```text
reverse patches
```

---

# 47. Uninstall

Uninstall :

```text
remove pack from desired Active Set
→ resolve new Effective IR
→ materialize new profile/core-only mode
→ optionally remove package from store
```

Aucune décompilation.

---

# 48. Agentic-core uninstall

`agentic-core` constitue le bootstrap.

Dans un environnement géré :

```text
agentic-core
```

n’est pas une dependency optionnelle.

Le retirer signifie désinstaller `agentic-workflow` lui-même.

Les Expertise Packs peuvent être retirés indépendamment.

---

# 49. Existing Agent Plugins

Migrer :

```text
ML-Eng
PythonDev
Vision-Eng
Inference-Eng
```

vers ce système sans réécrire inutilement leurs skills.

## ML-Eng

Contribue :

```text
ml-engineer
```

## Vision-Eng

Dépend de capability :

```text
ml
```

et augmente principalement `ml-engineer`.

## Inference-Eng

Pas de nouvel agent v1.

## PythonDev

Pas de nouvel agent.

Le travail principal ici est leur contrat d’intégration déclaratif.

---

# 50. Source package validation tests

Tester séparément :

```text
agentic-core
ML-Eng
PythonDev
Vision-Eng
Inference-Eng
```

Un pack source invalide ne doit jamais atteindre la phase de composition.

---

# 51. Composition properties

Tester obligatoirement :

```text
compose(A, B, C)
==
compose(C, A, B)
```

quand les dépendances permettent les deux ordres.

Tester également :

```text
compose(state)
→ IR1

compose(state)
→ IR2

IR1 == IR2
```

---

# 52. Runtime duplication test

Créer un test explicite garantissant :

```text
core-only:
exactly one orchestrator visible
```

et :

```text
managed-profile:
exactly one orchestrator visible
exactly one architect visible
...
```

Avec ML-Eng :

```text
exactly one ml-engineer visible
```

Aucune skill ne doit apparaître deux fois à cause de :

```text
source plugin
+
effective profile
```

---

# 53. Round-trip test

Tester :

```text
core-only
→ activate ML-Eng
→ activate PythonDev
→ deactivate ML-Eng
→ deactivate PythonDev
→ core-only
```

Le dernier runtime doit être sémantiquement identique au runtime initial.

Aucun artefact stale ne doit rester visible.

---

# 54. Workspace isolation

Tester deux workspaces simultanément.

Workspace A :

```text
agentic-core
ML-Eng
Vision-Eng
PythonDev
```

Workspace B :

```text
agentic-core
PythonDev
```

Leurs capabilities effectives ne doivent pas fuir entre les deux.

---

# 55. Project-specific customization test

Workspace contient :

```text
.github/agents/product-data-specialist.agent.md
.github/skills/internal-data-contract/
```

Vérifier :

```text
they remain workspace-owned
they are not copied into Effective Profile
they remain discoverable by harness
registered project agent can enter Orchestrator allowlist when explicitly authorized
```

---

# 56. Static-check regression

Les validators actuels des agents et skills doivent continuer à fonctionner.

S’ils supposent actuellement des chemins directs comme :

```text
.github/agents/
.github/skills/
```

les refactorer pour accepter :

```text
source package
or
materialized target
```

sans dupliquer la logique de validation.

Créer des fonctions de validation réutilisables.

---

# 57. Core semantic preservation

Pendant composition, vérifier que les agents canoniques ne changent que sur les surfaces autorisées :

```text
frontmatter tools
frontmatter allowed agents
agent-skills projections
```

et éventuellement d’autres champs explicitement autorisés par schema.

MUST remain identical :

```text
Role
Responsibilities
Constraints
Definitions
Routing
Workflow
Output Contract
```

après composition.

---

# 58. Provenance

Chaque contribution effective doit être traçable.

Exemple :

```text
implementer.skill.python-typing
← PythonDev@1.0.0

quality-assurance.tool.ml.split.audit
← ML-Eng@1.2.0

orchestrator.agent.ml-engineer
← ML-Eng@1.2.0
```

`pluginctl inspect <agent>` doit idéalement exposer cette provenance.

---

# 59. Context-efficiency

Mesurer :

```text
skills visible
tools visible per agent
agents visible
unused tool exposure
```

avant/après plugin.

Le système est mauvais si activer Vision-Eng distribue tous ses tools à tous les agents.

Least privilege est obligatoire.

---

# 60. Non-goals v1

NE PAS construire :

```text
public marketplace
arbitrary Internet plugin discovery
distributed plugin registry
background daemon
hot reload if unsupported
complex ontology patching
automatic arbitrary workspace-agent trust
generic remote package manager
```

Rester simple.

---

# 61. Ordre d’implémentation

Procéder dans cet ordre :

```text
1. Inspect current repository and existing Agent Plugins.
2. Preserve existing work whenever compatible.
3. Package agentic-core as standalone Agent Plugin.
4. Verify core-only bootstrap works immediately after install.
5. Extract pluginctl as deterministic core infrastructure.
6. Create install-agent-plugin skill.
7. Define integration metadata schema.
8. Define semantic capability naming.
9. Implement private plugin store.
10. Implement AVAILABLE/INSTALLED/ACTIVE/MATERIALIZED states.
11. Implement trusted registry.
12. Implement source-package validation.
13. Implement capability registry/resolver.
14. Implement Effective IR.
15. Implement plugin composition.
16. Implement skill projection.
17. Implement tool projection.
18. Implement contributed-agent composition.
19. Make Orchestrator generically plugin-aware.
20. Add minimal Planner/core compatibility changes if required.
21. Implement workspace project-agent registration if needed.
22. Implement profile hash/cache.
23. Implement Copilot Host Materializer.
24. Implement Effective Profile validation.
25. Implement transactional runtime switching.
26. Implement safe fallback when runtime switch requires host reload.
27. Implement deactivate/uninstall/rollback by recomposition.
28. Migrate ML-Eng integration metadata.
29. Migrate PythonDev.
30. Migrate Vision-Eng.
31. Migrate Inference-Eng.
32. Add static-check tests at all three layers.
33. Add composability/idempotence tests.
34. Add duplicate-runtime tests.
35. Add multi-workspace tests.
36. Add project-customization tests.
37. Add context-efficiency tests.
38. Document the complete lifecycle.
```

---

# 62. Acceptance scenario — fresh installation

Given:

```text
fresh VS Code
fresh project
```

When:

```text
install agentic-core Agent Plugin
```

Then immediately:

```text
9 canonical agents available
canonical skills available
Orchestrator usable
install-agent-plugin usable
no Effective Profile required
```

---

# 63. Acceptance scenario — first ML task

Given core-only runtime.

Task requires:

```text
ml.training
```

Expected:

```text
resolve trusted ML-Eng
install into private store
validate
activate for workspace
build Effective IR
materialize Effective Profile
validate
switch from core runtime to profile runtime
```

Effective runtime contains:

```text
all core agents
+
ml-engineer
+
only relevant ML skill/tool projections
```

Exactly one copy of every core agent exists.

---

# 64. Acceptance scenario — CV + Python

Capabilities:

```text
ml
ml.vision
python.development
```

Resolve:

```text
ML-Eng
Vision-Eng
PythonDev
```

ML Engineer receives relevant combined expertise.

Implementer receives only relevant Python expertise.

QA/Reviewer receive their narrow projections.

No unrelated agent receives all ML/Vision/Python tools.

---

# 65. Acceptance scenario — deactivate everything

Starting profile:

```text
agentic-core
ML-Eng
Vision-Eng
PythonDev
```

Deactivate all Expertise Packs.

Expected:

```text
return safely to direct agentic-core runtime
```

No generated copy remains active.

No plugin-specific capabilities remain visible.

---

# 66. Acceptance scenario — host cannot hot-switch

If Copilot cannot activate the generated profile automatically:

```text
profile is materialized and validated
state = MATERIALIZED_PENDING_ACTIVATION
```

Do not expose duplicate core/profile runtime.

Return the exact minimal host action required.

Resume orchestration only after the effective profile is actually available.

---

# 67. Acceptance scenario — delete generated profiles

Delete:

```text
~/.agentic-workflow/profiles/*
```

Then rerun materialization.

Expected:

```text
identical effective profiles recreated from:
agentic-core source
plugin store
workspace desired state
lockfile
host capabilities
```

Generated profiles must contain no irreplaceable state.

---

# 68. Fundamental invariants

Preserve these rules above all else:

> `agentic-core` is itself a directly installable, standalone Agent Plugin.

> Expertise Packs managed by `agentic-workflow` are source packages, not simultaneously active harness plugins.

> Installing a plugin never mutates canonical core sources.

> Workspace customizations remain project-specific and are never replaced by generated copies of the core.

> Runtime composition is produced from immutable inputs, never incremental patches.

> Deactivation/uninstall means recomposition, never decompilation.

> Core-only runtime and Effective Profile runtime must never be active simultaneously in the same workspace.

> Static checking occurs at source-package, Effective-IR and materialized-target levels.

> If generated runtime artifacts are deleted, the complete effective runtime must be reproducible.

---

# 69. Final report

À la fin, produire :

```text
1. Existing architecture discovered.
2. Existing Agent Plugin work preserved/refactored.
3. agentic-core Agent Plugin structure.
4. Core-only bootstrap validation.
5. pluginctl architecture.
6. install-agent-plugin skill.
7. Private plugin store design.
8. Plugin state machine.
9. integration metadata schema.
10. Capability registry/resolver.
11. Effective IR design.
12. Agent composition rules.
13. Skill projection rules.
14. Tool projection rules.
15. Contributed-agent handling.
16. Workspace project customization handling.
17. Effective Profile format.
18. Profile hash/cache strategy.
19. Copilot materialization strategy.
20. Host activation/reload limitations found.
21. Static validation architecture.
22. Runtime duplication guarantees.
23. Transaction/rollback strategy.
24. ML-Eng migration status.
25. PythonDev migration status.
26. Vision-Eng migration status.
27. Inference-Eng migration status.
28. Tests and results.
29. Context-efficiency results.
30. Known limitations and deferred work.
```

Do NOT claim completion if any of these remain possible:

```text
core and compiled core visible simultaneously
Expertise Pack source and compiled contribution visible simultaneously
plugin installation mutates canonical core
workspace contains generated copies of generic agents/skills
uninstall requires reversing patches
installation order changes Effective IR
generated profiles contain non-reconstructible state
invalid source package can reach runtime
unresolved capability silently disappears
failed materialization corrupts previous runtime
```

The architecture is complete only when `agentic-core` can operate alone immediately after installation and can later enrich itself with arbitrary compatible Expertise Packs without duplicating, mutating or destabilizing its canonical runtime.
