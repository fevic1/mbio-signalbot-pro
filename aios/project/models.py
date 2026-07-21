from dataclasses import dataclass, field
from typing import List, Optional
import uuid


@dataclass
class Goal:
    id: str
    title: str
    description: str = ""


@dataclass
class TaskNode:
    id: str
    name: str
    status: str = "pending"
    depends_on: List[str] = field(default_factory=list)


@dataclass
class Milestone:
    id: str
    name: str
    tasks: List[TaskNode] = field(default_factory=list)


@dataclass
class Project:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    goal: Optional[Goal] = None
    milestones: List[Milestone] = field(default_factory=list)
    status: str = "created"
