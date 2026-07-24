from collections import defaultdict


class PerformanceTracker:

    def __init__(self):

        self.strategy = defaultdict(
            list
        )

        self.asset = defaultdict(
            list
        )


    def record(
        self,
        trade: dict,
    ):

        strategy = trade.get(
            "strategy",
            "UNKNOWN",
        )

        asset = trade.get(
            "asset",
            "UNKNOWN",
        )

        self.strategy[strategy].append(
            trade
        )

        self.asset[asset].append(
            trade
        )


    def strategy_performance(
        self,
    ):

        return {
            key: self._calculate(
                trades
            )
            for key, trades in self.strategy.items()
        }


    def asset_performance(
        self,
    ):

        return {
            key: self._calculate(
                trades
            )
            for key, trades in self.asset.items()
        }


    def _calculate(
        self,
        trades,
    ):

        pnl = [
            float(
                t.get("pnl", 0)
            )
            for t in trades
        ]

        wins = [
            x for x in pnl
            if x > 0
        ]

        return {
            "trades": len(pnl),
            "win_rate": (
                len(wins) / len(pnl)
                if pnl
                else 0
            ),
            "total_pnl": sum(pnl),
        }
