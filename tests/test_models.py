from __future__ import annotations

from datetime import datetime

from strava.models._enums import ActivityType, SportType
from strava.models.activities import (
    ActivityZone,
    ClubActivity,
    Comment,
    DetailedActivity,
    Lap,
    MetaActivity,
    SummaryActivity,
    UpdatableActivity,
)
from strava.models.athletes import (
    ClubAthlete,
    DetailedAthlete,
    MetaAthlete,
    SummaryAthlete,
)
from strava.models.clubs import DetailedClub, MetaClub, SummaryClub
from strava.models.common import (
    Fault,
    PolylineMap,
    Split,
)
from strava.models.gear import DetailedGear, SummaryGear
from strava.models.routes import Route
from strava.models.segments import (
    DetailedSegment,
    DetailedSegmentEffort,
    ExplorerResponse,
    SummaryPRSegmentEffort,
    SummarySegment,
)
from strava.models.stats import ActivityStats, ActivityTotal, Zones
from strava.models.streams import StreamSet
from strava.models.uploads import Upload
from strava.models.webhooks import (
    WebhookEvent,
    WebhookSubscription,
    WebhookValidationRequest,
    WebhookValidationResponse,
)


class TestMetaModels:
    def test_meta_activity(self):
        m = MetaActivity.from_dict({"id": 123})
        assert m.id == 123

    def test_meta_athlete(self):
        m = MetaAthlete.from_dict({"id": 456})
        assert m.id == 456

    def test_meta_club(self):
        m = MetaClub.from_dict({"id": 789, "name": "Test Club", "resource_state": 2})
        assert m.id == 789
        assert m.name == "Test Club"


class TestAthleteModels:
    def test_summary_athlete(self):
        data = {
            "id": 1234,
            "firstname": "John",
            "lastname": "Doe",
            "city": "Denver",
            "state": "Colorado",
            "country": "US",
            "sex": "M",
            "premium": True,
            "summit": True,
            "created_at": "2018-01-01T00:00:00Z",
            "updated_at": "2024-06-15T12:30:00Z",
        }
        a = SummaryAthlete.from_dict(data)
        assert a.id == 1234
        assert a.firstname == "John"
        assert a.sex == "M"
        assert a.premium is True
        assert isinstance(a.created_at, datetime)
        assert a.created_at.year == 2018

    def test_detailed_athlete(self):
        data = {
            "id": 1234,
            "firstname": "John",
            "lastname": "Doe",
            "follower_count": 50,
            "friend_count": 30,
            "measurement_preference": "meters",
            "ftp": 250,
            "weight": 72.5,
            "clubs": [{"id": 1, "name": "Club A"}],
            "bikes": [{"id": "b123", "name": "Road Bike", "primary": True}],
            "shoes": [],
        }
        a = DetailedAthlete.from_dict(data)
        assert a.follower_count == 50
        assert a.weight == 72.5
        assert len(a.clubs) == 1
        assert a.clubs[0].name == "Club A"
        assert a.bikes[0].id == "b123"

    def test_club_athlete(self):
        data = {"firstname": "Jane", "admin": True, "owner": False}
        a = ClubAthlete.from_dict(data)
        assert a.firstname == "Jane"
        assert a.admin is True

    def test_to_dict(self):
        a = SummaryAthlete(id=1, firstname="Test")
        d = a.to_dict()
        assert d["id"] == 1
        assert d["firstname"] == "Test"
        assert "city" not in d  # None fields excluded


