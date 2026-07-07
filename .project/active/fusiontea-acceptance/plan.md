# Implementation Plan: fusion-tea Acceptance & Workaround Retirement (PIPELINE-TRUTH Item 3)

**Status:** Draft
**Created:** 2026-07-06
**Last Updated:** 2026-07-06

## Source Documents
- **Spec:** `.project/active/fusiontea-acceptance/spec.md` ← success criteria SC-A/B/C/D, known requirements, non-goals
- **Epic:** `.project/backlog/epic_pipeline_truth.md` (Item 3, lines 291–341)
- **No design** — execution item. It assembles and retires against landed Item-2 mechanisms; it builds no new resolution code.
- **Upstream (Item 2, consumed):** `.project/active/whole-plant-resolution/{spec,design,plan}.md` — value-fill mechanism, source-QN fan-out collapse, `run_pipeline` runner contract

### Landed Item-2 substrate this plan consumes (verified this session)
- `tests/fixtures/fusion_tea/` — vendored canonical models + committed **v2** snapshot (`extraction_snapshot.json`, `snapshot_format_version: 2`). `hif_driver_instance` is present (`designs/hif_ife/hif_driver.sysml:100`). This is SC-A **state (i)**.
- `tests/conformance/test_fusion_tea_snapshot.py` — proves **zero V11 offenders** on that snapshot (SC-4 proxy / SC-A state (i) gate) and proves the renamed-consumer fan-out collapses to **one source-QN EP** (`driver.efficiency` → `eta` + `driver_efficiency`; `chamber.blanket_energy_multiple` → two readers).
- `tests/runtime/pipeline_runner.py` — `run_pipeline(package_dir, inputs) -> dict[str, float]`. Reused verbatim. `tests/runtime/test_pipeline_runner.py` shows the exact anchor + perturbation pattern (module import → run in YAML order → channel dict; `inputs=` override perturbs an entry point).

---

## Implementation Strategy

**Two venues, deliberately separated (spec R1 / epic "cross-repo"):**

| Venue | What lands there | Branch |
|-------|------------------|--------|
| **sysml-codegen (this repo)** | Durable **license-free** acceptance proof (run-C 270.12 + perturbed key via `run_pipeline` on the committed snapshot) + SNAP-19 parametrization + fusion_tea live-parity leg | `pipeline-truth-epic` (current) |
| **fusion-tea (`~/1cfe/fusion-tea`)** | The actual workaround **deletions** + Meier channel re-anchor + state-(ii) re-capture + a simplified `run_anchors.py` mirroring the same numbers live | a fusion-tea branch (convention TBD — see Risks) |

