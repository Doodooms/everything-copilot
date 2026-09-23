# create-skill benchmark

This benchmark is generated from `benchmark_manifest.json`. It evaluates create-skill as a meta-skill: the primary output is a high-quality skill package, and the application tasks test whether that package would give another agent enough structure to build a coherent project.

## Benchmark: what it evaluates

- `skill-*` (`authoring-contract`): authoring semantics, ontology, contract, canonical grouped-list topology, and original-spec provenance.
- `probe-support-file-discipline`, `probe-review-and-checklist`, `probe-scripts-validation`, and `probe-repair-recovery`: explicit support-file, point-of-need review, executable repair, and stale-package recovery families.
- `app-*` (`downstream-guidance`): downstream project guidance quality for bounded application requests, including domain modeling, implementation workflow, security, failure handling, acceptance criteria, and verification gates. These tasks judge the generated skill; current adapters do not execute a second downstream project.
- `reject-*-near-miss` (`routing-near-miss`): routing and refusal quality for requests owned by agents, prompts, MCP servers, hooks, direct application implementation, or benchmark optimization.
- `train`: broad optimization signal covering all manifest skills plus representative applications.
- `selection`: held-in optimization selection signal with representative skills, applications, and near misses.
- `holdout`: unseen application domains used only for final generalization checks; it is excluded from SkillOpt configuration.

Waza task files use the standard task schema. Adapter-only contract metadata is stored in each split's `adapter_manifest.json` and is executed by the local SkillOpt/Waza adapter before Waza runs: package shape, declared frozen support files, provenance, script self-containment, and routing metadata are deterministic hard gates. `support_files_optimized: false` explicitly records that SkillOpt changes only SKILL.md; assets, references, and scripts remain frozen fixtures. Near-miss result text receives a deterministic post-Waza routing gate. Application tasks judge package guidance only; downstream project execution is unavailable. Freeze this directory before optimization.
