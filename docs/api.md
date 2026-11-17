# Practical API Reference

[Quick start](../README.md#quick-start) · [Usage guide](usage.md) · [Migration](migration.md)

The SDK exposes 31 API resource endpoints and three webhook management endpoints.
Method names below are relative to an open `Strava` / `AsyncStrava` client.
See [Strava's official reference](https://developers.strava.com/docs/reference/)
for response schemas, server-side constraints, and access policies.

## Return Conventions

- **Model / `list[T]` / `bytes` / `None`:** a sync method sends a request
  immediately. On `AsyncStrava`, await the method to send the request.
- **`Paginator[T]`:** shorthand here for `SyncPaginator[T]` or
  `AsyncPaginator[T]`. Calling the method makes no request. Consume it with
  `for` / `async for`, `.pages()`, or `.collect(max_items=...)`.
  Do **not** await async paginator creation.
- `per_page` is page size, not total result count. Use `collect(max_items=N)`
  for a total bound; consuming an unbounded paginator can fetch all history.
- Methods named `list` are not necessarily lazy: `segment_efforts.list()`,
  `activities.list_laps()`, `activities.list_zones()`, and `webhooks.list()`
  return eager lists.
- Optional request arguments default to the SDK's `NOT_GIVEN` sentinel. Omission
  means "do not send"; it is not equivalent to sending `None`.

Keep the client open until paginator consumption finishes. See
[pagination examples and cursor behavior](usage.md#pagination).

## Scopes

Request only the scopes you need using `build_authorization_url(scopes=[...])`.
Athletes can decline individual permissions. Check granted scopes during OAuth
and store them with the connection; the SDK does not preflight scope checks.

| Scope | Purpose |
| --- | --- |
| `read` | Public profile, route, segment, and other public data |
| `read_all` | Private routes/segments and athlete-specific segment details |
| `profile:read_all` | Full athlete profile and heart-rate/power zones |
| `profile:write` | Update athlete weight; star/unstar segments |
| `activity:read` | Everyone/Followers activities, excluding privacy-zone data |
| `activity:read_all` | Also Only Me activities and privacy-zone data |
| `activity:write` | Create manual activities/uploads; edit accessible activities |

In the tables, **activity read** means `activity:read`, or `activity:read_all`
when Only Me activities/privacy data are needed. **—** means the endpoint
description does not state an additional endpoint-specific scope; it does not
mean anonymous access is supported. All non-webhook resources use athlete-token
authentication. Scopes do not bypass ownership, subscription, or application
access-tier restrictions. See
[Strava's scope definitions](https://developers.strava.com/docs/authentication/#detailsaboutrequestingaccess).

## Activities

| Method | Return | Scope / important behavior |
| --- | --- | --- |
| [`activities.create(*, name, sport_type, start_date_local, elapsed_time, ...)`](https://developers.strava.com/docs/reference/#api-Activities-createActivity) | `DetailedActivity` | `activity:write`; manual activity; distance in meters, elapsed time in seconds |
| [`activities.retrieve(activity_id, *, include_all_efforts=...)`](https://developers.strava.com/docs/reference/#api-Activities-getActivityById) | `DetailedActivity` | Activity read; owned by the authenticated athlete |
| [`activities.update(activity_id, ...)`](https://developers.strava.com/docs/reference/#api-Activities-updateActivityById) | `DetailedActivity` | `activity:write`; also `activity:read_all` for Only Me |
| [`activities.list(*, before=..., after=..., per_page=...)`](https://developers.strava.com/docs/reference/#api-Activities-getLoggedInAthleteActivities) | `Paginator[SummaryActivity]` | Activity read; `before` / `after` are Unix seconds |
| [`activities.list_comments(activity_id, *, page_size=..., after_cursor=..., per_page=...)`](https://developers.strava.com/docs/reference/#api-Activities-getCommentsByActivityId) | `Paginator[Comment]` | Activity read; cursor pagination; `page_size` overrides `per_page` |
| [`activities.list_kudoers(activity_id, *, per_page=...)`](https://developers.strava.com/docs/reference/#api-Activities-getKudoersByActivityId) | `Paginator[SummaryAthlete]` | Activity read |
| [`activities.list_laps(activity_id)`](https://developers.strava.com/docs/reference/#api-Activities-getLapsByActivityId) | `list[Lap]` | Activity read; eager |
| [`activities.list_zones(activity_id)`](https://developers.strava.com/docs/reference/#api-Activities-getZonesByActivityId) | `list[ActivityZone]` | Activity read; subscription feature; eager |

Creation accepts optional `type`, `description`, `distance`, `trainer`, and
`commute`. Updates accept `name`, `description`, `type`, `sport_type`, `gear_id`,
`trainer`, `commute`, and `hide_from_home`. Both also accept `visibility` and
`tags`; do not combine `tags` and legacy `commute`. See
[visibility, tag names, and encoding](usage.md#activity-visibility-and-tags).

## Athletes

| Method | Return | Scope / important behavior |
| --- | --- | --- |
| [`athletes.retrieve_authenticated()`](https://developers.strava.com/docs/reference/#api-Athletes-getLoggedInAthlete) | `DetailedAthlete` | `profile:read_all` for full data; a lower-scope summary still parses into this model with absent fields unset |
| [`athletes.update_authenticated(*, weight)`](https://developers.strava.com/docs/reference/#api-Athletes-updateLoggedInAthlete) | `DetailedAthlete` | `profile:write`; weight in kilograms |
| [`athletes.retrieve_zones()`](https://developers.strava.com/docs/reference/#api-Athletes-getLoggedInAthleteZones) | `Zones` | `profile:read_all` |
| [`athletes.retrieve_stats(athlete_id)`](https://developers.strava.com/docs/reference/#api-Athletes-getStats) | `ActivityStats` | —; includes only Everyone activities |

## Clubs and Gear

| Method | Return | Scope / important behavior |
| --- | --- | --- |
| [`clubs.retrieve(club_id)`](https://developers.strava.com/docs/reference/#api-Clubs-getClubById) | `DetailedClub` | — |
| [`clubs.list_authenticated(*, per_page=...)`](https://developers.strava.com/docs/reference/#api-Clubs-getLoggedInAthleteClubs) | `Paginator[SummaryClub]` | —; authenticated athlete's clubs |
| [`gear.retrieve(gear_id)`](https://developers.strava.com/docs/reference/#api-Gears-getGearById) | `DetailedGear` | —; gear ID is a string such as a bike/shoe identifier |

Club activities, members, and administrators endpoints have been
[retired and removed](migration.md#retired-club-endpoints).

## Routes

| Method | Return | Scope / important behavior |
| --- | --- | --- |
| [`routes.retrieve(route_id)`](https://developers.strava.com/docs/reference/#api-Routes-getRouteById) | `Route` | `read_all` for private routes |
| [`routes.export_gpx(route_id)`](https://developers.strava.com/docs/reference/#api-Routes-getRouteAsGPX) | `bytes` | `read_all` for private routes; raw GPX data, not a filename |
| [`routes.export_tcx(route_id)`](https://developers.strava.com/docs/reference/#api-Routes-getRouteAsTCX) | `bytes` | `read_all` for private routes; raw TCX data, not a filename |
| [`routes.list_by_athlete(athlete_id, *, per_page=...)`](https://developers.strava.com/docs/reference/#api-Routes-getRoutesByAthleteId) | `Paginator[Route]` | Authenticated athlete's routes; private routes filtered without `read_all` |

## Segments and Segment Efforts

| Method | Return | Scope / important behavior |
| --- | --- | --- |
| [`segments.retrieve(segment_id)`](https://developers.strava.com/docs/reference/#api-Segments-getSegmentById) | `DetailedSegment` | `read_all` for private segments or athlete-specific details |
| [`segments.explore(*, bounds, activity_type=..., min_cat=..., max_cat=...)`](https://developers.strava.com/docs/reference/#api-Segments-exploreSegments) | `ExplorerResponse` | Approved Extended Access apps only; up to 10 matching segments |
| [`segments.list_starred(*, per_page=...)`](https://developers.strava.com/docs/reference/#api-Segments-getLoggedInAthleteStarredSegments) | `Paginator[SummarySegment]` | Private segments filtered without `read_all` |
| [`segments.star(segment_id, *, starred)`](https://developers.strava.com/docs/reference/#api-Segments-starSegment) | `DetailedSegment` | `profile:write`; `False` unstars |
| [`segment_efforts.retrieve(effort_id)`](https://developers.strava.com/docs/reference/#api-SegmentEfforts-getSegmentEffortById) | `DetailedSegmentEffort` | —; subscription required; effort from an activity owned by the athlete |
| [`segment_efforts.list(*, segment_id, start_date_local=..., end_date_local=..., per_page=...)`](https://developers.strava.com/docs/reference/#api-SegmentEfforts-getEffortsBySegmentId) | `list[DetailedSegmentEffort]` | —; subscription required; one eager response, **not a paginator** |

`bounds` is `[southwest_latitude, southwest_longitude, northeast_latitude,
northeast_longitude]` in decimal degrees. Segment-effort date filters are ISO 8601
local date-time strings. `segment_efforts.list(per_page=...)` changes the size of
that single response; the SDK does not automatically retrieve further pages.

## Streams

| Method | Return | Scope / important behavior |
| --- | --- | --- |
| [`streams.get_activity_streams(activity_id, *, keys, key_by_type=True)`](https://developers.strava.com/docs/reference/#api-Streams-getActivityStreams) | `StreamSet` | Activity read |
| [`streams.get_route_streams(route_id)`](https://developers.strava.com/docs/reference/#api-Streams-getRouteStreams) | `StreamSet` | `read_all` for private routes; no `keys` argument |
| [`streams.get_segment_effort_streams(effort_id, *, keys, key_by_type=True)`](https://developers.strava.com/docs/reference/#api-Streams-getSegmentEffortStreams) | `StreamSet` | `read_all`; athlete's own effort |
| [`streams.get_segment_streams(segment_id, *, keys, key_by_type=True)`](https://developers.strava.com/docs/reference/#api-Streams-getSegmentStreams) | `StreamSet` | `read_all` for private segments |

`keys` is a list of stream names: `time`, `distance`, `latlng`, `altitude`,
`velocity_smooth`, `heartrate`, `cadence`, `watts`, `temp`, `moving`, or
`grade_smooth`. A stream may be absent even when requested. See
[stream normalization and examples](usage.md#streams).

## Uploads

| Method | Return | Scope / important behavior |
| --- | --- | --- |
| [`uploads.create(*, file=..., sport_type=..., name=..., description=..., trainer=..., commute=..., data_type=..., external_id=..., visibility=..., tags=...)`](https://developers.strava.com/docs/reference/#api-Uploads-createUpload) | `Upload` | `activity:write`; submits a file for processing, does not wait for a finished activity |
| [`uploads.retrieve(upload_id)`](https://developers.strava.com/docs/reference/#api-Uploads-getUploadById) | `Upload` | `activity:write`; poll no more than once per second |

`file` accepts a binary file object or `bytes`. Specify the matching `data_type`,
for example `"fit"`, `"tcx"`, `"gpx"`, or strength-training `"json"`.
Inspect `Upload.activity_id`, `error`, and `status` to determine processing
outcome. See [strength-training formats and polling](usage.md#strength-training-uploads)
and [visibility/tags](usage.md#activity-visibility-and-tags).

## Webhooks

| Method | Return | Authentication / important behavior |
| --- | --- | --- |
| `webhooks.create(*, client_id, client_secret, callback_url, verify_token)` | `WebhookSubscription` | Application credentials; Strava verifies the callback |
| `webhooks.list(*, client_id, client_secret)` | `list[WebhookSubscription]` | Application credentials; eager |
| `webhooks.delete(subscription_id, *, client_id, client_secret)` | `None` | Application credentials |

Webhook management bypasses athlete-token authentication and automatic refresh.
There is one subscription per application. Activity events need the athlete's
`activity:read` consent. See [setup and callback handling](usage.md#webhook-subscriptions)
and the [official guide](https://developers.strava.com/docs/webhooks/).

## OAuth Helpers

`build_authorization_url(client_id, redirect_uri, *, scopes=None, state=None,
approval_prompt="auto")` returns a URL string without a request.
`approval_prompt="force"` always requests the authorization prompt.
Generate, store, validate, and consume `state` in your application.

| Sync helper | Async helper | Return |
| --- | --- | --- |
| `exchange_token(client_id, client_secret, code, ...)` | `async_exchange_token(...)` | `TokenResponse` |
| `refresh_access_token(client_id, client_secret, refresh_token, ...)` | `async_refresh_access_token(...)` | `TokenResponse` |
| `revoke_token(client_id, client_secret, token, *, token_type_hint=None, ...)` | `async_revoke_token(...)` | `None` |

All six network helpers accept keyword-only `timeout` (an `httpx.Timeout`,
seconds as `float`, or `None`; default `30.0`) and `http_client` (sync/async
HTTPX client as appropriate; default `None`). Await async helpers.
`TokenResponse` includes `access_token`, `refresh_token`, `expires_at`,
`expires_in`, `token_type`, optional `scope`, and optional `athlete`.
`revoke_token` uses HTTP Basic authentication with your application credentials.

Deprecated sync-only `deauthorize(access_token, *, client_id=None,
client_secret=None, timeout=30.0, http_client=None)` returns `None`. With both
credentials it delegates to revocation; otherwise it uses the retiring endpoint.
See [secure OAuth integration and client ownership](usage.md#oauth-authorization)
and [deauthorization migration](migration.md#token-revocation).

## Models, Identifiers, and Units

Models are typed dataclasses with `from_dict()` / `to_dict()` conversion.
Optional scalar fields and optional lists normally default to `None`. Collections
declared with list default factories are empty when omitted. `to_dict()` omits
`None` but preserves `False` and zero.
Known `SportType` / `ActivityType` strings become enum members; unknown strings
are retained for forward compatibility. Activity responses also expose optional
`visibility: ActivityVisibility | str | None` and
`tags: list[ActivityTag | str] | None`. Request tags are boolean mappings instead;
`UpdatableActivity.tags` is an optional `dict[str, bool]`.

`SportType` includes Strava's April 2026 additions: `BASKETBALL`, `CRICKET`,
`DANCE`, `PADEL`, `PHYSICAL_THERAPY`, and `VOLLEYBALL`.

All endpoints taking `activity_id` or `athlete_id` accept `int | str`. Activity
and athlete models preserve optional `id_str` alongside `id`, including nested
models and the athlete in OAuth responses. Neither value is generated from the
other. See [64-bit ID migration and JavaScript safety](migration.md#activity-and-athlete-identifiers).
Other endpoint IDs retain their documented types (`gear_id` is a string;
route/segment/effort/upload/club/subscription IDs are integers).

| Value | Unit / format |
| --- | --- |
| Distance and elevation | Meters |
| Elapsed / moving time, stream time, `utc_offset` | Seconds |
| Speed / `velocity_smooth` | Meters per second, not km/h |
| Athlete weight, strength-set weight | Kilograms |
| Heart rate | Beats per minute |
| Power / `watts` | Watts |
| `kilojoules` / `calories` | Kilojoules / kilocalories respectively |
| Temperature | Degrees Celsius |
| Grade | Percent |
| Coordinates / `latlng` | `[latitude, longitude]` in decimal degrees |
| OAuth `expires_at`, activity `before` / `after` filters | Unix epoch seconds |
| Request date-time strings | ISO 8601, with local-time semantics where the parameter says `_local` |

Model datetime parsing normalizes offset-aware values to UTC and treats naive
values as UTC. This also applies to `start_date_local`; the parser does not infer
an athlete's timezone from the field name. Preserve `timezone` / `utc_offset`
when interpreting local wall-clock data. `to_dict()` serializes datetimes as
ISO timestamps with an offset.

Resolved model type hints are cached per concrete class to avoid repeated type
introspection during parsing. This is an internal parsing optimization, not a
guarantee of an end-to-end SDK speedup.

### Activity and Segment Response Fields

Both `SummaryActivity` and `DetailedActivity` expose optional `resource_state`,
`has_heartrate`, `average_heartrate`, `max_heartrate`, `average_cadence`,
`average_temp`, `pr_count`, `suffer_score`, and `utc_offset` (seconds).
Both `SummarySegment` and `DetailedSegment` expose optional `resource_state`,
`starred`, and `hazardous`.

`athlete_segment_stats` remains a `SummarySegmentEffort` on both segment models.
It preserves the documented effort fields (`id`, `activity_id`, `elapsed_time`,
`start_date`, `start_date_local`, `distance`, and `is_kom`) and accepts the PR
fields returned by Strava's reference examples: `pr_elapsed_time`, `pr_date`,
`effort_count`, and optional `pr_activity_id`. Either or both shapes are supported
without changing `isinstance(stats, SummarySegmentEffort)` compatibility.
`athlete_pr_effort` continues to use `SummaryPRSegmentEffort`.

`pr_date` is parsed as a UTC-aware `datetime`; a date-only value such as
`"1993-04-03"` becomes midnight UTC and serializes with an offset. This supports
both shapes in Strava's [segment schema and examples](https://developers.strava.com/docs/reference/#api-models-DetailedSegment).

## Rate Limits

`client.rate_limits` is a `RateLimitInfo` snapshot of the **last API resource
response**, including HTTP error responses. It is not a cumulative SDK counter
or a cross-client coordinator. OAuth helpers do not populate this property.
The fields are `None` before a response or when the relevant header is absent
or invalid:

- `limit_15min`, `limit_daily`, `usage_15min`, `usage_daily`
- `read_limit_15min`, `read_limit_daily`, `read_usage_15min`, `read_usage_daily`

`exceeded` is `True` if any known usage value is **greater than or equal to** its
matching known limit; otherwise it is `False`. A false value with missing
headers does not prove capacity is available, and a snapshot may already be
stale when other clients share the application's limits.

Using an open `client`, after a resource request:

```python
athlete = client.athletes.retrieve_authenticated()
limits = client.rate_limits
print(limits.usage_15min, limits.limit_15min)
if limits.exceeded:
    print("Pause requests and consult the application's rate-limit policy")
```

Strava applies overall and separate read/non-upload limits. The latter is not
limited to HTTP GET requests. Short windows reset at natural 15-minute
boundaries; daily limits reset at midnight UTC. Read actual headers/settings
rather than hard-coding default quotas. HTTP 429 raises `RateLimitError`, which
also exposes the eight limit/usage fields. The SDK does not sleep, retry, or
throttle automatically. See [Strava's rate-limit guide](https://developers.strava.com/docs/rate-limits/).

## Errors

Resource requests, sync/async OAuth helpers, deprecated `deauthorize()`, and
automatic refresh map HTTP error responses to the same hierarchy:

| HTTP status | Exception |
| --- | --- |
| 400, 422 | `ValidationError` |
| 401 | `AuthenticationError` |
| 403 | `AuthorizationError` |
| 404 | `NotFoundError` |
| 429 | `RateLimitError` |
| 5xx | `ServerError` |
| Other 4xx | `StravaError` |

All are subclasses of `StravaError` and preserve `status_code`, `message`, the
original HTTP `response`, and the JSON `fault` dictionary when available.
Non-JSON error responses use response text as the message. Treat responses,
faults, and requests as potentially sensitive rather than logging them wholesale.

**Transport failures and timeouts remain HTTPX exceptions**, such as
`httpx.TransportError` and `httpx.TimeoutException`; they are not wrapped in
`StravaError`. Response decoding/model parsing errors are also not guaranteed
to be SDK HTTP exceptions.

Using an open `client`:

```python
import httpx

from strava import AuthenticationError, RateLimitError, StravaError

try:
    activity = client.activities.retrieve(123)
except AuthenticationError:
    print("Check credentials and the connection's authorization")
except RateLimitError as error:
    print(f"Rate limited: {error.usage_15min}/{error.limit_15min}")
except StravaError as error:
    print(f"Strava API error: {error.status_code}")
except httpx.TimeoutException:
    print("The request timed out")
except httpx.TransportError:
    print("The request failed at the transport layer")
```

A 401 does not reliably identify an expired token. `TokenExpiredError` remains
exported as an `AuthenticationError` subclass for compatibility, but the SDK
does not automatically raise it.

There are **no automatic retries**, exponential backoff, or rate-limit sleeps.
If your supplied HTTPX transport has a retry policy, that is separate from SDK
behavior. Implement a bounded application policy only where safe: a timed-out
create/upload may have succeeded, so blindly replaying writes can duplicate data.
Automatic pre-request token refresh is not a retry of a failed API request.
