# Repository interface

`python astrology_engine.py --help` lists legacy text commands and additive package
commands. The legacy Python functions remain supported as previously exposed;
inputs/fallback limitations are documented in the historical ARCHITECTURE sections.
No legacy return tuple is changed by the new package.

W09a keeps `local_to_utc(year, month, day, local_hour, tz_name)` as a two-item
`(utc_hour, offset_label)` result. The hour includes the signed day offset from
the supplied civil midnight, so it may be negative or >=24; passing that civil
date and hour to `julian_day` produces the correct instant. `resolve_birth`
retains its ten-item tuple but returns the actual UTC year/month/day and a UTC
clock hour in [0,24). On rollover its time label includes the UTC date.
Unknown-time noon is converted from local noon while `time_known` stays False.
Explicit coordinates count as resolved; zero is a valid coordinate. pytz is a
required dependency for the legacy conversion. Unresolved zones/cities, DST
ambiguity/gaps and legacy house/backend fallbacks still require W09b migration.

New typed APIs and JSON commands are owned/documented in `astroengine/INTERFACE.md`.
Successful JSON goes to stdout; failures use stderr and nonzero status. No birth
storage, networking or LLM inference occurs in the new computation package.
