# Brief — implement: nested-override-tripwire (unmatched-override warning in the supplied-value materializer)

**Owner directive (2026-07-24):** add a defensive tripwire for the `[NESTED-OCCURRENCE-OVERRIDE]`
silent-value-loss shape (read that BACKLOG.md entry first — it has the verbatim root cause at
pin `7526665`). This is the interim guard, NOT the full occurrence→definition-bridge fix —
scope is a warning, zero behavior change to resolution or generated output.

**Branch:** `nested-override-tripwire` (you are on it). Baseline: docs-lifecycle-sync tip.

## The failure shape to catch

In `resolution/supplied_values.py`, `enrich_graph_design_attributes` (`:517`): a demand whose
`resolve_logical_demand` returns `value is None` with `nonliteral=False` and
`malformed_literal=False` falls through **silently** (`:563-573` → `continue`). For the
nested-occurrence shape, an extracted override for that very attribute EXISTS
(`design_overrides` carries `owning_part_qn='..._Design__panel'`, `attribute_name='reading'`)
but matches at no tier because capture is definition-relative and demand is
occurrence-relative. The modeled value is lost with no diagnostic.

## Predicate design (orchestrator-analyzed; verify, then implement)

Do NOT warn on every silent fall-through — most demands legitimately have no supplied value.
Do NOT warn on every never-matched override — overrides on attributes no calc/constraint
consumes are legitimate (this is the site-4/D3-12 false-fire precedent; see the BACKLOG
`[D3-HYGIENE-TAIL-SITE4-TRANSITIVE-ALIAS]` entry for the cautionary tale).

The narrow predicate: warn only when a demand falls through silently AND some entry in
`design_overrides`/`redefinitions` shares the demand's leaf attribute name (and, if it keeps
the corpus clean, the part-usage leaf too) — i.e., "an override for this attribute exists but
matched at no tier; captured scope X vs demanded scope Y." That is precisely the
qualifier/occurrence mismatch and nothing else. The warning must name both scopes and the
attribute so a modeler can act on it, and reference `[NESTED-OCCURRENCE-OVERRIDE]`.

## Phases (all mandatory, in order)

**Phase 0 — corpus false-fire scan (gate; stop and report if it fails).** Before writing the
warning: implement the predicate as a probe (script under
`.project/active/nested-override-tripwire/probes/`, committed) and run it across ALL committed
snapshot fixtures the conformance suite uses (the `SNAPSHOT_MODELS` set — find it in
`tests/conformance/conftest.py` or equivalent). Record per-fixture fire counts in
`probes/verdict.md`. INV: every currently-clean fixture must produce ZERO fires. If any clean
fixture fires, do NOT weaken the fixture or ship the warning — narrow the predicate and
re-scan; if it cannot be narrowed to zero false fires, STOP and report (that outcome is the
site-4 story again and needs a design decision, not a shipped WARN).

**Phase 1 — RED.** Unit test(s) in `tests/unit/test_supplied_values.py` style: construct the
recorded mismatch coordinate (owning_part_qn `...__Design__panel` vs instance scope
`...__the_design__panel`, `target_path=['source','reading']`, LITERAL 80.0 — from the BACKLOG
entry) and assert, via `caplog`, that the warning FIRES with both scopes named — failing
before the implementation exists. Also a negative test: a demand with no matching-name
override anywhere stays silent (INV-6 discipline: silent-on-clean is load-bearing and must be
pinned, not assumed).

**Phase 2 — implement.** The warning in `enrich_graph_design_attributes`, following the
file's existing diagnostics pattern (collected during the loop, drained once after it, one
logical warn per normalized target — see I7 in the docstring and how `collisions`/
`malformed_targets` drain). Match the module's comment/naming idiom. No resolution behavior
change, no new synthesis, no output change.

**Phase 3 — gates.**
- Full suite with license: `set -a; source /home/reid/1cfe/agentic-mbse/.env; set +a` then
  `uv run --frozen pytest -q -rs tests/`. Expected: prior baseline (3115 passed / 47 skipped)
  plus your new tests, ZERO `no live syside license` skip lines (the skip-line check is the
  only valid license proof).
- `uv run ruff check src/` clean; `uv run mypy src/` no NEW errors (72 pre-existing accepted).
- Byte-check: the corpus conformance tests passing green IS the no-output-change proof
  (baselines are byte-compared); state this in the evidence.

**Phase 4 — bookkeeping.** Write a short `.project/active/nested-override-tripwire/evidence.md`
(probe verdict, RED→GREEN, gates). Amend the BACKLOG `[NESTED-OCCURRENCE-OVERRIDE]` entry with
one line: the calc-path silent loss now warns (tripwire, 2026-07-24); the full
occurrence-bridge fix remains the filed work. Update the docs honesty note in
`docs/architecture/modeling-assumptions.md` (the R5 limitation paragraph): "silently drops"
→ "drops with a warning naming both scopes" — keep the rest intact. Update the
`nested_occurrence_override_probe` fixture's PROVENANCE.md only if it states the calc path is
silent.

Commits: one for the probe + verdict, one for RED+implementation+gates+bookkeeping (or split
further if natural). Trailer: `Co-Authored-By: Claude <noreply@anthropic.com>`.

Finish with `ARTIFACT: .project/active/nested-override-tripwire/evidence.md`.
