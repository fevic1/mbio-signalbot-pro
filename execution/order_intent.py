from dataclasses import dataclass, field
from typing import Dict, Any

from execution.execution_labels import ExecutionLabel
from execution.order_types import OrderType
from execution.order_types import OrderType


@dataclass
class OrderIntent:


    coin: str

    side: str

    size: float


    label: ExecutionLabel


    strategy: str


    order_type: OrderType


    urgency: str = "NORMAL"


    metadata: Dict[str, Any] = field(
        default_factory=dict
    )



    def describe(self):

        return {

            "coin":
                self.coin,

            "side":
                self.side,

            "size":
                self.size,

            "label":
                self.label.value,

            "strategy":
                self.strategy,

            "order_type":
                self.order_type,

            "urgency":
                self.urgency,

            "metadata":
                self.metadata,

        }
