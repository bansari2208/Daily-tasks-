# Day 15 Canary Release Guide

This document explains the **90/10 Canary Release Architecture** for LLM prompt deployments using **Langfuse Prompt Management & Generation Tracing**.

---

## 1. Architectural Overview

A **Canary Release** safely introduces a new candidate prompt version to a small fraction of live traffic (e.g., 10%) while maintaining the established baseline prompt for the remaining traffic (90%).

```
                           ┌────────────────────────┐
                           │   Incoming Requests    │
                           └───────────┬────────────┘
                                       │
                                       ▼
                           ┌────────────────────────┐
                           │  Canary Prompt Router  │
                           └───────┬────────┬───────┘
                                   │        │
                   90% Traffic     │        │    10% Traffic
         ┌─────────────────────────┘        └────────────────────────┐
         ▼                                                           ▼
┌───────────────────────────────┐                   ┌───────────────────────────────┐
│ Production Prompt (v1)        │                   │ Candidate Prompt (v2)         │
│ Label: 'production'           │                   │ Label: 'latest' / Version: 2  │
└──────────────┬────────────────┘                   └──────────────┬────────────────┘
               │                                                   │
               ▼                                                   ▼
┌───────────────────────────────┐                   ┌───────────────────────────────┐
│ Langfuse Trace & Generation   │                   │ Langfuse Trace & Generation   │
│ Metadata: arm=PRODUCTION_90PCT│                   │ Metadata: arm=CANDIDATE_10PCT │
└───────────────────────────────┘                   └───────────────────────────────┘
```

---

## 2. Python SDK Canary Implementation

The 90/10 traffic routing is implemented cleanly using `CanaryPromptRouter` in [canary_release.py](file:///c:/Users/SVI/Desktop/Ticket%20Classifier/Day15/canary_release.py):

```python
class CanaryPromptRouter:
    def __init__(self, manager: LangfusePromptManager, canary_ratio: float = 0.10):
        self.manager = manager
        self.production_prompt = manager.get_prompt_by_label("ticket_classifier", label="production")
        self.candidate_prompt = manager.get_prompt_by_version("ticket_classifier", version=2)
        self.canary_ratio = canary_ratio  # 10% candidate, 90% production

    def select_prompt(self):
        if random.random() < self.canary_ratio:
            return self.candidate_prompt, "CANDIDATE_10PCT", 2
        return self.production_prompt, "PRODUCTION_90PCT", 1
```

---

## 3. Langfuse Observability & Tracing per Arm

Every LLM generation created during the canary release attaches the specific `prompt_obj` fetched from Langfuse:

```python
generation = trace.generation(
    name="llm_classifier_call",
    model="gpt-4.1-mini",
    prompt=prompt_obj,  # Links generation to exact Langfuse prompt version!
    metadata={"canary_arm": arm_name}
)
```

### Benefits of Langfuse Arm Tracing:
1. **Side-by-Side Performance Filtering**: In Langfuse UI (`Traces` tab), filter traces by `metadata.canary_arm = "CANDIDATE_10PCT"` or `metadata.canary_arm = "PRODUCTION_90PCT"`.
2. **Real-time Latency & Token Monitoring**: Compare latency distributions and token consumption live as traffic flows through both arms.
3. **Automated Error Rate Comparison**: Detect if Candidate v2 generates higher schema failure rates than Production v1 before full promotion.

---

## 4. Promotion & Demotion Criteria

| Metric | Candidate Threshold | Decision |
| :--- | :--- | :--- |
| **Schema Error Rate** | $\le 0.0\%$ | Pass -> Promote Candidate to 100% |
| **Latency Increase** | $\le +50\text{ ms}$ over baseline | Pass -> Promote Candidate |
| **Token Cost Increase** | Within budget limits ($+50\%$ max) | Pass -> Promote Candidate |
| **Schema Violation** | $> 1.0\%$ | **Fail** -> Immediately abort canary & revert traffic |
