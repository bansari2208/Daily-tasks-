import json
import os
from typing import Dict, Any, List, Type
from pydantic import BaseModel, Field
from jinja2 import Template

PROMPTS_DIR = os.path.join("archive", "Day11", "prompts")

def load_prompt(prompt_name: str = "production_prompt.jinja2") -> str:
    """
    Prompt Loader Helper (Item 5).
    Reads Jinja2 prompt template from disk.
    """
    prompt_path = os.path.join(PROMPTS_DIR, prompt_name)
    if not os.path.exists(prompt_path):
        return "[SYSTEM]\nIdentity: Support Ticket Classifier\n[USER]\n{{ ticket_text }}"
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read()

def load_langfuse_prompt(prompt_name: str = "ticket_classifier 1", label: str = "production", ticket_text: str = "") -> str:
    """
    Day 15 Integration: Fetches production prompt from Langfuse Prompt Management Registry
    and compiles using template variable {{ticket}}.
    """
    try:
        from Day15.langfuse_integration import LangfusePromptManager
        manager = LangfusePromptManager()
        prompt_obj = manager.get_prompt_by_label(prompt_name, label=label)
        return manager.compile_prompt(prompt_obj, ticket_text)
    except Exception:
        # Fallback to local prompt rendering if Langfuse is unreachable
        return render_production_prompt(ticket_text)


class TicketClassificationSchema(BaseModel):
    """
    Day 11 Schema-First Design Single Source of Truth (Task 42).
    """
    category: str = Field(default="General", description="Primary ticket category: Billing, Technical, Security, General")
    priority: str = Field(default="MEDIUM", description="Priority level: LOW, MEDIUM, HIGH, URGENT")
    urgency_score: float = Field(default=0.5, ge=0.0, le=1.0, description="Urgency score between 0.0 and 1.0")
    confidence: float = Field(default=0.9, ge=0.0, le=1.0, description="Confidence rating between 0.0 and 1.0")
    reason: str = Field(default="Routine query", description="Rationale for classification decision")

def generate_schema_specification(model_class: Type[BaseModel] = TicketClassificationSchema) -> str:
    """
    Schema-First Design Helper (Task 42).
    Dynamically derives the JSON output specification from a Pydantic model.
    """
    schema = model_class.model_json_schema()
    properties = schema.get("properties", {})
    required = schema.get("required", list(properties.keys()))
    
    spec_dict = {
        "type": "object",
        "required_fields": required,
        "properties": {
            k: {
                "type": v.get("type", "string"),
                "description": v.get("description", k)
            }
            for k, v in properties.items()
        }
    }
    return json.dumps(spec_dict, indent=2)

def render_production_prompt(ticket_text: str) -> str:
    """
    Renders production prompt template with dynamic schema specification and runtime ticket payload.
    """
    raw_template = load_prompt("production_prompt.jinja2")
    schema_spec = generate_schema_specification(TicketClassificationSchema)
    template = Template(raw_template)
    return template.render(
        output_specification=schema_spec,
        ticket_text=ticket_text
    )

def build_role_messages(
    ticket_text: str,
    positive_instruction: bool = True
) -> List[Dict[str, str]]:
    """
    OpenAI Role Separation Engine (Task 41).
    Separates System, Developer, Assistant, and User messages cleanly.
    """
    instruction_rule = (
        "Extract ticket details solely from the provided customer message."
        if positive_instruction
        else "Do not invent details, hallucinate information, or guess missing fields."
    )

    schema_spec = generate_schema_specification(TicketClassificationSchema)

    return [
        {
            "role": "system",
            "content": (
                "Identity: You are an enterprise-grade AI Customer Support Ticket Classifier.\n"
                "Metadata: Version v1.0.0 | Author: Staff AI Engineer | Created: 2026-08-02\n"
                "Permanent Rules: Analyze support tickets accurately and follow formatting strictly."
            )
        },
        {
            "role": "developer",
            "content": (
                f"Instruction: Classify the customer support ticket into category, priority, and urgency.\n"
                f"Rule: {instruction_rule}\n"
                f"Output Specification:\n{schema_spec}\n"
                "Constraint: Respond strictly with a single valid JSON object."
            )
        },
        {
            "role": "assistant",
            "content": json.dumps({
                "category": "Billing",
                "priority": "HIGH",
                "urgency_score": 0.90,
                "confidence": 0.95,
                "reason": "Ticket contains urgent outage or payment failure keywords."
            })
        },
        {
            "role": "user",
            "content": f"Ticket Text: {ticket_text}"
        }
    ]
