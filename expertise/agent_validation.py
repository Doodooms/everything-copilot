"""Target-neutral validation for Expertise agent sources."""

from __future__ import annotations

import re
from dataclasses import dataclass
from itertools import pairwise

import yaml

from .errors import TargetError

_FRONTMATTER = re.compile(r"\A---\r?\n(.*?)\r?\n---\r?\n?(.*)\Z", re.DOTALL)
_REQUIRED_SECTIONS = (
    "<routing>",
    "<critical_rules>",
    "<general_rules>",
    "<risk_assessment>",
    "<rules>",
    "<agent-skills>",
    "<workflow>",
)


def _validate_body_contract(body: str, agent_id: str) -> None:
    lines = [line.strip() for line in body.splitlines() if line.strip()]
    tags = (
        "definitions",
        "routing",
        "critical_rules",
        "general_rules",
        "risk_assessment",
        "rules",
        "agent-skills",
        "workflow",
    )
    positions: dict[str, tuple[int, int]] = {}
    for tag in tags:
        opens = [
            index for index, line in enumerate(lines) if line.casefold() == f"<{tag}>"
        ]
        closes = [
            index for index, line in enumerate(lines) if line.casefold() == f"</{tag}>"
        ]
        if tag == "definitions" and not opens and not closes:
            continue
        if len(opens) != 1 or len(closes) != 1:
            raise TargetError(
                f"agent body must contain one paired {tag} section: {agent_id}"
            )
        positions[tag] = (opens[0], closes[0])
    ordered_tags = [tag for tag in tags if tag in positions]
    if any(positions[tag][0] >= positions[tag][1] for tag in ordered_tags) or any(
        positions[left][1] >= positions[right][0]
        for left, right in pairwise(ordered_tags)
    ):
        raise TargetError(f"agent body sections are not in canonical order: {agent_id}")
    if "definitions" in positions:
        start, end = positions["definitions"]
        if end + 1 != positions["routing"][0] or not re.search(
            r"^\s*-\s+\*\*[^*]+\*\*\s*:\s+\S+",
            "\n".join(lines[start + 1 : end]),
            re.MULTILINE,
        ):
            raise TargetError(
                f"agent definitions must contain a term and precede routing: {agent_id}"
            )
    if _contains_admission_matrix(body) or re.search(
        r"^##\s+Step\s+0\b|\{[^{}]*[\"']status[\"']\s*:\s*[\"']refused[\"']",
        body,
        re.IGNORECASE | re.MULTILINE,
    ):
        raise TargetError(
            f"agent body contains a prohibited admission contract: {agent_id}"
        )

    def content(tag: str) -> str:
        start, end = positions[tag]
        return "\n".join(lines[start + 1 : end])

    routing = content("routing")
    routing_lines = [line.strip() for line in routing.splitlines() if line.strip()]
    accept_positions = [
        index for index, line in enumerate(routing_lines) if line == "## ACCEPT"
    ]
    reject_positions = [
        index for index, line in enumerate(routing_lines) if line == "## REJECT"
    ]
    if (
        len(accept_positions) != 1
        or len(reject_positions) != 1
        or accept_positions[0] >= reject_positions[0]
    ):
        raise TargetError(
            f"agent routing must have one ordered ACCEPT and REJECT section: {agent_id}"
        )
    accept_items = routing_lines[accept_positions[0] + 1 : reject_positions[0]]
    reject_items = routing_lines[reject_positions[0] + 1 :]
    reject_bullets = [line for line in reject_items if re.match(r"^-\s+\S", line)]
    if (
        not any(re.match(r"^-\s+\S", line) for line in accept_items)
        or not reject_bullets
        or any(
            not re.search(r"→\s*`[a-z0-9]+(?:-[a-z0-9]+)*`", line)
            for line in reject_bullets
        )
    ):
        raise TargetError(
            f"agent routing must define accepted and routed rejected work: {agent_id}"
        )
    for tag, marker in (
        ("critical_rules", r"MUST(?:\s+NOT)?"),
        ("general_rules", r"(?:SHOULD(?:\s+NOT)?|MAY)"),
    ):
        block = content(tag)
        if not re.search(r"^\s*-\s+\S+", block, re.MULTILINE) or not re.search(
            rf"\b{marker}\b", block
        ):
            raise TargetError(
                f"agent {tag} section lacks its required bullet policy: {agent_id}"
            )
    risk = content("risk_assessment")
    if agent_id == "orchestrator":
        if (
            not all(re.search(rf"\bL{level}\b", risk) for level in range(4))
            or not all(
                re.search(term, risk, re.IGNORECASE)
                for term in (r"impact", r"reversib", r"security|data", r"uncertainty")
            )
            or "record" not in risk.casefold()
        ):
            raise TargetError(
                f"orchestrator risk assessment must record L0-L3: {agent_id}"
            )
    elif not all(
        term in risk.casefold() for term in ("risk_level", "downgrade", "escalat")
    ):
        raise TargetError(
            f"specialist risk assessment must preserve and escalate the assigned risk: {agent_id}"
        )

    rules = content("rules")
    required_headings = (
        "## Role",
        "## Responsibilities",
        "## Constraints",
        "## Output Contract",
    )
    if any(rules.count(heading) != 1 for heading in required_headings):
        raise TargetError(
            f"agent rules must contain role, responsibilities, constraints, and output contract: {agent_id}"
        )
    if list(map(rules.index, required_headings)) != sorted(
        map(rules.index, required_headings)
    ):
        raise TargetError(f"agent rule sections are out of order: {agent_id}")
    if not re.search(r"^\s*-\s+\S+", content("agent-skills"), re.MULTILINE):
        raise TargetError(f"agent skill policy must contain an instruction: {agent_id}")
    workflow = content("workflow")
    step_pattern = r"^##\s+Step\s+(\d+)\s+-\s+.+$"
    step_headings = re.findall(step_pattern, workflow, re.MULTILINE)
    all_step_headings = re.findall(step_pattern, "\n".join(lines), re.MULTILINE)
    if step_headings != ["1", "2", "3"] or all_step_headings != ["1", "2", "3"]:
        raise TargetError(f"agent workflow must contain ordered Steps 1-3: {agent_id}")
    step_one_body = workflow.split("## Step 2", 1)[0]
    step_one_pattern = (
        r"risk(?:[_ -]assessment)?|assurance"
        if agent_id == "orchestrator"
        else r"risk_level"
    )
    if not re.search(step_one_pattern, step_one_body, re.IGNORECASE):
        raise TargetError(
            f"agent workflow Step 1 must address assigned risk: {agent_id}"
        )
    if (
        "<role>" in {line.casefold() for line in lines}
        or "</role>" in {line.casefold() for line in lines}
        or "# Role" in content("rules").splitlines()
    ):
        raise TargetError(
            f"agent body must use the canonical rules Role heading: {agent_id}"
        )


