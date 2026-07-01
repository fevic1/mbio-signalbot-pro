from hyperliquid import HyperliquidSync
import os

def get_account_state(info, wallet):
    """
    Fetch account state using the HyperliquidSync.info object.
    Returns: (account_value, free_collateral, positions, orders)
    """
    try:
        # Use the info object from HyperliquidSync
        account = info.user_state(wallet)
        
        # Extract data
        margin_summary = account.get('marginSummary', {})
        wallet_balance = float(margin_summary.get('accountValue', 0))
        free_collateral = float(account.get('withdrawable', 0))
        
        # Parse positions
        positions = []
        for pos in account.get('assetPositions', []):
            p = pos.get('position', {})
            if p:
                szi = float(p.get('szi', 0))
                positions.append({
                    'coin': p.get('coin'),
                    'side': 'LONG' if szi > 0 else 'SHORT',
                    'size': abs(szi),
                    'entry_px': float(p.get('entryPx', 0)),
                    'liquidationPx': float(p.get('liquidationPx', 0)) if p.get('liquidationPx') else 0
                })
        
        # Parse orders
        orders = []
        for order in account.get('orders', []):
            orders.append({
                'coin': order.get('coin'),
                'oid': order.get('oid'),
                'sz': float(order.get('sz', 0)),
                'side': order.get('side'),
                'limitPx': float(order.get('limitPx', 0)) if order.get('limitPx') else None
            })
        
        return wallet_balance, free_collateral, positions, orders
    except Exception as e:
        print(f"⚠️ Account error: {e}")
        return 0.0, 0.0, [], []
