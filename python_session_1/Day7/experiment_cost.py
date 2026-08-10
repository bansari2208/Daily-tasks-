"""
Day 7 — Cost Optimization & Token Economics Experiment
Calculates production volume costs across model tiers, prompt optimizations,
and analyzes multilingual token inflation (English vs Gujarati vs Hindi).
"""

import sys
import logging
from dataclasses import dataclass
from pathlib import Path

# Ensure UTF-8 output encoding for cross-platform terminal compatibility
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# Production volume parameter
DAILY_REQUESTS = 5000
DAYS_PER_MONTH = 30
MONTHLY_REQUESTS = DAILY_REQUESTS * DAYS_PER_MONTH

# Model pricing per 1,000,000 (1M) tokens stored in a dictionary
MODEL_PRICING = {
    "Cheap Model (Nano)": {"input_per_1m": 0.60, "output_per_1m": 3.60},
    "Balanced Model (Mini)": {"input_per_1m": 1.00, "output_per_1m": 6.00},
    "Premium Model (Pro)": {"input_per_1m": 2.50, "output_per_1m": 18.00},
}

# Prompt token specifications
PROMPTS = {
    "Prompt A (Verbose)": {"input_tokens": 400, "output_tokens": 100},
    "Prompt B (Optimized)": {"input_tokens": 220, "output_tokens": 60},
}


def calculate_cost(input_tokens: int, output_tokens: int, input_rate: float, output_rate: float) -> float:
    """Calculates cost per request based on per-1M token rates."""
    input_cost = (input_tokens / 1_000_000) * input_rate
    output_cost = (output_tokens / 1_000_000) * output_rate
    return input_cost + output_cost

def run_cost_experiment():
    """Calculates financial model comparisons across models and prompts."""
    baseline_monthly = None
    results = []

    for model_name, rates in MODEL_PRICING.items():
        for prompt_name, tokens in PROMPTS.items():
            cost_per_req = calculate_cost(
                tokens["input_tokens"],
                tokens["output_tokens"],
                rates["input_per_1m"],
                rates["output_per_1m"]
            )
            daily_cost = cost_per_req * DAILY_REQUESTS
            monthly_cost = daily_cost * DAYS_PER_MONTH

            if baseline_monthly is None:
                baseline_monthly = monthly_cost

            savings_pct = ((baseline_monthly - monthly_cost) / baseline_monthly) * 100

            results.append({
                "model": model_name,
                "prompt": prompt_name,
                "cost_req": cost_per_req,
                "daily": daily_cost,
                "monthly": monthly_cost,
                "savings": savings_pct
            })

    return results


def run_language_inflation_analysis():
    """Analyzes token inflation for non-English languages."""
    print("\n" + "=" * 96)
    print("                      Language Token Inflation Analysis                                 ")
    print("=" * 96)

    sample_texts = {
        "English": "Payment failed on checkout page. Card error 402.",
        "Gujarati": "ચેકઆઉટ પૃષ્ઠ પર ચુકવણી નિષ્ફળ ગઈ. કાર્ડ ભૂલ ૪૦૨.",
        "Hindi": "चेकआउट पेज पर भुगतान विफल रहा। कार्ड त्रुटि 402।"
    }

    # Try importing tiktoken if available, otherwise use character-to-token fallback approximation
    try:
        import tiktoken
        encoding = tiktoken.get_encoding("cl100k_base")
        method = "tiktoken (cl100k_base)"

        token_counts = {lang: len(encoding.encode(text)) for lang, text in sample_texts.items()}
    except ImportError:
        method = "Character Ratio Approximation (tiktoken unavailable)"
        # Simple estimation: English ~4 chars/token, Indic scripts ~1.5 chars/token
        token_counts = {
            "English": int(len(sample_texts["English"]) / 4.0),
            "Gujarati": int(len(sample_texts["Gujarati"]) / 1.5),
            "Hindi": int(len(sample_texts["Hindi"]) / 1.5),
        }

    baseline_tokens = token_counts["English"]

    print(f"Tokenization Estimation Method: {method}\n")
    print(f"{'Language':<14} | {'Sample Character Count':<24} | {'Estimated Tokens':<18} | {'Token Inflation %':<18}")
    print("-" * 84)

    for lang, count in token_counts.items():
        inflation = ((count - baseline_tokens) / baseline_tokens) * 100
        print(f"{lang:<14} | {len(sample_texts[lang]):<24} | {count:<18} | {inflation:<+17.1f}%")

    print("=" * 96)
    print("Takeaway: Non-English text experiences subword token inflation due to smaller vocabulary representation.\n")


if __name__ == "__main__":
    logging.info("Starting Day 7 Cost Optimization Experiment...")

    results = run_cost_experiment()

    print("\n" + "=" * 96)
    print("                      Day 7 Cost Calculator (5,000 Requests/Day)                        ")
    print("=" * 96)
    print(f"{'Model Tier':<22} | {'Prompt':<20} | {'Cost/Req ($)':<12} | {'Daily ($)':<10} | {'Monthly ($)':<12} | {'Savings %':<10}")
    print("-" * 96)

    for item in results:
        print(f"{item['model']:<22} | {item['prompt']:<20} | ${item['cost_req']:<11.6f} | ${item['daily']:<9.2f} | ${item['monthly']:<11.2f} | {item['savings']:<9.1f}%")

    print("=" * 96)

    cheapest = sorted(results, key=lambda x: x["monthly"])[0]

    print("\nRecommended Cheapest Configuration:")
    print(f"  Model        : {cheapest['model']}")
    print(f"  Prompt       : {cheapest['prompt']}")
    print(f"  Monthly Cost : ${cheapest['monthly']:.2f} (Savings: {cheapest['savings']:.1f}% vs Premium Verbose)")

    run_language_inflation_analysis()


