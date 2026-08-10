"""
Custom exception classes for ticket classifier.
"""


class ClassifierError(Exception):
    """Base exception for ticket classifier errors."""
    pass


class TransportError(ClassifierError):
    """Raised when network, HTTP, or API transport communication fails."""
    pass


class ModelOutputError(ClassifierError):
    """Raised when LLM model response format or content is invalid."""
    pass


class BusinessRuleViolation(ClassifierError):
    """Raised when input data or ticket parameters violate business logic rules."""
    pass
