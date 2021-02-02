import uuid
from unittest import mock

import pytest

from load_balancer.provider import Provider

UUIDS = [
    uuid.UUID("abe780f9-1edb-429f-8420-188004241fa1"),
    uuid.UUID("0c6b7ca9-7c48-4921-b5c8-20c972f332ef"),
]


@pytest.mark.asyncio
@mock.patch("uuid.uuid4", side_effect=UUIDS)
async def test_provider_get(_):
    provider_1 = Provider()
    provider_2 = Provider()
    assert await provider_1.get() == str(UUIDS[0])
    assert await provider_2.get() == str(UUIDS[1])
