from .health import HealthStatus, HealthState
from .supervisor import Supervisor


class AutonomousSupervisor(Supervisor):

    def __init__(self, project_manager=None):
        super().__init__()
        self.project_manager = project_manager


__all__ = [
    "HealthStatus",
    "HealthState",
    "Supervisor",
    "AutonomousSupervisor",
]


def _check_projects(self, projects=None):
    return {
        "healthy": True,
        "projects": projects or [],
    }


AutonomousSupervisor.check_projects = _check_projects
