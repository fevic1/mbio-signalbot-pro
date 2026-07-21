"""
Dynamic Grid & DCA Optimizer
Calculates optimal strategy parameters based on real-time GTJA-191 regime scores.
Strictly non-hardcoded: all multipliers are derived dynamically from market volatility and momentum.
"""
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class GridOptimizer:
    """
    Dynamically calculates grid range and node density based on factor scores.
    """
    def __init__(self, base_range_pct: float = 0.05, base_nodes: int = 10):
        # Base parameters act as the mathematical anchor, but final output is dynamic.
        self.base_range_pct = base_range_pct 
        self.base_nodes = base_nodes

    def calculate_parameters(self, regime_data: Dict[str, Any], current_price: float) -> Optional[Dict[str, float]]:
        """
        Calculates dynamic grid parameters.
        
        Args:
            regime_data: Output from RegimeAnalyzer.analyze()
            current_price: Current asset price
            
        Returns:
            Dict with 'lower_price', 'upper_price', 'node_count', 'investment_per_node'
        """
        if not regime_data or current_price <= 0:
            return None

        volatility = regime_data.get('volatility', 0.5)
        momentum = regime_data.get('momentum', 0.5)
        confidence = regime_data.get('confidence', 0.5)

        # 1. Dynamic Range Calculation
        # Higher volatility = wider range. We use a non-linear scale to prevent extreme ranges.
        # Formula: base_range * (1 + sqrt(volatility))
        dynamic_range_pct = self.base_range_pct * (1 + (volatility ** 0.5))
        
        # 2. Dynamic Node Calculation
        # Higher confidence in the regime = more nodes to capture fills. 
        # High momentum (trending) = fewer nodes to avoid premature exhaustion.
        # Formula: base_nodes * (1 + confidence) * (1 - (momentum * 0.5))
        dynamic_nodes = self.base_nodes * (1 + confidence) * (1 - (momentum * 0.5))
        
        # Ensure we never have less than 2 nodes (mathematical minimum for a grid)
        node_count = max(2, int(round(dynamic_nodes)))

        # 3. Calculate Price Bounds
        half_range = current_price * (dynamic_range_pct / 2)
        lower_price = current_price - half_range
        upper_price = current_price + half_range

        return {
            "lower_price": round(lower_price, 8),
            "upper_price": round(upper_price, 8),
            "node_count": node_count,
            "range_percentage": round(dynamic_range_pct * 100, 4)
        }

class DCAOptimizer:
    """
    Dynamically calculates DCA safety order spacing and sizing.
    """
    def __init__(self, base_spacing_pct: float = 0.02):
        self.base_spacing_pct = base_spacing_pct

    def calculate_spacing(self, regime_data: Dict[str, Any]) -> float:
        """
        Calculates dynamic DCA spacing based on volatility.
        Higher volatility = wider spacing between safety orders.
        """
        if not regime_data:
            return self.base_spacing_pct

        volatility = regime_data.get('volatility', 0.5)
        
        # Formula: base_spacing * (1 + volatility)
        dynamic_spacing = self.base_spacing_pct * (1 + volatility)
        
        return round(dynamic_spacing, 6)

def validate_and_fallback(
    dynamic_params: Optional[Dict[str, float]], 
    static_params: Dict[str, float],
    asset: str
) -> Dict[str, float]:
    """
    HARD CHECK: Validates dynamic parameters. If they are invalid or None, 
    instantly reverts to static parameters to prevent execution errors.
    """
    # 1. Check if dynamic calculation failed or returned None
    if not dynamic_params:
        logger.warning(f"[HARD CHECK FAILED] Dynamic params returned None for {asset}. Reverting to static.")
        return static_params

    # 2. Mathematical Validation
    lower = dynamic_params.get('lower_price', 0)
    upper = dynamic_params.get('upper_price', 0)
    nodes = dynamic_params.get('node_count', 0)

    if lower <= 0 or upper <= 0:
        logger.critical(f"[HARD CHECK FAILED] Invalid price bounds for {asset} (lower={lower}, upper={upper}). Reverting to static.")
        return static_params
        
    if lower >= upper:
        logger.critical(f"[HARD CHECK FAILED] Lower bound >= Upper bound for {asset}. Reverting to static.")
        return static_params
        
    if nodes < 2:
        logger.critical(f"[HARD CHECK FAILED] Node count < 2 for {asset} (nodes={nodes}). Reverting to static.")
        return static_params

    # 3. Success: Log the delta for audit purposes
    logger.info(
        f"[HARD CHECK PASSED] {asset}: Using dynamic params. "
        f"Range: {lower:.2f} - {upper:.2f} (Static was: {static_params.get('lower_price'):.2f} - {static_params.get('upper_price'):.2f}). "
        f"Nodes: {nodes} (Static was: {static_params.get('node_count')})."
    )
    return dynamic_params
