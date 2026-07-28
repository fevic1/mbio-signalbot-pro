from aios.core.identifiable import Identifiable

from .models import ProjectOperationResult


class AutonomousProjectManager(Identifiable):


    def __init__(
        self,
        health_monitor,
        decision_engine,
        planner=None,
    ):

        self.health_monitor = health_monitor

        self.decision_engine = decision_engine

        self.planner = planner



    def evaluate(
        self,
        project,
    ):

        health = self.health_monitor.analyze(
            project
        )


        decisions = self.decision_engine.decide(
            health
        )


        actions = []


        for decision in decisions:

            actions.append(
                decision.describe()
            )


        return ProjectOperationResult(

            project_id=getattr(
                project,
                "id",
                "unknown"
            ),

            health=health.describe(),

            decisions=[
                d.describe()
                for d in decisions
            ],

            actions=actions,
        )
