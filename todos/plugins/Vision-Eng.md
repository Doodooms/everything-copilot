# PROMPT 2 — Expertise Pack `Vision-Eng`

Implémente :

```text
Vision-Eng
```

comme extension de :

```text
ML-Eng
```

Ne crée PAS de nouvel agent.

Le propriétaire principal reste :

```text
ml-engineer
```

## Objectif

Ajouter uniquement l’expertise Computer Vision générique à plus forte valeur.

Limiter la v1 à **4 skills maximum**.

---

## Skills

### `vision-data-design`

Couvrir :

```text
image dimensions
aspect ratios
resize
crop
padding
interpolation
antialiasing
normalization
augmentation
photometric vs geometric transformations
distribution shift introduced by preprocessing
```

---

### `vision-model-selection`

Couvrir :

```text
CNN
ConvNeXt
ViT
hybrid architectures

inductive biases
spatial locality
invariance
equivariance
resolution
dataset size
pretraining
latency/memory constraints
```

Ne pas produire un catalogue de modèles.

---

### `vision-representation-learning`

Couvrir :

```text
transfer learning
feature extraction
fine-tuning
self-supervised learning
distillation
representation quality
linear/KNN probes
embedding analysis
```

Rester générique.

---

### `vision-evaluation`

Couvrir :

```text
per-class/slice errors
resolution sensitivity
augmentation robustness
distribution shift
embedding diagnostics
visual failure analysis
prediction confidence
```

---

## Tools

Limiter le MCP à quelques opérations mesurables :

```text
vision.dataset.inspect
vision.transforms.inspect
vision.embeddings.analyze
vision.model.inspect
```

`vision.dataset.inspect` peut retourner par exemple :

```text
image count
resolution distribution
aspect-ratio distribution
channels
class distribution
duplicates/near-duplicates when feasible
```

`vision.transforms.inspect` doit aider à vérifier un pipeline de preprocessing/augmentation.

---

## Projection

Principalement :

```text
ml-engineer
quality-assurance
reviewer
```

Architect ne doit recevoir une skill Vision que si une décision affecte réellement l’architecture globale.

---

## Dépendance

Le manifest doit déclarer :

```text
requires:
  ml-eng
```

Le pack ne doit pas fonctionner comme un système ML parallèle.

---

## Ne PAS créer en v1

```text
object-detection
segmentation
geometric-registration
OCR
multimodal
vision-language-models
image-generation
```

Ces capabilities pourront devenir des extensions lorsque réellement nécessaires.

---

## Tests de routing

Exemples :

```text
"Quelle stratégie de resize utiliser ?"
→ vision-data-design

"ConvNeXt ou ViT pour ce dataset ?"
→ vision-model-selection

"Comment exploiter 500k images non labellisées ?"
→ vision-representation-learning

"Pourquoi le modèle échoue sur certaines résolutions ?"
→ vision-evaluation
```

Le pack doit rester très petit et très profond.