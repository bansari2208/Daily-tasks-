import json
import os
import sys


def summarize_logs(log_file_path: str = "logs/llm_logs.jsonl"):
    """
    Reads JSONL logs and prints a summary table:
    request count per provider, average latency, and total cost.
    """
    if not os.path.exists(log_file_path):
        # Fallback path if run from a subfolder
        alt_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs", "llm_logs.jsonl")
        if os.path.exists(alt_path):
            log_file_path = alt_path

    if not os.path.exists(log_file_path):
        print(f"Log file not found: {log_file_path}")
        return

    provider_stats = {}

    with open(log_file_path, "r", encoding="utf-8") as f:
        for line in f:
            line_str = line.strip()
            if not line_str:
                continue
            try:
                data = json.loads(line_str)
            except json.JSONDecodeError:
                continue

            provider = data.get("provider") or "Unknown"

            # Latency fallback checking latency_ms, duration_ms, or total_latency_ms
            latency = data.get("latency_ms")
            if latency is None:
                latency = data.get("duration_ms")
            if latency is None:
                latency = data.get("total_latency_ms")
            if latency is None:
                latency = 0.0

            cost = data.get("estimated_cost")
            if cost is None:
                cost = 0.0

            if provider not in provider_stats:
                provider_stats[provider] = {"count": 0, "total_latency": 0.0, "total_cost": 0.0}

            provider_stats[provider]["count"] += 1
            provider_stats[provider]["total_latency"] += float(latency)
            provider_stats[provider]["total_cost"] += float(cost)

    if not provider_stats:
        print("No valid log entries found.")
        return

    print("=" * 64)
    print("                    LLM Log Summary Table                       ")
    print("=" * 64)
    print(f"{'Provider':<18} | {'Count':<8} | {'Avg Latency':<14} | {'Total Cost':<12}")
    print("-" * 64)

    total_count = 0
    total_latency_sum = 0.0
    total_cost_sum = 0.0

    for provider, stats in provider_stats.items():
        count = stats["count"]
        avg_lat = stats["total_latency"] / count if count > 0 else 0.0
        cost = stats["total_cost"]

        total_count += count
        total_latency_sum += stats["total_latency"]
        total_cost_sum += cost

        print(f"{provider:<18} | {count:<8} | {avg_lat:<11.2f} ms | ${cost:<11.6f}")

    print("-" * 64)
    overall_avg_lat = total_latency_sum / total_count if total_count > 0 else 0.0
    print(f"{'TOTAL':<18} | {total_count:<8} | {overall_avg_lat:<11.2f} ms | ${total_cost_sum:<11.6f}")
    print("=" * 64)


if __name__ == "__main__":
    log_path = sys.argv[1] if len(sys.argv) > 1 else "logs/llm_logs.jsonl"
    summarize_logs(log_path)
