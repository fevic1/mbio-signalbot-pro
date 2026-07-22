from collections import defaultdict


class RecoveryManager:
    def __init__(self, max_retries: int = 3):
        self.max_retries = max_retries
        self.retries = defaultdict(int)

    def record_failure(self, task_id: str):
        self.retries[task_id] += 1

    def should_retry(self, task_id: str) -> bool:
        return self.retries[task_id] < self.max_retries

    def reset(self, task_id: str):
        self.retries.pop(task_id, None)

    def action(self, task_id: str):
        if self.should_retry(task_id):
            return "retry"
        return "escalate"
