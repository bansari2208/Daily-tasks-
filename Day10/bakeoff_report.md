# Day 10 Model Bake-off Selection Memo

## 1. Recommendation & Winner
- **Primary Production Winner**: **GPT-4.1 Mini** (Model B)
  - *Overall Score*: **95.0%**
  - *Accuracy*: **95.0%** | *Latency*: **115.0 ms** | *Cost*: **$0.25 / 1k requests**
  - *Verdict*: Delivers enterprise-grade classification accuracy and 100% schema reliability at minimal cost.

- **Runner-Up**: **GPT-4.1 Nano** (Model A)
  - *Overall Score*: **87.5%** | *Latency*: **62.5 ms** | *Cost*: **$0.08 / 1k requests**
  - *Verdict*: Excellent choice for high-volume routine ticket classification.

- **Worst Performer**: **Mock Open Model** (Model D)
  - *Overall Score*: **73.8%** | *Schema Reliability*: **80.0%**
  - *Verdict*: Unacceptable for production due to schema parsing failures and lower accuracy.

---

## 2. Key Trade-offs & Considerations
1. **Budget Considerations**: `o3-mini` costs $15.00/1k requests (60x more expensive than `GPT-4.1 Mini`). Reserved strictly for complex multi-step reasoning escalation.
2. **Latency Considerations**: `GPT-4.1 Mini` responds in 115ms (well under our 500ms production SLA threshold).
3. **Quality & Structured Output**: Both `GPT-4.1 Mini` and `GPT-4.1 Nano` achieved 100% JSON schema validity.

---

## 3. Conditions to Revisit Decision
Revisit model selection if:
- Average latency of `GPT-4.1 Mini` exceeds 500ms over 24 hours.
- Total LLM monthly cost doubles baseline budget.
- Complex multi-step tickets exceed 30% of total incoming volume.
