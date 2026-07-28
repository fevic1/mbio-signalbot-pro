from datetime import datetime, timezone
import uuid


class RuntimeTransactionManager:

    def __init__(self):
        self._transactions = {}

    def begin(self, name: str):
        transaction_id = str(uuid.uuid4())

        self._transactions[transaction_id] = {
            "id": transaction_id,
            "name": name,
            "state": "started",
            "created": datetime.now(
                timezone.utc
            ).isoformat(),
        }

        return self._transactions[transaction_id]

    def commit(self, transaction_id: str):
        transaction = self._transactions[transaction_id]

        transaction["state"] = "committed"
        transaction["finished"] = datetime.now(
            timezone.utc
        ).isoformat()

        return transaction

    def rollback(self, transaction_id: str):
        transaction = self._transactions[transaction_id]

        transaction["state"] = "rolled_back"
        transaction["finished"] = datetime.now(
            timezone.utc
        ).isoformat()

        return transaction

    def get(self, transaction_id: str):
        return self._transactions.get(transaction_id)

    def all(self):
        return tuple(self._transactions.values())

    def clear(self):
        self._transactions.clear()

    def __len__(self):
        return len(self._transactions)
