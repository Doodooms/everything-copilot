---
id: chatgpt-work-handoff
description: 'Publish a verified implementation summary through an authorized GitHub pull request so ChatGPT Work can report the completed work back for discussion.'
invoke_for:
- finishing a local implementation that should trigger a ChatGPT Work status summary through GitHub PR activity
- configuring or verifying the bounded Codex/Copilot to GitHub to ChatGPT Work handoff
avoid_for:
- asking ChatGPT Work to implement, approve, merge, or choose the next change
- GitHub operations when the authorized GitHub App MCP is unavailable
references: []
---
<critical_rules>
- MUST keep work within this subskill’s declared scope and its specific safety or authority constraints.
- MUST NOT replace the parent domain skill’s admission, global routing, or authority boundaries.
</critical_rules>

<general_rules>
- SHOULD load listed references only at the procedure step that needs them.
- MAY report unavailable evidence or unresolved decisions as unknown.
</general_rules>

<risk_assessment>
Consume the Orchestrator-assigned `risk_level` through the parent domain skill; MUST NOT reclassify or downgrade it. SHOULD escalate only when new evidence materially increases risk. Scale evidence depth, not authority or approvals.
</risk_assessment>

<rules>
- MUST follow this selected subskill only within its declared procedure and scope.
- MUST NOT replace the parent domain skill’s admission, global routing, or authority boundaries.
- MUST return the result, evidence, remaining unknowns, risks, and status required by this procedure.
</rules>

<workflow>
## Step 0 - Confirm the handoff boundary.

1. DO consume the assigned `risk_level` inherited from the parent domain skill before applying this procedure; then Treat Codex/Copilot as the implementation and validation owner. ChatGPT Work observes the resulting PR and writes a concise report for the user and their discussion with ChatGPT.
2. Do not ask ChatGPT Work to modify code, approve or merge a PR, make architecture decisions, or autonomously assign follow-up work.
3. Use only the repository's authorized GitHub App MCP identity for remote GitHub operations. If its tools or authentication are unavailable, stop remote work and report the exact blocker; do not substitute local SSH, `gh`, or another account.
4. Keep existing Git history. Never force-push. Do not merge the handoff PR.

## Step 1 - Prepare a verifiable pull request.

1. Inspect the current branch, worktree, repository instructions, and intended diff. Preserve unrelated changes and do not include them in the handoff.
2. Run the implementation's required validations and record which checks were actually run, their outcomes, and any checks not run.
3. Prepare the PR title and body from observed changes. Include:
   - what was implemented and the relevant decisions;
   - important files or components changed;
   - validations run and their results;
   - deviations from the agreed plan;
   - open questions that need the user's decision or discussion.
4. Create and push a branch and open a PR only when those lifecycle actions are explicitly authorized and the GitHub App MCP is available. Target the repository's normal base branch; do not guess it.
   - When creating a new branch, first classify the task's primary repository effect and run `uv run --script <orchestrator.py> propose-branch --repo-root <absolute-repository-path> --title <task-title> --primary-effect <effect>`. For an explicitly authorized release lifecycle, also pass `--special-name vMAJOR.MINOR.PATCH`.
   - Use only the helper's validated branch output, ignore and recompute any host-suggested name, and record its `provenance` under `lifecycle.branch_naming`.
   - When continuing an already existing historical branch, preserve its name without retroactive revalidation or renaming.
5. For a deliberate handshake test, use a dedicated branch that was validated through the branch proposal step above, and the exact marker `COPILOT_HANDSHAKE_2026` in a harmless `.harness/chatgpt-handshake.md` file. Use the exact PR title `HANDSHAKE: Codex to ChatGPT`; explain that it tests `Codex/Copilot → GitHub → ChatGPT` in the body. Do not merge it.

## Step 2 - Configure the ChatGPT Work observer.

1. In ChatGPT Work, create an event-triggered task for PR activity in the authorized repository. Choose the event that means the PR is ready for review, and verify the displayed Trigger, Condition, and Prompt before saving. This configuration is performed in ChatGPT Work; do not claim Codex installed or verified it unless the host provides direct evidence.
2. Use a prompt with this behavior:

   > When a pull request in `Doodooms/plugin-factory` becomes ready for review, inspect its description, changed files, associated commits, and available checks. Do not change the repository, approve or merge the pull request, decide architecture, or choose the next task. Produce a concise report for the user and their ChatGPT discussion: implementation; decisions; important files/components; validations and observed results; deviations from the preceding plan; questions needing a decision; and items especially worth checking. Clearly label information that is not present or could not be verified.
   >
   > If the PR title starts with `HANDSHAKE:`, also check for `COPILOT_HANDSHAKE_2026` in the PR changes and report `CHATGPT_ACK_2026` together with the PR number only when the marker is actually present. Otherwise report the missing marker without acknowledging success.

3. Keep the event task scoped to reporting. Do not treat a PR event as authorization to write comments, edit files, merge, or start another implementation cycle.

## Step 3 - Verify and return the handoff state.

1. Verify the PR exists through GitHub App MCP and record its repository, branch, base branch, commit SHA, title, PR number, and URL. For a handshake, verify the marker is in the PR diff. Do not infer that ChatGPT Work ran merely because a PR exists.
2. Report the task status as `complete`, `partial`, or `blocked`. Separate verified GitHub state from ChatGPT Work configuration and execution, which may remain unknown until Work exposes evidence.
3. If GitHub access or Work event setup is unavailable, leave the applicable state `blocked` or `unknown` and return the exact next action and responsible surface.
</workflow>
