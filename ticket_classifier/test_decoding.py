import os
import json
import tempfile
import unittest
import asyncio
from ticket_classifier.config import (
    TEMPERATURE,
    TOP_P,
    CONFIDENCE_THRESHOLD,
    SCHEMA_VALIDATION,
)
from ticket_classifier.client import AsyncLLMClient, validate_response_schema
from ticket_classifier.logger import save_to_review_queue


class TestDecodingModule(unittest.TestCase):

    def test_config_defaults(self):
        self.assertEqual(TEMPERATURE, 0.0)
        self.assertEqual(TOP_P, 0.7)
        self.assertEqual(CONFIDENCE_THRESHOLD, 0.80)
        self.assertTrue(SCHEMA_VALIDATION)

    def test_validate_response_schema(self):
        valid = {"category": "Billing", "confidence": 0.95}
        self.assertTrue(validate_response_schema(valid))

        invalid_empty = {"category": ""}
        self.assertFalse(validate_response_schema(invalid_empty))

        invalid_type = "not a dict"
        self.assertFalse(validate_response_schema(invalid_type))

    def test_save_to_review_queue(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            test_queue_file = os.path.join(tmp_dir, "logs", "review_queue.json")
            entry = save_to_review_queue(
                ticket_id=101,
                category="General",
                confidence=0.64,
                reason="Low Confidence (< 0.80)",
                queue_file=test_queue_file,
            )

            self.assertTrue(os.path.exists(test_queue_file))
            self.assertEqual(entry["ticket_id"], 101)
            self.assertIn("timestamp", entry)
            self.assertEqual(entry["confidence"], 0.64)

            with open(test_queue_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            self.assertEqual(len(data), 1)
            self.assertEqual(data[0]["category"], "General")

    def test_confidence_and_routing_fields(self):
        client = AsyncLLMClient()

        async def run():
            res = await client.classify_ticket("Payment issue with credit card", ticket_id=1)
            self.assertIn("confidence", res)
            self.assertIn("routing", res)
            self.assertIn(res["routing"], ("AUTO_PROCESSED", "NEEDS_HUMAN_REVIEW"))

        asyncio.run(run())


if __name__ == "__main__":
    unittest.main()