class TestActivityModels:
    SUMMARY_DATA = {
        "id": 9876,
        "name": "Morning Run",
        "distance": 10000.5,
        "moving_time": 3600,
        "elapsed_time": 3700,
        "total_elevation_gain": 150.0,
        "type": "Run",
        "sport_type": "Run",
        "start_date": "2024-06-15T07:00:00Z",
        "start_date_local": "2024-06-15T09:00:00+02:00",
        "trainer": False,
        "commute": False,
        "average_speed": 2.78,
        "max_speed": 4.5,
        "athlete": {"id": 123},
        "map": {
            "id": "a123",
            "summary_polyline": "abc123",
            "polyline": None,
        },
    }

    def test_summary_activity(self):
        a = SummaryActivity.from_dict(self.SUMMARY_DATA)
        assert a.id == 9876
        assert a.name == "Morning Run"
        assert a.distance == 10000.5
        assert a.type == ActivityType.RUN
        assert a.sport_type == SportType.RUN
        assert isinstance(a.start_date, datetime)
        assert a.athlete is not None
        assert a.athlete.id == 123
        assert a.map is not None
        assert a.map.summary_polyline == "abc123"

    def test_detailed_activity(self):
        data = {
            **self.SUMMARY_DATA,
            "description": "Great run!",
            "calories": 500.0,
            "gear": {"id": "g123", "name": "Running Shoes"},
            "segment_efforts": [],
            "laps": [
                {
                    "id": 1,
                    "name": "Lap 1",
                    "distance": 5000.0,
                    "elapsed_time": 1800,
                }
            ],
            "splits_metric": [{"distance": 1000, "elapsed_time": 360, "split": 1}],
        }
        a = DetailedActivity.from_dict(data)
        assert a.description == "Great run!"
        assert a.calories == 500.0
        assert a.gear is not None
        assert a.gear.id == "g123"
        assert len(a.laps) == 1
        assert a.laps[0].name == "Lap 1"
        assert len(a.splits_metric) == 1

    def test_updatable_activity(self):
        u = UpdatableActivity(name="Updated", description="New desc", commute=True)
        d = u.to_dict()
        assert d["name"] == "Updated"
        assert d["commute"] is True

    def test_lap(self):
        data = {
            "id": 1,
            "name": "Lap 1",
            "distance": 5000.0,
            "elapsed_time": 1800,
            "moving_time": 1750,
            "start_date": "2024-06-15T07:00:00Z",
            "lap_index": 0,
            "activity": {"id": 9876},
            "athlete": {"id": 123},
        }
        lap = Lap.from_dict(data)
        assert lap.distance == 5000.0
        assert lap.activity is not None
        assert lap.activity.id == 9876

    def test_comment(self):
        data = {
            "id": 1,
            "activity_id": 100,
            "text": "Nice ride!",
            "athlete": {"id": 456, "firstname": "Jane"},
            "created_at": "2024-06-15T10:00:00Z",
        }
        c = Comment.from_dict(data)
        assert c.text == "Nice ride!"
        assert c.athlete is not None
        assert c.athlete.firstname == "Jane"

    def test_activity_zone(self):
        data = {
            "score": 100,
            "type": "heartrate",
            "sensor_based": True,
            "distribution_buckets": [
                {"min": 0, "max": 120, "time": 600},
                {"min": 120, "max": 150, "time": 1200},
            ],
        }
        z = ActivityZone.from_dict(data)
        assert z.type == "heartrate"
        assert len(z.distribution_buckets) == 2
        assert z.distribution_buckets[0].time == 600

    def test_club_activity(self):
        data = {
            "name": "Group Ride",
            "distance": 50000,
            "type": "Ride",
            "sport_type": "Ride",
        }
        ca = ClubActivity.from_dict(data)
        assert ca.name == "Group Ride"
        assert ca.type == ActivityType.RIDE


class TestGearModels:
    def test_summary_gear(self):
        g = SummaryGear.from_dict(
            {"id": "b123", "name": "Trek", "primary": True, "distance": 5000.0}
        )
        assert g.id == "b123"
        assert g.primary is True

    def test_detailed_gear(self):
        g = DetailedGear.from_dict(
            {
                "id": "b123",
                "name": "Trek",
                "brand_name": "Trek",
                "model_name": "Domane",
                "frame_type": 3,
            }
        )
        assert g.brand_name == "Trek"
        assert g.model_name == "Domane"


class TestSegmentModels:
    def test_summary_segment(self):
        data = {
            "id": 1234,
            "name": "Alpe du Zwift",
            "activity_type": "Ride",
            "distance": 12000.0,
            "average_grade": 8.5,
            "maximum_grade": 14.0,
            "elevation_high": 1050.0,
            "elevation_low": 50.0,
            "climb_category": 1,
        }
        s = SummarySegment.from_dict(data)
        assert s.name == "Alpe du Zwift"
        assert s.average_grade == 8.5

    def test_detailed_segment(self):
        data = {
            "id": 1234,
            "name": "Test Segment",
            "hazardous": False,
            "star_count": 42,
            "created_at": "2020-01-01T00:00:00Z",
            "map": {"id": "s1234", "polyline": "abc"},
        }
        s = DetailedSegment.from_dict(data)
        assert s.star_count == 42
        assert s.map is not None
        assert s.map.polyline == "abc"

    def test_segment_effort(self):
        data = {
            "id": 1,
            "activity_id": 100,
            "elapsed_time": 300,
            "distance": 1000.0,
            "is_kom": False,
            "name": "Sprint",
            "average_watts": 250.0,
            "segment": {"id": 1234, "name": "Test"},
        }
        e = DetailedSegmentEffort.from_dict(data)
        assert e.name == "Sprint"
        assert e.segment is not None
        assert e.segment.id == 1234

    def test_summary_pr_effort(self):
        data = {
            "pr_activity_id": 100,
            "pr_elapsed_time": 120,
            "pr_date": "2024-01-15T00:00:00Z",
            "effort_count": 5,
        }
        pr = SummaryPRSegmentEffort.from_dict(data)
        assert pr.effort_count == 5

    def test_explorer_response(self):
        data = {
            "segments": [
                {"id": 1, "name": "Seg 1", "avg_grade": 5.0, "distance": 1000},
                {"id": 2, "name": "Seg 2", "avg_grade": 3.0, "distance": 2000},
            ]
        }
        r = ExplorerResponse.from_dict(data)
        assert len(r.segments) == 2
        assert r.segments[0].avg_grade == 5.0


