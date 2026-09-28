Tu travailles dans le repository `agentic-workflow`.

Je veux faire converger le projet vers une architecture **plugin-first**.

## Objectif

Tout ce qui constitue une expertise **réutilisable et générique** doit être packagé dans un **Agent Plugin**.

Je ne veux plus maintenir en parallèle des copies user-space séparées de :

```text
agents/
skills/
MCP/
```

lorsque ces composants appartiennent déjà à un domaine réutilisable.

Le modèle cible est :

```text
Agent Plugin
    ↓
bounded expertise domain
    ↓
Agents
    ↓
Skills
    ↓
Workflows
    ↓
References / Assets
    ↓
MCP Tools
```

Avec les responsabilités suivantes :

```text
Agent Plugin
= package d'expertise réutilisable / bounded domain

Agent
= propriétaire d'une responsabilité durable

Skill
= interface vers un sous-domaine d'expertise

Workflow
= procédure spécialisée interne à une skill

Reference / Asset
= connaissance profonde chargée progressivement

MCP Tool
= capability exécutable/déterministe
```

---

## 1. Les Agent Plugins deviennent l’unité principale de packaging

Exemples :

```text
agentic-core/
ml-eng/
research/
hr/
legal/
python-dev/
rust-dev/
...
```

Chaque plugin doit contenir tout ce qui lui appartient :

```text
plugin/
├── plugin manifest
├── skills/
├── MCP declarations / servers
├── harness-specific extensions/
└── agentic-workflow integration metadata/
```

Lorsqu’un harness supporte nativement un composant, utiliser son format natif.

Lorsqu’il ne le supporte pas, conserver une représentation portable/canonique dans le plugin et laisser un adapter harness-specific la matérialiser.

---

## 2. Ne pas dupliquer les composants

Éviter absolument :

```text
agentic-core plugin:
    implementer
    testing

AND

global user-space:
    implementer
    testing

AND

workspace:
    implementer
    testing
```

Une capability générique doit avoir **une seule source canonique : son plugin**.

---

## 3. Le workspace n’est pas un second package store

Le workspace doit être réservé à ce qui est réellement spécifique au projet :

```text
project-specific agents
project-specific skills
project instructions
project semantic model
project configuration
plugin selection / lock state
```

Exemples légitimes :

```text
factory-image-specialist
internal-release-process
company-dataset-conventions
project-specific-domain-rules
```

Les agents et skills génériques de `agentic-core`, `ML-Eng`, etc. ne doivent PAS y être copiés manuellement.

---

## 4. `agentic-core`

`agentic-core` devient lui-même un Agent Plugin directement installable.

Il contient le baseline générique du workflow logiciel :

```text
Orchestrator
Architect
Planner
Researcher
Implementer
Quality Assurance
Reviewer
Challenger
DevOps

+ canonical core skills
+ plugin-management capability
```

Il doit fonctionner seul après installation.

Conceptuellement :

```text
agentic-core
=
agentic organizational runtime
+
baseline software-engineering expertise
```

Ne pas essayer pour l’instant de séparer un `agentic-kernel` d’un `software-engineering-plugin`.

---

## 5. Vertical vs Horizontal plugins

Préserver deux familles.

### Vertical

Représente un domaine relativement autonome :

```text
ML-Eng
Research
HR
Legal
Finance
Security
```

Peut apporter :

```text
new agents
domain skills
domain workflows
domain tools
```

### Horizontal

Apporte une expertise transverse :

```text
PythonDev
RustDev
Database
AWS
ScientificPython
```

Il augmente surtout les agents existants plutôt que d’introduire un nouvel ownership.

---

## 6. Progressive disclosure interne

Les plugins doivent utiliser la hiérarchie :

```text
Plugin
→ Agent
→ Skill
→ Workflow
→ Reference / Asset / Tool
```

Le harness ne doit découvrir que les high-level skills.

Exemple :

```text
testing/
├── SKILL.md
├── workflows/
│   ├── regression.md
│   ├── property-based.md
│   ├── concurrency.md
│   └── integration.md
└── references/
```

