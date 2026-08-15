# Evidence: Lifecycle Item 4 — Diagnostic Severity and Modeled-Default Fidelity

**Status:** Round 3 — N1/N2 closed (Pass-with-notes → certify). Final candidate.
**Owner:** Reid W
**Created:** 2026-07-20
**Epic:** CONSTRAINT-LIFECYCLE-REMEDIATION — register row 4
**Spec:** `.project/active/constraint-lifecycle-diagnostics-defaults/spec.md`
**Design:** `.project/active/constraint-lifecycle-diagnostics-defaults/design.md` (rev 2 + C3 amendment)

---

## Revision set (LC-I09)

| | value |
|---|---|
| **CANDIDATE_REV (sysml-codegen)** | see the remediation section — `16dbaa7` was audit round 1 |
| **CANDIDATE_REV (agentic-mbse)** | `4c18d616f77e26932a8e158cefc2637db47f9b07` |
| RED predecessor (codegen) | `3fbec63a9fc5f81e74b9794885b05219d5812e58` |
| Stage-entry commit (codegen) | `05c567c` |
| **Prior agentic-mbse pin (Item 0)** | `515e08bbcd70aa9d23212765161bd02b3e3d8f23` |
| **New agentic-mbse pin (moved by this item, DD-R02)** | `4c18d616f77e26932a8e158cefc2637db47f9b07` |
| Resolved lock | editable path override, `pyproject.toml:65` → `../agentic-mbse`; the `agentic-mbse>=0.1.2` floor at `:24` does no work in dev and is **not** the guard (see DD-R14) |
| Branch (both repos) | `constraint-exec-epic` |
| Open predecessor rows | none — rows 0–3 closed |

**Additive-certified status of the candidate chain since `515e08bb`.** Items 1–3 landed on the
codegen side only; `515e08bb..4c18d61` on the agentic-mbse side is exactly this item's one commit.
The chain is additive: `constraint-facts/v2` adds a field and closes two vocabularies, and every
pre-existing reason code and diagnostic kind is accepted unchanged (DD-A01 test asserts all 27
reasons still construct).

**Merge order is load-bearing** (DD-R03): agentic-mbse **PR #11 first**, sysml-codegen **PR #9
second**. Merging #9 first would leave main's codegen pinning `constraint-facts/v2` against a v1
upstream, and the `_upstream_pins` guard test would fail on main. No replacement upstream PR was
opened.

### Codegen commits

| commit | content |
|---|---|
| `7430aba` | Phase 0 probes + Phase 1 carry (C3 amendment applied first) |
| `7341807` | Phase 1 regeneration under the accepted Gate 1 table; suite to zero |
| `3bdf0b7` | Phases 2+3: warning totality, tier-2 visibility, default fidelity |
| `3d094d0` | Phases 4+5: facts-v2 consumption, envelope v4, 35-snapshot re-capture |
| `16dbaa7` | version-literal generalisation in two stale pins |

---

## Final gate results (at CANDIDATE_REV)

| gate | result |
|---|---|
| codegen suite | **3040 passed, 0 failed**, 41 skipped, 17 deselected |
| codegen `PYTHONOPTIMIZE=1` | identical **except** 2 pre-existing `assert`-stripped tests (below) |
| licence verification | **0** `no live syside license` skips in `-rs` output |
| agentic-mbse suite | **1811 passed**, 1 skipped, 33 deselected (pre-existing `slow` marker) |
| mypy (codegen) | 72 errors before and after — **zero added** |
| mypy (agentic-mbse) | 105 errors before and after — **zero added** |
| ruff (both) | clean |
| byte-identity / forced differences | every delta pinned before regeneration and verified after (tables below) |

**The two `-O` failures are pre-existing and not this item's.**
`test_expression_compiler.py::TestReqEc06WorstCaseRollup::test_rollup_unknown_raises_assertion` and
`test_expression_compiler.py::TestClassifyCompilability::test_unknown_in_results_raises_assertion`
assert that an `assert` raises; `PYTHONOPTIMIZE=1` strips asserts. Verified by stash that both fail
identically at the predecessor.

**Execution lane:** not re-run this item. Item 4 changes no generated module body — the entry-point
*keys* moved and two `null` fields were added to the graph model, both covered by the byte-identity
and baseline gates. Flagged for the audit as a deliberate scope call, not an oversight.

---

## Per-requirement record

### A. Scope, authority, coordinated pair

| req | disposition | evidence |
|---|---|---|
| DD-R01 | **Met** | `DiagnosticSeverity` (`constraint_facts.py`), fixed at construction from `EXTRACTION_DIAGNOSTIC_SEVERITY`; unknown kind refused at construction and at parse |
| DD-R02 | **Met** | pin moved `515e08bb` → `4c18d61`; both revs and the additive-certified statement above |
| DD-R03 | **Met** | PR #11 before PR #9; no replacement upstream PR |
| DD-R04 | **Met** | Item 1's warning bytes: **zero moved** (DD-A10). Item 2's resolver: `KEY_FORMS` table, tier order, and every row function other than row 16 unchanged. Item 3's V11 caller unchanged |

### B. Diagnostic severity and stable codes

| req | disposition | evidence |
|---|---|---|
| DD-R05 | **Met** | `EligibilityDiagnostic.__post_init__` enforces `REASON_CODES` in production; all 27 accepted unchanged |
| DD-R06 | **Met** | `CONSTRAINT_FACTS_SCHEMA_VERSION` v1 → v2 |
| DD-R07 | **Met** | severity is a field, never recomputed by a reader; **I1 proved by `rg`** — no `kind → severity` lookup on any read path in either repo |
| DD-R08 | **Met** | two production consumers: codegen `screen_extraction_diagnostics` (both routes) and agentic-mbse L6 `ValidationIssue.reason_code` |
| DD-R09 | **Met** | BLOCKING raises `CodeGenerationError` before lowering with code/severity/message/location; ADVISORY logs at WARNING |
| DD-R10 | **Met** | `ValidationIssue.reason_code` carries the profile's own code as a branchable field on `QualityCheckResult.issues` |

