# 🧪 Ticket Classifier Experiments (`experiments/`)

This directory contains standalone, beginner-friendly educational Python scripts demonstrating **Day 6**, **Day 7**, and **Day 8** LLM operational engineering concepts.

Each script is self-contained, heavily commented, under ~150 lines of code, and executable independently.

---

## 📁 Directory Structure

```text
experiments/
├── experiment_latency.py       # Day 6: Streaming Latency & Prefill vs Decode Dynamics
├── experiment_cost.py          # Day 7: Cost Calculator & Multilingual Token Inflation
├── experiment_decoding.py      # Day 8: Temperature vs Top-p Hyperparameter Sweep
├── experiment_json_modes.py    # Day 8: Prompt-only vs JSON Mode vs JSON Schema Mode
├── experiment_confidence.py    # Day 8: Logprob Confidence Scoring & Human Review Routing
└── README.md                   # Documentation & Execution Guide
```

---

## ⚡ 1. Day 6 — Inference Latency & Streaming (`experiment_latency.py`)

### What it Demonstrates
- Measures **Time To First Token (TTFT)**, **Total Latency**, and **Time Per Output Token (TPOT)** across Small (~200 tokens), Medium (~2,000 tokens), and Large (~20,000 tokens) prompts.
- Automatically determines whether an execution is **Prefill Dominated** (large input prompts) or **Decode Dominated** (small prompts with long output generation).

### How to Run
```bash
python experiments/experiment_latency.py
```

### Expected Output
A formatted comparison table showing TTFT, Total Latency, Output Tokens, TPOT, and Dominant Phase, followed by a concise explanation of inference dynamics.

---

## 💰 2. Day 7 — Cost Economics & Token Inflation (`experiment_cost.py`)

### What it Demonstrates
- Simulates a 5,000 tickets/day production volume scenario across 3 model tiers (`Cheap Model`, `Balanced Model`, `Premium Model`) and 2 prompt designs (`Prompt A Verbose` vs `Prompt B Optimized`).
- Calculates daily and monthly operational costs, highlighting percentage savings.
- Evaluates **Multilingual Token Inflation** comparing English, Gujarati, and Hindi subword token counts.

### How to Run
```bash
python experiments/experiment_cost.py
```

### Expected Output
- Model and Prompt comparison cost table.
- Recommendation for the cheapest viable configuration.
- Token inflation table comparing English, Gujarati, and Hindi token overhead.

---

## 🎛️ 3. Day 8 — Decoding Parameter Sweep (`experiment_decoding.py`)

### What it Demonstrates
- Evaluates hyperparameter combinations across **Temperature** (`0.0`, `0.2`, `0.5`, `0.8`) and **Top-p** (`0.7`, `0.9`, `1.0`) over 10 iterations per setting.
- Tracks **Schema Validity %**, **Average Response Length**, and **Unique Outputs** to show how sampling randomness impacts determinism and structure.

### How to Run
```bash
python experiments/experiment_decoding.py
```

### Expected Output
A grid sweep table displaying schema validity percentages and output uniqueness across temperatures.

---

## 🔒 4. Day 8 — JSON Output Control Modes (`experiment_json_modes.py`)

### What it Demonstrates
- Compares three JSON enforcement mechanisms:
  1. **Prompt-only JSON**
  2. **JSON Mode**
  3. **JSON Schema Mode**
- Evaluates Schema Validity %, Latency (ms), and Response Length.

### How to Run
```bash
python experiments/experiment_json_modes.py
```

### Expected Output
A strategy comparison table followed by a recommendation for Schema-Constrained Generation.

---

## 🎯 5. Day 8 — Confidence Scoring & Routing (`experiment_confidence.py`)

### What it Demonstrates
- Extracts/simulates log probability confidence scores per prediction (`0.0` – `1.0`).
- Implements a configurable threshold (`Confidence < 0.70`) to route low-confidence predictions to **Human Review Required**.

### How to Run
```bash
python experiments/experiment_confidence.py
```

### Expected Output
A ticket prediction list detailing confidence scores and routing decisions (`Accept Prediction` vs `Send to Human Review`).
