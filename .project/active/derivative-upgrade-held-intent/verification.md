# Verification — Derivative Upgrade Under Held Intent (CONSTRAINT-SEMANTICS Item 9)

**Run:** 2026-08-13, implement stage, branch `item7-rebuild`.
**Interpreter:** `/home/reid/1cfe/item7-rebuild-venv/bin/python` (not `uv run`).
**License:** `set -a; source /home/reid/1cfe/agentic-mbse/.env; set +a` on every run below.

Counts, not adjectives. Every line here is a number a later reader can re-measure.

---

## SC-6 — the commit order is the evidence

The item landed in five commits. **C2 carries every expectation and sits before the first
confirmation run**, which is C3. Nothing was read off a run and written back as an expectation.

| commit | SHA | what it carries |
|---|---|---|
| C1 | `28942ec` | the three edited `.sysml` sources + the re-captured snapshot (**a capture, not an expectation**) |
| C2 | `185dec7` | **all five expectation documents**, derived from the ruled table and from authored source |
| C3 | `da034ac` | the per-occurrence prover, the falsification cases, and the **first confirmation run** |
| C4 | `52c6381` | the two BACKLOG records (SC-3 side 2 + the `ProductWithinBand` cost) |
| C5 | *this file* | `verification.md` |

The one value C2 needed from outside the ruled table is A9's `source_line`, **171**, read from
`designs/catf_mfe/vacuum.sysml` after C1's edit. Source is not an expectation.

No committed expectation was contradicted by any later run, so the plan's "correct it in its own
named commit" path (Item 5's discipline) was never entered.

---

## The restated identity

```
$ python scripts/check_gated_manifest.py --check
identity closes: 65 = 56 carriers + 9 named deletions
  carriers matched by name:         53
  carriers matched by renamed_from: 3
```

**30 derivations gated per occurrence** (13 for A5 + 14 for A6 + 3 pre-existing), counted from
`DERIVATIONS`. Every one is anchored to its owning declaration block; there is no file-wide
fallback and no unchecked row.

One failure message, read end to end, to confirm it names the layer rather than the file:

```
CATFMFERadialBuild::catf_radial_build::RadiusThicknessConsistency: the derivation
`attribute outer_radius : Real = inner_radius + thickness;` in `blanket` at
designs/catf_mfe/radial_build.sysml:243 is missing the undirected relation and the
chosen-basis statement — required by owner-disposition.md:37-41
```

---

## Measured generation shape (Phase 1, both lanes)

The lane the design probe never exercised — v6 capture, re-seal, license-free projection —
**completed with no refusal.** No `SnapshotCertifiabilityError`. Design bet **B3** holds through
snapshot certification, not only through generation.

| | `generate --models` | `generate --from-snapshot` |
|---|---|---|
| outcome | sealed | sealed |
| modules | 62 | 62 |
| implementation stencils | 58 | 58 |
| parameter-group schemas | 9 | 9 |
| JSON input templates | 9 | 9 |
| preflights | all five pass | all five pass |

**Module count is measured, not pre-committed** (the ruled table cannot predict it — 27 new
computed attributes mint modules). The probe saw 62; this stage re-measured and got 62.

**Expected registry warning present on both routes and left alone:**
`Module class name collisions detected: ['outer_radiusModule']. Generating aliased imports for 15
modules.` That is the registry preflight doing its job.

### Public key movement — 65 → 55, exactly the derived sets

**26 leave, 16 arrive.** Both match the design's source-derived sets with nothing left over. A key
moving outside those sets would have been a surfacing event; none did.

- **26 leaving** — the 13 geometry-carrying layers' `inner_radius` + `outer_radius` pairs.
  `axis_region` carries no geometry calc, so its two radii were never keys — the same 26/27 split
  Item 5 measured.
- **16 arriving** — 13 layer `thickness` keys (`tf_coil.thickness` was already one) +
  `axis_region.thickness` + `axis_region.inner_radius` + A9's `pump_capacity_each` and
  `pumping_speed_agrees__rel_tol`. Counted from the generated `inputs/*.json`: 13 thickness keys
  including `axis_region.thickness`, plus `axis_region.inner_radius`, plus the two A9 keys = 16.

### Snapshot re-capture diff

**The v6 envelope carries no `captured_at` field**, so the plan's "anything beyond `captured_at`"
filter had nothing to filter. Every field that moved traces to the edited sources:

- `sources.files` — exactly three entries changed, by `sha256` and `size_bytes`:
  `radial_build.sysml`, `vacuum.sysml`, `gate_forms.sysml`. The other 26 files are byte-identical.
- `sources.fingerprint`, `integrity.digest`, `instance_graph.fingerprint` — all follow the content.
- `instance_graph.graph` — `attrs` 374→360, `calcs` 44→58, `constraint_usages` 58→56,
  `constraints` 5→3.

