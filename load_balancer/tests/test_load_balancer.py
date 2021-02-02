import uuid
import random
from unittest import mock

import pytest

from load_balancer import provider_selectors
from load_balancer.load_balancer import LoadBalancer
from load_balancer.provider import Provider


def test_load_balancer_init():
    providers = [Provider(), Provider()]
    load_balancer = LoadBalancer(providers, provider_selector=mock.Mock())
    assert load_balancer.providers == providers
    assert load_balancer.providers is not providers


def test_load_balancer_init_negative__too_many_providers():
    providers = [Provider() for _ in range(11)]
    with pytest.raises(ValueError):
        LoadBalancer(providers, provider_selector=mock.Mock())


UUIDS = [
    uuid.UUID("abe780f9-1edb-429f-8420-188004241fa1"),
    uuid.UUID("abe780f9-1edb-429f-8420-188004241fa2"),
    uuid.UUID("abe780f9-1edb-429f-8420-188004241fa3"),
    uuid.UUID("abe780f9-1edb-429f-8420-188004241fa4"),
]


@pytest.mark.asyncio
@mock.patch("uuid.uuid4", side_effect=UUIDS)
@pytest.mark.parametrize(
    "provider,expected_uids",
    [
        (
            provider_selectors.RandomProviderSelector,
            [
                "abe780f9-1edb-429f-8420-188004241fa3",
                "abe780f9-1edb-429f-8420-188004241fa2",
                "abe780f9-1edb-429f-8420-188004241fa3",
                "abe780f9-1edb-429f-8420-188004241fa4",
                "abe780f9-1edb-429f-8420-188004241fa3",
                "abe780f9-1edb-429f-8420-188004241fa3",
            ],
        ),
        (
            provider_selectors.RoundRobinSelector,
            [
                "abe780f9-1edb-429f-8420-188004241fa1",
                "abe780f9-1edb-429f-8420-188004241fa2",
                "abe780f9-1edb-429f-8420-188004241fa3",
                "abe780f9-1edb-429f-8420-188004241fa4",
                "abe780f9-1edb-429f-8420-188004241fa1",
                "abe780f9-1edb-429f-8420-188004241fa2",
            ],
        ),
    ],
)
async def test_load_balancer_selectors(_, provider, expected_uids):
    random.seed(1337)
    providers = [Provider() for _ in range(4)]
    load_balancer = LoadBalancer(providers, provider_selector=provider)
    for expected_uid in expected_uids:
        assert await load_balancer.get() == expected_uid
