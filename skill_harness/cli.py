from __future__ import annotations

import argparse
import json
from pathlib import Path

from .benchmark import freeze_benchmark, verify_benchmark
from .ablation import prepare_phase_0a
from .metrics import RoutingTrial, aggregate_trials
from .reports import write_metrics_json, write_metrics_markdown
from .routing import load_architecture, load_routing_spec, render_routing_variant
from .scaffold import ScaffoldConfig, scaffold_skill, validate_scaffold
from .selection import (
    ArchitectureResult,
    SelectionConstraints,
    select_architecture,
    write_canonical_architecture,
    write_selection_report,
)
from .validator import validate_skill_structure
from .waza_adapter import scaffold_waza_eval


def _path(value: str) -> Path:
    return Path(value).expanduser().resolve()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="skill-harness")
    commands = parser.add_subparsers(dest="command", required=True)

    render = commands.add_parser("render-routing")
    render.add_argument("--spec", type=_path, required=True)
    render.add_argument("--architecture", type=_path, required=True)
    render.add_argument("--output", type=_path, required=True)

    aggregate = commands.add_parser("aggregate-routing")
    aggregate.add_argument("--trials", type=_path, required=True)
    aggregate.add_argument("--json", type=_path, required=True)
    aggregate.add_argument("--markdown", type=_path)

    select = commands.add_parser("select-architecture")
    select.add_argument("--results", type=_path, required=True)
    select.add_argument("--report", type=_path, required=True)
    select.add_argument("--canonical", type=_path)
    select.add_argument("--max-false-positive-final-rate", type=float, default=0.0)
    select.add_argument("--min-false-positive-recovery-rate", type=float, default=0.0)
    select.add_argument("--min-reject-route-accuracy", type=float, default=0.0)
    select.add_argument("--max-unexpected-workflow-entry-rate", type=float, default=0.0)
    select.add_argument("--max-post-sentinel-tool-calls", type=int, default=0)

    scaffold = commands.add_parser("scaffold")
    scaffold.add_argument("--config", type=_path, required=True)
    scaffold.add_argument("--output", type=_path, required=True)
    scaffold.add_argument("--original-spec", type=_path, required=True)

    validate = commands.add_parser("validate-scaffold")
    validate.add_argument("--config", type=_path, required=True)
    validate.add_argument("--skill", type=_path, required=True)

    freeze = commands.add_parser("freeze-benchmark")
    freeze.add_argument("--root", type=_path, required=True)
    freeze.add_argument("--lock", type=_path, required=True)

    verify = commands.add_parser("verify-benchmark")
    verify.add_argument("--root", type=_path, required=True)
    verify.add_argument("--lock", type=_path, required=True)

    waza = commands.add_parser("scaffold-waza-eval")
    waza.add_argument("--skill-name", required=True)
    waza.add_argument("--output", type=_path, required=True)
    waza.add_argument("--waza-bin", type=_path, default=Path(".tools/bin/waza"))

    prepare = commands.add_parser("prepare-phase-0a")
    prepare.add_argument("--specs", type=_path, required=True)
    prepare.add_argument("--architectures", type=_path, required=True)
    prepare.add_argument("--output", type=_path, required=True)
    prepare.add_argument("--waza-bin", type=_path, default=Path(".tools/bin/waza"))
    prepare.add_argument("--source-skill", type=_path)
    prepare.add_argument("--catalogue-one", type=_path)
    prepare.add_argument("--catalogue-five", type=_path)
    prepare.add_argument("--catalogue-n", type=_path)
    prepare.add_argument("--model")
    prepare.add_argument("--allow-admission-variants", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "render-routing":
        result = render_routing_variant(
            load_routing_spec(args.spec), load_architecture(args.architecture), args.output
        )
        print(json.dumps(result, indent=2, sort_keys=True))
    elif args.command == "aggregate-routing":
        trials = [RoutingTrial(**row) for row in json.loads(args.trials.read_text(encoding="utf-8"))]
        metrics = aggregate_trials(trials)
        write_metrics_json(args.json, metrics)
        if args.markdown:
            write_metrics_markdown(args.markdown, [{"architecture_id": "aggregate", "metrics": metrics}])
    elif args.command == "select-architecture":
        payload = json.loads(args.results.read_text(encoding="utf-8"))
        results = [ArchitectureResult(row["architecture_id"], row["metrics"]) for row in payload]
        constraints = SelectionConstraints(
            args.max_false_positive_final_rate,
            args.min_false_positive_recovery_rate,
            args.min_reject_route_accuracy,
            args.max_unexpected_workflow_entry_rate,
            args.max_post_sentinel_tool_calls,
        )
        selected, report = select_architecture(results, constraints)
        write_selection_report(args.report, report)
        if selected and args.canonical:
            write_canonical_architecture(args.canonical, selected.metrics.get("architecture", {
                "architecture_id": selected.architecture_id
            }))
        if not selected:
            return 2
    elif args.command == "scaffold":
        config = ScaffoldConfig.from_file(args.config)
        summary = scaffold_skill(args.output, config, args.original_spec.read_text(encoding="utf-8"))
        print(json.dumps(summary, indent=2, sort_keys=True))
    elif args.command == "validate-scaffold":
        validate_skill_structure(args.skill, ScaffoldConfig.from_file(args.config))
    elif args.command == "freeze-benchmark":
        print(json.dumps(freeze_benchmark(args.root, args.lock).as_dict(), indent=2, sort_keys=True))
    elif args.command == "verify-benchmark":
        print(json.dumps(verify_benchmark(args.root, args.lock).as_dict(), indent=2, sort_keys=True))
    elif args.command == "scaffold-waza-eval":
        scaffold_waza_eval(args.skill_name, args.output, waza_bin=args.waza_bin)
    elif args.command == "prepare-phase-0a":
        catalogue_roots = {
            key: value
            for key, value in {
                "1-skill": args.catalogue_one,
                "5-skills": args.catalogue_five,
                "N-skills": args.catalogue_n,
            }.items()
            if value
        }
        print(json.dumps(
            prepare_phase_0a(
                args.specs,
                args.architectures,
                args.output,
                waza_bin=args.waza_bin,
                source_skill=args.source_skill,
                catalogue_roots=catalogue_roots or None,
                model=args.model,
                allow_admission_variants=args.allow_admission_variants,
            ),
            indent=2,
            sort_keys=True,
        ))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
