from .models import EvidenceBundle


class EvidenceBuilder:

    def empty(self) -> EvidenceBundle:
        return EvidenceBundle()
