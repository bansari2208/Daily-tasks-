# Day 12 Few-Shot Accuracy vs. Cost Report

**Experiment Random Seed**: `42`  
**Dataset**: 30 Labelled Customer Support Tickets

---

## Performance & Cost Comparison Table

| Strategy | Accuracy | Prompt Tokens | Completion Tokens | Total Tokens | Cost / 1k Requests | Latency (ms) | JSON Validity |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **Zero-shot** | 73.3% | 85 | 20 | 105 | $0.08 | 75.0 ms | 100.0% |
| **Three-shot** | **93.3%** | **310** | **20** | **330** | **$0.25** | **115.0 ms** | **100.0%** |
| **Eight-shot** | 96.7% | 780 | 20 | 800 | $0.62 | 195.0 ms | 100.0% |
