from __future__ import annotations

from dataclasses import dataclass, field

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
    def from_stream_list(cls, streams: list[dict]) -> StreamSet:
        """Build StreamSet from the API's list-of-streams format.

        The API returns streams as a list of objects, each with a 'type' key,
        rather than a dict keyed by type.
        """
        kwargs: dict = {}
        for stream_data in streams:
            stream_type = stream_data.get("type")
            if stream_type and stream_type in _STREAM_TYPE_MAP:
                stream_cls = _STREAM_TYPE_MAP[stream_type]
                kwargs[stream_type] = stream_cls.from_dict(stream_data)
        return cls(**kwargs)