`constraints` 5→3 is the ruled movement, not a loss: the three inline definition-less nodes
(`LayerContinuity`, `RadiusThicknessConsistency`, `PumpingSpeedConsistency`) are gone, and
`CATFGateForms::ProductWithinBand` joined `PositiveQuantity` and `FractionWithinBand` as a
def-typed constraint. Nothing spurious moved.

---

## Suite

Full licensed run, `python -m pytest tests/` on the item7-rebuild venv:

```
7 failed, 2063 passed, 34 skipped, 79 deselected, 1 warning in 158.79s
```

**License proof: zero license-skip lines.** `grep -ci license /tmp/item9_full.log` → **1**, and
that single hit is a test *name*, not a skip:
`test_exact_route_snapshot_generation.py::test_generation_from_a_v6_snapshot_needs_no_license
PASSED`. None of the 34 skips is license-gated.

The plan's known pre-existing artifact,
`tests/execution/…::test_the_lane_runs_the_real_simkit`, **did not fail** on this whole-set run.

### The 7 failures are pre-existing and are not this item's — measured, not argued

All seven are in `tests/conformance/test_v6_snapshot_inventory.py`, and all seven fail the same
way:

```
FileNotFoundError: .project/active/unit-lane-port-metadata/snapshot-inventory-pre.json
```

That is **Item 8's own conformance test reading Item 8's own item folder by an `active/` path
that no longer exists.** The concurrent agent closed Item 8 at `fbd3495`, archiving the folder to
`.project/completed/20260813_unit-lane-port-metadata/`; the test still cites
`ROOT/".project"/"active"/"unit-lane-port-metadata"`
(`tests/conformance/test_v6_snapshot_inventory.py:16`).

Proof it is not Item 9's: the same file was run in a detached worktree at **`8942420`**, the
commit immediately before C1 and before any Item 9 edit:

```
$ git worktree add --detach /tmp/item9_preworktree 8942420
$ pytest tests/conformance/test_v6_snapshot_inventory.py
7 failed, 1 passed in 0.27s        # byte-for-byte the same seven
```

`git ls-tree 8942420 .project/active/unit-lane-port-metadata/` is already empty, so the path was
dead before this item started.

**Surfaced, not fixed.** Repointing the constant at the archived path would be an edit to another
agent's in-flight item, which the spec forbids (`[HARD]`: stage and commit only files this item
touches). It is recorded here so Item 8's close, or the epic's next audit, owns it.

**So: the suite is green except for seven pre-existing failures that reproduce on this item's
parent commit. Item 9 introduces no new failure.** The plan's Phase 5 gate reads "full licensed
suite green"; it is not green, and the honest statement is the one above rather than a claim of
green with a footnote.

---

## Static gates

| gate | baseline | measured at HEAD | new |
|---|---|---|---|
| `ruff check src/` | 12 | **12** | **0** |
| `mypy src/` | 52 | **52** | **0** |
| `ruff check` on the two Python files this item touched | — | **0 errors** ("All checks passed") | **0** |

`ruff check src/ scripts/ tests/` reports 642 at HEAD. That wider count is dominated by
pre-existing test files and is not the plan's stated baseline of 12, which is a `src/`-only number.
The zero-new claim over the wider scope rests on the direct measurement above: the only Python
files this item touched — `scripts/check_gated_manifest.py` and
`tests/conformance/test_gated_manifest_identity.py` — are clean, so the wider count cannot have
risen.

`git diff --check` over the twelve files this item's commits touch: **clean**, no whitespace errors.

---

## Frozen surfaces

Compared as git tree hashes over each directory, pre-Item-9 (`8942420`) against HEAD:

| surface | result |
|---|---|
| `tests/fixtures/catf_mfe_model/` | **IDENTICAL** |
| `tests/fixtures/catf_mfe_d5/` | **IDENTICAL** |
| `.project/completed/20260813_catf-constraint-policy-acceptance/` | **IDENTICAL** |

`git diff --stat 8942420..HEAD` over those three paths is **empty**.

> **The plan's literal check reads wrong, and is recorded rather than quietly substituted.**
> It asks that `git diff --stat main...HEAD` name no file under those paths. It names many — but
> because **earlier items on this branch created them**: `catf_mfe_d5` and the archived acceptance
> item are both new on `item7-rebuild` relative to `main`, and `catf_mfe_model`'s
> `extraction_snapshot.json` was deleted by the cutover retirement. The freeze this item owes is
> "Item 9 does not touch them", and the reference point that tests it is the pre-Item-9 commit,
> which is the measurement above. The `main` comparison cannot distinguish an Item 9 edit from an
> Item 5 creation.

`git status --porcelain` carries no staged file belonging to the concurrent agent. The twelve
files across C1–C5 are all this item's; `CURRENT_WORK.md`, `CHANGELOG.md` and the calcdef-design
archive moves were never staged.

---

