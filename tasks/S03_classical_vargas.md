# S03: classical divisional charts

Status: documented before code, 2026-10-06. Owner: Jyotisha divisions.
Files: astroengine/vargas.py, data/vargas.json, tests/test_vargas.py, CLI/interface.

Return the sixteen shodashavarga sign placements with named classical mapping.
D2 uses Sun/Leo and Moon/Cancer horas; D30 uses unequal odd/even segments; D60
uses the natal sign as the starting sign in the chosen Rao-2000 profile. Retain
source subdivision/fraction; do not claim a physically observed varga longitude.
No harmonic shortcut for all vargas. Unknown-time inputs omit divisional lagna.

Source: P.V.R. Narasimha Rao, Vedic Astrology: An Integrated Approach (2000),
section 6.2, printed pp. 52-60, with author-hosted 2010 update warning that later
research refined some methods. This is a named profile, not every school's rule.
https://www.vedicastrologer.org/articles/vedic_astro_textbook.pdf

Gate: independent worked examples 11/12/14/16/17/19-26; D2/D30 boundaries; all
sign/parity/modality partitions; errors for unsupported divisors; CLI integration.

## Receipt

78 total tests passed. Example 23 contains an inclusive-count contradiction;
D27 Gemini 11° computes Cancer per stated rule, with discrepancy ledger.
All sixteen mappings accessible from both CLIs; unknown time omits lagna.
