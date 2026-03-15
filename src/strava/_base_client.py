from __future__ import annotations

from typing import Any, TypeVar

from strava._exceptions import raise_for_status
from strava._serialization import strip_not_given
from strava.models._base import StravaModel

T = TypeVar("T", bound=StravaModel)

BASE_URL = "https://www.strava.com/api/v3"


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


def process_response(response: Any, model_cls: type[T]) -> T:
    raise_for_status(response)
    return model_cls.from_dict(response.json())


def process_response_list(response: Any, model_cls: type[T]) -> list[T]:
    raise_for_status(response)
    return [model_cls.from_dict(item) for item in response.json()]
