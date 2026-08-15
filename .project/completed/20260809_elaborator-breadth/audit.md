# Audit: Elaborator Breadth — Exact-Identity Item 5 (Phase-5 Owner Checkpoint)

> **Remediation note — 2026-08-09:** This verdict describes the pre-remediation checkpoint. The
> owner subsequently ratified the decisions recorded in `plan.md`, and the implementation now has
> a green executable 29-cell matrix and a 37-row ledger with no `needs-review` or `new-bug` rows.
> `product-lens.md` records how the findings were addressed. This note does not replace an
> independent `$my-audit`; rerun that stage before certification.

**Verdict:** Needs Work — Phases 1–4 verified complete; Phase 5 honestly incomplete at its owner
checkpoint, and the product-lens gate is BLOCKED (standing audit-F2 plus new audit-F11, F12, F15,
F16)
**Audited:** 2026-08-09
**Branch:** source-identity-epic (coordinated with agentic-mbse `elaborate-first-salvage` @ 65a35d7)
**Commit:** 6bed968 + uncommitted working tree (the audited state)
**Scope:** the whole item at the Phase-5 checkpoint. Phases 1–2 were verified in the prior pass
(`audit-20260808-phases12.md`); this pass re-used that record and independently verified Phases 3–5.
**Prior audits:** `audit-20260808-phases12.md` (Phases 1–2, partial certify),
`audit-20260808-rendered-path.md` (superseded rendered-path implementation).

---

## The Point

SysIDE has already resolved which declaration each semantic reference denotes. Codegen must
preserve that exact declaration identity, interpret it in one exact concrete occurrence, and store
the resulting node or output-port edge — never reduce the referent to a name and later guess which
same-named object was intended. One semantic source occurrence becomes exactly one runtime source
across calculation, constraint, FORMULA, alias, and aggregation consumers; unsupported or unstable
identity produces a named blocking outcome; strings enter only after semantic identity is settled.
Item 5 builds and proves that complete new front end while the legacy front end remains the
unchanged shipped authority; acceptance is a public off-default mutation, never internal-structure
fidelity.

## Summary

The engineering under this item is real and holds up under adversarial reproduction: every recorded
gate reproduced exactly, the corpus ledger's 37 rows reproduce from a fresh dual run, and the
Phase-5 public-mutation proof is exactly the observation the epic demanded. The item is still not
done, and the checkpoint's own framing needs correction before the owner rules on it: the
product lens found that the headline "symbolic multiplicity" conflict is a fixable literal-token
defect in the new walker, not a contract conflict, and that nine of the ten "public" matrix cells
are certified against internal graph structure rather than generated output. Needs Work, with the
owner checkpoint proceeding on corrected framing.

## Product Judgment

**Is this the right piece of work?** The route architecture is — exact identity before breadth,
breadth before projection, projection before the corpus grind, legacy frozen throughout. What is
not right yet is the evidence tier and the checkpoint framing, and both matter more than any
individual defect because the owner is about to make contract decisions on them.

Ledger gate: **BLOCKED**. Scanning every block: audit-F1 and audit-F3 are RESOLVED by citation
(2026-08-08 Phase-5 public-mutation block — I verified the cited test does what the resolution
claims). audit-F2 remains BLOCKED. The new 2026-08-09 lens run adds four BLOCKs:

- **audit-F11 (owner/HARD):** the walker blocks `[count]` populations as "non-finite" when the
  bound is a modeled finite integer (`occurrence.py:270-273` requires a `LiteralInteger` token;
  d38_caret's `count = 4` and solar's `module_count default := 20` are both finite). I reproduced
  the fixture facts and the code check myself. This re-anchors audit-F2: its falsifier is
  unobservable because of this defect, not because the contract's C17/C26 are wrong. **The
  diff-ledger's owner decision 1 should not be presented as written** — it invites the owner to
  amend owner-graded cells to accommodate a fixable walker check. Surfaced per capture-fidelity §4;
  the owner still rules (a prior surfaced question on d38_caret's parametric form exists in
  CURRENT_WORK), but with the corrected framing that the population is finite and computable.
