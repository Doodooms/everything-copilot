# Self-maintaining capabilities

## Goal

Allow the system to keep canonical agents, skills and their documentation current as tools, APIs, models and best practices evolve.

The system should be able to detect that something may be stale or improvable, evaluate a candidate change, and update canonical content only when the improvement is justified.

The objective is not uncontrolled self-modification.

Preferred lifecycle:

```text
observe
→ detect possible drift or opportunity
→ create maintenance work
→ investigate
→ propose candidate change
→ evaluate
→ validate
→ adopt only with sufficient evidence
```

## Ownership

### Plugin Factory

Plugin Factory owns:

- canonical agent definitions;
- canonical skills;
- canonical documentation and references associated with them;
- ownership metadata linking agents to the capabilities and documentation they maintain;
- validation of canonical content;
- optimization/evaluation mechanisms for agents and skills;
- projections generated from canonical sources.

An agent may be declared responsible for maintaining specific skills or documentation, but this responsibility does not imply unrestricted write authority.

### Control-Plane

Control-Plane may later own:

- creation of maintenance Tasks;
- scheduling or triggering maintenance work;
- Attempts executing maintenance;
- authorization;
- evidence and provenance;
- approvals and checkpoints;
- historical results.

Control-Plane must not become the source of canonical agent or skill content.

## Ownership model

A future canonical definition may express that an agent is responsible for maintaining a set of resources.

Conceptually:

```text
AgentDefinition
└── maintains
    ├── skills
    ├── references
    └── documentation
```

Exact schema is intentionally deferred.

Do not introduce an ownership abstraction until at least one real maintenance workflow requires it.

## Possible maintenance triggers

Potential triggers include:

- dependency or tool version changes;
- API changes;
- model/backend version changes;
- capability changes;
- repeated runtime failures;
- validation regressions;
- increased token cost;
- increased latency;
- documentation becoming stale;
- deprecated APIs or tools;
- discovery of a potentially superior tool;
- security changes;
- changes in harness behavior;
- changes in target projection formats.

A trigger indicates that re-evaluation may be useful.

It does **not** imply that the current implementation must change.

## Important invariant

```text
newer != better
fresh != better
different != better
```

A candidate replacement should only be adopted when evidence supports the change.

Useful evidence may include:

- higher task success;
- lower failure rate;
- lower token consumption;
- lower latency;
- lower operational complexity;
- lower cost;
- improved security;
- additional required capability;
- improved compatibility;
- improved maintainability.

Do not migrate simply because a newer tool or version exists.

## Evaluation order

Prefer cheap and deterministic mechanisms before model calls.

Possible order:

```text
metadata/version inspection
→ deterministic compatibility checks
→ existing tests
→ targeted runtime probe
→ benchmark/evaluation
→ model-assisted analysis if necessary
→ external research only when needed
```

Avoid periodic LLM reviews of the entire system when deterministic checks can identify whether anything changed.

## Self-improvement boundary

Agents must not silently rewrite their own canonical definitions, skills or documentation.

Preferred behavior:

```text
agent observes problem/opportunity
→ maintenance candidate
→ proposed canonical change
→ independent validation where appropriate
→ policy/human gate where required
→ canonical update
```

Self-maintenance should remain auditable and reproducible.

## Independent validation

Where the change can affect execution quality, security or authorization, the agent proposing the change should not be the sole source of validation.

Examples:

```text
skill author
→ proposes optimized skill
→ evaluator compares old/new
```

or:

```text
tool maintainer
→ proposes migration
→ deterministic compatibility/runtime tests
→ independent validation
```

Do not require independent validation mechanically for every documentation typo or trivial maintenance operation.

Use it where the risk justifies it.

## Relationship with skill optimization

This mechanism should eventually integrate with existing skill/agent evaluation approaches.

Potential future flow:

```text
drift detected
→ candidate generated
→ routing evaluation
→ task completion evaluation
→ cost/token comparison
→ regression checks
→ adoption decision
```

Existing approaches such as routing evaluation and skill optimization may be reused rather than creating a second optimization framework.

## Documentation maintenance

Documentation should remain tied to the canonical capability it describes.

Possible checks:

- referenced tool/version still exists;
- documented command still works;
- external API/schema has changed;
- examples still validate;
- generated projections remain consistent with canonical content;
- referenced capabilities are still observed.

Documentation freshness alone is not sufficient proof that documentation is incorrect.

## Provenance

Maintenance changes should eventually retain enough provenance to answer:

```text
why was this maintenance Task created?
what observation triggered it?
which agent proposed the change?
which evaluation was performed?
what evidence justified adoption?
which canonical resources changed?
```

Do not store model memory as provenance.

Use durable Control-Plane events/artifacts when the workflow becomes integrated.

## Future directions

Potential future capabilities:

- dependency drift detection;
- backend/model capability drift;
- automatic regression detection;
- documentation freshness checks;
- candidate tool discovery;
- automatic skill optimization;
- cost/performance regression monitoring;
- periodic controlled evaluations;
- maintenance Tasks generated from capability observations.

These are directions, not current requirements.

## Do not build yet

Do not build:

- a generic autonomous self-improvement engine;
- an always-running LLM maintenance loop;
- a universal dependency intelligence system;
- automatic adoption of newly discovered tools;
- a second durable orchestration system inside Plugin Factory;
- a generic maintenance scheduler owned by Plugin Factory;
- unrestricted self-editing agents.

Introduce mechanisms only when concrete maintenance workflows demonstrate the need.

## Target principle

The desired system is:

```text
self-observing
→ self-proposing
→ self-evaluating
→ self-validating
→ conditionally self-improving
```

not:

```text
self-modifying without external evidence or control
```