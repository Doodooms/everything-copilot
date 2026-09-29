# Plugin Factory upgrade candidates: evidence report

**Repository:** Doodooms/everything-copilot
**Revision reviewed:** 662ea3471b9e0a7a0ef34082a1539a8175c668b9 on develop
**Research date:** 2026-09-28
**Scope:** public repository and public upstream sources only. No product code changed; no candidate installed; no provider benchmark or test run.

Recommendations below are candidate-specific judgments, not a ranking. A reference pattern is not an adoption decision. Product demand and a measurable gap remain prerequisites for implementation.

## HIGH_VALUE_PATTERNS

### 1. Cost evidence should preserve identity, measurement source, and uncertainty

CodeBurn is useful as a reference for reading local harness session records and normalizing measured token and tool events without wrapping a provider call. Its strongest transferable idea is to distinguish what the source actually measured from what a later pricing table estimates. A useful record needs stable run/task/attempt/profile/session identifiers, event provenance, token categories, tool-call counts, outcome, and an explicit unknown state. Rate-card identity, date, and currency are needed if monetary cost is derived.

The repository already has much of the evaluation-side identity and outcome model. A focused offline parser fixture is a smaller next step than adopting a dashboard or a session-history product. Keep raw transcripts and tool output out of any new durable aggregate.

### 2. Skill quality benefits from progressive disclosure and layered evaluation

The addyosmani/agent-skills guidance is a useful reference for concise routing descriptions, clear activation criteria, and separating workflow instructions from references and evaluation material. The repository already has domain routers, workflow skills, references, validators, and a scenario harness. The remaining candidate is a cheap deterministic routing check against the existing scenarios, not a parallel skill catalog or bulk copy.

### 3. Security claims need a layer-by-layer model

Current official docs distinguish instructions and tool permissions from approval policy, OS sandboxing, filesystem scope, network access, and credential handling. A read-only execution mode constrains writes; by itself it does not establish a single-root read boundary. The merged execution backend adds process supervision and a read-only request, but does not establish a provider-call ceiling or prove the effective plugin/MCP inventory is isolated.

### 4. Runtime coordination patterns are not Plugin Factory requirements by default

AG2 and Paperclip expose useful public patterns for event-based coordination, explicit termination, durable ownership, leases, budgets, approvals, and audit history. The repository has dependency-aware task handoffs, durable task/evaluation records, and human checkpoints, but no demonstrated requirement for a generic always-on multi-agent or company-work runtime. Treat these as generic orchestration/control-plane concerns unless a repository-owned use case is measured.

## ALREADY_HAVE

Reviewed local evidence at the designated base:

- harness_factory/models.py defines HarnessResult with run identity, harness, status, scenario, base revision, observations, assertions, artifact/evidence references, optional token usage, latency, errors, model turns, and model calls.
- harness_factory/adapters.py extracts Codex per-turn usage from session JSONL and records MCP calls/declared servers separately. Tool observations are not yet one normalized count across every tool type.
- harness_factory/evaluation.py persists evaluation artifacts and usage, supports RunBudget and EvaluationProfile, records unknown values, and compares runs only when suite, base revision, harness, and scenario contracts match. It does not derive monetary cost or bind a rate-card version.
- Merged PR #4 at the reviewed base introduced ExecutionConstraints(timeout_seconds, read_only), ExecutionResult with task/attempt/harness/backend identity, artifact references, failure and optional external session ID, and a supervised Codex CLI backend using read-only sandboxing, ephemeral execution, timeout handling, JSON output and schema validation.
- The backend does not populate session identity or usage in ExecutionResult. One CLI process is not evidence of one provider model call or one model turn. A provider-call cap is not enforced by the current request. --ignore-user-config does not prove effective project/plugin/MCP isolation.
- Agentic Core already has domain routing, workflow skills, references, scripts and validators. It follows the Agent Plugins 1.0 shape with plugin metadata, skills, and MCP configuration.
- Evaluation history and task records are durable, but the reviewed public code does not provide a general live-memory bus or generic lease service.

Source links to the exact reviewed revision are collected in SOURCES.

## GENUINE_GAPS

