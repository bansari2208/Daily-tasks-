# Day 12 Production Edge Cases & Failure Mode Analysis

Documentation of 6 realistic production edge cases incorporated into the 30-item labelled evaluation dataset (`labelled_dataset.json`).

---

## Edge Case Breakdown

| ID | Edge Case Category | Input Ticket Text Sample | Expected Classification | Failure Mode & Risk | Mitigation Strategy |
| --- | --- | --- | --- | --- | --- |
| **25** | **Ambiguous Request** | *"System acting strange, not sure what happened, please check."* | Category: `General`<br>Priority: `LOW` | Model may hallucinate specific technical root causes or misclassify as high priority. | Prompt instruction to route vague inputs to `General` with low urgency. |
| **26** | **Multiple Issues** | *"Password reset email link expired AND credit card charged twice for annual plan."* | Category: `Billing`<br>Priority: `HIGH` | Model may pick only the first minor issue (password reset) and miss high-impact billing duplicate. | Priority rules enforce selecting the highest-severity issue (`Billing` / `HIGH`). |
| **27** | **Empty Message** | *"   "* | Category: `General`<br>Priority: `LOW` | Whitespace or empty input causes LLM parsing exceptions or infinite retries. | Pre-processing validation returns default safe classification fallback. |
| **28** | **Very Long Ticket** | *"Our enterprise deployment failed during schema migration... KeyError 'tenant_id'... 500 users blocked..."* | Category: `Technical`<br>Priority: `HIGH` | Long text (>200 chars) increases prompt token cost and may dilute key error signals. | Few-shot examples demonstrate extracting core technical root cause from long logs. |
| **29** | **Mixed Billing + Tech** | *"Payment Gateway returned 500 error during checkout and deducted $99 from my account."* | Category: `Billing`<br>Priority: `HIGH` | Blended technical error (500) and financial deduction ($99) causes category ambiguity. | Explicit few-shot rule: Financial loss/deduction takes precedence over HTTP error codes. |
| **30** | **Noisy / Typos / Emojis** | *"HELLOOO!! 🚨🚨 my billin is so wrong bro pls fix asap 💳💸"* | Category: `Billing`<br>Priority: `HIGH` | Excessive emojis (`🚨🚨💳💸`), slang ("bro"), and typos ("billin") degrade tokenization. | Few-shot examples train model to normalize informal noisy text to structured JSON. |