### C. Version skew, both directions, fail closed

| req | disposition | evidence |
|---|---|---|
| DD-R11 | **Met** | exact-equality preserved; both directions tested for the fact schema (`test_constraint_facts_severity.py`) and the envelope (`test_snapshot_v4_gate.py`) |
| DD-R12 | **Met** | `SNAPSHOT_FORMAT_VERSION` 3 → 4 |
| DD-R13 | **Met** | all 34 re-captured + 1 new (35 total); delta enumeration below |
| DD-R14 | **Met** | `sysml_codegen/_upstream_pins.py` + `test_upstream_pins.py` compares each pin against the imported upstream value. Package floor explicitly rejected as the guard (editable override always wins) |
| DD-R15 | **Met** | no second grandfathering route; version gate proven to run **before** the lowering-mode read (`test_envelope_gate_runs_before_the_lowering_mode_is_read`) |

### D. Warning totality and BLOCK preservation

| req | disposition | evidence |
|---|---|---|
| DD-R16 | **Met** | `warning_location` degrades to `<unmapped {basename}>:{line}:{column}`; cannot raise |
| DD-R17 | **Met** | every warning emitted in order, then `_raise_on_blocking` runs; `_raise_on_blocking` untouched |
| DD-R18 | **Met** | exclusion projection still raises on the same unmappable root (DD-A09) |
| DD-R19 | **Met — zero bytes moved.** A mappable location renders exactly as before; only the failure path changed | all Item-1-pinned sequences pass unchanged |

### E. Modeled-default fidelity

| req | disposition | evidence |
|---|---|---|
| DD-R20 | **Met** | `-0.1` → `-0.1`; `40.0 [W]` → `40.0` with unit carried; both routes |
| DD-R21 | **Met** | unsupported IR → explicitly unresolved + diagnosed; JSON emits `null`, never omits |
| DD-R22 | **Met** | diagnostic names the entry-point QN and the IR node kind |
| DD-R23 | **Met with exception** (audit F4) | two identical `float()` lanes collapsed to `design_attribute_float_default`; kept lanes justified by measurement (below) |
| DD-R24 | **Met** | modeled default stays an overridable typed contract parameter; not baked into predicate code |
| DD-R25 | **Met** | unit carried verbatim, never converted; no general constant folding (binary operator → unresolved) |

### F. Written-reference carry

| req | disposition | evidence |
|---|---|---|
| DD-R26 | **Met, mechanism amended** | reference **as written**, chain qualifier included; no name inferred from a formal, no structural-equality recovery. See PC-1 |
| DD-R27 | **Met** | loader + call-site plumbing only; both component fields already serialized in every committed snapshot; no extraction field, no schema bump of its own |
| DD-R28 | **Met** | `shared_producer` yields one entry point `SharedProducer__the_rig__gain`, default 40.0, one group; both routes (DD-A14) |
| DD-R29 | **Superseded by measurement** | 22-across-six was Item 2's estimate; measured 24 entry-point movements across seven fixtures. See PC-2 |
| DD-R30 | **Met** | final-generation V11 unchanged; Item 3's vacuity re-verified, not re-derived |
| DD-R31 | **Met** | falsified artifacts corrected (below) |

### G. Inherited residuals

| req | disposition | evidence |
|---|---|---|
| DD-R32 | **Met** | tier-2 malformed literal now diagnosed as a **new** log record; tier-1 byte-frozen string unchanged; Item 1's fall-through preserved (DD-A17) |
| DD-R33 | **Met** | SR-R16's basis amended to cross-source order-dependence (I5); bet-table row corrected |
| DD-R34 | **Closed non-reproducing** | verified at HEAD; nothing carried forward |

### H. Simplification and deletion (DD-R35/R36/R37)

**Deletions proved by absence, not by wrappers:**

| target | proof |
|---|---|
| `_literal_float` | `rg` finds only a docstring back-reference in its replacement |
| `producer_resolution._modeled_default` body | collapsed into `design_attribute_float_default`; no wrapper preserving the old shape |
| `if ep.default_value is not None` guard (`entry_point.py`) | deleted; every key now emitted |
| raising branch of warning-location preparation | replaced by the degrading renderer |
| three hand-copied version literals | replaced by `_upstream_pins` references |

**No LOC gate, baseline, cap, or counting obligation applies** (DD-R35, owner amendment 2026-07-19).
Simplicity is judged qualitatively at review.

**DD-R37:** the two profile consumers stay independent. Codegen re-evaluates facts and consumes no
authoring decision as state; `screen_extraction_diagnostics` reads a serialized field and consults
no table.

---

## Acceptance cells