## Design.md's Validation Approach, items 1–7

1. **`check_gated_manifest.py --check` reports `65 = 56 carriers + 9 named deletions`**, `53` by
   name, `3` by `renamed_from:`. ✅ Output quoted above.
2. **`test_gated_manifest_identity.py` green, including occurrence-scoped falsification cases.** ✅
   Four new cases, each mutating one owning block: `blanket`'s `outer_radius` documentation
   stripped → exactly **1** problem naming that derivation and both missing statements; that
   initializer removed → exactly **1**, "not found"; the owning block renamed → **2** ("owner block
   `blanket` not found", one per usage); the block duplicated → **2** ("is ambiguous"). No
   unbounded `str.replace`: the fixture's rewriter is scoped to one `part` block's line range.
3. **Licensed suite, zero license-skip lines**, on the item7-rebuild venv. ⚠️ Zero license-skip
   lines confirmed; 2063 passed. **Not fully green** — 7 pre-existing failures in Item 8's
   `test_v6_snapshot_inventory.py`, reproduced identically on this item's parent commit. Item 9
   introduces no new failure. See Suite.
4. **Frozen twins and the archived ruling untouched.** ✅ See Frozen surfaces, including the note
   on how the plan's `main`-relative phrasing reads.
5. **The package builds and seals; key movement is exactly the 26/16 sets.** ✅ Both lanes sealed;
   26 leave / 16 arrive, nothing outside the sets.
6. **SC-3 recorded on both sides.** ✅ `grep -n INLINE-PREDICATE-MARKER-DROP` hits **both**
   `tests/fixtures/catf_mfe_gated/PROVENANCE.md` (2 hits) and `.project/backlog/BACKLOG.md`
   (2 hits). Read: PROVENANCE §3b states the epic's third criterion is a conditional that did not
   fire and names the open defect as its trigger; the backlog entry states that closing the defect
   fires the B1–B5 marker migration. Neither side is missing, and the backlog's stale clause was
   **amended** rather than annotated.
7. **§5 carries an A9 subsection and the float-drift record is findable.** ✅
   `PROVENANCE.md:487` — *"### A9 `pumping_speed_agrees` — `observed` within
   `count * each_capacity ± 1%`"*, matching A2's and A3's shape and carrying the ruled unit-check
   cells. `PROVENANCE.md:260` — *"### The float-drift record — surfaced, not absorbed"*.
   `PROVENANCE.md:442` — *"### Item 9's decision D3 — `tf_coil.thickness`'s unit comment"*.

---

## Surfaced, not absorbed

**Float drift is real and is recorded in the fixture, not only in the archiving design.** Four
layers' `outer_radius` values drift −8.88e-16 m from the authored literals
(`vacuum_gap`, `first_wall`, `blanket`, `reflector`), the chain re-converges at
`ht_shield.outer_radius`, and `bioshield.outer_radius` is exactly `8.55`. No generated byte
changes, so it can only appear at execution. **If an execution expectation moves, that is the
surfacing event, not a number to absorb.** Recorded at `PROVENANCE.md` §2's float-drift record.

**The `ProductWithinBand` def-shape change is NOTE-ed, not silently adapted**, as row A9 requires:
the form cannot be generic over bare `Real` formals, because a constraint formal's port takes its
unit from the formal's own declaration. Recorded in the design's NOTE, in `PROVENANCE.md` §1 and
§5, and filed unowned as `[CONSTRAINT-FORM-PER-DIMENSION-COST]`.

**Nothing was re-dispositioned.** Every target form is the ruled one. The only source edit outside
the ruled 27 is D3's `tf_coil.thickness` comment, ratified at design review and recorded at
`PROVENANCE.md:442`.

---

## Orchestrator rider (2026-08-13, post-C5): the 7 suite failures are CURED at HEAD

The 7 failures recorded above (`tests/conformance/test_v6_snapshot_inventory.py`, all
`FileNotFoundError` on `.project/active/unit-lane-port-metadata/snapshot-inventory-pre.json`)
were caused by Item 8's close archiving its item folder (`fbd3495`) while the test still read
the `active/` path — pre-existing relative to Item 9's commits, reproduced at the pre-C1 parent.

Cured by the orchestrator under the F5 ruling family **[OWNER 2026-08-13]** (suite collection
must not depend on archive layout; durable home `tests/unit/data/`): both inventory JSONs moved
bytes-unchanged (`git mv`) to `tests/unit/data/item8-snapshot-inventory-{pre,final}.json`, the
test's path constants repointed (incl. the would-be recapture receipt), and a pointer stub left
at the archived location. Result: **8/8 pass** in the file. This makes the whole-suite expected
count `2070 passed` where the pre-rider record says `2063 passed / 7 failed`; the audit should
re-run and record the green number. Not Item 9 scope-creep: the cure touches no Item 9 surface
and is committed separately with its own provenance.
