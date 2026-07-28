from dataclasses import dataclass

from aios.core.models import Relationship


@dataclass(slots=True)
class Relation(Relationship):
    @property
    def relation(self):
        return self.kind

    @relation.setter
    def relation(self, value):
        self.kind = value
