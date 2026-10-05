# Changelog

## [Unreleased]

### Added

- Add sync and async webhook subscription creation, listing, and deletion using application credentials.
- Expose granted OAuth scopes and typed athlete summaries on token responses, with optional metadata for refresh responses.
- Add Basketball, Cricket, Dance, Padel, PhysicalTherapy, and Volleyball to `SportType`.
- Preserve recording device names on `SummaryActivity` responses, including activity listings.
- Add upload sport-type overrides and document JSON/FIT strength-training uploads with a structured JSON example.

### Fixed

- Continue sync and async page-number pagination until an empty response instead of truncating results at short intermediate pages.
- Use opaque cursor pagination for activity comments, expose optional `Comment.cursor`, and guard missing or nonadvancing cursors only when another page is needed. Preserve `per_page` as a comment `page_size` alias, with `page_size` taking precedence.
- Restore the default API base URL to the current official `https://www.strava.com/api/v3` for sync and async clients. Correct migration guidance: the future host is `https://api-v3.strava.com` (without `www`), available starting January 4, 2027; switching requires an explicit `base_url` override and is not based on the clock.

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
