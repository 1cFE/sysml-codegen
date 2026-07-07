# Audit: Plant-Value & Blind-Spot Fixtures (PIPELINE-TRUTH Item 1)

**Verdict:** PASS-WITH-NOTES
**Audited:** 2026-07-06
**Branch:** pipeline-truth-epic
**Commits:** de451e3, 2c29b54, d65c9a7, e9b7b64, 4432989, 98521a8, f64621c

---

## Summary

Item 1 delivers what it contracted. The headline `plant_values` fixture trips V11 today
with a three-offender set covering all three value-provision mechanisms; the secondary
`plant_value_shapes` fixture carries every epic-named shape with property pins (not
byte-equality); `spec_chain_twolevel` gains the plain cross-part-attr and fan-out shapes;
`deep_cross_scope_probe` gets its first committed snapshot plus a drift pin; and the rider
re-captures land in their own reviewed commit. Zero `src/` changes. All three implementer
deviations are recorded and justified.

The notes are documentation-drift and handoff-clarity issues, not code or fixture defects.
The load-bearing one: the Phase-4 revert of mechanism (c) to a one-hop chain removed its
source literal entirely, so headline (c) is now a **trip-only** offender with no value for
Item 2 to wire — qualitatively different from (a)/(b), which carry unwireable literals. This
is defensible (the spec assigns the value-carrying (c) to twolevel), but the Item-2 handoff
and the stale hand-computed anchor over-state that Item 2 "flips" all three headline
offenders. Correct those before Item 2 builds against them.

**Execution caveat (environment, not Item 1):** the audit sandbox is non-interactive and
gates `uv`/`pytest`/`python` execution behind an approval prompt no human can answer, so I
could not re-run `collect_uncovered_params`, the D6 probe, or the license-free suite live.
Everything below is verified statically (committed snapshots + baseline graph + pin sources
+ git) and cross-checked against the implementer's recorded green runs. The D6 gate is
confirmed at the artifact level: the committed baseline graph shows all three `cost_calc`
entry points with `default_value: null`, and the pin asserts exactly the three-mechanism
offender set. See the separate known LiteralReal coupling below.

---

## Verification of reported deviations

**Deviation 1 — `deep_cross_scope_probe` renamed `derived` → `derived_calc`.** VERIFIED and
justified. `derived` is a reserved KerML feature-modifier keyword (KerML §8.2.2.6 Reserved
Words; §7.3.4.2 lists it in the ordered prefix modifiers), so an unquoted feature named
`derived` cannot parse — the fixture was genuinely parse-broken and had never captured. The
rename to `derived_calc` (source line `library.sysml:85`) is a valid closure of D1-F6;
quoting as `'derived'` would also have worked, but the rename is a clean equivalent. The
first-ever committed snapshot lands (`d65c9a7`), closing the silent-drift gap. Source-level
`derived_value` / `derived_calc` identifiers are fine — only the bare token `derived`
collides.

**Deviation 2 — mechanism (c) authored one-hop, not two-hop.** VERIFIED. The truncation pin
exists: `test_deep_cross_scope_probe.py:59` (`test_pattern_a_deep_chain_source_path_truncates_degradation`)
pins that a 2+-hop dot CHAIN truncates its `source_path` to the first segment (`station`).
That degradation is why `deep_cross_scope_probe` is kept out of `SNAPSHOT_MODELS` (it would
fail the global dotted-`source_path` CHAIN invariant) and why headline (c) reverted to the
one-hop `chamber.cost_per_unit`. The one-hop shape still trips as offender #3: the committed
baseline graph shows `PlantValuesDesign__plant__cost_calc__chamber_cost` with
`default_value: null`, and `test_plant_values.py:27` pins it in `EXPECTED_UNCOVERED`. See
Finding F1 for the semantic side effect the revert introduced.

**Deviation 3 — zero escape-hatch filings; all secondary shapes loaded.** VERIFIED. All nine
epic-named shapes are present and loaded in `plant_value_shapes`:
attribute-def-typed nested `:>>` (`'Econ Param'`, `library.sysml:21`), quoted enum def +
usage-level quoted `:>>` (`'Wall Kind'::liquid_wall`, `design.sysml:47`), 5-deep chain with
abstract ends (`'Chain L1'..L5'`, `library.sysml:61`), quoted output param
(`out attribute 'net cost'`, `library.sysml:37`), Style-E mixed `out attribute`+`return`
(`'Mixed Output Style'`, `library.sysml:41`), return-in-quoted-def (`'Quoted Return Calc'`),
bare `default 10.0` (`design.sysml:16`), doc bodies inside a calc usage and on a `:>>`
redefinition (`design.sysml:9,48`), inherited-attr-in-binding-redefined-below (`'Flow Sub'`,
`library.sysml:81`), and the non-float enum EP (`wall`, Item 5 substrate). The fixture-gap
register confirms no extractor crash — the two likely crash candidates (`'net cost'`,
Style-E) both captured CORRECT.

