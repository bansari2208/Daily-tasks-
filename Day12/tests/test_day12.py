"""
Pytest unit test suite for Day 12 complete production build requirements.
"""

import json
import os
import sys
import pytest

DAY12_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Day12"))
DATASET_PATH = os.path.join(DAY12_DIR, "labelled_dataset.json")
EDGE_CASES_PATH = os.path.join(DAY12_DIR, "edge_cases.md")
PROMPTS_DIR = os.path.join(DAY12_DIR, "prompts")
OUTPUT_DIR = os.path.join(DAY12_DIR, "output")

from Day12.run_fewshot_benchmark import run_benchmark
from Day12.ordering_experiment import run_ordering_experiment
from Day12.cost_analysis import run_cost_analysis
from Day12.dynamic_selector import run_dynamic_selector_demo
from Day12.revision_example import generate_reproducible_split


def test_dataset_structure_and_edge_cases():
    """Verifies that labelled_dataset.json contains 30 items with required keys."""
    assert os.path.exists(DATASET_PATH), "labelled_dataset.json missing"
    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert len(data) == 30, "Dataset must contain exactly 30 records"

    for record in data:
        assert "ticket_id" in record
        assert "ticket_text" in record
        assert "expected_category" in record
        assert "expected_priority" in record
        assert "expected_reasoning_level" in record
        assert "expected_output" in record

    # Verify edge cases 25-30 exist
    edge_ids = {r["ticket_id"] for r in data if r["ticket_id"] >= 25}
    assert len(edge_ids) == 6, "Must contain 6 edge case records"
    assert os.path.exists(EDGE_CASES_PATH), "edge_cases.md missing"


def test_prompt_templates_exist():
    """Verifies all required Jinja2 prompt templates exist."""
    templates = ["zero_shot.jinja2", "three_shot.jinja2", "eight_shot.jinja2", "bad_examples.jinja2"]
    for t in templates:
        p = os.path.join(PROMPTS_DIR, t)
        assert os.path.exists(p), f"Template {t} missing"


def test_fewshot_benchmark_execution():
    """Verifies few-shot benchmark execution and output generation."""
    results = run_benchmark()
    assert "Zero-shot" in results
    assert "Three-shot" in results
    assert "Eight-shot" in results
    assert os.path.exists(os.path.join(DAY12_DIR, "accuracy_cost_report.md"))
    assert os.path.exists(os.path.join(DAY12_DIR, "results.json"))
    assert os.path.exists(os.path.join(OUTPUT_DIR, "benchmark_output.txt"))


def test_ordering_experiment_execution():
    """Verifies ordering experiment execution and text output."""
    res = run_ordering_experiment()
    assert "spread" in res
    assert res["spread"] > 0
    assert os.path.exists(os.path.join(OUTPUT_DIR, "ordering_output.txt"))


def test_cost_analysis_execution():
    """Verifies cost analysis CSV and curve generation."""
    best = run_cost_analysis()
    assert best["shots"] == 3
    assert os.path.exists(os.path.join(DAY12_DIR, "accuracy_vs_cost.csv"))
    assert os.path.exists(os.path.join(DAY12_DIR, "accuracy_vs_cost_curve.md"))
    assert os.path.exists(os.path.join(OUTPUT_DIR, "cost_analysis_output.txt"))


def test_dynamic_selector_execution():
    """Verifies dynamic selector demo and winner declaration."""
    comp = run_dynamic_selector_demo()
    assert "Dynamic Few-shot" in comp
    assert os.path.exists(os.path.join(OUTPUT_DIR, "dynamic_selector_output.txt"))


def test_bad_examples_analysis_file():
    """Verifies bad examples markdown analysis exists."""
    p = os.path.join(DAY12_DIR, "bad_examples_analysis.md")
    assert os.path.exists(p), "bad_examples_analysis.md missing"


def test_revision_example_reproducibility():
    """Verifies reproducible split producing identical IDs with seed 42."""
    ids = list(range(1, 31))
    t1, v1, s1 = generate_reproducible_split(ids, seed=42)
    t2, v2, s2 = generate_reproducible_split(ids, seed=42)
    assert t1 == t2
    assert v1 == v2
    assert s1 == s2
