from .entities import Entity
from .relations import Relation



class KnowledgeGraph:


    def __init__(self):

        self.entities = {}

        self.relations = []



    def add_entity(
        self,
        entity: Entity,
    ):

        self.entities[
            entity.id
        ] = entity


        return entity



    def connect(
        self,
        source,
        relation,
        target,
    ):

        link = Relation(
            source=source.id,
            relation=relation,
            target=target.id,
        )

        self.relations.append(
            link
        )

        return link



    def find_related(
        self,
        entity_id,
    ):

        results = []


        for relation in self.relations:

            if (
                relation.source
                ==
                entity_id
            ):

                results.append(
                    relation
                )


            if (
                relation.target
                ==
                entity_id
            ):

                results.append(
                    relation
                )


        return results



    def describe(self):

        return {

            "entities":
            [
                e.describe()
                for e in self.entities.values()
            ],

            "relations":
            [
                r.describe()
                for r in self.relations
            ],
        }
