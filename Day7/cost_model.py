import sys
import os

# Ensure UTF-8 output encoding for cross-platform terminal compatibility
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Production volume parameters
DAILY_TICKETS = 5000
DAYS_PER_MONTH = 30
MONTHLY_TICKETS = DAILY_TICKETS * DAYS_PER_MONTH

# Configurable Model Pricing per 1,000,000 (1M) tokens
MODEL_PRICING = {
    "GPT-4.1": {"input_per_1m": 2.50, "output_per_1m": 18.00},
    "GPT-4.1 Mini": {"input_per_1m": 1.00, "output_per_1m": 6.00},
    "GPT-4.1 Nano": {"input_per_1m": 0.60, "output_per_1m": 3.60},
}

# Prompt token estimates
PROMPT_SPECS = {
    "Prompt A (Verbose)": {"input_tokens": 400, "output_tokens": 100},
    "Prompt B (Optimized)": {"input_tokens": 220, "output_tokens": 60},
}


def calculate_request_cost(input_tokens: int, output_tokens: int, model_name: str) -> float:
    """Calculates single request cost based on token counts and model pricing."""
    pricing = MODEL_PRICING[model_name]
    input_cost = (input_tokens / 1_000_000) * pricing["input_per_1m"]
    output_cost = (output_tokens / 1_000_000) * pricing["output_per_1m"]
    return input_cost + output_cost


def print_model_comparison_table():
    """Prints monthly cost comparison across model choices (using Verbose Prompt A)."""
    print("=========================================================================================")
    print("                 Model Tier Cost Comparison (5,000 Requests/Day)                         ")
    print("=========================================================================================")
    print(f"{'Model Name':<15} | {'Cost/Request ($)':<18} | {'Daily Cost ($)':<15} | {'Monthly Cost ($)':<15}")
    print("-" * 75)
    for model_name in MODEL_PRICING:
        req_cost = calculate_request_cost(400, 100, model_name)
        daily_cost = req_cost * DAILY_TICKETS
        monthly_cost = req_cost * MONTHLY_TICKETS
        print(f"{model_name:<15} | ${req_cost:<17.6f} | ${daily_cost:<14.2f} | ${monthly_cost:<14.2f}")
    print("=========================================================================================\n")


def print_prompt_comparison_table():
    """Prints prompt optimization comparison using GPT-4.1."""
    p_a = PROMPT_SPECS["Prompt A (Verbose)"]
    p_b = PROMPT_SPECS["Prompt B (Optimized)"]

    cost_a = calculate_request_cost(p_a["input_tokens"], p_a["output_tokens"], "GPT-4.1") * MONTHLY_TICKETS
    cost_b = calculate_request_cost(p_b["input_tokens"], p_b["output_tokens"], "GPT-4.1") * MONTHLY_TICKETS
    diff = cost_a - cost_b
    pct_savings = (diff / cost_a) * 100.0

    print("=========================================================================================")
    print("                 Prompt Engineering Optimization (GPT-4.1 Model)                        ")
    print("=========================================================================================")
    print(f"{'Prompt Design':<22} | {'Input':<8} | {'Output':<8} | {'Total':<8} | {'Monthly Cost ($)':<15}")
    print("-" * 75)
    print(f"{'Prompt A (Verbose)':<22} | {p_a['input_tokens']:<8} | {p_a['output_tokens']:<8} | {p_a['input_tokens']+p_a['output_tokens']:<8} | ${cost_a:<14.2f}")
    print(f"{'Prompt B (Optimized)':<22} | {p_b['input_tokens']:<8} | {p_b['output_tokens']:<8} | {p_b['input_tokens']+p_b['output_tokens']:<8} | ${cost_b:<14.2f}")
    print("-" * 75)
    print(f"Cost Reduction: ${diff:.2f}/month | Savings: {pct_savings:.1f}%\n")


def print_language_inflation_analysis():
    """Prints multilingual token inflation analysis between English and Hindi/Gujarati."""
    eng_text = "Card payment failed twice on checkout page when attempting to upgrade my subscription."
    hindi_text = "मेरी सदस्यता को अपग्रेड करने का प्रयास करते समय चेकआउट पृष्ठ पर मेरा भुगतान दो बार विफल हो गया।"

    eng_tokens = len(eng_text.split())
    hindi_tokens = int(eng_tokens * 2.5)  # ~2.5x token inflation for South Asian scripts
    pct_increase = ((hindi_tokens - eng_tokens) / eng_tokens) * 100.0

    print("=========================================================================================")
    print("                 Multilingual Token Inflation (English vs. Hindi)                       ")
    print("=========================================================================================")
    print(f"{'Language':<15} | {'Sample Text Length':<25} | {'Est. Tokens':<12} | {'Token Inflation':<15}")
    print("-" * 75)
    print(f"{'English':<15} | {len(eng_text):<25} chars | {eng_tokens:<12} | Baseline (0.0%)")
    print(f"{'Hindi / Gujarati':<15} | {len(hindi_text):<25} chars | {hindi_tokens:<12} | +{pct_increase:.1f}%")
    print("=========================================================================================\n")


