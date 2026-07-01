"""Base test class with common utilities."""
import unittest
import asyncio
from unittest.mock import Mock, patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class BaseTestCase(unittest.TestCase):
    """Base test case with common setup."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_state = {
            'OPEN_POSITIONS': {},
            'ACCOUNT_BALANCE': 1000.0,
            'DAILY_PNL': 0.0,
        }
        
    def run_async(self, coro):
        """Helper to run async functions in tests."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(coro)
        finally:
            loop.close()
    
    def create_mock_position(self, symbol='BTC', side='BUY', entry=50000, size=0.01):
        """Create a mock position for testing."""
        return {
            'symbol': symbol,
            'side': side,
            'entry': entry,
            'size': size,
            'sl': entry * 0.98,
            'tp1': entry * 1.02,
            'tp2': entry * 1.04,
            'tp3': entry * 1.06,
            'opened_at': '2026-01-15T10:00:00Z',
            'strategy': 'MeanReversion',
            'regime': 'RANGING',
        }