---

## Findings

### Plan completion

All six phases (0–5) verified against their artifacts.

- **Phase 0** (`--fixtures` filter): `scripts/capture_filter.py` + argparse options on both
  capture scripts + `tests/unit/test_capture_fixtures_filter.py`. Scripts-only, no `src/`.
- **Phase 1** (author + rehearsal): all fixtures authored; rehearsal probe recorded the
  three-mechanism offender map.
- **Phase 2** (committed captures + D6 gate + byte-identity gate): D6 gate recorded PASS on
  the committed snapshot; git-status scope clean. Confirmed at artifact level (baseline
  graph, three null-default EPs).
- **Phase 3** (rider, own commit `e9b7b64`): re-captures `wi014_toy`,
  `self_named_binding_trap`, `quoted_owner_formula` and nothing else. The
  `quoted_owner_formula` `net_margin`/`total_payout` design→computed dedup is reviewed and
  confirmed against the prior epic's landed behavior.
- **Phase 4** (property pins, `4432989`): 20 pins across four files, all property-based.
- **Phase 5** (`98521a8`): impact block finalized in `spec.md`; fixture-gap register created;
  CURRENT_WORK updated.

### Spec conformance

- **SC-1 (headline trips V11 on all three mechanisms):** MET. Committed baseline graph:
  three `cost_calc` EPs (`driver_efficiency`, `target_cost`, `chamber_cost`), all
  `default_value: null`. `test_plant_values.py:60` pins the exact three-offender set and
  asserts `len == 3`, so it fails if the set empties or changes — the "before" pin Item 2
  flips. See F1: (c) is trip-only, not value-flippable.
- **SC-2 (twolevel extension):** MET. `test_spec_chain_twolevel.py:127`
  (`test_fanout_collapses_to_one_producer_channel`) pins `scale_a.s` and `scale_b.s`
  collapsing to the single EP `TwoLevelLib__IFE_Power_Plant__scale`;
  `test_plain_cross_part_attr_shape` (`:138`) pins `maint_calc.rate` →
  `TwoLevelLib__IFE_Driver__maintenance_rate`. The existing `usage_type_map`, gamma-channel,
  and `cost_per_joule`-wired pins are preserved.
- **SC-3 (per-shape observed-property pins):** MET. `test_plant_value_shapes.py` asserts
  concrete properties (bare `default` == "10.0"; quoted `'net cost'` de-quotes to `net_cost`;
  Style-E yields `{doubled, tripled}`; non-float `wall` EP is `None`, float sibling
  `footprint` == 12.0; econ-param nested `:>>` degraded to `None`). No whole-snapshot
  byte-equality pins (spot-checked four; grep-confirmed by the implementer). See F3 on one
  brittle assertion.
- **Assert-constraint substrate:** MET (as observed absence). Snapshot carries no
  `viability` usage and zero `eta`/`viability` tokens; `test_assert_constraint_is_invisible_today`
  pins the CONSTRAINT-SILENCE before-state; the `threshold` param leaks into
  `design_attributes` and is pinned (`:108`). Item 4 substrate recorded.
- **`deep_cross_scope_probe` committed snapshot + drift pin:** MET (`d65c9a7` +
  `test_deep_cross_scope_probe.py`).
- **Stale-fixture-refresh rider:** MET (own commit; reclassification reviewed).
- **Byte-identity of untouched baselines:** MET. Per-commit `--stat` shows each commit
  touches only its deliberately-touched set; no `catf_mfe`/`solar_battery`/`sample_model`/
  `ife_plant`/etc. baseline moved.
- **Fixture-gap register + Item 9 impact block:** MET. Register lists the four deferred D6
  shapes each with a §D6 pointer, escape-hatch = none (with evidence), plus three pinned
  degradations. The spec's Item-9 impact block names concrete `tests/fixtures/` paths per
  shape.

**Non-goals respected:** zero `src/` changes; no cross-part wiring of the headline (that is
Item 2); deferred shapes filed, not built.

### Design conformance

No design.md (fixtures + captures — correct per spec). The layout follows the ife_plant
plant-idiom (library/design split, provenance doc-comments, base-def-owns-calc + usage-level
overrides). Mechanism labels (a/b/c) are the discovery-§D6 partition, not the memory-note
A/B/C/D — used consistently throughout.

### Code integrity

- Zero `src/` production changes across all seven commits (confirmed by `git diff --stat`
  over the range restricted to `src/` — empty).
- The D7 `--fixtures` filter is factored into a shared, unit-testable pure function
  (`capture_filter.py`) rather than duplicated — a cleaner closure than the plan required.
- No silent fallbacks introduced: unknown `--fixtures` name exits non-zero naming the
  offender (fail-loud). Tests confirm.

---

