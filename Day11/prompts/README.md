# Day 11 Prompts Architecture & Role Separation Guide

## 1. Metadata & Versioning (Item 1)
- **Version**: v1.0.0
- **Author**: Staff AI Engineer
- **Created Date**: 2026-08-02
- **Purpose**: Enterprise Customer Support Ticket Classification & Structured Output

---

## 2. Prompts Overview

### Original Weak Prompt (`original_prompt.jinja2`)
```jinja2
Classify ticket: {{ ticket_text }} into Category, Priority, Urgency.
```
*Drawbacks*: Lacks role boundaries, lacks output schema constraints, susceptible to conversational preamble.

### Production 5-Part Anatomy Prompt (`production_prompt.jinja2`)
Structures the request into 5 explicit components:
1. **Instruction**: Task definition & rules.
2. **Context**: Domain ticketing background.
3. **Input**: Dynamic ticket payload (`{{ ticket_text }}`).
4. **Output Specification**: Auto-derived JSON schema from Pydantic model (`generate_schema_specification`).
5. **Example (Few-Shot)**: Standardized exemplar input/output payload.

---

## 3. Message Role Separation Matrix

| Message Role | Purpose | Content | Why It Belongs Here |
| :--- | :--- | :--- | :--- |
| **System** | Identity & Global Persona | Persona, permanent rules | Persists across conversations; sets immutable behavior. |
| **Developer** | Output Rules & Constraints | JSON schema spec, constraints | Developer role isolates system rules from user input. |
| **Assistant** | Few-Shot Exemplar | Target JSON completion example | Simulates past successful completion for format compliance. |
| **User** | Dynamic Input Payload | Dynamic customer ticket text | Isolates untrusted customer payload from system instructions. |

---

## 4. How to Edit Prompts

1. Open `archive/Day11/prompts/production_prompt.jinja2`.
2. Edit instructions under `[DEVELOPER]` or identity under `[SYSTEM]`.
3. To update output fields, modify `TicketClassificationSchema` in `ticket_classifier/prompt_engine.py`. The output specification in the prompt will update **automatically**.
4. Run `python scripts/run_day11_benchmark.py` to re-evaluate performance across the 20-input benchmark.
