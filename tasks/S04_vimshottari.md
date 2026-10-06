# S04: Vimshottari timing

Status: documented before code, 2026-10-06. Owner: Jyotisha period arithmetic.
Files: astroengine/dashas.py, data/timing.json, tests/test_dashas.py, CLI/interfaces.

Compute Moon-nakshatra-based 120-year maha/antar sequence with balance at birth.
Subperiods subdivide the full mahadasa, including its pre-birth portion; never
restart antardasa at birth. Expose tropical (365.2425), Julian (365.25) and savana
(360) day/year models. Half-open intervals, explicitly clipped reporting window,
optional UTC as-of lookup. No lifetime/event/health predictions.

Reference: Rao (2000), section 16.2-16.3, Example 50: Dhanishtha Moon at Aquarius
2°23' leaves 2.24875 Mars years. Calendar years vary by school; tests validate the
fraction and chosen continuous day clock rather than unreviewed narrative dates.

Gate: example balance, cycle sum/order, full antar partition, first clipped antar,
as-of exact boundary, positive finite horizon, date-aware UTC and CLI wiring.

## Receipt

87 total local tests passed; published example balance, cycle/partition/clip
invariants and CLI as-of request verified. Year-model output is explicit.
