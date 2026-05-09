"""
Post-tool-use hook: warns the agent if a just-edited Python file
contains blocking I/O patterns that violate conventions.

Input (stdin): JSON with tool_name and tool_input fields.
Output (stdout): JSON systemMessage if violations found, empty otherwise.
Exit code: 0 always (non-blocking warning only).
"""
import json
import os
import sys
import re

BLOCKING_PATTERNS = [
    (r"\bimport requests\b", "import requests — use aiohttp.ClientSession instead"),
    (r"\brequests\.(get|post|put|delete|patch|head)\(", "requests.* call — use aiohttp.ClientSession instead"),
    (r"\btime\.sleep\(", "time.sleep() — use await asyncio.sleep() instead"),
]

def main():
    try:
        hook_input = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)

    tool_name = hook_input.get("tool_name", "")
    tool_input = hook_input.get("tool_input", {})

    # Only check file-editing tools
    if tool_name not in ("editFiles", "create_file", "replace_string_in_file",
                         "multi_replace_string_in_file", "insert_edit_into_file"):
        sys.exit(0)

    # Resolve the file path from the tool input
    file_path = (
        tool_input.get("filePath")
        or tool_input.get("file_path")
        or tool_input.get("newString", "")  # fallback: won't be a path, will skip
    )

    if not isinstance(file_path, str) or not file_path.endswith(".py"):
        sys.exit(0)

    # Resolve relative to cwd if needed
    cwd = hook_input.get("cwd", os.getcwd())
    if not os.path.isabs(file_path):
        file_path = os.path.join(cwd, file_path)

    if not os.path.isfile(file_path):
        sys.exit(0)

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except OSError:
        sys.exit(0)

    violations = []
    for pattern, message in BLOCKING_PATTERNS:
        if re.search(pattern, content):
            violations.append(message)

    if violations:
        warning = "Blocking I/O detected in {}: {}".format(
            os.path.basename(file_path),
            "; ".join(violations)
        )
        print(json.dumps({"systemMessage": warning}))

    sys.exit(0)


if __name__ == "__main__":
    main()
