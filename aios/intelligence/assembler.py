class ContextAssembler:

    def assemble(
        self,
        capability,
        request,
    ):
        return {
            "capability": capability,
            "request": request,
        }
