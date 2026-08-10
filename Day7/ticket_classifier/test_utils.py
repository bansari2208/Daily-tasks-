import os
import json
import tempfile
import unittest
import sys
from io import StringIO
from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from .utils import timer
from .logger import log_llm_call


class TestUtils(unittest.TestCase):

    def test_timer_context_manager(self):
        captured_output = StringIO()
        with patch("sys.stdout", captured_output):
            with timer("Test Block"):
                x = sum(i * i for i in range(1000))

        output = captured_output.getvalue()
        self.assertIn("[Test Block] Started...", output)
        self.assertIn("[Test Block] Finished in", output)

    def test_opentelemetry_span_fields_in_logger(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            test_log_file = os.path.join(tmp_dir, "logs", "llm_logs.jsonl")

            entry = log_llm_call(
                model_name="llama-3.3-70b",
                prompt="Hello",
                completion="World",
                log_file=test_log_file,
            )

            # Check that OpenTelemetry span fields exist in entry and saved log
            self.assertIn("trace_id", entry)
            self.assertIn("span_id", entry)
            self.assertIn("parent_span_id", entry)
            self.assertIn("start_time", entry)
            self.assertIn("end_time", entry)
            self.assertIn("duration_ms", entry)

            with open(test_log_file, "r", encoding="utf-8") as f:
                log_data = json.loads(f.readline())

            self.assertIn("span_id", log_data)
            self.assertIn("start_time", log_data)
            self.assertIn("end_time", log_data)


if __name__ == "__main__":
    unittest.main()

