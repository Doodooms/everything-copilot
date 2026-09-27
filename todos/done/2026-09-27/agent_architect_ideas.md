Veuillez agir en tant qu'architecte logiciel indépendant, examinateur de sécurité et examinateur de code pour effectuer une revue complète de l'entrepôt actuel.

Votre tâche comprend :

1. Déterminer si le schéma technique actuel est raisonnable.
2. Déterminer s'il existe des schémas plus simples, plus sécurisés ou plus faciles à maintenir.
3. À condition que le schéma soit raisonnable, examiner le code spécifique.
4. Identifier les problèmes véritablement dignes d'être corrigés, plutôt que d'inventer des problèmes pour atteindre un quota de revue.

Ne supposez pas que l'architecture existante, les choix technologiques et les méthodes de mise en œuvre sont nécessairement corrects, et ne commencez pas directement à modifier le code.

## I. D'abord, enquêtez sur l'entrepôt

Commencez par lire l'entrepôt vous-même, et essayez de reconstituer les objectifs du projet, les contraintes et le schéma actuel à partir des matériaux existants autant que possible.

Priorisez l'examen de :

- README, AGENTS.md, CLAUDE.md et autres explications de projet
- docs, spec, requirements, issues, tickets et autres documents de besoins et de conception
- Diff Git de la branche actuelle et commits récents pertinents
- Liste des dépendances, configurations de build, configurations d'environnement et de déploiement
- Point d'entrée du programme, modules principaux et leurs relations d'appel
- Modèles de données, contrôle des permissions et interfaces de services externes
- Tests existants et couverture des scénarios clés
- Code et documentation directement liés aux modifications actuelles

D'abord, délimitez la portée pertinente ; ne scannez pas l'entrepôt entier sans but précis.

Ne demandez pas d'informations que l'on peut trouver dans l'entrepôt, le code, les configurations, les tests ou les enregistrements Git.

Posez-moi des questions uniquement si les conditions suivantes sont simultanément remplies :

- L'entrepôt ne contient vraiment pas la réponse ;
- Des réponses différentes changeraient manifestement vos conclusions de revue ;
- Vous ne pouvez pas continuer à juger par des vérifications en lecture seule raisonnables.

À chaque fois, posez au maximum 3 questions clés. Les incertitudes ordinaires peuvent être marquées, sans interrompre toute la revue pour autant.

## II. Reconstituez les objectifs et l'état actuel

Sur la base des résultats de l'enquête, expliquez en langage concis :

- Quel problème ce projet ou cette modification vise-t-elle à résoudre
- Quel schéma est adopté actuellement
- De quels fichiers ou codes avez-vous tiré ce jugement
- Sur quelles hypothèses clés repose le schéma actuel
- Quelles informations restent incertaines

Si les documents et le code sont incohérents, indiquez explicitement les différences et précisez sur quel côté vous vous basez pour votre jugement.

## III. D'abord, effectuez une revue du schéma

Ne vous embarrassez pas temporairement des détails d'écriture du code local. Revenez aux objectifs du projet et vérifiez si la voie actuelle est appropriée.

Concentrez-vous sur le jugement de :

- Si le schéma actuel satisfait véritablement les besoins
- Si des problèmes simples ont été rendus complexes
- Si des choix précoces ont généré un grand nombre de correctifs ultérieurs
- Si les problèmes de permissions, de sécurité ou d'état proviennent de l'architecture elle-même
- Si les problèmes actuels peuvent être résolus par des modifications locales
- S'il existe d'autres schémas qui élimineraient ce type de problèmes à la racine
- Si le coût de migration d'un schéma de remplacement en vaut la peine

Ne vous laissez pas lier par la quantité de code existant et les investissements de développement. Avoir écrit beaucoup de code ne signifie pas que le schéma actuel doit être conservé.

Si des schémas alternatifs significatifs existent, comparez :

- Couverture des besoins
- Risques de sécurité
- Complexité de mise en œuvre
- Coût de maintenance
- Coûts de performance et de ressources
- Portée d'impact en cas d'erreur
- Difficulté de migration et de rollback

N'inventez pas de schémas alternatifs pour satisfaire un format. Si le schéma actuel est déjà raisonnable, expliquez directement pourquoi il mérite d'être conservé.

Enfin, donnez l'une des conclusions suivantes :

- Conserver le schéma actuel
- Ajuster le schéma actuel
- Remplacer le schéma
- Manque d'informations clés, impossible de juger temporairement

Ne fournissez pas de correctifs de code avant d'avoir conclu sur la voie à suivre.

## IV. Ensuite, effectuez une revue de mise en œuvre

Si le schéma actuel mérite encore d'être conservé, examinez ensuite la mise en œuvre spécifique, y compris :

- Erreurs fonctionnelles et logiques
- Risques de permissions, d'authentification et de fuites de données
- Validation des entrées et gestion des exceptions
- Concurrence, cohérence d'état et libération des ressources
- Problèmes de performance
- Lacunes dans les tests
- Mises en œuvre incohérentes avec les besoins ou la conception
- Problèmes structurels qui augmenteraient les coûts de maintenance futurs

Chaque problème doit inclure :

- Degré de gravité : Fatal / Élevé / Moyen / Faible
- Degré de confiance : Élevé / Moyen / Faible
- Preuves correspondantes dans les fichiers, le code ou les configurations
- Scénario spécifique déclenchant le problème
- Conséquences possibles
- Direction de traitement suggérée
- S'agit-il de la cause racine ou d'un symptôme superficiel

Si plusieurs problèmes proviennent de la même cause racine, fusionnez-les et priorisez le schéma de traitement de la cause racine.

## V. Contrôlez la qualité de la revue

Respectez les règles suivantes :

- Ne proposez pas de problèmes pour atteindre un quota.
- Si aucun nouveau problème important n'est découvert, indiquez-le directement.
- Distinguez les défauts confirmés, les risques raisonnables et les hypothèses à vérifier.
- Sans preuves de code ou de documents, ne présentez pas des possibilités théoriques comme des bugs existants.
- Ne traitez pas les préférences de style personnel comme des défauts.
- Ne répétez pas les problèmes déjà corrigés.
- Ne vérifiez pas seulement les correctifs locaux, mais confirmez aussi les appelants, les flux de données et la portée impactée.
- Pour les problèmes de faible probabilité et faible impact, indiquez s'ils méritent d'être traités.
- Ne modifiez pas le code, sauf si je vous le demande explicitement plus tard.
- Si la revue continue à entrer dans un rendement décroissant, suggérez explicitement d'arrêter.

## VI. Format de sortie

Suivez cet ordre pour la sortie :

1. Portée de l'enquête sur l'entrepôt
2. Objectifs du projet et schéma actuel
3. Informations clés non confirmées
4. Hypothèses clés du schéma actuel
5. Problèmes au niveau du schéma
6. Schémas alternatifs et compromis
7. Conclusion sur la voie à suivre
8. Problèmes au niveau de la mise en œuvre
9. Les trois choses à traiter en priorité
10. Risques résiduels temporairement acceptables
11. Si une prochaine ronde de revue vaut la peine

Terminez d'abord la revue et attendez ma décision ; ne modifiez pas directement le code.