from .schema import CURRENT_SCHEMA_VERSION


class MigrationManager:


    def migrate(
        self,
        data,
    ):

        if isinstance(
            data,
            list,
        ):

            data = {
                "schema_version": 0,
                "records": data,
            }


        version = data.get(
            "schema_version",
            0
        )


        while version < CURRENT_SCHEMA_VERSION:

            data = self._upgrade(
                version,
                data,
            )

            version += 1


        return data



    def _upgrade(
        self,
        version,
        data,
    ):

        if version == 0:

            return {

                "schema_version": 1,

                "records":
                    data.get(
                        "records",
                        []
                    )
                    if isinstance(data, dict)
                    else data,

            }


        return data
