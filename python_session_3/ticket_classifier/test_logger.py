import os
import json
import tempfile
import unittest
import sys


from ticket_classifier.logger import log_llm_call


class TestLogger(unittest.TestCase):

    def test_log_llm_call(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            test_log_file = os.path.join(tmp_dir, "logs", "llm_logs.jsonl")

            entry = log_llm_call(
                model_name="llama-3.3-70b",
                prompt="Classify ticket: Payment failed",
                completion="Billing",
                prompt_tokens=15,
                completion_tokens=5,
                total_tokens=20,
                estimated_cost=0.0001,
                latency_ms=120.5,
                retry_count=1,
                finish_reason="stop",
                provider="MockPrimary",
                success=True,
                log_file=test_log_file,
            )

            self.assertTrue(os.path.exists(test_log_file))

            with open(test_log_file, "r", encoding="utf-8") as f:
                lines = f.readlines()

            self.assertEqual(len(lines), 1)
            data = json.loads(lines[0])

            required_fields = [
                "trace_id",
                "timestamp",
                "model_name",
                "prompt",
                "completion",
                "prompt_tokens",
                "completion_tokens",
                "total_tokens",
                "estimated_cost",
                "latency_ms",
                "retry_count",
                "finish_reason",
                "provider",
                "success",
            ]

            for field in required_fields:
                self.assertIn(field, data)

            self.assertEqual(data["model_name"], "llama-3.3-70b")
            self.assertEqual(data["prompt"], "Classify ticket: Payment failed")
            self.assertEqual(data["completion"], "Billing")
            self.assertEqual(data["prompt_tokens"], 15)
            self.assertEqual(data["completion_tokens"], 5)
            self.assertEqual(data["total_tokens"], 20)
            self.assertEqual(data["estimated_cost"], 0.0001)
            self.assertEqual(data["latency_ms"], 120.5)
            self.assertEqual(data["retry_count"], 1)
            self.assertEqual(data["finish_reason"], "stop")
            self.assertEqual(data["provider"], "MockPrimary")
            self.assertTrue(data["success"])


if __name__ == "__main__":
    unittest.main()

