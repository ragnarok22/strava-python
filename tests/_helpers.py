from __future__ import annotations

import inspect
from base64 import b64decode
from collections.abc import Callable
from typing import Any

import httpx


async def invoke(method: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
    """Call a sync or async SDK method while preserving exceptions and results."""
    result = method(*args, **kwargs)
    return await result if inspect.isawaitable(result) else result


def assert_basic_auth(request: httpx.Request, username: str, password: str) -> None:
    """Verify test credentials without storing a credential-like header literal."""
    scheme, encoded = request.headers["Authorization"].split(" ", 1)
    assert scheme == "Basic"
    assert b64decode(encoded, validate=True).decode() == f"{username}:{password}"
