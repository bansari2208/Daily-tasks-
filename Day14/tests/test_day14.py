"""
Day 14 - Unit Test Suite.

Tests tool execution pipeline, Pydantic argument validation rejection,
confirmation gate behavior, failure recovery path, and evaluation metrics.
"""

import sys
import os
import unittest

# Ensure Day14 folder is in sys.path

from tool_executor import ToolExecutor
from evaluation import run_evaluation_benchmark


class TestDay14ToolUse(unittest.TestCase):

    def setUp(self):
        self.executor = ToolExecutor()

    def test_read_only_tool_execution(self):
        """Test read-only tool (get_ticket_status) executes immediately without confirmation."""
        res = self.executor.execute_prompt("What is the current status of ticket 101?")
        self.assertEqual(res.tool_name, "get_ticket_status")
        self.assertEqual(res.status, "SUCCESS")
        self.assertEqual(res.confirmation_status, "EXECUTED_IMMEDIATELY")
        self.assertIsNotNone(res.result)
        self.assertEqual(res.result.get("ticket_id"), 101)

    def test_state_changing_tool_confirmed(self):
        """Test state-changing tool (close_ticket) executes when confirmed at Confirmation Gate."""
        res = self.executor.execute_prompt(
            "Please close ticket 101 with reason: Issue resolved by technician.",
            auto_confirm=True
        )
        self.assertEqual(res.tool_name, "close_ticket")
        self.assertEqual(res.status, "SUCCESS")
        self.assertEqual(res.confirmation_status, "CONFIRMED")
        self.assertEqual(res.result.get("status"), "CLOSED")

    def test_state_changing_tool_rejected(self):
        """Test state-changing tool (close_ticket) is cancelled when rejected at Confirmation Gate."""
        res = self.executor.execute_prompt(
            "Please close ticket 102 with reason: Fixed.",
            auto_confirm=False
        )
        self.assertEqual(res.tool_name, "close_ticket")
        self.assertEqual(res.status, "CANCELLED")
        self.assertEqual(res.confirmation_status, "REJECTED")

    def test_invalid_argument_rejected(self):
        """Test Pydantic argument validation rejects invalid arguments (negative ticket ID)."""
        res = self.executor.execute_prompt("Check status of ticket -5.")
        self.assertEqual(res.tool_name, "get_ticket_status")
        self.assertEqual(res.status, "VALIDATION_ERROR")
        self.assertIsNotNone(res.error)
        self.assertEqual(res.error.error_type, "ValidationError")

    def test_simulated_tool_failure_recovery(self):
        """Test simulated database failure on ticket 999 triggers StructuredError and recovery path."""
        res = self.executor.execute_prompt("What is the status of ticket 999?")
        self.assertEqual(res.tool_name, "get_ticket_status")
        self.assertEqual(res.status, "FAILED")
        self.assertIsNotNone(res.error)
        self.assertEqual(res.error.error_type, "DatabaseError")
        self.assertIsNotNone(res.result)
        self.assertEqual(res.result.get("recovery_status"), "RECOVERY_EXECUTED")

    def test_no_tool_decision(self):
        """Test general conversational queries result in NO_TOOL status."""
        res = self.executor.execute_prompt("Hello! What are your business operating hours?")
        self.assertIsNone(res.tool_name)
        self.assertEqual(res.status, "NO_TOOL")

    def test_evaluation_benchmark_accuracy(self):
        """Test 20-prompt evaluation benchmark metrics."""
        eval_stats = run_evaluation_benchmark(auto_confirm=True)
        self.assertEqual(eval_stats["total_prompts"], 20)
        self.assertGreaterEqual(eval_stats["tool_selection_accuracy_pct"], 90.0)
        self.assertGreaterEqual(eval_stats["no_tool_accuracy_pct"], 90.0)


if __name__ == "__main__":
    unittest.main()
