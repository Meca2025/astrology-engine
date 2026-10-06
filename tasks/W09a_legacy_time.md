# W09a: legacy UTC calendar rollover and explicit coordinate certainty

Status: implementing; documented before code, 2026-10-06.
Owner: legacy input adapter, under parent W09 migration.

## Problem and evidence

Legacy local_to_utc returns only UTC clock hours, losing previous/next UTC date.
resolve_birth keeps the original civil date for Julian day. Explicit valid
coordinates return city_resolved=False and can be incorrectly reported as a
fallback. New typed chart path is correct; the remaining sixteen legacy text
commands need a compatible migration with regression evidence.

## Files and outcome

astrology_engine.py input functions/headers; new focused regression tests;
COMMANDS/ARCHITECTURE/INTERFACE and evidence. Preserve function names, caller tuple
shape, default Western settings and normal-day text behavior. Choose a documented
representation that carries full UTC date without breaking Julian-day calls.
Correct explicit coordinate certainty; avoid truthiness tests that reject zero.

## Chosen compatibility contract

`local_to_utc` keeps its two-item result. Its UTC hour is measured from midnight
of the supplied civil date, including a signed day offset (negative or >=24 on
rollover). Passing it with that civil date to `julian_day` remains correct.
`resolve_birth` normalizes that result into the actual UTC year/month/day and a
clock hour in [0,24), retaining its ten-item tuple. Rollover display includes the
UTC date; ordinary same-day display is preserved. Unknown-time noon is local
noon converted to UTC and remains flagged as unknown. Make pytz a required
runtime dependency so installed legacy conversions do not depend on the geo
extra. Existing ambiguous/nonexistent-time fallback is preserved only in W09a;
strict rejection belongs to W09b. Natal explicit-coordinate labels use the actual
coordinates, and legacy synastry overlays accept zero-valued coordinates.

Before implementation, reproduced 2000-01-01 Asia/Kolkata 00:15 as Jan 1 18:45
(should be Dec 31), New York 23:45 as Jan 1 04:45 (should be Jan 2), and Kiritimati
noon as Jan 1 22:00 (should be Dec 31). Explicit (0,0) was marked fallback and
unknown-time Kolkata noon was used as 12:00 UTC instead of 06:30 UTC.

## Acceptance before implementation push

Reproduce midnight conversions in both directions with real IANA rules; historical
normal-day regression; local noon unknown-time handling; explicit coordinates
including latitude/longitude zero; known legacy commands exercised offline. Tests
must verify actual JD, not only display clock. Date labels and docs must agree.
Keep unresolved zone/city, ambiguous DST, polar houses and silent optional-body
failures visible as remaining W09b work rather than claiming strict migration done.

## Following slice

W09b strict legacy input/house/backend contracts and precision-aware event roots.
Each sub-slice needs a scoped task and its own acceptance fixtures; do not bundle
unvalidated event behavior into the time repair.
