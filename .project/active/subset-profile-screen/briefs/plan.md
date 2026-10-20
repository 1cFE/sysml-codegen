Plan EXEC-SUBSET-CONTRACT Item 2b, live half (`subset-profile-screen`, sysml-codegen, branch `subset-profile-screen`). Agentic-mbse sibling: `/home/reid/src/subset-conformance/agentic-mbse` (the design changes nothing there; keep it that way).

Read: `design.md` (approved after two review rounds), `design-review.md` (Resolutions), `spec.md` (revision 3), `briefs/align.md`, `product-lens.md`.

Intent, graded: [OWNER-ratified] the generator's own route alone decides refusal; the screen only reports. [OWNER] RG-1/RG-2/RG-3 stay with the owner. [ORCHESTRATOR] Engineering bar: a clean refactor, each phase leaving the suite green, behaviour-preserving moves separated from behaviour changes so each can be reviewed alone.

Plan shape I want:
- Phase 0 as the design says: baseline suites by test ID at this base (licensed; commands in `c381fb00:.project/active/subset-profile-conformance/evidence/baseline.md`), the byte-identity manifest of every generated package before any refactor, and timings.
- Pure moves first (extracting `prepare`/`emit_package`, the shared load) with byte-identity proven after each, then the behaviour changes (the late refusal moving into `prepare`, dropping re-checks, the screen, the report, `check`).
- The readiness rule D8 is PARKED with the owner. Put it in its own last phase, gated on the owner's answer, and make every earlier phase independent of it. Until the owner rules, the phase's checkbox stays open with a pointer to the question. The question: (1) READY = "builds, and nothing the package needs to run is known to be missing", with omitted/excluded findings shown as counts; (2) for the unbound String library default (`candidate-es-010-refusal__string_library_default__unbound_input`), either the owner decides RG-2 (2a's options B or D), or `check` reports "builds, not ready" for it via `unresolved_default_kind` until they do.
- Each phase: what changes, which tests prove it, and the exit check (suite, mypy, ruff no worse than baseline).
Write `.project/active/subset-profile-screen/plan.md` with checkboxes.
