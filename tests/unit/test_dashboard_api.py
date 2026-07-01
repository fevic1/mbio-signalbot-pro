"""Unit tests for the Real-time Dashboard API."""
import unittest
import sys
import os
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi.testclient import TestClient
from api.dashboard_router import router
from fastapi import FastAPI

# Create a test app
app = FastAPI()
app.include_router(router)
client = TestClient(app)

class TestDashboardAPI(unittest.TestCase):
    """Test the Dashboard API endpoints."""
    
    def test_status_endpoint(self):
        """Test the /status endpoint returns bot health."""
        response = client.get("/api/dashboard/status")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertEqual(data["status"], "online")
        self.assertEqual(data["version"], "9.0")
        self.assertIn("features", data)
        print(f"✅ /status endpoint works: {data['status']}")

    @patch('api.dashboard_router.state')
    def test_positions_endpoint_empty(self, mock_state):
        """Test /positions endpoint when no positions are open."""
        mock_state.OPEN_POSITIONS = {}
        
        response = client.get("/api/dashboard/positions")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["positions"], [])
        print("✅ /positions endpoint handles empty state correctly")

    @patch('api.dashboard_router.state')
    def test_positions_endpoint_with_data(self, mock_state):
        """Test /positions endpoint returns formatted position data."""
        mock_state.OPEN_POSITIONS = {
            'BTC': {
                'side': 'BUY',
                'entry': 65000,
                'size': 0.01,
                'sl': 64000,
                'tp1': 66000,
                'last_pattern': 'QUICK_WINNER',
                'llm_reasoning': 'Bullish divergence on 1H.'
            }
        }
        
        response = client.get("/api/dashboard/positions")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertEqual(len(data["positions"]), 1)
        self.assertEqual(data["positions"][0]["symbol"], "BTC")
        self.assertEqual(data["positions"][0]["pattern"], "QUICK_WINNER")
        print(f"✅ /positions endpoint formats data correctly: {data['positions'][0]['symbol']}")

    def test_performance_endpoint(self):
        """Test /performance endpoint returns metrics."""
        response = client.get("/api/dashboard/performance")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertIn("daily_pnl", data)
        print("✅ /performance endpoint returns metrics structure")

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestDashboardAPI)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
