# Day 6 — Transformer Internals & Inference Control

This directory contains the Day 6 benchmarking and latency modules for analyzing LLM Transformer inference dynamics.

## Key Concepts
- **TTFT (Time To First Token)**: Prefill phase processing prompt tokens in parallel.
- **TPOT (Time Per Output Token)**: Decode phase generating output tokens auto-regressively.
- **Prefill vs Decode Dominance**: Large prompts spend >90% time in prefill; small prompts with long outputs spend >95% time in decode.

## How to Run

```bash
# Run Day 6 Benchmark
python benchmark.py

# Run Day 6 Streaming Latency Experiment
python experiment_latency.py
```
