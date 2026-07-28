class Coordinator:

    def __init__(self):
        self._members = []

    def add(self, member):
        self._members.append(member)
        return member

    def remove(self, member):
        if member in self._members:
            self._members.remove(member)

    def execute(self, *args, **kwargs):
        result = None
        for member in self._members:
            if hasattr(member, "execute"):
                result = member.execute(*args, **kwargs)
            else:
                result = member(*args, **kwargs)
        return result

    def clear(self):
        self._members.clear()

    def __iter__(self):
        return iter(self._members)
