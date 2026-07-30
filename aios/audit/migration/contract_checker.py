class ContractChecker:


    def compare(self, current, canonical):

        return {
            "compatible":
                current == canonical,

            "adapter_required":
                current != canonical,

            "current":
                current,

            "canonical":
                canonical,
        }
