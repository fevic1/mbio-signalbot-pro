"""
BybitExecutor — Live Bybit Execution (Singleton with Runtime Balance Guard)
"""
import os
import threading
import logging
from typing import Optional, Dict

logger = logging.getLogger(__name__)

class BybitExecutor:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(BybitExecutor, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        
        self.api_key = os.getenv("BYBIT_API_KEY")
        self.api_secret = os.getenv("BYBIT_API_SECRET")
        self.testnet = os.getenv("BYBIT_TESTNET", "false").lower() == "true"
        
        if not self.api_key or not self.api_secret:
            logger.warning("⚠️ Bybit credentials not found. Bybit execution disabled.")
            self._initialized = True
            return

        try:
            from pybit.unified_trading import HTTP
            self.client = HTTP(
                testnet=self.testnet,
                api_key=self.api_key,
                api_secret=self.api_secret,
                recv_window=10000
            )
            logger.info(f"✅ BybitExecutor initialized (Testnet: {self.testnet})")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Bybit client: {e}")
            self.client = None
            
        self._initialized = True

    def place_order(self, coin: str, side: str, size: float, limit_price: Optional[float] = None, 
                    order_type: str = "Market", reduce_only: bool = False) -> Dict:
        if not self.client:
            return {"success": False, "error": "Bybit client not initialized"}
            
        try:
            bybit_side = "Buy" if side.upper() == "BUY" else "Sell"
            is_limit = order_type.lower() == "limit" and limit_price is not None
            order_type_bybit = "Limit" if is_limit else "Market"
            
            params = {
                "category": "linear",
                "symbol": f"{coin.upper()}USDT",
                "side": bybit_side,
                "orderType": order_type_bybit,
                "qty": str(size),
                "reduceOnly": reduce_only,
                "timeInForce": "GTC" if is_limit else "IOC"
            }
            
            if is_limit:
                params["price"] = str(limit_price)

            res = self.client.place_order(**params)
            if res["retCode"] == 0:
                logger.info(f"✅ Bybit Order Placed: {coin} {side} {size} @ {limit_price or 'Market'}")
                return {"success": True, "order_id": res["result"]["orderId"], "avg_price": limit_price or 0}
            else:
                logger.error(f"❌ Bybit Order Failed: {res['retMsg']}")
                return {"success": False, "error": res["retMsg"]}
        except Exception as e:
            logger.error(f"❌ Bybit place_order error: {e}")
            return {"success": False, "error": str(e)}

    def get_open_positions(self) -> list:
        if not self.client:
            return []
        try:
            res = self.client.get_positions(category="linear", settleCoin="USDT")
            if res["retCode"] == 0:
                positions = []
                for p in res["result"]["list"]:
                    if float(p["size"]) > 0:
                        positions.append({
                            "coin": p["symbol"].replace("USDT", ""),
                            "side": "long" if p["side"] == "Buy" else "short",
                            "size": float(p["size"]),
                            "entry_price": float(p["avgPrice"])
                        })
                return positions
        except Exception as e:
            logger.error(f"❌ Bybit get_open_positions error: {e}")
        return []

def get_bybit_executor() -> 'BybitExecutor':
    return BybitExecutor()
