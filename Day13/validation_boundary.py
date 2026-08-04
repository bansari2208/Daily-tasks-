"""
Day 13 Application Validation Boundary.
Enforces strict schema validation at the edge before data enters business logic.
"""

import json
from typing import Dict, Any, Type, TypeVar, Tuple
from pydantic import BaseModel, ValidationError

T = TypeVar("T", bound=BaseModel)


class ValidationBoundaryError(Exception):
    """Raised when validation fails at the application boundary."""
    def __init__(self, message: str, raw_input: Any, errors: Any = None):
        super().__init__(message)
        self.raw_input = raw_input
        self.errors = errors


class ValidationBoundary:
    """Application boundary validator."""

    @staticmethod
    def validate_raw_input(raw_input: str | Dict[str, Any], model_cls: Type[T]) -> T:
        """Parses and validates raw input string or dictionary into a Pydantic model.
        
        Validation happens strictly at this boundary.
        """
        if isinstance(raw_input, str):
            try:
                data = json.loads(raw_input)
            except Exception as parse_err:
                raise ValidationBoundaryError(
                    f"Malformed JSON at boundary: {str(parse_err)}",
                    raw_input=raw_input
                )
        elif isinstance(raw_input, dict):
            data = raw_input
        else:
            raise ValidationBoundaryError(
                f"Invalid input type '{type(raw_input).__name__}'. Expected str or dict.",
                raw_input=raw_input
            )

        try:
            validated_object = model_cls.model_validate(data)
            return validated_object
        except ValidationError as val_err:
            raise ValidationBoundaryError(
                f"Boundary Schema Validation Failed: {val_err.error_count()} errors found.",
                raw_input=raw_input,
                errors=val_err.errors()
            )

    @staticmethod
    def safe_validate(raw_input: str | Dict[str, Any], model_cls: Type[T]) -> Tuple[bool, T | None, str | None]:
        """Safe boundary check returning (is_valid, validated_obj, error_message)."""
        try:
            obj = ValidationBoundary.validate_raw_input(raw_input, model_cls)
            return True, obj, None
        except ValidationBoundaryError as err:
            return False, None, str(err)