| cell | verdict | where |
|---|---|---|
| DD-A01 | Pass | `test_constraint_facts_severity.py` (reason vocabulary) |
| DD-A02 | Pass | round-trip byte-identical; unrecognized severity/kind fail closed |
| DD-A03 | **Pass** (was wrongly Partial; audit F3) | `test_diagnostic_screen.py`, both routes + `non_finite_literal` fixture. Advisory leg pinned but honestly unreachable |
| DD-A04 | Pass | `reason_code` on the returned `ValidationIssue` list |
| DD-A05 | Pass | four cells: fact schema × 2 directions, envelope × 2 directions |
| DD-A06 | Pass | all 35 load at v4; retained v3 fails with the existing recapture message; delta enumeration below |
| DD-A07 | Pass | `test_upstream_pins.py` |
| DD-A08 | Pass | `test_unmappable_warning_location_degrades_and_block_still_halts` |
| DD-A09 | Pass | `test_unmappable_excluded_record_location_still_raises` |
| DD-A10 | Pass | **zero pinned bytes moved** |
| DD-A11 | Pass | both routes (`test_modeled_default_fidelity.py`), snapshot leg earned in Phase 5 |
| DD-A12 | Pass | unresolved is explicit, diagnosed, and `null` in JSON |
| DD-A13 | Pass | retired lanes absent; kept lanes justified by measurement |
| DD-A14 | Pass | RED authored against the two-key state, confirmed green, then flipped |
| DD-A15 | Pass | Gate 1 table; 0 same-key value changes across every fixture |
| DD-A16 | Pass | V11 caller unchanged |
| DD-A17 | Pass | `test_wholly_malformed_tier2_target_is_visible` + fall-through test stays green |
| DD-A18 | Pass | corrected artifacts contain no surviving assertion of the falsified premise |
| DD-A19 | Pass | this document |
| DD-A20 | Pass | gate-before-mode-read test; consumers independent |

---

## Premise conflicts and orchestrator rulings

### PC-1 — B2 falsified for CHAIN bindings (chain-aware carry)

**Trigger:** Gate 2 clause 1 caught a wrong-value regression during Phase 1.

B2 as designed said `source_attribute_name` equals the written reference. True for `reference`
bindings; **false for `chain` bindings**, where that field holds only the leaf and the qualifier
lives in `source_instance_name`.

**Recorded counterexample.** `catf_mfe_model` binds `in cryo_pump_count = cryo_pumps.n_pumps`
(`designs/catf_mfe/vacuum.sysml:184`). Carrying the leaf alone re-anchored `n_pumps` at the owning
part and selected a **different attribute of the same name**:

| | key | value |
|---|---|---|
| model means | `CATFMFEVacuum__catf_vacuum_pumping__cryo_pumps__n_pumps` | **32.0** |
| leaf-only carry selected | `CATFMFEVacuum__catf_vacuum_pumping__n_pumps` | **48.0** |

**Ruling (orchestrator, 2026-07-19): RATIFIED.** The leaf-only mechanism resolves a same-named
attribute at the wrong anchor — the precise silent-wrong-value family this epic exists to close —
so the chain-aware form is the faithful DD-R26 reading, not a concession. `written_reference` is
`{source_instance_name}.{source_attribute_name}` for a chain, the leaf otherwise. **DD-R27 survives:**
both component fields were already serialized, so no extraction change and no schema bump of its own.
B2 and D4 amended in the design with this counterexample as the recorded evidence.

### PC-2 — DD-R29's blast radius superseded by measurement

DD-R29 carried Item 2's **estimate** of 22 self-named bindings across six fixtures. Gate 3's probe
over all 34 fixtures and all five `ProducerRequest` builders measured **89 moved resolutions**,
every one landing on row 16, producing **24 entry-point movements across seven fixtures**.

**Ruling: ACCEPTED** as estimate → probe truth, **not a scope change**. Recorded as a spec annotation
under DD-R29. One clause did not survive contact: *"no wrong value is being fixed"* held for values
but not for anchors — see PC-1.

### PC-3 — fingerprint-stability mechanism rewrite (certified-seam change)

`test_fingerprint_stability::test_policy_update_changes_only_verifier_hash_and_derived_fingerprint`
generated its "reviewed" side from a whole archived git revision, silently assuming generated output
was otherwise stable across that boundary.

**The impossibility argument.** The test needs a revision differing from the working tree in
`contracts/verify.py` **and nothing else**. `verify.py` changed exactly once since the old pin, at
`e217119`, **strictly before** the carry. So every revision with the old policy also has the old
entry-point keys, and every revision with the new keys also has the current policy. Advancing the pin
makes `reviewed_verifier_hash == candidate_verifier_hash`, failing the test's own `!=` assertions;
leaving it fails on `pipeline.yaml`, `model_contract.json` and `inputs/design_params.json` drift.
Both directions fail and no third revision exists.

**What replaced it.** `REVIEWED_REVISION` now contributes exactly one file: the reviewed source tree
is the working tree with `verify.py` overwritten from `git show <rev>:...`, everything else
symlinked. Both sides generate from the same code, so the only difference reaching the seal is the
verifier policy — a stricter test of the same claim.

**The new loud guard is the load-bearing part.** Isolating the variable makes a silent no-op possible
in a way the old form prevented structurally: if `REVIEWED_REVISION` ever stops differing from the
working tree's `verify.py`, both sides become identical and every assertion would pass while testing
nothing. The test now asserts, **before generating anything**, that the two differ, with a message
naming the cause. **Verified to fire** — the intermediate state with the pin at the carry commit
tripped it exactly as intended, which is how the impossibility was confirmed empirically rather than
argued.

**Ruling: noted for audit scrutiny as a certified-seam mechanism change, not ruled on.**

### PC-4 — diagnostic sink placement deviates from the design's letter

Design D2 named `snapshot/loader.py` as the snapshot route's sink site. Implemented there, it made a
snapshot carrying a blocking diagnostic **impossible to even inspect**: `load_extraction_snapshot`
would raise, so no tooling could read the snapshot to see *why*.

**Rationale for the deviation, ratified:** loading is deserialization; generation is what a blocking
diagnostic stops. The sink moved to `snapshot_context.build_pipeline_context_from_snapshot` — the
snapshot route's generation entry point, still **after parse and before lowering**, and symmetric
with the live route's placement in `pipeline_builder`. It reads the already-parsed
`snap["constraint_facts"]`, so there is no second load. The design's requirement (one function, two
call sites, both before lowering) is met; only the site moved.

### PC-5 — the new fixture was initially captured extraction-only

