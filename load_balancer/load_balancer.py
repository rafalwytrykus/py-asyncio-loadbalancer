from typing import List, Sequence

from load_balancer.provider import Provider


class LoadBalancer:
    MAX_PROVIDERS = 10

    def __init__(self, providers: Sequence[Provider]):
        self.providers = providers

    @property
    def providers(self) -> List[Provider]:
        return self._providers

    @providers.setter
    def providers(self, value: Sequence[Provider]):
        if len(value) > LoadBalancer.MAX_PROVIDERS:
            raise ValueError(
                f"Number of providers can not exceed {LoadBalancer.MAX_PROVIDERS}"
            )
        self._providers = list(value)
