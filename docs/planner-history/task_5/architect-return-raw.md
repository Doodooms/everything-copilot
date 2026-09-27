Message Type: FINAL_ANSWER
Task name: /root
Sender: /root/mcp_skill_composition
Payload:
> **SUPERSEDED by plan r10 and architecture r6 for execution.** Retain this historical MCP composition return as context; do not use peer-package assumptions as implementation instructions.

## Architect handoff — TASK-5-05A

- **Status:** `success` — read-only architecture decision
- **Agent:** `architect`
- **Risk:** `L2` (assigned; unchanged)
- **Specification:** `SPEC-AGENTIC-CORE-NORMALIZATION@1`, revision 1
- **Requirements:** `REQ-1`, `REQ-2`
- **Acceptance criteria:** `AC-1`, `AC-2`
- **Existing decisions preserved:** `ADR-ACN-001`, `ADR-ACN-002`
- **Decision ID:** `ADR-ACN-003` (proposed here; no ADR file written)

### Recommendation

Keep one canonical common transport and security guide inside the `plugin-engineering` domain package:

`agentic-core/skills/plugin-engineering/references/create-mcp/common-transport-security.md`

Have both peer method skills link to that guide using the same explicit relative path, `../plugin-engineering/references/create-mcp/common-transport-security.md`. Treat it as supporting knowledge loaded at the point of use, not as another method skill or a procedure to route to.

Update the package linter and reference policy to allow **only this explicit plugin-internal target** from `create-mcp` and `create-mcp-rust`. Resolve and validate the canonical target beneath `agentic-core/skills/`, reject symlinks and all other package escapes, and check that the resolved reference exists in the materialized profile. Keep all Rust and `rmcp`-specific constraints in `create-mcp-rust`.

### Evidence and tradeoffs

- **Semantic contract:** `REQ-2` requires complementary validated MCP skills, one copy of common guidance, and preserved Rust-specific constraints. `AC-2` requires both packages to validate. `ADR-ACN-001` and `ADR-ACN-002` require complete peer packages and immediate-child skill discovery under `agentic-core/skills/`.
- The existing `create-mcp` workflow covers transport choice and approved server scope; `create-mcp-rust` already contains common transport and security rules alongside `rmcp`-specific feature, API, and toolchain rules. These are the sources to consolidate while retaining the Rust specialization.
- The linter currently rejects cross-package workflow references: [`_resolve_workflow_reference`](agentic-core/skills/plugin-engineering/references/create-skill/scripts/skill_lint_core.py:368) requires references to resolve inside the package, and [the linter test](tests/test_skill_workflow_linter.py:373) asserts that out-of-package references fail. So the proposed path is **not supported by the current linter contract**; it requires the narrow policy exception above, not unrestricted `..` access.
- The native plugin profile loader gathers files below every peer skill package but does not include arbitrary plugin-root references: [`_load_core`](agentic-core/runtime/pluginctl/controller.py:1036). Placing the guide under the domain package therefore keeps it in the existing materialization surface without changing that loader. A plugin-root guide would require expanding the loader.
- The portable Expertise Pack target copies files under each declared skill package path only: [`compile_target`](expertise/targets/portable.py:150). This recommendation applies to the native `agentic-core` plugin materialization path; independently projecting these skills as portable packs would need an explicit shared-support projection.

A plugin-root shared file is a weaker fit because the current native materializer does not collect arbitrary root files. Duplicating the guide violates the single-source requirement, and making it a third method skill conflicts with the no-forward-routing requirement.

### Constraints, risks, and validation implications

The linter exception must be restricted to the named source skills and canonical target, with containment checked after path resolution so other escapes remain rejected. The host’s ability to follow sibling-package Markdown links is not established by the inspected repository code; validate that behavior against the materialized profile during implementation/QA. Keep `create-mcp-rust`’s pinned-version, minimum-feature, typed API, and Rust lifecycle requirements local to that skill.

**Affected surfaces:** the future common guide, both method skill definitions, and the package linter/reference policy and its tests. No materializer change is recommended for native plugin profiles.

**Alternatives and tradeoffs:** Plugin-root shared guidance needs a materializer change; package-local copies duplicate procedures; another peer package adds a discoverable skill and routing ambiguity.

**Assumptions / unresolved questions:** The sibling link will be usable by both intended hosts after installation; confirm in the planned host validation. The portable pack projection is outside this decision’s scope.

**Non-goals:** Reopen peer-skill topology, nest skills, add method routing, define product scope, or implement the change.

- `changed_files: []`
- `commit_shas: []`
- **Next owner:** Implementer for `TASK-5-05B`, coordinating the bounded linter/reference-policy change with `TASK-5-03C`; QA and Reviewer retain the planned independent checks.
