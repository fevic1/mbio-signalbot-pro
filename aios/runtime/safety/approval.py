class ApprovalGate:

    RED_LINES = {
        "secret_access",
        "security_policy_change",
        "firewall_change",
        "production_schema_change",
        "financial_threshold_override",
    }

    def requires_approval(
        self,
        action,
    ):

        return action in self.RED_LINES

    def verify(
        self,
        action,
        approved=False,
    ):

        if self.requires_approval(action):
            return approved

        return True
