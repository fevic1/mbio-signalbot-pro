from datetime import datetime
import uuid


class ApprovalManager:

    def __init__(self):
        self.requests = {}


    def create_request(
        self,
        action,
        requested_by,
        payload=None
    ):

        request_id = str(uuid.uuid4())

        request = {

            "id": request_id,

            "action": action,

            "requested_by": requested_by,

            "payload": payload or {},

            "status": "pending",

            "created_at": datetime.utcnow().isoformat(),

            "approved_at": None,

            "approved_by": None

        }

        self.requests[request_id] = request

        return request


    def approve(
        self,
        request_id,
        approved_by="human"
    ):

        request = self.requests.get(request_id)

        if not request:
            return False

        request["status"] = "approved"
        request["approved_by"] = approved_by
        request["approved_at"] = datetime.utcnow().isoformat()

        return True


    def reject(
        self,
        request_id,
        approved_by="human"
    ):

        request = self.requests.get(request_id)

        if not request:
            return False

        request["status"] = "rejected"
        request["approved_by"] = approved_by
        request["approved_at"] = datetime.utcnow().isoformat()

        return True


    def get(self, request_id):
        return self.requests.get(request_id)


    def pending(self):

        return [
            request
            for request in self.requests.values()
            if request["status"] == "pending"
        ]


    def history(self):
        return list(self.requests.values())
