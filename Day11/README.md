# Day 11 Milestone: Prompt Engineering & Structured Output

## 1. Purpose
Implement production-grade prompt engineering, 5-part prompt anatomy, OpenAI role separation, and Schema-First JSON output derivation for the Ticket Classifier system.

---

## 2. Directory & Files Layout

```
archive/Day11/
├── prompts/
│   ├── original_prompt.jinja2     # Weak legacy prompt template
│   ├── production_prompt.jinja2   # 5-part anatomy template with metadata
│   └── README.md                  # Prompts & Role Separation guide
├── benchmark_inputs.json          # 20 fixed realistic ticket inputs
├── day11_prompt_engine.py         # Schema spec generator & role builder
├── run_day11_benchmark.py         # Deterministic benchmark runner script
├── revision_example.py            # textwrap.dedent() prompt formatting demo (< 20 lines)
├── day11_evaluation_report.md     # Markdown benchmark report
└── day11_results.json             # Structured JSON benchmark metrics
```

---

## 3. How to Run Benchmark

Run the active benchmark script from the repository root:

```bash
python scripts/run_day11_benchmark.py
```

Or run directly from the archive directory:

```bash
python archive/Day11/run_day11_benchmark.py
```

---

## 4. Expected Output

- Generates `archive/Day11/day11_evaluation_report.md` (Markdown Report).
- Generates `archive/Day11/day11_results.json` (Structured JSON Results).
- Output Summary:
  - Original Prompt Pass Rate: 75.0%
  - Production Prompt Pass Rate: 100.0%
  - Positive Instruction Pass: 100.0%
  - Negative Instruction Pass: 90.0%
