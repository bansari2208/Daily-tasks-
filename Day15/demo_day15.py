import sys
import os
from dotenv import load_dotenv

# Ensure project root is in sys.path

# Load environment variables
load_dotenv()
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

host = os.getenv("LANGFUSE_HOST") or os.getenv("LANGFUSE_BASE_URL") or "https://cloud.langfuse.com"
os.environ["LANGFUSE_HOST"] = host
os.environ["LANGFUSE_BASE_URL"] = host

from langfuse import observe
from Day15.langfuse_integration import LangfusePromptManager
from Day15.canary_release import CanaryPromptRouter
from Day15.logger_extension import log_llm_call_versioned


@observe(name="day15_master_demo_trace")
def main():
    print("=========================================================================================")
    print("      Day 15: Prompt Versioning & Management with Langfuse (Master Demo Script)         ")
    print("=========================================================================================\n")

    manager = LangfusePromptManager()

    # 1. Prompt Registry & Retrieval Demonstrations
    print("--- 1. Langfuse Prompt Registry Demonstrations ---")
    prompt_name = "ticket_classifier 1"

    p_prod = manager.get_prompt_by_label(prompt_name, label="production")
    p_v1 = manager.get_prompt_by_version(prompt_name, version=1)
    p_v2 = manager.get_prompt_by_version(prompt_name, version=2)
    p_latest = manager.get_prompt_by_label(prompt_name, label="latest")

    print(f"[OK] Production Prompt Name : {p_prod.name} | Version = {p_prod.version} | Labels = {p_prod.labels}")
    print(f"[OK] Explicit Version 1     : {p_v1.name} | Version = {p_v1.version} | Labels = {p_v1.labels}")
    print(f"[OK] Explicit Version 2     : {p_v2.name} | Version = {p_v2.version} | Labels = {p_v2.labels}")
    print(f"[OK] Latest Version Prompt  : {p_latest.name} | Version = {p_latest.version} | Labels = {p_latest.labels}\n")

    # 2. Template Safety & Prompt Compilation
    print("--- 2. Template Safety & Prompt Compilation ---")
    sample_ticket = "Payment failed twice on checkout page when attempting to upgrade my subscription."
    compiled_v1 = manager.compile_prompt(p_v1, sample_ticket)
    compiled_v2 = manager.compile_prompt(p_v2, sample_ticket)

    print("[OK] Compiled Version 1 Prompt:")
    print("-" * 60)
    print(compiled_v1)
    print("-" * 60)

    print("\n[OK] Compiled Version 2 Prompt:")
    print("-" * 60)
    print(compiled_v2)
    print("-" * 60 + "\n")

    # 3. Langfuse Trace & Generation Logging
    print("--- 3. Langfuse Prompt Version Telemetry & Traces ---")
    trace_res_v1 = manager.log_traced_generation(
        prompt_obj=p_v1,
        ticket_text=sample_ticket,
        compiled_prompt=compiled_v1,
        completion_text='{"category": "Billing", "priority": "HIGH", "reason": "Payment failure"}',
        model_name="gpt-4.1-mini",
        prompt_tokens=120,
        completion_tokens=35,
        latency_ms=290.0
    )
    print(f"[OK] Trace Name: 'ticket_classification_traced' | Generation Name: 'llm_generation_v1' | ObsID: {trace_res_v1.get('observation_id')} | Prompt: '{trace_res_v1['prompt_name']}' v{trace_res_v1['prompt_version']}")

    trace_res_v2 = manager.log_traced_generation(
        prompt_obj=p_v2,
        ticket_text=sample_ticket,
        compiled_prompt=compiled_v2,
        completion_text='{"category": "Billing", "priority": "HIGH", "urgency_score": 0.90, "confidence": 0.95, "reason": "Payment processing error"}',
        model_name="gpt-4.1-mini",
        prompt_tokens=170,
        completion_tokens=48,
        latency_ms=330.0
    )
    print(f"[OK] Trace Name: 'ticket_classification_traced' | Generation Name: 'llm_generation_v2' | ObsID: {trace_res_v2.get('observation_id')} | Prompt: '{trace_res_v2['prompt_name']}' v{trace_res_v2['prompt_version']}\n")

    # 4. Extended JSONL Logging (Day 4 Schema Extension)
    print("--- 4. Extended Structured JSONL Logging ---")
    log_entry = log_llm_call_versioned(
        model_name="gpt-4.1-mini",
        prompt=compiled_v1,
        completion='{"category": "Billing", "priority": "HIGH"}',
        prompt_name=prompt_name,
        prompt_version=str(p_v1.version),
        prompt_tokens=120,
        completion_tokens=35,
        estimated_cost=0.00033,
        latency_ms=290.0,
        provider="langfuse"
    )
    print(f"[OK] Structured JSONL entry recorded: prompt_name='{log_entry['prompt_name']}', prompt_version='{log_entry['prompt_version']}'\n")

    # 5. 90/10 Canary Release Simulation
    print("--- 5. 90/10 Canary Traffic Router Simulation (20 Tickets) ---")
    router = CanaryPromptRouter(manager=manager, prompt_name=prompt_name, canary_ratio=0.10)
    sample_tickets = [f"Ticket payload #{i+1}: Issue with login/payment" for i in range(20)]
    canary_summary = router.process_batch(sample_tickets)

    print(f"[OK] Canary Traffic Distribution : Version 1 ({canary_summary['production_pct']}%) vs Version 2 ({canary_summary['candidate_pct']}%)")
    print(f"  - Total Processed           : {canary_summary['total_processed']}")
    print(f"  - Production (v1, 90%)      : {canary_summary['production_count']}")
    print(f"  - Candidate (v2, 10%)       : {canary_summary['candidate_count']}")
    print("  - Executions Summary:")
    for ex in canary_summary["executions"][:3]:
        print(f"    * [{ex['arm']}] Prompt '{ex['prompt_name']}' v{ex['prompt_version']}")
    print("\n")

    # 6. Zero-Code Label Rollback Simulation
    print("--- 6. Zero-Code Label Rollback Simulation ---")
    print("Scenario: Candidate v2 latency spike detected. Immediate rollback triggered in Langfuse UI.")
    print("Action  : 'production' label pointed back to Version 1.")
    p_rolled_back = manager.get_prompt_by_label(prompt_name, label="production")
    print(f"[OK] Rollback Summary: Active Production Prompt Version = {p_rolled_back.version} (Zero code changes required!)")

    print("\n=========================================================================================")
    print("                       [SUCCESS] Day 15 Master Demo Completed!                            ")
    print("=========================================================================================\n")

    # Flush & shutdown client telemetry
    manager.client.flush()
    manager.client.shutdown()


if __name__ == "__main__":
    main()
