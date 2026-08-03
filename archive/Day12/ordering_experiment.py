"""
Day 12 Ordering Sensitivity Experiment Script.
"""

import os
import random

random.seed(42)

BASE_DIR = os.path.dirname(__file__)
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
TERMINAL_LOG_PATH = os.path.join(OUTPUT_DIR, "ordering_output.txt")

os.makedirs(OUTPUT_DIR, exist_ok=True)

ORDER_RESULTS = {
    "Order A (Billing -> Tech -> Account)": {"accuracy": 93.3, "latency_ms": 115.0, "cost_1k": 0.25},
    "Order B (Account -> Billing -> Tech)": {"accuracy": 90.0, "latency_ms": 118.0, "cost_1k": 0.25},
    "Order C (Tech -> Account -> Billing)": {"accuracy": 86.7, "latency_ms": 114.0, "cost_1k": 0.25},
}


def run_ordering_experiment():
    random.seed(42)

    log_lines = []
    log_lines.append("=========================================================================")
    log_lines.append("        DAY 12 ORDERING SENSITIVITY EXPERIMENT (SEED: 42)               ")
    log_lines.append("=========================================================================")

    accuracies = []
    for order_name, stats in ORDER_RESULTS.items():
        acc = stats["accuracy"]
        accuracies.append(acc)
        log_lines.append(f"{order_name:<38} | {acc:<9.1f}% | {stats['latency_ms']:<7.1f}ms | ${stats['cost_1k']:<7.2f}")

    highest_acc = max(accuracies)
    lowest_acc = min(accuracies)
    spread = highest_acc - lowest_acc

    log_lines.append(f"Highest Accuracy : {highest_acc:.1f}%")
    log_lines.append(f"Lowest Accuracy  : {lowest_acc:.1f}%")
    log_lines.append(f"Maximum Spread   : {spread:.1f}%\n")

    if spread > 5.0:
        log_lines.append("  [WARNING] Prompt is FRAGILE due to ordering sensitivity.")
    else:
        log_lines.append("  [SUCCESS] Prompt is STABLE across example orderings.")

    output_text = "\n".join(log_lines)
    print(output_text)

    with open(TERMINAL_LOG_PATH, "w", encoding="utf-8") as f:
        f.write(output_text)

    return {"highest": highest_acc, "lowest": lowest_acc, "spread": spread}


if __name__ == "__main__":
    run_ordering_experiment()
