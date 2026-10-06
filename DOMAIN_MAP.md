# Domain map

| Domain | Owns | Boundary |
| --- | --- | --- |
| Inputs | date/time/zone/coordinates, uncertainty | No ephemeris or interpretation |
| Astronomy | JD, positions, speeds, angles, provenance | No tradition scores or narratives |
| Profiles | zodiac, ayanamsa, nodes, houses | Immutable rule data; no global client state |
| Jyotisha | vargas, nakshatras, dashas, panchanga, strengths | Named school/method, not Western dignity |
| Western | aspects, dignities, lots, timing, harmonics | Explicit rules and clocks |
| Relationships | two/multiple chart comparisons and composites | No deterministic relationship verdicts |
| Locations | relocation, angular lines, local space, parans | Geography and accuracy metadata |
| Traditions | Chinese/Tibetan/Hellenistic/etc. adapters | Source/licensing and conversion gates |
| Reports | text/JSON/SVG/map formatting | No hidden recalculation or altered inputs |
| Agent tools | discovery, schemas, routing, cancellation | No fabricated capabilities or positions |
| Verification | fixtures, tolerances, CI, portability | Evidence is scoped to tested environments |

Current legacy responsibilities live together in `astrology_engine.py`. New work
enters `astroengine/` behind explicit APIs; replacement/removal needs human approval.
