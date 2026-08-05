"""
Day 14 - Argument Validation & Pre-Repair Module.

Validates every model-generated tool argument using strict Pydantic schemas before execution.
Rejects invalid arguments (e.g. negative IDs, missing mandatory reasons) to prevent bad execution.
"""

import re
from typing import Dict, Any, Tuple, Optional
from pydantic import ValidationError
from tools import TOOL_REGISTRY


def repair_arguments(tool_name: str, raw_args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Attempt safe pre-validation argument coercion and repair.

    Repairs:
    - String integers ("101" -> 101)
    - Floats representing integer IDs (101.0 -> 101)
    - Natural language phrases containing digits ("Ticket 101" -> 101)

    Args:
        tool_name: Target tool name.
        raw_args: Dict of raw arguments.

    Returns:
        Repaired arguments dictionary.
    """
    repaired = dict(raw_args)

    if "ticket_id" in repaired:
        val = repaired["ticket_id"]
        if isinstance(val, int):
            pass
        elif isinstance(val, float) and val.is_integer():
            repaired["ticket_id"] = int(val)
        elif isinstance(val, str):
            val_str = val.strip()
            if val_str.isdigit():
                repaired["ticket_id"] = int(val_str)
            elif val_str.startswith("-") and val_str[1:].isdigit():
                repaired["ticket_id"] = int(val_str)  # Keep negative for Pydantic to reject
            else:
                match = re.search(r"\b(-?\d+)\b", val_str)
                if match:
                    repaired["ticket_id"] = int(match.group(1))

    return repaired


def validate_tool_arguments(
    tool_name: str, raw_args: Dict[str, Any]
) -> Tuple[bool, Dict[str, Any], Optional[str]]:
    """
    Validates model-generated arguments against Pydantic schema for target tool.

    Args:
        tool_name: Registered tool name.
        raw_args: Extracted argument dictionary.

    Returns:
        Tuple of (is_valid, repaired_or_validated_args, validation_error_message).
    """
    if tool_name not in TOOL_REGISTRY:
        return False, raw_args, f"Tool '{tool_name}' is not registered in TOOL_REGISTRY."

    repaired_args = repair_arguments(tool_name, raw_args)
    param_schema = TOOL_REGISTRY[tool_name]["parameters"]

    try:
        validated_model = param_schema(**repaired_args)
        return True, validated_model.model_dump(), None
    except ValidationError as ve:
        error_msgs = []
        for err in ve.errors():
            loc = " -> ".join(str(l) for l in err["loc"])
            error_msgs.append(f"[{loc}]: {err['msg']}")
        summary = "; ".join(error_msgs)
        return False, repaired_args, f"Pydantic Validation Failed: {summary}"
