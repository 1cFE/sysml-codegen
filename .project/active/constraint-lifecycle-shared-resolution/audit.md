# Audit: Lifecycle Item 2 — Shared Producer Resolution and Gate A

**Verdict:** Pass with notes
**Audited:** 2026-07-19
**Branch:** `constraint-exec-epic`
**Candidate:** `039d66e` (artifacts read at `dd97cdb`)
**Auditor:** independent session; no part of the implementing session's state reused

---

## Summary

The code is sound. Every behavioral gate reproduced independently at the candidate
coordinate: full suite, `-O`, the real-simkit execution lane, byte identity, the EP-key
manifest, and the Gate A RED→GREEN transition with a real verdict flip. The deletions are
real, the resolver is one authority, and the D2 safety claim — the one that would have been
serious if false — holds under an independent re-measurement.

The evidentiary record does not match the code in six places, and the cluster sits on the
item's headline residual. The recorded D2 falsification names the wrong table row, uses a
denominator that mixes two consumer populations, and — the substantive part — asserts a
conflict that the shipped table does not actually have. The shipped design is *better* than
the record claims: the alias-rung split reproduces both old ladders exactly, rather than
sacrificing one order for the other. Separately, one forced-difference entry is stated as
having no corpus population and it has 63 occurrences across 17 fixtures.

None of the findings changes a resolution outcome on the current corpus. All are correctable
in the artifacts and two docstrings, with no production change. That is why this is
pass-with-notes rather than needs-work.

---

## Gates reproduced

Environment: license via `set -a; source /home/reid/1cfe/agentic-mbse/.env; set +a`.

| Gate | Claimed | Reproduced | |
|---|---|---|---|
| Full suite | 3003 passed / 38 skipped / 0 failed | **3003 / 38 / 0**, exit 0 | ✅ |
| `-O` | 3001 passed, 2 pre-existing failures | **3001 passed, 2 failed** — both `test_expression_compiler` bare-`assert` nodes | ✅ |
| Real-simkit execution lane | 17 passed | **17 passed** (Item 1 evidence §3 invocation) | ✅ |
| Byte identity — baseline churn | every pre-existing fixture byte-identical | **zero** changes under `tests/fixtures/baseline_outputs/` across `287afc4..039d66e`; only the four new fixture dirs appear | ✅ |
| EP-key manifest | 34 fixtures / 273 EPs / 484 module inputs / 0 diffs | **34 / 273 / 484 / 0**, reconstructed from scratch | ✅ |
| Item 1 acceptance file | untouched | SHA-256 `aea7c82…4b` **matches exactly** | ✅ |
| D2 "none hits two" | 0 dual-conflicting-row bindings | **0**, under every reading tested | ✅ |

**EP manifest soundness.** No tool for this exists in the repo, so it was rebuilt against
`build_pipeline_context_from_snapshot` (`orchestration/snapshot_context.py:24`, the same
function `cli/__init__.py:949` calls). Three controls were run before trusting the zero:
the old-code override was confirmed by printing `sysml_codegen.__file__`; the two trees were
confirmed to differ on the exercised path (`input_resolver.py` present before, absent after;
`graph_builder.py` differs by 131 lines); and a deliberately mutated manifest produced
exactly one detected diff, proving the harness is not comparing empty structures.

**Test count delta, fully accounted.** The evidence's "3037 → 3003" does not reconcile
against either coordinate (F6 below). The real RED→candidate accounting, by per-file
collection at both commits:

| File | Δ |
|---|---|
| `test_input_resolver.py` (deleted) | −29 |
| `test_dual_resolution.py` (six parity classes retired) | −14 |
| `test_dead_code_removal.py` | −2 |
| `test_producer_resolution_table.py` (new) | +11 |
| `test_agg_key_forms.py` (new) | +9 |
| `test_producer_qn_rule.py` (new) | +9 |
| `test_gate_a_owner_classification.py` (new) | +4 |
| `test_agg_localterm_default.py` (new) | +3 |
| three golden suites × 4 new fixtures | +12 |
| **net collected** | **+3** (3038 → 3041) |

Passed moves 3012 → 3003 (−9); skipped moves 26 → 38 (+12), all twelve being the new
fixtures joining parametrized golden sweeps that legitimately skip. Nothing was silently
dropped. Every retired test is named and its replacement identified.

---

## Findings

### F1 — The recorded D2 residual does not describe the shipped table (evidence, design, docstring)

`producer_resolution.py:22-28`, `evidence.md:171-179`.

