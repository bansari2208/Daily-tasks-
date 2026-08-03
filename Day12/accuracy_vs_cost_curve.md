# Day 12 Accuracy vs. Cost Curve Analysis

**Experiment Random Seed**: `42`

---

## Accuracy vs Cost Data Table

| Examples (Shots) | Accuracy | Prompt Tokens | Completion Tokens | Total Tokens | Cost / 1k Requests |
| --- | --- | --- | --- | --- | --- |
| **0** | 73.3% | 85 | 20 | 105 | $0.08 |
| **3** | **93.3%** | **310** | **20** | **330** | **$0.25** |
| **8** | 96.7% | 780 | 20 | 800 | $0.62 |
| **12** | 96.7% | 1150 | 20 | 1170 | $0.91 |

---

## Key Conclusions & Recommendation

1. **Optimal Operating Point**: **3 Examples**
   - Delivers **93.3% accuracy** at **$0.25 / 1k requests** (330 tokens).
2. **Flat Line Diminishing Returns**:
   - Adding 4 more examples (8-shot $ightarrow$ 12-shot) adds +370 tokens (+47% cost) with **0.0% accuracy improvement**.
