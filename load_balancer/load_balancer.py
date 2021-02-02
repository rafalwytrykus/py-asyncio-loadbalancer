from typing import List, Sequence, Type

from load_balancer.provider import Provider
from load_balancer.provider_selectors import ProviderSelector


class LoadBalancer:
    MAX_PROVIDERS = 10

    def __init__(
        self, providers: Sequence[Provider], provider_selector: Type[ProviderSelector]
    ):
        self.providers = providers
        self._provider_selector = provider_selector()

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

    async def get(self):
        return await self._provider_selector.select_provider(self.providers).get()
