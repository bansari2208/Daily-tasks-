import random
from typing import Dict, Any, List, Tuple
from Day15.langfuse_integration import LangfusePromptManager


class CanaryPromptRouter:
    """
    Day 15 Canary Release Traffic Router.
    
    Splits traffic between Production Prompt (90%, 'production' label -> Version 1)
    and Candidate Prompt (10%, Version 2) while logging traces into Langfuse linked
    to the respective prompt version.
    """

    def __init__(
        self,
        manager: LangfusePromptManager,
        prompt_name: str = "ticket_classifier 1",
        production_label: str = "production",
        candidate_version: int = 2,
        canary_ratio: float = 0.10
    ):
        self.manager = manager
        self.prompt_name = prompt_name
        self.production_prompt = manager.get_prompt_by_label(prompt_name, label=production_label)
        self.candidate_prompt = manager.get_prompt_by_version(prompt_name, version=candidate_version)
        self.canary_ratio = canary_ratio  # 0.10 -> 10% candidate, 90% production

    def select_prompt(self, force_arm: str = None) -> Tuple[Any, str, int]:
        """
        Selects prompt object based on canary probability ratio.
        Returns tuple of (prompt_object, arm_name, version_number).
        """
        if force_arm == "candidate" or (force_arm is None and random.random() < self.canary_ratio):
            return self.candidate_prompt, "CANDIDATE_10PCT", getattr(self.candidate_prompt, "version", 2)
        return self.production_prompt, "PRODUCTION_90PCT", getattr(self.production_prompt, "version", 1)

    def process_ticket(
        self,
        ticket_text: str,
        force_arm: str = None
    ) -> Dict[str, Any]:
        """
        Processes ticket through selected canary arm and records Langfuse trace.
        """
        prompt_obj, arm_name, version = self.select_prompt(force_arm=force_arm)
        compiled_prompt = self.manager.compile_prompt(prompt_obj, ticket_text)

        # Simulated response tailored to version
        if version == 1:
            completion = '{"category": "Billing", "priority": "HIGH", "reason": "Urgent charge query"}'
        else:
            completion = '{"category": "Billing", "priority": "HIGH", "urgency_score": 0.88, "confidence": 0.96, "reason": "Urgent payment processing issue"}'

        trace_res = self.manager.log_traced_generation(
            prompt_obj=prompt_obj,  # Pass fetched prompt object directly to link generation!
            ticket_text=ticket_text,
            compiled_prompt=compiled_prompt,
            completion_text=completion,
            model_name="gpt-4.1-mini",
            prompt_tokens=110 if version == 1 else 165,
            completion_tokens=30 if version == 1 else 45,
            latency_ms=280.0 if version == 1 else 320.0,
            metadata={"canary_arm": arm_name}
        )

        return {
            "ticket": ticket_text,
            "arm": arm_name,
            "prompt_name": self.prompt_name,
            "prompt_version": version,
            "compiled_prompt": compiled_prompt,
            "completion": completion,
            "trace_telemetry": trace_res
        }

    def process_batch(self, tickets: List[str]) -> Dict[str, Any]:
        """
        Processes batch of tickets and calculates canary distribution metrics.
        """
        results = []
        prod_count = 0
        cand_count = 0

        for ticket in tickets:
            res = self.process_ticket(ticket)
            results.append(res)
            if res["arm"] == "PRODUCTION_90PCT":
                prod_count += 1
            else:
                cand_count += 1

        total = len(tickets)
        return {
            "total_processed": total,
            "production_count": prod_count,
            "candidate_count": cand_count,
            "production_pct": round((prod_count / total) * 100, 1) if total > 0 else 0,
            "candidate_pct": round((cand_count / total) * 100, 1) if total > 0 else 0,
            "executions": results
        }
