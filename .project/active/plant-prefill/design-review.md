# Design Review: Plant-Idiom Literal Pre-Fill (Item 9)

**Design:** `.project/active/plant-prefill/design.md`
**Spec:** `.project/active/plant-prefill/spec.md`
**Review File:** `.project/active/plant-prefill/design-review.md`
**Date:** 2026-07-05
**Reviewed at HEAD:** 354a09c (design), working tree

---

## Fundamental Assessment

**Sound approach, one load-bearing invariant is false.**

The shape of the fix is right and minimal: relax an over-broad guard, filter the newly-scanned
plain usages to LITERAL, reuse the existing deep-path rewrite, and harden the rewrite (shallow
per-instance copy, bare-name skip). No new abstraction, no parallel mechanism. Three one-function
edits. I would not ask for a rework of the approach.

But the design rests on a checkable invariant — **B2 / INV-5: relaxing the guard captures no
plain-usage LITERAL override in any committed fixture besides the three named** — and that
invariant is **false**. `unresolvable_attr_probe` is a fourth committed-snapshot fixture with
plain-usage LITERAL `:>>` overrides, and it is not any ordinary fixture: it is **the dedicated
V11 proof fixture** that Item 7's safety boundary depends on. The guard relaxation reaches into
it, and on a live re-capture it can dismantle that proof. This is not a rework, but it is a
Critical gap that must be resolved before implementation — the design's impact analysis, its
regen set, and its pin-flip checklist are all incomplete because of it.

The rest of the design (D2 shallow-copy, D3 filter placement, D4 issue22 coverage, the divergent-
sibling and bare-name tests) checks out on inspection. Details below.

---

## The Critical finding, traced

**`unresolvable_attr_probe` carries plain-usage LITERAL overrides on two plain usages**
(`design.sysml:40–51`):

```
part derived_instance : 'Derived Component' {
    :>> base_rate = 10.0;  :>> base_factor = 2.0;  :>> local_multiplier = 3.0;
}
part design_derived_instance : 'Design Derived' {
    :>> base_rate = 10.0;  :>> base_factor = 2.0;  :>> local_val = 5.0;
}
```

Both are **plain** usages (no `redefines`), so `owned_redefinitions` on the usage is empty and
today the guard (`hierarchy_resolver.py:187`) skips them. Their committed snapshot has
`"design_overrides": []` (`extraction_snapshot.json:165`). These are bare-name **LITERAL** RHS —
exactly the class the relaxed guard is built to capture, and the D3 LITERAL filter does **not**
exclude them (they are literals). So after relaxation, `design_overrides` gains ≥6 entries. That
alone churns a committed snapshot the design promises stays byte-identical (INV-5), and refutes
B2 as written.

**It goes deeper than a snapshot diff.** The instance calc `design_derived_instance__my_calc` has
a live `reference` binding (`extraction_snapshot.json:64–66`):

```
param_name: x
source_path: "UnresolvableAttrProbeDesign::'Design Derived'::local_val"
binding_type: reference
```

The newly-captured `:>> local_val = 5.0` on `design_derived_instance` is a non-deep-path LITERAL.
In `_rewrite_virtual_bindings` phase 1 it is keyed `(owning_part_qn, 'local_val')`
(`pipeline_builder.py:211–213`). The `my_calc` binding's parent path is
`UnresolvableAttrProbeDesign__design_derived_instance` and its leaf (via `::` rsplit) is
`local_val`. Those keys match, so phase 2 rewrites `x` from a reference to `LITERAL 5.0` and
clears `source_path` (`:248–252`).

**Why that matters:** `my_calc.x` is the **wired valueless entry point** that anchors Item 7's
V11 proof. `test_uncovered_params.py` pins it (`:104 test_collector_pins_unresolvable_attr_probe`
→ `[("x","my_calc")]`) and its docstring calls this fixture "the dedicated V11 proof" and "the
only committed real-fixture that exercises" the strict boundary (module docstring, `:9`).
`test_reconcile_raises_v11_on_wired_gap` (`:129`) feeds this same graph to prove the generation
boundary raises V11. If the guard relaxation fills `x` from `local_val = 5.0`, then `x` is no
longer valueless: the collector pin flips to `[]` and the V11 raise no longer fires. **Item 7's
only committed V11 proof evaporates.**

**The two ways this lands, both bad:**

