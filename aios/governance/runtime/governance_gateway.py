class GovernanceGateway:

    def __init__(
        self,
        permission_manager,
        approval_manager,
        audit_logger,
    ):
        self.permission_manager = permission_manager
        self.approval_manager = approval_manager
        self.audit_logger = audit_logger


    def request(
        self,
        action,
        agent,
        permission,
        payload=None,
    ):

        permission_ok = self.permission_manager.check(
            permission,
            permission,
        )

        if not permission_ok:

            result = {
                "allowed": False,
                "status": "denied",
                "reason": "insufficient permission",
            }

            self.audit_logger.record(
                agent,
                action,
                result,
            )

            return result


        if permission in ("execute", "critical"):

            request = self.approval_manager.create_request(
                action,
                agent,
                payload,
            )

            result = {
                "allowed": False,
                "status": "pending",
                "approval_id": request["id"],
            }

            self.audit_logger.record(
                agent,
                action,
                result,
            )

            return result


        result = {
            "allowed": True,
            "status": "approved",
        }

        self.audit_logger.record(
            agent,
            action,
            result,
        )

        return result


    def approve(
        self,
        approval_id,
        approved_by="human",
    ):

        approved = self.approval_manager.approve(
            approval_id,
            approved_by,
        )

        request = self.approval_manager.get(
            approval_id
        )

        result = {
            "approved": approved,
            "approval_id": approval_id,
        }

        if request:
            self.audit_logger.record(
                request["requested_by"],
                request["action"],
                {
                    "status": "approved",
                    "approved_by": approved_by,
                    "approval_id": approval_id,
                },
            )

        return result
