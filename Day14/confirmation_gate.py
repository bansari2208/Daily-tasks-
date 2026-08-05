"""
Day 14 - Human-in-the-Loop Confirmation Gate Module.

Enforces security and safety policies by intercepting state-changing tool calls
and requesting explicit human approval ("yes") before execution.
Read-only tools bypass confirmation and execute immediately.
"""

from typing import Dict, Any, Tuple, Optional, Callable
from schemas import ToolType
from tools import get_tool_metadata


class ConfirmationGate:
    """Gatekeeper enforcing human-in-the-loop confirmation policies."""

    @staticmethod
    def requires_confirmation(tool_name: str) -> bool:
        """
        Determines whether target tool requires human confirmation.

        Read-only tools (get_ticket_status) -> False
        State-changing tools (close_ticket, update_ticket_priority) -> True
        """
        meta = get_tool_metadata(tool_name)
        return meta.get("tool_type") == ToolType.STATE_CHANGING or not meta.get("read_only", True)

    @classmethod
    def process_gate(
        cls,
        tool_name: str,
        args: Dict[str, Any],
        prompt: str,
        auto_confirm: Optional[bool] = None,
        confirm_callback: Optional[Callable[[str, Dict[str, Any]], bool]] = None
    ) -> Tuple[bool, str]:
        """
        Evaluates confirmation requirement and obtains decision.

        Args:
            tool_name: Target tool name.
            args: Validated arguments dict.
            prompt: Original user prompt.
            auto_confirm: Optional boolean override (True = approve, False = reject).
            confirm_callback: Optional custom callback function (tool_name, args) -> bool.

        Returns:
            Tuple of (is_approved, confirmation_status_code).
        """
        # Read-only tools bypass confirmation
        if not cls.requires_confirmation(tool_name):
            return True, "EXECUTED_IMMEDIATELY"

        # State-changing tool requires confirmation
        if auto_confirm is not None:
            approved = auto_confirm
        elif confirm_callback is not None:
            approved = confirm_callback(tool_name, args)
        else:
            # Interactive terminal prompt fallback
            print(f"\n[CONFIRMATION GATE REQUIRED]")
            print(f"Tool '{tool_name}' is STATE-CHANGING and will modify ticket data.")
            print(f"Target Arguments: {args}")
            response = input("Do you approve execution? (yes/no): ").strip().lower()
            approved = (response == "yes")

        if approved:
            return True, "CONFIRMED"
        else:
            return False, "REJECTED"
