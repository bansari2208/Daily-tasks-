# Day 16: Reasoning Techniques & Task Decomposition — Chain-of-Thought Performance Prediction

**Date:** 2026-08-12  
**Status:** Pre-Experiment Prediction (Immutable)

---

## 1. Targeted Jobs Under Evaluation

The experiment evaluates three core expense review tasks under two prompt configurations:
- **Normal Prompt Variant**: Direct, constrained task instructions requiring structured output.
- **Reasoning-Enabled Prompt Variant**: Instructs the model to generate explicit step-by-step reasoning / chain-of-thought prior to producing the result.

The three jobs are:
1. **Job 1**: Line Item Extraction (`expense_extract_items`)
2. **Job 2**: Minor Rule Violation Classification (`expense_decide_verdict` for REVIEW vs. REJECT)
3. **Job 3**: Arithmetic Sum Check (`expense_check_arithmetic`)

---

## 2. Predicted Degradation & Hypothesis

> **Primary Prediction**: **Job 3 (Arithmetic Check)** and **Job 2 (Minor Violation Decision)** will experience degradation under reasoning-enabled prompts.

### Detailed Rationale & Expected Mechanisms:

1. **Job 3 (Arithmetic Sum Check)**:
   - **Mechanism**: LLMs do not execute numeric arithmetic natively in standard generation mode; they perform next-token prediction over text representations of numbers. When forced to produce natural language step-by-step math reasoning (e.g. *"First, adding 2500.0 USD to 2000.0 USD gives 4500.0 USD..."*), the model generates verbose tokens where intermediate sub-totals can drift or hallucinate rounding errors.
   - **Expected Degradation**: Increased token count, 2x–4x higher latency, higher financial cost, and a higher risk of arithmetic miscalculation compared to direct calculation logic.

2. **Job 2 (Minor Rule Violation Verdict - REJECT vs. REVIEW)**:
   - **Mechanism**: Verbalizing step-by-step policy evaluations creates a cognitive bias towards over-enforcement. When the model writes out verbose justifications (e.g. *"The meal claim of 1,250 USD exceeds the 1,200 USD daily cap. Since a rule has been breached, the claim must be rejected..."*), it tends to collapse the distinction between **minor rule breaches** (which require human `REVIEW`) and **hard policy prohibitions** (which warrant immediate `REJECT`).
   - **Expected Degradation**: Decreased verdict accuracy due to false REJECT classifications on minor overages, alongside increased latency and token usage.

3. **Job 1 (Line Item Extraction)**:
   - **Expected Behavior**: Accuracy will remain stable or slightly improve, but latency and token overhead will increase significantly without functional benefit.

---

## 3. Benchmark Metrics to Measure

- **Verdict Accuracy** (%)
- **Breach Accuracy** (%)
- **Overall Accuracy** (%)
- **P95 Latency** (ms)
- **Token Usage & Financial Cost** ($ per 1,000 claims)

---

*This prediction is logged prior to executing the Chain-of-Thought benchmarking suite.*
