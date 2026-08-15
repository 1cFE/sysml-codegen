# Audit: Slice 3D — Fusion Tea customer vertical and real TEAx

**Verdict:** CERTIFY (5 findings — 1 Medium, 2 Low, 2 Informational; none blocking)
**Audited:** 2026-08-11
**Auditor:** independent (did not implement this slice)
**Branch:** `item7-rebuild`
**Commits:** sysml-codegen `848628b` (+ OID record `4d1a3ed`); agentic-mbse unchanged at `cc6c7a7`

---

## The Point

sysml-codegen turns a SysML v2 model into Python a simulation framework can actually run. The
recovery plan is rebuilding the Item 7 cutover as vertical slices after the original attempt was
lost. Slice 3D is the evidence gate the original attempt never reached: the customer model — Fusion
Tea, a heavy-ion IFE plant economics model — has to go end to end on the exact route and then
actually execute inside real TEAx, with every published number matched against arithmetic derived
from the SysML by hand rather than against a previous run. The original Item 7 failed here by
self-certification: its tests asserted `is True` on a script's own self-report, and its runner rode
a fake SimKit stub. This slice's job is to make that impossible to repeat.

## Summary

The slice does what it claims. I re-derived every headline number independently from the SysML
equations, re-ran the whole real-TEAx lane, and built my own live and relocated generation +
execution probe outside the test suite: all eleven channels reproduce to the last digit on both
routes. The rename byte-proof, the mutation every-and-only partition, the 37-path corpus, the golden
record change sets, and both full suites all reproduce exactly as recorded.

One gate claim is false. The slice introduces a new mypy error at `elaborate.py:628` and the
completion notes record the mypy baseline as "identical". It is a benign local typing regression
with no runtime effect, but it is a gate reported without being re-run, which is the exact class of
defect this recovery exists to prevent. The remaining findings are evidence-prose accuracy and one
test assertion that is weaker than the claim it backs — I verified the stronger form myself and it
holds.

## Environment

Import paths re-asserted before any measurement (the F2 trap):

| package | resolved to |
|---|---|
| `sysml_codegen` | `/home/reid/1cfe/sysml-codegen-item7-rebuild/src/sysml_codegen/__init__.py` |
| `agentic_mbse` | `/home/reid/1cfe/agentic-mbse-item7-rebuild/src/agentic_mbse/__init__.py` |
| `simkit` | `/home/reid/1cfe/teax/packages/teax-simkit/simkit/__init__.py` |

Interpreter `/home/reid/1cfe/item7-rebuild-venv/bin/python`, CPython 3.12.11. License sourced from
`/home/reid/1cfe/agentic-mbse/.env`. `grep -c "no live syside license"` = **0** on the execution
lane and on the full codegen suite.

**The agentic-mbse "unchanged at `cc6c7a7`" claim is true, and needs one clarification.** The
checkout at `/home/reid/1cfe/agentic-mbse` is a *different* worktree, on `elaborate-first-salvage`
at `5088b41`. The paired rebuild worktree is `/home/reid/1cfe/agentic-mbse-item7-rebuild`, which is
clean and at `cc6c7a7411f6338a4811a7cc58ca002c29ef177b` on `item7-rebuild` — and that is the one
the venv resolves `agentic_mbse` from. Zero agentic paths appear in the `848628b` diff.

---

## What I verified, and how

### 1. The real-TEAx lane, re-executed and then re-derived from scratch

`python -m pytest tests/execution -m execution -q` → **38 passed, 0 skipped, 0 failed** (3.06 s).
Composition: 18 pre-existing nodes (`test_constraint_execution` 15, plus 3 singletons) and 20 new
ones (`test_fusion_tea_real_teax` 12, `test_fusion_tea_mutation_teax` 8). That accounts for the
`+20 deselected` in the default run exactly.

I did not stop at the tests. I wrote my own probe (`/tmp/claude-audit3d/probe.py`) that builds an
exact context, generates and seals a package, loads it through TEAx's `ProvisionalPackageLoader`,
discovers through `create_registry`, and runs `simkit.core.pipeline.execute_pipeline` — once live,
once from a v6 snapshot copied to a third directory with the model tree deleted. Both published
exactly 11 channels with identical numeric values:

