Oui, ton intuition est bonne, avec une nuance importante : **je ne transformerais pas mécaniquement chaque skill en un tool MCP distinct**. Je transformerais plutôt ton catalogue en une **capability layer MCP**, avec exposition sélective par agent et chargement tardif des capacités. C’est précisément aligné avec ton objectif de minimiser le contexte.

VS Code permet aujourd’hui à un custom agent de déclarer explicitement les tools auxquels il a accès, y compris des tools MCP individuels, des tool sets, ou tout un serveur via `<server>/*`. La documentation recommande d’ailleurs de garder le catalogue actif petit, car les définitions de tools consomment du contexte et compliquent la sélection ; il existe même une limite de 128 tools par requête. ([Visual Studio Code][1])

## Les MCP externes que je mettrais réellement dans ton système

| Priorité  | MCP                            | Agents principaux              | Pourquoi                                                                         |
| --------- | ------------------------------ | ------------------------------ | -------------------------------------------------------------------------------- |
| **1**     | **GitHub MCP**                 | Orchestrator, Reviewer, DevOps | PR, issues, Actions, releases, code/security findings, Dependabot, repo metadata |
| **2**     | **Context7**                   | Researcher                     | Docs API/librairies actuelles et versionnées, avec seulement quelques tools      |
| **3**     | **Semgrep MCP**                | Reviewer principalement        | Analyse statique déterministe, vulnérabilités, AST, règles Semgrep               |
| **4**     | **Playwright**                 | Quality Assurance              | Tests navigateur/E2E, exploration UI, network/storage/browser state              |
| **5**     | **Sentry MCP**                 | QA, éventuellement DevOps      | Bugs réels, stack traces, traces, performance, événements production             |
| **infra** | **Docker MCP Toolkit/Gateway** | système                        | Isolation, packaging et profils de serveurs MCP                                  |

### 1. GitHub MCP — presque obligatoire

C’est celui qui apporte le plus à ton Orchestrator.

Le serveur officiel GitHub expose notamment repositories, issues, PRs, Actions, releases, code scanning, secret scanning, Dependabot, Git et plusieurs autres surfaces. Surtout, il permet de limiter précisément les **toolsets** ou même les tools individuels, et possède un mode read-only. ([GitHub][2])

Je ne donnerais pas le même profil à tout le monde.

```text
orchestrator
→ PRs
→ issues
→ repositories
→ maybe Actions
→ lifecycle/write operations

reviewer
→ PRs
→ code_quality
→ code_security
→ dependabot
→ read-only

devops
→ Actions
→ releases
→ repository metadata
→ selected write operations
```

C’est exactement le genre de serveur où ton principe de **least privilege per agent** est très intéressant.

GitHub dit d’ailleurs explicitement que limiter les toolsets améliore la sélection des tools et réduit la taille du contexte. ([GitHub][2])

---

## 2. Context7 — très bon pour ton Researcher

Je le donnerais presque exclusivement au `researcher`.

Context7 fournit de la documentation récente et versionnée pour les bibliothèques et frameworks, et propose soit CLI + skill, soit MCP. ([GitHub][3])

Dans ton architecture :

```text
Architect / Implementer / Planner
          │
          ▼
      Researcher
          │
          ▼
      Context7 MCP
          │
          ▼
compact research packet
```

Ça correspond parfaitement à la raison pour laquelle tu as conservé Researcher : brûler beaucoup de contexte externe dans un subagent puis ne renvoyer que le résultat pertinent.

Et Context7 est relativement peu coûteux en surface de tools comparé à certains gros MCP.

---

## 3. Semgrep MCP — excellent complément à `security-review`

Je l’intégrerais.

Le serveur Semgrep existe maintenant directement dans le projet principal et se lance via :

```text
semgrep mcp
```

Il permet aux agents d’exécuter des scans Semgrep ; Semgrep fournit également des capacités de supply-chain scanning et secrets scanning. ([GitHub][4])

Je le donnerais principalement à :

```text
Reviewer
    └── security-review
            └── Semgrep MCP
```

QA reste propriétaire du **dynamic/adversarial security testing**.

Donc ta séparation reste :

```text
QA
security-testing
→ dynamic

Reviewer
security-review
→ static
→ Semgrep
```

