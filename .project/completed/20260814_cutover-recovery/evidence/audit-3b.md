# Audit — Slice 3B: Defensive context and exact public projection

**Verdict:** CERTIFY (nothing blocks 3C) — with 7 findings, all Low/Medium, none blocking.
**Audited:** 2026-08-11
**Auditor:** independent agent, fresh session, did not implement the slice
**Branch / commit:** `item7-rebuild` @ `d91431b` (+ OID record `3f13f2f`); worktree clean apart
from the untracked audit brief
**Paired repo:** `agentic-mbse-item7-rebuild` clean at `5088b417c9e5453271291d46cd5fb23fc0579b1e`,
as claimed
**Environment:** venv `/home/reid/1cfe/item7-rebuild-venv`; import paths re-asserted before any
measurement (F2 trap) — `sysml_codegen` → this worktree's `src`, `agentic_mbse` →
`agentic-mbse-item7-rebuild/src`, `simkit` → `teax/packages/teax-simkit`, `syside`/`jinja2` → venv.
No import resolves into an original or forensic path. Licensed run: **zero** `no live syside
license` lines. Scratch under `/tmp/claude-audit3b/`.

---

## The Point

Item 7's cutover was implemented as one monolithic commit that deleted the shipped route while
replacing it, so nothing could be reviewed, reverted, or trusted. The recovery rebuilds the exact
route as vertical slices while the legacy builder stays the shipped authority, and each slice must
prove itself on public behavior before any legacy owner is retired.

Slice 3B's share of that: give the exact route a public construction that cannot be mutated after
it is built, make its projection into the generation DTOs exact enough that a package built from a
relocated v6 snapshot matches one built live, and fix the group-identity defect Slice 3A pinned —
without turning the exact route into a second shipped authority.

## Summary

The slice delivers what it claims. I re-measured every headline number myself rather than reading
the implementer's notes, and the substantive ones all reproduce: the full licensed suite is
3519/47/18 with a collection delta of exactly +46 (one renamed test, zero Item 6 tests removed),
the live and relocated-v6 generated packages differ only in `SysML Source:` comments across an
identical 49-file set, the aggregation package really carries `+ 5.0`, `d38_caret` is genuinely
pre-existing, the three rejected `orchestration/` files are byte-unchanged, and the changed path
set equals the declared set.

The receipt is real. Under my own attack — not the implementer's tests — a projector that returns
a graph different from the sealed one is refused. That is precisely the defect the forensic
candidate's projection-receipt test had, and this implementation does not have it.

The findings are honesty-and-hygiene items, not defects in the delivered behavior. The one worth
acting on before 3E is a second exact-vs-legacy divergence that the evidence file records but the
plan's residual list and the test suite do not (F3).

## Product judgment

**Is this the right piece of work?** Yes. The product surface it defends is the customer's
generated package: a package built from a relocated snapshot must be the package built live. Before
this slice it was not — a snapshot-built package shipped `inputs/root_0_params.json` and a
`Root0Params` schema class, named after a staging directory. I regenerated both packages
independently and confirmed the fix at the product surface, not just in the graph.

The dual-authority risk the plan bans before 3E is respected: `grep` finds **no production caller**
of `exact_pipeline_context` (only a docstring reference from `elaborated_pipeline.py:44`), and the
new generated-package test drives the generation helpers directly rather than adding a second CLI
flag. The shipped legacy CLI is unmoved — I ran it: 48 files, `inputs/hif_plant_params.json`
present, `hif_driver__HIF_Driver__efficiency = 0.35`.

No product-drift smell fired. Specifically checked: the route-equality test's masking got *smaller*,
not larger (it now masks only module `source_file`), so the suite is not green because each
assertion is scoped to a different route.

**Product-lens ledger:** not run as a subagent — the stage brief replaces the standard audit rubric
with its own verify list and verdict vocabulary, and no `product-lens.md` ledger exists for this
item. The judgment above was derived directly from the durable product statements (`CLAUDE.md`,
`docs/architecture/reference/27-snapshot-generation.md`) and the regenerated packages.

---

## What I verified, and how

### 1. Receipt-bound immutability is real — CONFIRMED

I wrote an independent attack script (`/tmp/claude-audit3b/attack.py`) rather than trusting
`test_exact_pipeline_context.py`. Results:

