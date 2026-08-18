"""
Day 19 - Unit Test Suite for Systematic Prompt Optimisation.

Verifies:
1. Evaluation dataset contains exactly 20 items.
2. Dataset contains 4 balanced categories (5 items per category).
3. Evaluator scoring accuracy logic.
4. Baseline prompt exists and is explicit.
5. All 4 core prompt variants (Baseline, V2, V3, V4) are defined.
6. Failure analysis correctly categorizes error items.
7. Failure analysis accurately detects the largest failure class.
8. Failure reduction verification enforces Y < X.
9. Mean statistics function calculation.
10. Median statistics function calculation.
11. Sample StDev statistics function calculation (N-1 degrees of freedom).
12. Range statistics function calculation.
13. Master runner output JSON schema format.
"""

import os
import sys
import unittest

# Ensure Day19 directory is in sys.path
DAY19_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if DAY19_DIR not in sys.path:
    sys.path.insert(0, DAY19_DIR)

from evaluation_set import get_evaluation_set
from prompts import PROMPT_VARIANTS, build_optimized_prompt
from evaluator import parse_category_from_output, evaluate_prediction, evaluate_batch
from failure_analysis import analyze_failures, verify_failure_reduction
from statistics import calc_mean, calc_median, calc_stdev, calc_range, compute_run_statistics


class TestDay19SystematicPromptOptimization(unittest.TestCase):

    def setUp(self):
        self.dataset = get_evaluation_set()

    def test_01_dataset_size_20_items(self):
        """Test 1: Verify dataset contains exactly 20 items."""
        self.assertEqual(len(self.dataset), 20, f"Expected 20 evaluation items, got {len(self.dataset)}")

    def test_02_balanced_category_coverage(self):
        """Test 2: Verify 4 categories with 5 balanced items per category."""
        categories = [item["expected_category"] for item in self.dataset]
        counts = {
            "Billing": categories.count("Billing"),
            "Technical": categories.count("Technical"),
            "Account": categories.count("Account"),
            "General": categories.count("General")
        }

        self.assertEqual(counts["Billing"], 5, "Billing category must have 5 items.")
        self.assertEqual(counts["Technical"], 5, "Technical category must have 5 items.")
        self.assertEqual(counts["Account"], 5, "Account category must have 5 items.")
        self.assertEqual(counts["General"], 5, "General category must have 5 items.")

    def test_03_accuracy_evaluator(self):
        """Test 3: Verify evaluator accurately computes accuracy percentage."""
        sample_dataset = self.dataset[:4]
        # 3 correct, 1 incorrect
        sample_outputs = [
            '{"category": "Billing"}',
            '{"category": "Billing"}',
            '{"category": "Billing"}',
            '{"category": "General"}'
        ]
        res = evaluate_batch(sample_dataset, sample_outputs)
        self.assertEqual(res["total_items"], 4)
        self.assertEqual(res["correct_count"], 3)
        self.assertEqual(res["accuracy_percentage"], 75.0)

    def test_04_baseline_prompt_explicit(self):
        """Test 4: Verify Baseline prompt exists and is explicitly defined."""
        self.assertIn("Baseline", PROMPT_VARIANTS)
        self.assertIn("Classify the following customer support ticket", PROMPT_VARIANTS["Baseline"])

    def test_05_all_four_variants_defined(self):
        """Test 5: Verify Baseline, V2, V3, V4 are all defined in PROMPT_VARIANTS."""
        for var in ["Baseline", "V2", "V3", "V4"]:
            self.assertIn(var, PROMPT_VARIANTS, f"Prompt variant '{var}' missing from PROMPT_VARIANTS.")

    def test_06_failure_analysis_categorization(self):
        """Test 6: Verify failure analysis groups incorrect items into expected categories."""
        sample_results = [
            {"expected_category": "Billing", "is_correct": False},
            {"expected_category": "Billing", "is_correct": False},
            {"expected_category": "Technical", "is_correct": False},
            {"expected_category": "Account", "is_correct": True}
        ]
        fa = analyze_failures(sample_results)
        self.assertEqual(fa["total_failures"], 3)
        self.assertEqual(fa["category_failure_counts"]["Billing"], 2)
        self.assertEqual(fa["category_failure_counts"]["Technical"], 1)

    def test_07_largest_failure_class_detection(self):
        """Test 7: Verify failure analysis detects the category with maximum error count."""
        sample_results = [
            {"expected_category": "Technical", "is_correct": False},
            {"expected_category": "Technical", "is_correct": False},
            {"expected_category": "Technical", "is_correct": False},
            {"expected_category": "Billing", "is_correct": False}
        ]
        fa = analyze_failures(sample_results)
        self.assertEqual(fa["largest_failure_class"], "Technical")
        self.assertEqual(fa["largest_failure_count"], 3)

    def test_08_failure_reduction_verification(self):
        """Test 8: Verify failure reduction logic returns True if Y < X, False otherwise."""
        is_reduced, diff = verify_failure_reduction(5, 2)
        self.assertTrue(is_reduced)
        self.assertEqual(diff, 3)

        is_not_reduced, diff2 = verify_failure_reduction(2, 3)
        self.assertFalse(is_not_reduced)

    def test_09_calc_mean(self):
        """Test 9: Verify arithmetic mean calculation."""
        scores = [85.0, 90.0, 95.0]
        self.assertEqual(calc_mean(scores), 90.0)

    def test_10_calc_median(self):
        """Test 10: Verify median calculation."""
        scores = [85.0, 90.0, 95.0]
        self.assertEqual(calc_median(scores), 90.0)

    def test_11_calc_sample_stdev(self):
        """Test 11: Verify sample standard deviation calculation (N-1)."""
        scores = [85.0, 90.0, 95.0]
        # stdev of [85, 90, 95] is 5.0
        self.assertEqual(calc_stdev(scores), 5.0)

    def test_12_calc_range(self):
        """Test 12: Verify range calculation (Max - Min spread)."""
        scores = [85.0, 90.0, 95.0]
        self.assertEqual(calc_range(scores), 10.0)

    def test_13_results_json_schema(self):
        """Test 13: Verify compute_run_statistics outputs complete stats payload."""
        scores = [90.0, 95.0, 95.0]
        stats = compute_run_statistics(scores)
        self.assertIn("mean", stats)
        self.assertIn("median", stats)
        self.assertIn("sample_stdev", stats)
        self.assertIn("range", stats)
        self.assertEqual(stats["mean"], 93.33)


if __name__ == "__main__":
    unittest.main()
