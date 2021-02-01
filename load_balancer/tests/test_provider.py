import uuid
from unittest import mock

from load_balancer.provider import Provider

UUIDS = [
    uuid.UUID("abe780f9-1edb-429f-8420-188004241fa1"),
    uuid.UUID("0c6b7ca9-7c48-4921-b5c8-20c972f332ef"),
]


@mock.patch("uuid.uuid4", side_effect=UUIDS)
def test_provider_get(_):
    provider_1 = Provider()
    provider_2 = Provider()
    assert provider_1.get() == str(UUIDS[0])
    assert provider_2.get() == str(UUIDS[1])
