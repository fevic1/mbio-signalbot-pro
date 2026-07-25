from .base import IntegrityGuard
import importlib


class DependencyGuard(IntegrityGuard):


    name = "dependency"



    def check(self):

        modules = [

            "aios.council",

            "aios.governance",

            "aios.audit",

        ]


        failures = []


        for module in modules:

            try:

                importlib.import_module(
                    module
                )

            except Exception as e:

                failures.append(
                    {
                        "module": module,
                        "error": str(e),
                    }
                )


        return {

            "guard":
                self.name,

            "passed":
                len(failures) == 0,

            "failures":
                failures,

        }
