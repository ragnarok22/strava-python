from __future__ import annotations

import json
from email import policy
from email.parser import BytesParser
from types import MappingProxyType
from typing import Any
from urllib.parse import parse_qs

import httpx
import pytest
import respx

from strava import (
    NOT_GIVEN,
    ActivityTag,
    ActivityVisibility,
    AsyncStrava,
    DetailedActivity,
    Strava,
    SummaryActivity,
    UpdatableActivity,
)
from tests._helpers import invoke

BASE = "https://www.strava.com/api/v3"
CREATE_FIELDS = {
    "name": "Run with a friend",
    "sport_type": "Run",
    "start_date_local": "2026-11-17T09:00:00Z",
    "elapsed_time": 1800,
}


def request_fields(request: httpx.Request) -> dict[str, str]:
    content_type = request.headers["Content-Type"]
    if content_type.startswith("multipart/form-data"):
        message = BytesParser(policy=policy.default).parsebytes(
            f"Content-Type: {content_type}\r\n\r\n".encode() + request.content
        )
        return {
            part.get_param("name", header="content-disposition"): part.get_content()
            for part in message.iter_parts()
            if part.get_filename() is None
        }
    return {
        key: values[0] for key, values in parse_qs(request.content.decode()).items()
    }


@pytest.mark.asyncio
@pytest.mark.parametrize("endpoint", ["create", "update", "upload", "upload_form"])
@respx.mock
async def test_activity_options_request(
    client: Strava | AsyncStrava, endpoint: str
) -> None:
    tags: dict[str, bool] = {
        ActivityTag.WITH_PET: True,
        "Recovery": False,
        "Competition": True,
        "ForACause": False,
        "Commute": False,
    }
    original = tags.copy()
    upload = endpoint.startswith("upload")
    visibility = (
        ActivityVisibility.ONLY_ME
        if endpoint == "update"
        else ActivityVisibility.FOLLOWERS_ONLY
    )
    route = respx.route(
        method="PUT" if endpoint == "update" else "POST",
        url=f"{BASE}/uploads"
        if upload
        else f"{BASE}/activities"
        + ("/12345678901234567890" if endpoint == "update" else ""),
    ).mock(
        return_value=httpx.Response(
            200 if endpoint == "update" else 201,
            json={
                "id": 12345678901234567890,
                "visibility": visibility,
                "tags": ["WithPet"],
            },
        )
    )
    options = {"visibility": visibility, "tags": MappingProxyType(tags)}
    if upload:
        result = await invoke(
            client.uploads.create,
            file=b"<gpx/>" if endpoint == "upload" else None,
            data_type="gpx",
            trainer=False,
            **options,
        )
    elif endpoint == "update":
        result = await invoke(
            client.activities.update, "12345678901234567890", trainer=False, **options
        )
    else:
        result = await invoke(client.activities.create, **CREATE_FIELDS, **options)

    assert result.id == 12345678901234567890
    assert tags == original
    request = route.calls.last.request
    if endpoint == "update":
        assert request.headers["Content-Type"] == "application/json"
        assert json.loads(request.content) == {
            "trainer": False,
            "visibility": visibility,
            "tags": original,
        }
    else:
        fields = request_fields(request)
        assert fields["visibility"] == visibility
        for tag, value in original.items():
            assert fields[f"tags[{tag}]"] == ("true" if value else "false")
        assert "tags" not in fields
        assert "commute" not in fields
        if upload:
            assert fields["trainer"] == "0"
            assert fields["data_type"] == "gpx"
            if endpoint == "upload":
                assert b"<gpx/>" in request.content
                assert request.headers["Content-Type"].startswith(
                    "multipart/form-data;"
                )
        else:
            assert fields["sport_type"] == "Run"
            assert (
                request.headers["Content-Type"] == "application/x-www-form-urlencoded"
            )
    if not upload:
        assert result.visibility is visibility
        assert result.tags == ["WithPet"]


@pytest.mark.asyncio
@pytest.mark.parametrize("endpoint", ["create", "update", "upload"])
@pytest.mark.parametrize("commute", [True, False])
@pytest.mark.parametrize("tags", [{"Recovery": False}, {}])
@respx.mock
async def test_tags_cannot_be_combined_with_legacy_commute(
    client: Strava | AsyncStrava,
    endpoint: str,
    commute: bool,
    tags: dict[str, bool],
) -> None:
    with pytest.raises(ValueError, match="tags.*commute"):
        if endpoint == "upload":
            await invoke(
                client.uploads.create, file=b"<gpx/>", tags=tags, commute=commute
            )
        elif endpoint == "update":
            await invoke(client.activities.update, 123, tags=tags, commute=commute)
        else:
            await invoke(
                client.activities.create, **CREATE_FIELDS, tags=tags, commute=commute
            )
    assert not respx.calls


