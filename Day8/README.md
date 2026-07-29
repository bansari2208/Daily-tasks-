# Day 8 — Sampling, Determinism & Constrained Decoding

This directory contains the Day 8 experiments evaluating how decoding parameters, logprob confidence scoring, and output control mechanisms impact structured support ticket extraction quality.

## Key Concepts

- **Temperature & Top-p**: Controls sampling randomness during token selection (`0.0` – `0.2` for deterministic schema compliance).
- **Logprobs & Confidence Scoring**: Calculates model prediction certainty and routes low-confidence predictions (`< 0.80` or `< 0.70`) to **Human Review Required**.
- **Output Control Methods**: Compares `Prompt-only JSON`, `JSON Mode`, and `JSON Schema Mode` (Schema-Constrained Generation).
- **Two-Call Reasoning Workflow**: Free-form reasoning in Call 1 followed by structured JSON conversion in Call 2 for complex edge cases.

## Recommended Configuration

- **Temperature**: `0.2` (or `0.0`)
- **Top-p**: `0.9`
- **Output Method**: `JSON Schema Mode` (Schema-Constrained Generation)

## How to Run

```bash
# Run Day 8 Parameter Sweep & Reasoning Experiments
python experiment_decoding.py

# Run JSON Output Control Strategy Benchmark
python experiment_json_modes.py

# Run Confidence Scoring & Human Review Routing
python experiment_confidence.py
```
