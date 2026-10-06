# S07: relocation and angular location lines

Status: documented before code, 2026-10-06. Owner: location astronomy.
Files: astroengine/locations.py, ephemeris internal equatorial API,
tests/test_locations.py, CLI/interface/capabilities.

Relocation holds original UTC instant and celestial frame fixed while recalculating
houses at explicit destination coordinates. Reject unknown birth time. Calculate
planet right ascension/declination from Swiss equatorial coordinates, independent
of sidereal zodiac longitudes. At a requested latitude compute MC/IC meridians and
exact geometric ASC/DSC horizon longitudes, with circumpolar/no-crossing status.
Provide signed longitude residuals to lines, explicitly not geodesic distances.
No sampled-line nearest-distance, map, refraction, parans or local-space claims.

Gate: original instant and positions unchanged by relocation, direct destination
Swiss houses, horizon and meridian synthetic geometry, polar/equator edge cases,
longitude wrap/antimeridian and CLI uncertainty refusal.
