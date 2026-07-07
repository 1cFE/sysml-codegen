# Audit: fusion-tea Acceptance & Workaround Retirement (PIPELINE-TRUTH Item 3)

**Verdict:** PASS-WITH-NOTES (Certify)
**Audited:** 2026-07-06
**Branch:** pipeline-truth-epic (this repo) · chore/retire-pipeline-truth-workarounds (fusion-tea)
**Commits:** this repo `36d3394` `c44d7bb` `5946f7c` `74936da` · fusion-tea `5a889ac5` `2286e5aa`

---

## Summary

The item is solid and does what it claims. The audit's crux — the `pipeline_runner.py`
multi-output completion — is a genuine test-harness surface, not a patch masking a generation
defect: zero `src/` lines changed, and the runner change only teaches the in-repo runner to
read the multi-output channel form the (unchanged) generator already emits. All four acceptance
tests pass; I re-derived every anchor number independently and they match to the last place. All
retirement greps return zero on fusion-tea's operative surface; both offender states generate at
true-zero with canonical Meier channels; SNAP-19 parity is green across all six fixtures plus the
fusion_tea leg (license live — all ran, none skipped). Gates match exactly (2066/4/5, ruff 17,
mypy 104).

Two notes, neither a defect: (1) the fusion-tea *real teax* anchor run is attested by their
commit/report and corroborated here by byte-identical wiring + the in-repo executor reproducing
the same numbers — I did not re-execute their separate exec venv in this session; (2) the runner
deviation is fully vetted below.

## Findings

### Plan completion

All five phases verified.

- **Phase 1** (`36d3394`) — `tests/runtime/test_fusion_tea_acceptance.py` (4 tests) all pass
  (re-run this session). Runner completion in `tests/runtime/pipeline_runner.py` is tests-only.
- **Phase 2** (`c44d7bb`) — SNAP-19 parametrized over 6 fixtures; ran green with license.
- **Phase 3** (fusion-tea `5a889ac5`) — deletions + re-anchor + single-pass `run_anchors.py`;
  all four greps zero (re-run this session).
- **Phase 4** (fusion-tea `2286e5aa`, this repo `5946f7c`) — state-(ii) re-capture generates
  zero offenders with canonical channels (I generated it license-free); live legs green.
- **Phase 5** (`74936da`) — run report present, complete, and matches actual outputs.

### Spec conformance

- **SC-A (zero offenders both states) — met.** State (i): `test_fusion_tea_snapshot.py` green
  (3 passed). Regenerating the committed snapshot completes (V11 would abort) → zero offenders.
  State (ii): I generated from fusion-tea's re-captured `ife_workaround_free.snapshot.json`
  (v2) license-free → 6 modules (was 7), completes clean, Meier channels keyed
  `hif_plant_pkg__hif_plant__driver__meier_cost__*`, zero `hif_driver_instance` in the package.
  Consumer `driver_cost_constant` reads the canonical `...meier_cost__gamma` in **both** states
  (`pipelines/pipeline.yaml`) — the instance was never the wired source, so state-(i) true-zero
  holds independent of deletion, as the spec claims.
- **SC-B (run-C reproduces + proven consumed) — met.** `test_run_c_reproduces` → lcoe
  `270.1211779380445` bit-exact. `test_gain_perturbation_is_consumed` moves
  `hif_plant_pkg__hif_plant__lcoe_calc__gain` 80→100 and the lcoe follows to
  `216.55528392479388`. **I re-computed this target independently from `ife_lcoe.sysml`'s DCF
  arithmetic in a standalone script: `216.55528392479388` — exact match.** Anchor A (gamma
  `68.247088`, cost_billions `0.9749584`) and Anchor B (f_recirc `0.07222302470027446`) also
  re-derived independently and match (cost_billions differs only in the float last place,
  `0.9749584000000001`, inside the rel 1e-6 assertion). The perturbed value is a literal, hand-
  derived, never read back from the executor — R1 anti-pattern respected.
- **SC-C (every workaround deleted) — met.** Operative-surface greps (models +
  `exploration/ife_e2e/*.py`), all zero this session: `sanitize_names` 0, `hif_driver_instance`
  0, two-pass/gamma-feedback in `run_anchors.py` 0, `bridged`/`==10` in `run_anchors.py` 0.
  `run_anchors.py` reads the emitted `generated/inputs/` (INPUTS_DIR), single-pass anchor C, no
  hand-written JSONs, canonical Meier channel constants (`CH_GAMMA`/`CH_CB` under prefix
  `hif_plant_pkg__hif_plant__`). Historical-reference scoping is recorded (report §SC-C + Phase 3
  notes): `work/`, `.project/reports|research`, demo docs keep the workaround names as historical
  record — a documented, defensible scope decision.