| Channel | Value (live == relocated) |
|---|---|
| `hif_plant_pkg__hif_plant__lcoe_calc__lcoe` | `270.1211779380445` |
| `hif_plant_pkg__hif_plant__meier_coe_calc__coe_cents_kwh` | `4.735403549076959` |
| `hif_plant_pkg__hif_plant__meier_capital_calc__total_capital_billions` | `3.303886865568384` |
| `hif_plant_pkg__hif_plant__meier_reactor_cost_calc__reactor_cost_billions` | `0.7304442587805375` |
| `hif_plant_pkg__hif_plant__recirc_calc__f_recirc` | `0.07222302470027446` |
| `meier_cost__gamma` (both driver instances) | `68.247088` |
| `meier_cost__cost_billions` (both) | `0.9749584000000001` |
| constraint report | `all_satisfied`, margin `18.0`, `observed {eta: 0.35, gain_in: 80.0, threshold: 10.0}`, byte-equal `model_dump` |

`semantic_fingerprint` equal, seal `executable_fingerprint` different — as documented.

**I then checked the transcription itself against the SysML, not against the module's word.** I read
`ife_lcoe.sysml`, `hif_economics.sysml`, `fusion_cycle.sysml`, and all four design files, and typed
an independent implementation of the Hawker chain, the Meier chain, and the recirculating fraction
(`/tmp/claude-audit3d/hand.py`), never importing `fusion_tea_arithmetic`. Every intermediate in the
transcription — `energy_on_target`, `fusion_energy_per_shot`, `net_electric_power`, `shots_per_year`,
`driver_lifetime_years`, `annual_capital_cost`, `annual_operating_cost`, `annual_energy`, both
present-value factors — matches the model line for line. My independent LCOE:

- base → `270.1211779380445`
- availability 0.91 → `269.5300723203276`
- thermal efficiency 0.44 → `263.85170462810606`
- gain 100 → `216.55528392479388` (the acceptance-test control)

All four to the last digit, plus COE at both availabilities, `f_recirc` at both thermal
efficiencies, `gamma`, `cost_billions`, reactor cost, and total capital. **The transcription is
sound and the executed package agrees with it.**

### 2. No stub, no self-report

- The fake-SimKit runner is absent from the lane, and the pin genuinely detects it. I imported
  `tests.runtime.pipeline_runner` into a process and ran the pin: it **fails** with the intended
  message (`tests/execution/test_fusion_tea_real_teax.py:186`). The pin is real, not decorative.
  It is also the stronger gate: `_install_simkit_stub` returns early when `simkit` is already in
  `sys.modules` (`tests/runtime/pipeline_runner.py:40`), so the import-level pin fires before the
  stub could ever shadow anything.
- No `skipif`, no `skip(` anywhere under `tests/execution/`. With the license removed
  (`env -u SYSIDE_LICENSE_KEY`), the module produces **1 passed, 11 errors, 0 skipped** — it fails,
  it does not go green. The one pass is the import-environment guard, which touches no model.
- No new test asserts on a script self-report. The single `is True` in the new tests
  (`test_fusion_tea_real_teax.py:268`) is the executed constraint predicate's own evaluated value,
  not a runner's claim about itself.
- `test_the_generated_registry_is_the_public_simkit_builder` compares function *identity* against
  `simkit.core.registry_builder.create_registry`, which a same-named local could not satisfy.

### 3. Mutation evidence, re-run independently

I ran both injections in my own harness against a freshly generated sealed package
(`/tmp/claude-audit3d/ports.py`), and counted the partition against the graph rather than trusting
the test:

- The graph has 9 modules and **40** distinct `(module, formal)` input ports.
- `hif_plant_pkg__hif_plant__availability` feeds exactly `lcoe_calc.availability_in` and
  `meier_coe_calc.availability_in`; no other port in the 40 is named `availability*`.
