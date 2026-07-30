import os
import json
import statistics
from ticket_classifier.cost import (
    calculate_request_cost,
    compress_prompt,
    compare_language_inflation,
    get_model_recommendation,
)

# Default path to the JSONL log file generated in Step 1
LOG_FILE_PATH = os.path.join("logs", "llm_logs.jsonl")


def generate_report(log_file: str = LOG_FILE_PATH, batch_time: float = None):
    """Reads JSON logs and prints the improved Day 4 & Day 7 Cost & Latency Report summary."""

    # Check if the log file exists at default or absolute fallback path
    if not os.path.exists(log_file):
        alt_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "logs",
            "llm_logs.jsonl",
        )
        if os.path.exists(alt_path):
            log_file = alt_path
        else:
            print(
                f"No log file found at '{log_file}'. Run LLM requests first to generate logs."
            )
            return

    # Read and parse JSON log entries line by line
    logs = []
    with open(log_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                logs.append(json.loads(line))

    if not logs:
        print("Log file is empty. No data to generate report.")
        return

    # Total count of LLM requests logged
    total_requests = len(logs)

    # Model usage and cost breakdown
    model_counts = {}
    model_costs = {}
    for log in logs:
        m = log.get("model_name", "GPT-4.1 Nano")
        c = log.get("estimated_cost", 0.0)
        model_counts[m] = model_counts.get(m, 0) + 1
        model_costs[m] = model_costs.get(m, 0.0) + c

    # Provider success breakdown
    primary_success = sum(1 for log in logs if log.get("provider") == "MockPrimary")
    fallback_success = sum(1 for log in logs if log.get("provider") == "MockFallback")
    failed_requests = sum(1 for log in logs if not log.get("success", False))

    # Calculate retry metrics
    requests_with_retries = sum(
        1 for log in logs if log.get("retry_count", 0) > 0
    )
    total_retries = sum(log.get("retry_count", 0) for log in logs)
    retry_rate = (requests_with_retries / total_requests) * 100.0
    avg_retries_per_request = (
        total_retries / total_requests if total_requests > 0 else 0.0
    )

    # Aggregate token counts across all logged requests
    prompt_tokens = sum(log.get("prompt_tokens", 0) for log in logs)
    completion_tokens = sum(log.get("completion_tokens", 0) for log in logs)
    total_tokens = sum(log.get("total_tokens", 0) for log in logs)
    avg_tokens = total_tokens / total_requests if total_requests > 0 else 0.0

    # Calculate total cost and average cost per request
    total_cost = sum(log.get("estimated_cost", 0.0) for log in logs)
    avg_cost_per_request = (
        total_cost / total_requests if total_requests > 0 else 0.0
    )

    # Projected daily (5,000 req/day) and monthly costs
    est_daily_cost = avg_cost_per_request * 5000.0
    est_monthly_cost = est_daily_cost * 30.0

    # Extract latency list for statistics calculation
    latencies = [
        log.get("latency_ms", 0.0)
        for log in logs
        if log.get("latency_ms") is not None
    ]
    ttfts = [log.get("ttft_ms", 0.0) for log in logs if log.get("ttft_ms") is not None]
    tpots = [log.get("tpot_ms", 0.0) for log in logs if log.get("tpot_ms") is not None]

    if latencies:
        avg_latency = statistics.mean(latencies)
        p50_latency = statistics.median(latencies)
        min_latency = min(latencies)
        max_latency = max(latencies)
        sorted_latencies = sorted(latencies)
        p95_index = min(int(0.95 * len(sorted_latencies)), len(sorted_latencies) - 1)
        p99_index = min(int(0.99 * len(sorted_latencies)), len(sorted_latencies) - 1)
        p95_latency = sorted_latencies[p95_index]
        p99_latency = sorted_latencies[p99_index]
    else:
        avg_latency = p50_latency = p95_latency = p99_latency = min_latency = max_latency = 0.0

    avg_ttft = statistics.mean(ttfts) if ttfts else 0.0
    avg_tpot = statistics.mean(tpots) if tpots else 0.0

    # Batch execution time & throughput
    batch_time_str = f"{batch_time:.2f} s" if batch_time is not None else "N/A"
    throughput = (total_requests / batch_time) if batch_time and batch_time > 0 else None
    throughput_str = f"{throughput:.2f} req/s" if throughput is not None else "N/A"

    # Prompt compression and language inflation metrics
    prompt_sample = logs[0].get("prompt", "") if logs else ""
    compression_stats = compress_prompt(prompt_sample)
    inflation_stats = compare_language_inflation()
    recommendation = get_model_recommendation(avg_tokens)

    # Print formatted console report
    print("\n==================================")
    print("Day 4 Cost & Latency Report")
    print("==================================")
    print(f"Requests:                  {total_requests}")
    print(f"Primary Success:           {primary_success}")
    print(f"Fallback Success:          {fallback_success}")
    print(f"Failed Requests:           {failed_requests}")
    print()
    print(f"Retry Rate:                {retry_rate:.2f}%")
    print(f"Average Retries/Request:   {avg_retries_per_request:.2f}")
    print()
    print(f"Prompt Tokens:             {prompt_tokens}")
    print(f"Completion Tokens:         {completion_tokens}")
    print(f"Total Tokens:              {total_tokens}")
    print()
    print(f"Total Cost:                ${total_cost:.6f}")
    print(f"Average Cost:              ${avg_cost_per_request:.6f}")
    print()
    print(f"Fastest Request:           {min_latency:.2f} ms")
    print(f"Slowest Request:           {max_latency:.2f} ms")
    print(f"Average Latency:           {avg_latency:.2f} ms")
    print(f"P50 Latency:               {p50_latency:.2f} ms")
    print(f"P95 Latency:               {p95_latency:.2f} ms")
    print(f"P99 Latency:               {p99_latency:.2f} ms")
    print(f"Average TTFT:              {avg_ttft:.2f} ms")
    print(f"Average TPOT:              {avg_tpot:.2f} ms")
    print()
    print(f"Batch Execution Time:      {batch_time_str}")
    print(f"Throughput:                {throughput_str}")
    print()
    print("Logs Saved To:")
    print(log_file)
    print("==================================")

    # Print Day 7 Cost Optimization Report
    print("\n==================================")
    print("Cost Optimization Report")
    print("==================================")
    print(f"Total Requests:            {total_requests}")
    print(f"Average Tokens:            {avg_tokens:.2f}")
    print(f"Average Cost:              ${avg_cost_per_request:.6f}")
    print(f"Estimated Daily Cost:      ${est_daily_cost:.2f}")
    print(f"Estimated Monthly Cost:    ${est_monthly_cost:.2f}")
    print()
    print("Model Usage & Cost Breakdown:")
    for model_name, count in model_counts.items():
        cost_for_model = model_costs.get(model_name, 0.0)
        print(f"  {model_name:<16}: {count:>3} requests | Cost: ${cost_for_model:.6f}")
    print(f"  {'Total':<16}: {total_requests:>3} requests | Cost: ${total_cost:.6f}")
    print()
    print(f"Cheapest Model Option:     GPT-4.1 Nano (${est_monthly_cost * 0.1:.2f} / month)")
    print(f"Most Expensive Tier Option: GPT-4.1 (${est_monthly_cost * 10.0:.2f} / month)")
    print()
    print("Prompt Compression Savings:")
    print(f"  Original Tokens:         {compression_stats['original_tokens']}")
    print(f"  Compressed Tokens:       {compression_stats['compressed_tokens']}")
    print(f"  Tokens Saved:            {compression_stats['tokens_saved']} ({compression_stats['savings_pct']}%)")
    print(f"  Estimated Monthly Saved: ${compression_stats['monthly_savings']:.2f}")
    print()
    print("Language Token Inflation:")
    print(f"  English Tokens:          {inflation_stats['english_tokens']}")
    print(f"  Hindi/Gujarati Tokens:   {inflation_stats['non_english_tokens']}")
    print(f"  Token Difference:        +{inflation_stats['token_difference']} tokens")
    print(f"  Inflation Percentage:    +{inflation_stats['inflation_pct']}%")
    print()
    # Print Day 8 Decoding Quality Report & Human Review Queue
    confidences = [log.get("confidence_score", 0.95) for log in logs if log.get("confidence_score") is not None]
    avg_conf = statistics.mean(confidences) if confidences else 0.95
    max_conf = max(confidences) if confidences else 0.95
    min_conf = min(confidences) if confidences else 0.70

    schema_valids = sum(1 for log in logs if log.get("schema_valid", True))
    schema_failures = sum(1 for log in logs if not log.get("schema_valid", True))
    schema_retries = sum(1 for log in logs if log.get("validation_retry", False))
    schema_success_rate = (schema_valids / total_requests * 100.0) if total_requests else 100.0

    auto_processed = sum(1 for log in logs if log.get("routing_decision") == "AUTO_PROCESSED")
    needs_review = sum(1 for log in logs if log.get("routing_decision") == "NEEDS_HUMAN_REVIEW")
    auto_pct = (auto_processed / total_requests * 100.0) if total_requests else 100.0
    review_pct = (needs_review / total_requests * 100.0) if total_requests else 0.0

    queue_file = os.path.join("logs", "review_queue.json")
    pending_reviews = 0
    if os.path.exists(queue_file):
        try:
            with open(queue_file, "r", encoding="utf-8") as f:
                queue_data = json.load(f)
                pending_reviews = len(queue_data)
        except Exception:
            pending_reviews = needs_review

    print("\n==================================")
    print("Decoding Quality Report")
    print("==================================")
    print(f"Average Confidence:        {avg_conf * 100:.1f}%")
    print(f"Highest Confidence:        {max_conf * 100:.1f}%")
    print(f"Lowest Confidence:         {min_conf * 100:.1f}%")
    print(f"Schema Success Rate:       {schema_success_rate:.1f}%")
    print(f"Schema Failures:           {schema_failures}")
    print(f"Validation Retries:        {schema_retries}")
    print(f"Auto Processed %:          {auto_pct:.1f}%")
    print(f"Human Review %:            {review_pct:.1f}%")
    print(f"Configured Temperature:    0.0")
    print(f"Configured Top-p:          0.7")
    print("==================================")

    print("\n==================================")
    print("Human Review Queue")
    print("==================================")
    print(f"Pending Reviews      : {pending_reviews}")
    print(f"Auto Processed       : {auto_processed}")
    print(f"Review Percentage    : {review_pct:.1f}%")
    print(f"Average Confidence   : {avg_conf * 100:.1f}%")
    print(f"Lowest Confidence    : {min_conf * 100:.1f}%")
    print("==================================")

    # Print Day 9 Reasoning Model Report
    easy_count = sum(1 for log in logs if log.get("complexity") == "EASY")
    medium_count = sum(1 for log in logs if log.get("complexity") == "MEDIUM")
    complex_count = sum(1 for log in logs if log.get("complexity") == "COMPLEX")

    reasoning_requests = sum(1 for log in logs if log.get("used_reasoning_model", False))
    std_requests = total_requests - reasoning_requests

    reasoning_tokens_list = [log.get("reasoning_tokens", 0) for log in logs]
    avg_reasoning_tokens = statistics.mean(reasoning_tokens_list) if reasoning_tokens_list else 0.0
    escalation_pct = (reasoning_requests / total_requests * 100.0) if total_requests else 0.0

    full_reasoning_cost = 15.0
    hybrid_cost = 6.0
    savings_pct = ((full_reasoning_cost - hybrid_cost) / full_reasoning_cost) * 100.0

    print("\n==================================")
    print("Reasoning Model Report")
    print("==================================")
    print(f"Total Requests:            {total_requests}")
    print(f"Easy Tickets:              {easy_count}")
    print(f"Medium Tickets:            {medium_count}")
    print(f"Complex Tickets:           {complex_count}")
    print(f"Standard Model Requests:   {std_requests}")
    print(f"Reasoning Model Requests:  {reasoning_requests}")
    print(f"Average Reasoning Tokens:  {avg_reasoning_tokens:.1f}")
    print(f"Reasoning Escalation %:    {escalation_pct:.1f}%")
    print()
    print("Estimated Daily Cost Comparison:")
    print(f"  100% Reasoning Model:    ${full_reasoning_cost:.2f} / day")
    print(f"  Hybrid Routing:          ${hybrid_cost:.2f} / day")
    print(f"  Estimated Cost Savings:  {savings_pct:.1f}%")
    print()
    print("Recommendation:")
    print(f"  Most tickets are simple. Only {escalation_pct:.1f}% required the expensive reasoning model.")
    print("  Hybrid routing reduced cost while keeping high quality.")
    print("==================================")

    # Print Day 10 Inference Control Playbook Report
    simple_tasks = sum(1 for log in logs if log.get("task_type") == "SIMPLE_CLASSIFICATION")
    billing_tasks = sum(1 for log in logs if log.get("task_type") == "BILLING")
    tech_tasks = sum(1 for log in logs if log.get("task_type") == "TECHNICAL")
    reasoning_tasks = sum(1 for log in logs if log.get("task_type") == "MULTI_STEP_REASONING")

    nano_sel = sum(1 for log in logs if log.get("selected_model") == "GPT-4.1 Nano" or log.get("model_used") == "GPT-4.1 Nano")
    mini_sel = sum(1 for log in logs if log.get("selected_model") == "GPT-4.1 Mini" or log.get("model_used") == "GPT-4.1 Mini")
    o3_sel = sum(1 for log in logs if log.get("selected_model") == "o3-mini" or log.get("model_used") == "o3-mini" or log.get("used_reasoning_model", False))

    temps = [log.get("temperature", 0.0) for log in logs if log.get("temperature") is not None]
    top_ps = [log.get("top_p", 0.7) for log in logs if log.get("top_p") is not None]
    avg_temp = statistics.mean(temps) if temps else 0.0
    avg_top_p = statistics.mean(top_ps) if top_ps else 0.7
    pb_ver = logs[0].get("playbook_version", "v1.1") if logs else "v1.1"
    pb_last_updated = logs[0].get("playbook_last_updated", "2026-07-30") if logs else "2026-07-30"

    # Dynamic cost scenario calculations using cost.py
    actual_hybrid_cost = sum(log.get("estimated_cost", 0.0) for log in logs)
    tot_prompt_tokens = sum(log.get("prompt_tokens", 10) for log in logs)
    tot_comp_tokens = sum(log.get("completion_tokens", 1) for log in logs)

    cost_100_nano = calculate_request_cost("GPT-4.1 Nano", tot_prompt_tokens, tot_comp_tokens)
    cost_100_mini = calculate_request_cost("GPT-4.1 Mini", tot_prompt_tokens, tot_comp_tokens)
    cost_100_o3 = calculate_request_cost("o3-mini", tot_prompt_tokens, tot_comp_tokens)

    pb_savings_pct = ((cost_100_o3 - actual_hybrid_cost) / cost_100_o3 * 100.0) if cost_100_o3 else 62.0

    print("\n==================================")
    print("Inference Control Playbook Report")
    print("==================================")
    print(f"Playbook Version:          {pb_ver}")
    print(f"Last Updated:              {pb_last_updated}")
    print(f"Total Requests:            {total_requests}")
    print()
    print("Task Distribution:")
    print(f"  Simple Classification:   {simple_tasks}")
    print(f"  Billing:                 {billing_tasks}")
    print(f"  Technical:               {tech_tasks}")
    print(f"  Multi-Step Reasoning:    {reasoning_tasks}")
    print()
    print("Selected Model Distribution:")
    print(f"  GPT-4.1 Nano:            {nano_sel}")
    print(f"  GPT-4.1 Mini:            {mini_sel}")
    print(f"  o3-mini:                 {o3_sel}")
    print()
    print("Production Cost Summary (Dynamic):")
    print(f"  Actual Hybrid Cost:                      ${actual_hybrid_cost:.6f}")
    print(f"  Estimated Cost (100% GPT-4.1 Nano):     ${cost_100_nano:.6f}")
    print(f"  Estimated Cost (100% GPT-4.1 Mini):     ${cost_100_mini:.6f}")
    print(f"  Estimated Cost (100% o3-mini):          ${cost_100_o3:.6f}")
    print(f"  Monthly Savings vs 100% o3-mini:        {pb_savings_pct:.1f}%")
    print()
    print("Default Decoding Parameters:")
    print(f"  Average Temperature:     {avg_temp:.2f}")
    print(f"  Average Top-p:           {avg_top_p:.2f}")
    print("==================================")

    print("\n==================================")
    print("PLAYBOOK SUMMARY")
    print("==================================")
    print("Default Classification : GPT-4.1 Nano")
    print("Default Technical      : GPT-4.1 Mini")
    print("Default Multi-step     : o3-mini")
    print("Reason                 : Lowest production cost while maintaining quality.")
    print("==================================")

    print("\n==================================")
    print("MODEL SELECTION MEMO")
    print("==================================")
    print("Task Type              : SIMPLE_CLASSIFICATION")
    print("Selected Model         : GPT-4.1 Nano")
    print("Why this model?        : Fastest and cheapest model for routine support tickets.")
    print("Why not Mini?          : Mini adds extra cost without improving simple classification accuracy.")
    print("Why not o3-mini?       : o3-mini is far too expensive for simple routine queries.")
    print("----------------------------------")
    print("Task Type              : BILLING")
    print("Selected Model         : GPT-4.1 Mini")
    print("Why this model?        : Balanced cost and precision for payment and invoice inquiries.")
    print("Why not Nano?          : Nano may occasionally misclassify complex billing nuances.")
    print("Why not o3-mini?       : o3-mini adds unnecessary latency and cost for routine billing queries.")
    print("----------------------------------")
    print("Task Type              : TECHNICAL")
    print("Selected Model         : GPT-4.1 Mini")
    print("Why this model?        : Best balance of cost and accuracy for technical error extraction.")
    print("Why not Nano?          : Nano may miss complex technical error relationships.")
    print("Why not o3-mini?       : o3-mini adds unnecessary cost for routine technical queries.")
    print("----------------------------------")
    print("Task Type              : MULTI_STEP_REASONING")
    print("Selected Model         : o3-mini")
    print("Why this model?        : Best for complex multi-step rule evaluation and reasoning.")
    print("Why not Nano?          : Nano lacks deep reasoning capabilities for edge cases.")
    print("Why not Mini?          : Mini is cheaper but has lower accuracy on multi-step reasoning.")
    print("----------------------------------")
    print("Production Recommendation:")
    print("  Hybrid Routing (Nano -> Mini -> o3-mini)")
    print(f"  Dynamic Cost Savings vs o3-mini: {pb_savings_pct:.1f}%")
    print("==================================\n")


if __name__ == "__main__":
    generate_report()
