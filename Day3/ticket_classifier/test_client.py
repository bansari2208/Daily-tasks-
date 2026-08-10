import pytest
import asyncio
import sys
import os

# Ensure package import works regardless of execution directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from .client import AsyncLLMClient
from .circuit_breaker import CircuitBreaker


def test_timeout_retry():
    async def run():
        client = AsyncLLMClient(max_retries=2, base_delay=0.01)
        res = await client.classify_ticket("Payment issue", force_outcome="timeout")
        assert client.total_retries == 2
        assert res["provider"] == "MockFallback"
        assert res["status"] == "fallback_success"
    asyncio.run(run())


def test_429_retry():
    async def run():
        client = AsyncLLMClient(max_retries=2, base_delay=0.01)
        res = await client.classify_ticket("Rate limit test", force_outcome="429")
        assert client.total_retries == 2
        assert res["provider"] == "MockFallback"
        assert res["status"] == "fallback_success"
    asyncio.run(run())


def test_400_not_retried():
    async def run():
        client = AsyncLLMClient(max_retries=2, base_delay=0.01)
        res = await client.classify_ticket("Bad request test", force_outcome="400")
        # HTTP 400 must NOT be retried
        assert client.total_retries == 0
        assert res["provider"] == "MockFallback"
        assert res["status"] == "fallback_success"
    asyncio.run(run())


def test_fallback_provider():
    async def run():
        client = AsyncLLMClient(max_retries=1, base_delay=0.01)
        res = await client.classify_ticket("Fallback test", force_outcome="500")
        assert res["provider"] == "MockFallback"
        assert client.fallback_success_count == 1
    asyncio.run(run())


def test_semaphore_concurrency_limit():
    async def run():
        client = AsyncLLMClient(max_concurrency=5, base_delay=0.01)
        tickets = [f"Ticket #{i}" for i in range(25)]
        await asyncio.gather(*[client.classify_ticket(t, force_outcome="success") for t in tickets])
        
        # Assert max concurrent requests observed never exceeded limit of 5
        assert client.max_inflight_seen <= client.semaphore_limit
        assert client.max_inflight_seen > 1  # Confirm concurrent execution happened
    asyncio.run(run())


def test_circuit_breaker_states():
    cb = CircuitBreaker(failure_threshold=3, cooldown_seconds=0.5)
    assert cb.can_execute() is True
    
    # Trigger 3 failures
    cb.record_failure()
    cb.record_failure()
    cb.record_failure()

    # Circuit should now be OPEN
    assert cb.state == "OPEN"
    assert cb.can_execute() is False

    cb.record_success()
    assert cb.state == "CLOSED"
