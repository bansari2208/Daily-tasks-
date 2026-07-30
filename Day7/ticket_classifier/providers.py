import random
import asyncio
import httpx


class MockPrimaryProvider:
    """
    Simulates a primary LLM provider (e.g. Groq) without real network calls.
    Randomly or deterministically simulates success, 429, 500, 400, or TimeoutError.
    """

    def __init__(self, error_rate: float = 0.3):
        self.error_rate = error_rate

    async def classify(self, ticket_text: str, force_outcome: str = None) -> dict:
        """
        Classifies support ticket or simulates an API failure.
        force_outcome can be used in unit tests: 'success', '429', '500', '400', 'timeout'.
        """
        # Simulate slight network latency
        await asyncio.sleep(0.05)

        outcome = force_outcome
        if not outcome:
            if random.random() > self.error_rate:
                outcome = "success"
            else:
                outcome = random.choice(["429", "500", "400", "timeout"])

        request = httpx.Request("POST", "https://api.mockgroq.com/classify")

        if outcome == "429":
            response = httpx.Response(429, headers={"Retry-After": "0.1"}, request=request)
            raise httpx.HTTPStatusError("Rate limit exceeded", request=request, response=response)

        elif outcome == "500":
            response = httpx.Response(500, request=request)
            raise httpx.HTTPStatusError("Internal Server Error", request=request, response=response)

        elif outcome == "400":
            response = httpx.Response(400, request=request)
            raise httpx.HTTPStatusError("Bad Request", request=request, response=response)

        elif outcome == "timeout":
            raise httpx.TimeoutException("Request timed out", request=request)

        # Simple category logic for successful response
        category = "Billing" if "payment" in ticket_text.lower() or "card" in ticket_text.lower() else "Technical"
        return {
            "category": category,
            "confidence": 0.95,
            "provider": "MockPrimary"
        }

    async def classify_stream(
        self, ticket_text: str, target_output_tokens: int = 20, force_outcome: str = None
    ):
        """Simulates streaming classification with realistic prefill & decode latency based on prompt size."""
        prompt_tokens = max(len(ticket_text.split()), 1)
        # Prefill delay proportional to prompt size (~0.1ms per prompt token + base latency)
        prefill_delay = 0.02 + (prompt_tokens * 0.0001)
        await asyncio.sleep(prefill_delay)

        # Decode phase: yield tokens sequentially with TPOT delay (~10ms per token)
        for i in range(target_output_tokens):
            if i > 0:
                await asyncio.sleep(0.01)
            yield f"token_{i+1} "



class MockFallbackProvider:
    """
    Backup provider used when primary provider fails after retries or circuit opens.
    Always succeeds with a safe default answer.
    """

    async def classify(self, ticket_text: str) -> dict:
        await asyncio.sleep(0.02)  # Fast fallback response
        return {
            "category": "General",
            "confidence": 0.70,
            "provider": "MockFallback"
        }

