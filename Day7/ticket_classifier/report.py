import os
import json
import statistics

# Default path to the JSONL log file generated in Step 1
LOG_FILE_PATH = os.path.join("logs", "llm_logs.jsonl")


def generate_report(log_file: str = LOG_FILE_PATH, batch_time: float = None):
    """Reads JSON logs and prints the improved Day 4 Cost & Latency Report summary."""

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

    # Calculate total cost and average cost per request
    total_cost = sum(log.get("estimated_cost", 0.0) for log in logs)
    avg_cost_per_request = (
        total_cost / total_requests if total_requests > 0 else 0.0
    )

    # Extract latency list for statistics calculation
    latencies = [
        log.get("latency_ms", 0.0)
        for log in logs
        if log.get("latency_ms") is not None
    ]

    if latencies:
        avg_latency = statistics.mean(latencies)
        p50_latency = statistics.median(latencies)
        sorted_latencies = sorted(latencies)
        p95_index = min(
            int(0.95 * len(sorted_latencies)), len(sorted_latencies) - 1
        )
        p95_latency = sorted_latencies[p95_index]
    else:
        avg_latency = p50_latency = p95_latency = 0.0

    # Batch execution time & throughput
    batch_time_str = f"{batch_time:.2f} s" if batch_time is not None else "N/A"
    throughput = (total_requests / batch_time) if batch_time and batch_time > 0 else None
    throughput_str = f"{throughput:.2f} req/s" if throughput is not None else "N/A"

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
    print(f"Average Latency:           {avg_latency:.2f} ms")
    print(f"P50 Latency:               {p50_latency:.2f} ms")
    print(f"P95 Latency:               {p95_latency:.2f} ms")
    print()
    print(f"Batch Execution Time:      {batch_time_str}")
    print(f"Throughput:                {throughput_str}")
    print()
    print("Logs Saved To:")
    print(log_file)
    print("==================================\n")


if __name__ == "__main__":
    generate_report()