- **Usage normalization:** no common, provenance-bearing model for measured per-call input/output/cache tokens and tool events across harnesses. Codex usage extraction is a useful start.
- **Monetary-cost provenance:** no explicit rate-card ID, pricing date, currency, or measured-versus-estimated marker. Subscription “equivalent cost” must not be reported as an invoice.
- **Per-task marginal cost:** evaluation profiles and contract matching create a possible controlled comparison surface, but no provenance-backed matched baseline pair is present for the open cost gates.
- **Provider safety gates:** timeout and read-only process supervision do not establish a hard provider-call/turn ceiling, nor prove effective plugin/MCP isolation. Keep provider experiments blocked until those properties are demonstrated without a provider call.
- **Cheap routing evidence:** current skill routing is structured, but no verified deterministic lexical preflight result was found for the existing scenario prompts.
- **Cross-harness tool counts:** observations exist, but counts and semantics are not uniform enough to compare every tool category.
- **No demonstrated persistent shared-memory requirement:** ContextGraph presents useful provenance and context-pack patterns, but the reviewed Plugin Factory repository does not establish a product requirement for a shared memory service.

These are implementation/evidence gaps, not automatic reasons to adopt an external project.

## WRONG_SCOPE

- **Paperclip company operating model:** goals, org charts, hiring/team management and business scheduling do not map to plugin authoring. Durable work, leases, approvals, budgets and audit are generic orchestration/control-plane patterns only.
- **AG2 as runtime:** no measured need justifies replacing the repository’s current handoff and evaluation mechanisms with another agent runtime.
- **Host-specific Hermes profile:** oh-my-hermes installs skills, agents, routines and configuration into a Hermes user environment; it is not a repository-local Agentic Core extension.
- **Premortem duplication:** Challenger already asks for assumptions, failure modes, counterarguments, disconfirming checks, mitigations and residual risk. A separate transcript-producing workflow would duplicate this unless QA demonstrates a specific failure-story gap.
- **Document/web ingestion:** no owned corpus, representative input set, or acceptance criteria were found for generic document conversion or browser crawling. MarkItDown and Crawl4AI therefore remain NO_CURRENT_REQUIREMENT; no deep technical comparison is warranted.
- **Stealth browser projects:** no concrete browser automation requirement was found. Stealth or anti-detection alone is not a product need; CloakBrowser and Obscura remain out of scope.
- **ContextGraph service:** graph database, API/MCP, tenant ACL, retention and context assembly are runtime/infrastructure concerns. A provenance pattern may be referenced without bringing in a service.
- **Google product skills:** no current Google-specific product need was found. The repository already uses the shared Agent Plugins 1.0 structure; a broad catalog is not a gap.

## Candidate assessments

Each candidate uses the requested evidence fields. “Smallest experiment” is a proposal only; none was run.

### CodeBurn

~~~yaml
candidate: getagentseal/codeburn
useful_pattern: Parse local harness session records and normalize measured token/tool events; preserve measured, estimated, and unpriced distinctions.
existing_equivalent: HarnessResult, Codex session JSONL usage extraction, MCP observations, durable evaluation artifacts, EvaluationProfile, and exact scenario-contract matching.
genuine_gap: Cross-harness per-call normalization, explicit task/attempt/session/profile linkage, pricing provenance, and measured marginal cost versus task outcome.
wrong_scope: Installing a dashboard/history product or treating current-rate estimates as an invoice or causal plugin cost.
adoption_cost: Low for an offline fixture and small parser adapter; materially higher for provider coverage, history aggregation, and UI.
security_cost: Session files can contain sensitive prompts and outputs. Retain only aggregate events/metadata; avoid raw transcript persistence and network upload.
token_cost_implication: Parsing local records uses no provider tokens. Any later measured comparison must count retrieved context and tool calls and report unknown/estimated pricing separately.
source_evidence:
  - https://github.com/getagentseal/codeburn
  - https://github.com/getagentseal/codeburn/blob/main/docs/providers/codex.md
  - https://github.com/getagentseal/codeburn/blob/main/docs/yield.md
smallest_experiment: Add one synthetic/redacted Codex JSONL fixture that tests cumulative-counter replay/deduplication and emits aggregate usage with source/confidence fields; no install or provider call.
recommendation: EXPERIMENT
~~~

Evidence notes: CodeBurn’s Codex documentation describes parsing local session rollout JSONL, including token-count events and cumulative counters; replay/deduplication matters. Its cost view uses pricing data refreshed/cached over time, so the price is a present-day estimate and not necessarily the user’s billed amount. Its yield correlation is timestamp/branch based, not a direct task outcome or merge verification. The local CLI and optional desktop telemetry have different privacy behaviors; avoid an unqualified claim that no data can ever leave the machine. Do not install CodeBurn.

