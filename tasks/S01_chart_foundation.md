# S01: reproducible chart and agent contracts

Status: documented before code, 2026-10-06.

## Owner and files

Input/astronomy/profile/agent boundaries: astroengine/models.py, inputs.py,
ephemeris.py, service.py, cli.py, data/profiles.json, data/capabilities.json,
pyproject.toml, tests, CI and additive registration in astrology_engine.py.

## Before / after

Legacy text commands remain callable. Add `chart` JSON with explicit coordinates,
zone, house/zodiac/node settings and `capabilities` with actual availability.
Fix the import stdout side effect by limiting its existing wrapper to CLI execution.
Do not migrate old algorithms wholesale. Unknown time has no angles/houses; all
new failures are visible, not fabricated outputs. Requested/actual backend recorded.

## Acceptance

Offline UTC rollover in both directions, invalid date/time/zone/coordinates,
DST fold/gap rejection, unknown-time suppression, direct tropical Swiss positions
and houses, sidereal isolation, JSON successful/error subprocess contracts,
missing optional ephemeris path rejection, installed-package data discovery,
legacy CLI help/lunar smoke. Hosted Linux/macOS/Windows Python 3.11/3.12 CI.

## Daily intent

Today: restore time/input truth and separate calculation from I/O. Preserve existing
commands, license and source assets. Output schema version 1.0; no LLM provider.

## Acceptance receipt

24 local tests passed on Linux/Python 3.12; wheel built and imported through an
isolated wheel directory with packaged rules; direct chart computation succeeded.
Legacy help/import/lunar subprocess checks passed. CI matrix configured; hosted
results remain pending until checked. No physical Pi/mobile execution claimed.
