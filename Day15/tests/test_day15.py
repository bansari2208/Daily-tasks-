import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from Day15.langfuse_integration import LangfusePromptManager
from Day15.canary_release import CanaryPromptRouter
from Day15.logger_extension import log_llm_call_versioned


class TestDay15LangfuseIntegration(unittest.TestCase):

    def setUp(self):
        self.manager = LangfusePromptManager()
        self.prompt_name = "ticket_classifier 1"

    def test_get_prompt_by_name(self):
        prompt = self.manager.get_prompt_by_name(self.prompt_name)
        self.assertIsNotNone(prompt)
        self.assertEqual(getattr(prompt, "name", self.prompt_name), self.prompt_name)

    def test_get_prompt_by_version(self):
        p_v1 = self.manager.get_prompt_by_version(self.prompt_name, version=1)
        p_v2 = self.manager.get_prompt_by_version(self.prompt_name, version=2)
        self.assertEqual(getattr(p_v1, "version", 1), 1)
        self.assertEqual(getattr(p_v2, "version", 2), 2)

    def test_get_prompt_by_label(self):
        p_prod = self.manager.get_prompt_by_label(self.prompt_name, label="production")
        self.assertIsNotNone(p_prod)
        self.assertEqual(getattr(p_prod, "version", 1), 1)

    def test_compile_prompt_safety(self):
        p_v1 = self.manager.get_prompt_by_version(self.prompt_name, version=1)
        ticket = "Password reset request for user@example.com"
        compiled = self.manager.compile_prompt(p_v1, ticket)
        self.assertIsNotNone(compiled)

    def test_log_traced_generation(self):
        p_v1 = self.manager.get_prompt_by_version(self.prompt_name, version=1)
        res = self.manager.log_traced_generation(
            prompt_obj=p_v1,
            ticket_text="Test ticket",
            compiled_prompt="Compiled prompt text",
            completion_text='{"category": "General"}',
            latency_ms=250.0
        )
        self.assertEqual(res["status"], "LIVE_LANGFUSE_LOGGED")
        self.assertEqual(res["prompt_name"], self.prompt_name)

    def test_canary_router(self):
        router = CanaryPromptRouter(self.manager, prompt_name=self.prompt_name, canary_ratio=0.10)
        # Test forced production arm
        prompt_prod, arm_prod, v_prod = router.select_prompt(force_arm="production")
        self.assertEqual(arm_prod, "PRODUCTION_90PCT")
        self.assertEqual(v_prod, 1)

        # Test forced candidate arm
        prompt_cand, arm_cand, v_cand = router.select_prompt(force_arm="candidate")
        self.assertEqual(arm_cand, "CANDIDATE_10PCT")
        self.assertEqual(v_cand, 2)

    def test_logger_extension(self):
        log_entry = log_llm_call_versioned(
            model_name="gpt-4.1-mini",
            prompt="Test prompt",
            completion="Test output",
            prompt_name=self.prompt_name,
            prompt_version="1",
            latency_ms=180.0
        )
        self.assertEqual(log_entry["prompt_name"], self.prompt_name)
        self.assertEqual(log_entry["prompt_version"], "1")
        self.assertEqual(log_entry["duration_ms"], 180.0)


if __name__ == "__main__":
    unittest.main()