### AG2

~~~yaml
candidate: ag2ai/ag2
useful_pattern: Explicit async coordination, typed messages/channels, human input hooks, bounded waits, and explicit close/termination.
existing_equivalent: Dependency-aware repo handoffs, durable task/evaluation history, one-hop request validation, and human checkpoints.
genuine_gap: No measured live collaboration gap in Plugin Factory; current workflow is task/evaluation oriented.
wrong_scope: Adopting AG2 as the runtime or assuming an event pattern is itself durable cross-process storage.
adoption_cost: High for a runtime integration and ongoing compatibility; low for a no-provider protocol fixture.
security_cost: Additional agent/message/tool boundary and dependency surface; requires ownership, authorization, and retention policy.
token_cost_implication: Parallel agents and repeated coordination messages can increase model calls and prompt tokens; bounded timeouts do not bound provider spend.
source_evidence:
  - https://github.com/ag2ai/ag2
smallest_experiment: If a concrete live collaboration need appears, model a fake-agent event/close/timeout fixture with no provider. No experiment is currently justified.
recommendation: KEEP_AS_REFERENCE
~~~

Evidence notes: The current AG2 v1 README presents a protocol-driven AgentOS with Network Hub and typed channels and differs from legacy AG2 Classic; GroupChat has moved to the Classic repository. The examples demonstrate coordination patterns, not a demonstrated repository need or guaranteed durable storage across process restarts. No runtime adoption is proposed.

### Paperclip

~~~yaml
candidate: paperclipai/paperclip
useful_pattern: Durable issues and blocker dependencies, ownership/lease lifecycle, budgets and hard stops, approval checkpoints, audit activity, and status.
existing_equivalent: Durable task/evaluation records, dependency-aware handoffs, budgets/profiles, artifact references, and human checkpoints; no generic lease service was found.
genuine_gap: No measured Plugin Factory requirement for a company-work runtime or generic continuously scheduled worker.
wrong_scope: Company goals, org charts, hiring, teams, and business scheduling are not plugin-authoring requirements.
adoption_cost: Very high for adopting its server/database/runtime model; a single generic lease lifecycle is a separate future requirement.
security_cost: Persistent agent ownership, broad workspace access, approval policy, database/API exposure, and recurring execution require significant threat modeling.
token_cost_implication: Heartbeats and repeated agent work can incur recurring model usage; budgets/hard stops are useful generic controls but do not guarantee correct rate accounting.
source_evidence:
  - https://github.com/paperclipai/paperclip
  - https://github.com/paperclipai/paperclip/blob/master/docs/start/core-concepts.md
  - https://github.com/paperclipai/paperclip/blob/master/doc/DEVELOPING.md
smallest_experiment: None for Plugin Factory. If generic long-running work later becomes an explicit requirement, evaluate one ownership/lease lifecycle against a repository-owned scenario.
recommendation: ADOPT_LATER_IF_TRIGGERED
~~~

Public capability classification:

| Public idea | Classification |
|---|---|
| Plugin authoring, skill packaging, plugin validation | PLUGIN_FACTORY only where tied to repository-owned authoring needs; no new requirement established |
| Durable work items, blocker dependencies, ownership/leases, budgets, approvals, audit trail, progress/status | CONTROL_PLANE_GENERIC |
| Company goals, org charts, hiring, business-team administration and business scheduling | NOT_RELEVANT |

No private Control-Plane architecture or details are used.

### addyosmani/agent-skills

~~~yaml
candidate: addyosmani/agent-skills
useful_pattern: Precise skill descriptions and activation criteria; progressive disclosure; separate workflow, reference, onboarding, and evaluation content; layered cheap-to-expensive evaluation.
existing_equivalent: Agentic Core domain routers, workflow skills, references, validators, and scenario-based harness evaluation.
genuine_gap: No verified cheap deterministic routing preflight result across existing scenario prompts.
wrong_scope: Copying a parallel skill catalog or reorganizing existing skills without measured routing failures.
adoption_cost: Low for a small lexical fixture; high for a broad content migration.
security_cost: Copied instructions and third-party provenance require review; no runtime privilege is gained by adopting the writing pattern.
token_cost_implication: Progressive disclosure may reduce irrelevant context, but benefit must be measured on matched scenarios; oversized descriptions still consume context.
source_evidence:
  - https://github.com/addyosmani/agent-skills/blob/main/docs/getting-started.md
  - https://github.com/addyosmani/agent-skills/blob/main/docs/skill-anatomy.md
  - https://github.com/addyosmani/agent-skills/blob/main/docs/developer-onboarding.md
