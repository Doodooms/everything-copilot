#!/usr/bin/env bash
set -euo pipefail

if [[ -z "${GITHUB_APP_ID:-}" ]]; then
    printf 'github-mcp-server requires GITHUB_APP_ID in its host environment.\n' >&2
    exit 2
fi
if [[ -z "${GITHUB_APP_INSTALLATION_ID:-}" ]]; then
    printf 'github-mcp-server requires GITHUB_APP_INSTALLATION_ID in its host environment.\n' >&2
    exit 2
fi
if [[ -z "${GITHUB_APP_PRIVATE_KEY_PATH:-}" ]]; then
    printf 'github-mcp-server requires GITHUB_APP_PRIVATE_KEY_PATH in its host environment.\n' >&2
    exit 2
fi
if [[ "$GITHUB_APP_PRIVATE_KEY_PATH" != /* || ! -f "$GITHUB_APP_PRIVATE_KEY_PATH" || ! -r "$GITHUB_APP_PRIVATE_KEY_PATH" ]]; then
    printf 'GITHUB_APP_PRIVATE_KEY_PATH must name a readable absolute PEM file.\n' >&2
    exit 2
fi
if ! command -v docker >/dev/null 2>&1; then
    printf 'Docker is required to launch the GitHub App MCP server.\n' >&2
    exit 127
fi

exec docker run --rm -i \
    -v "${GITHUB_APP_PRIVATE_KEY_PATH}:/secrets/github-app.pem:ro" \
    -e GITHUB_APP_ID \
    -e GITHUB_APP_INSTALLATION_ID \
    -e GITHUB_APP_PRIVATE_KEY_PATH=/secrets/github-app.pem \
    ghcr.io/github/github-mcp-server:v1.12.2 \
    stdio \
    --read-only