@pytest.mark.asyncio
@pytest.mark.parametrize("endpoint", ["create", "update", "upload"])
@pytest.mark.parametrize(
    ("tags", "error"),
    [
        ({"Unsupported": True}, ValueError),
        ({"Recovery": "false"}, TypeError),
        ({"Recovery": 0}, TypeError),
        ({"Recovery": None}, TypeError),
        (["Recovery"], TypeError),
    ],
)
@respx.mock
async def test_invalid_tags_fail_before_request(
    client: Strava | AsyncStrava, endpoint: str, tags: Any, error: type[Exception]
) -> None:
    with pytest.raises(error, match="tag"):
        if endpoint == "upload":
            await invoke(client.uploads.create, file=b"<gpx/>", tags=tags)
        elif endpoint == "update":
            await invoke(client.activities.update, 123, tags=tags)
        else:
            await invoke(client.activities.create, **CREATE_FIELDS, tags=tags)
    assert not respx.calls


@pytest.mark.asyncio
@pytest.mark.parametrize("endpoint", ["create", "update", "upload"])
@respx.mock
async def test_omitted_options_preserve_legacy_commute_and_existing_tags(
    client: Strava | AsyncStrava, endpoint: str
) -> None:
    route = respx.route(
        method="PUT" if endpoint == "update" else "POST",
        url=f"{BASE}/uploads"
        if endpoint == "upload"
        else f"{BASE}/activities" + ("/123" if endpoint == "update" else ""),
    ).mock(
        return_value=httpx.Response(
            200, json={"id": 123, "tags": ["WithPet", "Recovery"]}
        )
    )
    options = {"commute": False, "visibility": NOT_GIVEN, "tags": NOT_GIVEN}
    if endpoint == "upload":
        await invoke(client.uploads.create, file=b"<gpx/>", **options)
    elif endpoint == "update":
        activity = await invoke(
            client.activities.update, 123, name="Updated", **options
        )
        assert activity.tags == ["WithPet", "Recovery"]
    else:
        await invoke(client.activities.create, **CREATE_FIELDS, **options)
    request = route.calls.last.request
    if endpoint == "update":
        assert json.loads(request.content) == {"name": "Updated", "commute": False}
    else:
        fields = request_fields(request)
        assert fields["commute"] == "0"
        assert "visibility" not in fields
        assert not any(key.startswith("tags") for key in fields)


@pytest.mark.parametrize("model", [SummaryActivity, DetailedActivity])
@pytest.mark.parametrize(
    "visibility", ["followers_only", "only_me", "future_visibility"]
)
def test_activity_options_response_roundtrip(
    model: type[SummaryActivity | DetailedActivity], visibility: str
) -> None:
    payload = {
        "id": 12345678901234567890,
        "id_str": "12345678901234567890",
        "visibility": visibility,
        "tags": [
            "WithPet",
            "Recovery",
            "Competition",
            "ForACause",
            "Commute",
            "FutureTag",
        ],
    }
    activity = model.from_dict(payload)
    assert activity.visibility == visibility
    assert activity.tags == payload["tags"]
    assert activity.tags is not None
    assert activity.tags[:5] == list(ActivityTag)
    assert all(isinstance(tag, ActivityTag) for tag in activity.tags[:5])
    assert activity.tags[-1] == "FutureTag"
    assert type(activity.tags[-1]) is str
    serialized = activity.to_dict()
    assert {key: serialized[key] for key in payload} == payload
    assert json.loads(json.dumps(serialized))["tags"] == payload["tags"]
    assert model.from_dict(serialized) == activity


@pytest.mark.parametrize(
    "model", [SummaryActivity, DetailedActivity, UpdatableActivity]
)
def test_activity_options_missing_or_null(
    model: type[SummaryActivity | DetailedActivity | UpdatableActivity],
) -> None:
    for payload in ({}, {"visibility": None, "tags": None}):
        activity = model.from_dict(payload)
        assert activity.visibility is None
        assert activity.tags is None
        assert "tags" not in activity.to_dict()
        assert "visibility" not in activity.to_dict()


def test_update_model_partial_tag_changes_roundtrip() -> None:
    payload = {"visibility": "only_me", "tags": {"WithPet": True, "Commute": False}}
    activity = UpdatableActivity.from_dict(payload)
    assert activity.tags == {"WithPet": True, "Commute": False}
    assert activity.to_dict() == payload
    assert UpdatableActivity(tags={}).to_dict() == {"tags": {}}
    assert SummaryActivity(tags=[]).to_dict() == {"tags": []}
    assert DetailedActivity(tags=[]).to_dict()["tags"] == []
