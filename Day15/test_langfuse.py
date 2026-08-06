import os
import sys
from dotenv import load_dotenv

# Load environment variables from Day15/.env
load_dotenv()
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

# Resolve host from LANGFUSE_BASE_URL or LANGFUSE_HOST
host = os.getenv("LANGFUSE_HOST") or os.getenv("LANGFUSE_BASE_URL") or "https://cloud.langfuse.com"
os.environ["LANGFUSE_HOST"] = host
os.environ["LANGFUSE_BASE_URL"] = host
os.environ["LANGFUSE_DEBUG"] = "True"

from langfuse import Langfuse, observe

print("\n==========================================")
print("     LANGFUSE LIVE TRACING TEST           ")
print("==========================================")
print("Host       :", host)
print("Public Key :", os.getenv("LANGFUSE_PUBLIC_KEY")[:12] + "...")
print("==========================================\n")

client = Langfuse(host=host)

# 1. Verify Authentication
auth_ok = client.auth_check()
print("Auth Check Result:", auth_ok)

# 2. Fetch Prompt Version 1 & Version 2
p1 = client.get_prompt("ticket_classifier 1", version=1)
print(f"Fetched Prompt v1: Name='{p1.name}', Version={p1.version}, Labels={p1.labels}")

p2 = client.get_prompt("ticket_classifier 1", version=2)
print(f"Fetched Prompt v2: Name='{p2.name}', Version={p2.version}, Labels={p2.labels}\n")

# 3. Create Traces & Linked Generations using @observe
@observe(name="test_ticket_classification_v1")
def run_v1_classification(ticket_text: str):
    compiled = p1.compile(ticket=ticket_text)
    gen = client.start_observation(
        name="llm_generation_v1",
        as_type="generation",
        model="gpt-4.1-mini",
        prompt=p1,  # Link generation directly to Prompt v1
        input={"ticket": ticket_text, "compiled_prompt": compiled},
        output={"category": "Billing", "priority": "HIGH", "reason": "Payment failed"},
        usage_details={"input": 120, "output": 35, "total": 155},
        metadata={"environment": "production", "prompt_version": p1.version}
    )
    return getattr(gen, "id", "obs-v1")

@observe(name="test_ticket_classification_v2")
def run_v2_classification(ticket_text: str):
    compiled = p2.compile(ticket=ticket_text)
    gen = client.start_observation(
        name="llm_generation_v2",
        as_type="generation",
        model="gpt-4.1-mini",
        prompt=p2,  # Link generation directly to Prompt v2
        input={"ticket": ticket_text, "compiled_prompt": compiled},
        output={"category": "Billing", "priority": "HIGH", "urgency_score": 0.9, "confidence": 0.95},
        usage_details={"input": 165, "output": 48, "total": 213},
        metadata={"environment": "production", "prompt_version": p2.version}
    )
    return getattr(gen, "id", "obs-v2")

print("Executing Traced Functions...")
obs1_id = run_v1_classification("Payment failed on checkout page")
print(f"v1 Generation Created: ID={obs1_id}")

obs2_id = run_v2_classification("Password reset request for admin")
print(f"v2 Generation Created: ID={obs2_id}")

# 4. Flush and Shutdown Telemetry Exporters
print("\nFlushing Langfuse Telemetry...")
client.flush()
client.shutdown()

print("==========================================")
print(" [SUCCESS] Test Traces & Generations Flushed!")
print("==========================================\n")
