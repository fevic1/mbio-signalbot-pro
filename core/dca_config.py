"""MBIO DCA Governor - canonical configuration."""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass(frozen=True)
class DCAAdaptiveConfig:
    enabled: bool = True
    order_ttl_seconds: int = 300
    max_order_age_seconds: int = 45
    market_move_trigger_pct: float = 0.25
    min_reprice_distance_pct: float = 0.15


@dataclass(frozen=True)
class DCAAccelerationConfig:
    enabled: bool = False
    max_multiplier: float = 3.0
    confidence_threshold: float = 0.75
    learner_score_threshold: float = 0.60
    max_accelerated_levels: int = 3
    require_risk_budget: bool = True


@dataclass(frozen=True)
class DCAProtectionConfig:
    profit_target_pct: Optional[float] = 15.0
    profit_ratchet_enabled: bool = True
    profit_ratchet_dollars: float = 1.0
    harvest_pct: float = 25.0
    min_harvest_profit_usd: float = 1.0
    trailing_exit_enabled: bool = True
    trailing_exit_pct: float = 5.0
    bounce_to_harvest_pct: float = 8.0
    profit_to_protect_pct: float = 15.0
    deterioration_pct: float = 5.0


@dataclass(frozen=True)
class DCAGuardrailConfig:
    pause: bool = False
    consecutive_loss_breaker: int = 5
    risk_budget_usd: Optional[float] = None
    max_levels: int = 10
    max_position_size_usd: Optional[float] = None
    max_single_add_usd: Optional[float] = None


@dataclass(frozen=True)
class DCAModeConfig:
    recovery_spacing_multiplier: float = 1.0
    recovery_size_multiplier: float = 1.0
    harvest_spacing_multiplier: float = 0.75
    harvest_size_multiplier: float = 1.0
    hybrid_spacing_multiplier: float = 1.0
    hybrid_size_multiplier: float = 1.0


@dataclass(frozen=True)
class DCAConfig:
    levels: int = 6
    spacing_pct: float = 2.0
    size_multiplier: float = 1.3
    base_order_size: float = 100.0

    adaptive: DCAAdaptiveConfig = field(default_factory=DCAAdaptiveConfig)
    acceleration: DCAAccelerationConfig = field(default_factory=DCAAccelerationConfig)
    protection: DCAProtectionConfig = field(default_factory=DCAProtectionConfig)
    guardrails: DCAGuardrailConfig = field(default_factory=DCAGuardrailConfig)
    modes: DCAModeConfig = field(default_factory=DCAModeConfig)

    default_mode: str = "HYBRID"

    def validate(self) -> List[str]:
        errors: List[str] = []

        if self.levels < 1:
            errors.append("levels must be >= 1")
        if self.spacing_pct <= 0 or self.spacing_pct >= 100:
            errors.append("spacing_pct must be > 0 and < 100")
        if self.size_multiplier < 1.0:
            errors.append("size_multiplier must be >= 1.0")
        if self.base_order_size <= 0:
            errors.append("base_order_size must be > 0")
        if self.default_mode not in {"RECOVERY", "HARVEST", "HYBRID"}:
            errors.append("default_mode must be RECOVERY, HARVEST, or HYBRID")

        p = self.protection
        if p.profit_ratchet_dollars <= 0:
            errors.append("profit_ratchet_dollars must be > 0")
        if not 0 < p.harvest_pct <= 100:
            errors.append("harvest_pct must be > 0 and <= 100")
        if p.min_harvest_profit_usd < 0:
            errors.append("min_harvest_profit_usd must be >= 0")
        if p.trailing_exit_pct <= 0:
            errors.append("trailing_exit_pct must be > 0")
        if p.bounce_to_harvest_pct <= 0:
            errors.append("bounce_to_harvest_pct must be > 0")
        if p.profit_to_protect_pct <= 0:
            errors.append("profit_to_protect_pct must be > 0")
        if p.deterioration_pct <= 0:
            errors.append("deterioration_pct must be > 0")

        g = self.guardrails
        if g.consecutive_loss_breaker < 1:
            errors.append("consecutive_loss_breaker must be >= 1")
        if g.max_levels < 1:
            errors.append("max_levels must be >= 1")

        a = self.acceleration
        if a.max_multiplier < 1.0:
            errors.append("max_multiplier must be >= 1.0")
        if a.max_accelerated_levels < 0:
            errors.append("max_accelerated_levels must be >= 0")
        if not 0 <= a.confidence_threshold <= 1:
            errors.append("confidence_threshold must be between 0 and 1")
        if not 0 <= a.learner_score_threshold <= 1:
            errors.append("learner_score_threshold must be between 0 and 1")

        return errors

    def assert_valid(self) -> None:
        errors = self.validate()
        if errors:
            raise ValueError("Invalid DCA configuration: " + "; ".join(errors))
