# Communication avec les sessions Codex locales

Vérifié le 2026-09-27 avec Codex CLI 0.157.1.

## Parcourir les sessions

- `codex agents` ouvre le navigateur interactif des sessions du daemon local Codex. Il expose les noms, statuts, projets et un aperçu du dernier message.
- En environnement sans terminal, `codex agents --no-alt-screen` échoue avec `ERROR: stdin is not a terminal`.
- Un pseudo-terminal (`script`) permet de rendre le navigateur visible. Le navigateur est interactif; arrêter uniquement le processus du navigateur après lecture, jamais la session Codex elle-même.
- Depuis un terminal interactif utilisateur, lancer simplement `codex agents`.

## Envoyer une demande courte à une session

`codex queue --thread "<nom exact ou UUID>" --message "<demande>"` met un message en file pour une session existante. Utiliser le nom exact relevé dans `codex agents`; demander une réponse courte et préciser « ne modifie aucun fichier » pour un simple point d’état.

Test effectué:

- Session : `Finaliser cost-eval-opt`, projet `agentic-workflow`.
- Message : demande d’un état en 1–2 phrases, sans lancer de travail ni modifier de fichiers.
- La CLI a confirmé la mise en file pour le thread `01a0dfa7-e419-7f31-a036-1d3d7514332b` (message `01a0dfca-e2ba-74f3-9355-f1f32b87543a`).
- **Limite :** l’accusé « Queued message » confirme seulement que le daemon a accepté le message; il ne prouve pas que Codex l’a consommé ni qu’une réponse a été produite. Vérifier ensuite le statut et le dernier message avec `codex agents`. Ne pas lancer `codex resume` pour une simple demande, car cela reprend la session.

## Dernier état observé

Au moment du contrôle, le navigateur affichait `Finaliser cost-eval-opt` comme `Inactive` (36 min). Son dernier message indiquait qu’il préparait l’évaluation comportementale et un seul smoke Codex borné, sans appel Copilot ni tests unitaires séparés. Il précisait que le plugin était actif pour les nouveaux processus Codex, tandis que la conversation en cours conservait son runtime initial.

Ce statut peut être périmé; il ne permet pas d’affirmer que la session travaille actuellement. Le registre Copilot/VS Code ne montrait pas cette session; le daemon local Codex et `codex queue` constituent ici le pont inter-harness vérifié.