smallest_experiment: Run a deterministic lexical routing check over the existing nine-scenario prompt set and report false positives/negatives; no model calls.
recommendation: KEEP_AS_REFERENCE
~~~

### google/skills

~~~yaml
candidate: google/skills
useful_pattern: Product/service-specific skills packaged alongside relevant MCP/tool configuration.
existing_equivalent: Agent Plugins 1.0 plugin metadata, repository skills, and MCP configuration.
genuine_gap: No current Google-specific product or service requirement was found.
wrong_scope: Importing a broad vendor skill catalog without an owning use case.
adoption_cost: Low for one reviewed skill if triggered; unnecessary maintenance for a catalog.
security_cost: Each skill/tool description and MCP permission surface needs source, behavior, and authorization review.
token_cost_implication: Extra skills and tool descriptions increase context and can expose more tools; actual use and marginal cost are unmeasured.
source_evidence:
  - https://github.com/google/skills
  - https://docs.github.com/en/copilot/concepts/agents/about-plugins
smallest_experiment: None until a concrete Google product task and acceptance test are identified.
recommendation: ADOPT_LATER_IF_TRIGGERED
~~~

### Salomondiei08/oh-my-hermes

~~~yaml
candidate: Salomondiei08/oh-my-hermes
useful_pattern: Opinionated bundles of workflows, agents, routines, and scripts for a specific host.
existing_equivalent: Agentic Core orchestrator/specialist boundaries, workflow skills, and durable progress/human gates.
genuine_gap: None demonstrated for the repository's plugin-authoring workflow.
wrong_scope: Hermes-specific user-profile installation and host routines are not repository-local Agentic Core packaging.
adoption_cost: Medium-to-high for translation and maintenance; direct install is outside this repository's scope.
security_cost: Host configuration and routines expand local tool exposure and persistence; provenance and permissions would need review.
token_cost_implication: Additional agents/routines may increase model calls and prompt overhead; no comparative measurements are available.
source_evidence:
  - https://github.com/Salomondiei08/oh-my-hermes
smallest_experiment: None; reconsider only if a repository-owned Hermes integration requirement appears.
recommendation: IGNORE
~~~

### Hi1talib1World/Premortem

~~~yaml
candidate: Hi1talib1World/Premortem
useful_pattern: Organize pre-mortem findings by failure story, assumption, warning signal, and mitigation.
existing_equivalent: Challenger contract already requests assumptions, failure modes, counterarguments, disconfirming checks, mitigations, and residual risk.
genuine_gap: No specific failure-story omission was demonstrated in current QA evidence.
wrong_scope: Adding a parallel Challenger process or persisting full transcripts without an evidence-backed need.
adoption_cost: Low for one prompt fixture; higher if a separate workflow and storage are maintained.
security_cost: Full transcripts can preserve sensitive prompts/results; parallel agents increase tool and data exposure.
token_cost_implication: Parallel deep dives and full transcript output increase tokens and provider calls.
source_evidence:
  - https://github.com/Hi1talib1World/Premortem
smallest_experiment: If an observed QA miss is traced to an unstructured failure story, test one synthetic fixture against the existing Challenger contract.
recommendation: KEEP_AS_REFERENCE
~~~

### Microsoft MarkItDown

~~~yaml
candidate: microsoft/markitdown
useful_pattern: No pattern assessed in depth because no concrete document-ingestion need is established.
existing_equivalent: No repository-owned generic document conversion pipeline was found or required by current acceptance criteria.
genuine_gap: NO_CURRENT_REQUIREMENT.
wrong_scope: Adding a converter without a representative corpus, supported-format decision, or output-quality criteria.
adoption_cost: Not assessed; defer package/runtime evaluation until a real need is specified.
security_cost: Not assessed; document parsing would require input trust, file-format, and content-handling review if triggered.
token_cost_implication: Conversion itself may be local, but extracted content can expand agent context; no workload exists to measure.
source_evidence:
  - https://github.com/microsoft/markitdown
smallest_experiment: None until an owned document corpus and deterministic acceptance criteria exist.
recommendation: IGNORE
~~~

### Crawl4AI

