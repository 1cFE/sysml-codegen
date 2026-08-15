# Audit Brief — Lifecycle Item 4: Diagnostic Severity and Modeled-Default Fidelity

**Stage:** audit (independent; fresh session)
**Candidates:** sysml-codegen `16dbaa7` (evidence commit `6d3d3c5` follows), agentic-mbse
`4c18d61` (pin moved from `515e08bb` — first companion movement since Item 0), TEAx `d545701f`
unchanged.
**Artifacts:** `.project/active/constraint-lifecycle-diagnostics-defaults/{spec,design,design-review,evidence}.md`

## Ratified context (audit mechanisms, not permissions)

All rulings are in evidence.md's PC ledger: chain-aware written_reference (PC-1, cryo_pumps
48.0-vs-32.0 counterexample), C3 row-16 or-expression, revised Gate 1 table (18+5+2 across
seven fixtures), fingerprint-mechanism rewrite (PC-3), sink placement deviation, bracket
safe-miss scope (PC-6), three exclusions with parent-commit reproductions, DD-B1 facts-side
severity. No LOC metrics (owner). Opus cap on suborchestration.

## Priorities (implementer's own pointers first — verify hardest where it flagged)

1. **PC-3 — the certified-seam test rewrite.** `test_fingerprint_stability` now takes only
   `contracts/verify.py` from the reviewed revision and generates both sides from the working
   tree. Verify: the asserted property is genuinely unchanged, the impossibility argument holds
   (verify.py last changed `e217119`, strictly before the carry), and the new loud guard fires
   when the pinned revision stops carrying a different policy. This is the highest-risk
   change in the item — an unsound rewrite here weakens a certified Item 7-family seam.
2. **PC-1 — the chain-aware carry.** Rerun the per-binding (outcome, identity, key_form) probe
   across the corpus and all five request builders; verify zero value movement, zero
   MODULE_OUTPUT transitions, rows 12/13 dead from calc, row 16 or-expression preserving the
   three graph_builder lenient sites; the cryo_pumps binding resolves 32.0.
3. **DD-A03 partial claim.** Verify the partial label is accurate in both directions: the unit
   surface really proves both sinks, AND no end-to-end fixture exists. If a non-finite-literal
   fixture is cheaply constructible, say so (that's a finding, not a fix — it belongs to the
   implementer).
4. **Cross-repo:** facts v1→v2 skew RED in both directions on both routes at the pinned pair;
   `parse` refuses stored-vs-table severity disagreement; `_upstream_pins` single-sourcing;
   the merge-order failure mode reproducible as stated (v2 pin against v1 upstream fails the
   guard test).
5. **Re-capture integrity:** every non-timestamp delta matches the enumeration (format 3→4,
   facts v1→v2, shared_producer source_hash, dropped_constraints removal with parent-commit
   reproduction); v3 snapshot rejection proven; Item 12 interaction (gate before mode read).
6. **R-8/defaults:** DD-A10 zero forced differences claim (Item-1-pinned warning bytes
   untouched); DD-A09's double-path test; signed/unit/arith/absent default matrix; the
   `_parse_default_value` retention justification (531/0/0 measurement).
7. **Gates at both candidates:** suites, -O, license via -rs skips, execution lane, mypy/ruff,
   byte-identity manifests, Items 1–3 acceptance files untouched and green.
8. **Evidence honesty:** checkbox scope notes (SR-A02 bracket limitation inline), open items
   recorded (bracketed convergence, stale-baseline class ×4, tier-1 DD-R32 mirror).

Environment: license via `set -a; source /home/reid/1cfe/agentic-mbse/.env; set +a`, verify
zero license skips (counts do not discriminate). agentic-mbse at /home/reid/1cfe/agentic-mbse.
Never format fixtures/baselines. `.claude/projects/` untouchable.

Verdict: Certify / Pass-with-notes / Needs-work with reproduced evidence. Write audit.md in
the item directory.
