from .models import RiskDecision


class RiskEngine:

    def __init__(
        self,
        max_position_size=1.0,
    ):

        self.max_position_size = max_position_size


    def check(
        self,
        action,
        payload=None,
    ):

        payload = payload or {}

        size = payload.get(
            "size"
        )

        if size is None:
            return RiskDecision(
                False,
                "missing position size",
                {
                    "max_position_size":
                    self.max_position_size
                },
            )


        if size <= 0:
            return RiskDecision(
                False,
                "invalid position size",
            )


        if size > self.max_position_size:
            return RiskDecision(
                False,
                "position limit exceeded",
                {
                    "max_position_size":
                    self.max_position_size
                },
            )


        return RiskDecision(
            True,
            "risk checks passed",
            {
                "max_position_size":
                self.max_position_size
            },
        )
