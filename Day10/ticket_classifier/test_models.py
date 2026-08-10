import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from .models import SupportTicket, ClassificationResult, LLMLogEntry


class TestModels(unittest.TestCase):

    def test_support_ticket_model(self):
        ticket = SupportTicket(ticket_id=1, text="Payment failed on checkout")
        self.assertEqual(ticket.ticket_id, 1)
        self.assertEqual(ticket.text, "Payment failed on checkout")

    def test_classification_result_model(self):
        res = ClassificationResult(category="Billing", confidence=0.95, provider="MockPrimary", ticket_id=1)
        self.assertEqual(res.category, "Billing")
        self.assertEqual(res.confidence, 0.95)
        self.assertEqual(res.provider, "MockPrimary")

    def test_llm_log_entry_model(self):
        log = LLMLogEntry(
            trace_id="abc-123",
            timestamp="2026-07-27T12:00:00Z",
            provider="MockPrimary",
            model_name="llama-3.3-70b",
            prompt="Help",
            completion="Technical",
            prompt_tokens=5,
            completion_tokens=2,
            total_tokens=7,
            estimated_cost=0.0001,
            latency_ms=50.0,
            retry_count=0,
            finish_reason="stop",
            success=True
        )
        self.assertEqual(log.trace_id, "abc-123")
        self.assertTrue(log.success)


if __name__ == "__main__":
    unittest.main()
