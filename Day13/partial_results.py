"""
Day 13 Partial Result Recovery.
Extracts valid fields and isolates invalid fields when whole-model validation fails.
"""

import json
from typing import Dict, Any, Type, Tuple
from pydantic import BaseModel, ValidationError
from .response_models import TicketClassificationResponse, CategoryEnum, PriorityEnum


class PartialResultExtractor:
    """Salvages valid fields from partially malformed or failing LLM responses."""

    @staticmethod
    def extract_partial_results(
        raw_input: str | Dict[str, Any],
        model_cls: Type[BaseModel] = TicketClassificationResponse
    ) -> Dict[str, Any]:
        """Extracts valid fields and field_errors dictionary without discarding valid data.
        
        Returns:
            {
                "valid_fields": Dict[str, Any],
                "field_errors": Dict[str, str],
                "has_partial_data": bool
            }
        """
        if isinstance(raw_input, str):
            try:
                data = json.loads(raw_input)
            except Exception as parse_err:
                return {
                    "valid_fields": {},
                    "field_errors": {"json_body": f"Malformed JSON: {str(parse_err)}"},
                    "has_partial_data": False
                }
        elif isinstance(raw_input, dict):
            data = raw_input
        else:
            return {
                "valid_fields": {},
                "field_errors": {"input_type": f"Unsupported input type '{type(raw_input).__name__}'"},
                "has_partial_data": False
            }

        valid_fields = {}
        field_errors = {}

        # Validate field by field against schema fields
        for field_name, field_info in model_cls.model_fields.items():
            if field_name not in data:
                if field_info.is_required():
                    field_errors[field_name] = "Missing required field"
                continue

            val = data[field_name]
            
            # Construct dynamic single-field validation schema
            try:
                temp_model = type(f"Temp_{field_name}", (BaseModel,), {
                    "__annotations__": {field_name: field_info.annotation},
                    field_name: field_info
                })
                temp_model.model_validate({field_name: val})
                valid_fields[field_name] = val
            except ValidationError as val_err:
                err_msg = val_err.errors()[0]["msg"] if val_err.errors() else "Validation failed"
                field_errors[field_name] = f"Invalid field value '{val}': {err_msg}"

        return {
            "valid_fields": valid_fields,
            "field_errors": field_errors,
            "has_partial_data": len(valid_fields) > 0
        }