- `hif_plant_pkg__hif_plant__thermal_efficiency` feeds exactly `lcoe_calc.thermal_efficiency_in`
  and `recirc_calc.thermal_efficiency_in`; likewise unique.
- Runtime movers: C25 → exactly `lcoe` and `coe_cents_kwh`; C2 → exactly `lcoe` and `f_recirc`.
  Values `269.5300723203276` / `4.6833661474387505` and `263.85170462810606` / `0.07058159232072277`
  — matching my hand arithmetic, not the forensic record.
- **Nothing written to disk:** I SHA-256'd all 50 package files before and after three evaluations.
  Byte-identical.
- Reseal refusal is proved against the real gate: `check_reseal_provenance` is imported from
  `sysml_codegen.contracts` and raises `ProvenanceError` naming
  `inputs/hif_plant_params.json` (`test_fusion_tea_mutation_teax.py:233-255`). No stand-in.

The two-leg structure is honest about why it exists: the evaluation seam projects 5 numeric outputs
plus 2 constraint responses and does not project the two multi-output driver-cost modules, so the
runtime leg alone would not be an every-and-only claim. The structural leg closes it, and the
`fed ==` exact-set assertion (not the `startswith` belt beside it) is what actually carries it.

### 4. Rename byte-proof

Reproduced the strip-check myself: stripping the eleven authorized `_in` suffixes out of the six
changed model files at `848628b` yields content **byte-identical** to `26e7d04` in all six. Changed
line counts per file (10, 2, 3, 5, 10, 17) match the record.

All fifteen D11 ledger rows map to a hunk: each final form `in <formal>_in = <formal>;` is present
and no old form `in <formal> = <formal>;` survives anywhere in the fixture tree. `FT-10` is on the
constraint definition, as the census says.

No unledgered model change. `git diff 26e7d04 848628b -- tests/fixtures/` touches only the six
`.sysml` files, `fusion_tea/extraction_snapshot.json` (rename-consequent plus one `captured_at` and
the documented `ReferenceUsage` → `AttributeUsage` referent shift), and the two goldens. No other
fixture's `.sysml` moved.

Golden change sets are exactly as designed, measured at record level:

- `calc_def_compilation_golden.json` — **15** output records changed, and they are precisely the
  fifteen the design enumerates (IFE LCOE's ten intermediates, `Meier_COE.coe_cents_kwh`,
  `Meier_HIF_Driver_Cost.{bank_energy_joules,cost_billions}`,
  `Meier_Reactor_Cost.reactor_cost_billions`, `Recirculating_Power_Fraction.fusion_cycle_gain`).
- `calc_compat_parity_golden.json` — **3** records changed, exactly the design's three.
  `IFE_LCOE.lcoe`, `Meier_HIF_Driver_Cost.gamma`, `Recirculating_Power_Fraction.f_recirc`, and all
  of `Meier_Total_Capital_Cost` are untouched and remain independent arithmetic controls.

### 5. The two unnamed production hunks

Both reproduced against their red state at `26e7d04`, both general.

**Enumeration literal** (`elaborate.py:620-640`, `_enumeration_literal` at `:720`). Reverting only
this file to `26e7d04` and elaborating the renamed model raises `ElaborationDiagnosticError` with
**exactly 7 `SI_OCCURRENCE_MISSING`** — the claim, reproduced. The fix keys on a
`FeatureReferenceExpression` whose referent's owner is an `EnumerationDefinition`. That is a
language-level shape, not a fusion-tea-shaped special case; no fixture name, package, or attribute
name appears in it. The `declaration_id_for(referent)` call is correctly commented as an identity
gate rather than a value read.

**`sanitize_name(node.calc_def_name)`** (`project.py:786-790`). Reverting only this file, generation
succeeds but ships `class Meier HIF Driver CostOutput(MultiOutput):`,
`class TestRecirculating Power FractionRunnable:`, and `schemas/meier hif driver cost_output.py` —
a package that cannot import. The test 3B said was missing now exists: with the hunk reverted, **11
of the 12 real-TEAx tests error**, and they pass with it. That is a genuine executable gate, not a
cosmetic assertion. The fix is a plain call to the shared sanitizer, applied at the one site that
reaches generation.