~~~yaml
candidate: unclecode/crawl4ai
useful_pattern: No pattern assessed in depth because no concrete web-crawling need is established.
existing_equivalent: No repository-owned crawling workflow, target corpus, or acceptance criteria were found.
genuine_gap: NO_CURRENT_REQUIREMENT.
wrong_scope: Introducing browser automation and extraction infrastructure absent a defined source and task.
adoption_cost: Not assessed; browser/runtime/dependency cost is premature.
security_cost: Not assessed; any future crawler must address untrusted pages, network allowlists, browser isolation, and prompt injection.
token_cost_implication: Crawled pages can add large context and tool overhead; no representative workload exists for measurement.
source_evidence:
  - https://github.com/unclecode/crawl4ai
smallest_experiment: None until a bounded corpus and extraction acceptance test are identified.
recommendation: IGNORE
~~~

### AllenMaxi/ContextGraph

~~~yaml
candidate: AllenMaxi/ContextGraph
useful_pattern: Provenance-bearing claims and explainable context packs with inclusion, exclusion, conflict, freshness, and token-budget rationale.
existing_equivalent: Evidence/artifact references and durable task/evaluation history; no shared contextual-memory service or claim graph was found.
genuine_gap: No repository requirement for cross-agent shared persistent memory, graph queries, or memory publication.
wrong_scope: Treating a runtime/orchestration memory service as a Plugin Factory primitive.
adoption_cost: High: database/backend, API/MCP, tenancy, ACL, freshness, retention, and operational ownership.
security_cost: High: memory poisoning, cross-tenant disclosure, ACL correctness, provenance trust, retention, and retrieved-content prompt injection.
token_cost_implication: Context packs can enforce budgets, but retrieval and MCP calls add context/tool tokens; no workload exists to establish savings.
source_evidence:
  - https://github.com/AllenMaxi/ContextGraph
smallest_experiment: If a shared-memory need is approved later, use a synthetic claim set to test provenance and context-pack inclusion/exclusion before any service integration.
recommendation: KEEP_AS_REFERENCE
~~~

### CloakBrowser

~~~yaml
candidate: CloakHQ/CloakBrowser
useful_pattern: None assessed; no concrete browser requirement was identified.
existing_equivalent: No browser automation need was found in the reviewed repository scope.
genuine_gap: None.
wrong_scope: Stealth/anti-detection alone is not a product requirement.
adoption_cost: Not assessed; defer while no use case exists.
security_cost: Not assessed; browser execution would require isolation, network boundaries, and untrusted-content handling.
token_cost_implication: Browser actions and page content can add tool and context costs; no scenario exists to measure.
source_evidence:
  - https://github.com/CloakHQ/CloakBrowser
smallest_experiment: None until an authorized, bounded browser task is defined.
recommendation: IGNORE
~~~

### Obscura

~~~yaml
candidate: h4ckf0r0day/obscura
useful_pattern: None assessed; no concrete browser requirement was identified.
existing_equivalent: No browser automation need was found in the reviewed repository scope.
genuine_gap: None.
wrong_scope: Stealth/anti-detection alone is not a product requirement.
adoption_cost: Not assessed; defer while no use case exists.
security_cost: Not assessed; browser execution would require isolation, network boundaries, and untrusted-content handling.
token_cost_implication: Browser actions and page content can add tool and context costs; no scenario exists to measure.
source_evidence:
  - https://github.com/h4ckf0r0day/obscura
smallest_experiment: None until an authorized, bounded browser task is defined.
recommendation: IGNORE
~~~

## SECURITY_FINDINGS

This is a documentation and public-source review, not a test of user configuration or a penetration test. No credentials, private settings, or secrets were accessed or changed. Status labels assess the corresponding claim in todos/harness/security-hardening-input.md, not the quality of every implementation.

### Layer matrix

