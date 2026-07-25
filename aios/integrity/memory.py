from .base import IntegrityGuard
from pathlib import Path
import json


class MemoryGuard(IntegrityGuard):


    name = "memory"



    def check(self):

        files = [

            ".aios/audit/decisions.json",

            ".aios/audit/sessions.json",

            ".aios/audit/governance.json",

        ]


        failures = []


        for file in files:

            path = Path(file)


            if not path.exists():

                continue


            try:

                json.loads(
                    path.read_text()
                )

            except Exception as e:

                failures.append(
                    {
                        "file": file,
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
