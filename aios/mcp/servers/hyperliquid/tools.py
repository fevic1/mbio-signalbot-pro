
from .adapter import HyperliquidAdapter

hl = HyperliquidAdapter()

TOOLS = {

    "hl_market_info":
        lambda a: hl.market_info(),

    "hl_all_mids":
        lambda a: hl.all_mids(),

    "hl_orderbook":
        lambda a: hl.orderbook(
            a["coin"]
        ),

    "hl_candles":
        lambda a: hl.candles(
            a["coin"],
            a["interval"],
            a["start"],
            a["end"],
        ),

    "hl_funding":
        lambda a: hl.funding(),

    "hl_open_orders":
        lambda a: hl.open_orders(
            a["address"]
        ),

    "hl_positions":
        lambda a: hl.positions(
            a["address"]
        ),

    "hl_balances":
        lambda a: hl.balances(
            a["address"]
        ),

    "hl_place_order":
        lambda a: hl.place_order(**a),

    "hl_cancel_order":
        lambda a: hl.cancel_order(
            a["coin"],
            a["oid"],
        ),
}
