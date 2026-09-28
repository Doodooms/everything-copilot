# État et plan — agentic-core

Date : 2026-09-26. Ce fichier est un instantané historique de suivi; les longues spécifications restent des sources de contexte.

## Git vérifié

- Dépôt : `/home/pm/projets-persos/agentic-workflow`.
- Branche locale active : `chore/unify-agent-contracts`.
- HEAD : `502163541128cfbab235166d2ff616bd7e336d60`, parent `005ad55983d404bf32cccc8e9888e743c0c003d7`.
- Le commit existe dans ce clone. Il n’a pas été poussé et la branche n’a pas d’upstream configuré; il n’est donc pas publié sur `origin`. `master` local pointe sur `3f53074`.
- Pour vérifier dans le terminal, utiliser le même chemin puis `git status -sb`, `git branch -vv` et `git log -1 --oneline --decorate`. Si le résultat diffère, le terminal est dans un autre clone/contexte.

## Réalisé

- Commit `feat(plugin): package agentic-core and tune role budgets` : package `agentic-core` ajouté, anciennes définitions workspace `.github/agents` et skills `create-agent`/`create-skill` retirées au profit du package, avec `plugin.json`, `mcp.json` et le runtime `pluginctl`.
- Le package contient **9 agents** et **10 domaines de skills**. Les agents disposent de politiques `<agent-skills>`; `quality-engineering` inclut notamment `test-design`.
- Le SDD prend en charge un modèle sémantique distinct du solution space, les hypothèses et la validation d’état. Les workflows spécialisés sont exposés directement sous `workflows/`, sans les anciens wrappers de procédure imbriqués.
- Les principes de risque et les profils statiques d’effort ont été ajustés. Les valeurs de `reasoning-effort` ne prouvent pas que l’hôte les applique; aucun mécanisme dynamique n’a été établi.
- `mcp.json` déclare Context7 `4.1.1`, Semgrep `1.177.0` et le serveur GitHub MCP officiel `v1.12.2`, lancé en stdio dans un conteneur Docker dédié avec les paramètres GitHub App fournis hors plugin et une clé montée en lecture seule. Orchestrator utilise le MCP distant; Researcher conserve une allowlist de lecture explicite.
- Des rapports précédents documentent la suite unittest complète passée et les validations ciblées des agents, skills et auteurs. Les comptes globaux consignés divergent (201/202); la suite n’a pas été relancée pendant cet état des lieux. Le scan Semgrep supply-chain n’a pas abouti (`Workspace directory not found`, CLI locale absente).

## Fichiers de suivi classés sous `done/2026-09-26` (statuts réévalués)

- [semantic_sdd.md](../../done/2026-09-26/semantic_sdd.md) — modèle sémantique et validation couverts par le SDD et ses tests.
- [subskills-fix-source.md](../../in_progress/2026-09-27/subskills-fix-source.md) — reclassé comme source active car l'audit n'est pas terminé. Dix copies `method-source.md` ont été retirées après comparaison et réintégration de leur contenu; 33 autres sources, la fidélité des procédures et les références orphelines restent suivies par `TASK-5-03A`.
- [skills_to_create.md](../../done/2026-09-26/skills_to_create.md) — inventaire et décisions de pruning documentés; les idées explicitement différées ne sont pas une commande de création immédiate.

Le 2026-09-27, les sources non terminées de ce dossier ont été reclassées dans `todos/backlog/2026-09-26` pour garder `todos/in_progress` vide. Ce déplacement ne les marque pas comme terminées; leurs livrables et validations ouverts restent à affecter dans un futur plan.

## État des autres tâches

- [plugin_migration_1.md](./plugin_migration_1.md) — **partiel** : le package Core existe; migration de tous les packs existants et conformité multi-harness ne sont pas établies.
- [plugin_migration_2.md](./plugin_migration_2.md) et [agent_plugin.md](./agent_plugin.md) — **partiels** : `pluginctl` fournit déjà active set, résolution, profils matérialisés et rollback; les Definition of Done du framework complet et de ML-Eng v1 ne sont pas atteintes. PythonDev, Vision-Eng et Inference-Eng ne sont pas livrés comme packs dans ce commit.
- [agents-fix.md](./agents-fix.md) — **partiel** : corrections de frontières, risque et effort appliquées; les scénarios A–F demandés n’ont pas tous une preuve d’exécution agentique.
- [skill-refactor.md](./skill-refactor.md) — **partiel** : hiérarchie et workflows directs en place; les évaluations comparatives flat/hierarchical, discoverability et coût/qualité demandées restent à établir.
- [skill_ideas.md](./skill_ideas.md) — **partiel** : politiques `<agent-skills>`, `test-design`, sémantique SDD et méthodes de conception existent; instrumentation/évaluations de l’usage et plusieurs critères de mesure restent à vérifier.
- [mcp_core.md](./mcp_core.md) — **partiel** : Context7, Semgrep et GitHub App MCP sont désormais déclarés; les choix éventuels Playwright MCP, Sentry et les autres serveurs restent à décider/configurer; aucun scan SCA réussi.
- [mcp-tools.md](./mcp-tools.md) — document d’idées d’intégrations Hermes, pas une intégration agentic-core spécifiée. Aucune de ces intégrations n’a été ajoutée; garder en attente d’une décision de pertinence.

## Travaux locaux non inclus dans le commit

Ils ont été préservés, pas nettoyés ni attribués à cette livraison : modifications de `scripts/build_create_skill_benchmark.py`, `skill_harness/routing_observation.py`, `tests/test_skill_harness.py`; configurations/snapshots `.tools/` et `.vscode/`; `docs/`, `experiments/routing/`, `outputs/`, `todo.md`, `agentic-core/skills/test-coverage-review/`, caches et fichiers `.workflow-routes.tmp`. Ils doivent être triés avant tout commit.

Le snapshot joint `file_github_repos.md` et sa copie de référence n’ont pas été modifiés; les dépôts/outils listés ne sont pas intégrés.

## Prochain plan

1. Confirmer quel clone/terminal doit recevoir la branche; ne pas pousser sans consigne.
2. Trier les modifications locales et caches, en gardant les changements utilisateur intacts; décider séparément ce qui appartient au travail de mesure.
3. Terminer ou réduire le périmètre du framework Expertise Pack à partir des critères de `plugin_migration_2.md`; vérifier les contrats d’intégration Codex sans lancer de tests runtime Codex.
4. Décider explicitement si ML-Eng v1 est le prochain pack; ne pas commencer les autres packs avant d’avoir validé ce chemin.
5. Exécuter les scénarios agentiques demandés pour les profils et les skills; publier les mesures coût/qualité plutôt qu’une estimation seule.
6. Choisir les MCP réellement nécessaires, vérifier leur déclaration et leur allowlist par agent, puis relancer le scan SCA dans un environnement Semgrep valide.