| attack | outcome |
|---|---|
| `pickle.dumps` at protocols 0, 1, 2, 5, HIGHEST | refused (`TypeError`) |
| `copy.copy` / `copy.deepcopy` | refused |
| `setattr` public / private / new attribute; `delattr` | refused |
| `vars()`, `__dict__`, `__class__` reassignment (both plain and `object.__setattr__`) | refused / absent |
| mutate returned `ComputationGraph` (`modules.clear()`) | next read unaffected (24 modules) |
| mutate a returned `ParameterGroup` in place (rename + clear parameters) | next read unaffected |
| `receipt` field assignment | refused (`FrozenInstanceError`) |
| swap `_instance_bytes` via `object.__setattr__` | refused — receipt detects |
| **monkeypatch `project` to drop a module, then read** | **refused** — "the projected computation graph disagrees with the receipt" |
| `object.__new__(ExactPipelineContext)` and a subclass bypassing `__new__` | refused with a named error, not a bare `AttributeError` |
| mutate the source `InstanceGraph` after `_seal` (`graph.calcs.clear()`) | context unaffected — 24 modules before and after |

The monkeypatched-projector case is the one that matters. The receipt is minted at build time over
independently-derived bytes and re-checked against a fresh re-derivation on every read, so it
detects a genuine graph/context disagreement. It is **not** comparing a copy to itself.

Two design details I checked rather than assumed: `_computation_digest` covers all six
`ComputationGraph` fields including the two `exclude=True` ones (`fallback_entry_points`,
`constraint_catalog`), so nothing semantic is outside the receipt; and `_seal` projects from the
*decoded* bytes, not the caller's object, so an encode/decode asymmetry cannot mint a receipt that
every later read fails against.

### 2. Option-C measurement claims — CONFIRMED, one summary imprecision

I re-measured group identity across all 77 fixture directories on three configurations: exact route
at `a7c13a6` (detached worktree, `PYTHONPATH` verified to resolve to the old `src`), exact route at
`d91431b`, and legacy route at `d91431b`.

**(a) Exactly one projecting fixture changed identity.** Confirmed. 33 fixtures project entry-point
groups; exactly one — `elab_constraint_formal_identity` — changed `(name, class_name)`, from
`elab_constraint_formal_identity_params` to `constraint_formal_identity_params`. The other 32
changed only the recorded `source_file` label (absolute path → identity token), which the plan
discloses separately as a deliberate rendering choice. The plan's wording ("keeps the exact name and
class it had") is precise and true.

I confirmed that label reaches generated bytes in exactly one place. `group.source_file` has two
consumers: `generation/entry_point.py:226` (`"Parameters from {label}."` in the schema docstring)
and `analysis/constraint_lowering.py:1449` (an identity tuple, `str()`-ed). Generated proof: the
exact route emits `"""Parameters from library.` where the legacy route emits
`"""Parameters from hif_driver.sysml.` — a docstring-only divergence, correctly carried to 3E.

**(b) Stem-named fixtures match legacy except `d38_caret`.** Substantially confirmed, with one
qualification (F3). Ten stem-named fixtures were compared in `evidence/3b-old-new-comparison.md`;
my sweep reproduces every row. Eight match (two of them vacuously, with no groups on either side;
one after setting aside the legacy-only `system_design` hierarchy group). `d38_caret` mismatches.
`unresolvable_attr_probe` also mismatches — the evidence table records it honestly, but the plan's
prose summary ("nine compared, eight match") does not carry it into the residual list.

**(c) Byte-equal group payloads across the three routes, asserted strictly.** Confirmed. The
diff of `tests/conformance/test_snapshot_v6_routes.py` shows `_masked` lost five masking rules and
gained none: it now masks only module `source_file`. Group name, class, label, `param_group` on
module inputs, and `param_group` on parameters are all compared unmasked, and
`group_source_files` was *added* to the by-value assertion set. This is a strictly stronger
comparison than at `a7c13a6`. I re-ran the module; it passes.

### 3. The generated-package comparison is honest — CONFIRMED

I regenerated both packages myself (`/tmp/claude-audit3b/regen.py`, driving the same shipped
generation helpers) and ran `diff -r` over the trees:

- File sets identical: 49 files each, `diff` of the sorted file lists is empty.
- 16 files differ. **Every** differing hunk is a `SysML Source:` line
  (`///home/reid/.../model.sysml:205` live vs `root-0/model.sysml:205` from the snapshot). No other
  line differs anywhere in the tree.
- `inputs/source_identity_mixed_consumers_params.json` and every `schemas/` file are byte-identical
  across routes. No `root_0` or `root-0` in any filename or schema class.

The test enumerates rather than allowlists: `test_the_two_packages_differ_only_in_provenance_comments`
computes the differing set, then asserts that every line unique to either side contains
`SysML Source:` or `sysml_source`. No directory is exempted. (It does not pin *which* files differ —
see F6.)

