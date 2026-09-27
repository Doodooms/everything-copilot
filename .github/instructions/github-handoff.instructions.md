---
applyTo: "**"
---

## GitHub handoffs

- For each significant, coherent change that is ready to discuss, commit it on a feature branch, push the branch, and open or update a pull request. Mark it ready for review when it is stable enough to examine.
- Preserve local user changes. Never force-push, rewrite or destroy history, or merge a pull request automatically.
- Use `.github/PULL_REQUEST_TEMPLATE.md`. Report only checks actually run and their results; state when checks were not run.
- Codex/Copilot own implementation and testing. ChatGPT Work reads PRs and summarizes them; do not assume it should change code or comment on the PR.
- Follow `docs/git-workflow.md` for the branch, release, hotfix, and commit model.
- Do not guess how to reconcile unrelated histories or map the existing `dev` branch to `develop`; ask the user before changing branches or repository settings.
- Put important uncertainties in `Open questions`. Leave major architecture and next-step decisions to the user and ChatGPT; do not start another major decision automatically.