- **SC-D (SNAP-19 parametrized + live leg) — met.** `test_live_vs_snapshot_byte_identical` ran
  green over all 6 fixtures; `test_fusion_tea_live_vs_snapshot` green; symlinked leg green — 8
  passed, 0 skipped (license live). Full-tree `_tree_diff` includes `pipelines/*.yaml`, so it is
  channel-identity, not a vacated-`fallback_entry_points` check; the inline comment pins this and
  Phase 2's R1 probe (repoint a channel → gate fails) is recorded.

Non-goals respected: teax T-1/T-2 router kept; ηG>10 constraint stays harness-side; no resolution
code built or changed in this item.

### Design conformance

No design doc (execution item, by plan). The plan's two-venue split holds: this repo carries the
license-free acceptance proof + parity tests; fusion-tea carries the deletions + re-anchor +
state-(ii) capture. The plan's reconciliation deviation (in-repo license-free SC-B rather than
the spec's literal "only the SNAP-19 test") is documented and is the lower-risk, CI-visible home
for the headline number. Sound.

### Code integrity

**The crux deviation — `pipeline_runner.py` multi-output completion — is honest.** Two additions,
both test-harness:

1. `_install_simkit_stub` adds `simkit.config.schema.MultiOutput` aliased to pydantic
   `BaseModel`. This is the *fake* simkit the runner installs; a generated multi-output wrapper
   does `from simkit.config.schema import MultiOutput`, and the runner reads each field via
   `getattr`. The stub is the only surface the runner needs.
2. `_resolve_source` adds a third source form: a bare channel name (no `.root`) for multi-output
   upstream channels. This matches the *emitted* YAML: e.g.
   `driver_cost_constant: float hif_plant_pkg__hif_plant__driver__meier_cost__gamma`
   (`pipelines/pipeline.yaml:70/82`) — a bare channel reference the generator already produces.

The ordering (`.root` → bare channel → entry point) is safe: entry-point tokens carry a
`<group>.<QN>` dot and bare multi-output channels do not, so no shadowing. The generator (`src/`)
was untouched (`git show --stat 36d3394` = only `tests/` + plan); the in-repo runner was simply
single-output-only because no prior fixture (twolevel) exercised multi-output. This is a reader
completing to match a correct emission, not a defect being papered over.

No slop or failure-honesty issues: no broad excepts, no silent fallbacks, no invariant-swallowing
defaults introduced. The unresolved-channel path still raises `KeyError`.

## Cross-repo hygiene

- fusion-tea branch `chore/retire-pipeline-truth-workarounds` is off `epic/pipeline-derisk-demo`
  (confirmed ancestor).
- git status: their in-progress `.project/` edits and `*_bridged` artifacts are pre-existing
  untracked/modified and untouched; the two retirement commits are pathspec-scoped.
- Commit messages carry the `Co-Authored-By:` trailer.

## Notes (not gaps)

1. **Real-teax leg attested, not re-executed here.** fusion-tea's `run_anchors.py` through their
   exec venv (A $252.30 / B $68.69 / C $270.12117794 single-pass, perturbed → $216.56) is
   recorded in commit `5a889ac5` and the report. I corroborated it two ways without their venv:
   the in-repo `run_pipeline` reproduces the same numbers on byte-identical wiring, and
   `test_fusion_tea_live_vs_snapshot` proves live emission == snapshot emission. Strong indirect
   evidence for the audit's actual concern (correct wiring as emitted).
2. Runner deviation vetted above — no action.

---

## Certification

Verified and marked:
- Spec SC-A/B/C/D already `[x]`; confirmed each against re-run evidence.
- Epic Item-3 heading appended `✅`; all four Item-3 success-criteria checkboxes marked `[x]`.

Checked this session: 4 acceptance tests (re-run, pass); independent arithmetic for all anchor
targets + perturbed lcoe (exact match); 4 retirement greps in fusion-tea (zero); state-(i) and
state-(ii) generation (zero offenders, canonical channels); SNAP-19 parametrized + fusion_tea +
symlinked legs (8 passed, license live); gates (suite 2066/4/5, ruff 17, mypy 104); fusion-tea
branch base / status / trailers.

Open only as a session limitation, not a defect: fusion-tea's teax executor was not re-run in
this audit (needs their separate exec venv); corroborated indirectly per Note 1.

ARTIFACT: .project/active/fusiontea-acceptance/audit.md