**Reconciliation note (deviation from spec's literal "this repo receives only the SNAP-19 test", line 160):** Item 2 vendored the fusion_tea fixture and built `run_pipeline` **in this repo specifically for Item 3 to consume sight-unseen**. The faithful, lowest-risk home for the SC-B acceptance number is therefore an **in-repo license-free test** (CI-visible, no license), with fusion-tea's `run_anchors.py` as the live mirror. This double-covers SC-B (license-free in CI + live upstream) and de-risks the numbers before any fusion-tea change. The plan phase is where this reconciliation belongs (spec line 79: "the plan phase re-reads the report with repo access and resolves the plan-time opens").

**Phasing rationale — de-risk the numbers license-free first, touch fusion-tea second, live legs last-and-contiguous:**
1. **Phase 1** proves the epic's headline number (270.12) reproduces and the JSON is *consumed* — license-free, in-repo, before touching anything upstream. This is the highest-risk unknown (the SC-3/SC-5 holes the adversarial pass named), so it goes first.
2. **Phase 2** parametrizes SNAP-19 (authoring is license-free; the live legs skip cleanly without a license).
3. **Phase 3** does the fusion-tea retirement (deletions + re-anchor + simplify) — pure edits/greps, no license.
4. **Phase 4** runs everything that needs a live license, **contiguous**: state-(ii) re-capture + SNAP-19 live legs + fusion_tea live-parity byte-diff.
5. **Phase 5** writes the run report and coordination/impact notes.

**Critical path:** Phase 1 (numbers real, license-free) → Phase 3 (retire upstream) → Phase 4 (live confirmation) → Phase 5 (record). Phase 2 is independent of 1/3 and can land any time before Phase 4.

**First proof point:** Phase 1's anchor-C assertion — `run_pipeline` on the package generated from the committed fusion_tea snapshot returns the lcoe channel at `270.1211779380445` within rel 1e-6. If that fails, the whole item stops and escalates to Item 2 (spec non-goal: this item does not patch resolution).

**Overall validation:** every phase starts with a test or a grep-verifiable assertion; the live legs skip cleanly (`@requires_license`) so CI stays green without a license.

---

## Phase 1: In-repo acceptance proof — run-C reproduces + perturbed key consumed (license-free)

### Goal
Prove, license-free on the committed fusion_tea snapshot, that the generated package executes to the epic's headline lcoe (270.12) through `run_pipeline`, and that moving one emitted-JSON key moves the output to a **hand-computed** value. This collapses the SC-3 (end state never run) and SC-5 (baked-default vs consumed) holes before any upstream change.

### Assumption Under Test
The vendored canonical models generate a package that (a) executes to `270.1211779380445/MWh` via `run_pipeline`, and (b) reads its entry-point JSON — perturbing the `gain` source-QN key changes the lcoe to an independently hand-computed target.

### Test Stencil (Write This First)
```python
# tests/runtime/test_fusion_tea_acceptance.py  (NEW)
import pytest
from sysml_codegen.cli import GenerationConfig, run_codegen
from tests.conftest import snapshot_fixture
from tests.runtime.pipeline_runner import run_pipeline

_LCOE_CHANNEL = "<derive at implement from emitted pipeline YAML>"   # hif_plant lcoe channel
_RUN_C_LCOE = 270.1211779380445
_GAIN_EP_KEY = "<derive: the post-collapse source-QN key for gain, e.g. ...__gain>"
_GAIN_PERTURBED = 100.0                    # gain 80 -> 100 (spec-named example)
_HAND_LCOE_AT_GAIN_100 = <hand-computed>   # from ife_lcoe.sysml arithmetic, NOT read back

def _gen(tmp_path):
    cfg = GenerationConfig(output_path=tmp_path/"pkg",
                           from_snapshot=snapshot_fixture("fusion_tea"),
                           package_name="pkg", overwrite=True)
    assert run_codegen(cfg) is True
    return tmp_path/"pkg"

def test_run_c_reproduces(tmp_path):                       # anchor C: full pipeline
    out = run_pipeline(_gen(tmp_path))
    assert out[_LCOE_CHANNEL] == pytest.approx(_RUN_C_LCOE, rel=1e-6)

def test_gain_perturbation_is_consumed(tmp_path):          # SC-B rider (SC-5 hole)
    out = run_pipeline(_gen(tmp_path), inputs={_GAIN_EP_KEY: _GAIN_PERTURBED})
    assert out[_LCOE_CHANNEL] == pytest.approx(_HAND_LCOE_AT_GAIN_100, rel=1e-6)

# anchors A/B: module-level (each calc's own semantics, in isolation)
def test_meier_driver_cost_module(tmp_path):               # anchor A
    # import the generated meier_cost module class, .run(**known_inputs), assert its own output
    ...
def test_recirc_fraction_module(tmp_path):                 # anchor B (fusion_cycle f_recirc)
    ...
```

### Changes Required
**See `test_pipeline_runner.py:16–48` for the anchor + perturbation pattern (copy it).** Key facts from the models:
- `ife_lcoe.sysml` — closed-form DCF lcoe from 14 params; `gain` is `in attribute gain` (`:54–58`). The hand-computed target at `gain=100` is derived from this arithmetic at implement and transcribed as a literal (spec Open Q; epic R1 anti-pattern ban — never read back from the executor).
- `hif_plant.sysml:87` — `:>> gain = 80.0` (DESIGN_ATTRIBUTE entry point; the perturbed source).
- Fan-out collapse (spec [INFERRED], lines 132–137): the emitted JSON key set is keyed by **source-attribute QN**, so `_GAIN_EP_KEY` must be an **existing post-collapse key** in the emitted `inputs/*.json`. Derive it at implement by generating the package and reading the emitted JSON — do not guess.

**Specific file changes:**

#### 1. Test file
**File:** `tests/runtime/test_fusion_tea_acceptance.py` (NEW — write first)
- [ ] Anchor C: `run_pipeline` on the from-snapshot package → lcoe channel `== approx(270.1211779380445, rel=1e-6)`.
- [ ] Anchors A/B: module-level checks (import the generated Meier-cost and recirc-fraction module classes, `.run()` with known inputs, assert each calc's own semantics; exact intermediate values derived at implement from the auto-impls, not invented here).
- [ ] Perturbed-key: derive `_GAIN_EP_KEY` from the emitted JSON, hand-compute `_HAND_LCOE_AT_GAIN_100` from `ife_lcoe.sysml`, assert `run_pipeline(..., inputs={key: 100.0})` moves the lcoe to it.

### Validation
**Automated:**
- [ ] `uv run pytest tests/runtime/test_fusion_tea_acceptance.py` → all pass
- [ ] `uv run pytest tests/` → no regressions (`test_fusion_tea_snapshot.py`, `test_pipeline_runner.py` still green)
- [ ] `uv run ruff check src/ tests/` → passes

**Manual:**
- [ ] Generate the package once by hand (`generate --from-snapshot tests/fixtures/fusion_tea/extraction_snapshot.json`), read `inputs/*.json`, confirm the chosen `gain` key exists post-collapse and its value is `80.0`.
- [ ] Sanity-check the hand-computed perturbed lcoe against a one-line desk calc of `ife_lcoe`'s formula.

**What We Know Works After This Phase:**
The generated fusion_tea package executes to the real lcoe, and the emitted JSON is genuinely consumed (perturbation moves the output). SC-A state (i) + SC-B are proven license-free. The numbers are locked before any upstream edit.

---

## Phase 2: SNAP-19 parity — parametrized over shape-bearing fixtures (channel-identity)

### Goal
Extend the byte-parity gate from `solar_battery`-only to the shape-bearing fixtures, so a full-emission live-vs-snapshot mis-wire on any of them fails the test. Assert **channel identity**, not merely that `fallback_entry_points` was vacated (the multi-hop EXPOSE precedent — memory `multihop-expose-offline-parity` — passed the weaker check).

### Assumption Under Test
The existing `_tree_diff` full-tree byte comparison (which includes the pipeline YAML, hence the wired channels) already *is* channel-identity; the gap is fixture **coverage**. Parametrizing over `retype_model`, `quoted_owner_formula`, `alias_agg_probe`, `ife_plant`, `plant_values` extends coverage without weakening the check.

### Test Stencil (Write This First)
```python
# tests/conformance/test_snapshot_generation.py  (extend)
_SNAP19_FIXTURES = ["solar_battery_model", "retype_model", "quoted_owner_formula",
                    "alias_agg_probe", "ife_plant", "plant_values"]  # exact dirs at implement

@requires_license
@pytest.mark.req("REQ-SNAP-19")
@pytest.mark.parametrize("fixture", _SNAP19_FIXTURES)
def test_live_vs_snapshot_byte_identical(fixture, tmp_path):
    abs_models = REPO_ROOT / "tests/fixtures" / fixture
    live = _run_cli("generate", "--models", str(abs_models), "--output", str(tmp_path/"live"),
                    "--package-name", fixture, "--overwrite")
    snap = _run_cli("generate", "--from-snapshot", str(abs_models/"extraction_snapshot.json"),
                    "--output", str(tmp_path/"snap"), "--package-name", fixture, "--overwrite")
    assert live.returncode == 0 and snap.returncode == 0
    assert _tree_diff(tmp_path/"live", tmp_path/"snap") == []   # full-tree = channel identity
```

### Changes Required
**See `tests/conformance/test_snapshot_generation.py:167–188` for the current single-fixture test.**
- [ ] Confirm at implement that each parametrized fixture has both a committed model dir **and** an `extraction_snapshot.json` at v2. Any fixture missing a snapshot either gets one captured in Phase 4 (live) or is dropped with a logged reason (no silent skip).
- [ ] Parametrize the byte-identity test over `_SNAP19_FIXTURES`; keep it `@requires_license` (live leg runs in Phase 4).
- [ ] Structuring call (spec Open Q, line 210): **extend** the existing test via `parametrize` rather than a new test — one gate, N fixtures.
- [ ] Channel-identity guard: the full-tree `_tree_diff` already compares `pipelines/*.yaml` (wired channels). Add an inline comment pinning *why* full-tree diff is the channel-identity check (defends against a future narrowing to metadata-only diff), per the multi-hop precedent.

### Validation
**Automated:**
- [ ] Without a license: `uv run pytest tests/conformance/test_snapshot_generation.py -k byte_identical` → **skips cleanly** (all params), no error.
- [ ] Deliberate mis-wire probe: hand-edit one fixture's committed snapshot to point a channel at the wrong source, run the test **with** license → it **fails** on that fixture (R1: fires on the shape it claims). Revert after.

**What We Know Works After This Phase:**
The parity gate is defined across every shape-bearing fixture and provably fires on a mis-wire. The live legs are wired to run in Phase 4.

---

## Phase 3: fusion-tea retirement — delete the workarounds, re-anchor the channels (no license)

### Goal
On a fusion-tea branch, delete every workaround the retirement table names, re-anchor the Meier channel EQNs to the canonical driver path, and simplify `run_anchors.py` to single-pass module-level A/B + full-pipeline C. Leave the two documented keep-items (teax T-1/T-2 router; the ηG>10 constraint check).

### Assumption Under Test
With Item 2 landed, deleting `hif_driver_instance` still leaves **zero V11 offenders** (spec fact 3: mechanism (d) resolves #9 and #10 in place), and the Meier channels re-anchor cleanly to `hif_plant_pkg__hif_plant__driver__meier_cost__*`. (The zero-offender half is *proven* in Phase 4's re-capture; this phase makes the edits and the greps.)

### Changes Required — retirement table (each row → concrete deletion + verification grep)

> Paths below are fusion-tea-repo-relative and must be confirmed at implement against the actual tree (this session cannot read `~/1cfe/fusion-tea`). Re-read the report's **§"Coordination actions"**, **§"Reproduce"**, and the **retirement table** with fusion-tea access first (spec Required Reading).

| # | Workaround | Action | Verification grep (must return **zero**) |
|---|-----------|--------|------------------------------------------|
| R-1 | `sanitize_names.py` (dead, not deleted) | Delete the file + any import | `grep -rn "sanitize_names" ~/1cfe/fusion-tea` |
| R-2 | `part hif_driver_instance` (template-expansion crutch) | Delete from the canonical models; re-anchor Meier channel EQNs in `run_anchors.py`/`sweep_ife.py` to `hif_plant_pkg__hif_plant__driver__meier_cost__*` | `grep -rn "hif_driver_instance" ~/1cfe/fusion-tea` |
| R-3 | Two-pass gamma feedback | Delete the second pass; `run_anchors.py` runs single-pass through the generated package | `grep -rni "two.pass\|second pass\|gamma feedback" ~/1cfe/fusion-tea/.../run_anchors.py` |
| R-4 | Hand-written input JSONs for wired/pre-filled values | Delete; the emitted `inputs/*.json` from the generated package is the sole source | confirm `run_anchors.py` reads the generated `inputs/` dir, not a checked-in JSON |
| R-5 | `run_anchors_bridged.py` (stale-key + exactly-10-offender guard bridge) | Delete; superseded by simplified `run_anchors.py` | `grep -rn "bridged\|== 10\|exactly.10" ~/1cfe/fusion-tea/.../run_anchors*` |
| R-6 | Six `out attribute` conversions (spec Open Q, lines 207–209) | **Inspect each**; revert to plain `attribute` where **not** load-bearing for a genuine output; leave any that are. Record the per-attribute call in the run report. | n/a — decision logged, not a zero-grep |

**KEEP (do not touch — out of epic scope):** teax `OutputRouter`/`WriteHandler` (T-1/T-2); `sweep_ife.py`'s ηG>10 viability check (stays harness-side until the constraint-execution epic).

**`run_anchors.py` simplification:**
- [ ] Anchors A/B → module-level checks (import the generated module class, `.run()`, assert the calc's own semantics) — mirror Phase 1's A/B.
- [ ] Anchor C → full pipeline via `run_pipeline`. **Coordination decision:** copy `tests/runtime/pipeline_runner.py` into the fusion-tea work dir as a self-contained vendored driver (no runtime cross-repo import). Note the provenance in a header comment so the two stay in sync.
- [ ] Add the perturbed-key rerun (mirror Phase 1) so the live run also proves consumption.

### Validation
**Automated (license-free parts):**
- [ ] All R-1…R-5 verification greps return zero.
- [ ] `run_anchors.py` has no `import`/reference to the bridge, the two-pass feedback, or a checked-in input JSON.

**Manual:**
- [ ] Confirm the fusion-tea branch name/PR flow against their actual conventions (see Risks — unverifiable this session).
- [ ] R-6: for each of the six `out attribute`s, record load-bearing / reverted in the run report.

**What We Know Works After This Phase:**
Every workaround is deleted upstream (SC-C greps clean) and `run_anchors.py` is simplified — but not yet *run* on the re-captured world. That is Phase 4.

---

## Phase 4: Live-license legs (contiguous) — state-(ii) re-capture + SNAP-19 live + fusion_tea parity

### Goal
Run everything that needs a live syside license, back-to-back: re-capture the fusion-tea snapshot after the `hif_driver_instance` deletion (SC-A state ii), run the simplified `run_anchors.py` live, and turn the SNAP-19 live legs green (parametrized set + the one-time fusion_tea live-vs-snapshot byte-diff).

### Assumption Under Test
The workaround-free models (state ii) generate at **still-zero** offenders with the Meier channels re-anchored, the simplified single-pass anchors pass, and every parametrized fixture's live emission is byte-identical to its snapshot emission.

### Changes Required

**Live leg A — state-(ii) re-capture + anchors (fusion-tea, R3 baseline discipline):**
- [ ] Re-capture the fusion-tea snapshot at **v2** from the workaround-free canonical models via the capture script, as a **reviewed diff** (memory `byte-identity-captured_at-churn`: a full re-capture rewrites every `captured_at`; run the timestamp-only diff gate so only the real structural change shows).
- [ ] Assert **zero V11 offenders** on the re-captured snapshot; assert the Meier channels are now keyed `hif_plant_pkg__hif_plant__driver__meier_cost__*` (state-(ii) channel identity, not just "no `hif_driver_instance`").
- [ ] Run the simplified `run_anchors.py` live: A/B module-level + C full-pipeline at rel 1e-6, **single-pass**, plus the perturbed-key rerun.
- [ ] **Do not** commit this snapshot into sysml-codegen (spec: "do not commit two fusion-tea snapshots"; the in-repo committed snapshot is state (i)). It lives fusion-tea-side.

**Live leg B — SNAP-19 parametrized set (this repo):**
- [ ] `uv run pytest tests/conformance/test_snapshot_generation.py -k byte_identical` **with license** → all parametrized fixtures green.
- [ ] Capture any missing per-fixture snapshot flagged in Phase 2 (reviewed diff, timestamp gate).

**Live leg C — fusion_tea live-vs-snapshot byte-diff (this repo, one-time):**
- [ ] Add a `@requires_license` test: generate live from the vendored `tests/fixtures/fusion_tea` models vs `generate --from-snapshot` on the committed snapshot; assert `_tree_diff == []` (full-tree = channel identity; the offline mis-wire precedent must be caught).

### Test Stencil (live leg C)
```python
@requires_license
@pytest.mark.req("REQ-SNAP-19")
def test_fusion_tea_live_vs_snapshot(tmp_path):
    models = REPO_ROOT / "tests/fixtures/fusion_tea"
    live = _run_cli("generate", "--models", str(models), "--output", str(tmp_path/"live"),
                    "--package-name", "fusion_tea", "--overwrite")
    snap = _run_cli("generate", "--from-snapshot", str(models/"extraction_snapshot.json"),
                    "--output", str(tmp_path/"snap"), "--package-name", "fusion_tea", "--overwrite")
    assert live.returncode == 0 and snap.returncode == 0
    assert _tree_diff(tmp_path/"live", tmp_path/"snap") == []
```

### Validation
**Automated (with license):**
- [ ] state-(ii) snapshot: zero offenders + re-anchored Meier channel identity asserted.
- [ ] `run_anchors.py` live: A/B/C green single-pass + perturbed-key moves the output.
- [ ] SNAP-19 parametrized + fusion_tea leg: all green.
- [ ] Timestamp-only diff gate on every re-capture shows only the intended structural change.

**What We Know Works After This Phase:**
Both offender states are verified (state i license-free in Phase 1; state ii live here). The epic's SC-A live gate and SC-D live leg are closed. The workaround-free world runs single-pass.

---

## Phase 5: Close-out — run report + coordination + Item-9/10 impact

### Goal
Record the assembled end state and discharge the report's coordination checklist.

### Changes Required
- [ ] **Run report** in `.project/active/fusiontea-acceptance/run-report.md` capturing: both offender states (i committed / ii re-captured), the run-C reproduction (270.12), the perturbed-input delta (key + hand-computed target + observed), the **recorded constraint-drop report** from `generate` (spec fact 2 — recorded as expected output, not a surprise), and the retirement checklist with each grep result.
- [ ] **Coordination notes to fusion-tea:** the report's §"Coordination actions" checklist marked discharged; the R-6 per-attribute decisions; the vendored-`pipeline_runner.py` provenance note.
- [ ] **Item-9 impact:** append this item's verification-matrix / release-note deltas for Item 9's accumulation (memory `verification-matrix-drift-modes`).
- [ ] **Item-10 impact:** note any close-out epic touchpoints.
- [ ] **R2 (agentic-mbse lockstep):** record explicitly — this item changes no executable SysML subset and no auditor behavior, so agentic-mbse impact is **none new** (spec [INFERRED], lines 169–171).

### Validation
- [ ] Run report is complete and matches the actual test/grep outputs (no self-certification — numbers pasted from real runs).
- [ ] fusion-tea PR opened per their conventions; this repo's parity + acceptance tests committed on `pipeline-truth-epic`.
- [ ] Suggest `/_my_audit` before PR (workflow-accountability rule).

**What We Know Works After This Phase:**
The epic's real-world proof is assembled, recorded, and coordinated. SC-A/B/C/D all discharged.

---

## Environment Setup
**See CLAUDE.md.** Tests: `uv run pytest tests/`. Type: `uv run mypy src/`. Lint: `uv run ruff check src/`. License-gated legs skip cleanly without a syside license (memory `syside-license-via-scripts-not-dashc`: the license loads for capture scripts / full pytest, not a bare `-c` probe — verify captures via the real capture path).

## Risk Management

- **fusion-tea branch/PR convention unverifiable from this session (HIGH-visibility, LOW-severity).** Every cross-repo read is blocked by this repo's working-directory sandbox. **Mitigation:** Phase 3 begins by inspecting `~/1cfe/fusion-tea` with proper access and following its actual conventions; until then the documented fallback (spec line 196) is a dedicated branch mirroring `pipeline-truth-epic`, PR per their norm. Do not commit upstream until the convention is confirmed.
- **Perturbed key must survive the fan-out collapse (MEDIUM).** The emitted JSON is keyed by source-QN, so per-consumer keys the report assumed may not exist. **Mitigation:** Phase 1 derives `_GAIN_EP_KEY` by reading the actually-emitted `inputs/*.json`, not from the report's key set (spec [INFERRED], lines 132–137).
- **Anchor C might not reproduce 270.12 (MEDIUM → escalate, don't patch).** If `run_pipeline` returns a different lcoe, this item **stops** — it consumes the Item-2 mechanism, it does not fix resolution (spec Non-Goals). Escalate to Item 2.
- **Re-capture timestamp churn (LOW).** A full re-capture rewrites every `captured_at`. **Mitigation:** the timestamp-only diff gate (memory `byte-identity-captured_at-churn`) on every capture in Phase 4.
- **State-(ii) re-anchor could mis-wire offline (MEDIUM).** **Mitigation:** assert the wired Meier channel's *identity* (`hif_plant_pkg__hif_plant__driver__meier_cost__*`), not merely the absence of `hif_driver_instance` (multi-hop EXPOSE precedent).

## Implementation Notes
[TO BE FILLED DURING IMPLEMENTATION — leave empty now]

### Phase 1 Completion
**Completed:** 2026-07-06

**Changes Made:**
- `tests/runtime/test_fusion_tea_acceptance.py` (NEW): 4 tests — anchor C (full pipeline
  → lcoe `270.1211779380445`), perturbed-key consumption (gain 80→100 → hand-computed
  `216.55528392479388`), anchor A (meier_cost module isolation: gamma `68.247088`,
  cost_billions `0.9749584`), anchor B (recirc module isolation: f_recirc
  `0.07222302470027446`). All expected values hand-derived from SysML arithmetic and
  transcribed with the arithmetic in the comments — never read back from the executor.
- `tests/runtime/pipeline_runner.py`: completed the fixture simkit stub for **multi-output**
  packages (fusion_tea is the first). Two faithful additions, NOT a re-implementation of the
  executor logic or a resolution patch: (1) `_install_simkit_stub` now provides
  `simkit.config.schema.MultiOutput` (aliased to pydantic `BaseModel` — the only surface the
  runner needs, it reads each output via `getattr`); (2) `_resolve_source` now recognizes a
  bare multi-output channel name as an upstream channel (the third source form alongside
  `<channel>.root` and `<group>.<QN>`). The generated YAML wiring was already correct (the
  report proved anchor C reproduces via the teax executor); the in-repo runner's token
  classifier was single-output-only because the twolevel fixture never exercised multi-output.

**Acceptance numbers achieved (exact):**
- anchor C lcoe: `270.1211779380445` (target `270.1211779380445`, rel 1e-6) — bit-exact
- perturbed lcoe @ `lcoe_calc__gain`=100: executor `216.55528392479388` == independent
  hand-calc `216.55528392479388` — bit-exact
- anchor A: gamma `68.247088`, cost_billions `0.9749584`; anchor B: f_recirc `0.07222302470027446`

**Deviations / notes:**
- **Perturbed key.** gain is emitted **per-consumer** (`hif_plant_pkg__hif_plant__lcoe_calc__gain`
  and `...__recirc_calc__gain`), NOT collapsed by source QN — it is a plant DESIGN_ATTRIBUTE
  bound into each calc usage, not a cross-part fan-out. Only `driver__efficiency` collapses
  (cross-part, one key feeding `lcoe_calc.driver_efficiency` + `recirc_calc.eta`). Perturbing
  the lcoe_calc gain key alone moves lcoe; recirc is untouched. This resolves the plan's MEDIUM
  risk (the per-consumer key the report assumed DOES exist post-collapse).
- **Anchors A/B** are module-level checks of the *current* generated modules' own semantics.
  The report's historical A=$252.30 / B=$68.69 were pre-wiring WI-015 dollar figures from an
  earlier model state (lcoe-calc fed `driver_cost_constant=5.0`); superseded per plan.
- **Runner-completion flag (for audit):** the two `pipeline_runner.py` edits are a
  test-harness surface completion, not a mechanism change. No `src/` resolution code touched.
- **Test isolation:** each test generates a uniquely-named package (from its tmp_path) — the
  runner imports by dir name and a shared name collides in `sys.modules`.

**Validation:** full suite `2060 passed, 4 skipped, 5 xfailed` (was 2056; +4 new). ruff src/
= 17 (unchanged), mypy src/ = 104 (unchanged). `test_fusion_tea_snapshot.py` /
`test_pipeline_runner.py` still green.

### Phase 2 Completion
**Completed:** 2026-07-06

**Changes Made:**
- `tests/conformance/test_snapshot_generation.py`: parametrized
  `test_live_vs_snapshot_byte_identical` over `_SNAP19_FIXTURES` = [`solar_battery_model`,
  `retype_model`, `quoted_owner_formula`, `alias_agg_probe`, `ife_plant`, `plant_values`]
  — one gate, 6 shapes (was solar_battery only). Added an inline comment pinning WHY the
  full-tree byte diff IS the channel-identity check (it includes `pipelines/*.yaml`, whose
  module inputs name each wired source channel) and a "do not narrow to metadata-only" guard.

**Verified at implement:** all six fixtures exist with committed **v2** snapshots — no
missing capture to defer to Phase 4.

**License note:** the syside license is LIVE in this session, so the `@requires_license`
legs actually RAN (not skipped): all 6 parametrized fixtures + the symlinked leg PASS
byte-identical. This satisfies Phase 4 leg B here.

**R1 mis-wire probe (fires on the shape it claims):** repointed the ife_plant snapshot's
cross-module channel source (`radial_build.magnet_volume_total` →
`radial_build.MISWIRED_channel`) in the committed snapshot; snap-gen aborted V11 (the
mis-wired channel mints no params key) and the parity test FAILED; snapshot reverted clean
(`git checkout`, status empty). Confirms the gate catches a channel mis-wire.

### Phase 3 Completion (fusion-tea repo)
**Completed:** 2026-07-06 · branch `chore/retire-pipeline-truth-workarounds` (off `epic/pipeline-derisk-demo`)

**Commit:** `5a889ac5` — retirement source edits (pathspec-scoped; their in-progress `.project/`
changes and bridged artifacts untouched):
- Deleted `exploration/ife_e2e/sanitize_names.py` (R-1).
- Deleted `part hif_driver_instance` from BOTH `models/designs/hif_ife/hif_driver.sysml` and
  the `exploration/ife_e2e/models/` copy (kept in sync) (R-2).
- Rewrote `exploration/ife_e2e/run_anchors.py` (R-2/R-3/R-4): module-level A/B, single-pass C
  reading the emitted `generated/inputs/`, Meier channels re-anchored to
  `hif_plant_pkg__hif_plant__driver__meier_cost__*`, no two-pass feedback, no hand-written
  input JSONs, + a perturbed-key rerun. Kept the teax T-1/T-2 OutputRouter/WriteHandler.

**Retirement greps (operative surface = models + `exploration/ife_e2e/*.py`), all ZERO:**
- `sanitize_names` → 0 · `hif_driver_instance` → 0 · `two.pass|second pass|gamma feedback` in
  run_anchors.py → 0 · `bridged` in exploration harness → 0.

**Scope decisions (documented deviations):**
- **Greps scoped to the operative surface.** `work/` (report, WI-015 findings, evidence,
  snapshots), `.project/reports|research`, and demo docs still name the workarounds as
  *historical record* — those legitimately document the workaround when it existed and are not
  mine to rewrite. Only models + harness are the retirement target.
- **`run_anchors_bridged.py` + the report's bridge artifacts kept** — frozen reproduce evidence
  I did not author; deleting breaks the report's Reproduce section. SC-C's spec text names
  sanitize_names/hif_driver_instance/two-pass, not the bridge; the canonical harness is clean.
- **`sweep_ife.py` untouched** — it calls the generated impls directly and never used the
  instance Meier-channel path, so it needs no re-anchor. Its ηG>10 viability check is a KEEP.
- **R-6 (seven `out attribute`): KEPT all.** They are genuine calc outputs correctly marked
  `out`; the report reclassifies them as non-workaround optional style; the vendored codegen
  fixture uses this form; my live run proved all seven extract/wire/execute to 270.12.
  Reverting to `return` is cosmetic-only with regeneration risk. (`cost_billions` must stay
  `out` — consumed channel — so a blanket revert was never on the table.)

### Phase 4 Completion (live legs — license LIVE in this session)
**Completed:** 2026-07-06

**Live leg A — state-(ii) regen + anchors (fusion-tea, commit `2286e5aa`):**
- Regenerated `exploration/ife_e2e/generated` from the workaround-free models: 6 modules
  (was 7), **zero V11 offenders**, Meier channels = `hif_plant_pkg__hif_plant__driver__meier_cost__*`,
  zero `hif_driver_instance` in the YAML, new `system_design` entry-point group.
- Captured the matching **v2** snapshot `work/.../snapshots/ife_workaround_free.snapshot.json`
  (new file, no timestamp-churn gate needed — nothing tracked to diff against); it generates to
  the same zero-offender package license-free.
- Ran the simplified `run_anchors.py` live through the real teax executor — ALL PASS rel 1e-6,
  single pass: **A $252.29996307, B $68.69020165, C $270.12117794** (gamma 68.247088, capital
  3.30388687, COE 4.73540355, f_recirc 0.07222302); **perturbed gain 80→100 → $216.55528392**
  (oracle-matched). Did NOT commit this snapshot into sysml-codegen.

**Live leg B — SNAP-19 parametrized (this repo):** all 6 fixtures + symlinked leg PASS
byte-identical with license (ran in-session, not skipped).

**Live leg C — fusion_tea live-vs-snapshot byte-diff (this repo):** added
`test_fusion_tea_live_vs_snapshot` (`@requires_license`) — live `--models` vs `--from-snapshot`
on the vendored fixture, `_tree_diff == []`. PASSES. (Derisk finding: needs the ABSOLUTE
`--models` path so `source_file` re-absolutizes to the snapshot dir — a relative path diverges
on the docstring source paths; matches the existing SNAP-19 pattern.)

### Phase 5 Completion

---

**Status:** Draft → In Progress → Complete
