from execution.execution_labels import ExecutionLabel
from execution.order_types import OrderType


class ExecutionValidationError(Exception):
    pass



class ExecutionValidator:


    def validate(
        self,
        intent,
    ):


        if not intent.label:

            raise ExecutionValidationError(
                "Execution label required"
            )


        if intent.size <= 0:

            raise ExecutionValidationError(
                "Invalid order size"
            )


        if intent.label in (
            ExecutionLabel.QT_ENTRY,
            ExecutionLabel.QT_EXIT,
            ExecutionLabel.QT_REDUCE,
            ExecutionLabel.QT_EMERGENCY_CLOSE,
        ):

            if intent.order_type != OrderType.MARKET:

                raise ExecutionValidationError(
                    "Quick Ticket requires MARKET execution"
                )


        if intent.label in (
            ExecutionLabel.DCA_ENTRY,
            ExecutionLabel.DCA_ADD,
            ExecutionLabel.DCA_EXIT,
        ):

            if intent.order_type != OrderType.LIMIT:

                raise ExecutionValidationError(
                    "DCA requires LIMIT execution"
                )


        return {

            "valid": True,

            "label":
                intent.label.value,

        }
