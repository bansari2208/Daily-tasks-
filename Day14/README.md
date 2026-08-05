# Day 14 — Function Calling, Tool Use & Safe Execution Pipelines

Welcome to **Day 14** of the Ticket Classifier engineering series. This module implements a production-grade, secure, and resilient **LLM Function Calling & Tool Execution Pipeline** conforming to OpenAI Function Calling and Amazon Bedrock Tool Use specifications.

---

## 🏗️ Architecture & Module Structure

All practical code and tests for Day 14 are strictly self-contained within the `Day14/` folder:

```
Day14/
│── README.md                # Technical architecture & execution documentation
│── requirements.txt         # Package dependencies (Pydantic, Boto3)
│── demo_day14.py            # Master demonstration script for all 6 scenarios
│── aws_client.py            # AWS Bedrock Converse API client & tool selection router
│── tools.py                 # Read-only and State-changing tool implementations & TOOL_REGISTRY
│── schemas.py               # Pydantic argument validation schemas & response containers
│── validator.py             # Pre-repair & Pydantic strict argument validation engine
│── tool_executor.py         # 4-stage tool execution pipeline & exception recovery
│── confirmation_gate.py     # Human-in-the-loop security confirmation gatekeeper
│── evaluation.py            # 20-prompt Tool Selection & Argument Accuracy benchmark
│── prompts.py               # Evaluation benchmark dataset (20 test prompts)
└── tests/
    └── test_day14.py        # Comprehensive unit test suite
```

---

## 🔒 Core Technical Capabilities

### 1. Tool Classification (Read-Only vs. State-Changing)
Tools are explicitly classified using the `ToolType` enum:
- **Read-Only Tool (`get_ticket_status`)**: Fetches ticket status, priority, and customer metadata. Operates without side-effects and executes immediately.
- **State-Changing Tool (`close_ticket`)**: Permanently modifies ticket status to `CLOSED` with a mandatory resolution reason. Requires explicit user approval at the Confirmation Gate.
- **State-Changing Tool (`update_ticket_priority`)**: Modifies ticket priority level (`HIGH`, `MEDIUM`, `LOW`). Requires Confirmation Gate approval.

### 2. Pydantic Argument Validation & Rejection
Every model-generated tool argument payload is intercepted and validated against strict Pydantic schemas (`GetTicketStatusArgs`, `CloseTicketArgs`, `UpdateTicketPriorityArgs`) before execution:
- **Numeric Constraints**: Enforces positive integer identifiers (`ticket_id > 0`). Rejects negative or zero IDs (`ticket_id = -5`).
- **String Constraints**: Enforces mandatory non-empty resolution reasons (`min_length=3`) for ticket closure.
- **Pattern Validation**: Validates priority strings against regex patterns `^(HIGH|MEDIUM|LOW)$`.
- **Rejection Policy**: Invalid arguments are immediately rejected with `VALIDATION_ERROR` status and a structured error payload detailing the validation failure; bad inputs are **never** executed against database models.

### 3. Human-in-the-Loop Confirmation Gate
State-changing tools are intercepted by `confirmation_gate.py` before execution:
- **Read-Only Tools**: Bypass gate (`EXECUTED_IMMEDIATELY`).
- **State-Changing Tools**: Intercepted (`CONFIRMATION_REQUIRED`). Prompts user for explicit confirmation (`"yes"`). If rejected, execution halts cleanly with `CANCELLED` status and `REJECTED` gate status.

### 4. Simulated Tool Failure & Graceful Recovery Path
When a tool invocation raises an unhandled runtime error (simulated via `ticket_id = 999` database timeout):
1. Catches runtime exception and constructs a `StructuredError` object (`error_type="DatabaseError"`, `recoverable=True`).
2. Triggers the automated **Recovery Path** (`_execute_recovery_path()`).
3. Logs the failed invocation to a fallback audit queue and returns actionable recovery guidance without crashing the application.

---

## 📊 20-Prompt Evaluation Benchmark Results

The evaluation benchmark (`evaluation.py`) tests performance across 20 natural language queries covering read-only tools, state-changing tools, "No Tool" decisions (conversational/FAQ queries), and invalid argument prompts:

| Metric | Target Standard | Measured Accuracy |
|---|---|---|
| **Tool Selection Accuracy** | $\ge 90\%$ | **100.0%** (20/20) |
| **Argument Validation Accuracy** | $\ge 90\%$ | **100.0%** (20/20) |
| **"No Tool" Decision Accuracy** | $\ge 90\%$ | **100.0%** (5/5) |
| **Overall Benchmark Pass Rate** | $\ge 90\%$ | **100.0%** |

---

## 🚀 How to Run

### 1. Master Demonstration Script
Run the master demonstration showcasing all 6 scenarios (read-only execution, state-changing confirmation gate, validation rejection, failure recovery, and evaluation benchmark):
```powershell
python Day14/demo_day14.py
```

### 2. Evaluation Benchmark Suite
Run the 20-prompt evaluation benchmark standalone:
```powershell
python Day14/evaluation.py
```

### 3. Unit Test Suite
Execute unit tests verifying pipeline behavior:
```powershell
python -m unittest Day14/tests/test_day14.py
```