### 6. Corpus

Re-ran `scripts/run_elaboration_corpus.py` over all 37 fixtures. Parsed the amended ledger and
compared per-row:

- **37/37 rows reproduce the amended ledger**, cell for cell, on both routes.
- Exact route: **15 public graphs / 22 typed errors**, all 22 `ElaborationError`. Legacy: 36 graphs
  / 1 error. Both totals match the amended block.
- Diffing the ledger at `26e7d04` against `848628b`, **exactly one row moved**: `fusion_tea`, from
  `error: 15× SI_SELF_BINDING` to `graph 9/27/1/7`. That is census obligation `B37-15`, and my own
  probe independently measured 9 modules on the exact route.
- The old cell contents and their basis are retained inside the amended row, and the totals block
  carries the Item 6 figures beside the current ones — the same treatment Slice 3A gave row 1.
- The driver reads both `diagnostics` and `findings` (`run_elaboration_corpus.py:52`) and records
  `error_type` beside the code list (`:58`), so the two error classes cannot collapse. This corpus
  only exercises `ElaborationError`, which the notes state plainly rather than implying coverage.

### 7. Gates

| Gate | Claimed | Measured |
|---|---|---|
| Full licensed codegen suite | 3539 / 47 / 38 | **3539 passed, 47 skipped, 38 deselected**, 0 license lines |
| `+20 deselected` are the new execution nodes | yes | yes — 18 pre-existing + 20 new, counted per module |
| `+1 passed` | `test_the_customer_model_carries_no_self_named_binding_...` | yes — node counts per changed module: `+1` in `test_elaboration_spike_parity.py`, `0` in the other four |
| agentic-mbse suite | 1825 / 1 / 5, unchanged | **1825 passed, 1 skipped, 5 deselected** |
| agentic-mbse clean at `cc6c7a7` | yes | yes — clean worktree, `rev-parse` matches, zero agentic paths in the diff |
| `ruff check src` | 16, identical | **16** at both `26e7d04` and `848628b` |
| `mypy src` | identical (71 in 17) | **71 in 17 → 72 in 18** — see Finding 1 |
| `git diff --check` | clean | clean |
| Changed paths ⊆ declared | equal | equal — 23 paths, all declared |
| Five changed test modules have recorded dispositions | yes | yes — one table row each, and every one carries an at-the-site comment explaining the move |

The acceptance command for the lane is recorded verbatim in the plan and does include the new
nodes: `addopts = -m "not execution"` deselects them from the default run, and
`pytest tests/execution -m execution` runs all 38. No node can go green without executing.

### 8. Test quality

Strong overall. The channel set is pinned by name as a set, so both a lost and an extra output
fail (`test_fusion_tea_real_teax.py:55-67`). Numbers are compared at `rel=1e-12` against the
transcription and separately against the headline constant at `rel=1e-6`, with
`assert hand.lcoe() == hand.RUN_C_LCOE` guarding the transcription itself from drifting into a new
target. The environment fixture asserts the resolved import paths rather than reporting them, so
the numbers cannot come from the wrong tree. The `fail_closed` rewrite replaces a diagnostic count
with a full seven-entry map of resolved enumeration attributes — one entry per former diagnostic —
so "empty diagnostics" cannot pass on an empty graph. The spike-parity split asserts the migration
by value, reading all fifteen renamed formals back off the graph.

Two assertions are weaker than the prose around them; see Findings 2 and 5. Neither changes the
result — I ran the stronger form of both and they hold.

---

## Findings

### Finding 1 — Medium — the mypy gate is recorded as identical but is not

`.project/active/cutover-recovery/plan.md:1922` — "`mypy src`: error set **identical** (71 errors in
17 files)". Measured, with only the two production files swapped between commits and everything
else held fixed:

- `26e7d04`: `Found 71 errors in 17 files`
- `848628b`: `Found 72 errors in 18 files`

The new error is introduced by this slice:

