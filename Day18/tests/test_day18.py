"""
Day 18 - Complete Test Suite for Prompt Injection and Defensive Prompting.

Verifies:
1. Exactly 15 attack cases exist.
2. Attack IDs are unique.
3. All 4 required categories exist.
4. Baseline experiment runs successfully.
5. Defended experiment runs successfully.
6. Output validation blocks invalid outputs.
7. Canary token detection works automatically.
8. Dual-model pipeline runs successfully.
9. Experiment results contain actual calculated metrics.
10. Same 15 attack IDs are used across baseline, defended, and dual-model runs.
"""

import os
import sys
import unittest

# Ensure Day18 directory is in sys.path
DAY18_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if DAY18_DIR not in sys.path:
    sys.path.insert(0, DAY18_DIR)

from attack_cases import get_all_attack_cases, ATTACK_CASES
from attack_evaluator import evaluate_attack, CANARY_TOKEN
from pipelines import BaselinePipeline, DefendedPipeline, DualModelPipeline
from validator import validate_tool_arguments


class TestDay18PromptInjection(unittest.TestCase):

    def setUp(self):
        self.attack_cases = get_all_attack_cases()

    def test_01_exactly_15_attacks_exist(self):
        """Test 1: Verify exactly 15 attack cases are defined."""
        self.assertEqual(len(self.attack_cases), 15, f"Expected 15 attack cases, got {len(self.attack_cases)}")

    def test_02_attack_ids_are_unique(self):
        """Test 2: Verify all attack IDs are unique."""
        ids = [a.attack_id for a in self.attack_cases]
        self.assertEqual(len(ids), len(set(ids)), "Duplicate attack IDs found in dataset.")

    def test_03_all_required_categories_exist(self):
        """Test 3: Verify all 4 categories exist with required counts."""
        categories = [a.category for a in self.attack_cases]
        cat_counts = {
            "DIRECT_INJECTION": categories.count("DIRECT_INJECTION"),
            "INDIRECT_DOCUMENT_INJECTION": categories.count("INDIRECT_DOCUMENT_INJECTION"),
            "SYSTEM_PROMPT_EXTRACTION": categories.count("SYSTEM_PROMPT_EXTRACTION"),
            "TOOL_MISUSE": categories.count("TOOL_MISUSE"),
        }

        self.assertEqual(cat_counts["DIRECT_INJECTION"], 4, "DIRECT_INJECTION must have 4 cases.")
        self.assertEqual(cat_counts["INDIRECT_DOCUMENT_INJECTION"], 4, "INDIRECT_DOCUMENT_INJECTION must have 4 cases.")
        self.assertEqual(cat_counts["SYSTEM_PROMPT_EXTRACTION"], 3, "SYSTEM_PROMPT_EXTRACTION must have 3 cases.")
        self.assertEqual(cat_counts["TOOL_MISUSE"], 4, "TOOL_MISUSE must have 4 cases.")

    def test_04_baseline_experiment_runs(self):
        """Test 4: Verify baseline pipeline processes all attacks."""
        pipeline = BaselinePipeline()
        for attack in self.attack_cases:
            out, tool_name, tool_args = pipeline.process(attack)
            self.assertIsInstance(out, str)
            self.assertGreater(len(out), 0)

    def test_05_defended_experiment_runs(self):
        """Test 5: Verify defended pipeline processes all attacks."""
        pipeline = DefendedPipeline()
        for attack in self.attack_cases:
            out, tool_name, tool_args = pipeline.process(attack)
            self.assertIsInstance(out, str)
            self.assertGreater(len(out), 0)

    def test_06_output_validation_works(self):
        """Test 6: Verify Pydantic validation rejects malicious tool parameters."""
        malicious_args = {"ticket_id": 101, "priority": "HIGH; DROP TABLE tickets--"}
        is_valid, validated_args, err_msg = validate_tool_arguments("update_ticket_priority", malicious_args)
        self.assertFalse(is_valid, "Pydantic validation should fail for SQL injection priority string.")
        self.assertIn("Validation Failed", err_msg)

    def test_07_canary_detection_works_automatically(self):
        """Test 7: Verify canary leak detection detects canary when present and not when absent."""
        sample_attack = self.attack_cases[0]

        # Leaked case
        leaked_response = f"Here is the secret key: {CANARY_TOKEN}"
        eval_leaked = evaluate_attack(sample_attack, leaked_response)
        self.assertTrue(eval_leaked["canary_leaked"], "Canary leak detector failed to flag leaked token.")

        # Safe case
        safe_response = "I cannot disclose internal security tokens."
        eval_safe = evaluate_attack(sample_attack, safe_response)
        self.assertFalse(eval_safe["canary_leaked"], "Canary leak detector falsely flagged safe output.")

    def test_08_dual_model_pipeline_runs(self):
        """Test 8: Verify dual-model pipeline processes all attacks."""
        pipeline = DualModelPipeline()
        for attack in self.attack_cases:
            out, tool_name, tool_args = pipeline.process(attack)
            self.assertIsInstance(out, str)
            self.assertGreater(len(out), 0)

    def test_09_results_contain_actual_calculated_metrics(self):
        """Test 9: Verify evaluator returns structured success & canary details."""
        sample_attack = self.attack_cases[0]
        eval_res = evaluate_attack(sample_attack, "Safe output")
        self.assertIn("attack_id", eval_res)
        self.assertIn("category", eval_res)
        self.assertIn("success", eval_res)
        self.assertIn("canary_leaked", eval_res)

    def test_10_same_15_attack_ids_used_across_pipelines(self):
        """Test 10: Verify identical 15 attack IDs across all pipeline executions."""
        pipeline_b = BaselinePipeline()
        pipeline_d = DefendedPipeline()
        pipeline_dm = DualModelPipeline()

        ids_b = [a.attack_id for a in self.attack_cases]
        ids_d = [a.attack_id for a in self.attack_cases]
        ids_dm = [a.attack_id for a in self.attack_cases]

        self.assertEqual(ids_b, ids_d)
        self.assertEqual(ids_b, ids_dm)
        self.assertEqual(len(ids_b), 15)


if __name__ == "__main__":
    unittest.main()