def print_prompt_caching_simulation() -> tuple[float, float]:
    """Simulates prompt caching with 50% discount on 80% cached system instructions."""
    p_b = PROMPT_SPECS["Prompt B (Optimized)"]
    pricing = MODEL_PRICING["GPT-4.1 Nano"]

    uncached_input_cost = (p_b["input_tokens"] / 1_000_000) * pricing["input_per_1m"] * MONTHLY_TICKETS
    output_cost = (p_b["output_tokens"] / 1_000_000) * pricing["output_per_1m"] * MONTHLY_TICKETS
    original_cost = uncached_input_cost + output_cost

    # 80% cached prompt tokens at 50% rate, 20% fresh tokens at full rate
    cached_input_tokens = p_b["input_tokens"] * 0.80
    fresh_input_tokens = p_b["input_tokens"] * 0.20
    cached_input_cost = ((cached_input_tokens * 0.50 * pricing["input_per_1m"] + fresh_input_tokens * pricing["input_per_1m"]) / 1_000_000) * MONTHLY_TICKETS
    cached_total_cost = cached_input_cost + output_cost

    savings = original_cost - cached_total_cost
    pct_saved = (savings / original_cost) * 100.0

    print("=========================================================================================")
    print("                 Prompt Caching Simulation (GPT-4.1 Nano + Prompt B)                    ")
    print("=========================================================================================")
    print(f"Original Monthly Cost: ${original_cost:.2f}")
    print(f"Cached Monthly Cost:   ${cached_total_cost:.2f}")
    print(f"Total Savings:         ${savings:.2f}")
    print(f"Percentage Savings:    {pct_saved:.1f}%\n")
    return original_cost, cached_total_cost


def print_batch_api_simulation() -> tuple[float, float]:
    """Simulates Batch API processing with 50% flat discount on all tokens."""
    p_b = PROMPT_SPECS["Prompt B (Optimized)"]
    normal_cost = calculate_request_cost(p_b["input_tokens"], p_b["output_tokens"], "GPT-4.1 Nano") * MONTHLY_TICKETS
    batch_cost = normal_cost * 0.50
    savings = normal_cost - batch_cost
    pct_saved = 50.0

    print("=========================================================================================")
    print("                 Batch API Pricing Simulation (GPT-4.1 Nano + Prompt B)                 ")
    print("=========================================================================================")
    print(f"Normal API Monthly Cost: ${normal_cost:.2f}")
    print(f"Batch API Monthly Cost:  ${batch_cost:.2f}")
    print(f"Total Savings:           ${savings:.2f}")
    print(f"Percentage Saved:        {pct_saved:.1f}%\n")
    return normal_cost, batch_cost


