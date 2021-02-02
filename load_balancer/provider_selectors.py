import abc
import random
from abc import abstractmethod
from typing import Sequence, TYPE_CHECKING

if TYPE_CHECKING:
    from provider import Provider


class ProviderSelector(abc.ABC):
    @abstractmethod
    def select_provider(self, providers: Sequence["Provider"]) -> "Provider":
        pass


class RandomProviderSelector(ProviderSelector):
    def select_provider(self, providers: Sequence["Provider"]) -> "Provider":
        return random.choice(providers)


class RoundRobinSelector(ProviderSelector):
    def __init__(self):
        self.index = 0

    def select_provider(self, providers: Sequence["Provider"]) -> "Provider":
        try:
            provider = providers[self.index]
        except IndexError:
            if len(providers) == 0:
                raise RuntimeError("Providers registry is empty")
            self.index = 0
            return self.select_provider(providers)
        self.index += 1
        return provider
