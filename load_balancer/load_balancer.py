from typing import List, Sequence, Type, Set

from load_balancer.provider import Provider
from load_balancer.provider_selectors import ProviderSelector


class LoadBalancer:
    MAX_PROVIDERS = 10

    def __init__(
        self, providers: Sequence[Provider], provider_selector: Type[ProviderSelector]
    ):
        self._providers: List[Provider] = []
        self._excluded_providers:  Set[Provider] = set()
        self.providers = providers
        self._provider_selector = provider_selector()

    @property
    def providers(self) -> List[Provider]:
        return self._providers

    @property
    def active_providers(self) -> List[Provider]:
        return [p for p in self._providers if p not in self._excluded_providers]

    @providers.setter
    def providers(self, value: Sequence[Provider]):
        if len(value) > LoadBalancer.MAX_PROVIDERS:
            raise ValueError(
                f"Number of providers can not exceed {LoadBalancer.MAX_PROVIDERS}"
            )
        if len(value) == 0:
            raise ValueError("Providers list cannot be empty")
        self._providers = list(value)

    def include_provider(self, provider: Provider) -> None:
        try:
            self._excluded_providers.remove(provider)
        except KeyError:
            pass
        if provider not in self.providers:
            self.providers.append(provider)

    def exclude_provider(self, provider: Provider) -> None:
        self._excluded_providers.add(provider)

    async def get(self):
        if len(self.active_providers) == 0:
            raise RuntimeError("No providers available")
        return await self._provider_selector.select_provider(
            self.active_providers
        ).get()
