from aios.storage.json_backend import JSONBackend


class AuditStorage:


    def __init__(
        self,
        root=".aios/audit",
    ):

        self.backend = JSONBackend(
            root
        )



    def append(
        self,
        category,
        data,
    ):

        return self.backend.append(
            category,
            data,
        )



    def read(
        self,
        category,
    ):

        return self.backend.read(
            category
        )
