from .decomposer import GoalDecomposer
from .graph.builder import TaskGraphBuilder


class ProjectPlanner:

    def __init__(self):

        self.decomposer = GoalDecomposer()
        self.graph = TaskGraphBuilder()


    def generate(self, project):

        project = self.decomposer.decompose(project)

        project = self.graph.build(project)

        return project
