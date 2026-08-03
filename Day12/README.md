# ⚡ Day 12 — Few-Shot Prompting, Example Selection & Cost Economics

This directory contains the complete self-contained implementation for **Day 12**: Few-Shot Prompting, Exemplar Selection, Ordering Sensitivity Detection, Cost-Accuracy Trade-off Analysis, Dynamic Similarity Retrieval, and Bad Examples Impact Analysis.

---

## 📌 1. Overview & Key Deliverables

1. **30-Item Labelled Evaluation Dataset (`labelled_dataset.json`)**:
   - 30 customer support tickets categorized into *Billing*, *Technical*, *Account*, *Security*, *Refund*, and *General*.
   - Includes 6 real-world production edge cases documented in `edge_cases.md` (ambiguous request, multiple issues, empty message, long log, mixed billing+tech, noisy text/emojis).
2. **Few-Shot Benchmarking (`run_fewshot_benchmark.py`)**:
   - Compares **Zero-shot** (73.3%), **Three-shot** (93.3%), and **Eight-shot** (96.7%) classification accuracy, token consumption, and cost.
   - Generates `accuracy_cost_report.md` and `results.json`.
3. **Ordering Sensitivity Experiment (`ordering_experiment.py`)**:
   - Evaluates identical 3-shot prompts across 3 distinct example orderings (Order A, Order B, Order C).
   - Detects a **6.6% accuracy spread** (> 5% threshold) and flags `[WARNING] Prompt is FRAGILE due to ordering sensitivity.`
4. **Accuracy vs. Cost Diminishing Returns (`cost_analysis.py`)**:
   - Evaluates 0, 3, 8, and 12 shots. Determines **Three-Shot** ($0.25 / 1k requests) as the optimal ROI operating point.
   - Generates `accuracy_vs_cost.csv` and `accuracy_vs_cost_curve.md`.
5. **Dynamic Few-Shot Selector (`dynamic_selector.py`)**:
   - Dynamically retrieves high-similarity exemplars for incoming tickets.
   - Outperforms static fixed examples (**96.7% vs 93.3% accuracy**) and declares `WINNER: Dynamic Few-shot`.
6. **Intentionally Bad Examples Analysis (`bad_examples_analysis.md`)**:
   - Demonstrates a **-40.0% accuracy drop** (53.3% vs 93.3%) caused by schema parsing contagion and wrong labels in `prompts/bad_examples.jinja2`.
7. **Reproducible Train/Val/Test Split (`revision_example.py`)**:
   - Uses `random.seed(42)` and list slicing to produce reproducible dataset splits.
8. **Interactive Live Demo (`demo_day12.py`)**:
   - 8-step interactive walkthrough script for project manager presentation.

---

## 📁 2. Directory Structure

```text
Day12/
├── output/
│   ├── benchmark_output.txt        # Saved terminal output for few-shot benchmark
│   ├── cost_analysis_output.txt    # Saved terminal output for cost analysis
│   ├── dynamic_selector_output.txt # Saved terminal output for dynamic selector
│   └── ordering_output.txt         # Saved terminal output for ordering test
├── prompts/
│   ├── bad_examples.jinja2          # Intentionally flawed exemplars
│   ├── eight_shot.jinja2            # 8-shot classification prompt template
│   ├── three_shot.jinja2            # 3-shot classification prompt template
│   └── zero_shot.jinja2             # Zero-shot prompt template
├── accuracy_cost_report.md          # Generated few-shot benchmark report
├── accuracy_vs_cost.csv            # Generated cost-accuracy data table
├── accuracy_vs_cost_curve.md       # Generated diminishing returns report
├── bad_examples_analysis.md        # Analysis of flawed few-shot exemplars
├── cost_analysis.py                # Script: Diminishing returns & cost curve
├── demo_day12.py                   # Script: Interactive live manager demo
├── dynamic_selector.py             # Script: Similarity-based dynamic retrieval
├── edge_cases.md                   # Breakdown of 6 production edge cases
├── labelled_dataset.json           # 30-item ground truth dataset
├── ordering_experiment.py          # Script: Order A/B/C sensitivity test
├── README.md                       # Day 12 documentation
├── results.json                    # Benchmark JSON metrics payload
├── revision_example.py             # Script: Reproducible random dataset split
└── run_fewshot_benchmark.py        # Script: Few-shot accuracy benchmark
```

---

## 🚀 3. Commands to Run Day 12

### A. Run Complete Interactive Live Demo (Sequential Manager Presentation)
```bash
python Day12/demo_day12.py
```

### B. Run Individual Task Scripts

#### 1. Few-Shot Accuracy & Cost Benchmark
```bash
python Day12/run_fewshot_benchmark.py
```

#### 2. Ordering Sensitivity Sensitivity Test
```bash
python Day12/ordering_experiment.py
```

#### 3. Diminishing Returns & Cost Analysis
```bash
python Day12/cost_analysis.py
```

#### 4. Dynamic Few-Shot Exemplar Selector
```bash
python Day12/dynamic_selector.py
```

#### 5. Reproducible Split Revision Exercise
```bash
python Day12/revision_example.py
```

---

## 🧪 4. Run Automated Pytest Suite

To run all automated unit tests covering Day 12:

```bash
python -m pytest tests/test_day12.py
```

---

## 📊 5. Summary Results Table

| Prompt Strategy | Accuracy | Prompt Tokens | Total Tokens | Cost / 1k Reqs | Latency | Status / Verdict |
| --- | --- | --- | --- | --- | --- | --- |
| **Zero-shot** | 73.3% | 85 | 105 | $0.08 | 75.0 ms | Baseline |
| **Three-shot (Fixed)** | 93.3% | 310 | 330 | $0.25 | 115.0 ms | **Optimal ROI** |
| **Eight-shot (Fixed)** | 96.7% | 780 | 800 | $0.62 | 195.0 ms | Diminishing Returns |
| **Dynamic Three-shot** | **96.7%** | **320** | **340** | **$0.26** | **122.0 ms** | **WINNER** |
| **Bad Exemplars (3-shot)**| 53.3% | 310 | 330 | $0.25 | 115.0 ms | -40% Accuracy Drop |
