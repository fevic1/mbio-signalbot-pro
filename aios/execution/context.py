from datetime import datetime
import uuid
import json


class ExecutionContext:

    def __init__(
        self,
        task,
        event_bus=None,
    ):

        self.id = str(uuid.uuid4())

        self.created = datetime.utcnow().isoformat()

        self.task = task

        self.results = {}

        self.memory = {}

        self.metadata = {}

        self.events = []

        self.status = "created"

        self.agent_status = {}

        self.event_bus = event_bus


    def emit(
        self,
        event_type,
        payload=None,
    ):

        event = {
            "event": event_type,
            "payload": payload or {},
            "time": datetime.utcnow().isoformat(),
        }

        self.add_event(event)

        if self.event_bus:

            from aios.events import Event

            self.event_bus.publish(
                Event(
                    event_type,
                    payload or {},
                )
            )


    def start(self):

        self.status = "running"

        self.emit(
            "execution_started"
        )


    def complete(self):

        self.status = "completed"

        self.emit(
            "execution_completed"
        )


    def fail(
        self,
        error,
    ):

        self.status = "failed"

        self.emit(
            "execution_failed",
            {
                "error": str(error)
            }
        )


    def add_result(
        self,
        agent,
        result,
    ):

        self.results[agent] = result

        self.agent_status[agent] = "completed"

        self.emit(
            "agent_completed",
            {
                "agent": agent
            }
        )


    def get_result(
        self,
        agent,
    ):

        return self.results.get(agent)


    def add_event(
        self,
        event,
    ):

        self.events.append(event)


    def set_metadata(
        self,
        key,
        value,
    ):

        self.metadata[key] = value


    def get_metadata(
        self,
        key,
        default=None,
    ):

        return self.metadata.get(
            key,
            default,
        )


    def _serialize(
        self,
        data,
    ):

        try:

            json.dumps(data)

            return data

        except TypeError:

            return str(data)


    def snapshot(self):

        return {
            "id": self.id,

            "created": self.created,

            "status": self.status,

            "task": self._serialize(
                self.task
            ),

            "results": self._serialize(
                self.results
            ),

            "metadata": self._serialize(
                self.metadata
            ),

            "agent_status": self.agent_status,

            "events": self.events,
        }
