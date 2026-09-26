# Final checklist

Run this checklist after the validation script. Treat any unchecked line as a
blocker unless you can explain why it does not apply.

An accepted request must persist its normalized source specification, load the
canonical architecture configuration, run the deterministic scaffold, fill only
mutable semantic regions, and validate the resulting package before reporting
success.

- [ ] **Name and folder:** `name` matches the skill folder exactly.
- [ ] **Discovery text:** `description` uses `WHAT`, `USE FOR`, and `DO NOT USE FOR`.
- [ ] **Metadata:** `metadata` records authorship or provenance.
- [ ] **Package shape:** `SKILL.md` exists and support directories contain only justified files.
- [ ] **Rule priority:** `<critical_rules>`, `<general_rules>`, and `<risk_assessment>` are separate; risk cannot relax critical rules, authority, or approvals.
- [ ] **Workflow structure:** `SKILL.md` routes to immediate specialized workflows; Step 1 applies risk and each step starts with ordered `1.` actions.
- [ ] **Token surface:** measure `SKILL.md`, selected immediate workflows, and available tool schemas; exclude generic references and record the estimator.
- [ ] **Point-of-need references:** every support file has a relative Markdown link from `SKILL.md` at the workflow action that consumes it.
- [ ] **Support-doc hygiene:** support Markdown contains no active `#tool:` or `#file:` markers.
- [ ] **Contrastive docs placement:** each decision surface has one dense Markdown matrix only when comparison across independent dimensions is necessary.
- [ ] **Access mode:** `user-invocable` and `disable-model-invocation` are deliberate for the target skill.
- [ ] **Compatibility:** `compatibility` exists when `context: fork`, newer tools, or version-gated behavior is used.
- [ ] **Validation output:** errors are fixed and warnings were reviewed intentionally.
- [ ] **Example invocation:** the final summary names one concrete way to invoke the skill.