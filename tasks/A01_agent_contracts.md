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
