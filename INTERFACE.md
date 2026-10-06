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
Explicit coordinates count as resolved; zero is a valid coordinate.

W09b1 replaces the legacy time fallback with strict ZoneInfo conversion shared
with the typed core. `resolve_birth` adds an optional final `timezone_override`
argument, preserving older positional arguments and the ten-item tuple. Invalid
civil inputs, unresolved locations/zones, DST folds/gaps and invalid/incomplete
coordinate pairs raise `CalculationError`. Its CLI boundary emits stderr/status 2
before chart output. Explicit `--timezone` bypasses discovery for nine birth-aware
commands; synastry/composite/synergy use separate `--timezone1/--timezone2` and
location flags. Both people are admitted before calculation/output. Existing
London defaults are labeled in paired output; Davison needs both real location
inputs. UTC-only antiscia/aspect-grid keep their declared UTC convention.

Shared date/time admission uses YYYY-MM-DD and HH:MM[:SS[.ffffff]]; only `None`
means an unknown-time noon surrogate. Empty strings reject. Historical IANA offset
seconds and supplied civil seconds are preserved. Progression/sky dates, return
years, ordered prediction windows, planetary-hour coordinates and location query
pairs also validate before output. Default prediction end is one civil year later,
clamping February 29 to February 28. House/backend/event-root migration remains
W09b2/W09b3. The existing pytz dependency is retained, though this adapter uses
stdlib ZoneInfo and the bundled tzdata fallback instead.

New typed APIs and JSON commands are owned/documented in `astroengine/INTERFACE.md`.
Successful JSON goes to stdout; failures use stderr and nonzero status. No birth
storage, networking or LLM inference occurs in the new computation package.
