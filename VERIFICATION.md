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
