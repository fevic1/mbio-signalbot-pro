"""
Central market cache.
Only this module talks to the exchange.
"""

import time
import threading

from core.app_context import app_context

class MarketCache:

    def get(self, asset):
        """Compatibility wrapper."""
        return self.snapshot().get(asset)


    def __init__(self):
        self._lock = threading.Lock()
        self._ttl = 1.0

        self._prices = {}
        self._positions = []
        self._orders = []

        self._last_prices = 0.0
        self._last_positions = 0.0
        self._last_orders = 0.0

    def _executor(self):
        return app_context.executor

    def all_mids(self):
        now = time.time()

        with self._lock:
            if now - self._last_prices > self._ttl:
                try:
                    self._prices = self._executor().info.all_mids()
                    self._last_prices = now
                except Exception:
                    pass

        return self._prices

    def price(self, asset):
        asset = asset.replace("-USD", "")
        return float(self.all_mids().get(asset, 0))

    def positions(self):
        now = time.time()

        with self._lock:
            if now - self._last_positions > self._ttl:
                try:
                    self._positions = self._executor().get_open_positions()
                    self._last_positions = now
                except Exception:
                    pass

        return self._positions

    def orders(self):
        now = time.time()

        with self._lock:
            if now - self._last_orders > self._ttl:
                try:
                    self._orders = self._executor().get_open_orders()
                    self._last_orders = now
                except Exception:
                    pass

        return self._orders

    def snapshot(self):
        return {
            "prices": self.all_mids(),
            "positions": self.positions(),
            "orders": self.orders(),
        }

market_cache = MarketCache()
