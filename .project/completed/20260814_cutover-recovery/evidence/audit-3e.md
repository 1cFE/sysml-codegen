# Slice 3E audit — public authority switch

**Verdict:** **CERTIFY** (6 findings — 1 Medium, 4 Low, 1 Informational; none blocking)
**Audited:** 2026-08-11
**Auditor:** independent agent, fresh session, did not implement this slice
**Subject:** sysml-codegen `430e26a` (+ OID record `885c2b1`) on `item7-rebuild`
**Companion:** agentic-mbse `cc6c7a7411f6338a4811a7cc58ca002c29ef177b`, verified unchanged and clean

---

## The point

The recovery exists because two generation authorities shipped at once and the string-era one
attributed model facts to the wrong places. Slice 3E is the hop where the product actually stops
being ambiguous: one public entry point, one construction route, two *sources* (live models, v6
snapshot). Everything before it was building the exact route beside the legacy one; everything
after it (Phase 4) deletes the legacy one. Phase 4's deletion planning consumes what this audit
certifies, so the two questions that matter here are whether the switch is real (not a spelling
change) and whether the 116 moved test nodes are an honest reclassification rather than a quiet
loss of coverage.

Both hold. The switch is proven by artifacts and refusals a caller can see, and the node-id diff
shows nothing was deleted, silenced, deselected or xfailed.

## Environment (asserted, not assumed)

- venv `/home/reid/1cfe/item7-rebuild-venv`; all three import paths re-asserted (F2 trap):
  `sysml_codegen` → `/home/reid/1cfe/sysml-codegen-item7-rebuild/src/...`, `agentic_mbse` →
  `/home/reid/1cfe/agentic-mbse-item7-rebuild/src/...`, `syside` → the venv's site-packages.
- Licence loaded via `set -a; source /home/reid/1cfe/agentic-mbse/.env; set +a`. Proof: **zero**
  `no live syside license` lines in the full-suite output.
- Old-commit work ran in a throwaway worktree at `0a812af` with `PYTHONPATH` forced and
  `sysml_codegen.__file__` asserted into that worktree before any measurement.
- Scratch `/tmp/claude-audit3e/`. The only repository file written is this one. No commits. One
  temporary production mutation (finding-free experiment, §4) was reverted and the tree verified
  byte-identical afterwards.

---

## 1. Single authority, verified by behaviour

Re-run by me, at the **installed console script** (`sysml-codegen`), not only through the test
module:

| Case | Measured |
|---|---|
| `generate --models tests/fixtures/d38_caret` | ships `inputs/library_params.json` — the exact route's answer. Legacy on the same model ships `inputs/design_params.json` with one key. Both arms re-measured by me. |
| `generate --models tests/fixtures/chain_spike_model` | refused, exit 1, typed: `Model is not ready for the exact route: SI_SELF_BINDING: …` (three). No output tree created. Legacy generates it (verified). |
| `generate --from-snapshot <v5 extraction snapshot>` | refused, exit 1: *"this is a v5 extraction snapshot, but the instance-graph route requires snapshot v6. Recapture with `sysml-codegen snapshot`."* No traceback, no fallback, no output tree. |
| `generate --design-path-filter designs` | refused, exit 1, names the flag and why. No output tree. |
| `snapshot --design-path-filter designs` | refused, exit 1, own message. No snapshot file written. |
| `snapshot` output | `version: 6`, no `snapshot_format_version`; round-trips into `generate --from-snapshot` to the same package. |

**Escape-hatch hunt (beyond the pinned residual).** I looked for a public path to legacy
construction that the module's pins would miss:

- **Environment variables:** `grep -rn "os.environ\|getenv" src/` → **zero hits in the whole
  production tree.** No route can be selected by environment. (The test that claims this measures
  something else — finding 3.)
- **Console scripts:** `pyproject.toml:38-39` declares exactly one, `sysml-codegen = sysml_codegen.cli:main`.
- **Subcommands:** exactly four (`generate`, `snapshot`, `seal`, `install-commands`), which is what
  the flag-surface test enumerates. `cmd_seal` is graph-free and constructs nothing.
