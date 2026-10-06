# Technique source and discrepancy ledger

## Astronomy

Swiss Ephemeris programmer documentation owns UT, sidereal flags and house API
conventions: https://www.astro.com/swisseph/swephprg.htm
Actual return flags identify backend selection; intended precision is not measured
accuracy. The core currently supplies UTC as UT without an external DUT1 correction.

## Jyotisha

P.V.R. Narasimha Rao, Vedic Astrology: An Integrated Approach (2000), author-hosted
PDF with a 2010 notice of later refinements:
https://www.vedicastrologer.org/articles/vedic_astro_textbook.pdf

Named varga profile follows section 6.2 sign rules. D2 is the two-hora Leo/Cancer
representation; D60 counts from the natal sign. Other variants remain explicit
future profiles. Output provides sign and source fraction, not physical longitude.

Discrepancy: Example 23 (printed p.58) maps Gemini 11° in D27 to Leo, despite
calling it the tenth sign from Libra. Counting inclusively gives Cancer. The stated
section 6.2.16 rule and independent arithmetic prevail; regression records Cancer.
This discrepancy is retained rather than quietly treating every printed example
as infallible. Other worked fixtures 11/12/14/16/17/19-26 agree with the rules.

Nakshatra name/order reference:
https://www.drikpanchang.com/tutorials/nakshatra/nakshatra.html

## Annual profections

Basic whole-sign time-lord description by Chris Brennan:
https://theastrologypodcast.com/2018/04/26/annual-profections-a-basic-time-lord-technique/
The implemented clock is explicit civil birthday age; solar-return timing remains
a distinct option for a later timing slice.

## Historical civil time

IANA Time Zone Database europe file (accessed 2026-10-06):
https://data.iana.org/time-zones/tzdb/europe
Europe/Paris specifies +00:09:21 LMT before 1891-03-16, then the same PMT offset
through 1911-03-11. The 1890 fixture subtracts 9 minutes 21 seconds from local noon
to expect UTC 11:50:39. This verifies handling of IANA's rule, not the historical
certainty of every supplied birth record. ZoneInfo uses installed system tzdb or
the packaged tzdata fallback; freezing/digesting that source remains I01 work.

## W09b2 failure and provenance fixtures

Swiss programmer documentation, accessed 2026-10-06, sections 3.3 and 13:
https://www.astro.com/swisseph/swephprg.htm
It specifies actual ephemeris selection/fallback flags and polar Placidus/Koch
failure. Python pyswisseph 2.10.3.2 raises swe.Error on house failure, so accepting
substitute cusps would violate the declared system. Installed rise_trans API
documentation states status 0 means found and -2 means circumpolar/unavailable.
Direct-library tests exercise J2000 houses and rise times; an empty data directory
reproduces Moshier major-body fallback and five unavailable optional bodies.
Injected node-motion/error fixtures verify adapter semantics, not independent
astronomical accuracy. No external ephemeris-file corpus was provisioned here.
