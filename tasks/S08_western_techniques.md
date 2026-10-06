# S08: advanced Western starter tools

Status: documented before code, 2026-10-06. Owner: Western timing/geometry.
Files: astroengine/western.py, western.json, tests/test_western.py, CLI/interfaces.

Whole-sign annual profections use completed civil-calendar age, natal Asc sign and
traditional ruler; named leap-birthday policy is February 28. Harmonics multiply
positions by positive integer factor and do not invent astronomical instants or
house cusps. Midpoint trees retain antipodal ambiguities and identify configured
orb hits on third planets. No birth time -> profection unavailable; positional
analyses keep existing surrogate warning. Explicit as-of date required.

Gate: age0/12/13, birthday and leap boundaries, traditional rulership, source-sign
wrap, positive integer harmonic, midpoint third-body orb thresholds and CLI.
Also refactor growing CLI registration into domain-focused functions without
changing any command flags or handlers; check complete registry parity.
