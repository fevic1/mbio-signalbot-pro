class Validatable:

    def validate(self):
        return True

    def validate_or_raise(self):
        if not self.validate():
            raise ValueError(
                f"{self.__class__.__name__} validation failed"
            )
        return self
