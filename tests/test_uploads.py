from __future__ import annotations

import json
from email import policy
from email.parser import BytesParser
from io import BytesIO
from pathlib import Path

import httpx
import pytest
import respx

from strava import SportType
from tests._helpers import invoke

BASE = "https://www.strava.com/api/v3"
EXAMPLE = Path(__file__).parents[1] / "examples" / "strength-training.json"


def multipart_fields(request: httpx.Request) -> dict[str, bytes]:
    message = BytesParser(policy=policy.default).parsebytes(
        f"Content-Type: {request.headers['Content-Type']}\r\n\r\n".encode()
        + request.content
    )
    assert message.is_multipart()
    fields = {}
    for part in message.iter_parts():
        name = part.get_param("name", header="content-disposition")
        payload = part.get_payload(decode=True)
        assert isinstance(name, str)
        assert isinstance(payload, bytes)
        fields[name] = payload
    return fields


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("sport_type", "expected_sport"),
    [
        (SportType.WEIGHT_TRAINING, "WeightTraining"),
        ("HighIntensityIntervalTraining", "HighIntensityIntervalTraining"),
        (SportType.WORKOUT, "Workout"),
        ("Crossfit", "Crossfit"),
    ],
)
@respx.mock
async def test_json_strength_training_upload_preserves_sets_and_streams(
    client, sport_type, expected_sport
):
    payload = EXAMPLE.read_bytes()
    route = respx.post(f"{BASE}/uploads").mock(
        return_value=httpx.Response(
            201,
            json={"id": 42, "status": "Your activity is still being processed."},
        )
    )

    with BytesIO(payload) as file:
        upload = await invoke(
            client.uploads.create,
            file=file,
            data_type="json",
            sport_type=sport_type,
            name="Strength & conditioning",
            external_id="strength-session-42",
        )
        assert not file.closed

    assert upload.id == 42
    assert upload.activity_id is None
    fields = multipart_fields(route.calls.last.request)
    assert fields == {
        "file": payload,
        "data_type": b"json",
        "sport_type": expected_sport.encode(),
        "name": b"Strength & conditioning",
        "external_id": b"strength-session-42",
    }
    document = json.loads(fields["file"])
    assert document["version"] == "1.0"
    assert document["sets"][0]["exercise_type"] == "BARBELL_BENCH_PRESS"
    assert document["sets"][0]["weight"] == 60.0
    assert document["sets"][-1]["duration"] == 60
    assert all(
        len(stream) == len(document["streams"]["time"])
        for stream in document["streams"].values()
    )
    assert route.calls.last.request.headers["Authorization"] == "Bearer test_token"


@pytest.mark.asyncio
@respx.mock
async def test_fit_upload_transmits_binary_data_and_sport_override(client):
    # Opaque binary fixture: transport tests do not simulate Strava's FIT ingestion.
    payload = b"\x0e\x20\x00\x00\x04\x00\x00\x00.FIT\x00\xff\x00\x80"
    route = respx.post(f"{BASE}/uploads").mock(
        return_value=httpx.Response(201, json={"id": 43, "status": "Processing"})
    )

    upload = await invoke(
        client.uploads.create,
        file=payload,
        data_type="fit",
        sport_type=SportType.CROSSFIT,
        trainer=True,
        commute=False,
    )

    assert upload.id == 43
    assert multipart_fields(route.calls.last.request) == {
        "file": payload,
        "data_type": b"fit",
        "sport_type": b"Crossfit",
        "trainer": b"1",
        "commute": b"0",
    }


@pytest.mark.asyncio
@respx.mock
async def test_upload_omits_unspecified_sport_to_allow_file_detection(client):
    route = respx.post(f"{BASE}/uploads").mock(
        return_value=httpx.Response(201, json={"id": 44})
    )
    await invoke(client.uploads.create, file=b"file data", data_type="fit")

    assert multipart_fields(route.calls.last.request) == {
        "file": b"file data",
        "data_type": b"fit",
    }