Three separate inaccuracies, in increasing order of importance:

1. **Wrong row.** The docstring calls row 5 "the bare alias form." Row 5 is
   `alias_deindexed` (`producer_resolution.py:434`); the bare alias form is **row 10,
   `alias_bare`** (`:439`). The distinction is load-bearing: rows {6,8} against {10} yields
   the stated 44 hits, while rows {6,8} against {5} yields 3. Rows 4, 5, 7 and 9 take zero
   hits from any consumer anywhere in the corpus, so the conflict *as literally written* is
   vacuous rather than latent.
2. **Mixed denominator.** "44 of 249 calculation bindings" — 249 is all resolver requests at
   the cutover commit: 235 calculation + 14 constraint. The 44 numerator is calculation-only.
3. **The conflict does not exist as stated.** Both deleted ladders reconstructed from
   `273ca57` are order-consistent *subsequences* of the unified table — calculation ran
   1→3→6→8→10, constraint ran 1→2→4→5→6→7→8→9→16→17→18. Neither reorders relative to the
   other. Splitting what each old ladder treated as one "alias rung" (prefixed/deindexed at
   4-5 before structured; bare at 10 after) reproduces **both** exactly. The table did not
   "take the constraint order" at the calculation order's expense; it satisfies both.

   The one genuine order inversion in the corpus is in the third ladder, which the record
   never mentions: at `273ca57`, `graph_builder.py:740-742` tried `alias_lookup` before
   `scoped_lookup`, the opposite of the table's scoped-before-alias precedence. Also
   unexercised — of 54 aggregation requests, 14 hit row 1 and 36 hit row 4, zero hit both.

**Why this is a note and not a blocker.** The safety property is intact and stronger than
claimed: no binding hits two conflicting rows under any reading, so no resolution outcome
can turn on the chosen order. Byte identity and the EP manifest independently confirm it.
The defect is that the item's headline residual is recorded against rows that don't conflict,
which would mislead the next agent who reasons about widening the table.

**What should change:** correct the docstring's row number and denominator; restate the
residual as the aggregation alias-before-scoped inversion, or withdraw it. No code change.

### F2 — "Each with no corpus population" is false for forced difference 2

`evidence.md:183-192`.

The five forced differences are introduced with "Each with no corpus population, so no
pre-existing generated byte moved." Driving all 34 committed snapshots through the graph
build emits **63 new lenient-miss WARNINGs across 17 of the 34 fixtures** — half the corpus.

The *conclusion* survives: warnings are not generated bytes, and zero baselines moved. But
the premise as written is wrong, and it understates a real change to the build log's
diagnostic surface. This was the brief's explicit falsification target, and it falsifies.

**What should change:** split the claim — four entries have no corpus population; entry 2
has broad population and moves no generated byte. State the 63/17 numbers.

### F3 — Design key-form table and shipped table disagree on numbering and one row's order

`design.md:415-450` versus `producer_resolution.py:429-452`.

The ratified design declares 20 rows; the code ships 21. Beyond the resulting off-by-one
across tier 2, one row genuinely moved: `chain_redefinition_follow` is design row **14**
(after both leaf-recombined forms) and code row **13** (before them). All three are
lenient-only tier-1 forms, so a reference both a chain redefinition and a leaf recombination
could reach now resolves differently than the design declares.

SR-R11 exists precisely so the order is declared in one place and drift is detectable. Two
tables that disagree defeat that. The design's own row split (5 → 5 and 10) is the correct
change per F1, but it was never recorded.

Follow-on: `producer_resolution.py:97` and `dependency_backtracker.py:570` cite "row 15" for
the occurrence-materialized form, which is row 16 in the shipped table. Those two docstrings
carry the PC-4 / SR-A02 argument, so the wrong number sits on the item's most-referenced
deferral.

**What should change:** regenerate the design's table from `KEY_FORMS`, record the split and
the chain-follow move as design deviations, and fix the two row-15 citations.

### F4 — `_resolve_binding_via_registry` survives, named for deletion, absent from the proof table

`dependency_backtracker.py:556`; `evidence.md:109`.

SR-R41 item 1 names four methods for deletion. The absence table lists three at zero and
silently omits the fourth, which survives at three occurrences.

Substantively this is fine — the method is now a nine-line request builder that owns no
ordering, no key construction, and no terminal behavior, which is exactly the consumer shape
SR-R10 requires. But SR-R41 says a retained path "is recorded as a deviation with that
reason, not silently kept," and no such deviation exists. An omission from a proof table
reads as a zero.

