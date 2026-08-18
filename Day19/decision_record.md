# Architectural Decision Record (ADR) — Day 19: Systematic Prompt Optimisation

## 1. Context & Goal
The objective is to establish a repeatable, quantifiable prompt experiment framework for **Customer Support Ticket Classification**. The framework evaluates multiple prompt variants against a fixed evaluation set, categorizes misclassifications, performs targeted prompt optimizations, measures statistical variance, and tracks metrics in Langfuse.

---

## 2. Fixed Evaluation Dataset & Model Specs
* **Task**: Single-label Customer Support Ticket Classification
* **Categories (4)**: `Billing`, `Technical`, `Account`, `General`
* **Dataset**: 20 fixed evaluation tickets (5 items per category)
* **Reproducibility**: Dataset, prompt templates, scoring rules, and statistical definitions are fixed. Output variance is measured across 3 repeated runs.

---

## 3. Benchmark Comparison Table

| Variant Name | Prompt Strategy | Accuracy (%) | Failures |
| --- | --- | :---: | :---: |
| **Baseline** | Unconstrained simple prompt (Anchor) | **75.0%** | 5 |
| **V2** | Structured JSON schema instructions | **80.0%** | 4 |
| **V3** | Few-shot classification examples | **90.0%** | 2 |
| **V4** | Chain-of-Thought (CoT) step-by-step reasoning | **90.0%** | 2 |
| **Optimized_Billing** | Targeted rule for `Billing` failures | **100.0%** | 0 |

---

## 4. Failure Category Analysis & Optimization Proof

1. **Initial Largest Failure Class**: `Billing` (3 errors out of 5 total failures).
2. **Targeted Change Made**: Appended explicit disambiguation rules for `Billing` edge cases.
3. **Before vs After Failure Count**: `Billing` failures reduced from **3** to **0**.
4. **Verification**: `Failure Reduction Verified = True` (0 < 3).
5. **Absolute Accuracy Gain**: **+25.0 percentage points** (75.0% -> 100.0%).

---

## 5. Statistical Variance Profile (3 Repeated Runs)

Evaluated on winning prompt `Optimized_Billing`:
* **Run Scores**: `[100.0, 100.0, 95.0]`
* **Mean**: `98.33%`
* **Median**: `100.0%`
* **Sample Standard Deviation ($N-1$)**: `2.89`
* **Range (Spread)**: `5.0 percentage points`

---

## 6. Observability & Tooling Assessment

### Langfuse Telemetry:
All variant runs and repeated evaluations were transmitted to Langfuse, logging prompt versions, latency, and `accuracy` scores.

### Promptfoo Evaluation Assessment:
* **Status**: Promptfoo configuration created, but execution could not be completed because the CLI/environment was unavailable.
* **Setup**: Configured in `Day19/promptfoo.yaml`.
* **Utility**: Excellent for matrix comparisons and visual diffs across local prompt versions.
* **Differences**: Custom Python runner provides granular statistical modeling and custom telemetry, whereas Promptfoo provides generic assertion assertions.
* **Stack Recommendation**: Recommended as a secondary local CI/CD CLI test tool alongside the primary Python experiment runner.

---

## 7. Stopping Condition & Engineering Recommendation

### Stopping Rule (Prompt Ceiling):
Stop prompt optimization when consecutive controlled prompt changes yield $< 2.0$ percentage points improvement on the fixed evaluation set.

### Final Recommendation:
On the current fixed evaluation set, the optimized prompt reached 100% accuracy. Further prompt tuning on this dataset is unlikely to provide meaningful measurable gains. Broader real-world evaluation should be performed before deciding whether to move to RAG, fine-tuning, a different model, or a product/workflow change.

---

## 8. Reproducibility Instructions

To reproduce this benchmark and comparison table:

```powershell
# 1. Ensure Python virtual environment is active
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

# 2. Run unit test suite
.\.venv\Scripts\python.exe -m unittest discover -s Day19/tests -v

# 3. Execute master benchmark pipeline
python Day19/run_day19.py
```
