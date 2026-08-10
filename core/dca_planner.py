"""
MBIO DCA Governor — Planner

Canonical DCA planning adapter.

Responsibilities:
    - validate the supplied DCA configuration
    - construct the canonical DCA ladder through DCAManager
    - expose a stable plan representation to governor/risk components
    - update fill state without duplicating ladder mathematics

This module does NOT:
    - submit orders
    - cancel orders
    - modify exchange state
    - perform risk approval
    - execute positions

The execution engine remains the canonical execution authority.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field, replace
from decimal import Decimal
from typing import Any, Optional

from core.dca_manager import DCAManager

logger = logging.getLogger(__name__)


@dataclass
class DCALevel:
    """Normalized planner representation of one DCA level."""

    level_index: int
    price: Decimal
    size: Decimal
    filled: bool = False
    order_id: Optional[Any] = None
    placed_at: Optional[Any] = None
    size_raw: Optional[Any] = None

    @property
    def value(self) -> Decimal:
        return self.price * self.size


@dataclass
class DCAPlan:
    """
    Canonical DCA plan projection.

    This is a planner representation only. Exchange state remains owned by
    the execution/runtime layers.
    """

    asset: str
    side: str
    entry_price: Decimal
    levels: list[DCALevel]
    total_planned_size: Decimal
    total_planned_value: Decimal
    avg_entry_target: Decimal
    profit_target_price: Optional[Decimal] = None
    config_hash: Optional[str] = None

    def filled_levels(self) -> list[DCALevel]:
        return [level for level in self.levels if level.filled]

    def current_avg_entry(self) -> Decimal:
        filled = self.filled_levels()

        if not filled:
            return self.entry_price

        total_size = sum(
            (level.size for level in filled),
            Decimal("0"),
        )

        if total_size <= 0:
            return self.entry_price

        total_value = sum(
            (level.price * level.size for level in filled),
            Decimal("0"),
        )

        return total_value / total_size

    def total_filled_size(self) -> Decimal:
        return sum(
            (level.size for level in self.filled_levels()),
            Decimal("0"),
        )


class DCAPlanBuilder:
    """
    Adapter around the existing MBIO DCAManager ladder calculation.

    There is deliberately no independent spacing/multiplier calculation here.
    """

    @staticmethod
    def _config_dict(config: Any) -> dict:
        if isinstance(config, dict):
            return dict(config)

        if hasattr(config, "to_dict"):
            result = config.to_dict()
            if isinstance(result, dict):
                return result

        if hasattr(config, "__dict__"):
            return {
                key: value
                for key, value in vars(config).items()
                if not key.startswith("_")
            }

        raise TypeError(
            "DCA configuration must be a mapping, dataclass-like object, "
            "or expose to_dict()"
        )

    @classmethod
    def build(
        cls,
        asset: str,
        side: str,
        entry_price: Decimal,
        config: Any,
        current_price: Optional[Decimal] = None,
        manager: Optional[DCAManager] = None,
    ) -> DCAPlan:
        if entry_price <= 0:
            raise ValueError("entry_price must be greater than zero")

        normalized_side = str(side).upper()

        if normalized_side not in {"LONG", "SHORT", "BUY", "SELL"}:
            raise ValueError(
                f"Unsupported DCA side: {side!r}"
            )

        config_dict = cls._config_dict(config)

        manager = manager or DCAManager.__new__(DCAManager)

        levels = cls._build_levels(
            manager=manager,
            asset=asset,
            entry_price=entry_price,
            config=config_dict,
        )

        normalized_levels: list[DCALevel] = []

        for index, level in enumerate(levels):
            if not isinstance(level, dict):
                continue

            price = level.get("price")
            size = level.get("size")

            if price is None or size is None:
                continue

            normalized_levels.append(
                DCALevel(
                    level_index=int(
                        level.get(
                            "level",
                            level.get(
                                "level_index",
                                index + 1,
                            ),
                        )
                    ),
                    price=Decimal(str(price)),
                    size=Decimal(str(size)),
                    filled=bool(level.get("filled", False)),
                    order_id=level.get("order_id"),
                    placed_at=level.get("placed_at"),
                    size_raw=level.get("size_raw"),
                )
            )

        total_size = sum(
            (level.size for level in normalized_levels),
            Decimal("0"),
        )

        total_value = sum(
            (level.price * level.size for level in normalized_levels),
            Decimal("0"),
        )

        if total_size > 0:
            avg_target = total_value / total_size
        else:
            avg_target = entry_price

        profit_target = cls._profit_target(
            entry_price=entry_price,
            config=config_dict,
            side=normalized_side,
        )

        return DCAPlan(
            asset=asset,
            side=normalized_side,
            entry_price=entry_price,
            levels=normalized_levels,
            total_planned_size=total_size,
            total_planned_value=total_value,
            avg_entry_target=avg_target,
            profit_target_price=profit_target,
            config_hash=None,
        )

    @staticmethod
    def _build_levels(
        manager: DCAManager,
        asset: str,
        entry_price: Decimal,
        config: dict,
    ) -> list[dict]:
        """
        Delegate ladder construction to the existing DCAManager.

        No planner-specific spacing, multiplier, or martingale formula is
        introduced here.
        """

        levels = int(
            config.get(
                "levels",
                config.get(
                    "max_levels",
                    config.get("max_dca_levels", 3),
                ),
            )
        )

        base_size = float(
            config.get(
                "base_size",
                config.get("size", 0),
            )
        )

        if levels <= 0:
            return []

        if base_size <= 0:
            return []

        try:
            result = manager.calculate_dca_levels(
                float(entry_price),
                base_size,
                config,
            )
        except TypeError:
            logger.exception(
                "Canonical DCA level calculation rejected configuration "
                "for %s",
                asset,
            )
            raise

        if result is None:
            return []

        return list(result)

    @staticmethod
    def _profit_target(
        entry_price: Decimal,
        config: dict,
        side: str,
    ) -> Optional[Decimal]:
        target_pct = config.get(
            "profit_target_pct",
            config.get("tp_pct"),
        )

        if target_pct is None:
            return None

        target = Decimal(str(target_pct))

        if target <= 0:
            return None

        multiplier = Decimal("1") + (
            target / Decimal("100")
        )

        if side in {"SHORT", "SELL"}:
            return entry_price / multiplier

        return entry_price * multiplier


class DCAPlanner:
    """
    Single planner facade for MBIO DCA.

    All ladder mathematics are delegated to the existing DCAManager.
    """

    def __init__(
        self,
        config: Any,
        manager: Optional[DCAManager] = None,
    ) -> None:
        self.config = config
        self.manager = manager

        validate = getattr(config, "validate", None)

        if callable(validate):
            errors = validate()

            if errors:
                raise ValueError(
                    f"Invalid DCAConfig: {errors}"
                )

    def plan_entry(
        self,
        asset: str,
        side: str,
        entry_price: float,
        current_price: Optional[float] = None,
    ) -> DCAPlan:
        """Build the canonical DCA plan for a new position."""

        plan = DCAPlanBuilder.build(
            asset=asset,
            side=side,
            entry_price=Decimal(str(entry_price)),
            config=self.config,
            current_price=(
                Decimal(str(current_price))
                if current_price is not None
                else None
            ),
            manager=self.manager,
        )

        logger.info(
            "[DCA PLANNER] Built plan for %s: "
            "%d levels, total_size=%s, avg_entry_target=%s",
            asset,
            len(plan.levels),
            plan.total_planned_size,
            plan.current_avg_entry(),
        )

        return plan

    def replan_after_fill(
        self,
        plan: DCAPlan,
        filled_level_index: int,
        fill_price: float,
        fill_size: float,
    ) -> DCAPlan:
        """
        Mark a planned level as filled.

        Fill price/size are recorded for validation/logging. The planner does
        not overwrite the exchange-confirmed level price or size.
        """

        if filled_level_index < 0:
            raise ValueError(
                "filled_level_index must be non-negative"
            )

        fill_price_decimal = Decimal(str(fill_price))
        fill_size_decimal = Decimal(str(fill_size))

        if fill_price_decimal <= 0:
            raise ValueError(
                "fill_price must be greater than zero"
            )

        if fill_size_decimal <= 0:
            raise ValueError(
                "fill_size must be greater than zero"
            )

        found = False
        new_levels: list[DCALevel] = []

        for level in plan.levels:
            if level.level_index == filled_level_index:
                found = True

                if level.filled:
                    logger.warning(
                        "[DCA PLANNER] Level %s already marked filled",
                        filled_level_index,
                    )

                new_levels.append(
                    replace(
                        level,
                        filled=True,
                    )
                )
            else:
                new_levels.append(level)

        if not found:
            raise ValueError(
                f"DCA level {filled_level_index} does not exist "
                f"for {plan.asset}"
            )

        updated = replace(
            plan,
            levels=new_levels,
        )

        logger.info(
            "[DCA PLANNER] Level %s fill verified for %s: "
            "exchange_price=%s exchange_size=%s "
            "avg_entry=%s filled=%d/%d",
            filled_level_index,
            plan.asset,
            fill_price_decimal,
            fill_size_decimal,
            updated.current_avg_entry(),
            len(updated.filled_levels()),
            len(updated.levels),
        )

        return updated