**What should change:** add the row with its surviving-consumer reason, as SR-R42 already
does for `_get_parent_part_for_usage` and `_consumer_scope_dotted`.

### F5 — `test_baselines.py` is not the byte-identity gate

`evidence.md:136`; `tests/conformance/test_baselines.py:1-40`.

The evidence lists "Byte-identity gate (`test_baselines.py`) — 17 passed." That file
regenerates nothing. It checks that four committed baseline JSONs round-trip through
Pydantic and that the registry `__init__.py` parses — it completes in 0.06s. The real
regenerate-and-compare gates are `test_factory_purity.py` and `test_gen_pipeline_yaml.py`,
both green in the full suite.

The byte-identity property does hold — I verified it independently through zero baseline
churn across `287afc4..039d66e` and the EP manifest. Only the citation is wrong, and it
matters because a future agent trusting this line would think a 0.06s well-formedness check
is protecting generated bytes.

### F6 — The retirement replacement pin covers one key form of twenty-one

`tests/conformance/test_dual_resolution.py`, `TestOneResolutionAuthority`.

The six retired classes are genuinely parity-shaped — each calls `resolve_input` alongside
the backtracker and compares — so retiring the comparison is correct, and the deleted
classes' one non-parity assertion (every aggregation `MODULE_OUTPUT` channel is in
`canonical_channels`) is now structurally guaranteed by `_direct_channel`'s membership check
at `producer_resolution.py:277`. The retirement itself is defensible.