**B37-01 at the product surface:** confirmed independently. I generated an `agg_literal_probe`
package on both routes. `handwritten/.../total_cost_impl.py:30` reads
`return ((inputs.cost_0 + inputs.cost_1 + inputs.cost_2) + 5.0)`, and
`inputs/library_params.json` carries three separate member entries at `10.0` each — 3 × 10.0 + 5.0
= 35.0, matching the model. The literal operand is intact and the three members did not collapse.

### 4. `d38_caret` pin honesty — CONFIRMED, characterization is narrow (F5)

Pre-existing: I ran the new `test_exact_group_identity.py` against `a7c13a6` production code.
`test_the_known_exact_versus_legacy_declaration_site_divergence` **passes there** — the divergence
is byte-identical before and after the slice. My fixture sweep agrees: exact said `library_params`
at `a7c13a6` and says `library_params` now.

Option C neither caused nor could fix it: `tests/fixtures/d38_caret/` contains `design.sysml` and
`library.sysml` and no `model.sysml`, so the changed fallback branch never executes for it.

The pin encodes a defect-to-disposition, not a guarantee: it asserts both routes' values by name,
and its docstring says the divergence "needs a disposition before the Slice 3E authority switch,
where it would change a shipped input filename." The no-second-stop judgment holds — rule 10's
"unexplained product diff" does not apply to a pre-existing, measured, named, and test-pinned
difference in an unshipped route.

### 5. Rejected forensic material did not leak — CONFIRMED

- `orchestration/{pipeline_context,pipeline_builder,snapshot_context}.py` are **byte-unchanged**
  vs `a7c13a6` (`git diff --quiet` clean on each).
- All 18 `PipelineContext` fields survive at HEAD, including every one the forensic hunk deleted:
  `calc_defs`, `group_deriver`, `backtracking_result`, `output_registry`, `constraint_facts`,
  `hierarchy_data`, `aggregation_expressions`, `channel_aliases`, `concrete_constraints`,
  `part_occurrences`, `computed_attributes`, `compilation_results`, `constraint_lowering_mode`.
- `build_pipeline_context_from_snapshot` (the shipped v5 `--from-snapshot` route) is untouched.

I diffed the new `exact_pipeline_context.py` against the forensic `pipeline_context.py` by reading
both. It is a **port of the idea into a new file**, not a rename-import of the rejected hunks: it
adds nothing on top of a shipped authority and removes nothing. Concrete differences from the
forensic version — `_VerifiedProjectionLease` dropped (a 3D/3E sealing concern), `include_all`
dropped, `CodeGenerationError` *imported from* the legacy module rather than redefined beside it
(so there is one error type, not two), and an explicit named refusal when a context is reached
without sealed authority. The disposition table's "Reimplement as an addition" is a fair label; the
structure is recognizably descended from the forensic file, which the notes do not hide.

### 6. Gates re-run — ALL CONFIRMED

| gate | claimed | measured by me |
|---|---|---|
| Full licensed suite | 3519 / 47 / 18, zero license skips | **3519 passed, 47 skipped, 18 deselected**, exit 0, `grep -c "no live syside license"` = **0** |
| Collection delta | exactly +46, no Item 6 test removed | node-ID diff vs `a7c13a6`: **47 added, 1 removed** (the renamed routes test) = net **+46**. Added: 15 context, 12 selection, 12 group identity, 4 package, 3 aggregation, 1 renamed routes test. No other removal. |
| Execution lane | 18 passed | **18 passed** |
| ruff `src` | byte-identical to baseline | `diff` of old vs new output: **identical**. New test modules lint clean. |
| mypy `src` | error set identical | **71 errors in 17 files** both sides, sorted error lines **identical**; 84 → 85 files checked |
| `git diff --check` | clean | clean |
| Changed paths ⊆ declared set | equal | 12 paths, **exactly** the declared set (10 declared + the 2 named mid-slice deviations). No docs, spikes, probes, snapshots, or baselines touched. |
| Legacy CLI smoke | 48 files, `hif_plant_params.json`, `0.35` | **48 files**, `inputs/hif_plant_params.json` present, `hif_driver__HIF_Driver__efficiency: 0.35` |

### 7. Test quality — meets the 3A bar, one imprecision

