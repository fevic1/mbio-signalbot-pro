class ModelIntelligence:


    def __init__(self):

        self.profiles = {}


    def register(
        self,
        model,
        profile,
    ):

        self.profiles[model] = profile


    def profile(
        self,
        model,
    ):

        return self.profiles.get(
            model,
            {}
        )


    def rank(
        self,
        models,
        requirement=None,
    ):

        return models
