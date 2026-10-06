# Repository orientation for agents

Start with TODO, TASK_astrology_expansion, RULES.AI, DOMAIN_MAP and the owning
INTERFACE. `astrology_engine.py` is the legacy CLI. New code belongs in astroengine;
immutable rule data belongs in data. See ROADMAP for feature/validation readiness.

Operate offline in tests with explicit coordinates/zones. Never store birth data or
invent unavailable chart features. Document before code, update evidence and push
each passing slice. Existing license/artwork/cultural documents remain preserved.
