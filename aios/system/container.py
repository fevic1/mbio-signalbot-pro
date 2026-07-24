class AIOSContainer:


    def __init__(self):

        self.services = {}



    def register(
        self,
        name,
        service,
    ):

        self.services[name] = service



    def get(
        self,
        name,
    ):

        return self.services.get(
            name
        )



    def describe(
        self,
    ):

        return list(
            self.services.keys()
        )
