from .decomposer import GoalDecomposer


class ProjectPlanner:

    def __init__(self):
        self.decomposer = GoalDecomposer()

    def generate(self, project):
        return self.decomposer.decompose(project)
