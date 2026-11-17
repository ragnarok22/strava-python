# Migration and Strava API Changes

[Quick start](../README.md#quick-start) · [Usage guide](usage.md) · [API reference](api.md)

This guide collects compatibility changes previously documented in the README.
See [CHANGELOG.md](../CHANGELOG.md) for versioned release history and
[Strava's reference](https://developers.strava.com/docs/reference/) for current
server-side requirements.

## API Hosts

The default API URL remains `https://www.strava.com/api/v3`. Strava's announced
future host, `https://api-v3.strava.com` (without `www`), becomes available
**January 4, 2027**. The SDK does not switch hosts automatically based on the
clock. Once that host is available, opt in explicitly on either client:

```python
import os

from strava import Strava

# Use only once Strava has made the future host available.
with Strava(
    access_token=os.environ["STRAVA_ACCESS_TOKEN"],
    base_url="https://api-v3.strava.com",
) as client:
    athlete = client.athletes.retrieve_authenticated()
```

OAuth endpoints remain independent of the API `base_url`.

## Activity and Athlete Identifiers

After **June 1, 2027**, Strava activity and athlete IDs may use 64-bit integers.
Python's `int` and the SDK's JSON parsing preserve these values exactly, so
existing code using `id` remains supported.

The `Meta`, `Summary`, and `Detailed` activity and athlete models also expose
`id_str: str | None`, including nested objects and the athlete in OAuth token
responses. Both fields preserve the values returned by Strava; neither is
generated from the other. Missing or null `id_str` values remain `None` and are
omitted by `to_dict()`.

All sync and async endpoints taking `activity_id` or `athlete_id` accept either
`int` or `str`, so you can pass `id_str` directly when available:

```python
import os

from strava import Strava

with Strava(access_token=os.environ["STRAVA_ACCESS_TOKEN"]) as client:
    athlete = client.athletes.retrieve_authenticated()
    if athlete.id_str is not None:
        stats = client.athletes.retrieve_stats(athlete.id_str)
    elif athlete.id is not None:
        stats = client.athletes.retrieve_stats(athlete.id)
```

Strava recommends `id_str` going forward. Prefer strings when sending data to
JavaScript, whose `Number` cannot represent every integer above `2**53 - 1`
exactly. For older responses without `id_str`, convert a non-null `id` to `str`
**in Python before serialization**, not after JavaScript has parsed it.
Review database schemas, bindings, and integrations for 32-bit integer limits.

## Retired Club Endpoints

Strava removed club activities, club members, and club administrators endpoints
on **September 1, 2026**. These SDK methods were removed from both `Strava` and
`AsyncStrava`:

- `clubs.list_activities()`
- `clubs.list_members()`
- `clubs.list_admins()`

Access now raises `AttributeError`. Remove calls and application features that
depend on these endpoints; Strava provides no documented replacements.
`clubs.retrieve()` and `clubs.list_authenticated()` remain supported.
`ClubActivity`, `ClubAthlete`, and their public exports remain available for
parsing existing data.

## Segment Exploration Access

Since **September 1, 2026**, `segments.explore()` is restricted to approved
Extended Access applications. A valid athlete token alone does not grant this
application-level permission.

## Token Revocation

`deauthorize()` is deprecated because Strava will retire `oauth/deauthorize`
on **June 1, 2027**. Prefer `revoke_token()` with your application credentials:

```python
import os

from strava import revoke_token

# Disconnects the token's authorization; do not run as a connectivity check.
revoke_token(
    client_id=os.environ["STRAVA_CLIENT_ID"],
    client_secret=os.environ["STRAVA_CLIENT_SECRET"],
    token=os.environ["STRAVA_ACCESS_TOKEN"],
    token_type_hint="access_token",
    timeout=30.0,
)
```

Async code should `await async_revoke_token(...)`; no deprecated async
deauthorization helper is provided. Both revoke helpers accept
`token_type_hint="refresh_token"` as well.

The compatibility `deauthorize()` helper accepts `timeout` and a caller-owned
sync `http_client`. When both `client_id` and `client_secret` are supplied, it
delegates to `revoke_token()`; otherwise it uses the retiring endpoint.
Supply both credentials or neither. See
[OAuth helper configuration](usage.md#oauth-helpers-and-httpx).

## Supplied HTTPX Clients

Previously, a supplied HTTPX client's auth, base URL, and timeout could take
precedence, and closing the SDK closed that HTTPX client. The current contract:

- Supply athlete-token and refresh settings to the SDK, not as HTTPX default auth.
- Move API URL and timeout overrides to the SDK constructor.
- Manage the supplied HTTPX client's lifetime yourself. SDK `close()` / context
  exit leaves it open; SDK-created clients are still closed by the SDK.
- SDK request settings do not mutate HTTPX's defaults. Other custom headers,
  transports, hooks, and connection pools remain reusable.
- Webhooks disable athlete-token auth and strip `Authorization` for each request.

The same ownership rules apply to the sync and async OAuth network helpers.
They now accept a keyword-only `timeout` (`httpx.Timeout | float | None`, default
`30.0`) and optional `http_client`. If you previously relied on HTTPX's default
timeout for a helper, pass the desired value explicitly. See
[HTTP client configuration](usage.md#http-client-ownership-and-configuration).

## OAuth Error Handling and Token Safety

OAuth HTTP failures now raise SDK exceptions instead of `httpx.HTTPStatusError`.
Update exception handlers for exchange, refresh, revoke, and deprecated
deauthorization helpers to catch `StravaError` or an appropriate subclass.
The new async helpers use the same mapping.

HTTPX transport and timeout exceptions are **not** wrapped; handle them
separately. Automatic refresh failures surface the mapped OAuth error before
the original request is sent, without replacing tokens or calling the
persistence callback. See the [error reference](api.md#errors).

Access and refresh tokens are no longer shown by `TokenResponse`'s `repr`.
Do not rely on its representation for serialization or token persistence.
Direct attributes and dataclass conversion still contain secrets; use secure
storage and redact request/response logs.

Concurrent expired-token requests through one client reuse a successful refresh.
Separate clients/processes are not coordinated. `on_token_refresh` is still a
synchronous callback, even for `AsyncStrava`; use nonblocking persistence
integration in an async application, not an `async def` callback. See
[automatic refresh](usage.md#automatic-token-refresh).

## Streams

All four stream methods return `StreamSet` and accept both keyed responses and
legacy lists of stream objects. `key_by_type=False` is no longer accepted and
raises `ValueError` before sending a request. Remove the argument or pass `True`.

`StreamSet.from_stream_list()` remains available for existing data.
`StreamSet.from_response()` handles either response shape. Unknown stream types
are ignored; an empty response creates an empty `StreamSet`.
See [stream usage](usage.md#streams).

## Comment Pagination

`activities.list_comments()` now uses opaque comment cursors rather than
page numbers. `page_size` controls the request size (default 30), and
`after_cursor` resumes from a saved cursor. `per_page` remains an alias;
`page_size` wins if both are supplied.

Do not decode, generate, or alter cursor values. Read `Comment.cursor` and store
it unchanged when resumable traversal is needed. Missing/invalid or cycling
cursors raise `RuntimeError` only when another page is needed.
See [comment cursor behavior](usage.md#comment-cursors).

## Visibility and Activity Tags

Manual creation, activity updates, and uploads now accept the documented
`visibility` and `tags` arguments. Existing `commute` remains supported, but
cannot be supplied in the same request as `tags`, even if the values are false
or empty. Use the `Commute` tag when migrating a call that sets other tags.
Only `followers_only` and `only_me` are supported as visibility overrides; these
do not relax privacy settings.

See [supported tags and request encoding](usage.md#activity-visibility-and-tags).
