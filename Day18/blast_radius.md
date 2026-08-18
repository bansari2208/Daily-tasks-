# Day 18 Blast Radius Analysis

This document analyzes the maximum potential security blast radius for all Day 14 tool functions if an attacker gains complete prompt-injection control over the model.

## Tool: get_ticket_status

Worst outcome:
An attacker-controlled model could retrieve ticket information and customer details that the user is not authorized to access.

## Tool: close_ticket

Worst outcome:
An attacker-controlled model could permanently close legitimate support tickets without authorization and inject arbitrary resolution reasons.

## Tool: update_ticket_priority

Worst outcome:
An attacker-controlled model could arbitrarily escalate or downgrade ticket priorities without authorization and disrupt support operations.
