from __future__ import annotations

import httpx
import pytest
import respx

from strava import Strava
from strava.models._enums import SportType

BASE = "https://www.strava.com/api/v3"


@pytest.fixture
def client():
    with Strava(access_token="test_token") as c:
        yield c


class TestActivitiesResource:
    @respx.mock
    def test_retrieve(self, client: Strava):
        respx.get(f"{BASE}/activities/123").mock(
            return_value=httpx.Response(
                200,
                json={
                    "id": 123,
                    "name": "Morning Run",
                    "distance": 10000,
                    "type": "Run",
                    "sport_type": "Run",
                },
            )
        )
        activity = client.activities.retrieve(123)
        assert activity.id == 123
        assert activity.name == "Morning Run"

    @respx.mock
    def test_create(self, client: Strava):
        respx.post(f"{BASE}/activities").mock(
            return_value=httpx.Response(
                201,
                json={
                    "id": 456,
                    "name": "Test Activity",
                    "sport_type": "Run",
                    "distance": 5000,
                },
            )
        )
        activity = client.activities.create(
            name="Test Activity",
            sport_type=SportType.RUN,
            start_date_local="2024-06-15T07:00:00Z",
            elapsed_time=1800,
            distance=5000.0,
        )
        assert activity.id == 456

    @respx.mock
    def test_update(self, client: Strava):
        respx.put(f"{BASE}/activities/123").mock(
            return_value=httpx.Response(
                200,
                json={
                    "id": 123,
                    "name": "Updated Name",
                    "description": "New desc",
                },
            )
        )
        activity = client.activities.update(
            123, name="Updated Name", description="New desc"
        )
        assert activity.name == "Updated Name"

    @respx.mock
    def test_list_laps(self, client: Strava):
        respx.get(f"{BASE}/activities/123/laps").mock(
            return_value=httpx.Response(
                200,
                json=[
                    {"id": 1, "name": "Lap 1", "distance": 5000},
                    {"id": 2, "name": "Lap 2", "distance": 5000},
                ],
            )
        )
        laps = client.activities.list_laps(123)
        assert len(laps) == 2
        assert laps[0].name == "Lap 1"

    @respx.mock
    def test_list_zones(self, client: Strava):
        respx.get(f"{BASE}/activities/123/zones").mock(
            return_value=httpx.Response(
                200,
                json=[
                    {
                        "type": "heartrate",
                        "score": 80,
                        "distribution_buckets": [{"min": 0, "max": 120, "time": 300}],
                    }
                ],
            )
        )
        zones = client.activities.list_zones(123)
        assert len(zones) == 1
        assert zones[0].type == "heartrate"


class TestAthletesResource:
    @respx.mock
    def test_retrieve_authenticated(self, client: Strava):
        respx.get(f"{BASE}/athlete").mock(
            return_value=httpx.Response(
                200,
                json={
                    "id": 1,
                    "firstname": "John",
                    "lastname": "Doe",
                    "follower_count": 50,
                },
            )
        )
        athlete = client.athletes.retrieve_authenticated()
        assert athlete.firstname == "John"

    @respx.mock
    def test_update_authenticated(self, client: Strava):
        respx.put(f"{BASE}/athlete").mock(
            return_value=httpx.Response(200, json={"id": 1, "weight": 72.5})
        )
        athlete = client.athletes.update_authenticated(weight=72.5)
        assert athlete.weight == 72.5

    @respx.mock
    def test_retrieve_zones(self, client: Strava):
        respx.get(f"{BASE}/athlete/zones").mock(
            return_value=httpx.Response(
                200,
                json={
                    "heart_rate": {
                        "custom_zones": False,
                        "zones": [{"min": 0, "max": 120}],
                    }
                },
            )
        )
        zones = client.athletes.retrieve_zones()
        assert zones.heart_rate is not None

    @respx.mock
    def test_retrieve_stats(self, client: Strava):
        respx.get(f"{BASE}/athletes/1/stats").mock(
            return_value=httpx.Response(
                200,
                json={
                    "biggest_ride_distance": 200000.0,
                    "recent_ride_totals": {"count": 5, "distance": 50000},
                },
            )
        )
        stats = client.athletes.retrieve_stats(1)
        assert stats.biggest_ride_distance == 200000.0


class TestClubsResource:
    @respx.mock
    def test_retrieve(self, client: Strava):
        respx.get(f"{BASE}/clubs/1").mock(
            return_value=httpx.Response(
                200,
                json={"id": 1, "name": "Test Club", "member_count": 100},
            )
        )
        club = client.clubs.retrieve(1)
        assert club.name == "Test Club"


