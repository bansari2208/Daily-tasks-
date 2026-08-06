# Day 15: Prompt Versioning & Management with Langfuse

Welcome to **Day 15: Prompt Versioning and Management**. This module provides production-grade integration with **Langfuse Prompt Registry (SDK v4.14.1)** and telemetry monitoring.

---

## 📁 Folder Structure

```text
Day15/
├── README.md                      # Comprehensive Day 15 documentation
├── langfuse_integration.py        # Langfuse SDK v4 client & Prompt Registry Manager
├── canary_release.py              # 90/10 Canary Traffic Router
├── logger_extension.py            # Structured JSONL logger extended with prompt attribution
├── demo_day15.py                  # Master Demonstration Script
├── verify_day15.py                # Automated PASS/FAIL Verification Helper
├── test_langfuse.py               # Live Langfuse tracing test script
├── version_comparison_report.md   # Day 11 vs Day 15 Prompt Comparison & Evaluation Report
├── ROLLBACK.md                    # Operational Zero-Code Rollback Playbook
├── CANARY_RELEASE.md              # Canary Deployment Strategy Guide
├── TEMPLATE_SAFETY.md             # Prompt Template Variable Safety Rules
├── REPRODUCIBILITY.md             # Step-by-step Execution & Reproduction Guide
├── prompts/
│   ├── ticket_classifier_v1.txt   # Local Version 1 Template (Basic JSON classification)
│   └── ticket_classifier_v2.txt   # Local Version 2 Template (Enhanced JSON with confidence & reasoning)
└── tests/
    ├── __init__.py
    └── test_day15.py              # Day 15 Unit Test Suite (7 tests)
```

---

## 🎯 Completed Day 15 Tasks

| Task ID | Requirement Description | Implementation / File Location |
| :--- | :--- | :--- |
| **Task 40** | Move prompts into versioned template files with explicitly declared variables (`{{ticket}}`). | Langfuse Cloud Registry & [`prompts/`](prompts/) |
| **Task 41** | Add prompt name & version to structured log records built on Day 4. | [`logger_extension.py`](logger_extension.py) |
| **Task 42** | Build registry providing prompt by name and version with documented default & changelog. | [`langfuse_integration.py`](langfuse_integration.py) |
| **Task 43** | Re-run Day 11 comparison through registry and produce version attribution report. | [`version_comparison_report.md`](version_comparison_report.md) |
| **Task 44** | Document rollback procedure: detection, decision-maker, and zero-code revert steps. | [`ROLLBACK.md`](ROLLBACK.md) |

---

## 🚀 Live Execution Commands

### 1. Master Demonstration Script
```powershell
python Day15/demo_day15.py
```

### 2. Automated System Verification (PASS / FAIL)
```powershell
python Day15/verify_day15.py
```

### 3. Unit Test Suite
```powershell
python -m unittest Day15/tests/test_day15.py
```

---

## 🌐 Live Langfuse Dashboard Telemetry
All executions export live OpenTelemetry spans and generations directly to:
- **Host**: `https://hipaa.cloud.langfuse.com`
- **Target Prompt**: `ticket_classifier 1`
- **Version 1 Label**: `production`
- **Version 2 Label**: `latest`