- **Config fields:** `GenerationConfig` has ten fields, pinned by value; none names an implementation.
- **Import-time side channels:** `sysml_codegen/__init__.py` exports nothing but `__version__`;
  there is no top-level re-export of a builder.
- **Callers of the legacy builders anywhere in `src/`:** only `snapshot/capture.py` (the v5
  capture, unreachable from any subcommand) and `orchestration/__init__.py`'s re-export. Both fall
  inside the accepted residual family, and `pipeline_builder` appears by name in the pinned
  residual set of `test_the_generation_half_still_reaches_v5_modules_and_that_residual_is_pinned`.
- `tests/helpers/legacy_route.py` has a `python -m` command line, but `tests/` is not in the wheel
  (`[tool.hatch.build.targets.wheel] packages = ["src/sysml_codegen"]`), so it is not a shipped surface.

**Nothing beyond the pinned residual was found.** The legacy production owners are byte-unchanged:
`git diff 0a812af 430e26a` over `pipeline_builder.py`, `snapshot_context.py`, `snapshot/loader.py`,
`snapshot/graph_rebuild.py` and `snapshot/capture.py` is empty.

One genuine loss of defensive code, verified safe: the public route no longer calls
`assert_snapshot_certifiable`. That guard is v5-only — a v5 snapshot could be captured without
lowered constraints, and the v6 envelope has no such mode because the catalog is projected from
the instance graph. Structurally sound; the leftover handler is finding 5.

## 2. The 116-node reclassification is honest

Verified by **node-id diff**, not by counts. Full collection (`-m ""`, so deselected nodes are
included) at `0a812af` in a forced-PYTHONPATH worktree vs HEAD:

- old: **3625** node ids, new: **3643**.
- **Removed: exactly one** — `test_shipped_cli_and_capture_remain_on_the_legacy_black_box_route`,
  which reappears as `test_the_shipped_cli_is_on_the_exact_route_and_the_legacy_owners_are_unreachable`
  in the same module. That is the documented inversion.
- **Added: 19** — the 18 nodes of `test_public_authority_switch.py` plus the renamed node.
- Zero nodes deleted, zero added `xfail`/`skipif`/`pytest.skip` in the diff (`git show 430e26a --
  tests/ | grep '^+.*xfail|skipif|skip'` → empty).

Assertion accounting rather than node accounting: the test diff **removes 35 assert lines and adds
86**. Every removed assertion I traced is either a route call (`run_codegen` → the legacy adapter),
the two updated `--design-path-filter` message assertions, the `graph.modules` source pin, or the
inverted import-boundary pins — except one that was dropped without a disposition (finding 4).

**Spot-check, 14 of the 16 repointed modules** (the other two are `test_snapshot_generation.py`,
which keeps a real subprocess, and `test_fusion_tea_acceptance.py`, discharged onto the exact
route). For each I confirmed: the specimen named in its responsibility row is what the module
actually loads; the module still calls the legacy adapter at live call sites; and the assertions
are still behavioural. Examples: `test_costed_component_e2e.py` still carries 35 assertions
including `agg_count == 20` and the multiplicity-parameter set — not reduced to a smoke call;
`test_full_pipeline.py` keeps ten legacy call sites on `chain_spike_model` (ledger row 7);
`test_fingerprint_stability.py` and `test_snapshot_generation.py` keep real subprocesses where
byte-identity and licence-free generation require them.

Every one of the 16 rows names a Gate 4C owner obligation. **The Gate 4B blocking language is in
the plan** at `plan.md:717-726`: *"Gate 4B may not delete a legacy production owner while any row
that owner serves still lacks its exact-route replacement"*, with `replacement_is_green(row)`
defined so absence scanning and a still-passing legacy node cannot satisfy it. It lives in the
Gate 4C block; Gate 4B's own bullet list (`plan.md:706-713`) does not cross-reference it
(finding 6, informational).

## 3. Package-diff classification, re-run independently

I re-ran the whole comparison myself with my own script (generate twice into clean trees, `rglob`
over both, byte compare). **Every count in `evidence/3e-package-comparison.md` reproduces exactly**
— files exact/legacy, exact-only, legacy-only, per fixture, all 14. `sample_model` is
byte-identical between routes. `constraint_inline` and `constraint_non_numerical` are refused
identically by both routes (0 files each side).

