# PROMPT 3 — Expertise Pack `Inference-Eng`

Implémente :

```text
Inference-Eng
```

comme Expertise Pack spécialisé dans :

```text
model export
runtime inference
latency
memory
numerical equivalence
runtime optimization
```

Ne crée PAS de nouvel agent en v1.

Il doit principalement augmenter :

```text
ml-engineer
implementer
quality-assurance
devops
reviewer
```

---

## Skills

Limiter à 3 :

```text
model-export
inference-optimization
inference-validation
```

---

### `model-export`

Couvrir :

```text
PyTorch export
ONNX
runtime compatibility
dynamic/static shapes
operator support
model simplification
artifact metadata
export constraints
```

---

### `inference-optimization`

Couvrir :

```text
CPU inference
GPU inference when relevant
latency
throughput
memory
threading
preallocation
quantization
runtime selection
graph optimization
batching tradeoffs
```

Ne pas automatiquement recommander batching si la contrainte est single-request latency.

---

### `inference-validation`

Couvrir :

```text
numerical equivalence
tolerance design
output comparison
pre/post-processing equivalence
export regressions
performance regressions
input-shape coverage
```

---

## MCP tools

Ici les tools ont plus de valeur que les skills.

Prioriser :

```text
inference.model.inspect
inference.onnx.validate
inference.outputs.compare
inference.benchmark
inference.memory.profile
```

Si OpenVINO est disponible :

```text
inference.openvino.inspect
inference.openvino.benchmark
```

Mais ne pas rendre le pack dépendant d’OpenVINO.

---

## Tool outputs

Les benchmarks doivent retourner des données structurées :

```text
runtime
device
threads
input shape
warmup
iterations
median
p95
memory
throughput
environment
```

Ne jamais retourner simplement :

```text
"it seems faster"
```

---

## Projection

```text
ml-engineer:
  model-export
  inference-optimization
  inference-validation

quality-assurance:
  inference-validation
  benchmark/compare tools

implementer:
  model-export when integration requires it

devops:
  runtime inspection/benchmark tools

reviewer:
  read-only benchmark/equivalence evidence
```

---

## Ne PAS inclure

```text
full MLOps
autoscaling
model registry
drift monitoring
deployment orchestration
```

Ils appartiennent à un futur `MLOps` pack.

---

## Tests

Tester :

```text
export correctness
ONNX validity
numerical mismatch
static/dynamic shape issue
latency regression
memory regression
runtime incompatibility
```