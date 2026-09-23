from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any

from .metrics import RoutingTrial


def _events(payload: Any) -> list[Mapping[str, Any]]:
    found: list[Mapping[str, Any]] = []
    if isinstance(payload, Mapping):
        transcript = payload.get("transcript")
        if isinstance(transcript, list):
            found.extend(item for item in transcript if isinstance(item, Mapping))
        for key, value in payload.items():
            if key in {"tool_events", "events", "actions", "checkpoints"} and isinstance(value, list):
                found.extend(item for item in value if isinstance(item, Mapping))
            elif key != "transcript":
                found.extend(_events(value))
    elif isinstance(payload, list):
        for item in payload:
            found.extend(_events(item))
    return found


def _event_text(event: Mapping[str, Any]) -> str:
    return json.dumps(event, sort_keys=True).lower()


def parse_routing_observation(
    payload: Mapping[str, Any],
    *,
    expected_route: str | None,
    discovery_expected: bool,
    admission_expected: bool | None,
) -> RoutingTrial:
    events = _events(payload)
    text = " ".join(_event_text(event) for event in events)
    response = str(payload.get("final_output", payload.get("output", payload.get("response", ""))))
    combined = f"{text} {response}".lower()
    discovery_actual = any(
        event.get("type") == "skill.invoked"
        or event.get("tool_name") == "skill"
        or token in _event_text(event)
        for event in events
        for token in ("skill_invocation", "skill-invocation", '"skill":')
    )
    target_probe_indices = [
        index
        for index, event in enumerate(events)
        if event.get("type") == "tool.execution_start"
        and event.get("tool_name") == "view"
        and "/.github/skills/tdd/" in str(event.get("arguments", {}).get("path", "")).lower()
        and "__routing_probe__.md" in str(event.get("arguments", {}).get("path", "")).lower()
    ]
    generic_sentinel_indices = [
        index
        for index, event in enumerate(events)
        if "routing_eval_workflow_entry" in _event_text(event)
        or "routing_eval_accepted" in _event_text(event)
        or "routing_probe" in _event_text(event)
    ]
    sentinel_indices = target_probe_indices or generic_sentinel_indices
    sentinel_events = (
        len(target_probe_indices)
        if target_probe_indices
        else combined.count("routing_eval_workflow_entry")
        + combined.count("routing_eval_accepted")
        + combined.count("routing_probe")
    )
    admission_actual: bool | None
    if "\"status\": \"rejected\"" in combined or "status: rejected" in combined:
        admission_actual = False
    elif (
        "routing_eval_accepted" in combined
        or "status: accepted" in combined
        or "routing_probe" in combined
        or discovery_actual
    ):
        admission_actual = True
    else:
        admission_actual = None
    actual_route = None
    specialist_routes = (
        "create-agent",
        "create-skill",
        "verification-loop",
        "clarification",
        "other-skill",
        "safe-alternative",
    )
    for event in events:
        if event.get("type") != "tool.execution_start" or event.get("tool_name") != "view":
            continue
        path = str(event.get("arguments", {}).get("path", "")).lower()
        for route in specialist_routes:
            if f"/.github/skills/{route}/skill.md" in path:
                actual_route = route
                if route == "verification-loop":
                    discovery_actual = True
                break
        if actual_route is not None:
            break
    if actual_route is None:
        for route in specialist_routes:
            if f'"routing":"{route}"' in response.lower() or f'"routing": "{route}"' in response.lower():
                actual_route = route
                break
    tool_calls = len(events)
    post_sentinel_tool_calls = 0
    if sentinel_indices:
        first_sentinel = sentinel_indices[0]
        post_sentinel_tool_calls = sum(
            (
                event.get("type") == "tool.execution_start"
                if target_probe_indices
                else bool(event.get("tool_name"))
            )
            for event in events[first_sentinel + 1 :]
        )
    return RoutingTrial(
        expected_route=expected_route,
        actual_route=actual_route,
        discovery_expected=discovery_expected,
        discovery_actual=discovery_actual,
        admission_expected=admission_expected,
        admission_actual=admission_actual,
        tool_calls=tool_calls,
        tokens=int(payload.get("tokens", payload.get("token_count", 0)) or 0),
        sentinel_events=sentinel_events,
        post_sentinel_tool_calls=post_sentinel_tool_calls,
    )