| Layer | Meaning and current evidence | Boundary / finding |
|---|---|---|
| instruction/policy | Text and configuration that guide agent behavior. Official product docs describe policy and instructions separately from OS enforcement. | Guidance can be ignored or bypassed by a different tool path; it is not a filesystem or network boundary. |
| approval policy | Rules that determine when an action requires user approval. Codex docs distinguish approval policy from sandbox capability. | Approval prompts do not themselves confine reads, writes, or network access. |
| tool permissions | Which named built-in or extension tools are exposed/allowed. Claude docs describe tool permissions and deny rules. | A tool-level deny does not necessarily stop an equivalent operation through shell or another tool. |
| filesystem permissions | Per-tool/path policies and OS filesystem access. Claude documents tool-specific path behavior; GitHub Copilot local sandboxing documents differences between built-in file tools and OS-enforced child processes. | The enforcement mechanism and tool matter. Do not generalize a Read rule into OS-wide read confinement. |
| sandbox | OS/process restrictions on file and process capabilities. Codex and Copilot docs describe sandboxing separately from approval and tools. | Must verify actual platform, effective configuration, child-process inheritance, and exceptions. Product claims can be platform- or preview-specific. |
| workspace scope | Which roots an agent is told or permitted to work within. | Naming a workspace or using read-only mode does not prove that reads are limited to that root. |
| network restrictions | Egress policy, network allowlists, proxies, or firewall controls. Claude docs describe sandbox network controls; Copilot docs distinguish remote MCP. | A command deny for curl or another executable is not an egress policy; alternate clients and child processes may exist. |
| secret storage | Where credentials are stored and which principal can access them. | Not established by the reviewed notes. Do not treat environment variables as a complete secret-management design. |
| secret injection | How credentials are supplied to an approved process, including scope, lifetime, masking, and proxying. | Keep separate from storage and from authorization. A masked value may still be available to the process. |
| output/log leakage | Secrets or sensitive content echoed into results, transcripts, logs, artifacts, or telemetry. | A valid threat to review; no specific redaction guarantee was demonstrated for the repository’s complete output path. |
| credential administration | Issuance, rotation, revocation, least privilege, and audit of credentials. | A runtime sandbox does not administer credentials or revoke them. No credential changes were made. |

### Claims from the security-hardening input

| Input claim / recommendation | Status | Evidence-based correction |
|---|---|---|
| Claude Read deny protects all reads, including shell grep or Python/Node file access | PARTIAL | Tool rules govern named tools; shell or programmatic reads are separate paths. Treat tool denies as one layer, not OS confinement. |
| Claude Grep/Glob denial covers equivalent shell search | PARTIAL | Built-in tool restrictions do not establish that shell commands cannot read the same content. |
| Claude Write path rules can block protected files | OUTDATED | Current permissions docs say path rules apply to Edit/Write-related tools selectively; legacy Write/NotebookEdit/MultiEdit path-rule examples in the input are not a reliable current control. Use the current documented mechanism and verify it. |
| An allow rule fires before a broad deny, so a narrow curl allow can make a safe exception | WRONG_ABSTRACTION | Current Claude docs describe deny precedence over allow. More fundamentally, a command matcher is not network egress control. |
| Denying curl prevents network access | WRONG_ABSTRACTION | Network access must be restricted at the sandbox/proxy/firewall or equivalent egress layer; other clients may be available. |
| Historical “more than 50 subcommands” behavior is a current general bypass | UNVERIFIED | A third-party report describes a historical issue; current official docs discuss compound-command checking but do not establish the exact alleged version boundary or universal current behavior. Do not copy the claim as a current fact. |
| CLAUDE_CODE_SKIP_PROMPT_HISTORY=1 is a supported security control | UNVERIFIED | Not located in current official settings documentation reviewed. Do not rely on it without current official support and a version-specific test. |
| Codex read-only means only the workspace can be read | WRONG_ABSTRACTION | Read-only describes write capability within the configured sandbox. It does not itself define a single workspace read root. Inspect effective sandbox roots/status and platform behavior. |
| Repository/harness process timeout and read-only request prove provider cost is bounded | PARTIAL | Process supervision limits runtime; it does not enforce a provider-call/token/monetary cap or prove one process equals one model call. |
| --ignore-user-config proves no plugin/MCP configuration is active | PARTIAL | It reduces user configuration influence but does not by itself prove the effective project configuration, plugins, or MCP servers. Inventory and isolation evidence are still needed. |
| Test secrets, dummy credentials, output redaction and secret-manager use are fully implemented | PARTIAL | These are sound requirements to verify, not evidence of an end-to-end implemented control in the public repository. No secret/config audit was performed. |

The source set includes official Codex approval/security docs, GitHub Copilot CLI and local sandbox docs, Claude Code permissions/sandbox/settings docs, and GitHub Agent Plugins docs. Copilot local sandbox documentation notes platform and preview limitations and differentiates built-in file tools from OS-enforced child processes; do not universalize its guarantees.

