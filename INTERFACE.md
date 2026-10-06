# Repository interface

`python astrology_engine.py --help` lists legacy text commands and additive package
commands. The legacy Python functions remain supported as previously exposed;
inputs/fallback limitations are documented in the historical ARCHITECTURE sections.
No legacy return tuple is changed by the new package.

New typed APIs and JSON commands are owned/documented in `astroengine/INTERFACE.md`.
Successful JSON goes to stdout; failures use stderr and nonzero status. No birth
storage, networking or LLM inference occurs in the new computation package.
