import unittest
import asyncio
import sys
import os

# Ensure package import works regardless of execution directory

from ticket_classifier.client import AsyncLLMClient
from ticket_classifier.circuit_breaker import CircuitBreaker
from ticket_classifier.errors import ClassifierError, TransportError, ModelOutputError, BusinessRuleViolation
from ticket_classifier.providers import MockPrimaryProvider


class TestClient(unittest.TestCase):

    def test_custom_errors_raised(self):
        async def run():
            client = AsyncLLMClient(max_retries=1, base_delay=0.01)
            with self.assertRaises(ClassifierError):
                await client.classify_ticket(None)

            provider = MockPrimaryProvider()
            with self.assertRaises(TransportError):
                await provider.classify("test", force_outcome="timeout")

            with self.assertRaises(ModelOutputError):
                await provider.classify("test", force_outcome="invalid_output")

        asyncio.run(run())

    def test_timeout_retry(self):
        async def run():
            client = AsyncLLMClient(max_retries=2, base_delay=0.01)
            res = await client.classify_ticket("Payment issue", force_outcome="timeout")
            self.assertEqual(client.total_retries, 2)
            self.assertEqual(res["provider"], "MockFallback")
            self.assertEqual(res["status"], "fallback_success")
        asyncio.run(run())

    def test_429_retry(self):
        async def run():
            client = AsyncLLMClient(max_retries=2, base_delay=0.01)
            res = await client.classify_ticket("Rate limit test", force_outcome="429")
            self.assertEqual(client.total_retries, 2)
            self.assertEqual(res["provider"], "MockFallback")
            self.assertEqual(res["status"], "fallback_success")
        asyncio.run(run())

    def test_400_not_retried(self):
        async def run():
            client = AsyncLLMClient(max_retries=2, base_delay=0.01)
            res = await client.classify_ticket("Bad request test", force_outcome="400")
            # HTTP 400 must NOT be retried
            self.assertEqual(client.total_retries, 0)
            self.assertEqual(res["provider"], "MockFallback")
            self.assertEqual(res["status"], "fallback_success")
        asyncio.run(run())

    def test_fallback_provider(self):
        async def run():
            client = AsyncLLMClient(max_retries=1, base_delay=0.01)
            res = await client.classify_ticket("Fallback test", force_outcome="500")
            self.assertEqual(res["provider"], "MockFallback")
            self.assertEqual(client.fallback_success_count, 1)
        asyncio.run(run())

    def test_semaphore_concurrency_limit(self):
        async def run():
            client = AsyncLLMClient(max_concurrency=5, base_delay=0.01)
            tickets = [f"Ticket #{i}" for i in range(25)]
            await asyncio.gather(*[client.classify_ticket(t, force_outcome="success") for t in tickets])
            
            # Assert max concurrent requests observed never exceeded limit of 5
            self.assertLessEqual(client.max_inflight_seen, client.semaphore_limit)
            self.assertGreater(client.max_inflight_seen, 1)  # Confirm concurrent execution happened
        asyncio.run(run())

    def test_circuit_breaker_states(self):
        cb = CircuitBreaker(failure_threshold=3, cooldown_seconds=0.5)
        self.assertTrue(cb.can_execute())
        
        # Trigger 3 failures
        cb.record_failure()
        cb.record_failure()
        cb.record_failure()

        # Circuit should now be OPEN
        self.assertEqual(cb.state, "OPEN")
        self.assertFalse(cb.can_execute())

        cb.record_success()
        self.assertEqual(cb.state, "CLOSED")


if __name__ == "__main__":
    unittest.main()