```
src/sysml_codegen/elaboration/elaborate.py:628: error: Incompatible types in assignment
(expression has type "float | int | str | None", variable has type "str")  [assignment]
```

`literal` is first assigned from `enumeration_literal`, which is typed `str | None` and narrowed to
`str` by the guard, so mypy pins the variable to `str`; the `elif` branch then assigns
`extract_literal_value(expression)`, whose type is wider (`elaborate.py:625-630`).

No runtime effect — the value is correct in every branch, and the corpus, the customer model, and
the whole suite prove it. The defect is in the evidence: the recorded figure is the *old* baseline,
so the gate was reported without being re-run against the final tree. That is the self-certification
failure mode this recovery exists to close, which is why this is Medium and not a nit.

**Resolution:** annotate the target (`literal: float | int | str | None`) ahead of the branch, re-run
`mypy src`, and correct the recorded baseline in the plan to whatever it then reads. If the
implementer instead wants to accept a 72-error baseline, the plan must say so explicitly rather
than say "identical".

### Finding 2 — Low — live/relocated difference confinement is one-directional and covers three suffixes, not the whole tree

`tests/execution/test_fusion_tea_real_teax.py:359-369`, and the claim it backs at
`plan.md:1712` ("the difference is confined to those comment lines, over the whole tree").

Two gaps:

1. The test computes `only_live = live_lines - relocated_lines` and asserts every member contains
   `SysML Source:`. Lines present in the *relocated* package but absent from the live one are never
   examined. A relocated-only spurious line would pass as long as a provenance line also differed.
2. `tree()` filters to `.py`, `.yaml`, `.md` (`:352`). The package's `.json` files — `contracts/`,
   `inputs/`, `schemas/` payloads — are outside the comparison entirely.

I ran the stronger form myself: both directions, every file type, all 50 files, package name
neutralised. The only file differing outside `SysML Source:` lines is
`contracts/package_contract.json`, whose per-file hash entries necessarily follow from the changed
comments. **So the substantive claim is true today** — the assertion is simply narrower than the
sentence it supports.

**Resolution:** symmetrise the difference set (`(a - b) | (b - a)`) and either widen `tree()` to all
files with the seal manifest explicitly excused and commented, or narrow the plan's wording from
"over the whole tree" to the three suffixes it actually covers.

### Finding 3 — Low — the notes name a red-state class name the red state does not produce

`.project/active/cutover-recovery/plan.md:1806` and the `848628b` commit message both say that
without the `sanitize_name` hunk "the exact route ships `class Recirculating Power FractionModule`".

I generated the package with `project.py` reverted to `26e7d04`. That string does not appear
anywhere in the tree. What the red state actually ships is
`class Meier HIF Driver CostOutput(MultiOutput):`,
`class TestRecirculating Power FractionRunnable:`, and the schema file
`schemas/meier hif driver cost_output.py` — the second half of the sentence is exact, the first is
not.

The conclusion is unaffected: the package does not import, and I confirmed 11 of 12 real-TEAx tests
error without the hunk. But this slice's whole contract is that written claims survive being
checked, so a fabricated-looking specimen in the evidence record is worth correcting.

**Resolution:** replace the example with one of the three strings the red state actually emits.

### Finding 4 — Informational — the arithmetic transcription's docstring misattributes four design values

`tests/execution/fusion_tea_arithmetic.py:18-19` credits `designs/generic_ife/ife_subsystems.sysml`
with "blanket multiple 1.15, yield cost 5e6, target cost 10.0, target factory 0.1". All four live in
`designs/hif_ife/hif_plant.sysml` — the first two on the `chamber` redefinition (`:66-68`), the
third on `target_factory` (`:52`), the fourth as a literal binding inside `meier_capital_calc`.
`ife_subsystems.sysml` declares those attributes with no values at all.

The numbers are right; only the pointer is wrong. It matters because this file's stated purpose is
to be "derivable from the model files alone" — a reader following the docstring to check the
transcription lands in a file that cannot confirm it.

**Resolution:** correct the file attribution in the docstring.

### Finding 5 — Informational — the constraint report is pinned field-by-field, not as a full dump against an independent expectation

