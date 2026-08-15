# Audit: Derivative Upgrade Under Held Intent (CONSTRAINT-SEMANTICS Item 9)

**Verdict:** Certify-with-residuals
**Audited:** 2026-08-13
**Branch:** `item7-rebuild`
**Commit:** `e92574d` (item commits C1–C5 = `28942ec`, `185dec7`, `da034ac`, `52c6381`, `2633834`;
post-C5 orchestrator cure `4155b4d`)
**Interpreter:** `/home/reid/1cfe/item7-rebuild-venv/bin/python` (never `uv run`)

---

## The Point

`tests/fixtures/catf_mfe_gated` is the worked example of the ruled constraint policy. Its rows must
be the shape the owner ruled, not the shape a defect allowed. Three rows were not: A5 and A6
asserted by constraint what the ruled basis says should be computed, A9 compared two independently
authored routes with an exact `==` where the owner ruled a 1% relative band, and the fixture's
PROVENANCE still carried `blocked-by-defect` markings whose cause (the unit-lane port defect) Item 8
cured at `62a07e5`.

Four obligations sit under that:

- The owner decides dispositions, bases and tolerances; agents execute them. A parameterization is
  an engineering decision carrying owner sign-off, never a side effect of classification.
- Every accounting number is a mechanical consequence of the ruled table — never a re-decision, and
  never read off a run (Item 5's SC-6 discipline).
- A deletion is accepted only against outside evidence: each `derive-instead` deletion ties to a
  derivation that exists in source and carries the undirected relation plus the chosen-basis
  statement. This is the gap that once shipped two bare initializers past four gates (audit A-1).
- Surfacing beats absorbing. A ruled form that cannot be built, or a number that moves when the
  arithmetic says it should not, is an owner event — not a re-baselined expectation.

## Summary

The item does what it claims, and the claims survived independent re-measurement. Every spec success
criterion is met. The prover's per-occurrence anchoring is real, not decorative: all four
occurrence-scoped failure modes were exercised on a scratch fixture copy and each was a reported
problem naming the layer, never a skip and never a sibling-satisfied pass. The 26-leave/16-arrive
public key movement reproduced exactly, key for key, from an independent generation run on both
lanes. The full licensed suite is green at **2070 passed, 0 failed, 34 skipped**, with zero license
mentions of any kind in the log.

The residuals are small and none blocks: one recorded count in `verification.md` does not reproduce
(implementation stencils), one plan checkbox is ticked against a substituted-and-disclosed
measurement, and the epic's third Item 9 criterion is by ruling a conditional that did not fire, so
the epic item cannot be fully ticked.

## Product Judgment

**Is this the right piece of work?** Yes. The item is the discharge of an obligation the epic-level
lens already carried against it (`.project/completed/20260813_catf-constraint-policy-acceptance/product-lens.md`
**audit-F5**, DISPOSED, "carried forward as an explicit obligation on the epic Item 9 follow-on"):
after this item, no instance-reaching physics gate sits outside the coverage denominator. It executes
held intent and re-derives arithmetic; it re-decides nothing.

**Ledger gate: DISPOSED, not BLOCKED.** Scanning every block in
`.project/active/derivative-upgrade-held-intent/product-lens.md`:

- spec block (CONCERNS, F1–F8) — all eight disposed in-session, dispositions recorded at
  `product-lens.md:167-186`, and each disposition is visible in the shipped artifacts. Spot-checked:
  F1 → requirement P-1 (archive frozen, verified byte-identical below); F2 → per-occurrence prover
  (verified by falsification); F7 → the ledger row carries its `complete` column
  (`tests/unit/data/expected-coverage.md:358`); F8 → `BACKLOG.md` amended, not appended (`52c6381`).
- design block (CONCERNS, D-F1, D-F2) — no disposition block was appended, but both resolve by
  citation in the delivered work: D-F1's predicate is written into the design
  (`design.md:205`), and D-F2's two live-surface records exist
  (`PROVENANCE.md:260` float drift, `PROVENANCE.md:442` decision D3). Recorded here so the
  resolution is not left to inference. No `BLOCK` exists anywhere in the ledger.

**Structural smells (product-lens spec §4), the five code/test ones:**

- **"Two representations manually kept synchronized" — fired, and disposed.** The prover's `_LAYERS`
  tuple (`scripts/check_gated_manifest.py:107-122`) restates the fixture's 14 radial-build layers and
  their order, which also live in `radial_build.sysml`. Disposed: the duplication is fail-closed in
  the direction that matters — a layer renamed or duplicated in source is a reported anchor failure,
  verified live (probes C and D below) — and the four *document* representations (both population
  files, PROVENANCE, the manifest expectation) are machine-joined, not hand-synchronized
  (`check_gated_manifest.py:411-434`, `_refuse_disagreement_with_the_ruled_table`). The residual
  direction is recorded as R4.
- **"A special category exempts a case whose user-visible meaning is unchanged" — fired on inherited
  code, disposed.** `DERIVATIONS` maps A1 and A4 to `None`, exempting two of the seven
  `derive-instead` rows from the outside-evidence gate on a hand-written judgment
  (`check_gated_manifest.py:153-155`). Disposed: pre-existing — identical at the pre-Item-9 parent
  `8942420` — reasoned in-line, and Item 9 neither widened nor narrowed it. Recorded as R5.
- **"Test passes only because it selects one route" — did not fire.** Both generation lanes were
  measured independently by this audit and agree field for field. The conformance falsification cases
  are scoped to one `part` block by line range rather than an unbounded `str.replace`
  (`tests/conformance/test_gated_manifest_identity.py:165-190`), which is precisely the anti-signature.
- **"Correctness depends on downstream knowledge of an internal representation"** and **"a baseline
  preserves behavior that contradicts the product's reason"** — did not fire.

Neither fired smell survives into a Needs-Work judgment: one is fail-closed and machine-checked, the
other is inherited and unchanged.

**Lens runner note.** The lens was applied by this session directly against
`~/.claude/scripts/product-lens.md` (readable this session, unlike at the spec and design stages)
rather than by a spawned subagent, per this session's standing instruction not to spawn agents
unless asked. SOURCES read: `CLAUDE.md`, `README.md`, `docs/architecture/`, `owner-disposition.md`,
the fixture's `PROVENANCE.md`. `.project/adr/` and `.project/product/` do not exist in this tree, so
there is no promise index to read first — the same absence the earlier blocks recorded.

## Findings

### Plan completion

All five phases are complete; every checkbox in `plan.md` is ticked and each was spot-verified
against the artifact it claims. Two notes, neither a gap:

- `plan.md:449` ticks *"`git diff --stat main...HEAD` names no file under [the three frozen paths]"*.
  That literal check does **not** pass, and `verification.md:194-201` says so explicitly and
  substitutes the pre-Item-9 parent as the reference point, with the reason (the twins and the
  archive were created on this branch, so a `main` comparison cannot distinguish an Item 9 edit from
  an Item 5 creation). The substitution is correct and disclosed rather than quietly performed. The
  ticked box is nevertheless ticked against a check that was not run as written — recorded as R2.
- `plan.md:459` ticks the `test_the_lane_runs_the_real_simkit` contingency. It did not arise: that
  test lives behind the `execution` marker, which `pyproject.toml:46` deselects by default (79
  deselected in this audit's run). Not exercised here — see **Not checked**.

### Spec conformance

Each success criterion, with the probe behind it:

- **Three executing gates (A2, A3, A9); A9 asserts `ProductWithinBand` at `rel_tol = 0.01`.** ✅
  `designs/catf_mfe/vacuum.sysml:171-176` carries the assert in exactly the ruled sketch's shape and
  bindings form. The disposition histogram is `{eligible: 3, excluded: 0, non_reaching: 53}`
  (`tests/expectations/gated_manifest/catf_mfe_gated.json`), read this session.
- **A5/A6 deleted and replaced by derivations on the ruled basis.** ✅ 14 × `attribute outer_radius :
  Real = inner_radius + thickness;` and 13 × `attribute inner_radius : Real = <below>.outer_radius;`
  in `radial_build.sysml` = the ruled 27. `axis_region.inner_radius = 0.0 [m]`
  (`radial_build.sysml:77`) is the free root. Neither `LayerContinuity` nor
  `RadiusThicknessConsistency` survives anywhere in the file.
- **`blocked-by-defect` retired on the live surface; the archive byte-untouched.** ✅ The only live
  occurrences are the retirement heading and its record (`PROVENANCE.md:291,293`); the archived
  `owner-disposition.md` still carries its 9 occurrences and is byte-identical (below).
- **Expectations re-derived from the table and committed before any confirmation run (SC-6).** ✅ See
  the dedicated section below — this is the criterion the audit probed hardest.
- **The manifest re-proves the restated identity.** ✅ `scripts/check_gated_manifest.py --check` run
  fresh this session prints `identity closes: 65 = 56 carriers + 9 named deletions`, `53` by name,
  `3` by `renamed_from:`, exit 0. The nine deletion records are `D1…D9` at
  `PROVENANCE.md:168-247`, and their qualified names are exactly the spec's nine-row table.
- **Frozen twins and the archived ruling byte-untouched.** ✅ Git tree hashes, pre-Item-9 `8942420`
  against HEAD: `tests/fixtures/catf_mfe_model/` `f0330fc…` = `f0330fc…`; `tests/fixtures/catf_mfe_d5/`
  `e3e8701…` = `e3e8701…`; `.project/completed/20260813_catf-constraint-policy-acceptance/`
  `1d5318b…` = `1d5318b…`. `git diff --stat 8942420..HEAD` over the three paths is empty.
- **Licensed suite green with zero license-skip lines.** ✅ `2070 passed, 34 skipped, 79 deselected,
  1 warning in 158.55s`; `grep -ci license` over the log is **0**. The seven
  `test_v6_snapshot_inventory.py` failures recorded pre-rider are gone — that file is now 8/8.
- **SC-3 recorded on both sides as a not-fired conditional.** ✅ Side 1 at `PROVENANCE.md:353-361`;
  side 2 at `BACKLOG.md:1148ff`, delivered as an amendment of the now-false clause rather than an
  appended line (`git show 52c6381` diff read in full), with the second stale cross-reference at
  `:1208` amended to match.

Tagged requirements, spot-checked beyond the criteria: the ruled 1% band is written relatively over
formals with no `[unit]` literal in the predicate body (`gate_forms.sysml:35-42`); no formal is named
`value`; the `ProductWithinBand` def-shape change is NOTE-ed rather than silently adapted
(`design.md:236`) and filed unowned as `[CONSTRAINT-FORM-PER-DIMENSION-COST]` (`BACKLOG.md`, C4).
Non-goals were respected: nothing outside the radial build was derived, the frozen twins did not
move, TEAx was untouched, and no schema or catalog-vocabulary token changed.

**Ruled-cell fidelity.** No re-disposition anywhere. The one source edit outside the ruled 27 is D3,
`tf_coil.thickness`'s trailing comment (`radial_build.sysml:507`), which matches its ratification
record at `PROVENANCE.md:442-452` verbatim — the original provenance text is preserved inside the
amended comment and only a readable unit was prepended.

### SC-6 provenance — the strongest evidence in the item

Three independent readings, all consistent:

1. **Commit order.** C2 `185dec7` (19:53:42) carries all five expectation artifacts and precedes C3
   `da034ac` (19:57:41), which carries the prover extension and the first confirmation run. C1
   `28942ec` carries only sources and the re-capture — a capture, not an expectation.
2. **Immutability after C2.** `git diff 185dec7 HEAD` over
   `tests/expectations/gated_manifest/catf_mfe_gated.json`,
   `tests/expectations/constraint_population/catf_mfe_gated.json` and
   `tests/unit/data/expected-coverage.md` is **empty**. No expectation was touched after the run that
   confirmed it, which is what reverse-engineering would look like.
3. **Spot-derivation from the ruled table, done by this audit without reading a run.**
   - `65 = 56 + 9`: 65 authored usages in the d5 population, 56 in the gated population, 9 `### D…`
     deletion records in PROVENANCE — counted directly from the three files.
   - The 9 by name are exactly the spec's table: the seven inherited (A1, A4, A7, A8, C37, C21, C28)
     plus A5 and A6. Seven `derive-instead` + two `delete-placeholder`.
   - Histogram: eligible 3 = A2 + A3 + A9; excluded 0 (A5/A6 left by deletion, A9 moved
     `excluded → eligible`); non_reaching 53 = 5 B-guards + 48 Group C guards, unchanged. 3 + 0 + 53
     = 56 closes against the carrier count.
   - Carrier split 53 by name + 3 by `renamed_from:` — the three renamed carriers are A2, A3 and A9,
     each carrying its authorizing row in the expectation file.
   - The 26-leave/16-arrive key sets: reproduced by generation, below.

### Design conformance

Implementation follows the design. The per-occurrence prover is built the way the design specified —
anchor by owning declaration block, close the block by brace depth, no file-wide fallback
(`check_gated_manifest.py:263-291`). Design bet B3 (the snapshot lane the probe never exercised)
holds: I re-ran both lanes at HEAD and both sealed with no `SnapshotCertifiabilityError`.

Design's Validation Approach items 1–7 all re-verify, with one number that does not reproduce (R1).

**Falsification sweep** — the prover's occurrence-scoped failure modes, exercised on a throwaway copy
of the fixture, mutating `reflector` (a middle layer, so a sibling-satisfied pass would show):

| mutation | result |
|---|---|
| A. `reflector.outer_radius` comment block stripped | **1 problem**, naming `reflector`, `radial_build.sysml:286`, both missing statements |
| B. `reflector.outer_radius` initializer deleted | **1 problem**, "derive-instead promises … inside `reflector` … not found" |
| C. owning block renamed to `reflector_renamed` | **2 problems** (one per usage), "owner block `reflector` not found" |
| D. owning block duplicated | **2 problems** (one per usage), "owner block `reflector` is ambiguous" |
| E. `vessel.inner_radius` comment stripped (the A5 leg) | **1 problem**, naming `vessel`, `radial_build.sysml:457` |

Baseline on the unmutated copy: no problems. Every mode is a reported problem that names the layer.
None degrades to a skip, to file scope, or to a pass on a sibling's documentation. The A-1 gap is
closed per occurrence, not per row.

**Independent generation probe** — `65 → 55` public input keys, both lanes:

- **26 leave**, and they are exactly the 13 geometry-carrying layers' `inner_radius`/`outer_radius`
  pairs. `axis_region`'s two radii were never keys.
- **16 arrive**: 13 `…__thickness` keys (including `axis_region__thickness`; `tf_coil__thickness` was
  already one), plus `axis_region__inner_radius`, plus A9's `…__pump_capacity_each` and
  `…__pumping_speed_agrees__rel_tol`.
- Nothing moved outside those sets. This matches `verification.md:78-89` key for key.
- Pipeline modules 62 on both lanes (64 entries − EntryPoint − ExitPoint), 9 parameter-group schemas,
  9 JSON input templates — all as recorded. The `outer_radiusModule` collision warning appears on
  both routes, which is the registry preflight working.

### Code integrity

No abstraction or failure-honesty problems found in the two Python files this item touched.

- `check_derivations` does one job and reports a list rather than raising on the first failure, so a
  multi-layer breakage names every layer. Anchor failures are caught narrowly (`AnchorError`), turned
  into reported problems, and never fall back to a wider scope — the explicit design choice, and the
  docstring says why (`check_gated_manifest.py:264-267`).
- No broad `except Exception`, no silent default, no optional parameter papering over missing data,
  no backwards-compatibility shim. Nesting stays shallow.
- The conformance fixture's rewriter is scoped to one `part` block's line range, with a comment
  saying that an unbounded `str.replace` would yield 14 problems and thereby prove file scope rather
  than per-occurrence scope (`test_gated_manifest_identity.py:165-190`). The test knows what it is
  falsifying.
- Static gates: `ruff check src/` **12** = baseline 12; `mypy src/` **52** = baseline 52; the two
  touched files clean on their own. The wider `ruff check src/ scripts/ tests/` reads **642** at
  HEAD and **642** at the pre-Item-9 parent `8942420` (measured in a detached worktree this session),
  so zero-new holds on the wide scope too, not only by inference. `git diff --check 8942420..HEAD`
  clean. `git status --porcelain` empty — nothing of the concurrent agent's was staged or absorbed.

### The post-C5 cure `4155b4d` (verified separately, not Item 9 scope)

The F5-family cure moves Item 8's two inventory JSONs bytes-unchanged to `tests/unit/data/`
(`git mv`, zero-line diffs in the stat), repoints the test's path constants, and leaves a pointer
stub at the archived location. It touches no Item 9 surface. Verified in effect:
`tests/conformance/test_v6_snapshot_inventory.py` is **8/8** in this audit's run, and the seven
`FileNotFoundError` failures recorded in `verification.md` are gone. The rider's predicted whole-suite
count of `2070 passed` is exactly what the re-run produced.

---

## Residuals

None blocks certification. All are recorded so the close does not have to rediscover them.

- **R1 — `verification.md:67` records "implementation stencils 58"; it measures 34.** Independently
  generated at HEAD on both lanes (`--models` and `--from-snapshot`), `handwritten/` holds 34 stencil
  modules (60 files including 26 package `__init__.py`). The other three rows of that table reproduce
  exactly: 62 pipeline modules, 9 parameter-group schemas, 9 JSON input templates. Nothing downstream
  depends on the number — the spec explicitly makes module and stencil counts measured, not
  pre-committed — so this is a wrong number in a record, not a defect in the work. It should be
  corrected in `verification.md` rather than left for a later reader to trip over.
- **R2 — `plan.md:449`'s frozen-surface checkbox is ticked against a substituted measurement.** The
  substitution is right and is disclosed at length (`verification.md:194-201`); the audit re-ran the
  correct measure and it passes. Recorded only so the tick is not read as "the literal check ran".
- **R3 — the epic's third Item 9 criterion is a not-fired conditional and stays unticked.** Ruled
  `[OWNER 2026-08-13]` at Align; both sides of the trigger are recorded. The epic item therefore
  cannot be fully checked off by this audit, and its heading is left without ✅ until
  `[INLINE-PREDICATE-MARKER-DROP]` closes.
- **R4 — the prover gates the 27 derivations it knows about, not the layers the file contains.**
  `_LAYERS` (`scripts/check_gated_manifest.py:107-122`) is the authority for what gets checked. A
  fifteenth layer added to `radial_build.sysml` with a derived radius but no `_LAYERS` row would carry
  no documentation obligation. Nothing today can drift silently — rename, duplication, missing
  initializer and stripped documentation all fail closed, verified above — so this is future-proofing,
  not a live hole.
- **R5 — `DERIVATIONS` exempts A1 and A4 from the outside-evidence gate by a hand-written `None`.**
  Pre-existing (identical at `8942420`), reasoned in-line, and untouched by this item. Worth an owner
  eye only if the gate is ever generalized beyond this fixture.

---

## Certification

**Certify-with-residuals.** Every spec success criterion is verified met, by re-measurement rather
than by reading the item's own record. The product-lens ledger gate is DISPOSED, not BLOCKED; two
structural smells fired and both are disposed in the Product Judgment above. The residuals are one
wrong recorded count, one disclosed measurement substitution, one criterion that is by ruling
conditional and did not fire, and two forward-looking notes on a prover that currently fails closed
everywhere it was probed.

Marked as a result of this audit: all eight spec success criteria; all five plan phases (already
ticked, verified); the epic's Item 9 first two success criteria. The epic's third criterion and the
Item 9 heading's ✅ are deliberately left, per R3.

**Not checked:**

- **The `execution` marker lane.** `pyproject.toml:46` deselects it by default; 79 tests were
  deselected in this run, including `test_the_lane_runs_the_real_simkit`. No real-simkit execution of
  the regenerated package was performed, so the float-drift surfacing prediction
  (`verification.md:243-248` — four layers' `outer_radius` drifting −8.88e-16 m, visible only at
  execution) is **unverified by this audit**. If an execution expectation later moves, that is the
  surfacing event the item already named, not a re-baseline.
- **The TEAx checkout.** Not read; no TEAx-side claim in this audit is first-hand.
- **`expected_study_outcomes`' runtime tokens.** The candidate outcomes were read as committed text,
  not executed.
- **Byte-level review of the re-captured `instance_graph_snapshot.json`.** The audit confirmed the
  envelope generates and seals on both lanes and that the fingerprint chain is coherent; it did not
  re-verify `verification.md`'s field-level diff account (three source files changed; `attrs`
  374→360, `calcs` 44→58, `constraint_usages` 58→56, `constraints` 5→3).
- **Sibling items.** Items 6 and 7 were not audited; the concurrent agent's in-flight work was read
  only where it intersected (`BACKLOG.md` cleanliness, the `4155b4d` cure's effect).
- **`CURRENT_WORK.md` and `BACKLOG.md` were read, not written** — per the orchestrator's concurrency
  instruction. Nothing was committed by this audit.
