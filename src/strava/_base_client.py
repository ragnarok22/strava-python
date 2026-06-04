from __future__ import annotations

from typing import Any

from strava._serialization import strip_not_given

BASE_URL = "https://www.api-v3.strava.com"


def build_query_params(params: dict[str, Any] | None) -> dict[str, Any]:
    if params is None:
        return {}
    cleaned = strip_not_given(params)
    result: dict[str, Any] = {}
    for k, v in cleaned.items():
        if isinstance(v, bool):
            result[k] = str(v).lower()
        elif isinstance(v, list):
            result[k] = ",".join(str(i) for i in v)
        elif v is not None:
            result[k] = v
    return result