## COST_EVAL_GATES

Classification is based on the public repository state at the reviewed revision. Under the required four-way scheme, every still-open gate remains STILL_BLOCKED; no gate is promoted by missing or synthetic evidence.

| Gate | Current evidence/status | Classification | Smallest required unblocker |
|---|---|---|---|
| AC-COST-3 | Required matched baselines are absent from the reviewed baseline inventory. Flat/hierarchical and old/new routing pairs were not found. Do not synthesize them. | STILL_BLOCKED | Locate an actual provenance-backed compatible pair, or deliberately create a small controlled pair with matching suite/base/harness/scenario contracts. |
| AC-COST-4 | Current process timeout/read-only execution does not enforce a hard provider-call ceiling or prove effective plugin/MCP isolation. | STILL_BLOCKED | No-provider proof/fixture for a hard call/turn cap plus an auditable effective plugin/MCP inventory and isolation boundary. Do not invoke a provider until proven. |
| AC-COST-5 | Evidence supports a blocked artifact/path, not a real bounded provider evaluation. | STILL_BLOCKED | After AC-COST-4 passes, run one bounded Codex scenario that creates a durable artifact and records usage/outcome. |
| AC-COST-6 | EvaluationProfile exists, but there is no qualifying provider run demonstrating it in use. | STILL_BLOCKED | After AC-COST-4 passes, execute the same bounded scenario with an explicit, hashed EvaluationProfile and persist it with the result. |
| AC-COST-7 | Documentation and partial plumbing exist; there are no matched behavioral results/baselines to support conclusions. | STILL_BLOCKED | Generate matched results under AC-COST-3 and AC-COST-5, retain unknowns, and report profile/rate-card provenance. |
| AC-COST-8 | One-hop policy/unit coverage exists, but independent QA evidence is absent. | STILL_BLOCKED | Independent no-provider review using fake adapters to exercise CrossHarnessValidationContext ownership, mutation boundaries, and no-recursion behavior. |

AC-COST-1 and AC-COST-2 are recorded as passing in the current follow-up notes; the table above covers the six gates requested. AC-COST-4 is a prerequisite before any provider-backed experiments in AC-COST-5/6/7.

## THREE_SMALLEST_EXPERIMENTS

1. **Offline usage-parser fixture.** Feed a synthetic/redacted Codex JSONL fixture through a small parser covering cumulative counters, replay/deduplication, tool events, and unknown usage. Persist only aggregate measurements with source/confidence. No installation, provider, or raw transcript retention.
2. **One matched, single-scenario cost pair, only after AC-COST-4 is proven.** Use two explicitly identified profiles with the same scenario contract and base revision. Capture usage, tool counts, outcome, latency, rate-card ID/date/currency, and estimated versus measured fields. If the call cap or isolation proof fails, do not invoke the provider.
3. **Independent AC-COST-8 boundary QA.** Use fake adapters only to test one-hop ownership, mutation constraints, and refusal of recursive dispatch. No provider or external harness required.

These are proposals. None was executed during this research task.

## IDEAS_REJECTED

- Installing CodeBurn or storing raw session transcripts to obtain a dashboard.
- Treating rate-card estimates, subscription equivalents, or timestamp-to-commit correlation as billed or causal per-task cost.
- Adopting AG2 as a runtime absent a measured collaboration gap.
- Importing Paperclip’s company/org model into Plugin Factory or using any private Control-Plane assumptions.
- Copying entire skill catalogs or adding a parallel skill system.
- Importing Hermes-specific routines/config into the repository.
- Duplicating Challenger with Premortem before an observed QA failure identifies a missing behavior.
- Adding MarkItDown or Crawl4AI without an owned input corpus and acceptance criteria (NO_CURRENT_REQUIREMENT).
- Adding CloakBrowser or Obscura for stealth/anti-detection alone.
- Adopting ContextGraph as a persistent service without a measured shared-memory requirement.
- Equating tool permissions, approvals, read-only mode, sandboxing, workspace scope, network egress, and credential handling.
- Starting a provider benchmark before hard call/turn and plugin/MCP isolation gates are evidenced.

## SOURCES

### Repository evidence

