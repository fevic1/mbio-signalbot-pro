import json
import os
from pathlib import Path
import tempfile


class AtomicWriter:


    def write(
        self,
        path,
        data,
    ):

        path = Path(path)

        payload = json.dumps(
            data,
            indent=2,
        )


        with tempfile.NamedTemporaryFile(
            "w",
            delete=False,
            dir=path.parent,
        ) as tmp:

            tmp.write(
                payload
            )

            tmp.flush()

            os.fsync(
                tmp.fileno()
            )

            temp_name = tmp.name


        os.replace(
            temp_name,
            path,
        )
