from __future__ import annotations

import pytest

from strava.models.streams import (
    AltitudeStream,
    CadenceStream,
    DistanceStream,
    HeartrateStream,
    LatLngStream,
    MovingStream,
    PowerStream,
    SmoothGradeStream,
    SmoothVelocityStream,
    StreamSet,
    TemperatureStream,
    TimeStream,
)


@pytest.mark.parametrize("shape", ["keyed", "list"])
@pytest.mark.parametrize(
    ("name", "model", "data"),
    [
        ("time", TimeStream, [0, 1]),
        ("distance", DistanceStream, [0.0, 10.5]),
        ("latlng", LatLngStream, [[45.0, -122.0], [45.1, -122.1]]),
        ("altitude", AltitudeStream, [10.0, 11.5]),
        ("velocity_smooth", SmoothVelocityStream, [2.0, 2.5]),
        ("heartrate", HeartrateStream, [120, 130]),
        ("cadence", CadenceStream, [80, 90]),
        ("watts", PowerStream, [200, 210]),
        ("temp", TemperatureStream, [20, 21]),
        ("moving", MovingStream, [True, False]),
        ("grade_smooth", SmoothGradeStream, [1.0, 1.5]),
    ],
)
def test_normalizer_preserves_typed_streams_and_metadata(shape, name, model, data):
    value = {
        "data": data,
        "original_size": 2,
        "resolution": "high",
        "series_type": "distance",
    }
    payload = (
        {name: value, "future_stream": {"data": [1, 2]}}
        if shape == "keyed"
        else [
            {"type": name, **value},
            {"type": "future_stream", "data": [1, 2]},
        ]
    )

    streams = StreamSet.from_response(payload)

    assert isinstance(streams, StreamSet)
    assert isinstance(getattr(streams, name), model)
    assert streams.to_dict() == {name: value}
    assert StreamSet.from_dict(streams.to_dict()) == streams


@pytest.mark.parametrize("payload", [{}, []])
def test_normalizer_empty_response(payload):
    assert StreamSet.from_response(payload) == StreamSet()


def test_keyed_response_uses_outer_type_without_mutating_payload():
    payload = {"time": {"type": "heartrate", "data": [0, 1]}}

    streams = StreamSet.from_response(payload)

    assert isinstance(streams.time, TimeStream)
    assert streams.time.data == [0, 1]
    assert streams.heartrate is None
    assert payload == {"time": {"type": "heartrate", "data": [0, 1]}}


def test_legacy_constructor_ignores_unknown_and_missing_types():
    streams = StreamSet.from_stream_list(
        [
            {"type": "time", "data": [0, 1]},
            {"type": "future_stream", "data": [2, 3]},
            {"data": [4, 5]},
        ]
    )

    assert isinstance(streams.time, TimeStream)
    assert streams.to_dict() == {"time": {"data": [0, 1]}}
