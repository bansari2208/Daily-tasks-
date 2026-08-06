import os
import sys
from dotenv import load_dotenv

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Load environment variables
load_dotenv()
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

host = os.getenv("LANGFUSE_HOST") or os.getenv("LANGFUSE_BASE_URL") or "https://cloud.langfuse.com"
os.environ["LANGFUSE_HOST"] = host
os.environ["LANGFUSE_BASE_URL"] = host

from langfuse import Langfuse
from Day15.langfuse_integration import LangfusePromptManager
from Day15.canary_release import CanaryPromptRouter


def run_verification():
    print("=========================================================================================")
    print("            Day 15: Langfuse Integration & Telemetry Verification Helper               ")
    print("=========================================================================================\n")

    prompt_name = "ticket_classifier 1"
    checks = []

    # Check 1: Client Authentication & Prompt Registry Access
    try:
        manager = LangfusePromptManager()
        auth_ok = manager.client.auth_check()
        if auth_ok:
            checks.append(("Prompt Registry & Client Auth Access", "PASS", f"Connected to {manager.host}"))
        else:
            checks.append(("Prompt Registry & Client Auth Access", "FAIL", "Auth check returned False"))
    except Exception as e:
        checks.append(("Prompt Registry & Client Auth Access", "FAIL", str(e)))
        manager = None

    if not manager:
        print("Initialization failed. Stopping verification.")
        return

    # Check 2: Prompt Version 1 Retrieval & Compilation
    try:
        p_v1 = manager.get_prompt_by_version(prompt_name, version=1)
        compiled_v1 = manager.compile_prompt(p_v1, "Test payload for version 1")
        if p_v1.version == 1 and compiled_v1:
            checks.append(("Prompt Version 1 Retrieval & Compilation", "PASS", f"Name='{p_v1.name}', Version=1, Labels={p_v1.labels}"))
        else:
            checks.append(("Prompt Version 1 Retrieval & Compilation", "FAIL", f"Version mismatch: {p_v1.version}"))
    except Exception as e:
        checks.append(("Prompt Version 1 Retrieval & Compilation", "FAIL", str(e)))

    # Check 3: Prompt Version 2 Retrieval & Compilation
    try:
        p_v2 = manager.get_prompt_by_version(prompt_name, version=2)
        compiled_v2 = manager.compile_prompt(p_v2, "Test payload for version 2")
        if p_v2.version == 2 and compiled_v2:
            checks.append(("Prompt Version 2 Retrieval & Compilation", "PASS", f"Name='{p_v2.name}', Version=2, Labels={p_v2.labels}"))
        else:
            checks.append(("Prompt Version 2 Retrieval & Compilation", "FAIL", f"Version mismatch: {p_v2.version}"))
    except Exception as e:
        checks.append(("Prompt Version 2 Retrieval & Compilation", "FAIL", str(e)))

    # Check 4: Version 1 Linked Generation Trace Export
    try:
        res_v1 = manager.log_traced_generation(
            prompt_obj=p_v1,
            ticket_text="Billing issue: Payment failed",
            compiled_prompt=compiled_v1,
            completion_text='{"category": "Billing", "priority": "HIGH"}',
            model_name="gpt-4.1-mini",
            prompt_tokens=100,
            completion_tokens=25
        )
        if res_v1.get("observation_id"):
            checks.append(("Version 1 Linked Generation Export", "PASS", f"ObsID={res_v1['observation_id']}"))
        else:
            checks.append(("Version 1 Linked Generation Export", "FAIL", "Missing observation_id"))
    except Exception as e:
        checks.append(("Version 1 Linked Generation Export", "FAIL", str(e)))

    # Check 5: Version 2 Linked Generation Trace Export
    try:
        res_v2 = manager.log_traced_generation(
            prompt_obj=p_v2,
            ticket_text="Technical issue: System crash",
            compiled_prompt=compiled_v2,
            completion_text='{"category": "Technical", "priority": "HIGH", "confidence": 0.99}',
            model_name="gpt-4.1-mini",
            prompt_tokens=150,
            completion_tokens=40
        )
        if res_v2.get("observation_id"):
            checks.append(("Version 2 Linked Generation Export", "PASS", f"ObsID={res_v2['observation_id']}"))
        else:
            checks.append(("Version 2 Linked Generation Export", "FAIL", "Missing observation_id"))
    except Exception as e:
        checks.append(("Version 2 Linked Generation Export", "FAIL", str(e)))

    # Check 6: Canary Release Traffic Router
    try:
        router = CanaryPromptRouter(manager=manager, prompt_name=prompt_name, canary_ratio=0.10)
        batch_summary = router.process_batch(["Test ticket"] * 10)
        if batch_summary["total_processed"] == 10:
            checks.append(("Canary 90/10 Traffic Router Simulation", "PASS", f"Processed=10, Prod={batch_summary['production_count']}, Candidate={batch_summary['candidate_count']}"))
        else:
            checks.append(("Canary 90/10 Traffic Router Simulation", "FAIL", "Total processed mismatch"))
    except Exception as e:
        checks.append(("Canary 90/10 Traffic Router Simulation", "FAIL", str(e)))

    # Check 7: Zero-Code Label Rollback Simulation
    try:
        p_rollback = manager.get_prompt_by_label(prompt_name, label="production")
        if p_rollback.version == 1:
            checks.append(("Zero-Code Production Label Rollback", "PASS", "Active production prompt resolved to Version 1"))
        else:
            checks.append(("Zero-Code Production Label Rollback", "FAIL", f"Expected Version 1, got {p_rollback.version}"))
    except Exception as e:
        checks.append(("Zero-Code Production Label Rollback", "FAIL", str(e)))

    # Flush telemetry
    manager.client.flush()
    manager.client.shutdown()

    # Print Summary Table
    print("\n-----------------------------------------------------------------------------------------")
    print(f"{'CHECK ITEM':<42} | {'STATUS':<6} | {'DETAILS'}")
    print("-----------------------------------------------------------------------------------------")
    all_passed = True
    for item, status, details in checks:
        color_status = f"[{status}]"
        print(f"{item:<42} | {color_status:<6} | {details}")
        if status != "PASS":
            all_passed = False
    print("-----------------------------------------------------------------------------------------\n")

    if all_passed:
        print("=========================================================================================")
        print("                 [OVERALL RESULT: PASS] All Day 15 Requirements Verified!                ")
        print("=========================================================================================\n")
    else:
        print("=========================================================================================")
        print("                 [OVERALL RESULT: FAIL] Some Verification Checks Failed.                  ")
        print("=========================================================================================\n")


if __name__ == "__main__":
    run_verification()
