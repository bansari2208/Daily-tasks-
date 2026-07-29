import unittest
import asyncio
import sys
import os

# Ensure package import works regardless of execution directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ticket_classifier.client import AsyncLLMClient
from ticket_classifier.circuit_breaker import CircuitBreaker


class TestClient(unittest.TestCase):

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
