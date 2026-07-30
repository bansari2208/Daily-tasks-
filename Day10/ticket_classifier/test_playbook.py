import unittest
import asyncio
from ticket_classifier.playbook import (
    detect_task_type,
    get_recommended_model,
    get_model_reason,
    get_model_tradeoffs,
    get_default_temperature,
    get_default_top_p,
    get_playbook_version,
    get_playbook_last_updated,
)
from ticket_classifier.client import AsyncLLMClient


class TestPlaybookModule(unittest.TestCase):

    def test_detect_task_type(self):
        self.assertEqual(detect_task_type("Please unlock my account"), "SIMPLE_CLASSIFICATION")
        self.assertEqual(detect_task_type("Payment card failed on checkout"), "BILLING")
        self.assertEqual(detect_task_type("Mobile app crash bug report"), "TECHNICAL")
        self.assertEqual(detect_task_type("Refund request for tax invoice after 404 error"), "MULTI_STEP_REASONING")

    def test_get_recommended_model(self):
        self.assertEqual(get_recommended_model("SIMPLE_CLASSIFICATION"), "GPT-4.1 Nano")
        self.assertEqual(get_recommended_model("BILLING"), "GPT-4.1 Mini")
        self.assertEqual(get_recommended_model("TECHNICAL"), "GPT-4.1 Mini")
        self.assertEqual(get_recommended_model("MULTI_STEP_REASONING"), "o3-mini")

    def test_get_model_reason(self):
        reason_simple = get_model_reason("SIMPLE_CLASSIFICATION")
        reason_billing = get_model_reason("BILLING")
        self.assertIn("Fastest", reason_simple)
        self.assertIn("Balanced", reason_billing)

    def test_get_model_tradeoffs(self):
        tradeoffs = get_model_tradeoffs("TECHNICAL")
        self.assertEqual(tradeoffs["selected"], "GPT-4.1 Mini")
        self.assertIn("why_selected", tradeoffs)
        self.assertIn("why_not_nano", tradeoffs)
        self.assertIn("why_not_reasoning", tradeoffs)

    def test_get_default_parameters(self):
        self.assertEqual(get_default_temperature("SIMPLE_CLASSIFICATION"), 0.0)
        self.assertEqual(get_default_temperature("MULTI_STEP_REASONING"), 0.2)
        self.assertEqual(get_default_top_p("TECHNICAL"), 0.7)
        self.assertEqual(get_playbook_version(), "v1.1")
        self.assertEqual(get_playbook_last_updated(), "2026-07-30")

    def test_client_playbook_metadata(self):
        client = AsyncLLMClient()

        async def run():
            res = await client.classify_ticket("Payment card failed twice", ticket_id=55)
            self.assertIn("task_type", res)
            self.assertIn("selected_model", res)
            self.assertIn("temperature", res)
            self.assertIn("top_p", res)
            self.assertIn("playbook_version", res)
            self.assertIn("playbook_last_updated", res)
            self.assertEqual(res["playbook_version"], "v1.1")
            self.assertEqual(res["playbook_last_updated"], "2026-07-30")

        asyncio.run(run())


if __name__ == "__main__":
    unittest.main()