Ce qui est particulièrement intéressant est que Semgrep apporte une vraie capacité **déterministe**, contrairement à une simple checklist de sécurité LLM.

---

## 4. Playwright : oui, mais avec une nuance importante

Pour QA :

```text
quality-assurance
    └── e2e-testing
        └── Playwright
```

est très naturel.

Playwright MCP fournit contrôle navigateur, snapshots d’accessibilité, interactions, network mocking, storage, tracing, etc. ([GitHub][5])

Mais Microsoft recommande désormais explicitement **Playwright CLI + Skills plutôt que MCP pour les coding agents**, précisément pour la raison qui t’intéresse : MCP charge les schemas des tools et produit des snapshots plus lourds, tandis que le CLI est plus token-efficient. Le MCP reste préférable lorsque tu as besoin d’une boucle browser persistante, exploratoire ou avec état. ([GitHub][6])

Donc pour ton architecture :

```text
default:
QA + e2e-testing skill
→ Playwright CLI

special case:
persistent/exploratory browser session
→ Playwright MCP
```

C’est un excellent exemple montrant que **MCP n’est pas automatiquement supérieur à skill + CLI**.

---

## 5. Sentry MCP — très puissant mais domain-dependent

Pas dans ton kernel universel, mais extrêmement intéressant dès qu’une codebase utilise Sentry.

Le MCP officiel est spécifiquement conçu pour les coding agents et donne accès aux issues, events, traces et recherches dans les erreurs/performance. ([GitHub][7])

Chez toi :

```text
user:
"production crashes sometimes"

Orchestrator
    ↓
Quality Assurance
    ↓
failure-analysis
    ↓
Sentry MCP
    ↓
actual production evidence
    ↓
defect packet
```

Là tu augmentes énormément la puissance de QA.

Je donnerais généralement Sentry en read-only/inspect à QA.

Éventuellement DevOps peut aussi avoir accès à certaines informations opérationnelles.

---

# Docker MCP Toolkit : intéressant pour ton infrastructure MCP

Docker propose maintenant un MCP Toolkit avec catalogue de serveurs vérifiés, isolation en containers, profils et même Dynamic MCP, qui permet d’ajouter des serveurs/tools à la demande. ([Docker Documentation][8])

Pour toi, je trouve surtout intéressant :

```text
profiles
```

par exemple :

```text
agentic-research
agentic-qa
agentic-review
agentic-devops
```

En revanche je serais prudent avec :

```text
Dynamic MCP:
"agent discovers arbitrary MCP servers dynamically"
```

parce que ça va à l’encontre de ton architecture :

```text
explicit authority
deterministic tools
auditable routing
least privilege
```

Je veux que **l’Orchestrator ou la configuration d’agent décide des capabilities**, pas que QA décide soudainement qu’il lui faut 17 serveurs MCP externes.

---

# Les MCP que je n’installerais PAS dans ton kernel

Je n’ajouterais pas un filesystem MCP : VS Code te donne déjà `read/search/edit`.

Je n’ajouterais probablement pas un Git MCP générique : tu as `execute` + Git local et GitHub MCP pour le remote.

Je n’ajouterais pas un generic shell MCP : `execute` existe déjà et peut être sandboxé.

Je n’ajouterais pas un generic memory MCP puisque ton système de mémoire est une responsabilité architecturale propre de ton harness.

Je n’ajouterais pas non plus Postgres/Kubernetes/Terraform/etc. globalement. Ceux-là deviennent des **domain MCPs**, activés uniquement pour les agents/codebases concernés.

---

# Concernant ton idée : transformer les skills en tools

L’idée fondamentale est bonne.

Aujourd’hui :

```text
agent
    ↓
sees N skill descriptions
    ↓
select skill
    ↓
loads SKILL.md
```

Tu voudrais :

```text
agent
    ↓
sees only authorized MCP tools
    ↓
select tool
    ↓
server executes/loads capability
```

Cela permet surtout :

```text
Architect
doesn't even know:
tdd
security-testing
e2e-testing
delivery-operations
...
```

alors que :

```text
QA
doesn't even see:
architecture-design
implementation-planning
delivery-operations
...
```

C’est conceptuellement très bon.

Et VS Code permet exactement cette limitation au niveau du custom agent. ([Visual Studio Code][1])

---

# Mais je ne compilerais pas `1 skill = 1 MCP tool` systématiquement

