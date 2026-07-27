import time


class CircuitBreaker:
    """
    A simple Circuit Breaker to prevent hammering failing providers.

    States: CLOSED, OPEN, HALF-OPEN
    Prints logs ONLY when the state actually changes.
    """

    def __init__(self, failure_threshold: int = 3, cooldown_seconds: float = 1.0):
        self.failure_threshold = failure_threshold
        self.cooldown_seconds = cooldown_seconds

        self.state = "CLOSED"
        self.failure_count = 0
        self.last_state_change = time.time()
        self.open_events = 0
        self.recoveries = 0

    def _set_state(self, new_state: str):
        if self.state != new_state:
            old_state = self.state
            self.state = new_state
            self.last_state_change = time.time()

            if new_state == "OPEN":
                self.open_events += 1
            elif new_state == "CLOSED" and old_state in ("OPEN", "HALF-OPEN"):
                self.recoveries += 1

            print(f"\nCircuit Breaker -> {self.state}")

    def can_execute(self) -> bool:
        """Check if a request is allowed to hit the primary provider."""
        if self.state == "CLOSED":
            return True

        if self.state == "OPEN":
            # Check if cooldown has elapsed to attempt HALF-OPEN state
            if time.time() - self.last_state_change >= self.cooldown_seconds:
                self._set_state("HALF-OPEN")
                return True
            return False

        # HALF-OPEN state allows trial execution
        return True

    def record_success(self):
        """Reset failure count and transition back to CLOSED."""
        self.failure_count = 0
        self._set_state("CLOSED")

    def record_failure(self):
        """Increment failure count and open circuit if threshold reached."""
        self.failure_count += 1
        if self.failure_count >= self.failure_threshold:
            self._set_state("OPEN")
