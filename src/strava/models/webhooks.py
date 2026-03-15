from __future__ import annotations

from dataclasses import dataclass, field

from strava.models._base import StravaModel
from strava.models._enums import WebhookAspectType, WebhookObjectType


@dataclass(slots=True, kw_only=True)
class WebhookEvent(StravaModel):
    object_type: WebhookObjectType | None = None
    object_id: int | None = None
    aspect_type: WebhookAspectType | None = None
    owner_id: int | None = None
    subscription_id: int | None = None
    event_time: int | None = None
    updates: dict[str, str] = field(default_factory=dict)


@dataclass(slots=True, kw_only=True)
class WebhookSubscription(StravaModel):
    id: int | None = None
    callback_url: str | None = None
    created_at: str | None = None
    updated_at: str | None = None
    application_id: int | None = None


@dataclass(slots=True, kw_only=True)
class WebhookValidationRequest(StravaModel):
    mode: str | None = None
    challenge: str | None = None
    verify_token: str | None = None

    _field_aliases = {
        "mode": "hub.mode",
        "challenge": "hub.challenge",
        "verify_token": "hub.verify_token",
    }


@dataclass(slots=True, kw_only=True)
class WebhookValidationResponse(StravaModel):
    challenge: str | None = None

    _field_aliases = {
        "challenge": "hub.challenge",
    }
