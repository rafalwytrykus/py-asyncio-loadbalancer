import asyncio
import uuid
import random
from unittest import mock

import pytest

from load_balancer import provider_selectors, exceptions
from load_balancer.load_balancer import LoadBalancer
from load_balancer.provider import Provider


def test_load_balancer_init():
    providers = [Provider(), Provider()]
    load_balancer = LoadBalancer(providers, provider_selector=mock.Mock)
    assert load_balancer.providers == providers
    assert load_balancer.providers is not providers


def test_load_balancer_init_negative__too_many_providers():
    providers = [Provider() for _ in range(11)]
    with pytest.raises(ValueError):
        LoadBalancer(providers, provider_selector=mock.Mock)


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


def test_load_balancer_include_provider():
    providers = [Provider(), Provider()]
    load_balancer = LoadBalancer(providers, provider_selector=mock.Mock)
    new_provider = Provider()
    load_balancer.include_provider(new_provider)
    assert load_balancer.active_providers == providers + [new_provider]


def test_load_balancer_exclude_provider():
    providers = [Provider(), Provider()]
    load_balancer = LoadBalancer(providers, provider_selector=mock.Mock)
    load_balancer.exclude_provider(providers[1])
    assert load_balancer.active_providers == providers[:1]


@pytest.mark.asyncio
async def test_load_balancer_heartbeat():
    provider = Provider()
    provider.check = mock.AsyncMock(return_value=False)
    load_balancer = LoadBalancer([provider], provider_selector=mock.Mock)
    assert load_balancer.active_providers == [provider]
    await load_balancer.check_heartbeats()
    assert load_balancer.active_providers == []

    #  Make provider healthy again
    provider.check = mock.AsyncMock(return_value=True)
    await load_balancer.check_heartbeats()
    assert load_balancer.active_providers == []
    await load_balancer.check_heartbeats()
    assert load_balancer.active_providers == [provider]


@pytest.mark.asyncio
@mock.patch("load_balancer.load_balancer.LoadBalancer.HEARTBEAT_INTERVAL_SECONDS", 0.1)
async def test_heartbeat_loop():
    provider = Provider()
    provider.check = mock.AsyncMock(return_value=False)
    load_balancer = LoadBalancer([provider], provider_selector=mock.Mock)
    assert load_balancer.active_providers == [provider]
    heartbeat_loop_task = asyncio.create_task(load_balancer.heartbeat_loop())
    await asyncio.sleep(0.2)
    assert load_balancer.active_providers == []
    provider.check = mock.AsyncMock(return_value=True)
    await asyncio.sleep(0.2)
    assert load_balancer.active_providers == [provider]
    heartbeat_loop_task.cancel()


@pytest.mark.asyncio
async def test_load_balancer_capacity_limiting__negative():
    class SlowProvider(Provider):
        async def get(self) -> str:
            await asyncio.sleep(0.1)
            return await super().get()

    load_balancer = LoadBalancer(
        [SlowProvider()], provider_selector=provider_selectors.RoundRobinSelector
    )
    _ = asyncio.create_task(load_balancer.get())
    t2 = asyncio.create_task(load_balancer.get())
    with pytest.raises(exceptions.CapacityExceeded):
        await t2
    await asyncio.sleep(0.2)
    await load_balancer.get()
