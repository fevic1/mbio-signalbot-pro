class ConfigValidator:


    def __init__(
        self,
        required=None,
    ):

        self.required = required or []



    def validate(
        self,
        config,
    ):

        missing = [

            item

            for item in self.required

            if item not in config

        ]


        return {

            "valid":
                len(missing) == 0,

            "missing":
                missing,

        }
