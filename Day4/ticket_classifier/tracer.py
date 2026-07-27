import os
import uuid
from dotenv import load_dotenv

# 1. Read credentials from .env file
env_path = os.path.join(os.path.dirname(__file__), ".env")
if not os.path.exists(env_path):
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
load_dotenv(dotenv_path=env_path)

LANGFUSE_PUBLIC_KEY = os.getenv("LANGFUSE_PUBLIC_KEY")
LANGFUSE_SECRET_KEY = os.getenv("LANGFUSE_SECRET_KEY")
LANGFUSE_BASE_URL = os.getenv("LANGFUSE_BASE_URL") or os.getenv("LANGFUSE_HOST")

# Global session ID per batch execution
current_session_id = f"session_{uuid.uuid4().hex[:12]}"

# Counter for sent traces
langfuse_trace_count = 0

# 2. Initialize Langfuse v4 client safely
langfuse_client = None
if LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY:
    try:
        from langfuse import Langfuse
        langfuse_client = Langfuse(
            public_key=LANGFUSE_PUBLIC_KEY,
            secret_key=LANGFUSE_SECRET_KEY,
            host=LANGFUSE_BASE_URL
        )
    except Exception:
        langfuse_client = None

# Check for LangSmith API Key
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY") or os.getenv("LANGCHAIN_API_KEY")

try:
    from langsmith import traceable

    @traceable(name="llm_ticket_classification", run_type="llm")
    def _record_trace(
        input: str,
        output: dict,
        latency: float,
        retry_count: int,
        provider: str,
        finish_reason: str,
    ) -> dict:
        return {
            "input": input,
            "output": output,
            "latency": latency,
            "retry_count": retry_count,
            "provider": provider,
            "finish_reason": finish_reason,
        }

except Exception:
    _record_trace = None


def get_tracing_status() -> str:
    """Returns status string indicating whether Langfuse tracing is enabled or disabled."""
    if langfuse_client is not None:
        return "Tracing: Enabled (Langfuse)"
    return "Tracing: Disabled"


def trace_langfuse_call(
    ticket_id: int,
    input_text: str,
    output_data: dict,
    latency_ms: float = 0.0,
    retry_count: int = 0,
    finish_reason: str = "stop",
    provider: str = "unknown",
    success: bool = True,
    trace_id: str = None,
    session_id: str = None
) -> str:
    """Manually creates exactly one trace in Langfuse with session_id, tags, and metadata."""
    global langfuse_trace_count
    if langfuse_client is None:
        return trace_id

    fallback_used = (provider == "MockFallback" or output_data.get("status") == "fallback_success")
    effective_session_id = session_id or current_session_id

    try:
        obs = langfuse_client.start_observation(
            name="classify_ticket",
            as_type="generation",
            input=input_text,
            output=output_data,
            model="llama-3.3-70b",
            metadata={
                "session_id": effective_session_id,
                "ticket_id": ticket_id,
                "provider": provider,
                "retry_count": retry_count,
                "fallback_used": fallback_used,
                "latency_ms": latency_ms,
                "finish_reason": finish_reason,
                "success": success,
                "tags": ["day4", "ticket-classifier", "demo"],
                "trace_id": trace_id,
            }
        )
        obs.end()
        langfuse_trace_count += 1
        return obs.trace_id
    except Exception:
        return trace_id


def flush_langfuse_traces():
    """Flushes all pending traces safely to Langfuse server and prints summary report."""
    if langfuse_client is not None:
        try:
            langfuse_client.flush()
            base_url = LANGFUSE_BASE_URL or "https://hipaa.cloud.langfuse.com"
            print("\n-----------------------------------")
            print("Langfuse Summary")
            print("-----------------------------------")
            print("Tracing: Enabled (Langfuse)")
            print(f"Session ID: {current_session_id}")
            print(f"Traces Sent: {langfuse_trace_count}")
            print("Flush Status: Success")
            print(f"Dashboard: {base_url}")
            print("-----------------------------------\n")
        except Exception:
            pass


def trace_llm_call(
    input: str,
    output: dict,
    latency: float = 0.0,
    retry_count: int = 0,
    provider: str = "unknown",
    finish_reason: str = "stop",
):
    """Wraps an LLM request inside a LangSmith trace."""
    if not LANGSMITH_API_KEY or _record_trace is None:
        return

    try:
        _record_trace(
            input=input,
            output=output,
            latency=latency,
            retry_count=retry_count,
            provider=provider,
            finish_reason=finish_reason,
        )
    except Exception:
        pass
