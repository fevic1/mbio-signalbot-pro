from collections import deque


class ExperienceReplay:

    def __init__(self, limit=1000):
        self.buffer = deque(maxlen=limit)

    def remember(self, context):
        self.buffer.append({
            "request": context.get("task_plan"),
            "reflection": context.get("reflection"),
            "verification": context.get("verification"),
            "metrics": context.get("metrics"),
            "tool_scores": context.get("tool_scores"),
            "source_trust": context.get("source_trust"),
        })

    def replay(self):
        return list(self.buffer)
