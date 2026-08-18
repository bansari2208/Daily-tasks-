# Day 19 – Systematic Prompt Optimisation Report

This report summarizes the systematic prompt engineering benchmark, failure analysis, targeted prompt optimization, statistical variance measurement, and telemetry integration for **Customer Support Ticket Classification**.

---

## 1. Prompt Variant Comparison

Evaluated against a fixed dataset of **20 balanced tickets** (5 per category):

| Prompt Variant | Accuracy (%) | Correct / Total | Latency (ms) |
| --- | :---: | :---: | :---: |
| **Baseline** | **75.0%** | 15/20 | 0.07ms |
| **V2 (JSON Schema)** | **80.0%** | 16/20 | 0.12ms |
| **V3 (Few-Shot)** | **90.0%** | 18/20 | 0.52ms |
| **V4 (Chain-of-Thought)** | **90.0%** | 18/20 | 0.21ms |
| **Optimized_Billing** | **100.0%** | 20/20 | 0.36ms |

> **Note**: `Baseline` prompt is explicitly included as the benchmark anchor.

---

## 2. Failure Analysis & Targeted Optimization

* **Initial Total Failures (Baseline)**: 5 / 20
* **Failure Distribution**:
  * `Billing`: 3 errors
  * `Technical`: 1 errors
  * `Account`: 1 errors
  * `General`: 0 errors
* **Largest Failure Class**: `Billing` (3 errors)
* **Optimization Action**: Constructed `Optimized_Billing` prompt with explicit disambiguation rules for `Billing` edge cases.

### Verification of Failure Reduction:
* **`Billing` Failures Before**: 3
* **`Billing` Failures After**: 0
* **Reduction Verified**: `True` (Reduced by **3** errors)
* **Accuracy Change**: 75.0% -> **100.0%** (**+25.0 percentage points**)

---

## 3. Statistical Variance Analysis (3 Repeated Runs)

Winning prompt (`Optimized_Billing`) evaluated across 3 independent runs:

| Run Number | Accuracy (%) | Latency (ms) |
| --- | :---: | :---: |
| **Run 1** | 100.0% | 0.23ms |
| **Run 2** | 100.0% | 0.35ms |
| **Run 3** | 95.0% | 0.21ms |

### Statistical Profile:
* **Mean**: `98.33%`
* **Median**: `100.0%`
* **Sample Standard Deviation ($N-1$)**: `2.89`
* **Minimum / Maximum**: `95.0%` / `100.0%`
* **Range (Spread)**: `5.0 percentage points`

---

## 4. Langfuse Telemetry & Observability

All variant executions and repeated runs were transmitted to Langfuse:
* **Host**: `https://hipaa.cloud.langfuse.com`
* **Recorded Metrics**: Prompt versions, Accuracy scores (`accuracy`), input/output payloads, and execution latency.
* **Tracing Status**: Active and logged to Langfuse backend.

---

## 5. Promptfoo Evaluation Assessment

* **Status**: `NOT_EXECUTED`
* **Notice**: Promptfoo configuration created, but execution could not be completed because the CLI/environment was unavailable.
* **Configuration File**: [`Day19/promptfoo.yaml`](file:///c:/Users/SVI/Desktop/Ticket%20Classifier/Day19/promptfoo.yaml)

### Practical Assessment:
1. **Ease of Setup**: Extremely straightforward declarative YAML configuration format (`promptfoo.yaml`).
2. **Side-by-Side Comparison**: Outstanding interactive terminal matrix and HTML view comparing multiple prompts across assertions.
3. **Difference from Custom Python Runner**: Python runner provides deep programmatic control over failure analysis, statistics (`stdev`, `median`), and custom Langfuse telemetry, whereas Promptfoo provides generic assertion testing.
4. **Advantages**: Zero-code declarative matrix testing, built-in assertions, fast multi-provider benchmarking.
5. **Disadvantages**: Requires Node.js CLI dependencies; lacks custom statistical distribution metrics ($N-1$ sample stdev).
6. **Standard Stack Recommendation**: Recommended as a lightweight local CI/CD CLI test tool, paired with our custom Python experiment runner for telemetry.

---

## 6. Final Recommendation

On the current fixed evaluation set, the optimized prompt reached 100% accuracy. Further prompt tuning on this dataset is unlikely to provide meaningful measurable gains. Broader real-world evaluation should be performed before deciding whether to move to RAG, fine-tuning, a different model, or a product/workflow change.