1. **If the byte-exact / baseline sweep re-runs live extraction for all fixtures** (Validation
   step 3), `unresolvable_attr_probe` churns and the sweep **fails** — surfacing the problem at
   implement, but proving INV-5 / B2 wrong.
2. **If the sweep only regenerates the enumerated three**, the committed `unresolvable_attr_probe`
   snapshot goes **stale** — it no longer reflects true live extraction. The offline collector
   pins keep passing on the stale bindings, so the divergence is invisible until someone re-captures
   the snapshot, at which point the V11 proof silently collapses. This is the *same* latent-snapshot
   hazard the spec-review caught for `BindingInfo`, reappearing one layer over.

**The real question the design must answer** (not a regen detail): is `my_calc.x` *supposed* to be
pre-filled by `:>> local_val = 5.0` now? A defensible reading says yes — its valueless-ness was
itself a symptom of the very dropped-plain-usage-override bug Item 9 fixes. If so, the V11 proof
must be **re-anchored** to a fixture whose valueless input is genuinely unbound (not a droppable
plain-usage literal), or the guard predicate narrowed so this fixture is untouched (though the
LITERAL filter alone won't do that). Either way it is a design decision, not a snapshot bump.

**Scope of the churn, corrected.** The complete set of committed fixtures whose extraction output
changes under the relaxed guard is **four**, not three:

| Fixture | Plain-usage LITERAL `:>>` | Committed snapshot? | In design's regen set? |
|---|---|---|---|
| `ife_plant` | `capacity_factor = 0.95` | yes | yes |
| `alias_agg_probe` | `widget.base_cost = 50.0` | yes | yes |
| `issue22_model` | `widget.base_cost = 100.0` | yes | yes |
| **`unresolvable_attr_probe`** | `base_rate`, `base_factor`, `local_multiplier`, `local_val` | **yes** | **no — MISSED** |
| `deep_cross_scope_probe` | `reading = 10.0`, `baseline_value = 2.0` | no (orphan; no test refs) | n/a — safe |

`solar_battery` and `chain_override_probe`'s literal `:>>` overrides sit on `part redefines`
usages — already captured today, unaffected. `catf_mfe` is CHAIN — the LITERAL filter keeps it
out, stays V11-pinned. Those parts of the design's invariance hold.

---

## Dimensional Review

### 1. Spec Compliance
**Assessment:** Concerns

The design implements the spec's revised scope faithfully (guard relax + LITERAL filter, shallow
copy, bare-name skip, D1 live re-capture). But the spec's SC "existing 4 committed baselines
byte-identical EXCEPT ife_plant / alias_agg_probe / issue22" carries the same three-fixture
under-count, and the design inherits it verbatim (INV-5). The `unresolvable_attr_probe` interaction
means an SC the item promises cannot be met as stated. The design should have caught this in its
own B2 verification ("the byte-exact suite is the guard") rather than asserting B2 true.

### 2. Pattern Consistency
**Assessment:** Pass

Reuses `_extract_single_redefinition`, `_rewrite_virtual_bindings`' deep-path matcher, and the
capture/load split. No parallel matcher (R1 honored). The `is_part_redefines = bool(...)` +
always-scan + `continue`-on-non-LITERAL shape (Implementation Notes) is the minimal change and
preserves the `part redefines` path unchanged (INV-4 holds — same objects, same order for that
branch).

### 3. Abstraction Quality
**Assessment:** Pass

No new abstraction. Three one-function edits along the existing flow. D2 correctly mints each
instance's own scalars while sharing read-only AST references. This is the right altitude.

### 4. Duplication Avoidance
**Assessment:** Pass

D4's issue22 clean-generation test is proposed as a shared body / second parametrization of the
alias_agg_probe generation test — reuse, not a fork. Good.

### 5. Data Structure Clarity
**Assessment:** Pass (D2 verified)

I verified `BindingInfo` field-by-field (`usage_extractor.py:63–73`). Top-level fields only:
`param_name`, `source_path`, `binding_type`, `is_cross_file`, `raw_expression`, `literal_value`
(scalars/enums), plus three object references (`source_instance_elem`, `source_attribute_elem`,
`expression_ast`). **There is no nested mutable container** (no list/dict field) that a shallow
copy would keep shared. The rewrite reassigns only `binding_type`, `literal_value`, `source_path`
(`pipeline_builder.py:249–254`) — all top-level scalar reassignments on the copy, invisible to
siblings. The AST references are read-only (accessed via `source_instance_name` / `source_attribute_name`
properties, `:75–90`), never mutated. **So `copy.copy(b)` is sufficient and correct**, and B3 is
verified true. `copy.deepcopy` would indeed recurse into `expression_ast` / `source_instance_elem`
(SysIDE parse subgraph) — rightly rejected. D2 is sound.

