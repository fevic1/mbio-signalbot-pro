"""
state/state_manager.py — Redis-based state management with atomic operations.
Falls back to in-memory if Redis is unavailable.
"""
import json
import logging
import os
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Dict, Optional

import redis

logger = logging.getLogger(__name__)

# Redis configuration
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)

class StateManager:
    """Redis-based state manager with fallback to in-memory."""
    
    def __init__(self):
        self.use_redis = False
        self.redis_client = None
        self.memory_state = {
            'positions': {},
            'signals': {},
            'daily_pnl': Decimal('0'),
            'daily_pnl_reset_date': datetime.now(timezone.utc).strftime("%Y-%m-%d")
        }
        
        # Try to connect to Redis
        try:
            self.redis_client = redis.Redis(
                host=REDIS_HOST,
                port=REDIS_PORT,
                db=REDIS_DB,
                password=REDIS_PASSWORD,
                decode_responses=True,
                socket_connect_timeout=5
            )
            self.redis_client.ping()
            self.use_redis = True
            logger.info(f"✅ Redis connected: {REDIS_HOST}:{REDIS_PORT}")
        except Exception as e:
            logger.warning(f"⚠️ Redis unavailable, using in-memory state: {e}")
            self.use_redis = False
    
    # Position management
    def set_position(self, symbol: str, position: Dict[str, Any]) -> None:
        """Store position with 24h TTL."""
        if self.use_redis:
            key = f"position:{symbol}"
            self.redis_client.setex(key, 86400, json.dumps(position, default=str))
        else:
            self.memory_state['positions'][symbol] = position
    
    def get_position(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Retrieve position."""
        if self.use_redis:
            key = f"position:{symbol}"
            data = self.redis_client.get(key)
            return json.loads(data) if data else None
        else:
            return self.memory_state['positions'].get(symbol)
    
    def get_all_positions(self) -> Dict[str, Dict[str, Any]]:
        """Get all open positions."""
        if self.use_redis:
            positions = {}
            for key in self.redis_client.scan_iter("position:*"):
                symbol = key.replace("position:", "")
                data = self.redis_client.get(key)
                if data:
                    positions[symbol] = json.loads(data)
            return positions
        else:
            return self.memory_state['positions'].copy()
    
    def delete_position(self, symbol: str) -> None:
        """Remove position."""
        if self.use_redis:
            self.redis_client.delete(f"position:{symbol}")
        else:
            self.memory_state['positions'].pop(symbol, None)
    
    # Signal cache
    def set_signal_cache(self, symbol: str, signal_data: Dict[str, Any]) -> None:
        """Cache signal with 1h TTL."""
        if self.use_redis:
            key = f"signal_cache:{symbol}"
            self.redis_client.setex(key, 3600, json.dumps(signal_data, default=str))
        else:
            self.memory_state['signals'][symbol] = signal_data
    
    def get_signal_cache(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get cached signal."""
        if self.use_redis:
            key = f"signal_cache:{symbol}"
            data = self.redis_client.get(key)
            return json.loads(data) if data else None
        else:
            return self.memory_state['signals'].get(symbol)
    
    # Daily PnL (atomic operations)
    def add_pnl(self, amount: float) -> Decimal:
        """Atomically add to daily PnL."""
        if self.use_redis:
            new_value = self.redis_client.incrbyfloat("daily_pnl", amount)
            return Decimal(str(new_value))
        else:
            self.memory_state['daily_pnl'] += Decimal(str(amount))
            return self.memory_state['daily_pnl']
    
    def get_daily_pnl(self) -> Decimal:
        """Get current daily PnL."""
        if self.use_redis:
            value = self.redis_client.get("daily_pnl")
            return Decimal(value) if value else Decimal('0')
        else:
            return self.memory_state['daily_pnl']
    
    def reset_daily_pnl_if_new_day(self) -> None:
        """Reset daily PnL if it's a new day."""
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        
        if self.use_redis:
            stored_date = self.redis_client.get("daily_pnl_reset_date")
            if stored_date != today:
                self.redis_client.set("daily_pnl", "0")
                self.redis_client.set("daily_pnl_reset_date", today)
                logger.info(f"🔄 Daily PnL reset for {today}")
        else:
            if self.memory_state['daily_pnl_reset_date'] != today:
                self.memory_state['daily_pnl'] = Decimal('0')
                self.memory_state['daily_pnl_reset_date'] = today
                logger.info(f"🔄 Daily PnL reset for {today}")
    
    def is_drawdown_halt(self, threshold: float) -> bool:
        """Check if drawdown halt is triggered."""
        daily_pnl = float(self.get_daily_pnl())
        return daily_pnl <= threshold

# Global instance
_state_manager = None

def get_state_manager() -> StateManager:
    """Get or create state manager instance."""
    global _state_manager
    if _state_manager is None:
        _state_manager = StateManager()
    return _state_manager
