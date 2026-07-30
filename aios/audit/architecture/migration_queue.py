class MigrationQueue:


    def build(self, components):

        queue = []

        for component in components:

            if component.status != "migration_pending":
                continue

            queue.append(
                {
                    "component": component.name,
                    "canonical": component.canonical,
                    "owner": component.owner,
                    "risk": component.risk,
                    "implementations": component.implementations,
                }
            )

        return sorted(
            queue,
            key=lambda x: (
                x["risk"],
                x["component"],
            )
        )
