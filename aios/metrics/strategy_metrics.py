from collections import defaultdict


class StrategyMetrics:

    def __init__(self):

        self.records = []


    def add_trade(
        self,
        trade: dict,
    ):

        self.records.append(
            trade
        )


    def summary(
        self,
        strategy=None,
    ):

        trades = self.records

        if strategy:
            trades = [
                t for t in trades
                if t.get("strategy") == strategy
            ]

        if not trades:
            return {
                "trades": 0,
                "wins": 0,
                "losses": 0,
                "win_rate": 0,
                "average_pnl": 0,
                "expectancy": 0,
            }


        pnls = [
            float(
                t.get("pnl", 0)
            )
            for t in trades
        ]

        wins = [
            p for p in pnls
            if p > 0
        ]

        losses = [
            p for p in pnls
            if p <= 0
        ]


        win_rate = len(wins) / len(pnls)


        average_win = (
            sum(wins) / len(wins)
            if wins
            else 0
        )

        average_loss = (
            abs(sum(losses) / len(losses))
            if losses
            else 0
        )


        expectancy = (
            (win_rate * average_win)
            -
            ((1 - win_rate) * average_loss)
        )


        return {
            "trades": len(pnls),
            "wins": len(wins),
            "losses": len(losses),
            "win_rate": round(win_rate, 4),
            "average_pnl": round(
                sum(pnls) / len(pnls),
                6,
            ),
            "expectancy": round(
                expectancy,
                6,
            ),
        }
