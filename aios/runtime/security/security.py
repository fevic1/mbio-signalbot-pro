class RuntimeSecurity:

    def __init__(self):
        self._permissions: dict[str, set[str]] = {}

    def grant(self, subject: str, permission: str):
        self._permissions.setdefault(
            subject,
            set(),
        ).add(permission)

    def revoke(self, subject: str, permission: str):
        permissions = self._permissions.get(subject, set())
        permissions.discard(permission)

    def allowed(self, subject: str, permission: str):
        return permission in self._permissions.get(
            subject,
            set(),
        )

    def permissions(self, subject: str):
        return tuple(
            sorted(
                self._permissions.get(
                    subject,
                    set(),
                )
            )
        )

    def export(self):
        return {
            subject: sorted(perms)
            for subject, perms in self._permissions.items()
        }

    def clear(self):
        self._permissions.clear()
