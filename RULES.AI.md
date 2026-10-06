# AI development rules

Use Mythic Engineering's five layers: vision, domain, interface, execution,
verification. Read TODO, the owning interface, architecture and task before code.
Document and push a work order before implementation. The 2026-10-06 instruction
authorizes sequential implementation and pushes within this expansion roadmap.

No pseudocode, fake implementations, silent fabricated fallbacks or orphaned APIs.
No file/function/data deletions without human permission. Preserve legacy entry
points. Complete wiring, test it, document evidence, push each passing slice, and
verify the remote commit. Never force push or overwrite unrelated human work.

New Python uses type hints, dataclass requests, focused functions, clean internal
APIs, relative/dynamic paths and logging. Rule data belongs in JSON under `data/`.
Do not mutate base data at runtime. No circular imports or direct state mutation
across domains. Fail at public boundaries with clear diagnostics; catching errors
must not turn an invalid chart into a success. Legacy style is not a mandate to
spread legacy defects; migrate in explicit slices.

Important folders need README and README_AI; public module APIs need INTERFACE.
Keep docs and capability states current. All future AI provider settings must be
explicit, data-owned and set max tokens to 127000 when supported; no AI calls are
introduced by this work. Cross-platform design is required, but do not claim
platform validation without build/runtime evidence.
