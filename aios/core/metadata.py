class MetadataMixin:

    def metadata(self):
        return {
            k: v
            for k, v in vars(self).items()
            if not k.startswith("_")
        }

    def update_metadata(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        return self
