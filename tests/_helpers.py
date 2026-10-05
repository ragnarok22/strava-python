from __future__ import annotations

import inspect
from collections.abc import Callable
from typing import Any


async def invoke(method: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
    """Call a sync or async SDK method while preserving exceptions and results."""
    result = method(*args, **kwargs)
    return await result if inspect.isawaitable(result) else result
