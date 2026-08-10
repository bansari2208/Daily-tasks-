import os
import unittest
import sys
from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from .tracer import trace_llm_call


class TestTracer(unittest.TestCase):

    def test_trace_llm_call_without_api_key(self):
        # Verify that calling trace_llm_call without LANGSMITH_API_KEY does not crash
        with patch.dict(os.environ, {}, clear=True):
            try:
                trace_llm_call(
                    input="Payment issue",
                    output={"category": "Billing"},
                    latency=120.0,
                    retry_count=1,
                    provider="MockPrimary",
                    finish_reason="stop",
                )
            except Exception as e:
                self.fail(f"trace_llm_call raised an exception unexpectedly: {e}")

    def test_trace_llm_call_with_api_key(self):
        # Verify that tracing function executes gracefully with API key set
        with patch.dict(os.environ, {"LANGSMITH_API_KEY": "lsv2_pt_dummykey"}):
            try:
                trace_llm_call(
                    input="Reset password",
                    output={"category": "Technical"},
                    latency=95.5,
                    retry_count=0,
                    provider="MockPrimary",
                    finish_reason="stop",
                )
            except Exception as e:
                self.fail(f"trace_llm_call raised an exception unexpectedly: {e}")


if __name__ == "__main__":
    unittest.main()