Parce qu’il y a trois types de skills très différents.

### Type A — skill procédurale pure

Par exemple :

```text
tdd
architecture-design
implementation-planning
code-review
```

Elle contient principalement :

```text
instructions
decision process
workflow
references
```

Ce n’est pas réellement un « tool » au sens classique.

Le serveur n’effectue rien de déterministe.

Pour celles-ci je construirais plutôt un mécanisme de **capability loading**.

---

### Type B — skill avec vraie opération déterministe

Exemples :

```text
change-impact-analysis
verification-loop
security scan
dependency inspection
lint
AST extraction
coverage analysis
```

Là :

```text
skill → MCP tool
```

est excellent.

Le modèle appelle :

```text
impact.analyze(...)
security.scan(...)
verification.run(...)
```

et reçoit un résultat structuré.

---

### Type C — skill d'orchestration

Exemples :

```text
spec-driven-development
orchestrate
```

Je ne les transformerais surtout pas en un énorme :

```text
sdd.run_everything()
```

Le contrôle doit rester chez l’Orchestrator.

En revanche tu peux exporter des primitives déterministes :

```text
sdd.validate_spec
sdd.compute_staleness
sdd.check_traceability
sdd.compute_convergence
```

Ça, c’est parfait.

---

# L’architecture que je construirais pour tes skills

Je créerais ton propre MCP :

```text
capabilityd
```

ou éventuellement dans ton nomenclature actuelle :

```text
workflowd
```

et je ferais une distinction entre **discovery**, **loading** et **execution**.

Au départ il n’expose que quelques meta-tools :

```text
capability.search
capability.describe
capability.invoke
```

### `capability.search`

Input :

```json
{
  "query": "Need adversarial testing for authorization changes"
}
```

Output :

```json
{
  "matches": [
    {
      "id": "security-testing",
      "kind": "workflow",
      "description": "..."
    },
    {
      "id": "adversarial-testing",
      "kind": "workflow",
      "description": "..."
    }
  ]
}
```

Très peu de contexte.

---

### `capability.describe`

```text
capability.describe("security-testing")
```

retourne seulement à ce moment :

```text
definitions
admission
input contract
workflow
available deterministic operations
```

Donc tu reproduis ton **progressive disclosure**, mais au niveau MCP.

---

### `capability.invoke`

Pour les capacités exécutables :

```json
{
  "capability": "security-scan",
  "arguments": {...}
}
```

Le serveur valide les arguments avec le schema spécifique avant exécution.

---

# Encore mieux : activation dynamique

La spec MCP actuelle possède explicitement :

```text
tools/list
notifications/tools/list_changed
```

et un serveur peut signaler que son catalogue de tools a changé. ([Model Context Protocol][9])

Tu pourrais donc faire :

```text
initial context:

capability.search
capability.activate
capability.deactivate
```

Puis :

```text
agent:
capability.activate("tdd")
```

Le serveur enregistre alors :

```text
tdd.start
tdd.verify_red
tdd.verify_green
...
```

et envoie :

```text
notifications/tools/list_changed
```

Le client recharge uniquement ces schemas.

Après usage :

```text
capability.deactivate("tdd")
```

et ils disparaissent.

C’est exactement l’équivalent MCP de :

```text
progressive disclosure
```

au niveau des tools.

VS Code indique implémenter le protocole MCP complet, donc le mécanisme vaut clairement la peine d’être prototypé et évalué dans ton harness. ([Visual Studio Code][10])

---

# Mais je commencerais encore plus simplement

Avant Dynamic MCP :

```text
ONE MCP SERVER

capabilityd
```

avec tous les tools internes.

Puis les agents contrôlent ce qu’ils voient.

Exemple conceptuel :

```yaml
architect:
  tools:
    - read
    - search
    - capability/architecture_design
    - capability/change_impact
    - agent

implementer:
  tools:
    - read
    - search
    - edit
    - execute
    - capability/tdd
    - capability/verification
    - capability/documentation_sync

quality-assurance:
  tools:
    - read
    - search
    - execute
    - capability/adversarial_testing
    - capability/failure_analysis
    - capability/security_testing
    - playwright/*

reviewer:
  tools:
    - read
    - search
    - capability/code_review
    - capability/security_review
    - semgrep/*

researcher:
  tools:
    - read
    - search
    - context7/*
    - web
    - browser
```

