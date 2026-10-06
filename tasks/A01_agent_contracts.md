# A01: agent discovery and portable tool contracts

Status: documented before code, 2026-10-06. Owner: agent interface.
Files: SKILL.md, astroengine/agent.py, data/tool_schemas.json, CLI/discovery/tests.

Provide a checked-in Hermes/Codex-readable skill and JSON tool request schemas.
Add local `run_tool(name, parameters)` with whitelisted services and no shell,
network, inference or storage. Return capability schemas on discovery and support
`tools` CLI. Validation must reject unknown fields/tools rather than silently
ignore invented arguments. Core strict request validation stays authoritative.

Gate: schema/service command parity, valid Vedic/relationship routing, unsupported
method refusal, unknown field/type errors, no namespace mutation and CLI wiring.
Also audit/install final wheel with all JSON profiles, update README and next task.

## Boundary audit amendment (before repair)

The final audit found nine nominal pada boundaries vulnerable to floating-point
floor arithmetic. Add astroengine/partitions.py with explicit half-open boundary
lookup and apply it to nakshatra/varga/panchanga partitions. Test every exact
boundary plus neighboring representable floats, preserving genuine side selection
without arbitrary epsilon snapping. This is a correctness repair, not new scope.

## Receipt

136 tests pass locally. Schema/service availability parity, routing/defaults,
non-mutation and invented-field/unsupported-tool/non-finite rejection verified.
Exact boundary audit repaired with neighboring-float evidence. Final wheel and
hosted matrix receipts follow after the implementation push.

Final receipt: implementation 45c7a3e passed all six hosted matrix jobs in run
37443735522. Fresh wheel installation outside the checkout executed all eight
tools and found all nine rule resources. Repository remote HEAD verified after
push; W09a is the next published work order.
