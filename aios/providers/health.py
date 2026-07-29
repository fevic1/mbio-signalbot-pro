
from dataclasses import dataclass


@dataclass
class ProviderHealth:

    name: str

    configured: bool = False

    authenticated: bool = False

    reachable: bool = False

    usable: bool = False

    reason: str = ""


    def snapshot(self):

        return {
            "name": self.name,
            "configured": self.configured,
            "authenticated": self.authenticated,
            "reachable": self.reachable,
            "usable": self.usable,
            "reason": self.reason,
        }
