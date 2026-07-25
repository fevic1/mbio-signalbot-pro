from .query import AuditQuery
from .models import AuditRecord
from .storage import AuditStorage


class AuditLogger:


    def __init__(self):

        self.storage = AuditStorage()

        self.query = AuditQuery(
            self.storage
    )


    def record(
        self,
        session,
        decision,
    ):

        record = AuditRecord(

            session=session.describe(),

            decision=decision,

        )


        data = record.describe()


        self.storage.append(
            "decisions",
            data,
        )


        self.storage.append(
            "sessions",
            session.describe(),
        )


        if "governance" in decision:

            self.storage.append(
                "governance",
                decision["governance"],
            )


        return data



    def history(self):

        return self.storage.read(
            "decisions"
        )