class TestGearResource:
    @respx.mock
    def test_retrieve(self, client: Strava):
        respx.get(f"{BASE}/gear/b123").mock(
            return_value=httpx.Response(
                200,
                json={
                    "id": "b123",
                    "name": "Trek Domane",
                    "brand_name": "Trek",
                    "model_name": "Domane",
                },
            )
        )
        gear = client.gear.retrieve("b123")
        assert gear.brand_name == "Trek"


class TestRoutesResource:
    @respx.mock
    def test_retrieve(self, client: Strava):
        respx.get(f"{BASE}/routes/1").mock(
            return_value=httpx.Response(
                200,
                json={
                    "id": 1,
                    "name": "Sunday Route",
                    "distance": 50000.0,
                },
            )
        )
        route = client.routes.retrieve(1)
        assert route.name == "Sunday Route"

    @respx.mock
    def test_export_gpx(self, client: Strava):
        respx.get(f"{BASE}/routes/1/export_gpx").mock(
            return_value=httpx.Response(200, content=b"<gpx>data</gpx>")
        )
        data = client.routes.export_gpx(1)
        assert b"<gpx>" in data


class TestSegmentsResource:
    @respx.mock
    def test_retrieve(self, client: Strava):
        respx.get(f"{BASE}/segments/1").mock(
            return_value=httpx.Response(
                200,
                json={"id": 1, "name": "Test Segment", "distance": 1000.0},
            )
        )
        segment = client.segments.retrieve(1)
        assert segment.name == "Test Segment"

    @respx.mock
    def test_explore(self, client: Strava):
        respx.get(f"{BASE}/segments/explore").mock(
            return_value=httpx.Response(
                200,
                json={
                    "segments": [
                        {"id": 1, "name": "Seg", "avg_grade": 5.0, "distance": 1000}
                    ]
                },
            )
        )
        result = client.segments.explore(bounds=[37.0, -122.0, 38.0, -121.0])
        assert len(result.segments) == 1

    @respx.mock
    def test_star(self, client: Strava):
        respx.put(f"{BASE}/segments/1/starred").mock(
            return_value=httpx.Response(200, json={"id": 1, "name": "Test"})
        )
        segment = client.segments.star(1, starred=True)
        assert segment.id == 1


class TestSegmentEffortsResource:
    @respx.mock
    def test_retrieve(self, client: Strava):
        respx.get(f"{BASE}/segment_efforts/1").mock(
            return_value=httpx.Response(
                200,
                json={"id": 1, "name": "Sprint", "elapsed_time": 120},
            )
        )
        effort = client.segment_efforts.retrieve(1)
        assert effort.name == "Sprint"

    @respx.mock
    def test_list(self, client: Strava):
        respx.get(f"{BASE}/segment_efforts").mock(
            return_value=httpx.Response(
                200,
                json=[
                    {"id": 1, "elapsed_time": 120},
                    {"id": 2, "elapsed_time": 130},
                ],
            )
        )
        efforts = client.segment_efforts.list(segment_id=123)
        assert len(efforts) == 2


class TestStreamsResource:
    @respx.mock
    def test_get_activity_streams(self, client: Strava):
        respx.get(f"{BASE}/activities/1/streams").mock(
            return_value=httpx.Response(
                200,
                json=[
                    {
                        "type": "time",
                        "data": [0, 1, 2],
                        "series_type": "distance",
                        "original_size": 3,
                        "resolution": "high",
                    },
                    {
                        "type": "heartrate",
                        "data": [120, 130, 140],
                        "series_type": "distance",
                        "original_size": 3,
                        "resolution": "high",
                    },
                ],
            )
        )
        streams = client.streams.get_activity_streams(1, keys=["time", "heartrate"])
        assert streams.time is not None
        assert streams.time.data == [0, 1, 2]
        assert streams.heartrate is not None


class TestUploadsResource:
    @respx.mock
    def test_retrieve(self, client: Strava):
        respx.get(f"{BASE}/uploads/1").mock(
            return_value=httpx.Response(
                200,
                json={
                    "id": 1,
                    "status": "Your activity is ready.",
                    "activity_id": 100,
                },
            )
        )
        upload = client.uploads.retrieve(1)
        assert upload.status == "Your activity is ready."

    @respx.mock
    def test_create(self, client: Strava):
        respx.post(f"{BASE}/uploads").mock(
            return_value=httpx.Response(
                201,
                json={"id": 1, "status": "Your activity is still being processed."},
            )
        )
        upload = client.uploads.create(
            file=b"fake gpx data",
            data_type="gpx",
            name="Test Upload",
        )
        assert upload.id == 1