What the replacement loses is corpus reach. The retired sweeps drove real fixtures
(`solar_battery_model`, `issue22_model`, `alias_agg_probe`, plus Item 1's landed fixtures);
`test_two_consumers_of_one_reference_agree` drives one synthetic registry with one
reference and asserts all three consumers land on `scoped_prefixed` — row 1 of 21. It cannot
detect a consumer divergence introduced at any other row.

**What should change:** parametrize the pin across key forms, or drive it over a committed
fixture's references. Low cost, restores the property to the corpus.

Also under this heading: the evidence's "3037 → 3003" reconciles against neither coordinate.
Measured: 3012 passed at RED (`287afc4`), 3039 at the cutover commit (`46a9b15`), 3003 at the
candidate. The full accounting above is what should replace it.

### F7 — Case-insensitive leaf matching survives a requirement that names it

`graph_builder.py:1250`.

SR-R12 reads "No rung resolves by leaf name, case-insensitive name, suffix match, or
arbitrary first-pick." `_find_literal_redefinition`'s Strategy 2 still matches with
`sanitize_name(redef_part_name).lower() == part_usage.lower()`.

The normative content of SR-R12 is satisfied — the collision arm now refuses
(`:1262-1271`), which is the "arbitrary first-pick" the requirement targets — and the
evidence declares the survival plainly under SR-R17 with its reason (no exact form covers
its population). This is graded met, not a gap. Flagging it because SR-R17's spec text says
the leaf tier "does not survive," so the requirement text and the shipped code disagree even
though the shipped behavior is the right call.

Minor, same function: the docstring at `:1226` documents a `producer_ctx` parameter that is
not in the signature (SR-R44 asks for clean docstrings).

### F8 — The design's Implementation Notes stop at phase group 1

`design.md:703-788`; `evidence.md:19-20`.

The evidence says "Read the design's Implementation Notes for the phase-by-phase record."
Those notes cover Phase 0, 1, and 2 only — the Gate A owner-classification work. Phases 3,
4, 5, 5b and 6, which performed the entire ladder cutover and every deletion this item is
named for, have no implementation record. The evidence's per-requirement table partly
compensates, but the pointer is inaccurate and the phase-level record of the largest change
in the item does not exist.

---

## Spec conformance

**Success criteria — all four verified met.**

- [x] One production resolver; three consumer ladders gone. `producer_resolution.py` is the
      sole positive path; `input_resolver.py` deleted from the tree; `resolve_input`,
      `AGG_STRATEGIES`, `ResolutionStrategy` and all four strategy classes at zero
      occurrences in `src/`.
- [x] Usage-owned literal on a concrete `PartUsage`, self-named actual, no passthrough,
      public live route. Verified end to end: `GateA__the_host__gain` reaches generated
      inputs at 40.0, real simkit returns `satisfied`, override to 5.0 flips to `violated`.
- [x] No verdict from a guessed binding while V11 is clean. All four named guessing
      behaviors gone; every surviving name-based form is unique-or-refuse and lenient-only,
      unreachable from the strict consumer via `_admissible` (`:508-509`).
- [x] Superseded mechanisms deleted, not shimmed. No wrapper, flag, alias, or re-export
      found. Subject to F4's unrecorded retention.

**Tagged requirements.** SR-R01–R05, R10–R17, R20–R22, R30–R34, R40–R44, R50–R52 verified
as recorded, with F4 (R41), F7 (R12/R17), F3 (R11) and F5 (R34 citation) noted above.
SR-R23 is correctly recorded **not met** and referred to Item 4.

**SR-A02 / SR-R23 referral honesty — verified consistent** across spec (`:274`), evidence
(`:61`, `:88`), design (`:137`, `:516`, I9 annotated falsified), epic commit `c685a0a`, and
`tests/fixtures/shared_producer/PROVENANCE.md`. The PROVENANCE file is the strongest artifact
in the set: it pins the exact two-entry-point state, gives the structural reason the
calculation consumer cannot supply the reference, and records the rejected name-inference
workaround as a decision record rather than a prohibition addressed to future agents.

**Non-goals respected.** V11 scope unchanged — `_fallback_entry_points.add` appears exactly
once in `src/` (`dependency_backtracker.py:603`), calculation-only, with the widening
explicitly left to Item 3. `param_group` on LocalTerm mints left `None` by ruling. Item 1
seams extended, not reworked.

---

## Design conformance

Implementation follows the design, with F3's table divergence the one deviation.

The Gate A fix is exactly the extension the design review confirmed: one added branch inside
the `package` arm (`constraint_lowering.py:714-722`), three existing branches untouched. It
raises rather than falling through on an unrecognized owner kind
(`_concrete_usage_owner:391-395`), and `_expand_part_usage_owner` raises rather than
defaulting when the owner has no qualified name (`:403-406`). Both are the right failure
posture for a routing decision whose silent wrong answer is the defect being fixed.

D6's scope climb is placed as declared — after tier-1 rows, before tier 2, collect-then-
require-unique, gated to 3+-segment references (`:482-505`). D4's guard placement is
uniform and a rejection continues the table (`:544-546`).

---

## Code integrity

No slop or failure-honesty findings. This is unusually clean for a change this size.

Specifically checked and clean: no `try/except Exception` returning a default in the
resolver; no optional parameter papering over missing data; no backwards-compatibility shim;
no god function — every key form is a single-purpose function with a two-line body and a
uniform `(identity, tied_candidates)` contract; policy lives at the terminal fork rather
than inside the utilities. `_terminal_miss` (`:577-602`) raises for strict and mints for
lenient with nothing shared but the request, which is the whole SR-R14 claim made structural.

One observation, not a finding: `resolve_producer` keeps only the first tie encountered
(`ties = ties or tied`, `:541`, `:565`), so a strict error can name tied candidates from an
earlier row than the one that ultimately mattered. Diagnostic quality only, and diagnostics
are Item 4's.

---

## Certification

**Verified and marked:** the four spec success criteria; every gate in the validation
battery, each re-run rather than read; the deletion absences; the Gate A RED→GREEN
transition at `287afc4` with the predicted terminal raise
(`GateA__the_host__viability.gain: unresolved actual 'gain'`) and the package-owner control
passing on both sides; the D2 safety claim; the full test-count delta; Item 1's acceptance
file SHA.

**Not checked:**

- **Live-extraction parity.** Both the EP manifest and the D2 re-measurement run the
  snapshot route only. An aggregation-cutover divergence on a path snapshots do not reach
  would be invisible to both. This is the same limit the implementer's controls have.
- **Relocated whole-tree replay.** Correctly out of scope (SR-R08, Item 5). Only
  same-checkout replay exists and it is labeled non-certifying.
- **`mypy`/`ruff` counts.** Not re-run; the evidence's 72-vs-76 and 165-vs-171 figures are
  taken on trust. Neither is a project gate.
- **The 22 rejected name-inference bindings.** The PROVENANCE file's measurement of the
  rejected alternative (22 single-consumer bindings across six fixtures) was not
  independently reproduced.
- **Input ordering within modules.** The EP manifest reconstruction sorts module-input
  triples, so a pure reordering of inputs within a module would pass it.
- **Item 4 / Item 3 boundaries.** Whether the deferrals are correctly placed is those items'
  audits, not this one.

**Recommended before close:** F1, F2, F3, F4, F5 and F8 are artifact and docstring
corrections with no production change. F6's pin widening and F7's docstring fix are small
code changes. None blocks the epic's next item.
