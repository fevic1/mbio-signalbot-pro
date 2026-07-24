from datetime import datetime, timezone
import uuid


class ExecutionMemory:


    def __init__(self):

        self.records = []



    def store(
        self,
        execution,
    ):

        record = {
            "id": str(uuid.uuid4()),
            "execution": execution,
            "timestamp": (
                datetime.now(
                    timezone.utc
                ).isoformat()
            ),
        }


        self.records.append(
            record
        )


        return record



    def history(
        self,
    ):

        return self.records



    def find_agent_history(
        self,
        agent_name,
    ):

        return [
            record
            for record in self.records
            if record["execution"].get(
                "agent"
            ) == agent_name
        ]
