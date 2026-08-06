# Day 15 Experiment Reproducibility Guide

This document defines the **Deterministic Experiment Reproducibility Protocol** using **Langfuse Prompt Management**.

---

## 1. The Challenge of Non-Deterministic LLM Systems

Machine learning and LLM engineering experiments often suffer from reproducibility failure ("drift") due to:
- Implicit prompt edits in source code without version tagging.
- Model provider hyperparameter changes (temperature, top_p, max_tokens).
- Missing audit logs linking inputs, prompt versions, and outputs.

---

## 2. The 6-Point Langfuse Reproducibility Lock

To guarantee 100% experiment reproducibility, every classification request must bind and record the following 6 parameters:

| Parameter | Configuration / Value | Purpose |
| :--- | :--- | :--- |
| **1. Prompt Name** | `ticket_classifier` | Identifies the functional prompt pipeline in Langfuse Registry. |
| **2. Prompt Version** | `Version 1` (or `Version 2`) | Immutable version ID in Langfuse prompt history. |
| **3. Model Name** | `gpt-4.1-mini` (or bedrock model spec) | Pinpoint model architecture family and provider version. |
| **4. Temperature** | `0.0` | Eliminates random sampling variance for deterministic output generation. |
| **5. Hyperparameters** | `top_p=1.0`, `max_tokens=256` | Locks sampling constraints and response boundary limits. |
| **6. Dynamic Variables** | `{"ticket": "<exact_customer_text>"}` | Binds runtime variable payload to prompt template. |

---

## 3. Reproduction Workflow

To re-run any past experiment or audit a historical classification decision:

1. **Query Langfuse Trace**: Retrieve the historical trace ID from Langfuse dashboard or local JSONL log.
2. **Fetch Exact Prompt Object**:
   ```python
   # Fetch exact historical version tagged in trace metadata
   historical_prompt = langfuse.get_prompt("ticket_classifier", version=trace_metadata["prompt_version"])
   ```
3. **Re-compile Input**:
   ```python
   compiled_input = historical_prompt.compile(ticket=trace_input["ticket"])
   ```
4. **Re-execute Deterministically**: Run inference using `temperature=0.0`. The model will output identical structural tokens.

---

## 4. Compliance & Auditability

By combining **Langfuse Prompt Versioning** with **OpenTelemetry-compatible JSONL logs**, engineers can mathematically verify output consistency across model upgrades, prompt revisions, and regression tests.