VS Code permet explicitement ce type d’allowlist, y compris des tools MCP ou `<server>/*`. ([Visual Studio Code][1])

Tu obtiens immédiatement ton objectif sans développer de dynamic discovery complexe.

---

# Ce que je trouve particulièrement intéressant dans cette architecture

Actuellement ta séparation est :

```text
AGENT
= identity + ontology + authority

SKILL
= procedural knowledge

TOOL
= capability
```

Je ne supprimerais pas cette distinction.

Je ferais plutôt :

```text
AGENT
identity
authority
routing
local ontology

        ↓

CAPABILITY
procedural contract
admission
workflow

        ↓

TOOLS
deterministic operations
external systems
side effects
```

Donc une skill ne **devient pas nécessairement** un tool.

Une skill peut devenir un **capability package** qui déclare :

```text
instructions
resources
scripts
tools
input/output schemas
permissions
```

et ton MCP expose les parties exécutables.

C’est plus propre architecturalement.

---

## Ce que je mettrais en place en premier

Si je devais faire évoluer ton système maintenant, l’ordre serait :

1. **GitHub MCP**, parce qu’il renforce immédiatement Orchestrator/Reviewer/DevOps.
2. **Context7 MCP** uniquement pour Researcher.
3. **Semgrep MCP** pour Reviewer/security-review.
4. **Playwright CLI + skill** pour QA, MCP seulement quand l’état navigateur persistant est utile.
5. **Sentry MCP** comme extension de projet quand Sentry existe.
6. Construire **`capabilityd`**, ton MCP interne.
7. Au début, exposer statiquement quelques tools par agent.
8. Ensuite seulement expérimenter `tools/list_changed` + activation dynamique.
9. Mesurer avec Waza exactement comme pour tes skills :

   * tool-selection accuracy ;
   * false tool calls ;
   * tokens avant première action correcte ;
   * schemas chargés ;
   * task completion ;
   * cross-agent capability leakage.

Je pense que ton intuition sur MCP est très proche de la bonne architecture, mais la bonne abstraction n’est pas vraiment **« transformer toutes mes skills en tools »**. C’est plutôt :

> **transformer ton catalogue de skills en un registry de capabilities, puis exposer à chaque agent uniquement les interfaces exécutables ou chargeables dont il a besoin.**

C’est beaucoup plus puissant, et surtout ça préserve la séparation conceptuelle que tu as construite entre **agent = responsabilité**, **skill = méthode**, et **tool = action**.

[1]: https://code.visualstudio.com/docs/agent-customization/custom-agents?utm_source=chatgpt.com "Custom agents in VS Code"
[2]: https://github.com/github/github-MCP-server?utm_source=chatgpt.com "GitHub - github/github-mcp-server: GitHub's official MCP Server · GitHub"
[3]: https://github.com/upstash/context7?utm_source=chatgpt.com "GitHub - upstash/context7: Context7 Platform -- Up-to-date code documentation for LLMs and AI code editors · GitHub"
[4]: https://github.com/semgrep/semgrep?utm_source=chatgpt.com "GitHub - semgrep/semgrep: Lightweight static analysis for many languages. Find bug variants with patterns that look like source code. · GitHub"
[5]: https://github.com/microsoft/playwright.dev/blob/main/mcp/introduction.mdx?utm_source=chatgpt.com "playwright.dev/mcp/introduction.mdx at main · microsoft/playwright.dev · GitHub"
[6]: https://github.com/mcp/microsoft/playwright-mcp?utm_source=chatgpt.com "MCP Registry | Playwright · GitHub"
[7]: https://github.com/getsentry/sentry-mcp/blob/main/README.md?utm_source=chatgpt.com "sentry-mcp/README.md at main · getsentry/sentry-mcp · GitHub"
[8]: https://docs.docker.com/ai/mcp-catalog-and-toolkit/toolkit/?utm_source=chatgpt.com "Docker MCP Toolkit | Docker Docs"
[9]: https://modelcontextprotocol.io/specification/2025-11-25/server/tools "Tools - Model Context Protocol"
[10]: https://code.visualstudio.com/api/extension-guides/ai/mcp?utm_source=chatgpt.com "MCP developer guide | Visual Studio Code Extension API"