class TestClubModels:
    def test_summary_club(self):
        data = {
            "id": 1,
            "name": "Test Club",
            "sport_type": "cycling",
            "member_count": 100,
            "private": False,
        }
        c = SummaryClub.from_dict(data)
        assert c.member_count == 100

    def test_detailed_club(self):
        data = {
            "id": 1,
            "name": "Test Club",
            "membership": "member",
            "admin": False,
            "owner": False,
            "following_count": 50,
        }
        c = DetailedClub.from_dict(data)
        assert c.membership == "member"


class TestRouteModel:
    def test_route(self):
        data = {
            "id": 1,
            "name": "Sunday Route",
            "distance": 50000.0,
            "elevation_gain": 500.0,
            "private": False,
            "starred": True,
            "map": {"id": "r1", "summary_polyline": "abc"},
            "segments": [{"id": 10, "name": "Hill"}],
            "waypoints": [{"title": "Start", "distance_into_route": 0.0}],
        }
        r = Route.from_dict(data)
        assert r.name == "Sunday Route"
        assert r.starred is True
        assert len(r.segments) == 1
        assert len(r.waypoints) == 1


class TestStreamModels:
    def test_stream_set_from_list(self):
        streams = [
            {
                "type": "time",
                "data": [0, 1, 2, 3],
                "series_type": "distance",
                "original_size": 4,
                "resolution": "high",
            },
            {
                "type": "distance",
                "data": [0.0, 10.0, 20.0, 30.0],
                "series_type": "distance",
                "original_size": 4,
                "resolution": "high",
            },
            {
                "type": "heartrate",
                "data": [120, 130, 140, 150],
                "series_type": "distance",
                "original_size": 4,
                "resolution": "high",
            },
        ]
        ss = StreamSet.from_stream_list(streams)
        assert ss.time is not None
        assert ss.time.data == [0, 1, 2, 3]
        assert ss.distance is not None
        assert ss.distance.data == [0.0, 10.0, 20.0, 30.0]
        assert ss.heartrate is not None
        assert ss.heartrate.data == [120, 130, 140, 150]
        assert ss.altitude is None
        assert ss.watts is None


class TestUploadModel:
    def test_upload(self):
        data = {
            "id": 1,
            "id_str": "1",
            "external_id": "ext_1",
            "error": None,
            "status": "Your activity is ready.",
            "activity_id": 100,
        }
        u = Upload.from_dict(data)
        assert u.status == "Your activity is ready."
        assert u.activity_id == 100


class TestStatsModels:
    def test_activity_total(self):
        data = {
            "count": 10,
            "distance": 100000.0,
            "moving_time": 36000,
            "elapsed_time": 40000,
            "elevation_gain": 2000.0,
        }
        t = ActivityTotal.from_dict(data)
        assert t.count == 10
        assert t.distance == 100000.0

    def test_activity_stats(self):
        data = {
            "biggest_ride_distance": 200000.0,
            "biggest_climb_elevation_gain": 1500.0,
            "recent_ride_totals": {"count": 5, "distance": 50000},
            "all_run_totals": {"count": 100, "distance": 500000},
        }
        s = ActivityStats.from_dict(data)
        assert s.biggest_ride_distance == 200000.0
        assert s.recent_ride_totals is not None
        assert s.recent_ride_totals.count == 5
        assert s.all_run_totals is not None
        assert s.all_run_totals.count == 100

    def test_zones(self):
        data = {
            "heart_rate": {
                "custom_zones": False,
                "zones": [
                    {"min": 0, "max": 120},
                    {"min": 120, "max": 160},
                ],
            },
            "power": {
                "zones": [
                    {"min": 0, "max": 100},
                ],
            },
        }
        z = Zones.from_dict(data)
        assert z.heart_rate is not None
        assert len(z.heart_rate.zones) == 2
        assert z.power is not None
        assert len(z.power.zones) == 1