### 6. Route Safety
**Assessment:** Concerns

The bare-name skip-with-DEBUG (REQ-VBR-09) replacing the `raise` at `pipeline_builder.py:242` is
the right call — skipping is safe here because leaving the binding unchanged is the pre-relaxation
behavior for any binding the index doesn't cover, and the `self_named_binding_trap` fixture's
degenerate self-reference before-state is explicitly preserved (Non-Goals). One correction to the
design's framing: it calls REQ-VBR-09 "defensive (no committed fixture triggers it)." That is only
true because `unresolvable_attr_probe`'s `my_calc` source_paths are `::`-qualified (they hit the
`::` branch, not the bare-name `else`). So the raise is not reachable *there* — but the design's
reason ("no committed fixture combines a non-empty index with a bare-name source path") is now
thinner than stated, because `unresolvable_attr_probe` *does* produce a non-empty index. Worth a
one-line correction, not a blocker.

### 7. Bets & Decisions Integrity
**Assessment:** Fail (B2 is false as written)

- **B2 is refuted** (see Critical). It is a genuine, checkable bet — and it is wrong. The design
  even lists "unintended capture (B2)" under Potential Risks with the byte-exact sweep as
  mitigation, but then asserts B2 holds. The mitigation is exactly what would have caught it; the
  bet should not have been marked settled without running it.
- **B1 (probe faithful) and B3 (only scalars mutated)** are sound; B3 I verified directly.
- **Hidden bet surfaced:** the design assumes the *offline* collector pins are a faithful gate for
  the flip. They are only faithful if the underlying snapshot is regenerated. For
  `unresolvable_attr_probe` the design does *not* regenerate the snapshot, so its pin would keep
  passing on stale bindings while live extraction diverges — the unstated bet "not regenerating a
  snapshot is harmless" is false for any fixture the guard now newly touches.
- **D1 / D2 / D3 / D4** are real decisions with named rejected alternatives. D3's rejection of the
  rewrite-site filter (RedefinitionData carries no "from plain usage" flag) is correct and I confirm
  the field is absent.

### 8. Reader Comprehension
**Assessment:** Pass

Core Concept states the mechanism plainly before the details, and the shape-5 correction is called
out for sign-off rather than buried. The Appendix evidence is concrete and locatable. The one
comprehension cost is that the reader is told "only three snapshots change" as settled fact
(Research Findings, Test Design, INV-5) — which, being false, actively misleads. Fixing the
Critical finding fixes the comprehension issue.

---

## Issues by Severity

### Critical
- **C1 — `unresolvable_attr_probe` is a fourth churned fixture and it is the V11 proof anchor.**
  The relaxed guard captures its plain-usage LITERAL overrides; on live re-capture the
  `local_val = 5.0` override rewrites `my_calc.x` to a literal, collapsing the collector pin
  (`test_uncovered_params.py:104`) and the V11 raise proof (`:129`). B2 / INV-5 are false. The
  design must (a) enumerate this fixture, (b) decide whether `x` *should* now pre-fill, and (c)
  if so, re-anchor the V11 proof to a genuinely-unbound input. [Dim 1, 7]

### Major
- **M1 — pin-flip checklist is incomplete.** It omits `test_collector_pins_unresolvable_attr_probe`
  and `test_reconcile_raises_v11_on_wired_gap`, both of which the guard relaxation affects. The
  checklist is supposed to be the definitive flip set; as written an auditor would not know these
  two moved. [Dim 1]
- **M2 — B2 asserted without running the sweep it names as its own guard.** Process gap: the one
  check that refutes B2 is the check the design defers to implement. Run the full baseline sweep (or
  a static plain-usage-`:>>` grep across all committed-snapshot fixtures) *before* freezing the
  regen set. [Dim 7]

### Minor
- **m1 — REQ-VBR-09 "no committed fixture triggers it" is now thinner.** `unresolvable_attr_probe`
  produces a non-empty index (its source_paths are `::`-qualified so the raise still isn't reached,
  but the stated reason should be corrected). [Dim 6]
