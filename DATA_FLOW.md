# Data flow

Request -> validated coordinates and civil time -> UTC datetime -> Julian day ->
locked Swiss Ephemeris calculation -> immutable-by-convention chart snapshot ->
tradition/relationship/location calculation -> versioned report -> text/JSON.

Uncertain birth time -> explicit noon surrogate for positions -> no natal angles
or houses -> downstream methods requiring exact time reject or omit those outputs.

Configuration flows from read-only `data/` into fresh rule snapshots. No birth
records are stored. Explicit optional ephemeris paths are dynamically resolved.
Errors flow to stderr as versioned JSON with nonzero exit status; stdout contains
only a successful result. Agents must check both exit status and capability state.

Legacy W09b2: admitted full UTC -> frozen UT ephemeris request -> shared owner
lock/settings reset -> required/optional registry snapshot -> preflight known houses
-> time-aware text rendering. Required failures go to stderr/status 2 before chart
headers; optional unavailability is named in snapshot attributes and CLI warnings.
No house/angle surrogate flows from an unknown birth time. Event searches remain
an explicitly separate legacy path until W09b3 replaces their raw calls.
