import asyncio
import random
import time
import httpx
from ticket_classifier.circuit_breaker import CircuitBreaker
from ticket_classifier.providers import MockPrimaryProvider, MockFallbackProvider
from ticket_classifier.logger import log_llm_call
from ticket_classifier.tracer import trace_llm_call, trace_langfuse_call


class AsyncLLMClient:
    """
    Resilient Async LLM Client featuring:
    - Semaphore concurrency limits
    - Retry logic with backoff, jitter, and Retry-After
    - Circuit Breaker integration
    - Fallback provider safety net
    - Observability: Structured Logging & LangSmith Tracing
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

        # Error breakdown counters
        self.http_429_count = 0
        self.http_500_count = 0
        self.timeout_count = 0
        self.http_400_count = 0

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
            req_retries = 0
            start_time = time.time()

            try:
                # 1. Check Circuit Breaker before calling primary provider
                if not self.circuit_breaker.can_execute():
                    last_reason = "Circuit Breaker OPEN"
                    print("\nSwitching to fallback provider...")
                    res = await self._use_fallback(ticket_text, ticket_id, last_reason)
                    self._record_observability(ticket_text, res, start_time, req_retries, "stop")
                    return res

                # 2. Retry loop for Primary Provider
                for attempt in range(self.max_retries + 1):
                    try:
                        res = await self.primary_provider.classify(ticket_text, force_outcome)
                        self.circuit_breaker.record_success()
                        self.primary_success_count += 1
                        res["status"] = "primary_success"
                        res["ticket_id"] = ticket_id
                        self._record_observability(ticket_text, res, start_time, req_retries, "stop")
                        return res

                    except httpx.HTTPStatusError as err:
                        status = err.response.status_code

                        if status == 400:
                            self.http_400_count += 1
                            last_reason = "HTTP 400"
                            print("\nHTTP 400 encountered. Not retrying.")
                            break

                        if status in (429, 500) and attempt < self.max_retries:
                            self.total_retries += 1
                            req_retries += 1
                            attempt_num = attempt + 1
                            if status == 429:
                                self.http_429_count += 1
                                last_reason = "HTTP 429"
                                retry_after = float(err.response.headers.get("Retry-After", self.base_delay))
                                print(f"\nRetrying request (Attempt {attempt_num}/{self.max_retries}) after HTTP 429...")
                                print("Retry-After detected.")
                                print(f"Waiting {retry_after:.2f} seconds before retrying...")
                                await asyncio.sleep(retry_after)
                            else:
                                self.http_500_count += 1
                                last_reason = "HTTP 500"
                                delay = self.base_delay * (2 ** attempt) + random.uniform(0.01, 0.03)
                                print(f"\nRetrying request (Attempt {attempt_num}/{self.max_retries}) after HTTP 500...")
                                await asyncio.sleep(delay)
                        else:
                            if status == 429:
                                self.http_429_count += 1
                            elif status == 500:
                                self.http_500_count += 1
                            last_reason = f"HTTP {status}"
                            break

                    except (httpx.TimeoutException, TimeoutError):
                        self.timeout_count += 1
                        last_reason = "Timeout"
                        if attempt < self.max_retries:
                            self.total_retries += 1
                            req_retries += 1
                            attempt_num = attempt + 1
                            delay = self.base_delay * (2 ** attempt) + random.uniform(0.01, 0.03)
                            print(f"\nRetrying request (Attempt {attempt_num}/{self.max_retries}) after Timeout...")
                            await asyncio.sleep(delay)
                        else:
                            break

                # 3. Fallback when primary retries fail
                self.circuit_breaker.record_failure()
                print("Switching to fallback provider...")
                res = await self._use_fallback(ticket_text, ticket_id, last_reason)
                self._record_observability(ticket_text, res, start_time, req_retries, "stop")
                return res

            finally:
                self.current_inflight -= 1

    def _record_observability(self, ticket_text: str, res: dict, start_time: float, retry_count: int, finish_reason: str):
        """Helper to invoke structured logging and LangSmith tracing."""
        latency_ms = (time.time() - start_time) * 1000.0
        success = res.get("status") in ("primary_success", "fallback_success")
        provider = res.get("provider", "unknown")
        category = res.get("category", "")
        
        prompt_tokens = max(len(ticket_text.split()), 1)
        completion_tokens = max(len(str(category).split()), 1)
        total_tokens = prompt_tokens + completion_tokens
        estimated_cost = total_tokens * 0.00001

        log_llm_call(
            model_name="llama-3.3-70b",
            prompt=ticket_text,
            completion=str(category),
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            estimated_cost=estimated_cost,
            latency_ms=latency_ms,
            retry_count=retry_count,
            finish_reason=finish_reason,
            provider=provider,
            success=success,
        )

        trace_llm_call(
            input=ticket_text,
            output=res,
            latency=latency_ms,
            retry_count=retry_count,
            provider=provider,
            finish_reason=finish_reason,
        )

        trace_langfuse_call(
            ticket_id=res.get("ticket_id"),
            input_text=ticket_text,
            output_data=res,
            latency_ms=latency_ms,
            retry_count=retry_count,
            finish_reason=finish_reason,
            provider=provider,
            success=success,
        )

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

