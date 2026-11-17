# Usage Guide

[Quick start](../README.md#quick-start) · [API reference](api.md) · [Migration](migration.md)

Examples require a registered Strava application, real credentials supplied
securely by your application, and the appropriate [OAuth scopes](api.md#scopes).
They make real API requests. Examples that create activities, upload files, or
manage webhooks change your Strava data or application configuration.

## OAuth Authorization

Register a callback domain in your [API settings](https://www.strava.com/settings/api).
Use an HTTPS callback in production and request only the scopes your app needs.
The SDK builds URLs and exchanges tokens; your web application must authenticate
its own session and protect the callback against cross-site request forgery.

The following is a **framework-neutral integration sketch, not a standalone web
server**. Implement `StateStore` with a shared server-side session store or
database. Its `take()` operation must atomically remove and return an unexpired
value, and return `None` for an expired, missing, or already consumed value.
Bind the record to the initiating browser session, not an arbitrary session ID
accepted from the callback query string.

```python
import os
import secrets
from collections.abc import Mapping
from typing import Protocol

from strava import TokenResponse, build_authorization_url, exchange_token


class StateStore(Protocol):
    def put(self, session_id: str, state: str, *, ttl_seconds: int) -> None: ...

    def take(self, session_id: str) -> object: ...


def authorization_url(session_id: str, states: StateStore) -> str:
    state = secrets.token_urlsafe(32)
    states.put(session_id, state, ttl_seconds=600)
    return build_authorization_url(
        client_id=os.environ["STRAVA_CLIENT_ID"],
        redirect_uri=os.environ["STRAVA_REDIRECT_URI"],
        scopes=["read", "activity:read"],
        state=state,
    )


def finish_authorization(
    session_id: str, query: Mapping[str, object], states: StateStore
) -> TokenResponse:
    # Consume once, including on invalid or denied callbacks.
    expected = states.take(session_id)
    received = query.get("state")
    if (
        not isinstance(expected, str)
        or not expected
        or not expected.isascii()
        or not isinstance(received, str)
        or not received
        or not received.isascii()
        or not secrets.compare_digest(expected, received)
    ):
        raise ValueError("Invalid or expired OAuth state")

    if query.get("error") is not None:
        raise ValueError("Strava authorization was not granted")

    code = query.get("code")
    if not isinstance(code, str) or not code:
        raise ValueError("Missing authorization code")

    return exchange_token(
        client_id=os.environ["STRAVA_CLIENT_ID"],
        client_secret=os.environ["STRAVA_CLIENT_SECRET"],
        code=code,
    )
```

Redirect the browser to the returned URL. On the callback, pass the authenticated
browser's session ID and parsed query parameters to `finish_authorization()`.
Reject duplicate `state` or `code` parameters in your framework's query adapter.
Secure session cookies with `Secure`, `HttpOnly`, and an appropriate `SameSite`
policy. A new authorization attempt replaces the pending state in this sketch.

Persist the returned tokens securely **before** considering the account connected:

- Keep client secrets and refresh tokens on the server, never in browser storage,
  URLs, source control, or logs. Use a secret manager for application credentials
  and encrypted, access-controlled storage for athlete tokens.
- Store `access_token`, the **latest** `refresh_token`, and `expires_at` together;
  refresh tokens can rotate. Persist updates atomically and scope records to the
  correct application user/athlete.
- `expires_at` is a Unix timestamp in seconds; `expires_in` is a duration in seconds.
- Check granted scopes, not just requested scopes. `tokens.scope` preserves
  Strava's space-delimited granted scopes and may be `None`; the athlete can
  decline permissions. The callback also reports granted scopes. Do not assume
  that an omitted field grants access.
- `tokens.athlete` is a typed `SummaryAthlete` when supplied. It and `scope`
  default to `None` when absent, including in refresh responses.

`TokenResponse` hides access and refresh tokens in its `repr`, but that is not a
general logging safeguard: direct attributes, dataclass conversion, HTTP request
bodies/headers, and callback query strings can still expose secrets. Redact them
from application, proxy, HTTPX hook, and exception logs.

For an async callback, perform the same state validation and one-time consumption
using your async session store, then use `await async_exchange_token(...)`.
Do not call the blocking `exchange_token()` from an event-loop handler. See
[Strava's authentication guide](https://developers.strava.com/docs/authentication/).

### OAuth Helpers and HTTPX

| Synchronous helper | Asynchronous helper | Return |
| --- | --- | --- |
| `exchange_token(client_id, client_secret, code, ...)` | `await async_exchange_token(...)` | `TokenResponse` |
| `refresh_access_token(client_id, client_secret, refresh_token, ...)` | `await async_refresh_access_token(...)` | `TokenResponse` |
| `revoke_token(client_id, client_secret, token, ...)` | `await async_revoke_token(...)` | `None` |

All six helpers accept keyword-only `timeout: httpx.Timeout | float | None = 30.0`
and `http_client`. Use an `httpx.Client` with sync helpers and an
`httpx.AsyncClient` with async helpers. A float applies HTTPX's phase timeouts;
pass `httpx.Timeout(...)` for fine-grained control or `None` to disable timeouts.
These are not an overall deadline for the complete OAuth flow.

Supplied HTTPX clients remain caller-owned, open, and unmodified. The helper's
timeout overrides their default timeout for that request. Without a supplied
client, the helper creates and closes its own. Helpers use Strava's OAuth
endpoints independently of the API client's `base_url`; SDK authentication takes
precedence over a supplied client's default auth/`Authorization` header.

This function can be called after validating the OAuth callback state:

```python
import os

import httpx

from strava import TokenResponse, async_exchange_token


async def exchange_validated_code(code: str) -> TokenResponse:
    async with httpx.AsyncClient() as http:
        return await async_exchange_token(
            client_id=os.environ["STRAVA_CLIENT_ID"],
            client_secret=os.environ["STRAVA_CLIENT_SECRET"],
            code=code,
            timeout=httpx.Timeout(30.0, connect=5.0),
            http_client=http,
        )
```

For manual refresh, call `refresh_access_token()` or
`await async_refresh_access_token()` with the latest stored refresh token, then
atomically save the returned credentials. For revocation, pass the token and
optionally `token_type_hint="access_token"` or `"refresh_token"` to
`revoke_token()` / `async_revoke_token()`, then remove local credentials according
to your application's disconnect policy.

`deauthorize(access_token=..., timeout=..., http_client=...)` remains as a
deprecated sync-only compatibility helper; there is no `async_deauthorize`.
With both `client_id` and `client_secret`, it delegates to `revoke_token()`;
without them, it calls the retiring `oauth/deauthorize` endpoint. Provide both
credentials or neither. Prefer the revoke helpers for new integrations.

### Automatic Token Refresh

Provide refresh credentials and an expiration timestamp to either client.
This application helper expects a persistence callback implemented by your app:

```python
import os
from collections.abc import Callable

from strava import DetailedAthlete, Strava, TokenResponse


def fetch_athlete(
    tokens: TokenResponse,
    persist_tokens: Callable[[str, str, int], None],
) -> DetailedAthlete:
    with Strava(
        access_token=tokens.access_token,
        client_id=os.environ["STRAVA_CLIENT_ID"],
        client_secret=os.environ["STRAVA_CLIENT_SECRET"],
        refresh_token=tokens.refresh_token,
        expires_at=tokens.expires_at,
        on_token_refresh=persist_tokens,
    ) as client:
        return client.athletes.retrieve_authenticated()
```

Before an API request, the SDK checks `expires_at` and refreshes an expired token
when all refresh credentials are present. A per-client lock and second expiry
check let concurrent requests reuse successfully refreshed credentials instead
of refreshing the same expired token independently. This does not coordinate
separate SDK clients, processes, or application workers; coordinate shared token
records at the application level.

`on_token_refresh(access_token, refresh_token, expires_at)` runs synchronously,
including with `AsyncStrava`. Do not pass an `async def` callback or perform
blocking database/network I/O on an async event loop. If storage needs async I/O,
you can explicitly `await async_refresh_access_token(...)` and await durable
storage before issuing API calls, or implement a nonblocking handoff with
application-defined durability and failure handling. Always retain the newest
rotated refresh token.

If the persistence callback raises, its exception propagates after the
in-memory tokens have been updated. This does not roll back the OAuth operation;
your application must recover durable storage of the rotated credentials.

If refresh receives an HTTP error, the SDK raises the mapped OAuth error before
sending the original API request; tokens remain unchanged and the callback is
not called. A 401 by itself does not trigger a response retry or establish that
the token expired. See [error handling](api.md#errors).

## HTTP Client Ownership and Configuration

Pass `http_client=httpx.Client(...)` to `Strava`, or an `httpx.AsyncClient` to
`AsyncStrava`, to reuse a transport, connection pool, event hooks, and custom
default headers. The SDK applies its own settings to each resource request:

- `access_token` and the SDK's OAuth refresh credentials control authentication,
  overriding the supplied client's auth handler and default `Authorization`
  header. Webhook requests disable token authentication and remove
  `Authorization` entirely.
- `base_url` controls the API destination, including its path prefix. Its default
  is `https://www.strava.com/api/v3`, even if the supplied client has another URL.
- The SDK's `timeout` controls requests and automatic OAuth refresh, defaulting
  to 30 seconds even if the supplied client has another timeout. Refresh uses
  Strava's token endpoint independently of the API base URL.

The SDK does not mutate the supplied client's `base_url`, `timeout`, `auth`, or
default headers. Other custom default headers are retained on resource requests.
You own the supplied client: SDK `close()` and context exit leave it open.
SDK-created HTTP clients are closed by the SDK.

```python
import os

import httpx

from strava import Strava

with httpx.Client(headers={"X-App": "my-app"}) as http:
    with Strava(
        access_token=os.environ["STRAVA_ACCESS_TOKEN"],
        timeout=10.0,
        http_client=http,
    ) as client:
        athlete = client.athletes.retrieve_authenticated()
    # `http` remains open until its own context exits.
```

The same ownership rules apply to `AsyncStrava`; use `async with` for both clients
or close the supplied client yourself with `await http.aclose()`.
Configure proxy/TLS behavior, connection limits, and custom transports on HTTPX.
Do not attach real tokens to an untrusted API `base_url` or transport. See
[HTTPX timeouts](https://www.python-httpx.org/advanced/timeouts/) and
[transports](https://www.python-httpx.org/advanced/transports/).

## Pagination

In the following snippets, `client` and `async_client` are open, authenticated
`Strava` and `AsyncStrava` instances. See the [quick start](../README.md#quick-start)
for complete client setup.

```python
# Iterate one item at a time; this can fetch the entire history.
for activity in client.activities.list():
    print(activity.name)

# Collect all results eagerly; this is not limited by per_page.
all_activities = client.activities.list().collect()

# Limit the total results.
first_50 = client.activities.list(per_page=50).collect(max_items=50)

# Iterate page by page.
for page in client.activities.list(per_page=50).pages():
    print(f"Got {len(page)} activities")
```

Creating a paginator makes no request. Iteration and `.pages()` fetch pages on
demand; `.collect()` returns an eager list. `per_page` controls page size, not
the total. Page-number pagination continues until Strava returns an empty page,
even if an intermediate page is shorter than `per_page`.

`collect(max_items=0)` returns an empty list without a request; negative limits
raise `ValueError`. A positive limit stops as soon as enough items have been
collected, without fetching another page. It can still fetch a full page and
return only the requested number of items.

Not every method named `list` returns a paginator. In particular,
`segment_efforts.list()` returns a **single eager list**, not an iterator across
all pages. `activities.list_laps()`, `activities.list_zones()`, and
`webhooks.list()` also return eager lists. See [return types](api.md#return-conventions).

### Comment Cursors

`activities.list_comments()` uses cursor pagination and sends only `page_size`
and, when present, `after_cursor`. The default page size is 30. `per_page` remains
a backward-compatible alias; **`page_size` wins when both are supplied**.

```python
comments = client.activities.list_comments(123, page_size=50)
for comment in comments:
    print(comment.text)
```

Each `Comment` exposes an optional `cursor`. To resume, pass a previously saved
cursor unchanged as `after_cursor`:

```python
# `saved_cursor` is an opaque string saved by your application.
next_comments = client.activities.list_comments(
    123, page_size=50, after_cursor=saved_cursor
).collect(max_items=20)
```

The paginator uses the last raw comment's cursor for the next page without
decoding or modifying it. Short pages continue until an empty response.
If continuation requires a missing, invalid, repeated, or cycling cursor, it
raises `RuntimeError` rather than looping indefinitely. Validation is deferred
until another page is needed, so bounded collection and stopping after the
current page do not raise unnecessarily.

Async paginators provide the same behavior. Inside an async function, use
`async for`, `async for page in paginator.pages()`, or
`await paginator.collect(...)`; do not await the paginator factory:

```python
async for comment in async_client.activities.list_comments(123, page_size=50):
    print(comment.text)

comments = await async_client.activities.list_comments(123).collect(max_items=20)
```

## Activity Visibility and Tags

`activities.create()`, `activities.update()`, and `uploads.create()` accept:

- `visibility="followers_only"` or `"only_me"` to request a **more restrictive**
  visibility setting. These options cannot make an activity public or relax its
  existing privacy restrictions.
- `tags`, a dictionary of case-sensitive keys `WithPet`, `Recovery`,
  `Competition`, `ForACause`, or `Commute` to boolean values. `True` adds a tag;
  `False` removes it. Other read-only `Mapping` objects are also accepted.

You may also use `ActivityVisibility.FOLLOWERS_ONLY` / `.ONLY_ME` and
`ActivityTag` keys, imported from `strava`, instead of strings. The accepted
mapping types are `Mapping[str, bool]` or `Mapping[ActivityTag, bool]`.
Tag enum members are `WITH_PET`, `RECOVERY`, `COMPETITION`, `FOR_A_CAUSE`, and
`COMMUTE`.

Do not supply legacy `commute` and `tags` in the same request, even if
`commute=False` or `tags={}`. Use `tags={"Commute": True}` or
`tags={"Commute": False}` instead. Omit a keyword to leave it unspecified;
`None` is not a substitute for omission.

This example **creates a real manual activity** and requires `activity:write`:

```python
import os
from datetime import datetime

from strava import ActivityTag, ActivityVisibility, SportType, Strava

with Strava(access_token=os.environ["STRAVA_ACCESS_TOKEN"]) as client:
    activity = client.activities.create(
        name="Recovery run",
        sport_type=SportType.RUN,
        start_date_local=datetime.now().astimezone().isoformat(),
        elapsed_time=1800,  # seconds
        distance=5000.0,  # meters
        visibility=ActivityVisibility.ONLY_ME,
        tags={ActivityTag.RECOVERY: True, ActivityTag.COMPETITION: False},
    )
```

Use the same keywords for updates and uploads. Editing Only Me activities also
requires `activity:read_all`. Create/upload form bodies encode tags as
`tags[Recovery]=true` / `tags[Competition]=false`; updates use a nested JSON
`"tags": {"Recovery": true, "Competition": false}` object. The SDK handles these
wire formats; callers pass a Python dictionary.

Unknown tag names and a `tags`/`commute` conflict raise `ValueError` locally;
non-mapping tags or non-boolean values raise `TypeError`. Response
`SummaryActivity.tags` / `DetailedActivity.tags` are optional lists of tag names,
not update dictionaries; convert them deliberately rather than passing a
response's tag list directly back as `tags`. String visibility values are
validated by Strava, not by a local SDK `ValueError` check.

## Streams

All four stream methods return a typed `StreamSet`. They accept both responses
keyed by stream type and legacy lists of stream objects. Empty responses produce
an empty `StreamSet`; unknown stream types are ignored. Keyed values need no
inner `type` field. Missing streams remain `None`.

Using an open `client`:

```python
streams = client.streams.get_activity_streams(123, keys=["time", "heartrate"])
if streams.heartrate is not None:
    print(streams.heartrate.data)
route_streams = client.streams.get_route_streams(456)
```

Activity, segment-effort, and segment stream requests send comma-separated `keys`
and `key_by_type=true`. Route stream requests send no query parameters. Async
methods use `await`. `key_by_type=False` raises `ValueError` before a request;
see [migration guidance](migration.md#streams).

## Strength-Training Uploads

`uploads.create()` accepts `sport_type` as a `SportType` member or string to
override the sport detected from a file. If omitted, Strava uses file metadata.

Strava accepts JSON strength-training files for `WeightTraining`,
`HighIntensityIntervalTraining`, `Workout`, and `Crossfit`. The sample
[`examples/strength-training.json`](../examples/strength-training.json) contains
repetition-based and timed sets, weights in kilograms, and optional heart-rate
and active-time streams.

Run this example from the repository root; it **uploads a real activity**:

```python
import os

from strava import SportType, Strava

with Strava(access_token=os.environ["STRAVA_ACCESS_TOKEN"]) as client:
    with open("examples/strength-training.json", "rb") as file:
        upload = client.uploads.create(
            file=file,
            data_type="json",
            sport_type=SportType.WEIGHT_TRAINING,
            name="Strength session",
            visibility="only_me",
        )
    print(upload.id, upload.status)
```

Use `data_type="fit"` to upload a FIT strength-training file containing set
messages. Replace the file above with your own `strength.fit` and, for example,
use `SportType.CROSSFIT`. The SDK transmits file bytes without modifying them.
FIT files with sets do not need timestamped record messages, but must include
the activity timestamp and session total elapsed time required by Strava.

JSON files require version `"1.0"`, a timezone-aware `start_time`, `utc_offset`
in seconds, `elapsed_time`, and at least one set. If streams are provided,
`time` is required and all stream arrays must have equal lengths. These upload
streams are part of the file format, separate from the read-only streams API.
See the [uploads guide](https://developers.strava.com/docs/uploads/) for the
complete specification and supported exercises.

Uploads require `activity:write` and are processed asynchronously by Strava.
Once `upload.id` is non-null, poll `uploads.retrieve(upload.id)` **no more than
once per second**, with an application-defined overall deadline, until
`activity_id` is populated or `error` is set. The SDK does not poll automatically.
Async applications use `await client.uploads.create(...)` and
`await client.uploads.retrieve(...)`, with nonblocking waits between polls.

## Webhook Subscriptions

Manage subscriptions with application credentials. These requests bypass
athlete-token authentication and automatic token refresh. Strava permits one
subscription per application. An athlete access token is not needed, although
the SDK constructor still requires the `access_token` argument.

This example **creates and then deletes a real subscription**; deploy a working
callback endpoint first:

```python
import os

from strava import Strava

client_id = os.environ["STRAVA_CLIENT_ID"]
client_secret = os.environ["STRAVA_CLIENT_SECRET"]

with Strava(access_token="") as client:
    subscription = client.webhooks.create(
        client_id=client_id,
        client_secret=client_secret,
        callback_url=os.environ["STRAVA_WEBHOOK_CALLBACK_URL"],
        verify_token=os.environ["STRAVA_WEBHOOK_VERIFY_TOKEN"],
    )
    subscriptions = client.webhooks.list(
        client_id=client_id, client_secret=client_secret
    )
    if subscription.id is not None:
        client.webhooks.delete(
            subscription.id,
            client_id=client_id,
            client_secret=client_secret,
        )
```

Validate the callback verification token and answer Strava's verification request
within two seconds with `{"hub.challenge": "<received challenge>"}`. Async resource
methods use `await`. Activity events require the athlete to grant `activity:read`;
subscription credentials are not a substitute for athlete consent. Redact query
strings from request logs because subscription list/delete requests contain the
client secret. See the [official webhook guide](https://developers.strava.com/docs/webhooks/)
for verification and event handling.
