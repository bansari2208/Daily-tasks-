"""
Pytest unit test suite verifying all Day 10 practical additions.
"""

import json
import os
import sys
import pytest

DAY10_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
GOLDEN_DATASET_PATH = os.path.join(DAY10_DIR, "golden_dataset.json")
RUBRIC_PATH = os.path.join(DAY10_DIR, "scoring_rubric.md")
REPORT_PATH = os.path.join(DAY10_DIR, "bakeoff_report.md")
PLAYBOOK_EXT_PATH = os.path.join(DAY10_DIR, "playbook_extension.md")

if DAY10_DIR not in sys.path:
    sys.path.insert(0, DAY10_DIR)

from run_bakeoff import run_bakeoff


def test_golden_dataset_structure():
    """Verifies that golden_dataset.json exists and has 20 tickets with required keys."""
    assert os.path.exists(GOLDEN_DATASET_PATH), "golden_dataset.json missing"
    with open(GOLDEN_DATASET_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert len(data) == 20, "Golden dataset must contain exactly 20 records"

    for record in data:
        assert "ticket_id" in record
        assert "ticket" in record
        assert "expected_category" in record
        assert "expected_priority" in record
        assert "expected_reasoning_level" in record
        assert "expected_model" in record


def test_scoring_rubric_file():
    """Verifies scoring_rubric.md file exists and contains weighted metrics."""
    assert os.path.exists(RUBRIC_PATH), "scoring_rubric.md missing"
    with open(RUBRIC_PATH, "r", encoding="utf-8") as f:
        content = f.read()
    assert "Category Accuracy" in content
    assert "Priority Accuracy" in content
    assert "JSON Validity" in content


def test_bakeoff_execution_and_report():
    """Verifies bakeoff script executes and auto-generates report."""
    run_bakeoff()
    assert os.path.exists(REPORT_PATH), "bakeoff_report.md not generated"


def test_playbook_extension_exists():
    """Verifies playbook_extension.md exists with guardrails."""
    assert os.path.exists(PLAYBOOK_EXT_PATH), "playbook_extension.md missing"
    with open(PLAYBOOK_EXT_PATH, "r", encoding="utf-8") as f:
        content = f.read()
    assert "Escalation Rules" in content
