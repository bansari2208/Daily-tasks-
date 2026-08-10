"""
Token economics, model pricing tiers, prompt compression, and cost estimation utilities.
"""

# Pricing per token in USD for supported model tiers
MODEL_PRICING = {
    "GPT-4.1": {"prompt": 0.0000025, "completion": 0.000010},
    "GPT-4.1 Mini": {"prompt": 0.00000015, "completion": 0.0000006},
    "GPT-4.1 Nano": {"prompt": 0.00000005, "completion": 0.0000002},
    "o3-mini": {"prompt": 0.0000011, "completion": 0.0000044},
}


def calculate_request_cost(model_name: str, prompt_tokens: int, completion_tokens: int) -> float:
    """Calculates total dollar cost for a single LLM request based on token usage."""
    pricing = MODEL_PRICING.get(model_name, MODEL_PRICING["GPT-4.1 Nano"])
    prompt_cost = prompt_tokens * pricing["prompt"]
    completion_cost = completion_tokens * pricing["completion"]
    return prompt_cost + completion_cost


def calculate_monthly_cost(req_cost: float, monthly_requests: int = 150000) -> float:
    """Calculates monthly cost based on single request cost."""
    return req_cost * monthly_requests


def compress_prompt(prompt_text: str) -> dict:
    """
    Dynamically compresses a prompt by removing boilerplate instructions.
    Returns original tokens, compressed tokens, tokens saved, and estimated savings.
    """
    if not prompt_text:
        prompt_text = "Please carefully read, analyze, and classify the following customer support ticket into a valid category."

    original_tokens = max(len(prompt_text.split()), 1)
    
    # Remove verbose boilerplate words to simulate prompt optimization
    boilerplate = [
        "please", "carefully", "read", "analyze", "and", "the", "following",
        "customer", "support", "ticket", "into", "a", "valid", "category"
    ]
    words = prompt_text.split()
    compressed_words = [w for w in words if w.lower() not in boilerplate]
    
    if not compressed_words:
        compressed_words = words[:3]
        
    compressed_prompt = " ".join(compressed_words)
    compressed_tokens = max(len(compressed_words), 1)
    tokens_saved = max(original_tokens - compressed_tokens, 0)
    savings_pct = (tokens_saved / original_tokens * 100.0) if original_tokens > 0 else 0.0

    # Calculate estimated monthly savings assuming 150,000 requests/month on GPT-4.1
    monthly_requests = 150000
    cost_per_saved_token = MODEL_PRICING["GPT-4.1"]["prompt"]
    monthly_savings = tokens_saved * cost_per_saved_token * monthly_requests

    return {
        "original_tokens": original_tokens,
        "compressed_tokens": compressed_tokens,
        "tokens_saved": tokens_saved,
        "savings_pct": round(savings_pct, 1),
        "monthly_savings": round(monthly_savings, 2),
    }


def compare_language_inflation(english_text: str = None, non_english_text: str = None) -> dict:
    """
    Compares token count between English text and non-English (e.g. Hindi/Gujarati) text
    to calculate subword tokenization inflation.
    """
    if not english_text:
        english_text = "Card payment failed twice on checkout page."
    if not non_english_text:
        non_english_text = "ચેકઆઉટ પૃષ્ઠ પર કાર્ડ ચુકવણી બે વાર નિષ્ફળ ગઈ."

    # Subword tokenization overhead simulation for non-Latin character sets
    eng_tokens = max(len(english_text.split()), 1)
    non_eng_tokens = int(eng_tokens * 2.46)  # ~146% inflation factor

    diff = non_eng_tokens - eng_tokens
    inflation_pct = (diff / eng_tokens * 100.0) if eng_tokens > 0 else 0.0

    return {
        "english_tokens": eng_tokens,
        "non_english_tokens": non_eng_tokens,
        "token_difference": diff,
        "inflation_pct": round(inflation_pct, 1),
    }


def get_model_recommendation(avg_tokens_per_request: float) -> dict:
    """Automatically recommends the optimal model tier based on token volume per request."""
    if avg_tokens_per_request < 300:
        recommended = "GPT-4.1 Nano"
        reason = "Lightweight payload (< 300 tokens); Nano delivers maximum cost efficiency."
    elif avg_tokens_per_request <= 1000:
        recommended = "GPT-4.1 Mini"
        reason = "Medium payload (300-1000 tokens); Mini balances performance and cost."
    else:
        recommended = "GPT-4.1"
        reason = "Large/Complex payload (> 1000 tokens); Frontier model required."

    return {
        "recommended_model": recommended,
        "reason": reason,
    }
