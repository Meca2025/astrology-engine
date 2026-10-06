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
