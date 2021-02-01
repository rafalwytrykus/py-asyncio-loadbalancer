import pytest

from load_balancer.load_balancer import LoadBalancer
from load_balancer.provider import Provider


def test_load_balancer_init():
    providers = [Provider(), Provider()]
    load_balancer = LoadBalancer(providers)
    assert load_balancer.providers == providers
    assert load_balancer.providers is not providers


def test_load_balancer_init_negative__too_many_providers():
    providers = [Provider() for _ in range(11)]
    with pytest.raises(ValueError):
        LoadBalancer(providers)
