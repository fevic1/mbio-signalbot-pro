"""
execution/hl_executor.py — Live Hyperliquid Execution (SDK-Agnostic)
Dynamically adapts to any hyperliquid SDK structure.
"""
import os
import logging
from typing import Optional, Dict
from core.hip4_metadata import HIP4MetadataManager


logger = logging.getLogger(__name__)

# =============================================================================
# DYNAMIC SDK IMPORTS — Try multiple patterns until one works
# =============================================================================
_Info = None
_Exchange = None
_constants = None

def _load_sdk():
    """Load Hyperliquid SDK classes using any available import pattern."""
    global _Info, _Exchange, _constants
    
    if _Info is not None:
        return  # Already loaded
    
    # Pattern 1: Submodule imports (official SDK structure)
    try:
        from hyperliquid.info import Info
        from hyperliquid.exchange import Exchange
        from hyperliquid.utils import constants
        _Info, _Exchange, _constants = Info, Exchange, constants
        logger.info("✅ SDK loaded: submodule imports")
        return
    except ImportError:
        pass
    
    # Pattern 2: Top-level imports (alternative structure)
    try:
        from hyperliquid import Info, Exchange
        from hyperliquid.utils import constants
        _Info, _Exchange, _constants = Info, Exchange, constants
        logger.info("✅ SDK loaded: top-level imports")
        return
    except ImportError:
        pass
    
    # Pattern 3: Direct attribute access
    try:
        import hyperliquid
        _Info = getattr(hyperliquid, 'Info', None)
        _Exchange = getattr(hyperliquid, 'Exchange', None)
        if _Info and _Exchange:
            from hyperliquid.utils import constants
            _constants = constants
            logger.info("✅ SDK loaded: attribute access")
            return
    except Exception:
        pass
    
    # If all patterns fail, raise clear error
    raise ImportError(
        "Could not load Hyperliquid SDK. "
        "Ensure 'hyperliquid-python-sdk (latest)' is installed and try rebuilding."
    )


# =============================================================================
# EXECUTOR CLASS
# =============================================================================

# Hardcoded precision (proven to work)
_PRECISION = {
    'BTC': {'sz_decimals': 4, 'tick': 1.0},
    'ETH': {'sz_decimals': 3, 'tick': 0.1},
    'SOL': {'sz_decimals': 2, 'tick': 0.01},
    'XRP': {'sz_decimals': 0, 'tick': 0.0001},  # Integer sizes only
    'DOGE': {'sz_decimals': 0, 'tick': 0.00001},
    'LINK': {'sz_decimals': 2, 'tick': 0.001},
    'BTC': {'sz_decimals': 5, 'tick': 1.0},
    'ETH': {'sz_decimals': 4, 'tick': 0.1},
    'AVAX': {'sz_decimals': 2, 'tick': 0.01},
    'HYPE': {'sz_decimals': 2, 'tick': 0.001},
}

def _round_px(asset, px):
    tick = _PRECISION.get(asset, {}).get('tick', 0.01)
    # Avoid floating point errors
    return float(f"{round(px / tick) * tick:.10f}")

def _round_sz(asset, sz):
    dec = _PRECISION.get(asset, {}).get('sz_decimals', 2)
    return round(sz, dec)


