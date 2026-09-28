# PROMPT 4 — Expertise Pack `PythonDev`

- libs python modernes a checker: polars, ruff, pyscript, pandera, jax, textual, llamaindex peut etre, robyn, duckdb, les librairies intéressantes pourraient etre spécifiées dans le Agent Plugin de PythonDev, il y'aura une recherche a faire pour l'état de l'art python en terme de libs et de toolset

Implémente :

```text
PythonDev
```

comme Expertise Pack transversal.

Ne crée aucun nouvel agent.

Son objectif principal est de corriger les comportements Python datés ou trop permissifs des agents génériques.

Il doit privilégier :

```text
modern Python
typing
clear APIs
modern tooling
dependency hygiene
performance awareness
```

sans réécrire arbitrairement une codebase existante.

---

## Principe

Toujours inspecter avant de recommander :

```text
Python version
pyproject.toml
existing package manager
formatter
linter
type checker
test framework
project conventions
```

Respecter une stack intentionnelle déjà établie.

Pour un projet greenfield ou une modernisation explicitement autorisée, considérer en priorité les outils modernes adaptés au projet.

---

## Skills

Limiter v1 à 3 :

```text
modern-python-development
python-typing
python-performance
```

---

### `modern-python-development`

Couvrir :

```text
modern Python syntax
project layout
pyproject.toml
dependency management
packaging
testing conventions
documentation conventions
error handling
resource management
async/sync boundaries
```

Favoriser une toolchain moderne lorsque compatible.

Éviter d’introduire automatiquement :

```text
setup.py
requirements.txt-only workflows
legacy formatter/linter stacks
```

sur un projet greenfield moderne.

---

### `python-typing`

Invariants :

```text
public APIs typed by default
meaningful domain types
avoid Any unless justified
use Protocol/TypedDict/dataclasses/etc. when they improve semantics
preserve readability
typing should describe contracts, not create ceremony
```

Les docstrings doivent documenter :

```text
public APIs
non-obvious semantics
important invariants
side effects
exceptions when material
```

Ne pas exiger une docstring triviale sur chaque helper privé.

---

### `python-performance`

Couvrir :

```text
profiling before optimization
Python loops vs native/vectorized execution
allocation
serialization
I/O
concurrency
async
multiprocessing
NumPy/native boundaries
dataframe implementation choices
```

Ne pas appliquer de micro-optimisations sans mesure.

---

## MCP tools

Créer/exposer si possible :

```text
python.project.inspect
python.dependencies.inspect
python.lint
python.format.check
python.typecheck
python.test
python.profile
```

Ces tools peuvent encapsuler la toolchain réellement détectée dans le projet.

Ne pas imposer Ruff/uv/ty si le projet a volontairement une autre stack.

---

## Modern tooling

Sur projet compatible/greenfield, le pack doit connaître et évaluer notamment :

```text
uv
Ruff
ty
pytest
```

ainsi que les librairies modernes pertinentes pour le problème.

Mais :

```text
modern != automatically migrate
```

Toute migration doit être justifiée.

---

## Projection

Principalement :

```text
implementer
quality-assurance
reviewer
devops
```

Architect ne doit pas recevoir tout le catalogue Python.

Il peut uniquement recevoir une capability Python lorsque la décision est réellement architecture/runtime/API-related.

---

## Reviewer

PythonDev doit augmenter Reviewer sur :

```text
typing quality
API clarity
modern idioms
resource lifetime
async correctness
obvious performance anti-patterns
dependency/tooling hygiene
```

---

## QA

QA doit pouvoir utiliser :

```text
typing
lint
tests
profiling
```

comme evidence, sans devenir responsable de réparer le code.

---

## Ne PAS créer en v1

```text
django
fastapi
pydantic
numpy
pandas
polars
asyncio
pytest
packaging
```

comme skills séparées.

Ces sujets doivent rester couverts par les trois skills tant qu’un workflow spécialisé ne justifie pas son extraction.

---

## Critère final

PythonDev est réussi si :

```text
the same generic Implementer
+
PythonDev active
```

produit du Python :

```text
plus moderne
plus typé
plus explicite
mieux vérifié
plus conscient des performances
```

tout en ajoutant très peu de bruit aux workflows non-Python.

Lorsque tu as fini p4, passe à p5.md, j'avais oublié celui ci dans le prompt initial. Il propose les server mcp important a utiliser pour avoir des tools optimisés pour certains agents.
