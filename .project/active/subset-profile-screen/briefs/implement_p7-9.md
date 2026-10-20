Phases 4-6 accepted. The extra reachable site (`unexpected_public_failure`) is fine as allowed; update the design's invariant 4 to name it in the Phase 7 or 8 commit.

Continue with Phases 7, 8 and 9, same rules (commit per phase with plan notes, exit check per phase). Stop after Phase 9 and report. Phase 10 (readiness rule) stays gated on the owner; Phase 7's interim rule (A1 in the plan) applies until then.

Phase 8 ships the `check` command and wires the report into `generate`. Hold the design's ordering (D16): in `generate` the screen runs after the seal, and nothing after the seal can change the exit code (D17). The 2a tripwire must still pass.

TEAx execution lane for Phase 9: time-box finding how earlier work built the `CODEGEN_EXECUTION_PROVENANCE` manifest to about an hour. Places to look: the git history of `tests/execution/environment_pins.py` (`git log --follow -p`), the pr-readiness-cleanup archive (`git show a082db22a120f5fa420312f96881a59b71166cd5:.project/` — its close recorded "stock TEAx: 96 passed"), and the ELABORATE-FIRST archives named in `.project/CURRENT_WORK.md`. TEAx is at `~/src/teax`. If you can build it, run the lane and record the receipt. If not, record the lane as not run, say exactly what blocked it, and keep going: that is acceptable, but it must be stated, not implied.
