from abc import ABC, abstractmethod

from aios.providers.types import (
    ProviderRequest,
    ProviderResponse,
)

from aios.neural_proxy.protocol import (
    AIOSRequest,
)


class ProviderAdapter(ABC):


    @abstractmethod
    def translate_request(
        self,
        request: AIOSRequest,
    ) -> ProviderRequest:
        ...


    @abstractmethod
    def translate_response(
        self,
        response: ProviderResponse,
    ):
        ...
