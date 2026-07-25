from .base import IntegrityGuard
from pathlib import Path


class ArchitectureGuard(IntegrityGuard):


    name = "architecture"



    def check(self):

        required = [

            "aios/council",

            "aios/governance",

            "aios/audit",

            "aios/policies",

        ]


        missing = [

            item

            for item in required

            if not Path(item).exists()

        ]


        return {

            "guard":
                self.name,

            "passed":
                len(missing) == 0,

            "missing":
                missing,

        }
