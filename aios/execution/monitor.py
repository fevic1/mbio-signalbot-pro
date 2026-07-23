from datetime import datetime


class ExecutionMonitor:
    """
    Collects execution metrics.

    The Council will consume these metrics to
    detect failures, slow agents, retries and
    abnormal execution behaviour.
    """

    def __init__(self):
        self.metrics = {}

    def start(self, task_id):

        self.metrics[task_id] = {
            "started": datetime.utcnow(),
            "finished": None,
            "duration": None,
            "status": "RUNNING",
            "retries": 0,
            "error": None,
        }

    def finish(self, task_id):

        metric = self.metrics[task_id]

        metric["finished"] = datetime.utcnow()

        metric["duration"] = (
            metric["finished"] - metric["started"]
        ).total_seconds()

        metric["status"] = "COMPLETED"

    def fail(self, task_id, error):

        metric = self.metrics[task_id]

        metric["finished"] = datetime.utcnow()

        metric["duration"] = (
            metric["finished"] - metric["started"]
        ).total_seconds()

        metric["status"] = "FAILED"

        metric["error"] = str(error)

    def retry(self, task_id):

        self.metrics[task_id]["retries"] += 1

    def summary(self):

        completed = sum(
            1
            for m in self.metrics.values()
            if m["status"] == "COMPLETED"
        )

        failed = sum(
            1
            for m in self.metrics.values()
            if m["status"] == "FAILED"
        )

        running = sum(
            1
            for m in self.metrics.values()
            if m["status"] == "RUNNING"
        )

        return {
            "tasks": len(self.metrics),
            "completed": completed,
            "failed": failed,
            "running": running,
            "metrics": self.metrics,
        }


    def record_failure(
        self,
        error,
        task_id="system",
    ):
        if task_id not in self.metrics:
            self.start(task_id)

        self.fail(task_id, error)
