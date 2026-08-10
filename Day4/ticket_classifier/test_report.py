import os
import json
import tempfile
import unittest
import sys
from io import StringIO
from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from .logger import log_llm_call
from .report import generate_report


class TestReport(unittest.TestCase):

    def test_generate_report(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            test_log_file = os.path.join(tmp_dir, "logs", "llm_logs.jsonl")

            # Log 3 sample requests
            log_llm_call(
                model_name="llama-3.3-70b",
                prompt="Prompt 1",
                completion="Completion 1",
                prompt_tokens=10,
                completion_tokens=5,
                total_tokens=15,
                estimated_cost=0.001,
                latency_ms=100.0,
                retry_count=0,
                provider="MockPrimary",
                success=True,
                log_file=test_log_file,
            )

            log_llm_call(
                model_name="llama-3.3-70b",
                prompt="Prompt 2",
                completion="Completion 2",
                prompt_tokens=20,
                completion_tokens=10,
                total_tokens=30,
                estimated_cost=0.002,
                latency_ms=200.0,
                retry_count=1,
                provider="MockPrimary",
                success=True,
                log_file=test_log_file,
            )

            log_llm_call(
                model_name="llama-3.3-70b",
                prompt="Prompt 3",
                completion="Failed",
                prompt_tokens=5,
                completion_tokens=0,
                total_tokens=5,
                estimated_cost=0.0005,
                latency_ms=300.0,
                retry_count=2,
                provider="MockFallback",
                success=False,
                log_file=test_log_file,
            )

            # Capture console output
            captured_output = StringIO()
            with patch("sys.stdout", captured_output):
                generate_report(log_file=test_log_file, batch_time=2.5)

            output = captured_output.getvalue()

            self.assertIn("Requests:                  3", output)
            self.assertIn("Primary Success:           2", output)
            self.assertIn("Fallback Success:          1", output)
            self.assertIn("Failed Requests:           1", output)
            self.assertIn("Retry Rate:                66.67%", output)
            self.assertIn("Average Retries/Request:   1.00", output)
            self.assertIn("Total Tokens:              50", output)
            self.assertIn("Prompt Tokens:             35", output)
            self.assertIn("Completion Tokens:         15", output)
            self.assertIn("Total Cost:                $0.003500", output)
            self.assertIn("Average Latency:           200.00 ms", output)
            self.assertIn("P50 Latency:               200.00 ms", output)
            self.assertIn("Batch Execution Time:      2.50 s", output)
            self.assertIn("Throughput:                1.20 req/s", output)
            self.assertIn("Logs Saved To:", output)


if __name__ == "__main__":
    unittest.main()
