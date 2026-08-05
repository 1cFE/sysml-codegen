---
date: 2026-08-03T20:30:11-07:00
researcher: Claude
topic: "Entry-surface fan-out: how the shared-attribute rebinding bug survived the design/review pipeline"
tags: [research, forensics, backtracker, entry-points, mechanism-d, process]
status: complete
last_updated: 2026-08-03
---

# Research: How the entry-surface fan-out bug survived the pipeline

**Date**: 2026-08-03 (PDT)
**Researcher**: Claude (orchestrator + 3 archaeology subagents + 1 spec ruling)
**Research Type**: Forensic (mechanism + documentary + git archaeology)

## Research Question

**[OWNER-VERBATIM]** (2026-08-03): "The next agent is going to have to research and tell me
how the fuck such a basic fucking bug slipped through our 100x design stage process."

The bug: one SysML attribute, authored once at plant level and consumed by several calc
usages via `in R = R`, becomes multiple independent entry fields in the generated package
(`…__geom__R` and `…__rb__R`; `recirc_calc__gain` and `lcoe_calc__gain`). Sweeping one
copy leaves the others frozen at the captured design point — silently inconsistent
evaluations. Confirmed and reproducible at the demo pin (`06d95f8`) and at the Item-8/9-era
pin; the fan-out is also in committed fixtures at merged main.

## Summary

- **Verdict: NEVER-BUILT.** Per-usage entry-point minting (`{usage_qn}__{param}`) is in
  the initial commit (2025-12-31); no historical version ever emitted a shared field for
  this shape; nothing regressed. **[OWNER 2026-08-03]** the intent needs no citation:
  backtracking symbols to a single set of source inputs *is the point of this library* —
  bound parameters in a SysML model must never be simulated independently. The forensic
  finding is that the requirements apparatus never encoded that founding purpose as a
  checkable property for the calc path: the matrix specifies the *mechanism* (how a miss
  is minted — REQ-IR-06) and never the *mission* (one attribute → one field), so 276 rows
  pass while the point of the library fails on the customer's first sweep.