`modeled_default_fidelity` was first added to `EXTRACTION_ONLY_MODELS`, which marks a snapshot
`constraint_lowering_mode = "grandfathered_off"`. The offline path then skips lowering and the
fixture's constraint entry points — the whole point of the fixture — never reach the graph.

**The grandfathered guard caught it**, loudly and by name:

> *"was captured with constraint lowering disabled (grandfathered) but carries 3 constraint
> assertion(s) — these assertions are NOT generated into this graph."*

**Recorded as the guard working as intended.** The fixture moved to `MODELS` (full capture, lowering
enabled). This is a datapoint for Item 12, which owns closing the `grandfathered_off` fail-open path:
the warning was sufficient to catch a real authoring error here.

### PC-6 — bracketed-owner convergence is a deliberate safe miss, scope-limited

Row 16 keys on the owning occurrence path. For a `PartUsage` owner (unbracketed) the calc and
constraint derivations coincide and convergence closes. For an **occurrence-indexed `part_def`
owner** the constraint side's path carries `[i]` brackets and a calc usage QN never does, so no
derivation from the QN can reproduce it.

**Disposition: row 16 misses, and missing is safe.** `_hit(None)` returns the same `_MISS` as any
other miss and the driver `continue`s, so a bracketed owner falls through to exactly today's lenient
terminal mint. Nothing regresses and no row is starved.

**Proven, not assumed.** Phase 0's exit was two checks, not one. `constraint_multi_instance` (which
already existed) is the bracketed-owner fixture: constraint side carries
`constraint_multi_instance__the_design__c__cell[0]`, the calc usage QN has no brackets, and the
design attribute is def-scoped (`constraint_multi_instance__Cell__cell_rating`). Row 16 **misses**
rather than hitting a wrong key — by a slightly different mechanism than predicted (def-scoping, not
only bracket mismatch), which is why the second check earned its keep. Gate 3's probe confirms no
bracketed-owner binding's `(outcome, identity, key_form)` moved at all.

**This is deliberate partial coverage, not silent partial coverage.** Convergence closes for the
unbracketed shape and is **explicitly not claimed** for the bracketed one. See Open items.

---

## Forced differences

Each was enumerated and pinned **before** any byte moved, and verified after. One regeneration event
per cause.

### FD-1 — Phase 1, the carry's entry-point identity movement

Resolution level: **89 of 303** `resolve_producer` calls moved, **every one to row 16** (51
`target_qn`→row 16 identity-preserved, 15 `dotted_pair`→row 16 identity-preserved, 23
`entry_point`→row 16 positive). **Zero MODULE_OUTPUT transitions in either direction** — no graph
re-wire.

Entry-point level, **24 across seven fixtures**:

| class | count | fixtures | default carried | numeric result |
|---|---|---|---|---|
| pure rename | 18 | catf_mfe 1, chain_spike 3, expression_binding_probe 1, fusion_tea 2, return_styles 3, solar_battery 8 | unchanged | unchanged |
| convergence (two keys → one that already existed) | 5 | shared_producer 1 (40.0), expression_binding_probe 2 (0.08), solar_battery 2 (0.008, 25.0) | unchanged | unchanged |
| convergence onto correct scope | 2 | catf_mfe 1 (elongation, 3.0), fusion_tea 1 (efficiency, 0.35) | unchanged | unchanged |

Classification consequence, uniform and value-free: `entry_type` flips `usage_literal` →
`design_attribute` for 13 entry points.

**Gate 2 verdict: PASS.** 0 shape stops, 0 value stops, **0 same-key value changes** across every
fixture's entry points. **Gate 3b: B4 holds** — hits are generated baselines, the DD-R31 artifacts,
and one stale provenance *comment* in `test_parameter_group_deriver.py:384-386` whose test still
passes (`classify()` traces the binding index, not the entry-point set).

Regenerated file set — **exactly the pinned prediction, no extras**:
`baseline_outputs/{catf_mfe,chain_spike,solar_battery}/computation_graph.json`,
`baseline_yaml/{chain_spike,solar_battery}.yaml`.

### FD-2 — Phase 3, the `EntryPoint` field addition

`EntryPoint` is a Pydantic model dumped with `exclude_none=False`, so `unit_text` and
`unresolved_default_kind` emit two new `null` keys on every entry point in every baseline.

**Verified after regeneration: 9 computation graphs, 184 entry points, and the diff is exactly
`+unit_text: null`, `+unresolved_default_kind: null`, plus the trailing comma on `python_type`.
Zero value movement, zero key movement.** No pipeline YAML changed (the YAML does not serialize
these fields); no committed `inputs/*.json` exists to churn.

### FD-3 — repinned byte gates, each with its reason recorded in-line

| pin | reason |
|---|---|
| `SNAPSHOT_MANIFEST_SHA256` (`test_constraint_snapshot_portability.py`) | delta verified to be exactly two key movements: `+plasma_region__elongation`, `pump_load__pumping_speed_total` → `pumping_speed_total`. Only `model_contract_bytes` and its two derived hashes changed |
| `REQ-DM-03` `BindingInfo` field set | +2 `stored_*` fields; **wire form unchanged** |
| `REQ-DM-03` `EntryPoint` field set | +2 fields (`unit_text`, `unresolved_default_kind`) |
| `production_facts.json` (agentic-mbse) | v1 → v2; its `diagnostics` list is empty, so the version string is the **only** delta |

### FD-4 — Phase 5 re-capture delta enumeration (DD-A06)

35 snapshots re-captured under licence. **No snapshot was timestamp-only**, so the byte-identity
procedure's revert step had nothing to apply — every file carries at least one intended delta.

