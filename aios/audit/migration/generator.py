from .models import MigrationManifest


class MigrationManifestGenerator:


    def generate(self, components):

        manifests = []

        for component in components:

            if component.status != "migration_pending":
                continue

            manifests.append(
                MigrationManifest(
                    component=component.name,
                    canonical=component.canonical,
                    owner=component.owner,
                    risk=component.risk,
                    implementations=component.implementations,
                )
            )

        return manifests
