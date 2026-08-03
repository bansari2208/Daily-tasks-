# Day 10 Model Bake-off Scoring Rubric

Production evaluation rubric for candidate LLM models against the 20-item Golden Evaluation Dataset.

---

## Weighted Scoring Criteria & Metric Explanations

| Metric Name | Weight | Brief Explanation & Scoring Formula |
| --- | --- | --- |
| **Category Accuracy** | **25%** | Correct classification into target ticket category (Billing, Technical, Account, Security, Refund, Login, Password Reset, Network, Subscription, General). |
| **Priority Accuracy** | **20%** | Correct prediction of urgency level (HIGH, MEDIUM, LOW). |
| **JSON Validity** | **15%** | Percentage of LLM outputs that parse successfully as valid JSON syntax. |
| **Structured Output Reliability** | **15%** | Conformance of JSON keys/types to the target Pydantic schema without missing or malformed fields. |
| **Latency Score** | **10%** | Response speed performance score based on average latency (<150ms = 100%, <300ms = 80%, <700ms = 50%). |
| **Cost Efficiency** | **10%** | Operational cost score ($0.08/1k = 100%, $0.25/1k = 90%, $15.00/1k = 40%). |
| **Reasoning Correctness** | **5%** | Accuracy in assigning the appropriate complexity tier (EASY, MEDIUM, COMPLEX). |

---

## Composite Score Calculation

$$\text{Composite Score} = (0.25 \times \text{CatAcc}) + (0.20 \times \text{PrioAcc}) + (0.15 \times \text{JSONVal}) + (0.15 \times \text{StructRel}) + (0.10 \times \text{LatencyScore}) + (0.10 \times \text{CostScore}) + (0.05 \times \text{ReasCorr})$$
