# Routing Ablation

## Local checkpoint (2026-09-27)

All six architecture JSON candidates and the `tdd` routing specification were
parsed, and each candidate rendered successfully to a temporary directory
outside the repository with `skill_harness render-routing`. This is fixture
generation only; it does not validate the real TDD skill package. The existing
preparation recipe still points to `.github/skills/tdd`, which is absent from
this checkout, so Waza behavioral trials, transcripts, metrics, and
architecture selection were not produced. Phase 0A/0B remain unmeasured;
preserve the candidates without treating any one as a winner.

This directory contains the fixed semantic fixtures and six architecture
candidates. The three `phase-0a-*.json` files are the Phase 0A candidates;
they are experiment inputs, not a preselected winner. Additional user-defined
candidates may be added as separate JSON files.

## What an architecture JSON means

An architecture JSON describes only the routing structure to render:

```json
{
  "id": "phase-0a-deferred",
  "progressive_disclosure": "deferred_workflow",
  "admission_representation": "grouped_lists",
  "workflow_location": "references/workflow.md"
}
```

`progressive_disclosure` selects the Phase 0A organization. `admission_representation` is fixed to `grouped_lists` during Phase 0A and changes only during Phase 0B. `workflow_location` records the expected location and is not a free-form prompt.

## Phase 0A

Compare progressive-disclosure variants while keeping admission representation fixed:

The current real target is `tdd`. Its five routing prompts live in
`specs/tdd.json`; they are not five synthetic skills. Each architecture is
prepared against three real catalogues:

- `1-skill`: `/home/pm/projets-persos/test-1-skill`
- `5-skills`: `/home/pm/projets-persos/test-5-skills`
- `N-skills`: the main workspace catalogue

Render the real target under all 3 Phase 0A candidates and all 3 catalogue
sizes:

The preparation command below only renders skills, creates isolated Waza evals,
and writes `preparation.json`; it never runs a model trial:

```bash
PYTHONPATH=. .venv/bin/python -m skill_harness prepare-phase-0a \
  --specs experiments/routing/specs \
  --architectures experiments/routing/architectures \
  --source-skill .github/skills/tdd \
  --catalogue-one /home/pm/projets-persos/test-1-skill \
  --catalogue-five /home/pm/projets-persos/test-5-skills \
  --catalogue-n . \
  --model gpt-5.6-luna \
  --output /tmp/routing-ablation \
  --waza-bin "$PWD/.tools/bin/waza"
```

The generated workspaces stay outside the repository's `.github/skills/`
directory.

```bash
render_root="$(mktemp -d /tmp/routing-ablation-renders.XXXXXX)"
for architecture in experiments/routing/architectures/phase-0a-*.json; do
  id=$(basename "$architecture" .json)
  for spec in experiments/routing/specs/*.json; do
    sid=$(basename "$spec" .json)
    PYTHONPATH=. python3 -m skill_harness render-routing \
      --spec "$spec" \
      --architecture "$architecture" \
      --output "$render_root/$id/$sid"
  done
done
```

For each isolated candidate workspace, first create the official Waza scaffold, replace its generic tasks with the prompts from the matching `specs/*.json`, set `config.inject_skill_body: false`, and verify it:

```bash
cd /tmp/routing-ablation/workspace
../../repo/.tools/bin/waza new eval <skill-name> --output eval.yaml
PYTHONPATH=../../repo python3 -m skill_harness ... # enrich tasks with fixture prompts and sentinel assertions
../../repo/.tools/bin/waza spec verify \
  --skill .github/skills/<skill-name> \
  --eval eval.yaml --format json
```

For this routing-only suite, `spec verify` is diagnostic: it checks textual
skill requirements, while routing correctness comes from actual invocation,
sentinel, rejection, and tool-trace observations after a Waza run. Do not use
`--fail` as the Phase 0 gate for these fixtures.

The generic scaffold is not a complete ablation suite: it must be enriched before rollout. Run the resulting Waza eval with multiple cheap trials:

```bash
.tools/bin/waza run <eval.yaml> --trials 5 --output experiments/routing/results/<run>.json \
  --transcript-dir experiments/routing/results/<run>-transcripts
```

## Analysis and selection

Convert collected trial rows to metrics, then apply hard constraints before ranking:

```bash
PYTHONPATH=. python3 -m skill_harness aggregate-routing \
  --trials <trials.json> \
  --json experiments/routing/results/metrics.json \
  --markdown experiments/routing/results/report.md

PYTHONPATH=. python3 -m skill_harness select-architecture \
  --results <architecture-results.json> \
  --report experiments/routing/results/selection.json
```

The selection command returns exit code `2` when no architecture satisfies the configured constraints. It never chooses a default architecture.

## Phase 0B

After Waza results select a Phase 0A architecture under hard constraints, provide only the Phase 0B admission representation variants (`grouped_lists`, `markdown_table`, and optionally `compact_rules`) and rerun the same process with progressive disclosure held constant. Persist the final user-approved winner as the canonical configuration. Only then should `create-skill` and `optimize-skill` be used.

## Approval gates

1. Preparation: render and verify all candidates without model calls.
2. Phase 0A: run Waza trials and inspect the comparative report.
3. Phase 0B: run representation trials only after Phase 0A approval.
4. Canonicalization: persist the selected architecture after user approval.
5. Optimization: create the frozen benchmark, run S0/SkillOpt/S* and holdout.

The real TDD target and its five fixed routing cases are under `specs/tdd.json`.
The source skill is copied from `.github/skills/tdd`; the source package is never
mutated by preparation.

Waza smoke protocol note: the installed Waza `0.38.7` currently creates an
empty temporary workspace for these evals even when `--context-dir` points at a
fixture catalogue. Do not treat token usage or routing outcomes as valid until
the transcript shows the target `SKILL.md` being discovered. The prepared
matrix is safe to keep, but Phase 0A rollout is blocked on that mount issue.
