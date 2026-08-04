"""
Day 13 Revision Exercise & Custom Exception Hierarchy.
Demonstrates try/except/else/finally control flow and taxonomy-aligned exception hierarchy.
"""

from typing import Dict, Any, Tuple, Optional
from response_models import TicketClassificationResponse
from validation_boundary import ValidationBoundary, ValidationBoundaryError


# ----------------------------------------------------
# Custom Exception Hierarchy matching Failure Taxonomy
# ----------------------------------------------------

class TicketClassifierError(Exception):
    """Base exception for all ticket classifier errors."""
    pass


class ValidationErrorBoundaryError(TicketClassifierError):
    """Raised when validation fails at boundary."""
    def __init__(self, message: str, raw_input: Any = None):
        super().__init__(message)
        self.raw_input = raw_input


class MissingRequiredFieldError(ValidationErrorBoundaryError): pass
class WrongDatatypeError(ValidationErrorBoundaryError): pass
class InvalidEnumError(ValidationErrorBoundaryError): pass
class ExtraFieldError(ValidationErrorBoundaryError): pass
class MalformedJSONError(ValidationErrorBoundaryError): pass
class HallucinatedValueError(ValidationErrorBoundaryError): pass
class UnknownCategoryError(ValidationErrorBoundaryError): pass


class MaxRetriesExceededError(TicketClassifierError):
    """Raised when self-repair retries exceed maximum limit."""
    def __init__(self, message: str, retry_count: int):
        super().__init__(message)
        self.retry_count = retry_count


def map_error_to_exception(error_category: str, msg: str, raw_input: Any = None) -> ValidationErrorBoundaryError:
    """Maps taxonomy error string to specific custom exception class."""
    mapping = {
        "Missing required field": MissingRequiredFieldError,
        "Wrong datatype": WrongDatatypeError,
        "Invalid enum": InvalidEnumError,
        "Extra field": ExtraFieldError,
        "Malformed JSON": MalformedJSONError,
        "Hallucinated value": HallucinatedValueError,
        "Unknown category": UnknownCategoryError,
    }
    exc_cls = mapping.get(error_category, ValidationErrorBoundaryError)
    return exc_cls(msg, raw_input=raw_input)


def safe_ticket_extraction_pipeline(raw_input: str) -> Dict[str, Any]:
    """Demonstrates complete try / except / else / finally control flow."""
    pipeline_state = {"status": "INITIALIZED", "cleaned_data": None, "cleanup_done": False}

    try:
        pipeline_state["status"] = "VALIDATING"
        is_valid, obj, err_msg = ValidationBoundary.safe_validate(raw_input, TicketClassificationResponse)

        if not is_valid:
            raise ValidationErrorBoundaryError(f"Validation failed: {err_msg}", raw_input=raw_input)

    except ValidationErrorBoundaryError as val_err:
        pipeline_state["status"] = "ERROR_HANDLED"
        pipeline_state["error"] = str(val_err)
        return pipeline_state

    except Exception as general_err:
        pipeline_state["status"] = "UNEXPECTED_ERROR"
        pipeline_state["error"] = f"Unexpected error: {str(general_err)}"
        return pipeline_state

    else:
        pipeline_state["status"] = "SUCCESS"
        pipeline_state["cleaned_data"] = obj.model_dump() if obj else None

    finally:
        pipeline_state["cleanup_done"] = True

    return pipeline_state
