# Day 16: Reasoning Techniques & Task Decomposition

Welcome to **Day 16**! This module focuses on expense claim evaluation using two distinct architecture patterns: a **Single-Prompt Baseline** and a **4-Stage Decomposed Pipeline** with typed handoffs and full **Langfuse Cloud** observability.

---

## 1. Overview & Objective

The objective of Day 16 is to process and audit corporate expense claims against five strict policy rules, determine the appropriate verdict (`APPROVE`, `REJECT`, or `REVIEW`), and identify all rule breaches cleanly.

### The Five Policy Rules:
1. **Meals**: Maximum **1,200 per person per day**. Overages trigger `REVIEW` (or `REJECT`).
2. **Travel**: **Economy class only**, and maximum **15,000 per trip**. Non-economy class or over-limit triggers `REJECT`.
3. **Receipt Requirement**: Any single item **above 5,000** requires a valid receipt reference. Missing receipt triggers `REJECT`.
4. **Expense Date Recency**: Every expense must be dated **within 30 days** of submission. Dated > 30 days triggers `REJECT`.
5. **Total Claim Cap**: Total per claim is capped at **50,000**. Exceeding cap triggers `REJECT`.
6. **Arithmetic & Currency Checks**: Stated total must match the sum of line items; claims mixing multiple currencies trigger `REJECT`.

---

## 2. Architecture & Decomposition Flow

```
day16_decomposed_pipeline (Parent Span)
    │
    ├── 1. expense_extract_items (Stage 1: Line item extraction)
    │
    ├── 2. expense_check_arithmetic (Stage 2: Sum vs stated total check)
    │
    ├── 3. expense_apply_rules (Stage 3: Policy rule evaluation)
    │
    └── 4. expense_decide_verdict (Stage 4: Final verdict & breach list assembly)
```

---

## 3. The 30-Claim Evaluation Set & 8 Hard Cases

