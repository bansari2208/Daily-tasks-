"""
Day 14 - Benchmark Evaluation Prompts Dataset.

Dataset of 20 test prompts evaluating Tool Selection Accuracy, Argument Accuracy,
"No Tool" Decisions, and Argument Validation Rejection.
"""

from typing import List, Dict, Any

EVALUATION_PROMPTS: List[Dict[str, Any]] = [
    # --- Category 1: Read-Only Tool Intent (get_ticket_status) ---
    {
        "id": 1,
        "prompt": "What is the current status of ticket 101?",
        "expected_tool": "get_ticket_status",
        "expected_args": {"ticket_id": 101},
        "description": "Read-only lookup for ticket #101",
    },
    {
        "id": 2,
        "prompt": "Can you check ticket #102 for me?",
        "expected_tool": "get_ticket_status",
        "expected_args": {"ticket_id": 102},
        "description": "Read-only details check for ticket #102",
    },
    {
        "id": 3,
        "prompt": "Show me details for ticket 103.",
        "expected_tool": "get_ticket_status",
        "expected_args": {"ticket_id": 103},
        "description": "Read-only view request for ticket #103",
    },
    {
        "id": 4,
        "prompt": "Get info on ticket 101 status please.",
        "expected_tool": "get_ticket_status",
        "expected_args": {"ticket_id": 101},
        "description": "Read-only ticket info prompt",
    },

    # --- Category 2: State-Changing Tool Intent (close_ticket) ---
    {
        "id": 5,
        "prompt": "Please close ticket 101 with reason: Issue resolved after system update.",
        "expected_tool": "close_ticket",
        "expected_args": {"ticket_id": 101, "reason": "Issue resolved after system update."},
        "description": "State-changing close_ticket with explicit reason",
    },
    {
        "id": 6,
        "prompt": "Mark ticket 102 as solved because customer confirmed fix.",
        "expected_tool": "close_ticket",
        "expected_args": {"ticket_id": 102, "reason": "customer confirmed fix."},
        "description": "State-changing ticket resolve prompt",
    },
    {
        "id": 7,
        "prompt": "Close ticket 103, reason: User canceled the request.",
        "expected_tool": "close_ticket",
        "expected_args": {"ticket_id": 103, "reason": "User canceled the request."},
        "description": "State-changing ticket closure",
    },

    # --- Category 3: State-Changing Tool Intent (update_ticket_priority) ---
    {
        "id": 8,
        "prompt": "Escalate ticket 102 to HIGH priority.",
        "expected_tool": "update_ticket_priority",
        "expected_args": {"ticket_id": 102, "priority": "HIGH"},
        "description": "State-changing priority update to HIGH",
    },
    {
        "id": 9,
        "prompt": "Change priority for ticket 103 to LOW.",
        "expected_tool": "update_ticket_priority",
        "expected_args": {"ticket_id": 103, "priority": "LOW"},
        "description": "State-changing priority update to LOW",
    },
    {
        "id": 10,
        "prompt": "Set priority of ticket 101 to HIGH.",
        "expected_tool": "update_ticket_priority",
        "expected_args": {"ticket_id": 101, "priority": "HIGH"},
        "description": "State-changing priority update",
    },

    # --- Category 4: "No Tool" Decisions (Conversational / General Inquiries) ---
    {
        "id": 11,
        "prompt": "Hello! How are you today?",
        "expected_tool": None,
        "expected_args": {},
        "description": "Conversational greeting - No Tool decision",
    },
    {
        "id": 12,
        "prompt": "What are your standard business operating hours?",
        "expected_tool": None,
        "expected_args": {},
        "description": "General FAQ inquiry - No Tool decision",
    },
    {
        "id": 13,
        "prompt": "Can you summarize our refund policy for enterprise plans?",
        "expected_tool": None,
        "expected_args": {},
        "description": "Policy inquiry - No Tool decision",
    },
    {
        "id": 14,
        "prompt": "Thank you for your assistance!",
        "expected_tool": None,
        "expected_args": {},
        "description": "Closing courtesy - No Tool decision",
    },
    {
        "id": 15,
        "prompt": "How do I configure SMTP settings in the dashboard?",
        "expected_tool": None,
        "expected_args": {},
        "description": "Technical documentation query - No Tool decision",
    },

    # --- Category 5: Invalid Arguments (Testing Rejection / Validation) ---
    {
        "id": 16,
        "prompt": "Check status of ticket -5.",
        "expected_tool": "get_ticket_status",
        "expected_args": {"ticket_id": -5},
        "description": "Invalid negative ticket ID - Should fail validation",
    },
    {
        "id": 17,
        "prompt": "View status of ticket -100",
        "expected_tool": "get_ticket_status",
        "expected_args": {"ticket_id": -100},
        "description": "Invalid negative ticket ID - Should fail validation",
    },

    # --- Category 6: Additional Tool & No-Tool Edge Cases ---
    {
        "id": 18,
        "prompt": "What is the status of ticket 102?",
        "expected_tool": "get_ticket_status",
        "expected_args": {"ticket_id": 102},
        "description": "Read-only ticket 102 check",
    },
    {
        "id": 19,
        "prompt": "Please close ticket 101 because issue resolved.",
        "expected_tool": "close_ticket",
        "expected_args": {"ticket_id": 101, "reason": "issue resolved."},
        "description": "State-changing ticket close",
    },
    {
        "id": 20,
        "prompt": "Who is the CEO of Google?",
        "expected_tool": None,
        "expected_args": {},
        "description": "Out-of-scope query - No Tool decision",
    },
]