class TestCommonModels:
    def test_polyline_map(self):
        m = PolylineMap.from_dict(
            {"id": "a1", "polyline": "abc", "summary_polyline": "a"}
        )
        assert m.polyline == "abc"
        d = m.to_dict()
        assert d["polyline"] == "abc"

    def test_split(self):
        s = Split.from_dict({"distance": 1000, "elapsed_time": 300, "split": 1})
        assert s.distance == 1000
        assert s.split == 1

    def test_fault(self):
        data = {
            "message": "Resource Not Found",
            "errors": [{"code": "not_found", "field": "", "resource": "Activity"}],
        }
        f = Fault.from_dict(data)
        assert f.message == "Resource Not Found"
        assert len(f.errors) == 1
        assert f.errors[0].code == "not_found"

    def test_empty_dict(self):
        m = PolylineMap.from_dict({})
        assert m.id is None


class TestEnums:
    def test_sport_type_from_string(self):
        st = SportType("Run")
        assert st == SportType.RUN
        assert str(st) == "Run"

    def test_activity_type_from_string(self):
        at = ActivityType("Ride")
        assert at == ActivityType.RIDE

    def test_enum_in_model(self):
        a = SummaryActivity.from_dict({"type": "Run", "sport_type": "TrailRun"})
        assert a.type == ActivityType.RUN
        assert a.sport_type == SportType.TRAIL_RUN

    def test_unknown_enum_passes_through(self):
        # API may add new types; we shouldn't crash
        a = SummaryActivity.from_dict({"sport_type": "FutureNewSport"})
        assert a.sport_type == "FutureNewSport"


class TestWebhookModels:
    def test_webhook_event_from_dict(self):
        data = {
            "object_type": "activity",
            "object_id": 1234567890,
            "aspect_type": "create",
            "owner_id": 9876,
            "subscription_id": 999,
            "event_time": 1516126040,
            "updates": {},
        }
        e = WebhookEvent.from_dict(data)
        assert e.object_type == "activity"
        assert e.object_id == 1234567890
        assert e.aspect_type == "create"
        assert e.owner_id == 9876
        assert e.subscription_id == 999
        assert e.event_time == 1516126040
        assert e.updates == {}

    def test_webhook_event_with_updates(self):
        data = {
            "object_type": "activity",
            "object_id": 1234567890,
            "aspect_type": "update",
            "owner_id": 9876,
            "subscription_id": 999,
            "event_time": 1516126040,
            "updates": {"title": "New Title", "type": "Run"},
        }
        e = WebhookEvent.from_dict(data)
        assert e.updates == {"title": "New Title", "type": "Run"}

    def test_webhook_event_deauthorization(self):
        data = {
            "object_type": "athlete",
            "object_id": 9876,
            "aspect_type": "update",
            "owner_id": 9876,
            "subscription_id": 999,
            "event_time": 1516126040,
            "updates": {"authorized": "false"},
        }
        e = WebhookEvent.from_dict(data)
        assert e.object_type == "athlete"
        assert e.aspect_type == "update"
        assert e.updates["authorized"] == "false"

    def test_webhook_event_round_trip(self):
        data = {
            "object_type": "activity",
            "object_id": 123,
            "aspect_type": "delete",
            "owner_id": 456,
            "subscription_id": 1,
            "event_time": 1700000000,
            "updates": {},
        }
        e = WebhookEvent.from_dict(data)
        d = e.to_dict()
        assert d["object_type"] == "activity"
        assert d["aspect_type"] == "delete"
        assert d["object_id"] == 123

    def test_webhook_subscription(self):
        data = {
            "id": 1,
            "callback_url": "https://example.com/webhook",
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
            "application_id": 12345,
        }
        s = WebhookSubscription.from_dict(data)
        assert s.id == 1
        assert s.callback_url == "https://example.com/webhook"
        assert s.application_id == 12345

    def test_webhook_validation_request(self):
        data = {
            "hub.mode": "subscribe",
            "hub.challenge": "15f7d1a91c1f40f8a748fd134752feb3",
            "hub.verify_token": "STRAVA",
        }
        r = WebhookValidationRequest.from_dict(data)
        assert r.mode == "subscribe"
        assert r.challenge == "15f7d1a91c1f40f8a748fd134752feb3"
        assert r.verify_token == "STRAVA"

    def test_webhook_validation_response_to_dict(self):
        r = WebhookValidationResponse(challenge="15f7d1a91c1f40f8a748fd134752feb3")
        d = r.to_dict()
        assert d == {"hub.challenge": "15f7d1a91c1f40f8a748fd134752feb3"}


class TestRoundTrip:
    def test_activity_round_trip(self):
        original = {
            "id": 1,
            "name": "Test",
            "distance": 5000.0,
            "type": "Run",
            "sport_type": "Run",
            "start_date": "2024-06-15T07:00:00+00:00",
            "trainer": False,
        }
        a = SummaryActivity.from_dict(original)
        d = a.to_dict()
        assert d["id"] == 1
        assert d["name"] == "Test"
        assert d["distance"] == 5000.0
        assert d["type"] == "Run"
        assert d["sport_type"] == "Run"
        assert d["trainer"] is False
