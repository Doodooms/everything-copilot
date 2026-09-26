# Orchestration workflow graph

## use_case: risk_selected_delivery

Each gate is selected from task risk and acceptance policy; unselected phases are omitted and recorded, not treated as failures. This success path permits L0 work to go from focused implementation evidence directly to convergence, while a selected Reviewer gate requires current QA evidence. On failure or rejection, the Orchestrator routes to the evidence-indicated owner and reruns only invalidated selected gates.

```mermaid
flowchart TD
    intake["Orchestrator: classify and capture decisions"]
    spec_gate{"Material intent or evidence drift?"}
    spec["SDD: normalize the current specification"]
    architecture_gate{"Material solution-space decision?"}
    architect["Architect: map approved semantics"]
    plan_gate{"Material decomposition or sequencing?"}
    plan["Planner: define the required task DAG"]
    implement["Implementer: bounded implementation attempt"]
    qa_gate{"Independent QA selected?"}
    qa["Quality Assurance: diagnose/falsify"]
    review_gate{"Final Review selected?"}
    review["Reviewer: final technical acceptance"]
    converge["SDD child: reconcile current evidence"]
    remediation["Orchestrator: route a bounded correction to its owner"]
    targeted["Owner: revise and refresh only invalidated gates"]
    done["Orchestrator: report and perform authorized lifecycle"]
    blocked["Orchestrator: record blocker, owner, and next action"]
    intake --> spec_gate
    spec_gate -->|yes| spec --> architecture_gate
    spec_gate -->|no| architecture_gate
    architecture_gate -->|yes| architect --> plan_gate
    architecture_gate -->|no| plan_gate
    plan_gate -->|yes| plan --> implement
    plan_gate -->|no| implement
    implement --> qa_gate
    qa_gate -->|yes| qa --> review_gate
    qa_gate -->|not selected| converge
    review_gate -->|yes| review
    review_gate -->|no| converge
    qa -->|fail or blocked| remediation --> targeted
    review -->|reject or blocked| remediation
    targeted --> converge
    review -->|approve| converge
    converge -->|converged| done
    converge -->|gaps| blocked
```

The remediation node represents one new, versioned attempt, not an automatic loop. Record its owner and rerun only the selected gates invalidated by that revision; unresolved gaps return to the Orchestrator as blockers.
