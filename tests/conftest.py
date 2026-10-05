from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any

import pytest
import pytest_asyncio

from strava import AsyncStrava, Strava
from tests._helpers import invoke


@pytest.fixture
def client_options() -> dict[str, Any]:
    """Override locally for endpoint-specific authentication scenarios."""
    return {}


@pytest_asyncio.fixture(params=[Strava, AsyncStrava], ids=["sync", "async"])
async def client(
    request: pytest.FixtureRequest, client_options: dict[str, Any]
) -> AsyncIterator[Strava | AsyncStrava]:
    client_cls: type[Strava | AsyncStrava] = request.param
    sdk = client_cls(**{"access_token": "test_token", **client_options})
    try:
        yield sdk
    finally:
        await invoke(sdk.close)