- **The bug shape was seen, named, fixtured, and dispositioned — as someone else's
  problem.** "Mechanism D" (self-named bindings resolve to the calc's own parameter) was
  identified 2026-07-05, given a trap fixture, and the unrescued case was labeled "the
  genuine modeling error" in code. Its general form — "two calcs reading one design
  attribute mint two JSON keys" — was written down the same day, and the follow-up
  (a syside vendor note) was recorded as **unfiled** and never filed.
- **The two big refactor PRs could not have caught it — by design.** The owner's two
  backtracking refactors (PR #2 OUTPUT-REGISTRY, PR #9 CONSTRAINT-EXEC; largest src churn
  of any PRs) were *preservation* refactors whose stated success criterion was byte-for-byte
  reproduction of the entry-point fallback. Their painstaking reviews verified faithful
  preservation — and faithfully preserved the fan-out. Committed baselines pin it as ground
  truth (`inner_radius` minted 13×, `fab_factor` 8×); one acceptance test hardcodes the
  fanned key with a comment rationalizing the split.
- **The customer's path is silent by construction.** The demo/IFE shape takes a code path
  (instance `:>>` override stamped into each self-named binding by leaf-name coincidence)
  that emits **zero diagnostics**: no lenient-miss warning, no completeness flag (clean
  entry points are exempt by owner decision D-1), no phantom check (the detector is not
  wired into the pipeline). Values stay consistent at every single-point run, so every
  acceptance gate passed honestly.
- **The last line of defense normalized it.** Nine days before discovery, downstream
  research named the fan-out "a sweep hazard nobody had named" (class A6), prescribed a
  consumer-side workaround, and filed a *different, smaller* finding upstream — not this.
- **Spec twist: SysIDE is right and the idiom is degenerate.** Per KerML nearest-scope
  resolution, `in R = R` is a self-binding (the parameter shadows the outer attribute);
  the spec-correct form is `in R = stellaris::R`. But the pipeline already *reinterprets*
  the idiom as "the outer attribute" on the constraint path and in SR-A02's calc+constraint
  fix — so the same line of SysML means three different things depending on which consumer
  reads it, and no layer warns on the degenerate form. That semantic ruling
  (reject-loudly vs converge-uniformly) is the owner decision a fix hangs on.

## The mechanism (verified at HEAD and at the pins)

There are **two distinct fan-out paths**. Both destroy the shared identity; they differ in
whether anything is logged.

### Step 0 — extraction resolves `in R = R` to the calc's own parameter

SysIDE resolves the bare right-hand-side `R` to the calc usage's **own input parameter**,
not the enclosing part's attribute. The demo snapshot records it directly:
`raw_expression: "FeatureReferenceExpression -> mfe_plant::'MFE Power Plant'::geom::R"`
(the calc's own param) for the binding of `geom.R`. Same for the trap fixture
(`tests/conformance/test_self_named_binding_trap.py:69` pins
`source_path == "TrapLib::'Trap Plant'::avail_calc::availability"`). The extractor stores
the referent's *resolved* QN (`extraction/usage_extractor.py:831-842`), so the link to the
plant attribute is severed at extraction. (Whether this resolution is spec-conformant is
addressed under "The spec ruling" below.)

### Path A — silent LITERAL stamp (the customer/demo/IFE-package bug)

When the design instance carries a `:>>` literal for the attribute (demo: `R = 12.7`;
IFE: `hif_plant.sysml:87` `:>> gain = 80.0`), the hierarchy rewrite
(`orchestration/pipeline_builder.py:285-379`, dating to COST-PATTERN, 2026-02-22) matches
the binding by `(parent_path, leaf_name)` — and the leaf of the self-reference QN is the
same string as the attribute name (that is what "self-named" means). The match is a **name
coincidence, not identity resolution**. It stamps `binding_type=LITERAL,
literal_value=<override>, source_path=None` into *each* consuming usage's binding
(`pipeline_builder.py:363-369`).

Downstream, the backtracker's LITERAL branch (`analysis/dependency_backtracker.py:445-463`)
mints one entry point per usage and **never calls the resolver** — so the lenient-miss
warning, the producer-completeness capture sink, and row 16 are all unreachable.
Classification lands on `USAGE_LITERAL` via the **catch-all else branch**
(`resolution/graph_builder.py:534-579`) — the label reads as "the modeler wrote a literal
here," which is false; it is a mis-resolved reference wearing a literal's clothes. An
offline build of the fusion_tea fixture emits **0 warning lines**.

Because every copy is stamped from the same override, all copies agree at capture — the bug
is invisible at any single-point run and only manifests when someone sweeps one copy.

### Path B — warned REFERENCE lenient miss (ife_plant fixture shape)

With only a def-level default (no instance `:>>`), the binding stays a self-referential
REFERENCE and reaches `resolve_producer`. Every row misses — row 16 requires the attribute's
extracted QN to equal the occurrence owner path, which holds only for attributes declared
directly on the owning part *usage* (the `shared_producer` fixture), not for def-declared
attributes materialized into an instance; rows 19-21 require dotted/bare references, not the
`::`-qualified self-ref QN. The terminal LENIENT miss mints `{usage_qn}__{param}`
(`producer_resolution.py:553`) **with** a log warning. Same fan-out, one log line.

### Why constraints don't fan out

The constraint consumer resolves actuals by exact identity (STRICT, `target_qn`) to the
source attribute — one field (`hif_plant_pkg__hif_plant__gain`). Hence the observed
asymmetry that localized the defect: the same attribute converges for a constraint and
fans out for calcs. The committed `solar_battery` baseline shows the same asymmetry on
`pack_count` (constraint/aggregation converge, calc consumer fans out).

## Timeline

| Date | Event |
|---|---|
| 2025-12-31 | Initial commit (`36bd2c2`): per-usage entry-point minting at every fallback site of `dependency_backtracker.py` (lines 269, 358, 448, 465). The fan-out is original behavior. |
| 2026-02-22 | COST-PATTERN (`d6c725f`): hierarchy override rewrite introduces the Path-A LITERAL stamp. `catf_mfe` baseline committed with `inner_radius`/`outer_radius` minted **13× each** — fan-out pinned as ground truth from day one of hierarchy support. |
| 2026-07-05 | UPSTREAM-FINDINGS deep research: mechanism D named (`20260705_upstream-findings-deep-research.md:160`); the general defect stated in writing (`:210`): "entry points are misclassified (USAGE_LITERAL instead of DESIGN_ATTRIBUTE…) and Step-3's dedup is lost (**two calcs reading one design attribute mint two JSON keys**)". |
| 2026-07-06 | PR #3 merged (`89e6f80`, "staged plant-idiom support"): `self_named_binding_trap` fixture authored as a *negative/diagnostic* case; `_rescue_self_named_bindings` built, covering **only** EXPOSE-backed upstream channels; the residue dispositioned in-code as "the genuine modeling error the `self_named_binding_trap` fixture pins" (`pipeline_builder.py:590-591`). The syside vendor note (self-named-binding recursion) recorded as **unfiled** (`NEXT_EPIC_PROMPT.md:116`) — never filed since. |
| 2026-07-07 | PR #5 PIPELINE-TRUTH: source-QN supplied-value collapse delivered — **LITERAL values, differently-named cross-part consumers only** (REQ-SVM-01/02/04). The self-named case never reaches it. |
| 2026-07-13→21 | CONSTRAINT-EXEC/LIFECYCLE (PR #9, `936315c`): resolver unification. The Item-2 design review catches that convergence "has no mechanism… mints a different QN per consumer, the opposite of convergence" (`shared-resolution/design-review.md:76-81`) — the process *worked* here — and SR-A02 is referred to Item 4, which delivers row 16 + the written-reference carry **for the calc+constraint, part-usage-owned, unbracketed shape only**, with the partial coverage conceded in docstrings (`dependency_backtracker.py:533-546`). |
| ~2026-07-22 | Demo pin `06d95f8` (Item-11 era): stellarator package generated; R/a/kappa fan out via Path A. |
| July 2026 | IFE acceptance study (2,301 rows) runs with the bug live. Swept fields feed only the constraint (which converges), so the 2294/2301 verdict agreement is genuine — but `recirc_calc`/`lcoe_calc` computed every row at the frozen design point. Masked by construction. |
| 2026-07-25 | fusion-tea research (`20260725-110828_study-failure-classes-and-mechanisms.md`) names the fan-out class **A6**, calls it "a sweep hazard nobody had named," prescribes a consumer-side contract fix ("kills A6 by construction"), files a *different* small upstream finding (unfenced `inspect`), and does not file this one. |
| 2026-08-02/03 | Owner pressure-tests the study-parameterization policy against real packages; the fan-out surfaces as a bug; Item 5 gated; this forensic ordered. |

## Where the behavior was specified (and not)

| Shape | Requirement | Behavior |
|---|---|---|
| Lenient terminal miss | REQ-IR-06 (`verification-matrix.md:335`) | Mint per-usage `{consumer_eqn}__{param}` — **the fan-out is the specified PASS behavior** |
| One attribute, calc + constraint, part-usage-owned, unbracketed | SR-A02 / REQ-IR-07 (`shared-resolution/spec.md:277`, matrix `:336`) | Converge on one field (delivered by lifecycle Item 4) |
| Supplied values, LITERAL, differently-named consumers | REQ-SVM-01/02/04 (matrix `:566-569`) | Collapse by source QN |
| Constraint actuals | REQ-CL-05 (matrix `:172`) | Deduped entry point |
| Self-named binding, outer EXPOSE resolves | REQ-VBR-10 (matrix `:586`) | Rescue to upstream *channel* (wiring, not a shared field) |
| **Two calc consumers, shared non-literal attribute, self-named** | **none — no REQ, no fixture, no backlog item** | Falls to REQ-IR-06 per-usage minting |

The only fixture with two calc siblings self-naming one attribute is the customer's own
model class. In-repo, `tests/runtime/test_fusion_tea_acceptance.py:40-44` **hardcodes** the
fanned key (`_GAIN_EP_KEY = "hif_plant_pkg__hif_plant__lcoe_calc__gain"`) with a comment
rationalizing the split ("gain is emitted per-consumer … distinct from recirc_calc's").
The same suite proves convergence for chain bindings two files over
(`test_fusion_tea_snapshot.py:48`) — the knowledge that convergence is the right outcome
sat next to the test that froze its absence.

## The spec ruling on `in R = R`

**[AGENT]** (sysml-expert spec reading, 2026-08-03; corroborated by observed SysIDE
behavior; optionally confirmable with a live `sysmlv2-validator` parse):

SysIDE's resolution is **spec-conformant**. Per SysML v2 Part 1 §7.5 (deferring to KerML
8.2.3.5 nearest-scope lexical resolution), the RHS `R` resolves outward from the binding
expression; the first scope containing a member named `R` is the calc usage itself (its own
input parameter), which **shadows** the plant attribute. `in R = R;` is therefore a
degenerate self-binding per spec, not "bind to the outer attribute." The spec-correct idiom
is `in R = stellaris::R;` (qualified name) or a feature chain. So the "genuine modeling
error" disposition was semantically defensible — no project record ever checked this, but
it happens to be right.

That makes the real defect sharper, not softer. The toolchain gives this one idiom
**three different semantics depending on which path consumes it**:

1. **Constraint actuals** reinterpret it as the outer attribute (exact-identity resolution
   → one converged source field). SR-A02's fix extends the same reinterpretation to the
   calc consumer for the part-usage-owned shape (`shared_producer` fixture).
2. **Calc bindings under an instance `:>>` override** (Path A) get the override value
   silently stamped in per-usage — an accidental *value-level* reinterpretation that
   produces correct numbers at the design point and wrong identity everywhere.
3. **Calc bindings without an override** (Path B) keep the spec-literal self-reference,
   miss everything, and mint per-usage fallback fields.

A degenerate-per-spec idiom that the pipeline *sometimes* deliberately reinterprets as the
intended meaning is a semantics the pipeline has adopted — partially. Having adopted it for
constraints and for SR-A02, silently doing something different on the calc path is the
inconsistency the customer observed. And at no point does any layer *reject or warn on* the
degenerate idiom itself: the 2026-07-05 research proposed a conventions/lint check in
agentic-mbse (register A-1) — not built — and the syside vendor note was never filed
(moot now: SysIDE is conformant; the note would have come back "works as specified").

The scoping pedantry does not soften the defect. A binding in the model is a binding
**[OWNER 2026-08-03]**: simulating a bound parameter as an independent input is not a
permissible reading under either ruling — "reject loudly" and "converge uniformly" both
eliminate the fan-out; only the silent status quo is indefensible.

## How it survived each defense layer

1. **Specs encoded the mechanism, never the mission.** The library's constitutive purpose
   — every consumed value backtracks to one source declaration — appears in prose
   everywhere (CLAUDE.md, epic names, PR titles) and as a checkable requirement nowhere.
   The matrix's only calc-path convergence row (REQ-IR-07) is discharged by the
   calc+constraint fixture. Reviews audit artifacts against written requirements, so every
   review honestly passed a surface that violated the library's reason to exist. The gap
   is not "nobody asked for it" — it is that the verification apparatus was never pointed
   at the property everyone knew was the point.
2. **Refactor reviews.** Both big PRs (#2, #9) defined success as *behavior preservation*
   ("zero regressions", "byte-identical to the pre-extraction inline code"). Review effort
   went into proving the old surface was reproduced exactly — which it was, fan-out
   included. A preservation gate cannot catch a defect that predates it; it can only
   embalm it.
3. **Baselines.** The fan-out is committed ground truth in `catf_mfe` (13×), `solar_battery`
   (8×), `ife_plant`, and fusion_tea baselines. Byte-identity gates then *defend* the
   defect against accidental fixes.
4. **Diagnostics.** Path A emits nothing: the LITERAL stamp logs a success count; the
   backtracker's LITERAL branch bypasses the resolver; producer-completeness exempts clean
   entry points (owner decision D-1); the phantom detector is not wired into the
   generation pipeline. The one tripwire that exists (lenient-miss warning, I7) covers
   only Path B — the path the customer did *not* hit.
5. **Partial fixes as coverage theater.** Three adjacent shapes each got a real convergence
   fix (SVM literals, SR-A02 calc+constraint, EXPOSE rescue). Each epic could honestly
   report "shared keys collapse" / "dedup returns" — and each report was scoped in a
   clause that excluded the plant idiom. Repeated narrow wins made the area *feel*
   covered.
6. **Disposition language.** The residue was labeled "modeling error" (trap docstring),
   "negative/diagnostic case" (Item 8), "known-incomplete, referred" (SR-A02 before Item
   4), and "vendor note" (unfiled). Every label made the remaining gap someone else's
   category — the modeler's, a later item's, the vendor's. No label was "bug in our entry
   surface," so nothing entered the backlog.
7. **Numerical masking.** Capture stamps one consistent value into every copy, so every
   single-point acceptance (handshake, headline, 41/41 composed proof) passed honestly.
   The one sweep that ran (July IFE study) happened to sweep only constraint-feeding
   converged fields — the fan-out sat inert in the cost modules of all 2,301 rows.
8. **Downstream normalization.** The 2026-07-25 taxonomy saw it plainly, named it A6, and
   engineered around it. The framing was "hazard class + consumer-side contract," not
   "upstream defect + file it." The last reader who could have escalated instead wrote a
   coping strategy.

## Code References

- `src/sysml_codegen/extraction/usage_extractor.py:831-842` — reference bindings store the
  referent's resolved QN (the self-reference enters here)
- `src/sysml_codegen/orchestration/pipeline_builder.py:285-379` — hierarchy override
  rewrite; `:344-345` leaf extraction, `:363-369` the Path-A LITERAL stamp
- `src/sysml_codegen/orchestration/pipeline_builder.py:574-631` — `_rescue_self_named_bindings`
  (mechanism D rescue, EXPOSE-backed only; "genuine modeling error" disposition at `:590-591`)
- `src/sysml_codegen/analysis/dependency_backtracker.py:445-463` — LITERAL branch: per-usage
  mint, resolver bypassed
- `src/sysml_codegen/resolution/producer_resolution.py:553-566` — `entry_point_qualified_name`
  per-usage mint ("byte-for-byte" preservation); `:416-449` row 16
- `src/sysml_codegen/resolution/graph_builder.py:534-579` — USAGE_LITERAL as catch-all else
- `tests/conformance/test_self_named_binding_trap.py:69` — pins self-resolution
- `tests/runtime/test_fusion_tea_acceptance.py:40-44` — hardcodes the fanned key as expected
- `tests/fixtures/baseline_outputs/catf_mfe/computation_graph.json` — 13× fan-out pinned
- `docs/architecture/verification-matrix.md:335,336,566-569,172,586` — the REQ landscape

## Feasibility Assessment (fix-scope facts only)

Per owner direction, this report does not advance mitigations. Fix-relevant facts the
record establishes: identity is lost at two sites (extraction's self-resolution at Step 0;
the Step-3.5 name-coincidence stamp), both before the resolver runs — so no resolver-table
change alone can fix Path A. The convergence machinery that would receive a corrected
reference (row 16 + written-reference carry, source-QN keying) already exists for adjacent
shapes. A fix is upstream-visible (entry-key sets change → baselines, params JSONs,
contracts churn), which the 2026-07-05 research already predicted ("flag the key-collapse
in release notes").

## Open Questions

1. **Did anything consume LCOE/cost outputs from the July IFE study rows?** (Carried from
   the 2026-08-03 handoff, still unowned.) If yes, those numbers are design-point values
   mislabeled as swept results.
2. **Which semantics does the owner ratify for `in R = R`?** The spec says degenerate
   self-binding; the pipeline already reinterprets it as "outer attribute" on two paths.
   Options are: adopt the reinterpretation uniformly (calc path converges like the
   constraint path), or reject the idiom loudly at extraction/validation and require
   `stellaris::R`. Both existing in-house model corpora and the customer models use the
   bare idiom pervasively, so this ruling sets the migration burden. [awaiting owner]
3. **Filing** — this defect plus the three queued upstream findings (producer-channel/
   aggregation scoping; `pm update-validation` corruption; `pm close-item` crash) await
   the owner's go-ahead post-forensics.
4. **Fix-first vs workaround for demo Item 5** — owner ruling, deliberately not argued here.
5. **Optional confirmation** — a live `sysmlv2-validator` parse of the exact demo fixture
   would nail the SysIDE binding target beyond the snapshot evidence; the spec ruling and
   the captured `raw_expression` already agree, so this is corroboration, not a gap.
