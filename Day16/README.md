# Day 16: Reasoning Techniques & Task Decomposition (Part 1 - TODAY)

## Overview
This directory contains the Day 16 Expense Claim Review baseline implementation comparing:
1. **Single Prompt Baseline**: Evaluates claim parsing, arithmetic, policy rules, and verdict decision in a single step.
2. **Decomposed Pipeline**: Breaks down the review process into four distinct, single-responsibility typed stages.

## What Was Implemented Today
- `evaluation_set.py`: 30 expense claims with ground-truth expected verdicts and breach lists (includes the 8 mandatory hard cases).
- `evaluator.py`: Scoring module comparing verdict correctness and breach-list correctness.
- `decomposed_pipeline.py`: 4-stage pipeline (Extract Items -> Check Arithmetic -> Apply Rules -> Decide Verdict) using TypedDict handoffs.
- `single_prompt.py`: Single prompt baseline implementation.
- `run_experiments.py`: Experiment harness tracing runs in Langfuse and generating `results/day16_today_results.json`.
- `prompts/`: Standard prompt template files (`single_claim.txt`, `extract_items.txt`, `check_arithmetic.txt`, `apply_rules.txt`, `decide_verdict.txt`).

## How to Run Today's Experiment
```bash
python -m Day16.run_experiments
```
Or:
```bash
$env:PYTHONPATH="."; python Day16/run_experiments.py
```

## Langfuse Integration
- **Prompts registered in Langfuse Cloud**:
  - `expense_single`
  - `expense_extract_items`
  - `expense_check_arithmetic`
  - `expense_apply_rules`
  - `expense_decide_verdict`
- **Trace Structure**:
  - Single Prompt: One generation per claim run (`expense_single`).
  - Decomposed Pipeline: One parent trace (`decomposed_claim_pipeline`) containing 4 child generation observations (`expense_extract_items`, `expense_check_arithmetic`, `expense_apply_rules`, `expense_decide_verdict`).

## What Remains for Tomorrow
- Chain-of-Thought (CoT) experiments and comparison.
- Two-call reasoning + structured output experiments.
- Self-consistency, Tree-of-Thought, and budget optimization.
