
from execution.hl_executor import HLExecutor

class HyperliquidAdapter:

    def __init__(self):
        self.hl = HLExecutor()

    async def market_info(self):
        return self.hl.info.meta()

    async def all_mids(self):
        return self.hl.info.all_mids()

    async def orderbook(self, coin):
        return self.hl.info.l2_snapshot(coin)

    async def candles(
        self,
        coin,
        interval,
        start,
        end,
    ):
        return self.hl.info.candles_snapshot(
            coin,
            interval,
            start,
            end,
        )

    async def funding(self):
        return self.hl.info.meta_and_asset_ctxs()

    async def open_orders(self, address):
        return self.hl.info.open_orders(address)

    async def positions(self, address):
        return self.hl.info.user_state(address)

    async def balances(self, address):
        return self.hl.info.user_state(address)

    async def place_order(self, **kwargs):
        return self.hl.place_order(**kwargs)

    async def cancel_order(
        self,
        coin,
        oid,
    ):
        return self.hl.cancel_order(
            coin,
            oid,
        )
