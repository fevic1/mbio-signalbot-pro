class PermissionManager:


    LEVELS = {
        "read": 1,
        "research": 2,
        "execute": 3,
        "critical": 4
    }


    def check(
        self,
        agent_permission,
        required_permission
    ):

        agent_level = self.LEVELS.get(
            agent_permission,
            0
        )

        required_level = self.LEVELS.get(
            required_permission,
            99
        )


        return agent_level >= required_level
