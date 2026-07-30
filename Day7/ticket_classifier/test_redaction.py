import os
import json
import tempfile
import unittest
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ticket_classifier.redaction import redact_text
from ticket_classifier.logger import log_llm_call


class TestRedaction(unittest.TestCase):

    def test_redact_email(self):
        text = "Please send invoice to john.doe@company.org regarding ticket."
        result = redact_text(text)
        self.assertNotIn("john.doe@company.org", result)
        self.assertIn("[REDACTED]", result)

    def test_redact_phone(self):
        text = "Call me at +1-555-123-4567 or 555-987-6543 immediately."
        result = redact_text(text)
        self.assertNotIn("+1-555-123-4567", result)
        self.assertNotIn("555-987-6543", result)
        self.assertIn("[REDACTED]", result)

    def test_redact_credit_card(self):
        text = "My card number is 4532 1234 5678 9012 for billing."
        result = redact_text(text)
        self.assertNotIn("4532 1234 5678 9012", result)
        self.assertIn("[REDACTED]", result)

    def test_redact_api_key(self):
        text = "My key is api_key=sk_live_998877665544332211."
        result = redact_text(text)
        self.assertNotIn("sk_live_998877665544332211", result)
        self.assertIn("[REDACTED]", result)

    def test_redact_password(self):
        text = "Account password=SecretP@ss1234!"
        result = redact_text(text)
        self.assertNotIn("SecretP@ss1234!", result)
        self.assertIn("[REDACTED]", result)

    def test_logger_redacts_pii_in_log_file(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            test_log_file = os.path.join(tmp_dir, "logs", "llm_logs.jsonl")

            sensitive_prompt = (
                "User john@example.com phoned +1-555-000-1111 with card 4111 2222 3333 4444"
            )
            sensitive_completion = "Approved for password=supersecret"

            log_llm_call(
                model_name="llama-3.3-70b",
                prompt=sensitive_prompt,
                completion=sensitive_completion,
                log_file=test_log_file,
            )

            self.assertTrue(os.path.exists(test_log_file))

            with open(test_log_file, "r", encoding="utf-8") as f:
                log_data = json.loads(f.readline())

            # Assert sensitive info is never present in log file output
            self.assertNotIn("john@example.com", log_data["prompt"])
            self.assertNotIn("+1-555-000-1111", log_data["prompt"])
            self.assertNotIn("4111 2222 3333 4444", log_data["prompt"])
            self.assertNotIn("supersecret", log_data["completion"])

            self.assertIn("[REDACTED]", log_data["prompt"])
            self.assertIn("[REDACTED]", log_data["completion"])


if __name__ == "__main__":
    unittest.main()

