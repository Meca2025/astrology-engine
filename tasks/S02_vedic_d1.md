# S02: Jyotisha D1 and lunar mansions

Status: documented before code, 2026-10-06. Owner: Jyotisha adapter.

## Files and boundary

astroengine/vedic.py; data/vedic.json; service/CLI registration; test_vedic.py;
public interface, command guide and capability status.

## Outcome

`vedic` uses explicit sidereal, whole-sign and mean-node defaults (overridable
ayanamsa/node profile). Return rasi/navagraha positions, lagna when time known,
27 equal nakshatras and 108 padas, lords and lunar placement. Rahu/Ketu are
aliases of correctly opposed nodes with identical longitude speed.

Do not infer Western dignity, yogas, divisional charts or predictive verdicts.
Reject tropical input for a Jyotisha request. Keep school choices in metadata.

## Verification

Independent 0/13°20'/3°20'/360 boundaries, all 27 lords and pada cycling,
Lahiri positions/houses versus direct Swiss Ephemeris, alternate ayanamsas and
true/mean nodes, missing-time omission and wired CLI JSON contract.

## Receipt

34 total local tests passed; 10 new D1/nakshatra cases. Evidence: rule partition
fixtures, direct Swiss comparison and CLI invocation; independent practitioner
chart cross-validation remains a later reference-corpus gate.
