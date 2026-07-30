import asyncio
import random
import httpx
from ticket_classifier.circuit_breaker import CircuitBreaker
from ticket_classifier.providers import MockPrimaryProvider, MockFallbackProvider


class AsyncLLMClient:
    """
    Resilient Async LLM Client featuring:
    - Semaphore concurrency limits
    - Retry logic with backoff, jitter, and Retry-After
    - Circuit Breaker integration
    - Fallback provider safety net
    """

    def __init__(
        self,
        primary_provider=None,
        fallback_provider=None,
        max_concurrency: int = 5,
        max_retries: int = 2,
        base_delay: float = 0.05,
    ):
        self.primary_provider = primary_provider or MockPrimaryProvider()
        self.fallback_provider = fallback_provider or MockFallbackProvider()
        
        self.max_concurrency = max_concurrency
        self.semaphore_limit = max_concurrency  # Alias for explicit concurrency verification
        self.semaphore = asyncio.Semaphore(max_concurrency)
        self.max_retries = max_retries
        self.base_delay = base_delay

        # Metrics tracking
        self.current_inflight = 0
        self.max_inflight_seen = 0
        self.total_retries = 0
        self.primary_success_count = 0
        self.fallback_success_count = 0
        self.failed_count = 0

        self.circuit_breaker = CircuitBreaker()

    async def classify_ticket(
        self, ticket_text: str, ticket_id: int = None, force_outcome: str = None
    ) -> dict:
        """Classifies ticket with concurrency limits, retries, circuit breaker, and fallback."""
        async with self.semaphore:
            self.current_inflight += 1
            self.max_inflight_seen = max(self.max_inflight_seen, self.current_inflight)
            
            assert self.current_inflight <= self.semaphore_limit, (
                f"In-flight requests ({self.current_inflight}) exceeded limit ({self.semaphore_limit})!"
            )

            last_reason = None
            try:
                # 1. Check Circuit Breaker before calling primary provider
                if not self.circuit_breaker.can_execute():
                    last_reason = "Circuit Breaker OPEN"
                    print("\nSwitching to fallback provider...")
                    return await self._use_fallback(ticket_text, ticket_id, last_reason)

                # 2. Retry loop for Primary Provider
                for attempt in range(self.max_retries + 1):
                    try:
                        res = await self.primary_provider.classify(ticket_text, force_outcome)
                        self.circuit_breaker.record_success()
                        self.primary_success_count += 1
                        res["status"] = "primary_success"
                        res["ticket_id"] = ticket_id
                        return res

                    except httpx.HTTPStatusError as err:
                        status = err.response.status_code

                        if status == 400:
                            last_reason = "HTTP 400"
                            print("\nHTTP 400 encountered. Not retrying.")
                            break

                        if status in (429, 500) and attempt < self.max_retries:
                            self.total_retries += 1
                            attempt_num = attempt + 1
                            if status == 429:
                                last_reason = "HTTP 429"
                                retry_after = float(err.response.headers.get("Retry-After", self.base_delay))
                                print(f"\nRetrying request (Attempt {attempt_num}/{self.max_retries}) after HTTP 429...")
                                print("Retry-After detected.")
                                print(f"Waiting {retry_after:.2f} seconds before retrying...")
                                await asyncio.sleep(retry_after)
                            else:
                                last_reason = "HTTP 500"
                                delay = self.base_delay * (2 ** attempt) + random.uniform(0.01, 0.03)
                                print(f"\nRetrying request (Attempt {attempt_num}/{self.max_retries}) after HTTP 500...")
                                await asyncio.sleep(delay)
                        else:
                            last_reason = f"HTTP {status}"
                            break

                    except (httpx.TimeoutException, TimeoutError):
                        last_reason = "Timeout"
                        if attempt < self.max_retries:
                            self.total_retries += 1
                            attempt_num = attempt + 1
                            delay = self.base_delay * (2 ** attempt) + random.uniform(0.01, 0.03)
                            print(f"\nRetrying request (Attempt {attempt_num}/{self.max_retries}) after Timeout...")
                            await asyncio.sleep(delay)
                        else:
                            break

                # 3. Fallback when primary retries fail
                self.circuit_breaker.record_failure()
                print("Switching to fallback provider...")
                return await self._use_fallback(ticket_text, ticket_id, last_reason)

            finally:
                self.current_inflight -= 1

    async def _use_fallback(self, ticket_text: str, ticket_id: int, reason: str) -> dict:
        """Invoke secondary fallback provider."""
        try:
            res = await self.fallback_provider.classify(ticket_text)
            self.fallback_success_count += 1
            res["status"] = "fallback_success"
            res["fallback_reason"] = reason or "Primary Failed"
            res["ticket_id"] = ticket_id
            return res
        except Exception as e:
            self.failed_count += 1
            return {
                "status": "failed",
                "ticket_id": ticket_id,
                "fallback_reason": reason or "Primary Failed",
                "error": str(e),
                "provider": "Failed"
            }
