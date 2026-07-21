class LLMAdapter:


    def __init__(
        self,
        router
    ):

        self.router = router


    def choose(
        self,
        task_type
    ):

        model = (
            self.router
            .select_model(
                task_type
            )
        )


        if not model:

            return {
                "status": "no_model",
                "task": task_type
            }


        return {

            "status": "selected",

            "model":
                model.name,

            "provider":
                model.provider

        }
