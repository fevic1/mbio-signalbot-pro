from aios.core.factory import Factory

from .models import PolicyVersion


class PolicyRegistry:


    def __init__(self):

        self._items = {}



    def create(
        self,
        name,
        content,
    ):

        policy = PolicyVersion(
            name=name,
            content=content,
        )

        self._items[name] = [
            policy
        ]

        return policy.describe()



    def update(
        self,
        name,
        content,
    ):

        versions = self._items.get(
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

        self._items[name] = versions

        return version.describe()



    def history(
        self,
        name,
    ):

        return [

            item.describe()

            for item in self._items.get(
                name,
                []
            )

        ]