Adversarial sampling of the diffs the notes discuss least (`wi014_toy`, `retype_model`,
`deep_cross_scope_probe`, `shadowed_reference`) found no *unexplained* hunk — but it did find that
the "five named mechanisms" summary does not cover every hunk (finding 2). `wi014_toy` renames
entry-point keys from definition-scoped to occurrence-scoped
(`toy_plant__Toy_Plant__plant_budget` → `toy_plant__demo_plant__plant_budget`); `retype_model`
does the same and adds a channel. Both are covered by their cited ledger rows (row 37: *"source
keys now use concrete occurrences and modeled attributes"*; row 26), so the per-fixture
classification holds — the summary list is what is incomplete.

**fusion_tea, checked against the four things the brief names:**

- **Module and schema class names equal.** `diff` of the two `modules/` trees is empty; the only
  `schemas/` differences are the two exact-only group files and the legacy-only `system_design`.
- **No group renamed.** `hif_driver_params`, `hif_plant_params`, `ife_plant_params` all survive.
- **Hand values unchanged.** Every literal in the table is present on both sides; `gain=80.0`,
  `thermal_efficiency=0.43`, `availability=0.9`, threshold `10.0`, etc.
- **The per-consumer collapse is exactly the ratified single-source semantics, checked in the
  emitted YAML and not only in the JSON keys.** In `pipelines/pipeline.yaml`:
  `hif_plant_params.hif_plant_pkg__hif_plant__gain` feeds **three** consumers (`recirc_calc:59`,
  `lcoe_calc:103`, `viability:115`); `…__thermal_efficiency` feeds `recirc_calc` and `lcoe_calc`;
  `…__availability` feeds `meier_coe_calc` and `lcoe_calc`. One key per modelled attribute, every
  consumer wired to it. Legacy published the same values under two or three separate keys.

One shipped key rename in that package is not in the evidence file's fusion_tea section and is not
one of the five mechanisms — finding 1.

**Row 36 / `unresolvable_attr_probe` reproduced.** The exact route reaches generation and the
generator's module-class collision guard refuses, with the message the ledger quotes verbatim. The
corpus row genuinely did not move (below), and the recorded classification is accurate. Two details
the record omits are finding 5.

**Corpus, re-run by me over all 37 paths:** exact **15 graphs / 22 errors**, all 22
`ElaborationError`; legacy 36 graphs / 1 `CodeGenerationError`. Per-fixture outcome strings equal
the amended ledger's — **zero rows moved**, verified as an exact per-row comparison, not a total.

## 4. New fixture and the two specimens

- The committed `tests/fixtures/fusion_tea/instance_graph_snapshot.json` is `version: 6`. I copied
  it alone into an empty directory (no model tree) and generated: **succeeds, and succeeds with
  the licence environment variable unset** — 65 files, `gain=80.0`, `thermal_efficiency=0.43`.
  Relocation and licence-freedom both hold.
- It drives the oracle: `tests/runtime/test_fusion_tea_acceptance.py` generates from it through the
  shipped `run_codegen` and asserts the hand LCOE `216.55528392479388` at `gain=100`, keyed on
  `_GAIN_EP_KEY = "hif_plant_pkg__hif_plant__gain"`. 4 passed.
- `tests/fixtures/fusion_tea/README.md` marks it plainly: *"The v6 file is a test fixture, not an
  accepted corpus recapture,"* with the regeneration command and Phase 5 ownership stated.
- **The two fail-before-mutate specimens are not vacuous.** I broke the guard experimentally, in
  two independent ways: (A) `_clear_output_directory` moved ahead of context construction in
  `run_codegen`; (B) `_reconcile_params_coverage` moved after `_setup_output_directories`. Under
  the mutation **both specimens fail**; with the file restored, all 18 nodes pass. So they do reach
  the guard on the exact route through public `generate`, and they pin the ordering rather than
  the fixture. The mutation was reverted and the working tree verified identical to `HEAD`.
- **The forged-identity retirement is a measurement, not an argument.** The claim is that the
  forged `IdentityFact` acts on `analysis/constraint_lowering.py`, which the exact construction
  closure does not import. `test_the_construction_path_reaches_no_legacy_authority_even_transitively`
  computes the closure by AST walk from `exact_pipeline_context` and asserts that module's absence;
  it passes, and my own read of the closure agrees. The old specimen is repointed at the legacy
  route, not deleted.

## 5. After-battery, re-run

| Gate | Recorded | Measured by me |
|---|---|---|
| Full licensed codegen suite | 3557 / 47 / 38 | **3557 passed, 47 skipped, 38 deselected**, exit 0, zero licence-skip lines |
| Delta vs `0a812af` | +18, all new | **+18 passed**, node-id diff = 18 new nodes + 1 rename, 0 deletions |
| Execution lane | 38 passed, real TEAx | **38 passed**, zero skipped, through the switched `run_codegen`; LCOE asserted against `fusion_tea_arithmetic.RUN_C_LCOE = 270.1211779380445` on live and relocated-v6 |
| Corpus | 15/22, zero rows moved | **15 graphs / 22 ElaborationError, zero rows moved**, exact multisets |
| agentic-mbse suite | 1825 / 1 / 5, unchanged | **1825 passed, 1 skipped, 5 deselected** from the paired worktree at `cc6c7a7`, clean |
| `ruff check src` | byte-identical (16) | **byte-identical** — diffed the two outputs with paths normalised, not the counts |
| `mypy src` | 71 errors in 17 files | **71 errors in 17 files** |
| `git diff --check` | clean | clean |
| Declared paths | "changed paths equal the declared set" | 41 changed paths; 38 map to the declared set, 3 do not (finding 6a) |
| agentic-mbse | untouched at `cc6c7a7` | worktree `/home/reid/1cfe/agentic-mbse-item7-rebuild` at `cc6c7a7…`, `git status` clean |

## 6. Checklist reconciliation

Spot-checked the 3A–3D pointers. All four audit records exist with the verdicts the checklist
claims: 3A **FINDINGS** with exactly three (F1 HIGH, F2 MEDIUM, F3 LOW), 3B **CERTIFY** with 7, 3C
**CERTIFY** with 4, 3D **CERTIFY** with 5. The 3D mypy exception is accurate and is the one place
the checklist tells on itself: `audit-3d.md:246` records Finding 1 — *"the mypy gate is recorded as
identical but is not"* (72 in 18, not 71 in 17) — and the checklist box at `plan.md:599-602` is
ticked against the follow-up commit rather than against `848628b`, saying so in words. Worth
noting precisely: the item is **ticked with a written exception**, not left unticked. Given the
follow-up landed and I measure 71/17 at HEAD, that is the honest state.

---

## Findings

### F1 — Medium — a shipped fusion_tea input key is renamed and the evidence file does not list it

`.project/active/cutover-recovery/evidence/3e-package-comparison.md:60-99` (the fusion_tea
section) enumerates what changed in the customer package and is explicitly the table the Phase 5
owner is meant to read *instead of a summary*. It lists the per-consumer collapse, the two
exact-only groups and the legacy-only `system_design`. It does not list this:

```
legacy  inputs/system_design.json    : hif_plant_pkg__hif_plant__viability__81ddf10fb1d1749b__threshold = 10.0
exact   inputs/ife_plant_params.json : hif_plant_pkg__hif_plant__viability__threshold                  = 10.0
```

The group move is mechanism 4 (`system_design` is legacy-only, so the key had to land somewhere).
The **key name** change — the constraint's disambiguating id `81ddf10fb1d1749b` is dropped from
the entry-point key, while the same id is retained in the module id and the output channel
(`…viability__81ddf10fb1d1749b__evaluation`, both routes) — is neither mechanism 2 nor any of the
other four, and no diff-ledger row covers it (fusion_tea is row 15, which is about self-bindings).
The value is unchanged and the wiring is correct, so nothing is broken; but this is a
customer-visible rename of a shipped input key inside the largest customer-visible change of the
recovery, and it is invisible in the artifact that exists to make that change visible.

It is also worth a second look on its own merits: dropping the disambiguator means two constraint
usages with the same name under one owner would mint the same `…__threshold` key. I found no such
model in the corpus and no measured failure, so this is a question for the owner packet, not a
defect claim.

**Resolution:** add the row to the fusion_tea table with its mechanism, and flag the
disambiguator-drop to the Phase 5 owner packet with the rest.

### F2 — Low — "every difference reduces to five named mechanisms" is not true as written

`evidence/3e-package-comparison.md:30-47` and `plan.md:2236-2238`. At least one further mechanism
appears in the measured diffs: entry-point keys move from **definition-scoped to occurrence-scoped
naming** (`toy_plant__Toy_Plant__plant_budget` → `toy_plant__demo_plant__plant_budget` on
`wi014_toy`; the same shape plus a new channel on `retype_model`). Both are correctly classified
per fixture — ledger row 37 says it in words, row 26 covers the retype case — so the rule-10
"unexplained: zero" claim survives. The summary sentence does not.

**Resolution:** name the sixth mechanism (occurrence-scoped key naming, ledger rows 26/37) in the
mechanism list, or reword the claim to "every difference maps to a ratified ledger row or a
recorded slice mechanism", which is what the per-fixture table actually shows.

### F3 — Low — the "no environment variable selects a route" pin measures the test process, not the product

`tests/conformance/test_public_authority_switch.py:246`:

```python
assert [name for name in os.environ if "SYSML_CODEGEN" in name.upper()] == []
```

This asserts that the *pytest process* has no such variable set. It would fail spuriously for an
operator who exports one for unrelated reasons, and — the part that matters — it would still pass
if `run_codegen` started reading `SYSML_CODEGEN_ROUTE` tomorrow. The plan's claim at
`plan.md:2110` ("no `SYSML_CODEGEN*` environment variable is read") is stronger than the test
behind it. I verified the claim independently: `grep -rn "os.environ\|getenv" src/` returns
nothing in the entire production tree, so the *product* statement is true today.

**Resolution:** pin the source, not the ambient environment — assert that no module in the
construction closure references `os.environ`/`os.getenv`, the same AST-walk style the neighbouring
import pins already use.

### F4 — Low — an import-boundary assertion was dropped without a disposition row

`tests/unit/test_elaboration_import_boundaries.py:282-306`. The inverted test correctly flips the
CLI's two assertions and records the old expectation in its docstring. But it also stops reading
`orchestration/__init__.py` entirely, dropping
`assert "build_elaborated_pipeline" not in public_orchestration` — a pin that kept the exact
route's elaborator entry out of the public orchestration API. That symbol still exists
(`orchestration/elaborated_pipeline.py:35`), and the property still holds (I checked
`orchestration/__init__.py`), but nothing fails now if it is re-exported. The commit message's
"nothing was deleted" is about nodes, and the disposition table's row for this module says
"inverted, not deleted" without mentioning the dropped third assertion.

**Resolution:** restore that assertion in the inverted test, or record it as a deliberate drop with
its reason.

### F5 — Low — two residues of the v5 route survive inside the public writer, unnamed

Both in `src/sysml_codegen/cli/__init__.py`, both dead:

- `:1061` imports `GrandfatheredSnapshotError` and `:1139` catches it inside
  `_generate_package_from_graph`. The only raiser is `assert_snapshot_certifiable`
  (`snapshot/__init__.py:72`), which the public route no longer calls and which the legacy test
  adapter calls *before* this function. The handler is unreachable on both paths.
- The `unresolvable_attr_probe` refusal (row 36) is not typed. The guard raises a bare `ValueError`
  (`generation/registry.py:146`), which lands in the bottom `except Exception` at `:1151` and is
  reported to the operator as **"Unexpected error"** with a traceback — the shape the v5 refusal
  work in this slice deliberately eliminated elsewhere. It also fires inside `_generate_modules`,
  after the output tree was cleared, so it leaves a **half-written package** (I measured 34 files,
  no contracts, no seal). Neither detail is in the ledger row or the evidence file, both of which
  say only "generation refuses".

Neither is a regression the slice introduced — the guard and its handling predate it — but the
switch is what made this path reachable from public `generate`, so it is now product behaviour.

**Resolution:** Gate 4A ledger rows for the dead import/handler; add the two measured details
(untyped, partial tree) to row 36 and the Phase 5 owner packet.

### F6 — Informational — two record-keeping inaccuracies

- **(a)** `plan.md:2077-2083` declares the path set by reference to the tables and claims "Actual
  changed paths equal that set." Three of the 41 changed paths are not nameable from any table:
  `tests/conformance/test_snapshot_v6_envelope.py` (a message-match update following the
  `envelope.py` change), `tests/execution/test_fusion_tea_real_teax.py` and
  `tests/execution/test_fusion_tea_mutation_teax.py` (helper-rename call sites; the six-further-
  modules sentence at `plan.md:2186-2190` names only `real_teax.py` and `test_constraint_execution.py`
  from that directory). All three are mechanical; I read every hunk. The same sentence says "six
  further modules" and then names eight.
- **(b)** The Gate 4B hard gate is written into Gate 4C (`plan.md:717-726`) and is correctly and
  forcefully worded there. Gate 4B's own bullets (`plan.md:706-713`) do not reference it, so a
  Phase 4 agent working down Gate 4B's list will not encounter the constraint until it reaches
  Gate 4C, which is *after* the deletions that constraint governs.

**Resolution:** (a) extend the declared path list to the three modules and fix the count word;
(b) add a one-line cross-reference in Gate 4B's first bullet.

---

## Certification

**CERTIFY.** Nothing here blocks Phase 4 planning. The three claims Phase 4 depends on are true
under independent measurement:

1. **One public authority.** Every public surface — console script, four subcommands, `cli.__all__`,
   `GenerationConfig`, environment — constructs through the exact route or refuses. The legacy
   owners are byte-unchanged and reachable only through the accepted, pinned import residual and
   `orchestration/__init__`'s re-export, both already Gate 4A inputs.
2. **The reclassification is honest.** Node-id diff: one rename, eighteen additions, zero
   deletions, zero silencing. Sixteen responsibility rows, each with a Gate 4C owner and a hard
   gate on 4B.
3. **Every shipped-package difference is classified.** All 14 fixture comparisons reproduce
   exactly; zero unexplained hunks; the fusion_tea collapse is the ratified single-source
   semantics, confirmed in the emitted pipeline YAML on the C25 and C2 axes.

The Medium finding is an evidence-completeness defect in the artifact the owner will read, not a
behaviour defect. The four Low findings are one weak pin, one dropped assertion, dead v5 residue,
and record-keeping. None of them changes what the product does.

## Not checked

Stated plainly, because Phase 4 starts from this record.

- **The full suite at `0a812af` was not re-run.** I collected node ids there but ran only HEAD.
  The `+18` delta is verified structurally (node-id diff) and arithmetically (3557 = 3539 + 18 with
  skips and deselections unchanged); the 3539 baseline itself is inherited from the 3D record.
- **The 47 skipped nodes were not enumerated against the old run.** No node moved passed→skipped
  (the arithmetic closes), but I did not compare the two skip *sets*.
- **The exact route's internals were not audited** — elaboration, projection, receipt binding,
  v6 envelope semantics. Those are Slices 3A–3D's subject and their audits'.
- **The diff-ledger's ratified classifications were not re-litigated.** I verified that rows 12, 26,
  36 and 37 say what the evidence cites them as saying; whether `expected-fix` is the right call is
  the owner's ruling, already made.
- **The hand-arithmetic transcription in `fusion_tea_arithmetic.py` was not re-derived** from the
  SysML equations. I verified the execution lane asserts against it and that the value is unchanged
  across the switch.
- **TEAx internals** (`ProvisionalPackageLoader`, `execute_pipeline`) were treated as a trusted
  dependency.
- **Mutation testing was applied only to the two fail-before-mutate specimens**, not to the
  repointed modules generally. For those I checked assertion content by reading, not by mutation.
- **`docs/` was not examined at all** — Gate 4D's scope, and the documentation is known-stale.
- **Only 14 of the 16 repointed modules were spot-checked** for specimen/row agreement (the two
  omitted are `test_snapshot_generation.py` and the discharged `test_fusion_tea_acceptance.py`,
  both of which I exercised in other ways).
- **The `unresolvable_attr_probe` collision was not investigated for a fix.** I reproduced it and
  measured its two undocumented consequences; whether the fixture or the aliasing rule should
  change is Phase 5 owner territory.
