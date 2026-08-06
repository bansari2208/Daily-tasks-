# Day 15 Rollback Procedure Guide (Langfuse Zero-Code Rollback)

This guide documents how **Langfuse Prompt Management** enables **Zero-Code Instant Rollbacks** without requiring application code changes, redeployments, or service restarts.

---

## 1. Concept: Label-Based Decoupling

In traditional software architectures, prompt templates are hardcoded inside Python code or committed to git repositories. Rolling back a prompt requires:
1. Reverting a git commit.
2. Passing code reviews.
3. Triggering CI/CD build pipelines.
4. Redeploying microservices (5–30 minutes downtime risk).

With **Langfuse Prompt Registry**, application code retrieves prompts dynamically by label:

```python
# Application code NEVER hardcodes prompt versions!
prompt = langfuse.get_prompt("ticket_classifier", label="production")
```

The application executes whatever prompt version is tagged with the `production` label in Langfuse.

---

## 2. Step-by-Step Rollback Workflow in Langfuse UI

When a newly promoted prompt (e.g. Version 2) exhibits regression in production (e.g. unexpected latency spikes, schema errors, or degraded quality):

### Step 1: Open Langfuse Prompt Management
1. Log into your **Langfuse Dashboard**.
2. Navigate to **Prompts** in the left sidebar menu.
3. Select the target prompt: `ticket_classifier`.

### Step 2: Access Version History & Labels
1. Click on the **Versions** tab.
2. Locate **Version 1** (the previous known stable baseline) and **Version 2** (the newly promoted version).

### Step 3: Re-assign the `production` Label
1. Click the **Labels** dropdown or menu on **Version 1**.
2. Select or add the label: `production`.
3. Langfuse will automatically remove the `production` label from Version 2 and attach it to Version 1.

---

## 3. Instant Code Effect Verification

Because the Python backend requests prompts using `label="production"`, the next incoming LLM request instantly fetches **Version 1**:

```bash
# Verification snippet in Python:
manager = LangfusePromptManager()
active_prompt = manager.get_prompt_by_label("ticket_classifier", label="production")
print(f"Active Production Prompt Version: {active_prompt.version}")
# Output: Active Production Prompt Version: 1
```

* **Downtime:** 0 seconds.
* **Code Deployment Required:** None.
* **Rollback Time:** < 5 seconds.

---

## 4. Langfuse Audit Logging & Safety

Every label reassignment in Langfuse generates an immutable audit record in Langfuse:
- **User identity** who triggered the label change.
- **Timestamp** of the label move.
- **Previous label state** vs **New label state**.

This guarantees complete traceability and compliance auditing across prompt releases.
