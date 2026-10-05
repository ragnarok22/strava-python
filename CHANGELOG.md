# Changelog

## [Unreleased]

### Added

- Add strict Python 3.11 mypy checks for the SDK and static public API consumer contracts through `make typecheck`, CI, and release builds.
- Add sync and async webhook subscription creation, listing, and deletion using application credentials.
- Expose granted OAuth scopes and typed athlete summaries on token responses, with optional metadata for refresh responses.
- Add Basketball, Cricket, Dance, Padel, PhysicalTherapy, and Volleyball to `SportType`.
- Preserve recording device names on `SummaryActivity` responses, including activity listings.
- Add upload sport-type overrides and document JSON/FIT strength-training uploads with a structured JSON example.
- Add optional activity resource state, heart-rate metrics, cadence, temperature, PR count, suffer score, and UTC offset to both summary and detailed models; expose resource state, starred, and hazardous flags on both segment models.

### Fixed

- Preserve concrete model and subclass return types from `from_dict`, sync and async endpoints, and paginator iteration/collection. Correct async OAuth flow, stream map, dictionary, and activity list return annotations without type-check suppressions. Enum model annotations now include the existing unknown-string fallback; known values still parse as enum members, including optional unions and nested lists, with unchanged serialization. **Typing compatibility:** code that assumes enum-only response fields must also handle unknown strings; paginators are typed for `StravaModel` subclasses.
- Apply SDK authentication (including automatic refresh), API base URL, and timeout to every sync and async resource request when an HTTPX client is supplied, including SDK defaults. Preserve caller transport, hooks, pooling, and custom headers without mutating client settings; override default `Authorization` for API requests and remove it for unauthenticated webhooks. Preserve API path prefixes and propagate request timeouts to automatic OAuth refresh. **Compatibility change:** Configure API auth, base URL, and timeout on the SDK; supplied clients remain open after SDK close/context exit and must be closed by the caller.
- Propagate automatic OAuth refresh failures through the SDK exception hierarchy before sending the original API request, changing tokens, or invoking the refresh callback. Preserve the OAuth response status, message, fault, response object, and rate-limit details, including streamed async error bodies.
- Use the same SDK HTTP status mapping for token exchange, manual refresh, revocation, and deprecated deauthorization. **Compatibility change:** OAuth helpers now raise `StravaError` subclasses instead of `httpx.HTTPStatusError`; update exception handlers accordingly. Document that 401 maps to `AuthenticationError`, while `TokenExpiredError` remains exported for compatibility and is not automatically raised.
- Read streamed OAuth refresh responses asynchronously in async clients before parsing tokens, preserving token rotation and closing response bodies correctly.
- Normalize keyed and legacy list responses into typed `StreamSet` results for all four sync and async stream endpoints, including empty responses and unknown stream types. Send CSV `keys` and `key_by_type=true` for activity, segment-effort, and segment streams, and omit query parameters for route streams. Compatibility note: `key_by_type=False` now raises `ValueError` before HTTP; remove it or pass `True`. `StreamSet.from_stream_list()` remains supported.
- Continue sync and async page-number pagination until an empty response instead of truncating results at short intermediate pages.
- Use opaque cursor pagination for activity comments, expose optional `Comment.cursor`, and guard missing or nonadvancing cursors only when another page is needed. Preserve `per_page` as a comment `page_size` alias, with `page_size` taking precedence.
- Restore the default API base URL to the current official `https://www.strava.com/api/v3` for sync and async clients. Correct migration guidance: the future host is `https://api-v3.strava.com` (without `www`), available starting January 4, 2027; switching requires an explicit `base_url` override and is not based on the clock.
- Preserve PR-style `athlete_segment_stats` (`pr_elapsed_time`, `pr_date`, `effort_count`, and optional `pr_activity_id`) alongside documented effort fields, including mixed responses. Keep the existing `SummarySegmentEffort` type and `SummaryPRSegmentEffort` semantics; normalize PR dates to UTC, including date-only values at midnight.

### Removed

- **Breaking:** Remove `clubs.list_activities()`, `clubs.list_members()`, and `clubs.list_admins()` from both sync and async clients after Strava removed these endpoints on September 1, 2026. Accessing these methods now raises `AttributeError`; remove their calls and dependent application features. Strava provides no documented replacement endpoints. `clubs.retrieve()` and `clubs.list_authenticated()` remain supported, and `ClubActivity` / `ClubAthlete` models and public exports remain available for parsing existing data.

## [0.5.1] - 2026-06-05

- Harden pagination, rate-limit, and datetime parsing edge cases.
- Centralize client request handling and resource pagination helpers.
- Add package licensing and metadata details.

## [0.5.0] - 2026-06-04

### Added

- Add `revoke_token()` for Strava's `oauth/revoke` endpoint using HTTP Basic authentication.

### Changed

- Change the default API host to `https://www.api-v3.strava.com` for Strava's planned API migration.
  - Correction: this historical release switched prematurely to an incorrect hostname. The future host is `https://api-v3.strava.com` (without `www`), available starting January 4, 2027. The Unreleased fix restores the current official base URL.
- Document Strava's 2026 endpoint changes for club activities, club administrators, club members, and segment explore.

### Deprecated

- Deprecate `deauthorize()` because Strava will retire `oauth/deauthorize` on June 1, 2027.
