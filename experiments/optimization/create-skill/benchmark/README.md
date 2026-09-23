# create-skill benchmark

This benchmark is generated from `benchmark_manifest.json`. It evaluates create-skill as a meta-skill: the primary output is a high-quality skill package, and the application tasks test whether that package would give another agent enough structure to build a coherent project.

## Benchmark: what it evaluates

- `skill-*`: authoring quality across domains, including ontology, semantic contract, acceptance criteria, rejection boundaries, canonical topology, provenance, self-contained support files, validation, and user review.
- `app-*`: downstream project guidance quality for a bounded application request, including domain modeling, implementation workflow, security, failure handling, acceptance criteria, and verification gates. These tasks inspect the generated skill; they do not yet execute a second project with it.
- `reject-*-near-miss`: routing and refusal quality for requests that belong to agents, prompts, MCP servers, hooks, or direct application implementation rather than create-skill.
- `train`: broad optimization signal covering all manifest skills plus representative applications.
- `selection`: held-in optimization selection signal with representative skills, applications, and near misses.
- `holdout`: unseen application domains used only for final generalization checks; it is excluded from SkillOpt configuration.

The Waza prompt grader scores ontology, semantic contract and boundaries, topology and provenance, executable workflow, self-contained support-file discipline, validation and review evidence, downstream implementation utility, and failure/security/verification coverage. Efficiency remains a secondary bounded-action metric. Freeze this directory before optimization.