def print_comprehensive_comparison_table():
    """Prints final summary comparison table including Day 7 Stretch Goal features."""
    p_a = PROMPT_SPECS["Prompt A (Verbose)"]
    p_b = PROMPT_SPECS["Prompt B (Optimized)"]

    naive_cost = calculate_request_cost(p_a["input_tokens"], p_a["output_tokens"], "GPT-4.1") * MONTHLY_TICKETS
    opt_prompt_cost = calculate_request_cost(p_b["input_tokens"], p_b["output_tokens"], "GPT-4.1") * MONTHLY_TICKETS
    cheaper_model_cost = calculate_request_cost(p_a["input_tokens"], p_a["output_tokens"], "GPT-4.1 Mini") * MONTHLY_TICKETS

    # GPT-4.1 Nano uncached
    nano_base = calculate_request_cost(p_b["input_tokens"], p_b["output_tokens"], "GPT-4.1 Nano") * MONTHLY_TICKETS

    # Prompt caching cost
    pricing = MODEL_PRICING["GPT-4.1 Nano"]
    cached_input_cost = ((p_b["input_tokens"] * 0.8 * 0.5 * pricing["input_per_1m"] + p_b["input_tokens"] * 0.2 * pricing["input_per_1m"]) / 1_000_000) * MONTHLY_TICKETS
    out_cost = (p_b["output_tokens"] / 1_000_000) * pricing["output_per_1m"] * MONTHLY_TICKETS
    caching_cost = cached_input_cost + out_cost

    # Batch API cost (50% off base)
    batch_cost = nano_base * 0.50

    # Best Overall Config (Prompt B + GPT-4.1 Nano + Prompt Caching + Batch API)
    best_overall_cost = caching_cost * 0.50

    configs = [
        ("Naive Configuration", "GPT-4.1", naive_cost),
        ("Optimized Prompt", "GPT-4.1", opt_prompt_cost),
        ("Cheaper Model", "GPT-4.1 Mini", cheaper_model_cost),
        ("Prompt Caching", "GPT-4.1 Nano", caching_cost),
        ("Batch API", "GPT-4.1 Nano", batch_cost),
        ("Best Overall Configuration", "GPT-4.1 Nano", best_overall_cost),
    ]

    print("=========================================================================================")
    print("                      Day 7 Comprehensive Cost Comparison                                ")
    print("=========================================================================================")
    print(f"{'Configuration':<27} | {'Model':<13} | {'Monthly Cost ($)':<16} | {'Savings ($)':<12} | {'Reduction %':<11}")
    print("-" * 91)
    for name, model, cost in configs:
        savings = naive_cost - cost
        pct = (savings / naive_cost) * 100.0 if naive_cost > 0 else 0.0
        sav_str = "-" if savings <= 0 else f"${savings:<11.2f}"
        print(f"{name:<27} | {model:<13} | ${cost:<15.2f} | {sav_str:<12} | {pct:<10.1f}%")
    print("=========================================================================================\n")

    print("Cheapest Configuration:")
    print("Model:                   GPT-4.1 Nano")
    print("Prompt:                  Prompt B (Optimized) + Prompt Caching + Batch API")
    print(f"Estimated Monthly Cost:  ${best_overall_cost:.2f}")
    print(f"Monthly Savings:         ${(naive_cost - best_overall_cost):.2f}")
    print(f"Percentage Saved:        {((naive_cost - best_overall_cost) / naive_cost * 100):.1f}%\n")


def print_final_recommendation():
    """Prints final decision recommendations based on business SLAs."""
    print("==================================")
    print("Final Cost Optimization Recommendation")
    print("==================================")
    print("1. Real-Time Production Endpoints (Interactive UX):")
    print("   - Configuration: GPT-4.1 Nano + Prompt B (Optimized) + Prompt Caching")
    print("   - Monthly Cost: $44.28/month (89.5% savings over Naive)")
    print("   - Rationale: Delivers immediate low-latency responses for active customer support sessions.\n")

    print("2. Asynchronous / Overnight Batch Processing:")
    print("   - Configuration: GPT-4.1 Nano + Prompt B + Prompt Caching + Batch API")
    print("   - Monthly Cost: $22.14/month (94.7% savings over Naive)")
    print("   - Rationale: Provides maximum cost efficiency when 24-hour turnaround is acceptable.\n")


def print_quality_verification():
    """Prints quality verification strategy for cost reduction validation."""
    print("==================================")
    print("Quality Verification Strategy")
    print("==================================")
    print("1. Classification Consistency Check:")
    print("   - Run 1,000 historical support tickets through GPT-4.1 and GPT-4.1 Nano.")
    print("   - Verify category agreement rate stays above 95%.\n")

    print("2. Manual Sample Review:")
    print("   - Support team leads manually review 100 random predictions from the optimized model.")
    print("   - Ensure priority levels (HIGH/MEDIUM/LOW) match escalation standards.\n")

    print("3. Validation Data Accuracy Benchmark:")
    print("   - Evaluate classification F1-score against a golden labeled test dataset.")
    print("   - Require F1 >= 0.92 before deploying prompt or model changes to production.\n")

    print("4. Output Schema Enforcement:")
    print("   - Validate that Pydantic JSON outputs conform strictly to the required schema.")
    print("   - Enforce zero schema failure rate across all API responses.\n")


def main():
    print("\nStarting Day 7 Cost Optimization & Token Economics Analysis...\n")
    print_model_comparison_table()
    print_prompt_comparison_table()
    print_language_inflation_analysis()
    print_prompt_caching_simulation()
    print_batch_api_simulation()
    print_comprehensive_comparison_table()
    print_final_recommendation()
    print_quality_verification()


if __name__ == "__main__":
    main()

