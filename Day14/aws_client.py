"""
Day 14 - AWS Bedrock Client & Tool Router Integration Module.

Integrates AWS Bedrock Runtime (boto3) for tool calling and provides a safe fallback
rule-based tool router for offline testing environments.
"""

import os
import re
import json
import logging
from typing import Tuple, Dict, Any, Optional

logger = logging.getLogger(__name__)


class AWSBedrockClient:
    """Client for AWS Bedrock Converse API tool selection with fallback offline router."""

    def __init__(self, model_id: str = "us.amazon.nova-lite-v1:0", region_name: str = "us-east-1"):
        self.model_id = model_id
        self.region_name = region_name
        self.bedrock_available = False
        self.client = None

        # Check if boto3 and AWS credentials are available
        try:
            import boto3
            if os.environ.get("AWS_ACCESS_KEY_ID") or os.environ.get("AWS_PROFILE"):
                self.client = boto3.client("bedrock-runtime", region_name=self.region_name)
                self.bedrock_available = True
        except Exception:
            self.bedrock_available = False

    def select_tool(self, prompt: str) -> Tuple[Optional[str], Dict[str, Any]]:
        """
        Processes prompt and extracts intended tool call and arguments.

        Args:
            prompt: Natural language user query.

        Returns:
            Tuple of (tool_name_or_None, raw_arguments_dict).
        """
        if self.bedrock_available and self.client:
            try:
                return self._call_bedrock_converse(prompt)
            except Exception as e:
                logger.warning(f"Bedrock invocation failed ({e}). Falling back to rule-based parser.")

        return self._fallback_rule_parser(prompt)

    def _call_bedrock_converse(self, prompt: str) -> Tuple[Optional[str], Dict[str, Any]]:
        """Calls AWS Bedrock Converse API with tool configuration."""
        from tools import TOOL_REGISTRY

        tools_config = []
        for name, entry in TOOL_REGISTRY.items():
            tools_config.append({
                "toolSpec": {
                    "name": name,
                    "description": entry["description"],
                    "inputSchema": {
                        "json": entry["json_schema"]
                    }
                }
            })

        response = self.client.converse(
            modelId=self.model_id,
            messages=[{"role": "user", "content": [{"text": prompt}]}],
            toolConfig={"tools": tools_config}
        )

        output_message = response.get("output", {}).get("message", {})
        content = output_message.get("content", [])

        for block in content:
            if "toolUse" in block:
                tool_use = block["toolUse"]
                tool_name = tool_use.get("name")
                raw_args = tool_use.get("input", {})
                return tool_name, raw_args

        return None, {}

    def _fallback_rule_parser(self, prompt: str) -> Tuple[Optional[str], Dict[str, Any]]:
        """Deterministic rule-based parser for offline evaluation and testing."""
        prompt_lower = prompt.lower()

        # 1. Close Ticket intent
        if any(kw in prompt_lower for kw in ["close", "resolve", "solved", "solve", "mark solved", "close ticket"]):
            match = re.search(r"ticket\s*#?\s*(-?\d+)", prompt_lower)
            ticket_id = int(match.group(1)) if match else 101

            reason_match = re.search(r"(?:because|reason:?|with reason|due to)\s+(.+)$", prompt, re.IGNORECASE)
            if reason_match:
                reason = reason_match.group(1).strip()
            elif "resolved" in prompt_lower or "fixed" in prompt_lower:
                reason = "Issue resolved by support representative."
            else:
                reason = "Closing ticket as requested."

            return "close_ticket", {"ticket_id": ticket_id, "reason": reason}

        # 2. Get Ticket Status intent
        elif any(kw in prompt_lower for kw in ["status", "check", "view", "details", "info", "get status"]):
            match = re.search(r"ticket\s*#?\s*(-?\d+)", prompt_lower)
            if match:
                return "get_ticket_status", {"ticket_id": int(match.group(1))}
            # Check for solitary number like "status of 102"
            num_match = re.search(r"\b(-?\d+)\b", prompt_lower)
            if num_match:
                return "get_ticket_status", {"ticket_id": int(num_match.group(1))}

        # 3. Update Priority intent
        elif "priority" in prompt_lower or "escalate" in prompt_lower:
            match = re.search(r"ticket\s*#?\s*(-?\d+)", prompt_lower)
            ticket_id = int(match.group(1)) if match else 101

            prio = "HIGH" if "high" in prompt_lower or "escalate" in prompt_lower else "MEDIUM"
            if "low" in prompt_lower:
                prio = "LOW"

            return "update_ticket_priority", {"ticket_id": ticket_id, "priority": prio}

        # 4. No Tool Decision (General query, conversational, greeting, or out-of-scope)
        return None, {}
