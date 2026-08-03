# Day 10 Inference Control Playbook Extension

Production guardrails, hyperparameter defaults, and escalation rules for ticket classifier deployment.

---

## 1. Task-Level Model & Hyperparameter Defaults

| Task Category | Default Model | Default Temp | Default Top-p | Max Latency SLA | Max Cost / Request |
| --- | --- | --- | --- | --- | --- |
| **Simple Classification** | `GPT-4.1 Nano` | `0.0` | `0.7` | `200 ms` | `$0.0001` |
| **Billing & Invoices** | `GPT-4.1 Mini` | `0.0` | `0.7` | `300 ms` | `$0.0005` |
| **Technical Errors** | `GPT-4.1 Mini` | `0.0` | `0.7` | `300 ms` | `$0.0005` |
| **Multi-Step Reasoning** | `o3-mini` | `0.2` | `0.7` | `800 ms` | `$0.0050` |

---

## 2. Fallback & Escalation Rules

1. **Provider Resilience Fallback Strategy**:
   - Primary Provider (`MockPrimary`) $\rightarrow$ Fallback Provider (`MockFallback`).
   - If 3 consecutive requests fail, trigger **Circuit Breaker** to OPEN state for 30 seconds.

2. **Reasoning Model Escalation Triggers**:
   - Escalate to `o3-mini` **ONLY** when:
     - Ticket text contains multi-step keywords (`refund`, `invoice 404`, `charged twice`, `tax reconciliation`).
     - Ticket length exceeds 180 characters with multiple distinct user requests.
     - Categorization confidence score drops below `0.80`.

3. **Cost & Latency Guardrails**:
   - Maximum allowed latency per request: **500 ms** (routine) / **800 ms** (reasoning).
   - Maximum allowed retry count: **2 retries**.
   - Maximum cost ceiling per request: **$0.0050**.
