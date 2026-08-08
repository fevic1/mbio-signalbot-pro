import logging
from core.market_cache import market_cache

import core.state as state

from .manager import RecoveryModule
from core.app_context import app_context

logger = logging.getLogger(__name__)


class ExchangeRecovery(RecoveryModule):

    name = "Exchange"

    async def discover(self):
        self.executor = app_context.executor

        self.positions = market_cache.positions()
        self.orders = market_cache.orders()

        logger.info(
            "Exchange: discovered %d position(s), %d order(s)",
            len(self.positions),
            len(self.orders),
        )

    async def recover(self):

        recovered = 0

        for p in self.positions:

            asset = p.get("coin")
            if not asset:
                continue

            pos = state.OPEN_POSITIONS.setdefault(asset, {})

            pos["side"] = "BUY" if float(p.get("szi", 0)) >= 0 else "SELL"
            pos["size"] = abs(float(p.get("szi", 0)))
            pos["entry"] = float(
                p.get("entryPx", p.get("entry_price", 0))
            )
            pos["avg_entry"] = pos["entry"]

            recovered += 1

        logger.info("Exchange: recovered %d position(s)", recovered)

    async def validate(self):

        missing = []

        for p in self.positions:
            coin = p.get("coin")
            if coin not in state.OPEN_POSITIONS:
                missing.append(coin)

        if missing:
            logger.warning(
                "Exchange validation failed: %s",
                missing,
            )
        else:
            logger.info("Exchange validation OK")

    async def repair(self):

        state.save_state()
        logger.info("Exchange state persisted")