Les workflows ne sont pas des skills globalement enregistrées.

Ils constituent l’expertise spécialisée interne du parent skill.

---

## 7. Workspace d’intégration

Je veux ensuite pouvoir créer un **petit workspace d’intégration**, indépendant des plugins eux-mêmes.

Sa responsabilité sera uniquement :

```text
select plugins
resolve capabilities
adapt canonical plugin representation to current harness
materialize harness-specific configuration when required
validate resulting runtime surface
```

Conceptuellement :

```text
                Agent Plugins

      agentic-core   ML-Eng   PythonDev
             \         |        /
              \        |       /
                 Integration
                  Workspace
                     |
                Host Adapter
                     |
        ┌────────────┼────────────┐
        │            │            │
      Copilot      Codex       Future Host
```

---

## 8. Harness adapters

Un plugin ne doit pas être conçu autour de VS Code, Codex ou d’un autre harness particulier.

Préférer :

```text
portable/canonical plugin content
        +
optional harness-specific extension
```

Puis :

```text
integration workspace
→ target harness adapter
```

Un adapter peut notamment :

```text
translate agent definitions
resolve tool identifiers
materialize allowlists
project plugin skills/tools onto agents
generate host-specific files/configuration
```

Mais il ne doit jamais modifier la source canonique du plugin.

---

## 9. Important architectural invariant

Le plugin décrit :

```text
WHAT expertise exists
WHO owns responsibilities
HOW subdomains are structured
WHAT capabilities are required/provided
```

Le workspace d’intégration décrit :

```text
HOW this set of plugins is exposed to this particular harness
```

Donc :

> Domain expertise belongs to plugins.

> Harness compatibility belongs to adapters.

> Project-specific knowledge belongs to the project workspace.

Ne pas mélanger ces trois niveaux.

---

## 10. Desired developer workflow

Je veux pouvoir travailler ainsi :

### Ajouter une nouvelle expertise

```text
create/update plugin
→ define agents
→ define high-level skills
→ define internal workflows
→ define tools/capabilities
→ validate plugin
```

### Utiliser cette expertise dans un projet

```text
select plugin
→ integration workspace resolves it
→ appropriate host adapter materializes it
→ project-specific customizations remain local
```

### Changer de harness

```text
same plugins
same expertise
same ownership
        ↓
different adapter
        ↓
different harness representation
```

Aucune réécriture du domaine ne doit être nécessaire.

---

## 11. Migration demandée

Inspecte l’architecture actuelle et propose le chemin minimal vers ce modèle.

En particulier :

```text
1. Identify reusable agents/skills/tools currently outside plugins.
2. Determine which plugin should own each one.
3. Identify actual project-specific content that should remain workspace-local.
4. Remove or deprecate duplicated user/workspace copies.
5. Make agentic-core a self-contained Agent Plugin.
6. Preserve existing Expertise Packs.
7. Define the minimum canonical integration metadata needed by adapters.
8. Design a small integration workspace.
9. Keep harness-specific logic outside domain plugins whenever possible.
10. Validate that one plugin source can target multiple harnesses.
```

Do not perform a large speculative rewrite if the current architecture can be migrated incrementally.

---

## 12. Non-goals

Do NOT build yet:

```text
generic marketplace
full package manager
complex remote dependency solver
DecisionEngine/Jev
runtime hot-reload system
unnecessary abstraction framework
```

The objective is first to establish clean packaging and ownership boundaries.

---

## 13. Final architecture

Target:

```text
REUSABLE EXPERTISE
        │
        ▼
   Agent Plugins
        │
        │ canonical
        ▼
Integration Workspace
        │
        ▼
 Harness Adapter
        │
        ▼
Effective Harness Runtime

+

PROJECT WORKSPACE
        │
        └── genuinely project-specific customization
```

Fundamental rule:

> If a capability makes sense across multiple repositories, it probably belongs in an Agent Plugin.

> If it only makes sense for one repository, it belongs in that workspace.

> If it exists only because a harness expects a particular representation, it belongs in the integration adapter.

Use these rules to simplify the current repository structure and remove unnecessary duplication.
