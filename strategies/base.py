import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class BaseStrategy(ABC):
    def __init__(self, name: str):
        self.name = name
        self.wins = 0
        self.losses = 0
        self.total_pnl = 0.0

    @abstractmethod
    def calculate_signal(self, data: dict) -> tuple:
        pass

    def update_performance(self, pnl_pct: float):
        self.total_pnl += pnl_pct
        if pnl_pct > 0:
            self.wins += 1
        else:
            self.losses += 1

    def win_rate(self) -> float:
        total = self.wins + self.losses
        return self.wins / total if total > 0 else 0.5

    def avg_pnl(self) -> float:
        total = self.wins + self.losses
        return self.total_pnl / total if total > 0 else 0.0
