# scripts/validate_skill.py
from pathlib import Path
import re
import sys
import yaml
import typer

app = typer.Typer()

def read_frontmatter(path: Path):
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return None, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None, text
    fm_text = parts[1]
    rest = parts[2]
    try:
        fm = yaml.safe_load(fm_text)
    except Exception:
        return None, text
    return fm, text

@app.command()
def validate(skill_dir: Path = Path(".")):
    skill_dir = skill_dir.resolve()
    md = skill_dir / "SKILL.md"
    if not md.exists():
        typer.echo(f"ERROR: SKILL.md not found in {skill_dir}")
        raise typer.Exit(code=2)

    fm, full_text = read_frontmatter(md)
    errors = []
    warnings = []

    # frontmatter
    if not fm:
        errors.append("Missing or invalid YAML frontmatter in SKILL.md")
    else:
        for k in ("name", "description", "user-invocable"):
            if k not in fm:
                errors.append(f"Missing frontmatter key: {k}")
        if "name" in fm and fm["name"] != skill_dir.name:
            warnings.append(f"Frontmatter name '{fm.get('name')}' != folder name '{skill_dir.name}'")

    # length
    lines = full_text.splitlines()
    if len(lines) > 500:
        warnings.append(f"SKILL.md is {len(lines)} lines (recommended <500)")

    # assets existence
    assets = skill_dir / "assets"
    if not assets.exists() or not any(assets.iterdir()):
        warnings.append("No files in `assets/` — include at least one template")

    # references existence
    refs = skill_dir / "references"
    if not refs.exists() or not any(refs.iterdir()):
        warnings.append("No files in `references/` — include docs or examples")

    # file references (#file:) and tool references (#tool:)
    file_refs = re.findall(r"#file:\s*([^\s`]+)", full_text)
    for fr in file_refs:
        p = (skill_dir / fr).resolve() if fr.startswith("./") or fr.startswith("../") else (skill_dir / fr)
        # ensure reference is not deeper than one level from SKILL.md (e.g., ./assets/foo.md is ok)
        parts = Path(fr).parts
        if len(parts) > 2 and not fr.startswith("./"):
            warnings.append(f"#file reference appears deep: {fr}")
        # existence check (best-effort)
        candidate = skill_dir.joinpath(fr.lstrip("./"))
        if not candidate.exists():
            warnings.append(f"#file reference not found (best-effort): {fr}")

    tool_refs = re.findall(r"#tool:([^\s`]+)", full_text)
    if not tool_refs:
        warnings.append("No `#tool:` references found; ensure you reference required tools (e.g., #tool:vscode/askQuestions)")

    # summary
    if errors:
        typer.echo("ERRORS:")
        for e in errors:
            typer.echo(f"  - {e}")
    if warnings:
        typer.echo("WARNINGS:")
        for w in warnings:
            typer.echo(f"  - {w}")
    if errors:
        raise typer.Exit(code=3)
    typer.echo("Validation passed (warnings may need attention).")
    raise typer.Exit(code=0)

if __name__ == '__main__':
    app()