- Reviewed base: [develop revision 662ea3471b9e0a7a0ef34082a1539a8175c668b9](https://github.com/Doodooms/everything-copilot/tree/662ea3471b9e0a7a0ef34082a1539a8175c668b9)
- [Harness result model](https://github.com/Doodooms/everything-copilot/blob/662ea3471b9e0a7a0ef34082a1539a8175c668b9/harness_factory/models.py)
- [Harness adapters](https://github.com/Doodooms/everything-copilot/blob/662ea3471b9e0a7a0ef34082a1539a8175c668b9/harness_factory/adapters.py)
- [Evaluation and profile logic](https://github.com/Doodooms/everything-copilot/blob/662ea3471b9e0a7a0ef34082a1539a8175c668b9/harness_factory/evaluation.py)
- [Execution backend added by merged PR #4](https://github.com/Doodooms/everything-copilot/tree/662ea3471b9e0a7a0ef34082a1539a8175c668b9/harness_factory)
- Inputs reviewed: [core upgrade candidates](https://github.com/Doodooms/everything-copilot/blob/662ea3471b9e0a7a0ef34082a1539a8175c668b9/todos/gh-repos/core-upgrade.md), [security hardening input](https://github.com/Doodooms/everything-copilot/blob/662ea3471b9e0a7a0ef34082a1539a8175c668b9/todos/harness/security-hardening-input.md), [cost evaluation notes](https://github.com/Doodooms/everything-copilot/blob/662ea3471b9e0a7a0ef34082a1539a8175c668b9/todos/harness/cost-eval-opt.md), [current cost follow-ups](https://github.com/Doodooms/everything-copilot/blob/662ea3471b9e0a7a0ef34082a1539a8175c668b9/todos/backlog/2026-09-27/cost-eval-opt-followups.md), [baseline inventory](https://github.com/Doodooms/everything-copilot/blob/662ea3471b9e0a7a0ef34082a1539a8175c668b9/outputs/evals/baseline-inventory-r7.json).

### Public upstreams and official documentation

All external documentation below was checked on 2026-09-28; upstream default branches may change.

- [CodeBurn repository](https://github.com/getagentseal/codeburn), [Codex parser notes](https://github.com/getagentseal/codeburn/blob/main/docs/providers/codex.md), [yield correlation](https://github.com/getagentseal/codeburn/blob/main/docs/yield.md)
- [AG2 repository](https://github.com/ag2ai/ag2)
- [Paperclip repository](https://github.com/paperclipai/paperclip), [core concepts](https://github.com/paperclipai/paperclip/blob/master/docs/start/core-concepts.md), [lease/developer notes](https://github.com/paperclipai/paperclip/blob/master/doc/DEVELOPING.md)
- [addyosmani/agent-skills onboarding](https://github.com/addyosmani/agent-skills/blob/main/docs/getting-started.md), [skill anatomy](https://github.com/addyosmani/agent-skills/blob/main/docs/skill-anatomy.md), [developer onboarding](https://github.com/addyosmani/agent-skills/blob/main/docs/developer-onboarding.md)
- [google/skills](https://github.com/google/skills)
- [Salomondiei08/oh-my-hermes](https://github.com/Salomondiei08/oh-my-hermes)
- [Hi1talib1World/Premortem](https://github.com/Hi1talib1World/Premortem)
- [Microsoft MarkItDown](https://github.com/microsoft/markitdown)
- [Crawl4AI](https://github.com/unclecode/crawl4ai)
- [AllenMaxi/ContextGraph](https://github.com/AllenMaxi/ContextGraph)
- [CloakBrowser](https://github.com/CloakHQ/CloakBrowser)
- [Obscura](https://github.com/h4ckf0r0day/obscura)
- OpenAI, [Codex approvals and security](https://learn.chatgpt.com/docs/agent-approvals-security)
- GitHub, [Copilot CLI security](https://docs.github.com/en/copilot/concepts/agents/copilot-cli/about-copilot-cli), [local sandboxing](https://docs.github.com/en/copilot/concepts/agents/copilot-cli/understanding-local-sandboxing), [Agent Plugins](https://docs.github.com/en/copilot/concepts/agents/about-plugins)
- Anthropic, [Claude Code permissions](https://code.claude.com/docs/en/permissions), [sandboxing](https://code.claude.com/docs/en/sandboxing), [settings](https://code.claude.com/docs/en/settings)
- Historical allegation reviewed only as a third-party claim, not authoritative current behavior: [Adversa report](https://adversa.ai/blog/critical-claude-code-vulnerability-deny-rules-silently-bypassed-because-security-checks-cost-too-many-tokens/)

OVERNIGHT_RESEARCH: READY