- **Independently derived expectations.** `test_exact_target_selection.py:28` walks the *complete*
  graph's wiring to compute the expected closure, then requires the selector to match it — it does
  not ask the selector what it selected. `test_exact_projection_aggregation.py` reads 10.0, 3, and
  5.0 off the fixture source by hand and `eval`s the generated expression against them.
  `test_exact_group_identity.py:71` reads `package ElabMatrixC14` out of the `.sysml` file before
  asserting the rendered name.
- **No monkeypatching away the subject.** None of the five new modules patches production code.
- **No self-comparison** in the selection, mutation, group-identity, or package tests.
- One line is closer to tautology than the module docstring admits — see F7.

---

## Findings

### F1 — Low, code integrity. A dangling-alias guard became unreachable.
`src/sysml_codegen/elaboration/project.py:921`

The new `selected_outputs` filter sits *above* the channel lookup:

```python
if node.alias_target.target not in selected_outputs:   # :921
    continue
channel = self.output_channels.get(node.alias_target.target)
if channel is None:
    _fail(ElaborationCode.SI_EDGE_DANGLING, "... targets an absent producer")   # :925
```

In the complete projection `selected_outputs` is `set(self.output_channels)`, so the filter's
condition is *identical* to `channel is None`. The `_fail` at :925 can no longer execute on the
complete path — an alias pointing at an absent producer is now silently dropped where it used to
raise. This is defence-in-depth only (`require_projectable()` → `validate()` → `_validate_edge`
already refuses a dangling `ProducerRef` at `graph.py:706`), so no real graph reaches it. But a
loud refusal was replaced by a silent skip, which is the failure-honesty pattern the plan's own
code-integrity bar flags.

*Resolution:* move the `selected_outputs` filter below the `channel is None` check, so the guard
still fires in the complete projection and the filter still prunes in the selected one.

### F2 — Low, dead state. `_targets` is stored, never read, never verified.
`src/sysml_codegen/orchestration/exact_pipeline_context.py:150`, `:236`

`_seal` writes `_targets` into the slot, but `_verified_projection` projects with
`receipt.targets` and never looks at `_targets`. I confirmed by tampering: after
`object.__setattr__(ctx, "_targets", ("bogus",))` the read still succeeds and returns all 24
modules. The field is inert — a reader of `__slots__` would reasonably assume it is authoritative.

*Resolution:* delete `_targets`, or check `self._targets != receipt.targets` alongside the
projector-semantics check so the slot means what it looks like it means.

### F3 — Medium, disposition gap. A second exact-vs-legacy divergence is recorded but not carried.
`.project/active/cutover-recovery/evidence/3b-old-new-comparison.md:37`; plan.md:1243

`unresolvable_attr_probe` is a stem-named fixture where the two routes ship different packages:

```
exact  : design_params / DesignParams  — 9 parameters
legacy : system_design / SystemDesign  — 1 parameter (…design_derived_instance__my_calc__x)
```

The evidence table names it honestly ("legacy emits only the hierarchy group"). But the plan's
summary says "nine compared, eight match" and names `d38_caret` as *the* residual, which reads as
if this one matched. It also has no pinning test, so unlike `d38_caret` it can move unnoticed. At
the 3E authority switch it changes a shipped input filename for a model of this shape — the same
consequence the plan gives `d38_caret`.

*Resolution:* correct the plan's count to ten compared / eight matching, add
`unresolvable_attr_probe` to the named residual list beside `d38_caret`, and pin it by value in
`test_exact_group_identity.py`. (Whether it is a naming question or an entry-point-classification
question is a 3E disposition, not a 3B fix.)

### F4 — Low, factual accuracy. The red-state claim is wrong for one module.
`plan.md:1290`

"All five new modules failed to collect at `a7c13a6` (`exact_pipeline_context` and
`elaborate_model_paths` do not exist there)." `test_exact_group_identity.py` imports only
`build_elaborated_pipeline` and `build_pipeline_context`, both of which exist at `a7c13a6`. I ran
it against the old production code: it collects and reports **4 failed, 8 passed**.

Red was genuinely demonstrated (the four identity assertions fail), and the eight that pass are the
ones that *should* pass — including the `d38_caret` pin and the stem-compatibility test, which is
useful independent evidence that the stem rule was untouched. Only the sentence is wrong.

*Resolution:* restate as "four modules failed to collect; the fifth collected with 4 failed / 8
passed," and note that the eight passing pre-existed by design.

### F5 — Low, characterization. The `d38_caret` pin is narrower than the measured divergence.
`tests/conformance/test_exact_group_identity.py:115`; `evidence/3b-old-new-comparison.md:47`

Both describe the divergence as purely "which file declares an entry point." Measured, the routes
also disagree on the entry-point *set*:

