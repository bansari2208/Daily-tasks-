"""
Pytest unit test suite for Day 13 complete production build requirements.
"""

import os
import sys
import json
import pytest

DAY13_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Day13"))

from Day13.response_models import TicketClassificationResponse, FlexibleTicketResponse, FlexibleCategoryEnum
from Day13.validation_boundary import ValidationBoundary, ValidationBoundaryError
from Day13.self_repair import BoundedSelfRepairLoop, MaxRetriesExceededError, run_retry_budget_analysis
from Day13.failure_taxonomy import FailureTaxonomyAnalyzer, run_taxonomy_analysis
from Day13.unknown_schema_demo import run_unknown_comparison
from Day13.partial_results import PartialResultExtractor
from Day13.constrained_vs_repair import run_constrained_vs_repair_experiment
from Day13.revision_example import (
    TicketClassifierError,
    ValidationErrorBoundaryError,
    MissingRequiredFieldError,
    WrongDatatypeError,
    InvalidEnumError,
    safe_ticket_extraction_pipeline,
    map_error_to_exception
)
from Day13.evaluation_report import generate_day13_evaluation_report


def test_response_validation():
    """Verifies response model validation at boundary."""
    raw_valid = '{"ticket_id": 201, "category": "Billing", "priority": "HIGH", "confidence": 0.9, "reasoning": "Double charge"}'
    is_val, obj, err = ValidationBoundary.safe_validate(raw_valid, TicketClassificationResponse)
    assert is_val is True
    assert obj is not None
    assert obj.ticket_id == 201
    assert obj.category.value == "Billing"

    raw_invalid = '{"ticket_id": 202, "category": "Technical"}'
    is_val2, obj2, err2 = ValidationBoundary.safe_validate(raw_invalid, TicketClassificationResponse)
    assert is_val2 is False
    assert obj2 is None
    assert err2 is not None


def test_retry_limit():
    """Verifies bounded self-repair loop raises MaxRetriesExceededError when budget exhausted."""
    loop = BoundedSelfRepairLoop(max_retries=2)
    def mock_always_fail(p: str) -> str:
        return '{"ticket_id": 203, "category": "BadCategory"}'

    with pytest.raises(MaxRetriesExceededError) as exc_info:
        loop.execute_with_repair(mock_always_fail, "Classify ticket", ticket_id=203)

    assert exc_info.value.total_retries == 2


def test_retry_budget_analysis():
    """Verifies retry budget analysis output format for budgets 1..4."""
    results = run_retry_budget_analysis()
    assert 1 in results
    assert 2 in results
    assert 3 in results
    assert 4 in results
    assert results[3]["validity_pct"] >= 90.0


def test_taxonomy_counts():
    """Verifies 50 failure samples are properly categorized and reports generated."""
    analyzer = FailureTaxonomyAnalyzer()
    res = analyzer.analyze()
    total_counts = sum(v["count"] for v in res.values())
    assert total_counts == 50

    tax_md, sum_md, csv_path = run_taxonomy_analysis()
    assert os.path.exists(tax_md)
    assert os.path.exists(sum_md)
    assert os.path.exists(csv_path)


def test_unknown_path():
    """Verifies UNKNOWN fallback reduces hallucinations."""
    res = run_unknown_comparison()
    assert res["reduction_pct"] > 50.0
    assert os.path.exists(os.path.join(DAY13_DIR, "reports", "unknown_before.json"))
    assert os.path.exists(os.path.join(DAY13_DIR, "reports", "unknown_after.json"))
    assert os.path.exists(os.path.join(DAY13_DIR, "reports", "unknown_comparison.md"))


def test_partial_results():
    """Verifies partial result extractor salvages valid fields."""
    raw = '{"ticket_id": 301, "category": "InvalidCat", "confidence": 0.95, "reasoning": "Valid reasoning"}'
    extracted = PartialResultExtractor.extract_partial_results(raw)
    assert "ticket_id" in extracted["valid_fields"]
    assert extracted["valid_fields"]["ticket_id"] == 301
    assert "confidence" in extracted["valid_fields"]
    assert "category" in extracted["field_errors"]
    assert extracted["has_partial_data"] is True


def test_constrained_decoding_comparison():
    """Verifies constrained decoding vs self-repair benchmark metrics."""
    res = run_constrained_vs_repair_experiment()
    assert "repair" in res
    assert "constrained" in res
    assert res["constrained"]["validity_pct"] >= 95.0
    assert os.path.exists(os.path.join(DAY13_DIR, "reports", "constrained_vs_repair.md"))


def test_exception_hierarchy():
    """Verifies custom exception hierarchy and try/except/else/finally pipeline."""
    exc = map_error_to_exception("Missing required field", "Missing field")
    assert isinstance(exc, MissingRequiredFieldError)
    assert isinstance(exc, ValidationErrorBoundaryError)
    assert isinstance(exc, TicketClassifierError)

    valid_raw = '{"ticket_id": 401, "category": "Account", "priority": "LOW", "confidence": 0.95, "reasoning": "Password reset request"}'
    pipe_res = safe_ticket_extraction_pipeline(valid_raw)
    assert pipe_res["status"] == "SUCCESS"
    assert pipe_res["cleanup_done"] is True


def test_evaluation_report_generation():
    """Verifies day13_evaluation_report.md generation."""
    report_path = generate_day13_evaluation_report()
    assert os.path.exists(report_path)