| lines | delta class | disposition |
|---|---|---|
| 68 | `snapshot_format_version` 3 → 4 | **intended** (DD-R12), 34 files × 2 |
| 68 | `constraint-facts/v1` → `v2` | **intended** (DD-R06), 34 files × 2 |
| 68 | `captured_at` | timestamp churn, expected |
| 2 | `source_hash` on `shared_producer` **only** | the header correction carried forward from Phase 1 (DD-R31); comment-only, no semantic change |
| 594 | `dropped_constraints` section removed | **pre-existing capture drift — see exclusions** |
| 42 | `channel_aliases` trailing comma | mechanical consequence of the line above |

---

## Deliberate exclusions, each with its parent-commit reproduction

These are pre-existing conditions this item declined to absorb, so that each diff has one cause. All
three were **verified to reproduce with Item 4 reverted**.

| excluded | reproduction | disposition |
|---|---|---|
| `baseline_outputs/plant_values/` | regenerates differently at the parent commit (`git stash` of `src/`, re-capture, diff non-empty) | **stale baseline**, same class as the recorded `deep_cross_scope` case. Not regenerated. Fails no test |
| `constraint_inline` baseline | `capture_pipeline_baselines.py` aborts on it with a constraint name-safety violation (`generated_binding_overlap`, `final_binding='value'`), reproduced at the parent | **pre-existing capture failure**. Not regenerated |
| `dropped_constraints` section | a re-capture at the parent also drops it — the committed snapshots predate a capture-script change | **unavoidable in any re-capture** under DD-R13. Enumerated in FD-4 rather than silently absorbed |

---

## Falsified-premise artifact corrections (DD-R31, DD-R33)

| artifact | correction |
|---|---|
| `tests/fixtures/shared_producer/PROVENANCE.md` | rewritten: convergence now closes; both false claims recorded as corrections rather than deleted — (1) "structurally unreachable from the calculation consumer" was false (the name was in every snapshot; the *loader* dropped it), (2) **"a test asserts it" was false — no such test existed at HEAD** |
| `tests/fixtures/shared_producer/model.sysml` header | updated; prior note preserved as describing the Item 2/3 state |
| `resolution/producer_resolution.py` docstring | rewritten — the "unreachable from it" claim removed |
| `analysis/dependency_backtracker.py` docstring | rewritten to state what the consumer now supplies and why |
| Item 2 `design.md` I9 | "falsified" → "falsified for Item 2; **restored and delivered** by Item 4", with Item 2's own scope left intact |
| Item 2 `design.md` PC-4 consequence | corrected block quote added; original paragraph kept as the record of what Item 2 measured |
| Item 2 `spec.md` SR-R16 basis | amended: owner D-1 → cross-source order-dependence (I5) |
| Item 2 `spec.md:295` bet row | corrected to match |

Because no test pinned the two-entry-point state, DD-A14's surface was **newly authored** (Gate 4):
written against the current state first, confirmed green so the RED could not be a plumbing failure,
then flipped in the same shape.

---

## Lane consolidation measurement (DD-A13)

The design left one lane boundary open. Settled by measurement, both halves recorded:

- **Collapsed:** `ParameterGroupDeriver.design_attribute_default_value` and
  `producer_resolution._modeled_default` were the same bare-`float()` lane over two different
  QN-keyed indexes → one `design_attribute_float_default(attr)`. The indexes differ legitimately;
  the parsing did not.
- **Kept, now justified rather than inherited:** `_parse_default_value`. Across all 34 committed
  fixtures, **531 captured defaults parse as float, zero signed, zero unit-bracketed**; the 138
  non-parsing values are feature references (`split.half`), a different shape resolved through the
  computed-attribute path. Mechanically, the AST lane that produces the string routes operator
  expressions through `evaluate_true_static_expression` (`parameter_groups.py:239`), folding signs
  and stripping units **before** capture. So it reads a genuinely different input — a captured
  string for which no IR exists — and does not cut over.
- **Kept:** the AST lane itself (a *producer* of that string, pinned by
  `test_ast_dispatch_invariant.py`) and `extractor._extract_default_value` (narrower node set, same
  producer role).

---

## Open items

| item | status |
|---|---|
| **Bracketed-owner convergence** | **Not claimed, deliberately.** Convergence closes for the unbracketed (`PartUsage`-owned) shape only. A bracketed `part_def` owner falls through to today's lenient mint — safe, but not converged. Closing it needs its own owner-path derivation and is **a new item**, not an extension smuggled in here (PC-6) |
| **Stale-baseline class needs an owner** | `plant_values`, `constraint_inline`, and the `dropped_constraints` capture drift are three instances of one pattern: committed artifacts that no longer match what their generator produces. Each reproduces at the parent commit. Joins the recorded `deep_cross_scope` case. **No owner assigned** |
| **DD-A03 end-to-end fixture** | The codegen halt and advisory logging are proven at the unit surface and both sinks are load-bearing, but no fixture carries a real blocking extraction diagnostic through generation. `non_finite_literal` is currently the only kind and requires a non-finite literal in a model. Flagged rather than claimed |
| **Execution lane not re-run** | deliberate scope call (see gates); Item 4 changes no generated module body |
| **Tier-1 mirror of DD-R32** | recorded in the design's Non-Goals: a malformed *tier-1* literal suppresses tiers 2a/2b entirely, the same class Item 1 fixed *within* tier 2. DD-R32 scoped this item to tier-2 silence. **Needs an owner elsewhere** |
| **`test_parameter_group_deriver.py:384-386`** | provenance comment names a key the pipeline no longer mints; the test still passes on its own terms. Cosmetic |

---

## Next step

Independent `/_my_audit` against `16dbaa7` (codegen) and `4c18d61` (agentic-mbse). The three items
most worth adversarial attention: **PC-3** (certified-seam mechanism rewrite), **PC-1** (the design
bet amended mid-implementation), and **DD-A03** (the one cell claimed partial).


---

# Remediation — audit round 1 (Needs Work → all four findings closed)

