# 🚀 Daily Tasks - GenAI Module

A progressive multi-day repository for building and testing production-grade Generative AI modules.

---

## 📁 Repository Structure

```
Daily-tasks-/
├── Day1/       # Baseline GenAI Module & Schema-First FastAPI Application
├── Day2/       # Testing Non-Deterministic AI Systems (3-Tier Pytest Suite & DI)
└── README.md
```

---

## 📅 Daily Task Breakdown

### 🔹 [Day 1] - GenAI Module Foundations
- Typed Pydantic schemas for LLM responses and domain models.
- Explicit mapping layer between raw LLM outputs and domain logic.
- Input sanitization and business rule validators.
- Strict `mypy` type checking.

### 🔹 [Day 2] - Testing Non-Deterministic AI Systems
- **Dependency Injection**: LLM client is fully injectable in `LLMService`.
- **Strict Schema Enforcement**: Required `category` and `confidence` fields without default fallbacks.
- **Controlled Error Handling**: Explicit error handling for malformed JSON, timeouts, and LLM refusals.
- **Three-Tier Pytest Test Suite**:
  - **Tier 1 (Pure Unit Tests)**: Input sanitization, mapping, domain business rules, parametrized validation, PII leakage detection, and Hypothesis property-based testing.
  - **Tier 2 (Mocked LLM Tests)**: Fully isolated tests for success, malformed JSON, timeout (`TimeoutError`), and refusal scenarios using `unittest.mock.Mock`.
  - **Tier 3 (Live LLM Test)**: Isolated live model test decorated with `@pytest.mark.live`.

---

## 🧪 Running Tests (Day 2)

Navigate to the repository root and run:

```bash
# Run Tier 1 & Tier 2 tests (Default run: 0 network calls, < 5s execution time)
python -m pytest Day2/tests -m "not live"

# Run Tier 3 Live LLM test (Requires GROQ_API_KEY environment variable)
python -m pytest Day2/tests -m live

# Run all tests with Code Coverage report
python -m pytest Day2/tests -m "not live" --cov=app --cov-report=term-missing
```

---

## 📊 Day 2 Verification Results

- **Execution Speed**: `2.45s` (Sub-5-second target)
- **Network Calls**: `0` during default pytest execution
- **Test Pass Rate**: `100%` (17 passed, 1 deselected)
- **Code Coverage**: `91%`
