"""Simple rate limiter to enforce requests per second."""

import time
import threading


class RateLimiter:
    """
    Token bucket rate limiter.
    Ensures that no more than `max_requests` are made in `period` seconds.
    """

    def __init__(self, max_requests: int, period: float):
        self.max_requests = max_requests
        self.period = period
        self.tokens = max_requests
        self.last_refill = time.monotonic()
        self.lock = threading.Lock()

    def _refill(self):
        now = time.monotonic()
        elapsed = now - self.last_refill
        if elapsed > self.period:
            self.tokens = min(self.max_requests, self.tokens + int(elapsed / self.period))
            self.last_refill = now

    def acquire(self):
        """Block until a token is available."""
        with self.lock:
            self._refill()
            while self.tokens < 1:
                time.sleep(0.05)
                self._refill()
            self.tokens -= 1