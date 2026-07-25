from .models import PolicyVersion


class PolicyRegistry:


    def __init__(self):

        self.policies = {}



    def create(
        self,
        name,
        content,
    ):

        policy = PolicyVersion(
            name=name,
            content=content,
        )

        self.policies[name] = [
            policy
        ]

        return policy.describe()



    def update(
        self,
        name,
        content,
    ):

        versions = self.policies.get(
            name,
            []
        )

        version = PolicyVersion(
            name=name,
            content=content,
            version=len(versions) + 1,
        )

        versions.append(
            version
        )

        self.policies[name] = versions

        return version.describe()



    def history(
        self,
        name,
    ):

        return [

            item.describe()

            for item in self.policies.get(
                name,
                []
            )

        ]