```
exact  library_params: 6 parameters (noop__x, pack__cell[0..3]__base_cost, pack__exponent)
legacy design_params : 1 parameter  (noop__x)
```

The shared parameter is indeed a declaration-site difference. The other five are a content
difference the pin does not capture, since it asserts group names only. The "no group-naming rule
can reconcile it" reasoning is still correct; the description is just incomplete, and a reader at
3E would size the disposition wrongly from it.

*Resolution:* add the parameter-set assertion to the pin and correct the two prose descriptions to
say the routes disagree on both the declaration site and the entry-point set.

### F6 — Low, test scope vs claim. The differing-file *set* is not pinned.
`tests/conformance/test_exact_route_generated_package.py:111`; plan.md:1197

The plan says "every differing file is named and checked." The test checks every differing file's
lines but only asserts the set is non-empty (`assert differing`), so a file that newly starts
differing in provenance would pass unnoticed. I established the real set independently — 16 files
under `modules/` and `handwritten/`, all provenance-only — so the claim is *true today*, it is just
stronger than what the test enforces.

*Resolution:* assert the expected differing-file set explicitly, or soften the plan's wording to
"every differing file is checked."

### F7 — Low, near-tautology. One digest assertion cannot fail independently.
`tests/conformance/test_exact_pipeline_context.py:68`

`assert receipt.computation_digest == _expected_digest(context.computation_graph)` — but
`context.computation_graph` is only returned *after* production has verified that same equality.
The assertion can only fail if the test's local copy of the payload formula diverges from
production's, which makes it a field-coverage check on the digest, not a receipt check. The module
docstring's "Nothing is read back off the context and compared with itself" overstates this line.

The line above it (`receipt.instance_fingerprint` vs an independently elaborated and encoded graph)
*is* genuinely independent, and my monkeypatched-projector attack proves the receipt has teeth. So
this is a docstring-precision issue, not a hole in coverage.

*Resolution:* label the line as the field-coverage check it is, or derive the expected digest from
an independently elaborated graph rather than from the context's own read.

---

## Certification

Verified and marked: all five Slice 3B plan checkboxes are supported by evidence I reproduced
independently. Every gate in "Validation for every Phase 3 slice" re-ran green under my own hand.
The commit-gate row for 3B (`d91431b`, 3519/47/18, +46 all new, smoke PASS) is accurate as written.

**Nothing blocks Slice 3C.** F3 is the only finding with a 3E consequence, and it is a
disposition/pinning gap in an unshipped route, not a defect in delivered behavior. F1, F2, F5, F6
and F7 are hygiene. F4 is a documentation correction.

Rule-10 check: no premise conflict found. The slice's own rule-10 stop was resolved by the recorded
orchestrator ruling, the ruling's three measurement requirements were met, and the two rendering
choices that go beyond the ruling's literal wording (PascalCase-to-snake_case, `source_file` as a
token) are both disclosed in the plan with reasons and are both confirmed by measurement to be
what makes the identity route-invariant.

**Not checked:**

- **Real TEAx execution** of the exact-route packages. Out of 3B scope (Slice 3D), and the
  execution lane I ran covers the legacy route only.
- **Semantic correctness of the 3519 passing tests.** I verified counts, node-ID identity against
  `a7c13a6`, and license-skip absence — not what each pre-existing test asserts.
- **Slice 3A's carried residuals** (offline source-referent re-labelling, the accepted
  `source_roots` limit). Inherited from `audit-3a.md` as certified; not re-litigated here.
- **`select()` beyond the corpus fixture.** Target selection was exercised on
  `source_identity_mixed_consumers` only, live route only. I read the closure walk and confirmed
  its logic, but did not measure selection across the fixture corpus or from a snapshot.
- **`_declaring_package`'s package-scoped failure branch.** Confirmed unreachable by the corpus (it
  needs a package-scoped entry point in a file named `model.sysml`); I did not construct a fixture
  to exercise the refusal.
- **`constraint_catalog` contents under selection.** `select()` carries the complete catalog
  unfiltered; I confirmed all admitted constraints ride along and the report aggregator is present,
  but did not verify the catalog's internal references against the reduced module set.
- **ruff/mypy over `tests/`** beyond linting the five new modules.
- **The forensic test material's own dispositions** (`test_cutover_projection_receipt.py`,
  `test_cutover_target_selection.py`, `test_elaboration_occurrence.py`) — I confirmed the new tests
  do not carry the projection-receipt self-comparison defect, but did not review those forensic
  files hunk by hunk.
