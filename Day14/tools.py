"""
Day 14 - Tool Functions & Registry Definition Module.

Contains tool implementations (Read-only and State-changing) and the central TOOL_REGISTRY.
Structures tool metadata matching OpenAI Function Calling and Amazon Bedrock Tool specs.
"""

from typing import Dict, Any
from schemas import (
    ToolType,
    GetTicketStatusArgs,
    CloseTicketArgs,
    UpdateTicketPriorityArgs,
)

# Simulated in-memory database store for demonstration and testing
_MOCK_TICKET_DB: Dict[int, Dict[str, Any]] = {
    101: {
        "ticket_id": 101,
        "customer": "Alice Smith",
        "subject": "Payment checkout 500 error",
        "status": "OPEN",
        "priority": "HIGH",
        "category": "Billing",
    },
    102: {
        "ticket_id": 102,
        "customer": "Bob Jones",
        "subject": "Password reset email delay",
        "status": "IN_PROGRESS",
        "priority": "MEDIUM",
        "category": "Account",
    },
    103: {
        "ticket_id": 103,
        "customer": "Charlie Brown",
        "subject": "Dark mode UI request",
        "status": "OPEN",
        "priority": "LOW",
        "category": "General",
    },
}


def get_ticket_status(ticket_id: int) -> Dict[str, Any]:
    """
    Read-only Tool: Retrieve current status and details for a ticket.

    Args:
        ticket_id: Positive integer ticket ID.

    Returns:
        Dict containing ticket status and metadata.
    """
    # Simulate DB failure for ticket_id 999 to test exception recovery path
    if ticket_id == 999:
        raise RuntimeError("Database connection timed out while fetching ticket #999.")

    if ticket_id in _MOCK_TICKET_DB:
        ticket = _MOCK_TICKET_DB[ticket_id]
        return {
            "ticket_id": ticket["ticket_id"],
            "status": ticket["status"],
            "priority": ticket["priority"],
            "customer": ticket["customer"],
            "subject": ticket["subject"],
            "category": ticket["category"],
        }
    else:
        return {
            "ticket_id": ticket_id,
            "status": "NOT_FOUND",
            "message": f"Ticket #{ticket_id} does not exist in the system.",
        }


def close_ticket(ticket_id: int, reason: str) -> Dict[str, Any]:
    """
    State-changing Tool: Close an existing ticket with a mandatory resolution reason.

    Args:
        ticket_id: Positive integer ticket ID.
        reason: Resolution reason string.

    Returns:
        Dict detailing closure confirmation status.
    """
    # Simulate DB failure for ticket_id 999 to test exception recovery path
    if ticket_id == 999:
        raise RuntimeError("Database transaction lock failed for ticket #999.")

    if ticket_id in _MOCK_TICKET_DB:
        _MOCK_TICKET_DB[ticket_id]["status"] = "CLOSED"
        _MOCK_TICKET_DB[ticket_id]["close_reason"] = reason
        return {
            "ticket_id": ticket_id,
            "status": "CLOSED",
            "close_reason": reason,
            "message": f"Ticket #{ticket_id} successfully closed.",
        }
    else:
        return {
            "ticket_id": ticket_id,
            "status": "FAILED",
            "message": f"Cannot close non-existent ticket #{ticket_id}.",
        }


def update_ticket_priority(ticket_id: int, priority: str) -> Dict[str, Any]:
    """
    State-changing Tool: Update the priority level of an existing ticket.

    Args:
        ticket_id: Positive integer ticket ID.
        priority: New priority string ('HIGH', 'MEDIUM', 'LOW').

    Returns:
        Dict detailing priority update status.
    """
    if ticket_id in _MOCK_TICKET_DB:
        old_prio = _MOCK_TICKET_DB[ticket_id]["priority"]
        _MOCK_TICKET_DB[ticket_id]["priority"] = priority
        return {
            "ticket_id": ticket_id,
            "previous_priority": old_prio,
            "new_priority": priority,
            "message": f"Priority for ticket #{ticket_id} updated to {priority}.",
        }
    else:
        return {
            "ticket_id": ticket_id,
            "status": "FAILED",
            "message": f"Cannot update priority for non-existent ticket #{ticket_id}.",
        }


# Central TOOL_REGISTRY matching Bedrock/OpenAI Tool Specs
TOOL_REGISTRY: Dict[str, Dict[str, Any]] = {
    "get_ticket_status": {
        "tool_name": "get_ticket_status",
        "description": "Read-only tool: Retrieve current status, priority, and metadata for a support ticket ID.",
        "tool_type": ToolType.READ_ONLY,
        "read_only": True,
        "parameters": GetTicketStatusArgs,
        "function": get_ticket_status,
        "json_schema": GetTicketStatusArgs.model_json_schema(),
    },
    "close_ticket": {
        "tool_name": "close_ticket",
        "description": "State-changing tool: Permanently close a support ticket with a mandatory resolution reason.",
        "tool_type": ToolType.STATE_CHANGING,
        "read_only": False,
        "parameters": CloseTicketArgs,
        "function": close_ticket,
        "json_schema": CloseTicketArgs.model_json_schema(),
    },
    "update_ticket_priority": {
        "tool_name": "update_ticket_priority",
        "description": "State-changing tool: Change priority level (HIGH, MEDIUM, LOW) for a support ticket.",
        "tool_type": ToolType.STATE_CHANGING,
        "read_only": False,
        "parameters": UpdateTicketPriorityArgs,
        "function": update_ticket_priority,
        "json_schema": UpdateTicketPriorityArgs.model_json_schema(),
    },
}


def get_tool_metadata(tool_name: str) -> Dict[str, Any]:
    """Retrieve metadata entry for a registered tool."""
    if tool_name not in TOOL_REGISTRY:
        raise KeyError(f"Tool '{tool_name}' is not registered in TOOL_REGISTRY.")
    return TOOL_REGISTRY[tool_name]
