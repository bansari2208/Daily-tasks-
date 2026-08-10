import asyncio
import os
import random
import time
from datetime import datetime, timezone
import httpx
from .circuit_breaker import CircuitBreaker
from .providers import MockPrimaryProvider, MockFallbackProvider
from .logger import log_llm_call, save_to_review_queue
from .cost import calculate_request_cost
from .tracer import trace_llm_call, trace_langfuse_call
from .config import (
    TEMPERATURE,
    TOP_P,
    CONFIDENCE_THRESHOLD,
    SCHEMA_VALIDATION,
    STANDARD_MODEL,
    REASONING_MODEL,
)
from .reasoning import (
    analyze_ticket_complexity,
    should_use_reasoning_model,
    estimate_reasoning_tokens,
)


def validate_response_schema(res: dict) -> bool:
    """Validates that structured LLM response contains a valid non-empty category."""
    if not isinstance(res, dict):
        return False
    cat = res.get("category")
    return bool(cat and isinstance(cat, str) and cat.strip() != "")


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
        debug_latency: bool = False,
    ):
        self.primary_provider = primary_provider or MockPrimaryProvider()
        self.fallback_provider = fallback_provider or MockFallbackProvider()
        
        self.max_concurrency = max_concurrency
        self.semaphore_limit = max_concurrency  # Alias for explicit concurrency verification
        self.semaphore = asyncio.Semaphore(max_concurrency)
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.debug_latency = debug_latency or os.getenv("DEBUG_LATENCY", "False").lower() in ("true", "1")

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

            # Playbook task detection and active model selection
            task_type = detect_task_type(ticket_text)
            recommended_model = get_recommended_model(task_type)
            selected_model = recommended_model
            model_reason = get_model_reason(task_type)
            pb_temp = get_default_temperature(task_type)
            pb_top_p = get_default_top_p(task_type)
            pb_ver = get_playbook_version()
            pb_updated = get_playbook_last_updated()

            complexity = analyze_ticket_complexity(ticket_text)
            reasoning_tokens = estimate_reasoning_tokens(complexity)

            try:
                # 1. Check Circuit Breaker before calling primary provider
                if not self.circuit_breaker.can_execute():
                    last_reason = "Circuit Breaker OPEN"
                    print("\nSwitching to fallback provider...")
                    res = await self._use_fallback(ticket_text, ticket_id, last_reason)
                    res["task_type"] = task_type
                    res["recommended_model"] = recommended_model
                    res["selected_model"] = selected_model
                    res["model_used"] = selected_model
                    res["temperature"] = pb_temp
                    res["top_p"] = pb_top_p
                    res["playbook_version"] = pb_ver
                    res["playbook_last_updated"] = pb_updated
                    res["playbook_reason"] = model_reason
                    res["playbook_decision_reason"] = model_reason
                    res["complexity"] = complexity
                    res["reasoning_tokens"] = reasoning_tokens
                    self._record_observability(ticket_text, res, start_time, req_retries, "stop")
                    return res

                # 2. Retry loop for Primary Provider
                for attempt in range(self.max_retries + 1):
                    try:
                        res = await self.primary_provider.classify(ticket_text, force_outcome)
                        
                        # Schema Validation check
                        schema_valid = validate_response_schema(res)
                        val_retry = False
                        if not schema_valid and SCHEMA_VALIDATION and force_outcome != "schema_fail":
                            val_retry = True
                            try:
                                res = await self.primary_provider.classify(ticket_text, force_outcome)
                                schema_valid = validate_response_schema(res)
                            except Exception:
                                pass

                        if not schema_valid:
                            res = await self._use_fallback(ticket_text, ticket_id, "Schema Validation Failed")
                            res["task_type"] = task_type
                            res["recommended_model"] = recommended_model
                            res["selected_model"] = selected_model
                            res["model_used"] = selected_model
                            res["temperature"] = pb_temp
                            res["top_p"] = pb_top_p
                            res["playbook_version"] = pb_ver
                            res["playbook_last_updated"] = pb_updated
                            res["playbook_reason"] = model_reason
                            res["playbook_decision_reason"] = model_reason
                            res["complexity"] = complexity
                            res["reasoning_tokens"] = reasoning_tokens
                            self._record_observability(
                                ticket_text, res, start_time, req_retries, "stop",
                                schema_valid=False, validation_retry=val_retry
                            )
                            return res

                        self.circuit_breaker.record_success()
                        self.primary_success_count += 1
                        res["status"] = "primary_success"
                        res["ticket_id"] = ticket_id

                        # Confidence calculation & Human Review Routing
                        conf = float(res.get("confidence", 0.95))
                        routing = "AUTO_PROCESSED" if conf >= CONFIDENCE_THRESHOLD else "NEEDS_HUMAN_REVIEW"
                        res["confidence"] = round(conf, 2)
                        res["routing"] = routing
                        res["task_type"] = task_type
                        res["recommended_model"] = recommended_model
                        res["selected_model"] = selected_model
                        res["model_used"] = selected_model
                        res["temperature"] = pb_temp
                        res["top_p"] = pb_top_p
                        res["playbook_version"] = pb_ver
                        res["playbook_last_updated"] = pb_updated
                        res["playbook_reason"] = model_reason
                        res["playbook_decision_reason"] = model_reason
                        res["complexity"] = complexity
                        res["reasoning_tokens"] = reasoning_tokens

                        if routing == "NEEDS_HUMAN_REVIEW":
                            save_to_review_queue(
                                ticket_id=ticket_id or 0,
                                category=res.get("category", "General"),
                                confidence=conf,
                                reason=f"Low Confidence (< {CONFIDENCE_THRESHOLD})",
                            )

                        if self.debug_latency:
                            print("\nTicket Analysis")
                            print("---------------")
                            print(f"Task Type      : {task_type}")
                            print(f"Model          : {selected_model}")
                            print(f"Reason         : {model_reason}")
                            print(f"Confidence     : {conf:.2f}")
                            print(f"Routing        : {routing}")
                            print(f"Category       : {res.get('category', '')}")
                            print(f"Priority       : {res.get('priority', 'NORMAL')}")

                        self._record_observability(
                            ticket_text, res, start_time, req_retries, "stop",
                            schema_valid=schema_valid, validation_retry=val_retry
                        )
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

    async def classify_stream(
        self, ticket_text: str, target_output_tokens: int = 20, force_outcome: str = None
    ):
        """Streams classification tokens asynchronously while enforcing semaphore limits."""
        async with self.semaphore:
            if hasattr(self.primary_provider, "classify_stream"):
                async for token in self.primary_provider.classify_stream(
                    ticket_text, target_output_tokens, force_outcome
                ):
                    yield token
            else:
                res = await self.classify_ticket(ticket_text, force_outcome=force_outcome)
                yield str(res)

    def _record_observability(
        self,
        ticket_text: str,
        res: dict,
        start_time: float,
        retry_count: int,
        finish_reason: str,
        schema_valid: bool = True,
        validation_retry: bool = False,
    ):
        """Helper to invoke structured logging, metrics calculation, and LangSmith tracing."""
        end_time_sec = time.time()
        latency_ms = (end_time_sec - start_time) * 1000.0
        success = res.get("status") in ("primary_success", "fallback_success")
        provider = res.get("provider", "unknown")
        category = res.get("category", "")
        
        prompt_tokens = max(len(ticket_text.split()), 1)
        completion_tokens = max(len(str(category).split()), 1)
        total_tokens = prompt_tokens + completion_tokens

        # Determine actual model used based on provider and compute exact cost
        if provider == "MockPrimary":
            model_name = "GPT-4.1 Nano"
        elif provider == "MockFallback":
            model_name = "GPT-4.1 Mini"
        else:
            model_name = "GPT-4.1"

        estimated_cost = calculate_request_cost(model_name, prompt_tokens, completion_tokens)

        # Calculate production TTFT and TPOT
        ttft_ms = min(20.0 + (prompt_tokens * 0.1), latency_ms)
        tpot_ms = max(latency_ms - ttft_ms, 1.0) / completion_tokens
        cb_state = str(getattr(self.circuit_breaker, "state", "CLOSED"))

        req_started_at = datetime.fromtimestamp(start_time, tz=timezone.utc).isoformat()
        req_finished_at = datetime.fromtimestamp(end_time_sec, tz=timezone.utc).isoformat()

        # High latency warning for production monitoring (> 1000ms)
        if latency_ms > 1000.0:
            print(f"\nWARNING: High latency detected ({latency_ms:.2f} ms > 1000 ms)")

        # Optional debug latency console logging
        if self.debug_latency:
            print(f"[Latency Info] Total: {latency_ms:.2f}ms | TTFT: {ttft_ms:.2f}ms | TPOT: {tpot_ms:.2f}ms")

        conf = float(res.get("confidence", 0.95))
        routing = res.get("routing", "AUTO_PROCESSED")
        complexity = res.get("complexity", "EASY")
        model_used = res.get("selected_model", res.get("model_used", STANDARD_MODEL))
        reasoning_tokens = res.get("reasoning_tokens", 0)
        used_reasoning_model = (model_used == REASONING_MODEL)
        task_type = res.get("task_type", "SIMPLE_CLASSIFICATION")
        rec_model = res.get("recommended_model", model_used)
        sel_model = res.get("selected_model", model_used)
        pb_version = res.get("playbook_version", "v1.1")
        pb_updated = res.get("playbook_last_updated", "2026-07-30")
        pb_reason = res.get("playbook_decision_reason", "Fastest and cheapest for routine tickets")
        req_temp = res.get("temperature", TEMPERATURE)
        req_top_p = res.get("top_p", TOP_P)

        log_llm_call(
            model_name=model_name,
            prompt=ticket_text,
            completion=str(category),
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            estimated_cost=estimated_cost,
            latency_ms=latency_ms,
            ttft_ms=ttft_ms,
            tpot_ms=tpot_ms,
            request_started_at=req_started_at,
            request_finished_at=req_finished_at,
            circuit_breaker=cb_state,
            temperature=req_temp,
            top_p=req_top_p,
            confidence_score=conf,
            routing_decision=routing,
            schema_valid=schema_valid,
            validation_retry=validation_retry,
            complexity=complexity,
            model_used=model_used,
            reasoning_tokens=reasoning_tokens,
            used_reasoning_model=used_reasoning_model,
            task_type=task_type,
            recommended_model=rec_model,
            selected_model=sel_model,
            playbook_version=pb_version,
            playbook_last_updated=pb_updated,
            playbook_decision_reason=pb_reason,
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

            conf = float(res.get("confidence", 0.70))
            routing = "AUTO_PROCESSED" if conf >= CONFIDENCE_THRESHOLD else "NEEDS_HUMAN_REVIEW"
            res["confidence"] = round(conf, 2)
            res["routing"] = routing

            if routing == "NEEDS_HUMAN_REVIEW":
                save_to_review_queue(
                    ticket_id=ticket_id or 0,
                    category=res.get("category", "General"),
                    confidence=conf,
                    reason=f"Low Confidence (< {CONFIDENCE_THRESHOLD})",
                )

            task_type = detect_task_type(ticket_text)
            recommended_model = get_recommended_model(task_type)
            selected_model = recommended_model
            model_reason = get_model_reason(task_type)
            pb_temp = get_default_temperature(task_type)
            pb_top_p = get_default_top_p(task_type)
            pb_ver = get_playbook_version()
            pb_updated = get_playbook_last_updated()
            complexity = analyze_ticket_complexity(ticket_text)
            reasoning_tokens = estimate_reasoning_tokens(complexity)

            res["task_type"] = task_type
            res["recommended_model"] = recommended_model
            res["selected_model"] = selected_model
            res["model_used"] = selected_model
            res["temperature"] = pb_temp
            res["top_p"] = pb_top_p
            res["playbook_version"] = pb_ver
            res["playbook_last_updated"] = pb_updated
            res["playbook_reason"] = model_reason
            res["playbook_decision_reason"] = model_reason
            res["complexity"] = complexity
            res["reasoning_tokens"] = reasoning_tokens

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

