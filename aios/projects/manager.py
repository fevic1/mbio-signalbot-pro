from typing import Dict


class ProjectManager:


    def __init__(self):

        self.projects: Dict = {}


    def create(
        self,
        project,
    ):

        self.projects[
            project.id
        ] = project

        return project


    def get(
        self,
        project_id,
    ):

        return self.projects.get(
            project_id
        )


    def active_projects(
        self,
    ):

        return [
            project
            for project in self.projects.values()
            if project.status == "active"
        ]


    def summary(
        self,
    ):

        return [
            project.describe()
            for project in self.projects.values()
        ]