class HLExecutor:
    def __init__(self, private_key: str | None = None, chat_id: int | None = None):
        _load_sdk()  # Ensure SDK is loaded
        
        # Multi-user support: use provided key or fallback to env var
        if private_key:
            self.private_key = private_key
        else:
            self.private_key = os.getenv("HL_PRIVATE_KEY")
        if not self.private_key:
            raise ValueError("HL_PRIVATE_KEY not set")
        
        from eth_account import Account
        self.account = Account.from_key(self.private_key)
        self.address = self.account.address
        
        # Initialize clients using dynamically loaded classes
        base_url = _constants.MAINNET_API_URL
        self.info = _Info(base_url, skip_ws=True)
        
        # --- HIP-4 INSTITUTIONAL INTEGRATION ---
        from core.hip4_metadata import HIP4MetadataManager
        self.hip4_manager = HIP4MetadataManager.get_instance()
        self.hip4_manager.initialize(self.info)
        logger.info("✅ HIP-4 Metadata Manager initialized.")
        # ---------------------------------------
        self.exchange = _Exchange(self.account, base_url, account_address=self.address)
        
        mode = "multi-user" if private_key else "single-user (env)"
        logger.info(f"✅ HLExecutor initialized for {self.address} [{mode}]")

    def cancel_order(self, coin: str, order_id: int) -> dict:
        """Cancel an open order by ID. Wraps exchange.cancel_order()."""
        try:
            result = self.exchange.cancel(coin=coin, oid=int(order_id))
            logger.info(f"🗑️ Cancelled order {order_id} for {coin}: {result}")
            return {"success": True, "result": result}
        except Exception as e:
            logger.error(f"❌ Failed to cancel order {order_id} for {coin}: {e}")
            return {"success": False, "error": str(e)}

    def get_open_positions(self):
        try:
            import requests
            # Use HL_ACCOUNT_ADDRESS from env (master account) for querying positions
            query_address = os.getenv("HL_ACCOUNT_ADDRESS", self.address)
            
            # Use direct HTTP call to clearinghouseState (bypasses SDK issues)
            resp = requests.post(
                "https://api.hyperliquid.xyz/info",
                json={"type": "clearinghouseState", "user": query_address},
                timeout=15
            )
            logger.debug(f"🔍 Querying positions for: {query_address}")
            if resp.status_code != 200:
                logger.error(f"Failed to fetch positions: HTTP {resp.status_code}")
                return []
            
            user_state = resp.json()
            logger.info(f"🔍 API Response keys: {list(user_state.keys())}")
            logger.info(f"🔍 assetPositions count: {len(user_state.get('assetPositions', []))}")
            if user_state.get('assetPositions'):
                logger.info(f"🔍 First position sample: {user_state['assetPositions'][0]}")
            positions = []
            for p in user_state.get("assetPositions", []):
                pos = p.get("position", {})
                szi = float(pos.get("szi", 0))
                if abs(szi) > 0.0001:
                    positions.append({
                        "coin": pos.get("coin", "?"), 
                        "side": "long" if szi > 0 else "short", 
                        "size": abs(szi), 
                        "entry_price": float(pos.get("entryPx", 0) or 0)
                    })
            logger.info(f"📊 Fetched {len(positions)} open positions from exchange")
            return positions
        except Exception as e:
            logger.error(f"Failed to get open positions: {e}")
            return []

    def place_order(
        self,
        coin: str,
        side: str,
        size: float,
        limit_price: Optional[float] = None,
        order_type: str = "Limit",
        reduce_only: bool = False
    ) -> Dict:
        """Place a synchronous order (call from async context with asyncio.to_thread)."""
        try:
            is_buy = side.upper() == "BUY"
            sz = float(size)
            # Round size to exchange precision
            # _prec removed: Using HIP-4 live metadata
            sz = self.hip4_manager.format_size(coin, sz)
            
            # Determine price
            if limit_price is None:
                mids = self.info.all_mids()
                mid = float(mids.get(coin, 0))
                limit_price = mid * 1.001 if is_buy else mid * 0.999
            
            # Convert to float without rounding (preserve full precision)
            px = float(limit_price)
            
            logger.info(f"🚀 Order: {side} {coin} {sz} @ {px}")
            
            # Apply tick rounding and size rounding according to asset precision
            px = _round_px(coin, px)
            # sz = _round_sz(coin, sz)  <-- REMOVED: HIP-4 format_size already applied
            logger.info(f"🎯 Rounded: {coin} px={px} sz={sz}")
            

            # Hyperliquid minimum order protection
            notional = abs(sz * px)

            if notional < 10:
                logger.warning(
                    f"⛔ Skipping order: {coin} {side} "
                    f"size={sz} px={px} "
                    f"notional=${notional:.2f} < $10 minimum"
                )

                return {
                    "success": False,
                    "error": f"Order value ${notional:.2f} below Hyperliquid $10 minimum"
                }

            result = self.exchange.order(coin, is_buy, sz, px, {"limit": {"tif": "Gtc"}}, reduce_only)
            
            # Defensive response parsing
            if not isinstance(result, dict):
                return {"success": False, "error": "Invalid response type"}
            
            # Try multiple response structures
            statuses = None
            if "response" in result and isinstance(result["response"], dict):
                data = result["response"].get("data", {})
                statuses = data.get("statuses") if isinstance(data, dict) else None
            elif isinstance(result.get("response"), list):
                statuses = result["response"]
            elif isinstance(result, list):
                statuses = result
            
            if statuses and isinstance(statuses, list) and len(statuses) > 0:
                status = statuses[0]
                if "filled" in status:
                    f = status["filled"]
                    return {"success": True, "order_id": f.get("oid"), "avg_price": f.get("avgPx")}
                if "resting" in status:
                    return {"success": True, "order_id": status["resting"].get("oid"), "status": "resting"}
                if "error" in status:
                    return {"success": False, "error": status["error"]}
            
            err = result.get("response", {}).get("data", {}).get("error", "Unknown")
            return {"success": False, "error": err}
            
        except Exception as e:
            logger.error(f"❌ Order failed: {e}")
            return {"success": False, "error": str(e)}


