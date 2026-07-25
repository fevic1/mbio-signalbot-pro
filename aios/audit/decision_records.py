import json
from pathlib import Path


class DecisionRecordStore:


    def __init__(
        self,
        path=".aios/audit/decision_records.json",
    ):

        self.path = Path(path)

        self.path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        if not self.path.exists():

            self.path.write_text(
                "[]"
            )



    def append(
        self,
        record,
    ):

        data = self._load()

        data.append(
            record
        )

        self.path.write_text(
            json.dumps(
                data,
                indent=2,
            )
        )

        return record



    def get(
        self,
        record_id,
    ):

        for record in self._load():

            if record.get("id") == record_id:

                return record


        return None



    def history(self):

        return self._load()



    def _load(self):

        return json.loads(
            self.path.read_text()
        )
