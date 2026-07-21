from datetime import datetime
import uuid


class TaskManager:

    def __init__(
        self
    ):
        self.tasks = {}


    def create_task(
        self,
        name,
        category,
        priority="normal"
    ):

        task_id = str(uuid.uuid4())


        task = {

            "id": task_id,

            "name": name,

            "category": category,

            "priority": priority,

            "status": "pending",

            "assigned_agent": None,

            "created":
                datetime.utcnow().isoformat()
        }


        self.tasks[task_id] = task


        return task


    def assign(
        self,
        task_id,
        agent_name
    ):

        if task_id in self.tasks:

            self.tasks[task_id][
                "assigned_agent"
            ] = agent_name


            self.tasks[task_id][
                "status"
            ] = "assigned"


            return True


        return False


    def update_status(
        self,
        task_id,
        status
    ):

        if task_id in self.tasks:

            self.tasks[task_id][
                "status"
            ] = status

            return True


        return False


    def get_task(
        self,
        task_id
    ):

        return self.tasks.get(task_id)


    def list_tasks(
        self
    ):

        return list(
            self.tasks.values()
        )
