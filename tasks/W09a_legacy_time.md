# W09a: legacy UTC calendar rollover and explicit coordinate certainty

Status: next ready slice; documented before code, 2026-10-06.
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
