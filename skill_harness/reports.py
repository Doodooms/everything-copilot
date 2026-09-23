from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def write_metrics_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_metrics_markdown(path: Path, rows: list[dict[str, Any]]) -> None:
    lines = [
        "# Routing Ablation Results",
        "",
        "| Architecture | Discovery F1 | Admission F1 | Reject route accuracy | Tokens mean |",
        "|---|---:|---:|---:|---:|",
    ]
    for row in rows:
        metrics = row.get("metrics", row)
        lines.append(
            "| {id} | {discovery:.3f} | {admission:.3f} | {route:.3f} | {tokens:.1f} |".format(
                id=row.get("architecture_id", "unknown"),
                discovery=metrics.get("discovery", {}).get("f1", 0.0),
                admission=metrics.get("admission", {}).get("f1", 0.0),
                route=metrics.get("reject_route_accuracy", 0.0),
                tokens=metrics.get("tokens", {}).get("mean", 0.0),
            )
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
