# 🏢 Internal Demo Project (`internal_demo_project`)

An independent consumer application that demonstrates how to import and reuse the locally installed `ticket_classifier` Python package.

---

## 🎯 Why This Project Exists

This standalone project verifies that `ticket_classifier` is a fully reusable, modular Python package that can be imported into external applications without copying source code files or depending on internal module structures.

---

## ⚡ Installation & Setup

1. First, install the `ticket_classifier` package in editable mode from the root workspace:

```bash
pip install -e ..
```

2. Navigate into this project directory:

```bash
cd internal_demo_project
```

3. Run `app.py`:

```bash
python app.py
```

---

## 🔍 How It Proves Package Reusability

- **Zero Code Duplication**: No source files from `ticket_classifier` were copied into `internal_demo_project`.
- **Clean Public API Imports**: `app.py` consumes exports directly:
  ```python
  from ticket_classifier import (
      AsyncLLMClient,
      SupportTicket,
      predict_priority,
      redact_text,
      generate_report,
  )
  ```
- **Independent Execution**: `app.py` instantiates input models, performs PII redaction, classifies tickets asynchronously, predicts priority levels, and records observability metrics via package APIs.
