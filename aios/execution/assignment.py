from aios.core.execution.runner import ExecutionRunner

from typing import List, Dict


class TaskAssignmentEngine(ExecutionRunner):


    def assign(
        self,
        task_graph: List[Dict],
        mission_team,
    ):

        assignments = []


        agents = mission_team.agents


        for node in task_graph:

            milestone = node["milestone"]

            selected = self._select_agent(
                milestone,
                agents,
            )


            assignments.append(
                {
                    "milestone": milestone,
                    "agent": selected,
                    "task": node["tasks"][0],
                    "status": "assigned",
                }
            )


        return assignments



    def _select_agent(
        self,
        milestone,
        agents,
    ):

        name = milestone.lower()


        for agent in agents:

            role = agent.role.lower()


            if (
                "research" in name
                and "research" in role
            ):
                return agent


            if (
                "architecture" in name
                and "architect" in role
            ):
                return agent


            if (
                "development" in name
                and "coder" in role
            ):
                return agent


            if (
                "testing" in name
                and (
                    "tester" in role
                    or "reviewer" in role
                )
            ):
                return agent


        return agents[0] if agents else None
