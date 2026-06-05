# Changelog

## [0.5.1] - 2026-06-05

- Harden pagination, rate-limit, and datetime parsing edge cases.
- Centralize client request handling and resource pagination helpers.
- Add package licensing and metadata details.

## [0.5.0] - 2026-06-04

### Added

- Add `revoke_token()` for Strava's `oauth/revoke` endpoint using HTTP Basic authentication.

### Changed

- Change the default API host to `https://www.api-v3.strava.com` for Strava's June 1, 2027 API migration.
- Document Strava's 2026 endpoint changes for club activities, club administrators, club members, and segment explore.

### Deprecated

- Deprecate `deauthorize()` because Strava will retire `oauth/deauthorize` on June 1, 2027.
