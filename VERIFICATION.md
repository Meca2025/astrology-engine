# Verification and evidence

## Local acceptance

As of first-wave/agent completion on 2026-10-06, 136 tests pass on Linux x86_64,
Python 3.12. Tests cover complete UTC rollover, DST fold/gap refusal, coordinates,
profile/ephemeris failures, direct Swiss positions/houses, sidereal isolation,
27/108 boundaries, sixteen classical vargas, period partitions and birth balance,
panchanga, relationships, relocation, Western techniques, schemas and CLI errors.
All exact equal-partition boundaries and neighboring floats are checked.

## Evidence layers

- Formula/boundary fixtures: independently counted angles, dates, signs and geometry.
- Direct Swiss library comparisons: adapter contracts; not an independent ephemeris.
- Published worked examples: Rao section 6.2/16; D27 discrepancy explicitly recorded.
- Hosted matrix: Linux/macOS/Windows on Python 3.11/3.12; inspect exact run SHA.
- Packaging: build wheel, import from installed resources outside source checkout.
- Unperformed: physical Raspberry Pi/mobile, broad expert comparison corpus,
  high-precision DUT1 corrections and ephemeris-file provisioning across date ranges.

## Reproduce

```bash
python -m pip install '.[test]'
python -m pytest -q
python -m astroengine tools
python astrology_engine.py --help
```

Never translate passed arithmetic tests into predictive/scientific validation of
symbolic astrology, or broad universal-tradition coverage. CI verifies program
behavior in its tested environment; method authority remains source-scoped.

## Verified hosted and packaging receipt

Implementation commit: 45c7a3e29f3effc3bceefb9a557f2720b74c4531.
GitHub Actions run 37443735522 completed successfully in all six matrix jobs:
Linux/macOS/Windows, Python 3.11/3.12. This run includes 136 tests.
https://github.com/hrabanazviking/astrology-engine/actions/runs/37443735522

Final wheel was installed into a fresh Python 3.12 environment and run outside the
source checkout. All eight local tools computed successfully; all nine JSON rule
resources were present. No external agent-host deployment or physical Pi/mobile
execution is implied by these checks.

## W09a local receipt

2026-10-06: 150 tests passed on Linux/Python 3.12, including fourteen new legacy
regressions. Thirteen reproduced failures before the repair. Actual Julian days
are checked against hand-specified UTC dates with both Swiss and formula paths;
real natal and geoastrology CLI commands run offline. The 1975 Indiana same-day
offset/display stays unchanged. Hosted acceptance for this slice is pending its
implementation push and will be recorded by exact SHA/run.

W09a hosted acceptance: c1c8c2cabf537d9827fcd17d523846fdbf8558d0, [run 37445523298](https://github.com/hrabanazviking/astrology-engine/actions/runs/37445523298), all six jobs successful. All 150 tests pass; W09b1 is next.

## W09b1 local receipt

2026-10-06: 223 tests pass on Linux/Python 3.12; all 150 prior tests remain. New
coverage exercises API and actual CLI input-error status/stderr/empty-stdout, nine
birth handlers' override/help wiring, three paired commands' distinct actual Julian
days, explicit zero admission, absent discovery, invalid geocoding results, typed
empty-time errors, civil/UTC calendar boundaries, secondary dates and leap windows.
The Paris 1890 offset +00:09:21 comes from IANA's Europe/Paris zone record, and the
expected UTC 11:50:39 is separately subtracted. Hosted acceptance and fresh wheel
resource/import evidence are recorded separately after implementation push.

W09b1 hosted/wheel acceptance: c6a3696718d87791b7cb87b98b3cbdfddd1eb0cc, [run 37447854001](https://github.com/hrabanazviking/astrology-engine/actions/runs/37447854001), all six jobs successful with 223 tests. A rebuilt wheel installed outside source passed strict adapter and nine-resource checks. Next: W09b2.

## W09b2 local acceptance

2026-10-06: 283 local Linux/Python 3.12 tests pass, retaining prior admission/UTC
coverage and adding 60 astronomy/uncertainty cases. Tests cover seven direct Swiss
house comparisons, real polar Placidus rejection, no chart stdout on requested
house/body failure, partial unknown-time output, independent receiving overlays,
Davison admission/preflight, strict optional diagnostics with empty ephemeris data,
actual Moshier flags, same-motion antipodal nodes, mixed Fagan/Lahiri thread calls,
real ordered rise/set/day-length checks, polar event status and invalid data.
The prior planet-hours admission test now asserts unexpected exceptions propagate
instead of depending on the corrected broad successful-error catch. AST audit
preserves all 72 existing top-level legacy functions. Hosted/wheel evidence follows
by exact implementation SHA; arithmetic/library tests are not physical-device or
independent ephemeris/practitioner validation.

W09b2 installed-wheel check passed in a fresh Python 3.12 environment outside the
source checkout: all ten JSON resources, frozen UT request/import, required and
optional bodies with actual Moshier flags, same-motion nodes, requested houses and
polar failure, ordered solar events, unknown-time chart and updated capability
scope. The wheel ships the typed bridge; the legacy text script still runs from
the source checkout. Hosted acceptance remains pending the implementation push.
