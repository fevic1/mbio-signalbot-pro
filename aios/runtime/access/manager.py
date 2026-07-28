class RuntimeAccessManager:

    def __init__(self):
        self._roles = {}
        self._bindings = {}

    def create_role(self, name: str, permissions=None):
        self._roles[name] = set(
            permissions or []
        )

        return name

    def grant(self, role: str, permission: str):
        self._roles.setdefault(
            role,
            set(),
        ).add(permission)

    def revoke(self, role: str, permission: str):
        if role in self._roles:
            self._roles[role].discard(
                permission
            )

    def bind(self, subject: str, role: str):
        self._bindings[subject] = role

    def allowed(self, subject: str, permission: str):
        role = self._bindings.get(subject)

        if role is None:
            return False

        return permission in self._roles.get(
            role,
            set(),
        )

    def roles(self):
        return {
            name: sorted(perms)
            for name, perms in self._roles.items()
        }

    def bindings(self):
        return dict(self._bindings)

    def export(self):
        return {
            "roles": self.roles(),
            "bindings": self.bindings(),
        }

    def clear(self):
        self._roles.clear()
        self._bindings.clear()