- **m2 — `deep_cross_scope_probe`** has plain-usage LITERAL `:>>` too, but no committed snapshot and
  no test references it — its live extraction changes with nothing asserting it. Note it so a future
  snapshot capture isn't a surprise. [Dim 1]

---

## Recommendations

1. **Resolve C1 before implementing.** Decide the intended semantics for `unresolvable_attr_probe`'s
   `my_calc.x`: is pre-filling it from `:>> local_val = 5.0` correct (the drop was the bug) or must
   this fixture be held constant? If pre-fill is correct, re-anchor Item 7's V11 proof to a fixture
   whose valueless input is genuinely unbound — not a droppable plain-usage literal — and add
   `unresolvable_attr_probe` to the regen set and the pin-flip checklist with the correct from→to.
2. **Run the invariance check now, not at implement.** A static grep for plain-usage (non-`redefines`)
   LITERAL `:>>` across every committed-snapshot fixture settles B2 deterministically and license-free.
   Update B2 / INV-5 / the regen enumeration to whatever it returns (this review found four:
   ife_plant, alias_agg_probe, issue22_model, unresolvable_attr_probe).
3. **Keep D2, D3, D4, and REQ-VBR-09 as designed** — they verify out. Correct the REQ-VBR-09 rationale
   sentence (m1).

---

## Resolutions

Resolved 2026-07-05; design.md updated in place.

- **C1 (the decision):** Pre-filling `my_calc.x` from `:>> local_val = 5.0` is **correct** — its
  valueless-ness was the very dropped-plain-usage-override bug Item 9 fixes. Recorded as **D5**.
  The "dedicated committed V11 proof" role re-anchors to the two genuinely cross-part inputs that
  stay wired-valueless until Item 10: **catf_mfe `[cryo_load.magnet_volume]`** and **ife_plant
  shape-4 `magnet_volume`**. `unresolvable_attr_probe`'s full violation list traced to **`[]`**
  (its only wired binding is `my_calc.x`; `'Derived Component'` has no calc) → clean strict
  generation. Item-7 docstrings/comments that call it "the only committed real-fixture / dedicated
  V11 proof" are updated (pin-flip checklist row added).
- **M1:** Pin-flip checklist now folds in `test_collector_pins_unresolvable_attr_probe`
  (`[("x","my_calc")]` → `[]`), `test_reconcile_raises_v11_on_wired_gap` (re-anchor → catf_mfe),
  and `test_seeded_strict_generation_aborts_independently_of_catf_mfe` (re-anchor → ife_plant).
- **M2 / B2:** The license-free plain-usage-`:>>` sweep was run across all committed-snapshot
  fixtures and tabulated (Architecture → B2 sweep). Definitive affected set = **four**
  (ife_plant, alias_agg_probe, issue22_model, unresolvable_attr_probe). Verified `solar_battery`
  and `chain_override_probe` literals sit on `part redefines` (unaffected); `catf_mfe` is CHAIN
  (filtered); `wi014_toy` none; `deep_cross_scope_probe` orphan (no snapshot). B2 rewritten as
  corrected-and-run; INV-5 restated to "exactly the four change, rest byte-identical, verified by
  the full re-capture sweep."
- **m1:** REQ-VBR-09 rationale corrected — `unresolvable_attr_probe` produces a **non-empty**
  index; the raise stays unreached because its reachable source_paths are `::`-qualified (they
  take the `::` branch, not the bare-name `else`). Guarantee now stated by-branch, not by-empty-
  index.
- **m2:** `deep_cross_scope_probe` noted — plain-usage LITERAL `:>>`, no committed snapshot, no
  test reference; its live extraction changes silently. Flagged so a future capture is not a
  surprise.

**Unchanged (verified sound by the review):** D2 shallow-copy, D3 filter-at-capture, D4 issue22
coverage, the divergent-sibling test, and the D1 regeneration decision (now over four snapshots).

---

**Overall:** Revise
**Next Steps:** Resolve C1 first — it determines whether the V11 proof needs re-anchoring and how
much the regen set / pin-flip checklist grow. Once resolutions are recorded here, re-run
`/_my_design` (or return to the design-agent session) and point it at this review to incorporate.
The reviewer does not edit the design.
