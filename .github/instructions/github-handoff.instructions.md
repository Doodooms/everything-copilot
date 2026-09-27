---
applyTo: "**"
---

## GitHub handoffs

- Read `AGENTS.md` and `docs/git-workflow.md`. Start ordinary work branches from `develop` and open pull requests back to `develop`.
- Preserve user changes and published commit SHAs. Do not force-push, rewrite published commits, or merge a pull request automatically.
- Use `.github/PULL_REQUEST_TEMPLATE.md`; report only checks actually run and list unresolved decisions under `Open questions`.
- Codex and Copilot implement and validate locally. ChatGPT Work reads pull requests and summarizes them; do not assume it should change code or comment on a pull request.
- Leave architecture and the next major step to the user. Get explicit authorization before changing `main`, `dev`, archive refs, tags, or repository settings.