- **audit-F12 (owner/HARD):** nine "public"-state matrix cells cite tests asserting internal
  `InstanceGraph` structure (I confirmed C25's cited test reads `mixed.calcs`/`node_ref`). Only C11
  reaches generated output. Contract invariant 57 makes that insufficient evidence.
- **audit-F15 (owner/HARD):** projection emits definition-level template declarations as runtime
  modules (`unresolvable_attr_probe`: 10 exact modules vs 1 legacy).
- **audit-F16 (owner/HARD):** a supported referent-table form fails closed
  (`deep_cross_scope_probe` → `SI_OCCURRENCE_MISSING`; the fixture is the contract's own normative
  witness for two supported rows).

Smells that fired, escalated here and not resolved: smell 3 (a category — "non-finite" — exempts
`[count]` whose user-visible meaning equals `[4]`; audit-F11), smell 4 (matrix acceptance depends
on internal representation; audit-F12), smell 6 (matrix green by selecting the internal route and
source-text presence over executed outcome; audit-F12/F13). Unresolved owner/HARD contradictions
and fired smells forbid Certify regardless of the rubric below.

The lens also recorded what holds, and I verified it independently: the SRC-01 fail-closed posture
(27/37 corpus errors) is the ratified contract behavior, not over-reach — the over-blocking is
isolated to F11/F16/F17 — and the public-mutation test pair is the evidence model the remaining
cells should copy.

## Findings

### Plan completion

**Phases 1–2 — complete** (verified in `audit-20260808-phases12.md`; not re-litigated). The
Phase-3 obligations that audit carried forward are now discharged, verified in code this pass:

- audit-F4: `SI_OCCURRENCE_AMBIGUOUS` is live at nine emit sites (`elaborate.py:914,923,928,986,
  1004,1011,1040,1045,1099`) and pinned by
  `test_elaboration_fail_closed.py::test_non_unique_definition_reference_has_named_ambiguity`.
- audit-F5: complete per-fixture lenient multisets are asserted — fusion_tea's exact
  `Counter({SI_SELF_BINDING: 15, SI_OCCURRENCE_MISSING: 7})` with the `{scope: 6, wall_type: 1}`
  breakdown (`test_elaboration_fail_closed.py:86-103`), plus five sibling multiset assertions.
- audit-F6: one `ElaborationCode` vocabulary in `diagnostics.py`; every previously-dead code is
  emitted with its name; no bare `ValueError("SI_...")` remains. (Residue noted under Code
  integrity.)
- audit-F8: the model-wide global-uniqueness fallback is gone — `_resolve_leaf`
  (`elaborate.py:1071-1108`) searches only consumer lineage and lineage-anchored descendants, and
  non-unique resolution raises the named ambiguity code.
- audit-F9: the import guard now reads `display.py` and asserts it is the sanctioned sanitize
  boundary (`test_elaboration_import_boundaries.py:29-34`).

**Phase 3 — verified complete.** Fail-closed and collision suites exist and pass (10 tests this
run); strict/lenient differ only in halt-versus-report; `sum` plurality keys from the pinned
SysIDE declaration UUID (`elaborate.py:109,1298`), not a name string.

**Phase 4 — verified complete, one letter-level deviation.** Projection, generation-boundary, and
round-trip suites pass (9 tests this run); `project.py` refuses unprojectable graphs
(`graph.py:258-262`) and raises `SI_RENDERING_COLLISION` on name collisions; the
`instance-graph/v1` codec imports no model-loading or resolution machinery and is imported nowhere
in shipped code (only the two conformance tests). Deviation: the "constraint catalog seam"
checkbox named `analysis/constraint_lowering.py` / `generation/constraint_catalog.py`, but neither
changed — projection assembles the catalog itself in `project.py:873-950`, reusing the existing
`mint_constraint_id`. This satisfies the intent (graph-driven assembly, no rerun of actual
resolution, legacy untouched) with less code; recording it here as the deviation note the plan
lacks.

**Phase 5 — incomplete, and honestly so.** The checked boxes are genuine: the internal route is
complete/deterministic and provably not a shipped flag (`test_elaboration_dual_run.py`); the diff
harness compares complete public graphs; the corpus runner and ledger reproduce (I re-ran the
37-fixture dual run: exact 10 graphs / 27 typed errors, legacy 36 / 1, only `sample_model`
byte-equal — every ledger total matches); the public mutations prove the one-source fan-out on
live and rebuilt routes down to generated JSON. The unchecked boxes (matrix green, ledger gate,
owner checkpoint) are correctly unchecked. Two recording notes: (1) the plan's own admission
stands — the internal route implementation preceded its kept test, so Phase 5 does not satisfy the
red-first rule; (2) the recorded "focused selection passes 33 tests" does not match the natural
Phase-5 file selection, which collects 38 (26 passed + 12 xfailed) — the plan does not record the
exact command, so the count is unauditable as written.

### Spec conformance

- **R1 (one elaboration pass) — met on the new route** for supported forms; no post-graph
  re-resolution exists (verified via projection/codec import surfaces).
- **R2 (identity by construction) — met where projection is reachable.** The public mutation
  proves one input per source and exact fan-out. Breadth is limited by the blocked cells
  (audit-F11/F16/F17 shrink the reachable set).
- **R3 (self-binding fails) — met.** Exact element-ID comparison
  (`source_evidence.py:130-141`), corpus-wide blocking behavior per contract.
- **R4 (distinct occurrences) — met** by construction; pinned by the shadowing/equal-valued
  suites. C7/C23's own cells still lack fixtures (audit-F14).
- **R5 (projection on the verified seam) — met structurally**: modules of all five kinds,
  entry-point groups, execution order, aliases, constraint catalog, V11 coverage assertion, no
  generation-code change. audit-F15 (template modules) is a correctness defect inside this
  delivery.
- **R6 (dual-run capable) — met.** Internal entry, never a flag, no legacy intermediates.
- **R7 (acceptance authority) — structurally met, evidentially weak.** The matrix maps exactly
  the 29 contract cells without duplicating definitions (parsed from the contract at test time),
  but green cells assert only that the named kept test exists, and blocked cells use imperative
  `pytest.xfail`, which never flips red when a cell starts working (audit-F12/F13/F14).
- **R8 (deletion in scope of design) — met** at the design tier; the two-complete-routes
  duplication is the ratified migration shape, not a ledger violation.
- **R9 (exact parser identity) — met for all covered forms**, re-verified this pass at the
  resolver and evidence boundaries.
- **Non-goals** — respected: no snapshot v5 or baseline byte changed (verified), no legacy
  deletion, no shipped flag. The non-finite-multiplicity non-goal's *boundary* is what audit-F11
  contests: the blocked populations are finite.

### Design conformance

- **D1–D7:** implemented as designed and verified (identity wrappers, endpoint-ID slot families,
  independent walker, typed node/port identity, one resolver with named zero/multiple outcomes,
  ordered writer tiers by subtype partial order, direct typed edges).
- **D8:** projection owns strings; nothing flows back into graph identity (no graph mutation in
  `project.py`); collisions block before write.
- **D9:** the codec is canonical, fingerprinted, validated, and unconnected to the v5 loader,
  capture, or CLI (verified importers).
- **D10 — partial residue:** the catalog is live, but two loud-yet-uncoded escapes remain:
  `NonFiniteMultiplicityError`/`RecursiveContainmentError` are plain `ValueError` subclasses
  (`occurrence.py:42,46`) outside the `ElaborationCode` vocabulary, and bare `ValueError`s exist
  at `elaborate.py:490,640`. Strict/lenient never fabricates an edge (verified).
- **Integration strategy:** honored — complete-route isolation verified at import level and by
  kept tests; `orchestration/__init__.py` byte-identical to HEAD; only `analysis/`-frozen files
  untouched.

### Code integrity

- **Silent skip (failure honesty):** `elaborate.py:293-298` drops a feature that has no slot
  (`continue` on missing element or `KeyError` from `slot_of`) with no diagnostic. This is the
  exact class the diagnostic vocabulary exists to name. Should emit a named finding or be
  justified as a recorded rule.
- **Sentinel mode switch:** `_typed_definition(..., required: bool = True)`
  (`elaborate.py:631-644`) either raises or returns `None` by flag, and its raise is an uncoded
  `ValueError`. Split the two behaviors or code the error.
- **Guard coverage gap:** the import-boundary guard scans only `identity.py`/`occurrence.py`/
  `elaborate.py` (+`display.py` allowlist). `project.py`, `diff.py`, `diagnostics.py`, and
  `snapshot/instance_graph.py` are unscanned (`elaborated_pipeline.py` is separately covered by
  the dual-run source test). `project.py`'s `sanitize_name` import is legitimate under D8 but
  unguarded — extend the guard or state the boundary.
- **Matrix xfail mechanics:** imperative `pytest.xfail` is behaviorally a skip (audit-F13/F14);
  the `EVIDENCE` map and the suite are hand-synchronized representations (smell 1 pattern,
  second instance beside the resolved enum/exception one).
- Notes, no action demanded: `Diagnostic.code` is a union of `ElaborationCode | ReadinessCode` —
  two vocabularies by construction, but the readiness codes are the inherited contract codes, so
  the split mirrors the extraction/elaboration boundary; the corpus runner's hardcoded 37 exits
  non-zero on drift (loud, and pinned by the ledger test); the runner's one broad `except` records
  the route outcome as data, which is its job. No TODO/FIXME/placeholder stubs anywhere in the new
  modules.

---

## Certification

**Needs Work.** The product-lens ledger gate is BLOCKED (standing audit-F2, new
audit-F11/F12/F15/F16 — all owner/HARD-graded), three smells fired and are unresolved, and the
item's own plan records Phase 5 as incomplete pending owner dispositions. Under the audit rule, an
unresolved owner/`[HARD]` contradiction forbids Certify regardless of the green rubric.

What was checked and left marked:

- Plan Phases 1–4 Progress boxes and all their changes-required/validation boxes — verified,
  remain `[x]`. Phase 5's checked boxes verified as genuinely done; its unchecked boxes remain
  honestly unchecked. No box state changed.
- No spec or epic success criterion was marked (none is met: matrix not green, ledger rows
  unresolved, owner checkpoint pending).
- Appended the 2026-08-09 product-lens block to `product-lens.md`; preserved the Phases-1–2 audit
  at `audit-20260808-phases12.md`.

Gates reproduced on this tree (licensed):

- Full codegen: **3280 passed / 47 skipped / 18 deselected / 12 xfailed** — exact match to the
  recorded gate. Full agentic-mbse: **1814 / 1 / 33**.
- Focused: fail-closed + collisions + projection + generation + round-trip = 19 passed; Phase-5
  files = 26 passed + 12 xfailed (the 12 cells listed in the matrix).
- Fresh 37-fixture dual run matches every ledger total and the checkpoint rows I probed
  (solar/d38/deep_cross_scope/retype errors; non-numerical and unresolvable-attr graphs).
- `mypy src/`: 72-error baseline. Scoped `ruff check` over all changed/new files: clean.
  `git diff --check`: clean. No snapshot-v5 or baseline fixture bytes changed; `orchestration/`,
  `analysis/`, `resolution/` untouched except nothing at all.

**Before the owner checkpoint is presented,** the checkpoint materials need two corrections that
this audit surfaces rather than resolves: (1) diff-ledger decision 1 should present C17/C26 as
blocked by the walker's literal-token check on finite modeled populations (audit-F11), alongside
the previously surfaced parametric-form question — not solely as a contract-amendment choice;
(2) the "12 blocked cells" figure should be split into 5 reproduced blockers (C5, C17, C18, C21,
C26) and 7 unwritten fixtures (C2, C3, C4, C6, C7, C14, C23) per audit-F14.

**Not checked:** red-first chronology beyond the plan's own notes (trees are uncommitted; git
cannot confirm sequence, and Phase 5's violation is self-recorded); line-level zero-license-skip
proof for this pass's full-suite rerun (counts match the licensed baseline exactly, which an
unlicensed run cannot produce, but skip reasons were not enumerated); C18's load-error reproduction
(taken from the matrix xfail reason and ledger, not re-run); row-level content of the six
`needs-review` rendered-metadata diffs (totals and statuses verified, per-section payloads not);
full-tree ruff/format debt beyond the accepted baselines; downstream consumers of the changed
agentic-mbse fact types beyond its full suite; and the lens's line-number citations into the
contract/epic (its code and fixture claims were independently reproduced; its prose citations were
spot-checked only).
