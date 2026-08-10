import unittest
import asyncio
from .reasoning import (
    analyze_ticket_complexity,
    should_use_reasoning_model,
    estimate_reasoning_tokens,
)
from .config import STANDARD_MODEL, REASONING_MODEL
from .client import AsyncLLMClient


class TestReasoningModule(unittest.TestCase):

    def test_analyze_ticket_complexity(self):
        self.assertEqual(analyze_ticket_complexity("Please reset password"), "EASY")
        self.assertEqual(analyze_ticket_complexity("My payment failed on checkout"), "MEDIUM")
        self.assertEqual(analyze_ticket_complexity("Need duplicate charge refund for invoice"), "COMPLEX")

    def test_should_use_reasoning_model(self):
        self.assertFalse(should_use_reasoning_model("EASY"))
        self.assertFalse(should_use_reasoning_model("MEDIUM"))
        self.assertTrue(should_use_reasoning_model("COMPLEX"))

    def test_estimate_reasoning_tokens(self):
        self.assertEqual(estimate_reasoning_tokens("EASY"), 0)
        self.assertEqual(estimate_reasoning_tokens("MEDIUM"), 150)
        self.assertEqual(estimate_reasoning_tokens("COMPLEX"), 700)

    def test_client_reasoning_metadata(self):
        client = AsyncLLMClient()

        async def run():
            res = await client.classify_ticket("Need duplicate refund for tax invoice #101", ticket_id=99)
            self.assertIn("complexity", res)
            self.assertEqual(res["complexity"], "COMPLEX")
            self.assertEqual(res["model_used"], REASONING_MODEL)
            self.assertEqual(res["reasoning_tokens"], 700)

        asyncio.run(run())


if __name__ == "__main__":
    unittest.main()
