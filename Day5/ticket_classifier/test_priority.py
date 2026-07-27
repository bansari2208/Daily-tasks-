import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ticket_classifier.priority import predict_priority
from ticket_classifier.models import PriorityResult


class TestPriority(unittest.TestCase):

    def test_high_priority_keywords(self):
        res = predict_priority("Payment failed on checkout page")
        self.assertEqual(res.priority, "HIGH")
        self.assertGreaterEqual(res.score, 0.80)

    def test_high_priority_billing_category(self):
        res = predict_priority("Update my card info", category="Billing")
        self.assertEqual(res.priority, "HIGH")

    def test_medium_priority(self):
        res = predict_priority("I cannot reset my password")
        self.assertEqual(res.priority, "MEDIUM")

    def test_low_priority(self):
        res = predict_priority("Dark mode feature request")
        self.assertEqual(res.priority, "LOW")

    def test_empty_ticket_text_raises_error(self):
        with self.assertRaises(ValueError):
            predict_priority("")


if __name__ == "__main__":
    unittest.main()
