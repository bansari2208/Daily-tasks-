"""
Day 14 - Tool Executor Pipeline & Error Recovery Module.

Orchestrates tool routing, Pydantic argument validation, confirmation gate enforcement,
simulated failure handling, and recovery paths.
"""

import time
import logging
from typing import Dict, Any, Optional, Callable, Tuple
from schemas import ToolExecutionResult, StructuredError
from tools import TOOL_REGISTRY
from validator import validate_tool_arguments
from confirmation_gate import ConfirmationGate
from aws_client import AWSBedrockClient

logger = logging.getLogger(__name__)


class ToolExecutor:
    """Production tool execution pipeline managing validation, security gates, and failure recovery."""

    def __init__(
        self,
        aws_client: Optional[AWSBedrockClient] = None,
        confirm_callback: Optional[Callable[[str, Dict[str, Any]], bool]] = None
    ) -> None:
        """
        Initialize ToolExecutor instance.

        Args:
            aws_client: AWS Bedrock or fallback router client instance.
            confirm_callback: Optional custom callback function for confirmation gate testing.
        """
        self.aws_client = aws_client or AWSBedrockClient()
        self.confirm_callback = confirm_callback

    def execute_prompt(
        self,
        prompt: str,
        auto_confirm: Optional[bool] = None
    ) -> ToolExecutionResult:
        """
        Executes a user prompt through the complete tool execution pipeline.

        Pipeline Stages:
        1. Tool Routing & Argument Extraction
        2. Pydantic Argument Validation (rejection of bad arguments)
        3. Confirmation Gate (for state-changing tools)
        4. Tool Execution & Failure Recovery

        Args:
            prompt: User natural language prompt string.
            auto_confirm: Optional boolean override for confirmation gate.

        Returns:
            Structured ToolExecutionResult object.
        """
        start_time = time.perf_counter()

        # Stage 1: Tool Selection & Argument Extraction
        tool_name, raw_args = self.aws_client.select_tool(prompt)

        # Handle "No Tool" Decision
        if tool_name is None:
            exec_time = (time.perf_counter() - start_time) * 1000
            return ToolExecutionResult(
                tool_name=None,
                status="NO_TOOL",
                arguments={},
                raw_arguments={},
                result={"response": "No tool call required. Conversational answer provided."},
                execution_time_ms=round(exec_time, 2),
                confirmation_status="N/A",
            )

        # Stage 2: Pydantic Argument Validation & Rejection
        is_valid, validated_args, val_error_msg = validate_tool_arguments(tool_name, raw_args)

        if not is_valid:
            exec_time = (time.perf_counter() - start_time) * 1000
            err_payload = StructuredError(
                status="FAILED",
                error_type="ValidationError",
                message=val_error_msg or "Argument validation failed.",
                recoverable=True,
                suggestion="Provide valid arguments (e.g. positive integer ticket_id, non-empty reason).",
            )
            return ToolExecutionResult(
                tool_name=tool_name,
                status="VALIDATION_ERROR",
                arguments=validated_args,
                raw_arguments=raw_args,
                error=err_payload,
                execution_time_ms=round(exec_time, 2),
                confirmation_status="N/A",
            )

        # Stage 3: Confirmation Gate Enforcement
        is_approved, gate_status = ConfirmationGate.process_gate(
            tool_name=tool_name,
            args=validated_args,
            prompt=prompt,
            auto_confirm=auto_confirm,
            confirm_callback=self.confirm_callback,
        )

        if not is_approved:
            exec_time = (time.perf_counter() - start_time) * 1000
            return ToolExecutionResult(
                tool_name=tool_name,
                status="CANCELLED",
                arguments=validated_args,
                raw_arguments=raw_args,
                result={"message": f"Execution of state-changing tool '{tool_name}' was cancelled by user."},
                execution_time_ms=round(exec_time, 2),
                confirmation_status="REJECTED",
            )

        # Stage 4: Tool Execution & Simulated Failure Recovery Path
        tool_fn = TOOL_REGISTRY[tool_name]["function"]
        try:
            tool_output = tool_fn(**validated_args)
            exec_time = (time.perf_counter() - start_time) * 1000
            return ToolExecutionResult(
                tool_name=tool_name,
                status="SUCCESS",
                arguments=validated_args,
                raw_arguments=raw_args,
                result=tool_output,
                execution_time_ms=round(exec_time, 2),
                confirmation_status=gate_status,
            )

        except RuntimeError as r_err:
            # Simulated tool failure (e.g., ticket ID 999 database timeout)
            exec_time = (time.perf_counter() - start_time) * 1000
            err_payload = StructuredError(
                status="FAILED",
                error_type="DatabaseError",
                message=str(r_err),
                recoverable=True,
                suggestion="Simulated database failure detected. Recovery path initiated.",
            )

            # Executing Recovery Path
            recovery_result = self._execute_recovery_path(tool_name, validated_args, str(r_err))

            return ToolExecutionResult(
                tool_name=tool_name,
                status="FAILED",
                arguments=validated_args,
                raw_arguments=raw_args,
                result=recovery_result,
                error=err_payload,
                execution_time_ms=round(exec_time, 2),
                confirmation_status=gate_status,
            )

    def _execute_recovery_path(self, tool_name: str, args: Dict[str, Any], error_msg: str) -> Dict[str, Any]:
        """
        Recovery Path executed when a tool operation fails at runtime.

        Provides graceful degraded fallback response and retry advice.
        """
        return {
            "recovery_status": "RECOVERY_EXECUTED",
            "fallback_action": f"Logged failed tool call '{tool_name}' with args {args} to fallback audit queue.",
            "user_guidance": "The system encountered a database transaction error. A retry request has been queued automatically.",
            "original_error": error_msg,
        }