def _contains_admission_matrix(body: str) -> bool:
    lines = body.splitlines()
    for index, line in enumerate(lines):
        if re.match(r"^\s{0,3}#{1,6}\s+.*\badmission matrix\b", line, re.IGNORECASE):
            return True
        if "|" not in line:
            continue
        headers = [
            cell.strip().strip("`*_ ").upper()
            for cell in line.strip().strip("|").split("|")
        ]
        if not any("REQUEST SHAPE" in cell for cell in headers) or not any(
            re.fullmatch(r"INVOKE\??", cell) for cell in headers
        ):
            continue
        has_yes = has_no = False
        for row in lines[index + 1 :]:
            if "|" not in row:
                break
            cells = {
                cell.strip().strip("`*_ ").upper()
                for cell in row.strip().strip("|").split("|")
            }
            has_yes |= "YES" in cells
            has_no |= "NO" in cells
            if has_yes and has_no:
                return True
    return False


@dataclass(frozen=True)
class AgentSource:
    metadata: dict[str, object]
    body: str


def validate_agent_semantics(
    content: bytes, agent_id: str, source_name: str
) -> AgentSource:
    """Check identity and required role/routing/body contract without host assumptions."""
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise TargetError(f"agent source is not valid UTF-8: {source_name}") from exc
    match = _FRONTMATTER.match(text.replace("\r\n", "\n"))
    if match is None:
        raise TargetError(f"agent source is missing YAML frontmatter: {source_name}")
    try:
        metadata = yaml.safe_load(match.group(1))
    except yaml.YAMLError as exc:
        raise TargetError(f"agent frontmatter is invalid: {source_name}") from exc
    if not isinstance(metadata, dict):
        raise TargetError(f"agent frontmatter must be a mapping: {source_name}")
    body = match.group(2).strip()
    if metadata.get("name") != agent_id:
        raise TargetError(f"agent name must match contribution ID: {agent_id}")
    if (
        not isinstance(metadata.get("description"), str)
        or not metadata["description"].strip()
    ):
        raise TargetError(f"agent description must be non-empty: {agent_id}")
    if not body:
        raise TargetError(f"agent body is empty: {agent_id}")
    if not all(section in body for section in _REQUIRED_SECTIONS):
        raise TargetError(
            f"agent body is missing required role or workflow sections: {agent_id}"
        )
    _validate_body_contract(body, agent_id)
    for clause in ("WHAT:", "INVOKE FOR:", "DO NOT INVOKE FOR:"):
        if clause.casefold() not in metadata["description"].casefold():
            raise TargetError(f"agent description is missing {clause}: {agent_id}")
    return AgentSource(metadata=metadata, body=body)
