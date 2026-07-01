"""
Smart Exit Strategies Engine.
Handles partial profit taking, dynamic TP adjustment, and time-based exits.
Stateless and multi-user safe.
"""
import logging
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)

class SmartExitManager:
    """
    Manages advanced exit logic.
    """
    
    def __init__(self):
        pass

    def calculate_partial_sizes(self, total_size: float, partials: List[float]) -> List[float]:
        """
        Calculate sizes for partial exits based on percentages.
        Example: partials = [0.3, 0.3, 0.4] -> 30% at TP1, 30% at TP2, 40% at TP3.
        """
        if not partials:
            return [total_size]
            
        total_pct = sum(partials)
        if abs(total_pct - 1.0) > 0.01:
            logger.warning(f"Exit partials do not sum to 1.0 ({total_pct}), normalizing...")
            partials = [p / total_pct for p in partials]
            
        # Round sizes to reasonable precision based on asset type (simplified here)
        sizes = [total_size * p for p in partials]
        
        # Adjust the last chunk to account for floating point errors so total matches exactly
        diff = total_size - sum(sizes[:-1])
        sizes[-1] = diff
        
        return sizes

    def get_volatility_multiplier(self, regime: str, trend_strength: float) -> float:
        """
        Calculate a multiplier for TPs based on regime.
        Ranging: Tighter TPs (0.8). Trending: Wider TPs (1.2).
        """
        if regime == "RANGING":
            return 0.8
        elif regime == "TRENDING":
            # Scale up based on ADX strength (clamped)
            strength_factor = min(trend_strength / 50.0, 1.0) 
            return 1.0 + (strength_factor * 0.4) # 1.0 to 1.4
        return 1.0

    def adjust_tps_for_volatility(self, entry_price: float, base_distances: Dict[str, float], regime: str, trend_strength: float = 20.0) -> Dict[str, float]:
        """
        Adjust TP prices based on current volatility and regime.
        
        Args:
            entry_price: The entry price of the position.
            base_distances: Dict of {'tp1': 100.0, 'tp2': 200.0...} representing price distance from entry.
            regime: 'RANGING' or 'TRENDING'.
            trend_strength: ADX value or similar metric.
        """
        multiplier = self.get_volatility_multiplier(regime, trend_strength)
        adjusted = {}
        
        for key, distance in base_distances.items():
            # Apply multiplier
            new_distance = distance * multiplier
            adjusted[key] = new_distance
            
        logger.info(f"📐 Smart Exit: Regime={regime}, Multiplier={multiplier:.2f}")
        return adjusted

    def calculate_time_based_exit(self, age_hours: float, max_age_hours: float) -> bool:
        """
        Determine if a position should be closed based purely on time.
        """
        if max_age_hours <= 0:
            return False
        return age_hours >= max_age_hours
