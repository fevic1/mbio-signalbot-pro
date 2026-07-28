#!/usr/bin/env python3

from collections import defaultdict


class PermissionManager:

    def __init__(self):
        self.permissions = defaultdict(set)

    def grant(self, plugin, permission):
        self.permissions[plugin].add(permission)

    def revoke(self, plugin, permission):
        self.permissions[plugin].discard(permission)

    def allowed(self, plugin, permission):
        return permission in self.permissions[plugin]

    def require(self, plugin, permission):
        if not self.allowed(plugin, permission):
            raise PermissionError(
                f"{plugin} missing permission '{permission}'"
            )

    def list(self, plugin=None):
        if plugin is None:
            return {
                k: sorted(v)
                for k, v in self.permissions.items()
            }

        return sorted(self.permissions.get(plugin, []))


permissions = PermissionManager()


if __name__ == "__main__":

    permissions.grant("superpowers", "filesystem.read")
    permissions.grant("superpowers", "filesystem.write")
    permissions.grant("superpowers", "network.http")

    print(permissions.list())

    permissions.require("superpowers", "filesystem.read")

    try:
        permissions.require("superpowers", "shell.execute")
    except PermissionError as e:
        print(e)
