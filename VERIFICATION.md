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
