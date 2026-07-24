from dataclasses import dataclass


@dataclass(frozen=True)
class Role:

    name: str

    description: str


AIOS_OPERATOR = Role(
    name="operator",
    description=(
        "Autonomous operator responsible for "
        "planning, coordination, and execution."
    ),
)


AIOS_ADMIN = Role(
    name="administrator",
    description=(
        "Administrative authority responsible "
        "for elevated system management."
    ),
)
