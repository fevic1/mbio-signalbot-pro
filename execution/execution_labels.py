from enum import Enum


class ExecutionLabel(str, Enum):

    # Quick Ticket
    QT_ENTRY = "QT_ENTRY"
    QT_EXIT = "QT_EXIT"
    QT_REDUCE = "QT_REDUCE"
    QT_EMERGENCY_CLOSE = "QT_EMERGENCY_CLOSE"


    # DCA
    DCA_ENTRY = "DCA_ENTRY"
    DCA_ADD = "DCA_ADD"
    DCA_EXIT = "DCA_EXIT"


# Normal signal execution
    SIGNAL_ENTRY = "SIGNAL_ENTRY"
    SIGNAL_EXIT = "SIGNAL_EXIT"


def normalize_execution_label(value):
    if isinstance(value, ExecutionLabel):
        return value

    try:
        return ExecutionLabel(value)
    except ValueError:
        raise ValueError(
            f"Invalid execution label: {value}"
        )
