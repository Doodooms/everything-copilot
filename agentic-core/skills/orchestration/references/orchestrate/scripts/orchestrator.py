# /// script
# requires-python = ">=3.11"
# ///
"""Propose a repository-approved branch name from task semantics."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import unicodedata
from pathlib import Path
from typing import Any

BRANCH_POLICY_PATH = ".agentic-core/branch-naming.json"
FALLBACK_BRANCH_PREFIXES = {
    "feature": "feat",
    "bugfix": "fix",
    "refactor": "refactor",
    "test": "test",
    "docs": "docs",
    "maintenance": "chore",
}
PRIMARY_EFFECT_ALIASES = {
    "feature": "feature",
    "bugfix": "bugfix",
    "defect": "bugfix",
    "refactor": "refactor",
    "test": "test",
    "verification": "test",
    "docs": "docs",
    "documentation": "docs",
    "maintenance": "maintenance",
    "release": "release",
    "hotfix": "hotfix",
}
BRANCH_SLUG_RE = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")


class BranchPolicy:
    """Validated branch policy and bounded source provenance."""

    def __init__(
        self,
        prefixes: dict[str, str],
        special: dict[str, bool],
        provenance: dict[str, str],
    ) -> None:
        self.prefixes = prefixes
        self.special = special
        self.provenance = provenance


def _validate_branch_policy(document: Any, *, source: str, digest: str) -> BranchPolicy:
    if not isinstance(document, dict) or set(document) != {
        "version",
        "ordinary_prefixes",
        "special",
    }:
        raise ValueError(
            "branch policy must contain version, ordinary_prefixes, and special"
        )
    if type(document["version"]) is not int or document["version"] != 1:
        raise ValueError("unsupported branch policy version")
    prefixes = document["ordinary_prefixes"]
    if not isinstance(prefixes, dict) or set(prefixes) != set(FALLBACK_BRANCH_PREFIXES):
        raise ValueError(
            "ordinary_prefixes must define the six supported effect categories"
        )
    for prefix in prefixes.values():
        if (
            not isinstance(prefix, str)
            or not re.fullmatch(r"[a-z][a-z0-9-]{0,31}", prefix)
            or prefix in {"release", "hotfix", "archive"}
        ):
            raise ValueError(f"invalid ordinary branch prefix: {prefix!r}")
    if len(set(prefixes.values())) != len(prefixes):
        raise ValueError("ordinary branch prefixes must be unique")
    special = document["special"]
    if not isinstance(special, dict) or set(special) != {"release", "hotfix"}:
        raise ValueError("special must define release and hotfix")
    if any(not isinstance(enabled, bool) for enabled in special.values()):
        raise ValueError("special branch settings must be booleans")
    return BranchPolicy(
        prefixes=dict(prefixes),
        special=dict(special),
        provenance={
            "policy_source": source,
            "policy_version": "1",
            "policy_sha256": digest,
        },
    )


def _branch_policy_digest(document: dict[str, Any]) -> str:
    canonical = json.dumps(
        document, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def load_branch_policy(repo_root: str | Path) -> BranchPolicy:
    """Load a repository override, or the deterministic built-in policy."""
    root = Path(repo_root).resolve()
    path = root / BRANCH_POLICY_PATH
    if not path.exists() and not path.is_symlink():
        document = {
            "version": 1,
            "ordinary_prefixes": FALLBACK_BRANCH_PREFIXES,
            "special": {"release": True, "hotfix": True},
        }
        return _validate_branch_policy(
            document,
            source="built_in_fallback",
            digest=_branch_policy_digest(document),
        )
    raw = path.read_bytes()
    try:
        document = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"invalid branch policy at {path}: {exc}") from exc
    return _validate_branch_policy(
        document,
        source=BRANCH_POLICY_PATH,
        digest=_branch_policy_digest(document),
    )


def classify_primary_effect(primary_effect: str) -> str:
    """Normalize a structured task effect; ambiguous prose is not guessed."""
    if not isinstance(primary_effect, str):
        raise TypeError("primary effect must be a structured category string")
    try:
        return PRIMARY_EFFECT_ALIASES[primary_effect.strip().casefold()]
    except KeyError as exc:
        raise ValueError(
            f"unsupported primary effect: {primary_effect!r}; choose one of "
            f"{', '.join(sorted(PRIMARY_EFFECT_ALIASES))}"
        ) from exc


def derive_branch_slug(title: str, *, max_length: int = 60) -> str:
    """Create a stable lowercase kebab slug from a human task title."""
    if not isinstance(title, str):
        raise TypeError("branch title must be text")
    normalized = unicodedata.normalize("NFKD", title.casefold())
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_text).strip("-")
    slug = slug[:max_length].rstrip("-")
    if not slug or not BRANCH_SLUG_RE.fullmatch(slug):
        raise ValueError("task title does not produce a valid branch slug")
    return slug


def validate_branch_name(branch_name: str, policy: BranchPolicy) -> dict[str, Any]:
    """Positively validate ordinary and policy-approved special branch names."""
    if not isinstance(branch_name, str) or branch_name.startswith("archive/"):
        raise ValueError("branch name is not permitted by the active branch policy")
    if branch_name.startswith("release/"):
        version = branch_name.removeprefix("release/")
        valid = policy.special["release"] and bool(
            re.fullmatch(
                r"v(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)",
                version,
            )
        )
        if valid:
            return {"valid": True, "category": "release"}
        raise ValueError("release branches must use release/vMAJOR.MINOR.PATCH")
    if branch_name.startswith("hotfix/"):
        slug = branch_name.removeprefix("hotfix/")
        if (
            policy.special["hotfix"]
            and len(slug) <= 60
            and BRANCH_SLUG_RE.fullmatch(slug)
        ):
            return {"valid": True, "category": "hotfix"}
        raise ValueError("hotfix branch is not permitted or has an invalid slug")
    if branch_name.count("/") != 1:
        raise ValueError("branch name must have one allowlisted prefix and one slug")
    prefix, slug = branch_name.split("/", 1)
    if (
        prefix not in policy.prefixes.values()
        or len(slug) > 60
        or not BRANCH_SLUG_RE.fullmatch(slug)
    ):
        raise ValueError("branch name is not permitted by the active branch policy")
    return {
        "valid": True,
        "category": next(k for k, v in policy.prefixes.items() if v == prefix),
    }


def propose_branch(
    *,
    repo_root: str | Path,
    title: str,
    primary_effect: str,
    host_suggestion: str | None = None,
    special_name: str | None = None,
) -> dict[str, Any]:
    """Derive a new branch from task semantics, never from host identity/suggestion."""
    del host_suggestion
    policy = load_branch_policy(repo_root)
    category = classify_primary_effect(primary_effect)
    if category == "release":
        if not special_name:
            raise ValueError(
                "release proposals require an explicit --special-name version"
            )
        version = special_name.strip()
        branch_name = f"release/{version}"
    elif category == "hotfix":
        slug = derive_branch_slug(special_name or title)
        branch_name = f"hotfix/{slug}"
    else:
        slug = derive_branch_slug(title)
        branch_name = f"{policy.prefixes[category]}/{slug}"
    validation = validate_branch_name(branch_name, policy)
    provenance = {
        **policy.provenance,
        "category": category,
        "validation": "accepted",
    }
    return {
        "branch": branch_name,
        "category": category,
        "validated": validation["valid"],
        "provenance": provenance,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Propose a branch name from task semantics and repository policy."
    )
    parser.add_argument("--repo-root", required=True, type=Path)
    parser.add_argument("--title", required=True)
    parser.add_argument("--primary-effect", required=True)
    parser.add_argument("--host-suggestion")
    parser.add_argument("--special-name")
    args = parser.parse_args(argv)
    if not args.repo_root.is_absolute():
        parser.error("--repo-root must be an absolute path")
    proposal = propose_branch(
        repo_root=args.repo_root,
        title=args.title,
        primary_effect=args.primary_effect,
        host_suggestion=args.host_suggestion,
        special_name=args.special_name,
    )
    print(json.dumps(proposal, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
