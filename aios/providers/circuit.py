from time import time


class CircuitBreaker:

    def __init__(self, threshold=3, cooldown=60):
        self.threshold = threshold
        self.cooldown = cooldown
        self.failures = {}
        self.blocked_until = {}

    def allow(self, provider):
        until = self.blocked_until.get(provider, 0)
        return time() >= until

    def success(self, provider):
        self.failures[provider] = 0
        self.blocked_until.pop(provider, None)

    def failure(self, provider):
        count = self.failures.get(provider, 0) + 1
        self.failures[provider] = count

        if count >= self.threshold:
            self.blocked_until[provider] = time() + self.cooldown

    def status(self):
        return {
            "failures": self.failures,
            "blocked_until": self.blocked_until,
        }


circuit = CircuitBreaker()
