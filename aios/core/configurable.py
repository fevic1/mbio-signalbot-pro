class Configurable:

    def configure(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        return self

    def configuration(self):
        return {
            k: v
            for k, v in self.__dict__.items()
            if not k.startswith("_")
        }
