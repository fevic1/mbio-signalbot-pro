import json
from pathlib import Path


class RecoveryManager:


    def validate(
        self,
        path,
    ):

        path = Path(path)


        if not path.exists():

            return {

                "valid": False,

                "reason":
                    "missing",

            }


        try:

            json.loads(
                path.read_text()
            )

            return {

                "valid": True

            }


        except Exception as e:

            return {

                "valid": False,

                "reason":
                    str(e),

            }
