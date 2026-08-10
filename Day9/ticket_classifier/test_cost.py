import unittest
from .cost import (
    calculate_request_cost,
    compress_prompt,
    compare_language_inflation,
    get_model_recommendation,
)


class TestCostModule(unittest.TestCase):

    def test_calculate_request_cost(self):
        cost_nano = calculate_request_cost("GPT-4.1 Nano", prompt_tokens=100, completion_tokens=50)
        self.assertGreater(cost_nano, 0.0)

        cost_gpt4 = calculate_request_cost("GPT-4.1", prompt_tokens=100, completion_tokens=50)
        self.assertGreater(cost_gpt4, cost_nano)

    def test_compress_prompt(self):
        res = compress_prompt("Please carefully read and analyze this ticket")
        self.assertIn("original_tokens", res)
        self.assertIn("compressed_tokens", res)
        self.assertIn("tokens_saved", res)
        self.assertGreaterEqual(res["tokens_saved"], 0)

    def test_compare_language_inflation(self):
        res = compare_language_inflation()
        self.assertIn("english_tokens", res)
        self.assertIn("non_english_tokens", res)
        self.assertGreater(res["non_english_tokens"], res["english_tokens"])

    def test_get_model_recommendation(self):
        rec_small = get_model_recommendation(150)
        self.assertEqual(rec_small["recommended_model"], "GPT-4.1 Nano")

        rec_medium = get_model_recommendation(500)
        self.assertEqual(rec_medium["recommended_model"], "GPT-4.1 Mini")

        rec_large = get_model_recommendation(1500)
        self.assertEqual(rec_large["recommended_model"], "GPT-4.1")


if __name__ == "__main__":
    unittest.main()
