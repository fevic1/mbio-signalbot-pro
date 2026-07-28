#!/usr/bin/env python3

import threading
import time
import uuid


class TaskScheduler:

    def __init__(self):
        self.tasks = {}

    def once(self, delay, func, *args, **kwargs):

        task_id = str(uuid.uuid4())

        def runner():
            time.sleep(delay)
            func(*args, **kwargs)

        thread = threading.Thread(target=runner, daemon=True)
        thread.start()

        self.tasks[task_id] = {
            "type": "once",
            "thread": thread,
        }

        return task_id

    def every(self, interval, func, *args, **kwargs):

        task_id = str(uuid.uuid4())

        def runner():
            while True:
                time.sleep(interval)
                func(*args, **kwargs)

        thread = threading.Thread(target=runner, daemon=True)
        thread.start()

        self.tasks[task_id] = {
            "type": "every",
            "thread": thread,
        }

        return task_id

    def list(self):
        return {
            k: v["type"]
            for k, v in self.tasks.items()
        }


scheduler = TaskScheduler()


if __name__ == "__main__":

    def hello():
        print("tick")

    scheduler.once(1, hello)
    scheduler.every(2, hello)

    time.sleep(5)

    print(scheduler.list())