`tests/execution/test_fusion_tea_real_teax.py:252-276` asserts `headline`, `assessed_count`, and the
single result's `constraint_id`, `status`, `actual_value`, `observed`, and `margin`, each against a
value derived from the model. That covers every semantically load-bearing field, and the margin is
computed rather than read back. What it is not is a whole-object comparison: `catalog_fingerprint`
is unasserted, and the only full `model_dump` comparison (`:317`) is live-against-relocated, which
is a consistency check rather than an independent expectation.

Recorded for completeness rather than as a gap — an added field carrying a wrong value would slip
through, but no field currently in the report is unchecked except the fingerprint.

**Resolution:** optional. Compare the full `model_dump` against a literal expectation, with the
fingerprint popped and asserted separately as an opaque non-empty value.

---

## Certification

**CERTIFY.** Nothing here blocks Slice 3E.

The slice's central claim — the customer model executes in real TEAx, live and relocated, pinned to
hand arithmetic — is true, and I established it independently rather than by re-reading the tests:
my own generation-and-execution probe and my own transcription of the model equations agree with the
committed evidence to the last digit on all eleven channels and all four mutation figures. The
mutation protocol writes nothing, the seal refuses the invalid route in code, the fake-SimKit runner
cannot reach the lane and the pin that says so genuinely fires, and the new tests fail rather than
skip when the license is removed. The rename is byte-proved, the corpus reproduces 37/37 with
exactly the one authorized row moved, and both full suites reproduce their recorded counts exactly.

The Medium finding is an evidence defect, not a behavior defect: a stale mypy baseline recorded as
"identical" when the slice added one error. It should be fixed before 3E as a matter of the
recovery's own discipline, but it gates nothing.

One process note, not a finding against 3D: the plan's **"Validation for every Phase 3 slice"**
checklist (`plan.md:583-596`) is still entirely unchecked, for 3A through 3D alike. Each slice's
completion notes cover the same ground in prose, so nothing is unrecorded — but the checklist reads
as though no slice has been validated. Worth reconciling once, at 3E, rather than per slice.

**Not checked:**

- **The forensic parts bin.** I did not diff the landed hunks against their originals at
  `07531e64`. The claim that the forensic `_enumeration_value`'s `SI_ID_MISSING` branch was
  unreachable and correctly dropped is unverified against its source; I verified only that the
  landed code is general, correct, and reproduces the documented red state.
- **The census beyond what the plan quotes.** I read D11's fifteen rows and confirmed each against
  the model, but did not audit `cutover-census.md`'s `FIX-01`, `B37-15`, or `PROD-24` rows against
  their own upstream basis.
- **The legacy CLI 48-file smoke comparison.** I did not regenerate the shipped-CLI package at
  `26e7d04` and diff it tree-to-tree against `848628b`. The claim that only the fifteen `_in` field
  names and their dependent hashes moved is taken from the notes.
- **The v5 recapture gate.** `test_live_vs_snapshot_byte_identical[fusion_tea]` passed inside the
  full suite; I did not separately re-capture the snapshot and confirm only `captured_at` moved.
- **agentic-mbse lint/type.** Not re-run — nothing changed there, and the repository is clean at
  `cc6c7a7`.
- **`_enumeration_literal` outside the shape this fixture exercises.** I confirmed it is general
  over `FeatureReferenceExpression` with an `EnumerationDefinition` owner. I did not probe enum
  references reached through an alias, an inherited redefinition chain, or a non-`Feature`
  referent.
- **Carried residuals.** The Slice 3A/3B/3C findings and the named 3E residuals (`d38_caret`,
  `unresolvable_attr_probe`, the `SysML Source:` provenance divergence) were read for context but
  not re-audited.
- **Slice 3E's own gap.** The notes state plainly that the exact route still has no public
  `generate` entry point and that `real_teax.py` reproduces `cmd_generate`'s step sequence
  internally. I confirmed the sequence matches `cli/__init__.py` by reading both, but did not assess
  whether that is a sufficient stand-in for the public-API requirement the plan sets for 3E.