The benchmark dataset consists of **30 ground-truth claims** stored in [evaluation_set.py](file:///c:/Users/SVI/Desktop/Ticket%20Classifier/Day16/evaluation_set.py).

### The 8 Mandatory Hard Cases:
1. **Hard Case 1 (`claim_001`)**: Line items do not add up to stated total (stated 5,000 vs sum 4,500).
2. **Hard Case 2 (`claim_002`)**: Meal claim slightly above daily cap (1,250 vs 1,200 limit).
3. **Hard Case 3 (`claim_003`)**: Multi-rule double breach (meal 1,350 > 1,200 AND equipment 7,000 without receipt).
4. **Hard Case 4 (`claim_004`)**: Expense dated 31 days before submission.
5. **Hard Case 5 (`claim_005`)**: Laptop 6,500 with no receipt reference.
6. **Hard Case 6 (`claim_006`)**: Mixed currencies (USD and EUR in same claim).
7. **Hard Case 7 (`claim_007`)**: Claim under 50,000 cap containing Business Class travel.
8. **Hard Case 8 (`claim_008`)**: Clean claim that must pass (`APPROVE`, zero breaches).

---

## 4. Langfuse Manager Demo Guide

Use this simple step-by-step walkthrough to demonstrate the Day 16 system to your manager in Langfuse Cloud:

### STEP 1: Show the 30-Item Evaluation Dataset
1. Open your Langfuse Cloud project dashboard.
2. Go to **Datasets** $\rightarrow$ **`expense_claim_evaluation_v1`**.
3. Point out that the dataset contains **exactly 30 items** (30 unique `claim_id` values, 0 duplicates, 8 hard cases).
4. Show an item's **Input**, **Expected Output** (`{"verdict": "...", "breaches": [...]}`), and **Metadata** (`claim_id`, `hard_case`).

### STEP 2: Show Dataset Experiments & Verification
1. Go to **Datasets** $\rightarrow$ **`expense_claim_evaluation_v1`** $\rightarrow$ **Experiment Runs** tab.
2. Show the official 30-item experiment runs:
   - `day16_single_prompt`
   - `day16_decomposed_pipeline`
   - `day16_two_call`
   - `day16_self_consistency_3`
   - `day16_self_consistency_5`
3. Verify that **30 items were executed** for each experiment run.
4. *(Note: `test_run_1` was an old manual SDK test run containing 2 items used during early setup, and should be ignored).*

### STEP 3: Show Experiment Outputs & Evaluation Scores
1. Click open `day16_decomposed_pipeline`.
2. Show how actual outputs are compared against manually defined expected outputs.
3. Show logged scores: `verdict_accuracy`, `breach_accuracy`, `overall_accuracy`, `hard_case_verdict_accuracy`, `verdict_correct`, `breach_list_correct`, and `overall_pass`.

### STEP 4: Show the 4-Stage Decomposed Pipeline Trace
1. Go to **Tracing** in Langfuse UI.
2. Click a trace for `day16_decomposed_pipeline`.
3. Show the parent span and expand the 4 child stage observations:
   - `expense_extract_items`
   - `expense_check_arithmetic`
   - `expense_apply_rules`
   - `expense_decide_verdict`
4. Show how data flows cleanly through typed handoffs (`ExtractedClaim` $\rightarrow$ `ArithmeticResult` $\rightarrow$ `RuleCheckResult` $\rightarrow$ `FinalDecision`).

### STEP 5: Show Versioned Prompts in Prompt Management
1. Go to **Prompts** in Langfuse UI.
2. Show versioned production prompts: `expense_single`, `expense_extract_items`, `expense_check_arithmetic`, `expense_apply_rules`, and `expense_decide_verdict`.

### STEP 6: Show Final Architecture Recommendation
- **Winning Architecture:** `Decomposed Pipeline` (100.0% Hard-Case Verdict Accuracy, 27.3 ms P95 Latency, $0.72 per 1,000 claims).

---

## 5. Summary of Experiments & Benchmark Results

| Experiment Name | Verdict Acc | Breach Acc | Overall Acc | Hard Verdict Acc | P95 Latency | Cost / 1k Claims |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| `day16_single_prompt` | 96.7% | 96.7% | 96.7% | 100.0% | 20.0 ms | $0.3500 |
| `day16_decomposed_pipeline` | **96.7%** | **96.7%** | **96.7%** | **100.0%** | **27.3 ms** | **$0.7200** |
| `day16_two_call` | 96.7% | 96.7% | 96.7% | 100.0% | 386.3 ms | $0.8500 |
| `day16_self_consistency_3` | 96.7% | 96.7% | 96.7% | 100.0% | 113.3 ms | $2.1600 |
| `day16_self_consistency_5` | 96.7% | 96.7% | 96.7% | 100.0% | 195.8 ms | $3.6000 |

---

## 6. How to Run & Verify

### Step 1: Run Offline Unit Tests
```bash
python -m pytest Day16/tests/test_day16.py -v
```

### Step 2: Verify Langfuse Dataset Integrity (Local vs Cloud)
```bash
python Day16/verify_langfuse_dataset.py
```

### Step 3: Verify Langfuse Dataset Experiment Runs
```bash
python Day16/verify_langfuse_experiments.py
```

### Step 4: Execute Master Experiment Suite & Generate Reports
```bash
python Day16/run_all_experiments.py
```

---

## 7. Artifact Locations
- **JSON Final Report**: [day16_final_report.json](file:///c:/Users/SVI/Desktop/Ticket%20Classifier/Day16/results/day16_final_report.json)
- **Markdown Final Report**: [day16_final_report.md](file:///c:/Users/SVI/Desktop/Ticket%20Classifier/Day16/results/day16_final_report.md)
- **Dataset Verification Script**: [verify_langfuse_dataset.py](file:///c:/Users/SVI/Desktop/Ticket%20Classifier/Day16/verify_langfuse_dataset.py)
- **Experiments Verification Script**: [verify_langfuse_experiments.py](file:///c:/Users/SVI/Desktop/Ticket%20Classifier/Day16/verify_langfuse_experiments.py)
