from uuid import uuid4


class Identifiable:

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not hasattr(self, "id"):
            self.id = uuid4().hex

    @property
    def identifier(self):
        return self.id
