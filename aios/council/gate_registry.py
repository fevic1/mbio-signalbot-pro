from aios.core.execution import ExecutionEngine

class GateRegistry:


    def __init__(self):

        self.gates = []



    def register(
        self,
        gate,
    ):

        self.gates.append(
            gate
        )



    def run(
        self,
        context,
    ):

        results = []

        passed = True


        for gate in self.gates:

            result = gate.check(
                context
            )

            results.append(
                result
            )


            if not result["passed"]:

                passed = False


        return {

            "passed":
                passed,

            "results":
                results,

        }
