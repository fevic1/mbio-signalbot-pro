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
