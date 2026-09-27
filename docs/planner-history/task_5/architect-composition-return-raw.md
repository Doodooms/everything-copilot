Message Type: FINAL_ANSWER
Task name: /root
Sender: /root/peer_skill_composition
Payload:
> **SUPERSEDED by plan r10 and architecture r6 for execution.** Preserve this historical architecture return; workflow subskills remain nested under domain skills and use the canonical skill body structure.

## Architect handoff — `TASK-5-03E`

- **Status:** success
- **Agent:** architect (`peer_skill_composition`)
- **Risk:** L2, as assigned
- **Specification:** `SPEC-AGENTIC-CORE-NORMALIZATION@1`, revision 1
- **Requirements:** `REQ-1`, `REQ-2`
- **Acceptance criteria:** `AC-1`, `AC-2`
- **Semantic contracts consumed:** every routed workflow becomes a complete peer skill; domain taxonomy provides domain routing followed by method disclosure; MCP methods share common guidance without copying it.
- **Changed files:** `[]`
- **Commit SHAs:** `[]`

### Decision recommendation — proposed `ADR-ACN-004`

Amend `ADR-ACN-001`’s unconditional “method does not route onward” clause. It conflicts with `REQ-2`’s explicit allowance for composition and with existing procedures that select other methods. Preserve the two-stage **taxonomy** while allowing narrowly declared **procedural composition**: a domain selects an entry skill; that complete skill may conditionally compose another complete peer skill as part of its procedure. Composition does not nest packages or add another domain layer.

Each method remains complete for its own scope. Composition must be explicit, bounded, and owned by the source method. It must preserve the source method’s decision and handoff contracts, and must not create implicit recursion or transfer ownership merely because another method is selected.

### Source evidence

- `REQ-1` and `AC-1` require complete routed skills and the domain-to-method disclosure path. `REQ-2` and `AC-2` explicitly permit composition. See [the specification](todos/in_progress/2026-09-27/agentic-core-normalization.md:13).
- The plugin-engineering router directs Rust cases from `create-mcp` to `create-mcp-rust`; `create-mcp.md` repeats that conditional handoff in its language-selection and implementation steps. See [plugin-engineering/SKILL.md](agentic-core/skills/plugin-engineering/SKILL.md:39) and [create-mcp.md](agentic-core/skills/plugin-engineering/workflows/create-mcp.md:22).
- `deep-research` composes a finite set of source-class procedures, validates each return, and follows a declared sequential DAG. See [deep-research.md](agentic-core/skills/research/workflows/deep-research.md:21) and its [composition contract](agentic-core/skills/research/references/deep-research/references/composition.md:17).
- Other workflow-to-workflow composition includes `plugin-creation` composing authoring procedures, `orchestrate` loading specification and prior-art procedures conditionally, and `strategic-compact` selecting context methods. The multi-harness `codex`/`copilot` procedures also name paired methods and `harness-distribution`; their reciprocal “read the paired procedure” links should be classified separately from execution routes.
- `ADR-ACN-003` governs shared support-file references. Those references are support dependencies, not method composition or routing, and this recommendation does not reopen its placement or exception. See [topology r2](docs/harness-history/task_5/architecture-skill-topology-r2.md:42).

### Allowed composition forms

1. **Domain → entry method:** the sole taxonomy route for a selected competency.
2. **Conditional method specialization:** for example, `create-mcp` → `create-mcp-rust` when Rust applies.
3. **Bounded method orchestration:** for example, `deep-research` selecting needed evidence methods in its declared order.
4. **Declared method prerequisites or paired reads:** validate that the referenced skill exists, but do not treat a read prerequisite as executing that skill’s procedure. This distinction accommodates reciprocal `codex`/`copilot` cross-reads without creating a recursive execution loop.
5. **Support-file reference:** validate under the package/path rules, separately from the route graph; retain the exact `ADR-ACN-003` exception.

A composition target must itself be a complete root-level skill package. No composition edge may create a nested package or imply a new domain taxonomy.

### Route-graph and linter implications

- Represent and validate **typed edges**: domain routes, method composition, method prerequisites/paired reads, and support references. Do not infer executable routes from arbitrary prose or ordinary Markdown links.
- Require an explicit, machine-checkable declaration for each domain route and composition edge; compare it with the source procedure’s stated behavior. Choose the declaration format only after confirming it does not break the Codex and Copilot projections.
- Verify every domain route and composition target resolves to one stable skill ID with a root-level `SKILL.md`. Preserve global ID uniqueness and the complete domain-to-method path.
- Check the executable composition subgraph for cycles, missing targets, and undeclared edges. Validate prerequisites as existence/read dependencies rather than executable route edges, so reciprocal pairing cannot trigger recursive traversal.
- Keep file-path validation independent: support references must satisfy package containment, symlink rejection, and `ADR-ACN-003`’s exact exception.

### Assumptions, risks, and open questions

- **Assumption:** “two disclosure steps” defines the domain discovery taxonomy. A method’s explicit procedural specialization is allowed by `REQ-2` and existing behavior; it does not create nested domain taxonomy.
- **Risk:** converting prose handoffs into separately discoverable skills can accidentally drop behavior or turn an ordinary reference into an executable route. Typed edge classification and behavior-preserving migration are required.
- **Reversibility:** the rule and route declarations are reversible, but omitting an existing handoff from the migrated methods would be a user-visible behavior change.
- **No semantic blocker found.** The conflict is in the architecture wording: the current `ADR-ACN-001` prohibition is broader than the approved requirements and observed procedures. It should be amended explicitly.

**Suggested next owner:** Orchestrator to adopt or reject the proposed amendment and update the canonical architecture wording; Planner can then unblock the Implementer with typed-route validation as an acceptance constraint. No independent challenge was performed in this handoff.
