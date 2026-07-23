from datetime import datetime


class CapabilityRegistry:

    def __init__(self):

        self.agents = {}


    def register(
        self,
        name,
        agent,
        capability,
        version="1.0.0",
        permission="read"
    ):

        self.agents[name] = {

            "agent": agent,

            "name": name,

            "capability": capability,

            "version": version,

            "permission": permission,

            "enabled": True,

            "registered":
                datetime.utcnow().isoformat()
        }


        return True


    def enable(
        self,
        name
    ):

        if name in self.agents:
            self.agents[name]["enabled"] = True
            return True

        return False


    def disable(
        self,
        name
    ):

        if name in self.agents:
            self.agents[name]["enabled"] = False
            return True

        return False


    def get(
        self,
        name
    ):

        return self.agents.get(name)


    def list_agents(self):

        return [
            {
                "name": data["name"],
                "capability": data["capability"],
                "version": data["version"],
                "enabled": data["enabled"],
                "permission": data["permission"]
            }

            for data in self.agents.values()
        ]