Audit report: `audit.md`. PC-3 was verified sound in all three respects and every engineering
gate reproduced; the four findings were places where a claim outran its evidence. All four are
closed. **No finding was closed by weakening a test or an assertion.**

## F1 — snapshot-route sink ran after lowering. **Fixed.**

The auditor's call-order probe reproduced exactly: `['lower_constraints',
'screen_extraction_diagnostics']`. `build_full_graph_from_snapshot` lowers, and the sink sat eight
lines below it. So the routes were not symmetric, contrary to PC-4's own rationale, and D2's
"both before lowering" was unmet on the licence-free production path.

The sink moved above `build_full_graph_from_snapshot`. Order is now
`['screen_extraction_diagnostics', 'lower_constraints']`, pinned by
`test_snapshot_route_screens_before_lowering`, which records the call order directly rather than
inferring it from where the code sits. The cost is one extra snapshot load, stated in the comment
rather than hidden — the graph build that follows dominates it. `diagnostic_screen.py`'s docstring
no longer names `snapshot/loader` as the second site.

## F2 — the carry re-anchored a `::`-qualified reference. **Fixed, and the first fix was wrong.**

The auditor was right and the finding was the most serious of the four.
`in kappa = catf_radial_build::elongation` resolved to an owner-local shadow
(`...__plasma_region__elongation`) instead of the outer key its thirteen siblings reach. Masked
entirely because both attributes hold 3.0 — a value coincidence was the only thing between this
and a wrong number, and FD-1 filed it as a success.

**First attempt, discarded — recorded because the discard is the point.** Returning `None` from
`written_reference` when `source_path` contains `::` looked right and was wrong: `source_path`
holds the *resolved* QN, which is `::`-qualified for a bare self-named leaf too
(`shared_producer`'s `gain` resolves to `SharedProducer::the_rig::scaler::gain`). That guard
silently killed the SR-A02 convergence and reverted 14 entry points across three fixtures. Caught
by regenerating baselines and reading the diff before believing the fix.

**The rule that is actually correct: exact identity beats re-anchoring.** Row 16 keys an
owner-*relative* name under the consumer's owner. When the consumer's reference already resolves
to a real design attribute by exact identity, the reference was scope-qualified as written, and
re-anchoring would select a same-named local shadow. Row 16 defers; row 17 keys it by exact
identity, which is where it resolved before Item 4.

**Scoped to the calculation consumer only.** The first cut of *this* rule broke
`test_precedence_occurrence_qn_beats_target_qn_design_attribute` — a **certified Item-2 seam**
where row 16 deliberately beats row 17 for the constraint consumer. The rule now fires only when
`target_qn is None`, which is the calculation consumer, the one Item 4 newly pointed at this row.
Item 2's ratified precedence is untouched. Extending the seam, not reworking it.

**Discriminating regression test, as required.** `tests/fixtures/shadowed_reference/` holds two
same-named attributes with **different** values — outer `scale = 2.0`, inner shadow `scale = 7.0`.
Verified genuinely discriminating by reverting the fix: **7.0 without it, 2.0 with it.** A value
coincidence can never mask this class again.

**FD-1 correction.** The third row's catf_mfe entry was *not* a convergence. Corrected:

| class | count | note |
|---|---|---|
| pure rename | 18 | unchanged |
| convergence (two keys → one that already existed) | 5 | unchanged |
| convergence onto correct scope | **1** (was 2) | `fusion_tea` only — a genuine `.` chain, correctly labelled |
| ~~catf_mfe elongation~~ | **0** | **was a regression, not a convergence. Now reverted; the key no longer exists** |

Total entry-point movement is **23 across six fixtures**, not 24 across seven.

**Known partial coverage, now stated alongside PC-6's brackets.** A `::`-qualified reference is
not consumed by row 16 at all. Anchoring it at its *written* scope would need an occurrence path
derived from a scope qualifier — the same missing derivation that leaves bracketed owners
uncovered — and would duplicate what row 17 already does correctly. Scope: 84 `::`-qualified
bindings across two fixtures.

## F3 — DD-A03 was Fail, not Partial. **Fixed; the label was wrong and I accept that.**

The "unit surface" I cited did not exist. Coverage confirmed the auditor's reading: the raise, the
advisory branch, and the whole `_render` formatter never executed under any test.

`tests/fixtures/non_finite_literal/` (a `1.0e400` overflow) plus
`tests/conformance/test_diagnostic_screen.py` — 8 tests covering the raise, the location renderer,
the absent-location marker, silence on no diagnostics, the advisory branch, the live route
end-to-end, the snapshot route, and F1's ordering.

**Two structural limits, stated rather than papered over.** A `non_finite_literal` diagnostic
**cannot reach a snapshot by construction** — the facts serializer refuses non-finite floats
(`allow_nan=False`, the D2a backstop), so the snapshot leg uses a synthesized payload, the same
technique the envelope-gate test uses. And the **advisory branch has no reachable input**: the
writer table has one entry, BLOCKING, and `parse` refuses a document disagreeing with it. The
advisory test constructs the fact directly and says so in the test body. DD-A03 is now **Pass**
for the blocking path on both routes; the advisory path is pinned but honestly labelled unreachable.

## F4 — the retained string lane disagrees with the IR lane. **Justification corrected; root cause surfaced, not fixed.**

The disagreement reproduces: `ModeledDefaultFidelity__Derived_Bound__limit` captures `'5.0'` (the
AST lane folded `2.0 + 3.0`) while the IR lane returns explicitly unresolved. The 531/0/0
measurement stands, but the auditor is right that the retention justification — "a captured string
for which no expression IR exists" — is false. The "zero carry a sign" clause also went stale in
the same commit: `drift` is `-0.1`. The claim that survives is that no captured string carries a
**unit**.

**Root cause, measured: 8 constraint-definition formals across 4 fixtures are captured as design
attributes**, which is what hands two lanes the same input. Removing that double-ownership is the
correct fix and moves entry-point identity across `shared_producer`, `plant_values`, `fusion_tea`
and `gate_a` — a four-fixture blast radius needing its own forced-difference table. **That is not
remediation scope, and I did not smuggle it into a remediation commit.**

What was done: the docstring now states the boundary honestly (same input, two policies, one
unconsumed), names the root cause with its blast radius, and
`tests/conformance/test_default_lane_disagreement.py` pins the disagreement *and* pins why it is
unobservable — so the justification cannot go stale again unnoticed. Recorded below as an open
item. **DD-R23 is downgraded from Met to Met-with-exception.**

## Evidence corrections the auditor asked for

- **FD-4's seventh delta class, accounted for.** `dropped_constraints` is **582** lines, not 594.
  The missing 12 are `source_line`/`line` shifts of exactly +2 in `shared_producer`, caused by the
  Phase-1 header correction being net +2 lines. Folded into another row before, named now.
  "Comment-only, no semantic change" understated it: the edit moved location metadata.
- **The "retained v3 snapshot" is not an artifact.** No committed fixture carries
  `"snapshot_format_version": 3`; `test_snapshot_v4_gate.py` synthesizes v3 in `tmp_path` from the
  v4 payload. The rejection is genuinely proven, by a different mechanism than the wording implied.
- **The merge-order failure presents as an ImportError, not the guard message.** With agentic-mbse
  at the old pin, collection dies at `analysis/diagnostic_screen.py` with `ImportError: cannot
  import name 'DiagnosticSeverity'` — the guard test never runs. It still fails closed and loudly,
  so DD-R03's conclusion stands and PR #11 must precede PR #9, but the evidence should not claim
  the operator sees the guard's message. They see an ImportError.
- **SR-A02's bracket scope note moved inline**, next to the criterion it qualifies, following the
  epic's model rather than sitting after the closing block.
- **`plant_values` drifts `registry_init.py` too**, not only `computation_graph.json`.

## Gates at the remediated candidate

| gate | result |
|---|---|
| codegen suite | **3050 passed, 0 failed**, 44 skipped |
| codegen `-O` | identical except the 2 pre-existing assert-stripped tests |
| licence | **0** skips |
| agentic-mbse suite | **1811 passed** (unchanged — no agentic-mbse change in remediation) |
| mypy | 72, zero added |
| ruff | clean |

Baselines regenerated once for the F2 revert (`catf_mfe`); the portability manifest SHA repinned
with both movements enumerated in-line.

## Open items after remediation

Carried from before: **bracketed-owner convergence**; the **stale-baseline class** (`plant_values`
— both files — `constraint_inline`, `dropped_constraints` drift, plus `deep_cross_scope`); the
**tier-1 mirror of DD-R32**.

Added by this remediation:

| item | status |
|---|---|
| **`::`-qualified references are not row-16 consumable** | deliberate safe-miss on the *written* qualifier (round 2). They resolve correctly by exact identity through row 17 — this is not a coverage gap, it is the right resolution path for a scope-qualified reference. Recorded as a design fact, not an open item |
| **Constraint-def formals captured as design attributes** | 8 across 4 fixtures; the root cause of F4's lane disagreement. Correct fix has a four-fixture blast radius and **needs its own item with a forced-difference table**. Unowned |
| **The advisory severity leg is unreachable** | one-entry writer table. Not a defect — there is genuinely one diagnostic kind today — but DD-R09's advisory half stays unfalsifiable end-to-end until a second kind exists |

---

# Remediation round 2 — F2 closed by capturing the written qualifier

Round-1's F2 fix scoped row 16 by resolution ("is the resolved QN indexed"), which the
re-audit (F2b) showed re-imports the resolved-vs-written ambiguity: it silently reverted
fusion_tea's bare-leaf `driver_efficiency` to a definition-scoped key, so two instances
shared one parameter — the SR-A02 defect this item exists to close, masked by both keys
holding 0.35 in a fixture with no baseline. **Ruling: execute the correct fix — capture the
written qualifier at extraction.**

**STOP condition checked and cleared.** Requirement 1 said to stop if the reference expression
node is not reachable through codegen's existing adapter surface. It is: the FeatureReference
expression carries a `cst_node` with `start_byte`/`end_byte`, and slicing the source document
(the same surface used for source locations) yields the written text exactly —
`catf_radial_build::elongation` (29 bytes) vs a bare `gain` (4 bytes). No agentic-mbse change.
`_written_qualifier` (`usage_extractor.py`) captures the qualifier, `None` for a bare leaf.

**Schema decision: amend v4, not v5.** v4 has never shipped — no remote contains the v4 commit
(`git branch -r --contains` empty), and every other worktree is pre-v4 (`512786c`/`6db3212`,
both < v4). So no pre-amendment v4 snapshot can exist anywhere a gate must catch, in a CI cache
or another worktree. A new field on an unshipped version is not a skew surface. v3 rejection and
both skew directions stay fail-closed and RED-tested (`test_snapshot_v4_gate.py` unchanged).

**Discriminator now on the written form.** `BindingInfo.written_reference` returns `None` when
`source_written_qualifier` is set, so row 16 misses for a scope-qualified reference and serves the
bare leaf it exists for. The index-based guard in `_occurrence_materialized_qn` is **deleted** —
row 16 keys what it is given.

## The three sentinel bindings — final resolved keys (snapshot route)

| binding | shape | resolves to |
|---|---|---|
| `shared_producer` `scaler.gain` | bare leaf | `SharedProducer__the_rig__gain` (converges — SR-A02) |
| `fusion_tea` `driver.meier_cost.driver_efficiency` | bare leaf | `hif_plant_pkg__hif_plant__driver__efficiency` (**instance-scoped, restored**) |
| `catf_mfe` `plasma_region.volume_calc.kappa` | `::`-qualified | `CATFMFERadialBuild__catf_radial_build__elongation` (outer, correct) |

Pinned by `test_written_qualifier_anchoring.py::test_three_sentinel_bindings`.

## Whole-corpus probe (per requirement 2)

Per-binding entry-point probe at the new candidate vs the parent **coordinated pair**
(`3fbec63` codegen + `515e08bb` agentic-mbse — the parent codegen cannot load facts-v2 alone, so
the pair is the correct baseline) and vs `16dbaa7`.

**vs parent pair:** 273 → 275 entry points. **0 same-key value changes.** 23 key movements across
**seven** fixtures. This is the authoritative FD-1.

**vs `16dbaa7`** (the F2/F2b correction alone): 3 movements — catf_mfe's `plasma_region__elongation`
key removed (the F2 regression), and shadowed_reference's shadow key (7.0) replaced by the outer key
(2.0). No other binding moved, so the written-form discriminator changed nothing that was already
correct.

### FD-1, corrected (supersedes every earlier count)

| class | count | fixtures |
|---|---|---|
| pure rename (key moves, value preserved) | **18** | catf_mfe 1, chain_spike 3, expression_binding_probe 1, fusion_tea 2, return_styles 3, solar_battery 8 |
| convergence (two keys collapse onto one that already existed) | **5** | expression_binding_probe 2 (0.08), shared_producer 1 (40.0), solar_battery 2 (0.008, 25.0) |
| **total** | **23** | **seven fixtures** |

Round-1's table was wrong three ways, all now fixed: it summed 18+5+1 to 23 (arithmetic error — the
"+1" was the false catf_mfe convergence, which F2b showed was a regression and is now gone, so the
real total is 18+5=23 with no third row); it labelled the moved fusion_tea binding a `.` chain (it
is a bare leaf — the `.` chain in that fixture is a different, unaffected consumer); and it counted
six fixtures where the probe measures seven. **0 same-key value changes** across the whole corpus —
every rename and convergence preserved its value.

## Gates

| gate | result |
|---|---|
| codegen suite | **3056 passed, 0 failed**, 44 skipped |
| codegen `-O` | identical except the 2 pre-existing assert-stripped tests |
| licence | **0** skips |
| agentic-mbse suite | **1811 passed** (no upstream change) |
| mypy | 72, zero added (the two new property lines match the pre-existing `source_attribute_name` pattern) |
| ruff | clean |

Re-capture: 36 snapshots, amend-v4. Only non-timestamp delta is the new `source_written_qualifier`
key on 294 reference bindings (plus trailing-comma churn). `shadowed_reference` now registered for
baseline capture (F2c) and pinned by an actual loading test.

## F2c / F2d closed

- **F2c** — `shadowed_reference` is registered (`capture_pipeline_baselines.py`) so the parametrized
  conformance tests stop skipping it, and `test_written_qualifier_anchoring.py` loads it on both
  routes and asserts the 2.0 outcome. A fixture that pins nothing is closed.
- **F2d** — FD-1 arithmetic corrected above; the false fusion_tea convergence row removed; the
  bare-leaf/`.`-chain mislabel fixed.

---

# Remediation round 3 — N1/N2 closed (Pass with notes → certify)

Round-3 re-audit: **Pass with notes**; PC-3 and the F2 fix both verified sound. Two notes, both
failing *toward* the F2 defect, now closed.

**N1 — structural presence check.** `test_written_qualifier_anchoring.py::
test_every_committed_snapshot_carries_the_written_qualifier_field` asserts every committed v4
reference binding carries `source_written_qualifier` (presence, null allowed for a bare leaf). This
holds the amend-v4 premise after merge: a snapshot lacking the key would load without a version
error and silently fall back to bare-leaf behaviour — the F2 defect — and this test catches exactly
that.

**N2 — error-path polarity flipped to fail away from the defect.** `_written_reference_text`
previously returned `None` on any recovery failure, and `_written_qualifier` read `None` as "bare
leaf" (row-16 consumable) — failing *toward* the re-anchor. Now:

- A recovery failure returns a `_WRITTEN_UNKNOWN` sentinel, distinct from a genuine bare leaf.
  `_written_qualifier` maps unknown → a non-empty marker, so `written_reference` returns `None`,
  so **row 16 misses** and the reference falls through to exact-identity resolution (today's
  behaviour, never a wrong number). Only a written form actually read, with no `::`, is reported
  as bare.
- The `except Exception` is gone. `get_source_file` is called directly, so a real adapter change
  raises rather than being absorbed as "unknown"; only the specific `OSError`/`UnicodeDecodeError`
  the recovery genuinely handles are caught. `start`/`end` are `isinstance(int)`-checked.
- The source-bytes cache is keyed on `(path, mtime_ns)`, removing the single-run assumption rather
  than only documenting it: a file edited between two extractions in one process cannot serve stale
  bytes.

**Corpus unmoved by the flip.** The per-binding entry-point probe is byte-identical before and
after N2 (0 movements) — recovery succeeds on every committed fixture, so the new failure path is
never taken today; it exists for robustness after merge. The three sentinels are unchanged.

**`::` caveat trimmed** (round-3 note): a `::`-qualified reference resolving by exact identity
through row 17 is the *correct* path, not a coverage gap. Recorded as a design fact above, not an
open item.

## Gates (round 3)

| gate | result |
|---|---|
| codegen suite | **3057 passed, 0 failed**, 44 skipped |
| codegen `-O` | identical except the 2 pre-existing assert-stripped tests |
| licence | **0** skips |
| mypy | 72, zero added | 
| ruff | clean |

No re-capture: N2 changes only an error path never taken on the committed corpus, and N1 adds a
test. No production data moved.