## Findings requiring attention (all NOTE-level — do not block Item 1)

**F1 — Headline mechanism (c) is trip-only, not value-flippable; the Phase-4 revert dropped
its source literal.** `tests/fixtures/plant_values/{library,design}.sysml`.
The two-hop original supplied `chamber.liner.cost_per_unit = 7.0` via a nested override — a
real value the pipeline could not wire (a true "before" state Item 2 flips to 7.0). The
Phase-4 revert to one-hop `chamber.cost_per_unit` removed the override entirely: the snapshot
shows `cost_per_unit` only as a binding `source_path`, with no redefinition, override, or
literal anywhere. Contrast (a) `efficiency = 0.35` (`hierarchy_data.redefinitions`) and (b)
`cost_per_target = 10.0` (`design_overrides`) — both carry unwireable literals.
Consequence: when Item 2 lands cross-part wiring, (a)/(b) resolve to 0.35/10.0 and clear as
offenders; (c) has nothing to resolve to and stays a valueless user-fill EP. So SC-1's "the
before state Item 2 flips" holds for (a)/(b) but over-states (c). This is defensible — the
spec assigns the value-carrying (c) to twolevel (`maintenance_rate`), and headline (c) as
"V11-trip role only" is spec-blessed — but the Item-2 handoff should say explicitly that
headline (c) is a trip-only offender, not a value-flip. Worth a one-line note in
CURRENT_WORK's Item-2 handoff. (The forced nature is real: a base-def literal yields a valued
EP and doesn't trip; a usage override IS mechanism (b); a two-hop chain trips-with-value but
truncates `source_path` — so a distinct, value-carrying, V11-tripping (c) has no legal
one-hop layout. Valueless was the available resolution.)

**F2 — Stale hand-computed anchor.** `plan.md` Phase-1 Completion (~line 724) records
`plant_cost = (target_cost + chamber_cost) / driver_efficiency = (10.0 + 7.0) / 0.35 =
48.5714…`. The `7.0` is the two-hop `chamber` value the Phase-4 revert removed; `chamber_cost`
now has no source value, so this expected value is unreproducible from the committed fixture.
The spec's [INFERRED] SC-B lineage anchor should be corrected (recompute without a (c) term,
or state that headline (c) carries no value and the (c) after-state is anchored on twolevel).
Left stale, Item 2 would validate its after-state against a number the fixture can't produce.

**F3 — Brittle substring assertion in the constraint-invisibility pin.**
`test_plant_values.py:104` asserts `blob.count("eta") == 0` on the whole snapshot JSON. It
passes today only because this snapshot happens to contain no `eta`-substring word; a future
snapshot-format field such as `metadata` (or `beta`/`theta`/`meter`) would make it fail
spuriously — a false drift signal, not a real regression. The sibling `blob.count("viability")`
is specific and fine. Tighten the `eta` check to a token/word-boundary or key-scoped test.

**F4 — Live execution unavailable in the audit environment (process note).** As stated in
the summary, the sandbox gated `uv`/`pytest`/`python` behind an un-answerable approval prompt,
so the D6 probe and the license-free suite were not re-run here. Verification is static +
recorded-run cross-check. Per the brief's known-issue note, the license-gated suite is
independently red from a concurrent Item-4 session's uncommitted agentic-mbse adapter edit
(`Unknown type name 'LiteralReal'`) — not Item 1's fault and not exercised here; Item 1's
greenness rests on the license-free conformance pins, which read committed snapshots only.

---

## Certification

Verified: zero `src/` changes (git); per-commit byte-scope (git `--stat` × 7); all three
deviations (KerML keyword spec via kerml-expert; truncation pin source; nine secondary-shape
sources); the D6 three-offender before-state at the artifact level (committed baseline graph
= three null-default EPs; the pin asserts the exact set); (a)/(b) source literals present and
(c) source value absent (snapshot `redefinitions`/`design_overrides`); property-pins not
byte-equality (four spot-checked); fan-out collapse and plain-attr twolevel pins; assert-
constraint invisibility (zero `viability`/`eta` tokens); fixture-gap register and Item-9
impact block concrete; rider own-commit scope and reviewed reclassification.

Not re-executed live (environment gate): `collect_uncovered_params`, the D6 probe, the
license-free suite. Confidence remains high via the static + recorded-run cross-check.

Item 1's deliverable — fixtures that trip V11 on three mechanisms and pin each blind-spot
shape's observed behavior — is met. The four notes are documentation/handoff hygiene; F1 and
F2 should be resolved before Item 2 builds against the headline's (c) before-state.

Marked: spec SC-1/SC-2/SC-3 and the capture-hygiene / register / impact criteria verified
met; plan already Complete; epic Item 1 success criteria met (heading left for the epic-scope
audit to append ✅, since F1/F2 are open handoff notes).

ARTIFACT: .project/active/plant-value-fixtures/audit.md
