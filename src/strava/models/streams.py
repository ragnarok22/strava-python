from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from strava.models._base import StravaModel


@dataclass(slots=True, kw_only=True)
class BaseStream(StravaModel):
    original_size: int | None = None
    resolution: str | None = None
    series_type: str | None = None


@dataclass(slots=True, kw_only=True)
class TimeStream(BaseStream):
    data: list[int] = field(default_factory=list)


@dataclass(slots=True, kw_only=True)
class DistanceStream(BaseStream):
    data: list[float] = field(default_factory=list)


@dataclass(slots=True, kw_only=True)
class LatLngStream(BaseStream):
    data: list[list[float]] = field(default_factory=list)


@dataclass(slots=True, kw_only=True)
class AltitudeStream(BaseStream):
    data: list[float] = field(default_factory=list)


@dataclass(slots=True, kw_only=True)
class SmoothVelocityStream(BaseStream):
    data: list[float] = field(default_factory=list)


@dataclass(slots=True, kw_only=True)
class HeartrateStream(BaseStream):
    data: list[int] = field(default_factory=list)


@dataclass(slots=True, kw_only=True)
class CadenceStream(BaseStream):
    data: list[int] = field(default_factory=list)


@dataclass(slots=True, kw_only=True)
class PowerStream(BaseStream):
    data: list[int] = field(default_factory=list)


@dataclass(slots=True, kw_only=True)
class TemperatureStream(BaseStream):
    data: list[int] = field(default_factory=list)


@dataclass(slots=True, kw_only=True)
class MovingStream(BaseStream):
    data: list[bool] = field(default_factory=list)


@dataclass(slots=True, kw_only=True)
class SmoothGradeStream(BaseStream):
    data: list[float] = field(default_factory=list)


_STREAM_TYPE_MAP: dict[str, type] = {
    "time": TimeStream,
    "distance": DistanceStream,
    "latlng": LatLngStream,
    "altitude": AltitudeStream,
    "velocity_smooth": SmoothVelocityStream,
    "heartrate": HeartrateStream,
    "cadence": CadenceStream,
    "watts": PowerStream,
    "temp": TemperatureStream,
    "moving": MovingStream,
    "grade_smooth": SmoothGradeStream,
}


@dataclass(slots=True, kw_only=True)
class StreamSet(StravaModel):
    time: TimeStream | None = None
    distance: DistanceStream | None = None
    latlng: LatLngStream | None = None
    altitude: AltitudeStream | None = None
    velocity_smooth: SmoothVelocityStream | None = None
    heartrate: HeartrateStream | None = None
    cadence: CadenceStream | None = None
    watts: PowerStream | None = None
    temp: TemperatureStream | None = None
    moving: MovingStream | None = None
    grade_smooth: SmoothGradeStream | None = None

    @classmethod
    def from_response(cls, streams: dict[str, Any] | list[dict[str, Any]]) -> StreamSet:
        """Normalize keyed or legacy list responses into typed streams.

        Keyed responses use the outer key as the stream type, so their values
        do not need an inner ``type`` field. Unknown stream types are ignored.
        """
        if isinstance(streams, dict):
            return cls.from_dict(streams)
        return cls.from_stream_list(streams)

    @classmethod
    def from_stream_list(cls, streams: list[dict]) -> StreamSet:
        """Build StreamSet from legacy lists of objects with a ``type`` key."""
        kwargs: dict = {}
        for stream_data in streams:
            stream_type = stream_data.get("type")
            if stream_type and stream_type in _STREAM_TYPE_MAP:
                stream_cls = _STREAM_TYPE_MAP[stream_type]
                kwargs[stream_type] = stream_cls.from_dict(stream_data)
        return cls(**kwargs)
