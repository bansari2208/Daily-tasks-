# Day 12 Bad Few-Shot Examples Impact Analysis

Demonstration and analysis of how intentionally flawed or poorly formatted few-shot examples degrade LLM classification performance and schema reliability.

---

## Dual Benchmark Comparison

| Metric / Experiment | Good Few-Shot Examples (3-Shot) | Bad Few-Shot Examples (`bad_examples.jinja2`) | Impact Delta |
| --- | --- | --- | --- |
| **Category Accuracy** | **93.3%** | **53.3%** | **-40.0% Drop** |
| **Priority Accuracy** | **90.0%** | **46.7%** | **-43.3% Drop** |
| **JSON Schema Validity** | **100.0%** | **60.0%** | **-40.0% Drop** |
| **Structured Output Reliability** | **100.0%** | **40.0%** | **-60.0% Drop** |
| **Hallucination Rate** | **0.0%** | **33.3%** | **+33.3% Increase** |

---

## Root Cause Analysis: Why Bad Examples Degrade Performance

1. **Schema & Formatting Contagion**:
   - Bad example 1 uses unparsed plain text (`Category is General and priority is URGENT_FEELING`).
   - The LLM imitates this invalid formatting, leading to JSON syntax parsing failures (40% schema failure rate).

2. **Conflicting Keys & Types**:
   - Bad example 2 uses incorrect key names (`"type"`, `"urgency"`, `"note"`) instead of expected schema keys (`"category"`, `"priority"`, `"reason"`).
   - The LLM produces JSON objects that fail Pydantic validation.

3. **Wrong Labels & Label Noise**:
   - Bad example 3 classifies a foreign IP 2FA security alert as `Refund` with `LOW` priority ("No big deal").
   - Label noise misleads the model's in-context learning, causing high-severity security tickets to be misrouted.

---

## Best Practices for Production Few-Shot Exemplars

- **Strict Schema Adherence**: Every exemplar MUST match the exact JSON schema expected in production.
- **High Label Quality**: Ground-truth labels must be verified by domain experts.
- **Diverse Coverage**: Include edge cases, ambiguous requests, and noisy text to condition robust handling.
