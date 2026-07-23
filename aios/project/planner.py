from aios.agents import DynamicAgentFactory
from .decomposer import GoalDecomposer
from .graph.builder import TaskGraphBuilder


class ProjectPlanner:

    def __init__(self):

        self.decomposer = GoalDecomposer()
        self.graph = TaskGraphBuilder()
        self.agent_factory = DynamicAgentFactory()


    def generate(self, project):

        project = self.decomposer.decompose(project)

        for milestone in project.milestones:
            milestone.agent = self.agent_factory.build(milestone)

        project = self.graph.build(project)

        return project
