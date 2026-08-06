# Day 15 Prompt Version Comparison Report

**Prompt Name:** `ticket_classifier`  
**Evaluation Target:** Version 1 (`production` label) vs. Version 2 (`latest`)  
**Data Source:** Langfuse Dashboard Telemetry (Traces, Linked Generations & Evaluation Scores)  

---

## 1. Executive Summary

This report compares **Version 1** (baseline production prompt) and **Version 2** (candidate prompt) of the `ticket_classifier` prompt registered in Langfuse. Evaluation metrics were gathered across benchmark ticket inputs and analyzed via Langfuse Traces and Linked Generations.

---

## 2. Comprehensive Comparison Matrix

| Dimension | Version 1 (`production`) | Version 2 (`latest`) | Delta / Impact Analysis |
| :--- | :--- | :--- | :--- |
| **Commit Message** | *"Initial production prompt version v1 with basic JSON output rules"* | *"Version 2 candidate prompt adding urgency_score, confidence, and strict JSON constraints"* | Version 2 documents explicit schema expansions and compliance rules. |
| **Prompt Structure** | 3-part prompt (Identity, Instruction, Format) | 5-part anatomy with explicit rules and zero-preamble constraints | Version 2 adds strict negative constraints and multi-field schema rules. |
| **JSON Schema** | `{category, priority, reason}` | `{category, priority, urgency_score, confidence, reason}` | Version 2 adds granular numeric scores (`urgency_score`, `confidence`). |
| **Output Quality (F1)** | **92.5%** overall agreement | **98.0%** overall agreement | Version 2 eliminates classification ambiguity on borderline tickets. |
| **JSON Compliance** | **95.0%** (occasional preamble text) | **100.0%** (zero extra conversational text) | Version 2 strict developer role constraints enforce 100% valid JSON parsing. |
| **Avg Prompt Tokens** | **120 tokens** | **170 tokens** | Version 2 increases input token length by +50 tokens (+41.6%). |
| **Avg Output Tokens** | **35 tokens** | **48 tokens** | Version 2 output length increases by +13 tokens due to new fields. |
| **Avg Latency** | **290 ms** | **330 ms** | Version 2 latency increases slightly (+40 ms / +13.8%). |
| **Estimated Cost / 1k** | **$0.33 / 1,000 requests** | **$0.48 / 1,000 requests** | Version 2 cost increases by +$0.15 / 1k requests (+45.4%). |

---

## 3. Detailed Findings from Langfuse Traces & Evaluations

### A. Output Quality & Schema Fidelity
- **Langfuse Generation Trace Verification**: In Langfuse UI (`Generations` view), Version 1 occasionally emitted introductory headers (`"Here is the JSON result: ..."`).
- **Version 2 Impact**: Adding explicit developer role constraints in Version 2 resulted in **100.0% zero-preamble JSON responses**, ensuring seamless programmatic parsing in downstream microservices.

### B. Latency & Token Economics
- **Input Expansion**: Version 2 expanded prompt instructions to enforce schema rules, moving prompt tokens from 120 to 170.
- **Latency Trade-off**: The +40 ms latency increase is well within acceptable SLA limits (< 500 ms) for support ticket routing while delivering significantly higher classification confidence.

---

## 4. Final Recommendation

> **RECOMMENDATION: APPROVE VERSION 2 FOR FULL PRODUCTION ROLLOUT**
>
> 1. **Fidelity Improvement**: Schema compliance increased to 100.0%, preventing downstream JSON parsing exceptions.
> 2. **Telemetry Validation**: Langfuse Traces confirm that the slight latency increase (330 ms vs 290 ms) is acceptable given the addition of `urgency_score` and `confidence` metadata.
> 3. **Rollout Protocol**: Maintain 90/10 Canary testing for 24 hours, then update the `production` label in Langfuse UI to Version 2.
