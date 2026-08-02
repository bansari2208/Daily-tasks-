import json
import os
import pytest
from ticket_classifier.prompt_engine import (
    TicketClassificationSchema,
    generate_schema_specification,
    build_role_messages,
    load_prompt
)

def test_load_prompt():
    """Verify prompt loader reads template correctly."""
    prompt = load_prompt("production_prompt.jinja2")
    assert "[SYSTEM]" in prompt
    assert "[DEVELOPER]" in prompt
    assert "[USER]" in prompt

def test_schema_generation():
    """Verify schema generation derives from Pydantic model dynamically."""
    spec_json = generate_schema_specification(TicketClassificationSchema)
    spec = json.loads(spec_json)
    
    assert spec["type"] == "object"
    assert "category" in spec["properties"]
    assert "priority" in spec["properties"]
    assert "urgency_score" in spec["properties"]
    assert "confidence" in spec["properties"]

def test_role_separation():
    """Verify instructions are moved into correct OpenAI roles."""
    messages = build_role_messages("Card payment failed twice on checkout page.")
    
    roles = [m["role"] for m in messages]
    assert roles == ["system", "developer", "assistant", "user"]
    
    assert "Identity" in messages[0]["content"]
    assert "Output Specification" in messages[1]["content"]
    assert "Billing" in messages[2]["content"]
    assert "Card payment failed" in messages[3]["content"]

def test_benchmark_inputs_exist():
    """Verify 20-input benchmark dataset file exists and has 20 inputs."""
    path = os.path.join("archive", "Day11", "benchmark_inputs.json")
    assert os.path.exists(path)
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert len(data) == 20

def test_pydantic_validation():
    """Verify TicketClassificationSchema validation."""
    data = {
        "category": "Billing",
        "priority": "HIGH",
        "urgency_score": 0.9,
        "confidence": 0.95,
        "reason": "Payment issue"
    }
    model = TicketClassificationSchema(**data)
    assert model.category == "Billing"
    assert model.priority == "HIGH"
    assert model.urgency_score == 0.9