# =============================================================================
# LEGACY WRAPPER — Matches main.py expectations
# =============================================================================
_executor = None

def _get_executor(private_key: str | None = None, chat_id: int | None = None):
    global _executor
    if private_key:
        # Multi-user mode: create new executor with user's key (not singleton)
        return HLExecutor(private_key=private_key, chat_id=chat_id)
    if _executor is None:
        # Single-user fallback: create singleton with global env var
        _executor = HLExecutor()
    return _executor

def execute_hl_order(coin: str, side: str, size: float, limit_px: Optional[float] = None, **kwargs) -> Dict:
    """Async wrapper — runs place_order in thread to avoid event loop conflicts."""
    import asyncio as _aio
    try:
        executor = _get_executor()
        _strategy = kwargs.get("strategy", "SIGNAL")
        _regime = kwargs.get("regime", "AUTO")
        
        # Delegate to the class method which handles all execution logic
        result = executor.place_order(
            coin=coin,
            side=side,
            size=size,
            limit_price=limit_px,
            order_type=kwargs.get("order_type", "Limit"),
            reduce_only=kwargs.get("reduce_only", False)
        )
        # Attach strategy metadata to result for downstream consumers
        if result and isinstance(result, dict):
            result["_strategy"] = _strategy
            result["_regime"] = _regime
        logger.info(f"📦 Order result: {result}")
        
        # 📊 --- SMART TRADE RECORDING ---
        if result and result.get("success"):
            try:
                from core.performance_tracker import get_performance_tracker
                import core.state as state
                tracker = get_performance_tracker()
                price = float(result.get("avg_price", limit_px or 0))
                
                if kwargs.get("reduce_only", False):
                    # THIS IS A CLOSING TRADE
                    pos = state.OPEN_POSITIONS.get(coin)
                    if pos:
                        # 1. Record directly to state history (works even for existing positions!)
                        state.record_closed_trade(
                            asset=coin, side=pos.get("side", side), entry=pos.get("entry", price),
                            exit_price=price, size=size, close_reason="Exit",
                            strategy=kwargs.get("strategy", "AI ensemble"), 
                            regime=kwargs.get("regime", "RANGING")
                        )
                        # 2. Update tracker if it happens to be there
                        tracker.record_close_trade(asset=coin, exit_price=price, close_reason="Exit")
                    else:
                        logger.warning(f"⚠️ Closing trade for {coin} but not found in OPEN_POSITIONS")
                else:
                    # THIS IS AN OPENING TRADE
                    tracker.record_open_trade(
                        asset=coin, side=side, entry=price, size=size, 
                        strategy=kwargs.get("strategy", "AI ensemble"), 
                        regime=kwargs.get("regime", "RANGING")
                    )
            except Exception as e:
                logger.warning(f"⚠️ Failed to record trade in tracker: {e}")
        # ---------------------------------

        return result or {"success": False, "error": "None returned"}
    except Exception as e:
        logger.error(f"❌ execute_hl_order error: {e}")
        return {"success": False, "error": str(e)}
