# Current Work

**Last Updated**: 2026-07-20

---

## Active Work

### CONSTRAINT-LIFECYCLE Item 11 — TEAx Constraint Evidence Durability (TEAx-owned) — ✅ CERTIFIED 2026-07-20
**Audit verdict: Certify** (`audit.md`). Reproduced independently (not trusted): C1 positive
write-phase signal (set-before/clear-on-success, no `finally`; entry-load→MODULE_EXECUTION,
unwritable output_dir→OUTPUT_WRITE, router-setup test flipped honestly); M1 six migrated sites
faithful; M2 frozen tree reproduced defeating nested status/margin/results mutation AND emitting
non-finite tags at depth (byte-identity crux) AND MF-3 firing inside the seal; M3 corruption raise
+ catalog authority ground-truth (constraint_free/excluded_only→False, sealed_package→True).
Teax **310 passed**; codegen source untouched vs `b987869` (docs-only diff); Items 8/9 surfaces
green; ruff clean; mypy errors pre-existing/unrelated. Four **Minor** non-blocking findings: (F1)
M3 catalog→corruption effect asserted only via forced flag, not end-to-end through cli.py; (F2)
design's "two-fingerprint control" delivered as fingerprint-scoping + store-incompat rejection
instead; (F3) INV-G "golden" is a round-trip proof, no captured pre-D2 byte golden; (F4) residual
legacy `toy_plant_params.json` fallback in `_entry_artifact_path` (safe, fails loud, no fixture).
All 7 spec SC marked met. **Candidate teax `c342b10`** on `constraint-exec-epic` (not pushed; Item 13
owns push); artifacts at `.project/active/constraint-lifecycle-evidence-durability/`. Next:
`/_my_pre_pr` / Item 13 push.

### CONSTRAINT-LIFECYCLE Item 10 — Producer Completeness + Stellarator Rollup — ✅ CERTIFIED + Major 1 CLOSED 2026-07-20
**Audit Major 1 closed:** the completeness check's MODULE_OUTPUT exemption left channel-tier name-based
rows (leaf_parent_scoped/leaf_consumer_scoped) uncaught for qualified terms — now flagged (check keys on
name-based key_form + qualified ref, regardless of outcome; chain_redefinition_follow + exact rows exempt).
2959 pass, corpus byte-clean. The revert-rationale loud guard is now airtight. WI-015 #4 root closed;
stellarator bridge-free, six anchors bit-exact, five verdicts satisfied.
**Audit verdict: Certify** (`audit.md`). Reproduced independently: 2956-test corpus green (licensed);
`run_stellaris_single.py` reran in the exec env → six anchors bit-exact, five verdicts satisfied,
single-pass, oracle reldev 0.00e+00; bridge/glue-2/handshake-rollup absence-checked; WI-027 D7
supersession present; five `resolve_producer` sites covered by the centralized sink; resolver fix
(per-child `:>>` capture + dual-scope row-13 follow + transitive instance-scoping) sound and byte-clean.
**Surfaced Major (owner ruling requested):** the producer-completeness check's guarantee is NOT airtight
— it exempts all `MODULE_OUTPUT`, so a qualifier-drop collapse via the channel-tier name-based rows
14–15 (`leaf_parent_scoped`/`leaf_consumer_scoped`) is uncaught (the design-attribute `leaf_unique`
path IS caught). Latent (no fixture trips it; the stellarator resolves at row 13), diagnostic not a hard
gate — does not affect the delivered acceptance, but the "completeness check is the loud guard" rationale
for the reverted global refusal holds only for the design-attribute tier. Spec SC2 marked met-as-mechanism
with the documented gap; SC1/3/4/5/6 verified-met. Evidence stale note: `handshake_comparison.json` WAS
refreshed (stellarator `342cc799`, the anticipated diagnostic-snapshot commit); evidence text not updated.
Next: `/_my_pre_pr` then `/_my_close` (certification stays ordered behind Item 9 per the register).

---

### (prior) CONSTRAINT-LIFECYCLE Item 10 — WI-015 #4 CLOSED; public gen proven 2026-07-20
Phases 0/1/2 done. The blocking finding (cross-part child.attr collapse) was ratified in-scope and
FIXED (general resolver mechanism, no rollup arm): (a1) capture per-child :>> redefinitions, (a2)
dual-scope channel follow, (a3) transitive instance-scoping for aggregation-composing sums. Global
_leaf_unique refusal tried+reverted (moved relied-upon behavior). Stellarator: 13-term collapse → 0
completeness violations, 0 V11 offenders; public generation (no bridge) EXIT 0 with constraint modules.
Byte-clean: 2956 pass. Stellarator staged formulas restored + snapshot recaptured (v5) + WI-027 amended
(D7 superseded by D-2). CANDIDATE_REVs: codegen ce09bb2, stellarator 0a8add96. **Remaining last-mile
(teax exec env):** numeric run (6 anchors + 5 verdicts), physical bridge/glue deletion, single-pass
runner cutover. Anchor movement = STOP. Evidence: evidence.md.
Phases 0/2 landed earlier (capture sink, completeness check, RED coordinate). Phase 1 (this
session, licensed): FORMULA→aggregation routing built (Step 4.7 `_route_crosspart_formula_aggregations`),
byte-identity sweep CLEAN (2953 pass), A7 chained-aggregation PROVEN on the real stellarator
(LocalTerms→module_output). Completeness check refined to qualified-ref-only leaf-guess (zero false
positives). **BLOCKING FINDING (STOP):** cross-part `child.attr` SingletonTerms collapse — the resolver
drops the part-usage qualifier and leaf-matches (`magnet.capital_cost`→one magnet EP; 13-way collapse).
The design's Decision-1 premise ("aggregation path already resolves cross-part refs") is empirically
false; the check catches it (13 leaf_name_guess violations). Phase 3 BLOCKED — needs a resolver
enhancement to follow child-part redefinitions per instance. Surfaced, not worked around. Evidence:
`evidence.md`.
Design approved-with-revisions (four Majors applied, `design-review.md` + `design.md`).
Implemented and verified: capture sink centralized in `resolve_producer` (covers all 5 call
sites by construction — closes R2), `producer_completeness.py` check, and the RED-first
ambiguous/defaulted acceptance (license-free, real resolver+check). 2952 pass / 0 fail / 44
license-skip; ruff clean; no mypy added. **Remaining:** Phase 1 (cross-part aggregation routing
+ 15-fixture byte-identity + gate wiring) and Phase 3 (stellarator cutover — license + teax env,
bit-exact anchors, both-harness deletion, WI-027 amend). Evidence: `evidence.md`. Anchor
movement is a STOP. Stopped for audit after Phases 0/2.
Spec: `.project/active/constraint-lifecycle-producer-completeness/spec.md`. Two faces of one rule
(producer completeness independent of V11): (1) ambiguous/defaulted producer acceptance, RED-first;
(2) codegen compiles the stellarator cross-part capital aggregation as a real graph producer,
retiring the private bridge/placeholder/two-pass glue and amending WI-027 (D7 superseded by D-2).
Measured distance at today's chain: Gate A/B resolved (Items 2/3); the bridge's sole remaining job
is the cross-part capital sum codegen still can't compile (`calc_compat_renderer.py:103`).

### CONSTRAINT-LIFECYCLE Item 9 — Multi-Entry Candidate Bridge (TEAx-owned) — spec drafted 2026-07-20

### CONSTRAINT-LIFECYCLE Item 9 — Multi-Entry Candidate Bridge (TEAx-owned) — CERTIFIED (independent audit 2026-07-20)

**Audit verdict: Certify.** `.project/active/constraint-lifecycle-multi-entry/audit.md`. Every
executable gate reproduced first-hand across all three repos at the audited commits (codegen
`240d170`, teax `07eb0ac`, fusion-tea `2422e715`). The three design-review Majors verified: **R1**
RED (uncaught `EvaluationFailed` with `bridge.build` outside the switch) → GREEN (`StudyBridgeDefect`),
reproduced by relocating the call and reverting; **R2** both baseline arms (fully-defaulted builds;
defaultless-unselected fails closed, never invented); **R3** `prove_catalog_seam.py` migrated off the
config scalars and green. Coordinates: zero end-to-end (`zero_channel` fixture, constraint-BEARING per
Item-11 firewall labeling), one, and the IFE 2301/2301 100%-agreement run all green through the stock
bridge, no wrapper. Codegen production delta = template + `sample_model.yaml` ONLY (byte-identity
airtight: `{% else %}` reachable only at zero channels); full licensed codegen suite **3084 passed /
44 skipped**, license loaded; teax full suite **301 passed**. Deletion inventory verified: zero code
survivors (`MultiChannelEvaluator`/`ThreeChannelEvaluator`/config scalars/bench usage all gone).

Minor honesty note (non-blocking): evidence §7 and the line below cite codegen `5a72366`, but the
actual audited HEAD is `240d170` — stale hash in the record, not a code defect. Full discrepancy list
(counts, fingerprint wording, docstring residual) in audit.md.

### CONSTRAINT-LIFECYCLE Item 9 — Multi-Entry Candidate Bridge (TEAx-owned) — IMPLEMENTED, stop for audit (2026-07-20)

Epic row 11 / CE-F2. Stock TEAx bridge now builds complete typed mappings for zero/one/many entry
channels; fusion's `MultiChannelEvaluator` (+ `ThreeChannelEvaluator`, `bench` usage) deleted.
Spec/design/design-review/evidence + codegen-gap finding at
`.project/active/constraint-lifecycle-multi-entry/`. Design-review R1–R5 applied before implementing.

**Landed:** teax `CandidateBridge(entry_models)` (partition by `model_fields`, fail-closed
unknown/malformed → `EvaluationFailed(ENTRY_VALIDATION)`, A2 ambiguity guard); **R1** `bridge.build`
relocated inside the runner failure switch (RED captured: uncaught `EvaluationFailed` before the
move); `StudyDefinition`/`StudyConfig` scalar `entry_channel`/`entry_model` deleted, fingerprint
basis moved (R5 store no-silent-rebind gate green). fusion study green through the stock bridge:
**2301/2301 IFE cases, 100% agreement, no wrapper**; Item-8 seam proof still green.

**Codegen gap found + ROUTED, not shimmed (Phase-0 A3 falsified):** codegen omits the EntryPoint
module at zero entry channels (`pipeline_yaml.jinja2:11`), so a zero-entry package is rejected by
stock TEAx (`Pipeline must declare exactly one EntryPoint module`). Zero *bridge shape* proven at
the unit level; zero *end-to-end package* parked on a codegen fix (owner TBD — Item 13 / codegen).
See `codegen-gap-zero-entry.md`.

**Gates:** teax full simkit `298 passed`; ruff clean; mypy zero-added; codegen source untouched.
Candidate revs: **codegen `5a72366`** (supersedes source-pin `589c8c4` — zero-entry template fix), **teax `07eb0ac`** (fixture+test) / `96578a4` (bridge), fusion-tea `2422e715`. Zero-entry gap FIXED in codegen same landing unit; zero end-to-end coordinate now a committed real package (301 teax passed; codegen 3083 licensed). Nothing pushed (Item 13 owns push).

### CONSTRAINT-LIFECYCLE Item 8 — Canonical Embedded Catalog and Store Transition — CERTIFIED (independent audit 2026-07-20, pass with notes; all notes now closed)

**Audit verdict: Certify — pass with notes.** `.project/active/constraint-lifecycle-catalog-store/audit.md`.
The item delivers its substance and every executable gate reproduced first-hand. Candidate revs:
codegen `19b74ac` (Phase 1) / teax `a5594e1` (Phase 2) / fusion-tea `667136fa` (Phase 3, branch
`item8-fusion-embedded-catalog`). Gates reproduced: codegen full suite **3080 passed / 44 skipped /
17 deselected** (catalog conformance non-vacuous); catalog surface 12 passed; teax **286 passed** +
skew 5 passed (both directions fail closed); fusion seam proof GREEN (schema 2.0.0, 1 eligible entry,
def→usage join `fusion_cycle::'Viability Threshold'`, verdict satisfied) + 6 package tests. The
alternate system (byte-hash stand-in, standalone `constraint_catalog.json`, fusion materializer) is
genuinely gone across all three repos, no shim; the six design-review Majors (F1–F6) landed in code.

The two moderate findings were missing regression guards (behaviour verified correct), now closed:
**F-A** — the F1 named-inline FK branch was vacuous; `constraint_inline` added to the parametrization
plus a dedicated named-inline test (codegen `82ad686`), branch now armed. **F-B** — the INV-6
source-scan the spec/design name was missing; now landed both sides: teax consumer scan
`tests/study/test_no_reconstruction.py` (`8286893`) and codegen producer scan
`tests/conformance/test_catalog_no_reconstruction.py` (follow-up), and the surviving alternate-schema
names `CatalogView`/`_Catalog` are renamed to `EmbeddedCatalogView`/`_EmbeddedCatalog` (no name
survives the deletion table). Minor notes closed: **N1** — `prove_catalog_seam.py` now sweeps stale
`.pytest_cache` before load so a reproducer starts clean; **N2** — Item-9 breadcrumb on the stale
`MultiChannelEvaluator` inline in `run_viability_study.py` (fusion `d7f7492d`). Evidence:
`.project/active/constraint-lifecycle-catalog-store/evidence.md` (audit-close section). Stellarator
demo repo untouched. Nothing pushed (Item 13 owns the push).

Epic `epic_constraint_execution_lifecycle_remediation.md` register row 10; operationalizes owner
decision D-3 (settled: codegen's embedded catalog is the sole schema authority). Spec + design at
`.project/active/constraint-lifecycle-catalog-store/`. Deletion inventory grounded across codegen +
teax + fusion-tea. Orchestrator rulings recorded: fusion-tea (not `-stellarator-mbse-demo`) is the
deletion target; no active store migration (pre-release stores; archival invariant + existing
eight-field no-silent-rebind gate suffice). Design settles the parked questions with code evidence:
three-tier catalog (add per-usage tier + 4 projected entry fields + `definition_qualified_name` FK
recorded at lowering), skew guard via `contracts/versions.py` central pin + TEAx vendored accepted
set (composes with Items 4/7, no new version machinery), phasing codegen→TEAx→fusion with the IFE
study proven green on the real catalog before the materializer dies. Next: `/_my_design_review`.

### CONSTRAINT-LIFECYCLE Item 7 — Trusted Package Bootstrap and Seal Provenance — CERTIFIED (independent audit 2026-07-20, candidate codegen `280a2bd` / teax `98a6d07`)

**Audit verdict: Certify.** `.project/active/constraint-lifecycle-package-trust/audit.md`. Both
attacks reproduced RED against pre-fix (loader reverted to `98a6d07^`; codegen src to `280a2bd^`),
GREEN at HEAD; working trees restored clean. All four design-review Majors verified landed in
code and design prose (no second review round needed): TOCTOU closed (compile+exec of read
bytes, no `exec_module`); single-version policy, both skew directions named, bare literal zero
survivors; manifest = tree-minus-globs with foreign-file-in-non-glob → hard fail, and the
consumer-anchor-vs-producer-gate honesty prose + seal-signing Non-Goal present; churn claim holds
(no `baseline_outputs`; teax diff = loader + test + enumerated re-seals). D3 fixtures at canonical
`ad0a855`, version unchanged, nothing else moved. Battery reproduced: codegen **3068 passed / 44
skipped / 0 license skips**, teax **281 passed**, certified Item-6 surface **59 passed**, mypy
**72** (base 73, +0), ruff clean. Items 1–6 acceptance surfaces untouched (scope = contracts/CLI
+ teax loader only). Epic Item 7 heading ✅; all 5 epic + 6 spec success criteria marked.
**Not checked:** full `-O` suite tally (flagged file confirmed assert-strip artifact, Item-7
code untouched); agentic-mbse not diffed (design claims no diff; scope consistent); the PR push
(Item 13's). Evidence hygiene note: `evidence.md:165-166` still carries CANDIDATE_REV placeholders.

Epic rows 8–9. Cross-repo (sysml-codegen + TEAx). Design + design-review (Approve-with-revisions,
4 Majors applied) + evidence at `.project/active/constraint-lifecycle-package-trust/`.

Both named attacks driven RED-first then GREEN:
- **Attack (a)** unconditional-success verifier — TEAx loader now authenticates the package-local
  `verify.py` bytes against a vendored `TRUSTED_VERIFIER_SHA256` and execs *the hashed bytes* (no
  `exec_module` re-read; TOCTOU closed). Rejected before any package code runs.
- **Attack (b)** foreign-file laundering — codegen emits `contracts/generation_manifest.json`
  (tree-minus-globs codegen set); a CLI-level `cmd_seal` provenance gate hard-fails a foreign or
  edited-generated file. Pure `seal_package` + both walkers untouched.
- **Version skew** — bare `package_load.py:22` literal deleted; single-version
  `ACCEPTED_RUNTIME_CONTRACT_VERSIONS` fails closed both directions with a named diagnostic.
- **D3 drift** — the two stale TEAx fixtures re-sealed to the canonical verifier (enumerated).

Battery green: codegen 3068 passed (0 license skips) + execution 17; teax 281; mypy/ruff no-new;
`-O` 2 failures pre-existing (confirmed on base). Candidate commits: codegen
`<CANDIDATE_REV_CODEGEN>`, teax `<CANDIDATE_REV_TEAX>` — **not pushed** (Item 13 owns the push).

### CONSTRAINT-LIFECYCLE Item 6 — Public Documentation and F1 Evidence Reconciliation — CERTIFIED (independent audit 2026-07-20, candidate `f917787` / TEAx `db23719`)

**Audit verdict: Certify (no findings).** `.project/active/constraint-lifecycle-docs-f1/audit.md`.
Light reconciliation item; every one of the seven requested areas reproduced first-hand.

- **S1–S8** — all eight STALE corrections now make a claim that is TRUE against landed code:
  snapshot v5 (`snapshot/__init__.py:28`), profile v4 (`_upstream_pins.py:33`), mbse floor
  0.1.2 (`pyproject.toml:24`), root-N portable referent (doc 27 §source_file), matrix
  REQ-SNAP-09 "current: 5". S7/S8 single-sourced from `PROFILE_SEMANTIC_VERSION`; pinning test
  regex-hardened (`r"executable-profile/v\d"`); `grep executable-profile/v3 src docs tests` empty.
  ("package 0.1.2" = the mbse *dependency floor*; codegen's own package is 0.1.0, correctly
  stated unchanged.)
- **TEAX_SIMKIT_PATH** — genuinely RED-first. Reproduced RED against the parent helper
  (`f917787^`: "DID NOT RAISE RuntimeError"), tree restored clean; GREEN at HEAD (6 passed);
  explicit path authoritative with no sibling fallback; unset/default unchanged; tests-only scope.
- **F1 at d545701** — `927a9e1` is docs-only (provably lacks the F1 change); `d545701` carries
  `pipeline_executor.py`/`evaluator.py`/tests. TEAx `db23719` corrects `audit.md:6` (1 line);
  `design.md:9` correctly left at 927a9e1. 15-test cluster GREEN. `OUTPUT_WRITE` honest —
  defined at `failure.py:23`, never emitted (evaluator sets only MODULE_EXECUTION/PREPARATION);
  Item 11's obligation, recorded not reimplemented.
- **PR drafts** — accurate against the local chain, zero release-readiness claims, correct
  merge order (agentic-mbse #11 first — the `_upstream_pins` guard). Item 13 owns the push.
- **"Already accurate" spot-checks** — V11 settled branch (only invoking caller of
  `collect_uncovered_params` is the final gate `cli/__init__.py:278`) and embedded catalog
  (no `constraint_catalog.json` in `src/`) both hold.
- **Surfaced gaps G1/G2** — recorded as decisions with ownership (Item 4 / Item 13), not
  instructions to future agents. Correction law honored; no "used to say X" prose.
- **Gates** — full suite **3064 passed / 44 skipped / 0 failed** (license sourced, no bare
  license skips); mypy **72** (baseline); no fixture/`baseline_outputs` bytes touched.

Epic Item 6 heading ✅; all 4 epic success criteria and spec §6 marked. **Not checked:** ruff
not re-run (evidence claims clean; small touched surface); the actual PR push (Item 13's).

### CONSTRAINT-LIFECYCLE Item 5 — Whole-Tree Snapshot Portability — CERTIFIED (independent audit 2026-07-20, candidate `4c6223c`)

**Audit verdict: Certify (three non-blocking notes).** `.project/active/constraint-lifecycle-portability/audit.md`.
Every priority reproduced first-hand. Two-root proof GREEN on two **fresh** fixtures the proof
never used (solar_battery 0/115, fusion_tea 0/47) at genuinely different roots — zero diff, zero
absolute-.sysml. Licensed A2 relocated anonymous leg (`OccurrenceDemandAnonymous__Admitted`)
GREEN, not skipped — closes Item 1's named open leg; admitted 3.0 preserved. v5 shape gate
rejects absolute + snapshot-relative + version skew loudly (closes Item 4 N1); anonymous
constraint_id folds the referent with **zero** Item-4 impact (catf_mfe has 0 anonymous-located
usages; manifest SHA unchanged, GREEN). Deletion real: `_reabsolutize`, Branch C `"models/"`
strips, baseline `.replace()`, `os` import — all gone, no shim; three schemes → one `root-N/`.
Re-capture: 36 snapshots all v5, field-classified deltas exactly {source_file, captured_at,
location.file, version}. Deferred gates run: execution lane 17 passed, `-O` 58 passed on changed
surface, ruff clean, mypy 72 (zero added). Premise corrections honest — design_attr keys still
absolute in snapshots (surfaced) but **proven** not to reach output (grep empty across all
baselines). D3 deferral sound (basename already portable). Epic row 5 ✅; all 4 epic + 6 spec
criteria marked. **Notes (non-blocking):** N1 live `--models` docstring parity pinned only
transitively (machinery fail-loud, can't silently leak); N2 graph_builder sentinel set diverges
under a "kept in sync" comment (benign, graph-layer-only); N3 evidence says design_attr-key
non-portability is "gated by the two-root diff" — strictly the diff cancels for snapshot-baked
absolutes; the scan axis is the real gate (implementer understands this per finding #1).

<details><summary>Spec+design record (pre-audit)</summary>

Epic register row 5; deps Item 4 (closed). Combined spec+design at
`.project/active/constraint-lifecycle-portability/spec-design.md`. Absolute-byte inventory
**measured** license-free (two roots, `catf_mfe`): 40/81 generated files differ — the leak is
`SysML Source: <abs>:<line>` docstrings in modules/stencils/output-schemas plus the seal's
`package_contract.json`; `model_contract.json` is already portable (certified `root-0/` referent).
Root cause: the loader re-absolutizes the portable snapshot-relative `source_file`
(`_reabsolutize_source_files`) and docstrings render it. Recommended design (D1): generalize the
certified `root-N/` referent to every `source_file`, delete the re-absolutization + the two
`"models/"` hacks, bump snapshot v4→v5 with a shape gate (closes Item 4 N1). Open for owner:
the v5 format-bump-vs-no-bump call. Completes Item 1's relocated `OccurrenceDemandAnonymous__Admitted` leg.

</details>

### CONSTRAINT-LIFECYCLE Item 4 — Diagnostic severity and modeled-default fidelity — PASS WITH NOTES (round-3 audit 2026-07-20, candidate `caa149c`)

**Round-3 verdict: all four findings closed; two non-blocking notes.** F2 was closed at `caa149c`
by moving the discriminator to the written scope qualifier captured from the CST byte span at
extraction (`usage_extractor.py`), deleting both prior resolution-based guards
(`producer_resolution.py` row 16). Verified across all three sentinel shapes — fusion_tea
`driver_efficiency` instance-scoped, catf_mfe `kappa` and shadowed_reference `factor` at the outer
key (2.0, not the 7.0 shadow) — and pinned on both routes by `test_written_qualifier_anchoring.py`
(6 tests, none skipped) with a committed baseline. Gates at `caa149c`: **3056 passed / 0 license
skips**, mypy 72 (zero added), ruff clean, `-O` clean but for the two pre-existing assert-stripped
tests. Scope disciplined (5 source files, all F2; Item-2 seam byte-unchanged).

**Two notes for the owner before merge (not blocking):**
- **N1 — v4 amended in place.** `source_written_qualifier` was added to the snapshot without a
  version bump. A field-less v4 snapshot loads with no error and reintroduces F2 (I reproduced it:
  `shadowed_reference.factor` → 7.0 shadow). The ratified premise (no field-less v4 anywhere a gate
  must catch) is verified today — the committed corpus is fully re-captured and the branch is
  unmerged — but no test guards field presence, and this contravenes DD-R12's own "one version, one
  payload" rationale. Merge (PR #11 before PR #9) is when the premise stops being free. Cheap close:
  a test asserting every committed v4 snapshot with reference bindings carries the field.
- **N2 — error-path degradation.** `_written_reference_text` returns `None` on any CST/file/decode
  failure, and `None` is treated as a bare leaf → re-anchor → F2. The fix's correctness silently
  depends on the byte span always being recoverable; failures fail toward the defect.

Also: the superseded round-1 FD-1 table (`evidence.md:504-513`) still carries the false fusion_tea
`.`-chain convergence row and "six fixtures," cured only by a later supersede note (`:659`) —
correction-by-appendix, same pattern flagged for DD-A06.

<details><summary>Round-2 record (candidate <code>765e8b8</code>) — F2 was open here</summary>

**Round-2 verdict: three of four findings closed; F2 was not.** Gates at `765e8b8`: 3050 passed / 0
failed, zero license skips, mypy 72 (zero added), ruff clean, agentic-mbse 1811 unchanged at
`4c18d61`.

- **F1 closed.** Sink moved above `build_full_graph_from_snapshot`; my call-order probe now returns
  `['screen_extraction_diagnostics', 'lower_constraints']`, pinned by a test that records real call
  order and cannot pass vacuously.
- **F3 closed.** `diagnostic_screen.py` coverage 63% → **100%**; 8 tests, both routes, plus the
  `non_finite_literal` end-to-end fixture. Both structural limits verified as facts — the serializer
  really does refuse non-finite floats (reproduced: `ValueError ... inf`), and the advisory branch
  really is unreachable with the one-entry table.
- **F4 closed as Met-with-exception.** False claim deleted, honest boundary stated, disagreement
  pinned by `test_default_lane_disagreement.py`, root cause recorded with a four-fixture blast
  radius as an unowned open item. Criterion 4 correctly stays unchecked.
- **F2 NOT closed → F2b.** The guard fires on `sanitize_qualified_name(req.reference) in
  ctx.design_attr_by_qn` — resolution, not written form — so it also captures the bare-leaf shape
  row 16 exists to serve. Verified across revisions: `fusion_tea`'s
  `hif_plant__driver__meier_cost.driver_efficiency` moved from instance-scoped
  `hif_plant_pkg__hif_plant__driver__efficiency` (`16dbaa7`) to definition-scoped
  `hif_driver__HIF_Driver__efficiency` (`765e8b8`), collapsing two instances onto one parameter.
  Masked by 0.35/0.35 and by fusion_tea having no committed baseline — the same pattern F2 was
  raised about. Plus F2c (`shadowed_reference` fixture has no test) and F2d (FD-1's corrected table
  mis-sums 24-as-23, says six fixtures where it is seven, and still claims the fusion_tea
  convergence the fix removed).

To clear: re-scope the guard by written form and re-check the corpus for guard-induced movement;
attach a test to `shadowed_reference`; correct FD-1; amend DD-A06 in place rather than by appendix.
Spec/epic criterion 1 re-checked by round 2; criterion 4 stays open; no ✅ on the epic heading.

</details>

<details><summary>Round-1 record (candidate <code>16dbaa7</code>)</summary>

Epic register row 4. Artifacts at `.project/active/constraint-lifecycle-diagnostics-defaults/`
(`spec.md`, `design.md` — which holds the phased plan, no separate `plan.md` — `design-review.md`,
`evidence.md`, `audit.md`, `briefs/`).

**Audit verdict: Needs Work.** Every gate reproduces exactly (3040 passed / 0 license skips, 72
mypy, 1811 upstream, the pinned FD-1 set with no extras) and PC-3 — the certified-seam fingerprint
rewrite the brief flagged as highest-risk — is sound in all three respects, guard verified to fire.
Three findings block certification:

1. **F1** — on the snapshot route the blocking-diagnostic sink runs **after** lowering
   (`snapshot_context.py:34` lowers via `graph_rebuild.py:213`, sink at `:42`). Proven by a call-order
   probe. PC-4, DD-R09, design D2, and the module docstring all claim before-lowering on both routes.
2. **F2** — the carry re-anchored `catf_mfe`'s `plasma_region` kappa binding from the outer
   `catf_radial_build::elongation` the model explicitly names onto an owner-local shadow, diverging
   from its thirteen identical siblings. Masked because both hold 3.0. FD-1 records it as
   "convergence onto correct scope." `::` qualifiers lose their qualifier the way `.` chains did
   before PC-1.
3. **F3** — DD-A03's "proven by unit surface" is false: `screen_extraction_diagnostics` has **zero**
   test coverage on either route (raise, advisory log, and `_render` all uncovered), the advisory
   branch is unreachable given the one-entry severity table, and the e2e fixture is ~20 lines, not
   costly. Should read Fail, not Partial.

Also: F4 (the retained string lane and the IR lane disagree on the same modeled default — 5.0 vs
explicitly unresolved), plus notes on FD-4's unnamed seventh delta class (582 vs 594), the
non-existent "retained v3" fixture, and the merge-order failure presenting as an ImportError at
collection rather than the guard's message. Spec/epic criteria 1 and 4 unmarked; no ✅ on the epic
heading.

</details>

**Audit round 1: Needs Work — all four findings closed.** F1 snapshot sink ran after lowering
(fixed, ordering now pinned). F2 the carry re-anchored a `::`-qualified reference onto an
owner-local shadow, masked because both attributes held 3.0 (fixed by "exact identity beats
re-anchoring", scoped to the calc consumer so Item 2's certified precedence is untouched; a
discriminating fixture with *different* values now exists). F3 DD-A03 was Fail not Partial — the
sink had zero coverage (fixed, 8 tests + fixture). F4 the string lane's retention justification was
falsified (corrected and pinned; root cause surfaced with its four-fixture blast radius, not fixed
here). Detail in `evidence.md` under "Remediation".

**CANDIDATE_REVs:** see `evidence.md` — `16dbaa7` was audit round 1; the remediated codegen rev is
`4c18d616f77e26932a8e158cefc2637db47f9b07` (agentic-mbse), both on `constraint-exec-epic`.

**This item MOVES the Item 0 agentic-mbse pin** `515e08bb` -> `4c18d61`. Merge order is
load-bearing: **agentic-mbse PR #11 before sysml-codegen PR #9**. Merging #9 first leaves main
pinning `constraint-facts/v2` against a v1 upstream and the `_upstream_pins` guard test fails on
main.

**Delivered.** Diagnostic severity as a versioned field (`constraint-facts/v2`, snapshot envelope
v4, 35-snapshot licensed re-capture) with both skew directions failing closed on both routes and two
load-bearing sinks. R-8 warning totality with zero Item-1 pinned bytes moved. The tier-2
malformed-literal silence closed as a new log record. Signed and unit-annotated modeled defaults
surviving to the generated JSON, with unsupported IR explicitly unresolved and diagnosed rather than
silently omitted. The written-reference carry closing SR-A02 on real data.

**Gates:** codegen 3040 passed / 0 failed, zero licence skips; agentic-mbse 1811 passed; `-O`
identical except two pre-existing assert-stripped tests; mypy zero added in both repos; ruff clean.

**Three things the audit should look at hardest** (evidence PC-1/PC-3, DD-A03):

1. **PC-1 — a design bet was amended mid-implementation.** B2 said the written reference equals
   `source_attribute_name`; that is false for CHAIN bindings, where the leaf alone re-anchors at the
   wrong owner. `catf_mfe`'s `cryo_pumps.n_pumps` selected the outer `n_pumps` (48.0) instead of
   32.0. Gate 2 caught it; the chain-aware form was ratified.
2. **PC-3 — a certified-seam test mechanism was rewritten.** `test_fingerprint_stability`'s policy
   test could not be repinned: no revision carries both the old verifier policy and the new
   entry-point keys. It now takes only `verify.py` from the reviewed revision, with a new guard that
   fails loudly if that revision ever stops differing.
3. **DD-A03 is claimed partial.** Both sinks are load-bearing and proven at the unit surface, but no
   fixture carries a real blocking extraction diagnostic end-to-end.

**Carried forward, unowned:** bracketed-owner convergence (deliberately not claimed — row 16 safely
misses for an occurrence-indexed `part_def` owner); the stale-baseline class (`plant_values`,
`constraint_inline`, the `dropped_constraints` capture drift, joining the recorded
`deep_cross_scope` case — all three reproduce at the parent commit); the tier-1 mirror of DD-R32.

### CONSTRAINT-LIFECYCLE Item 3 — Gate B vacuity proof and deletion — CERTIFIED, pass with notes (independent audit 2026-07-19 at `3df2c34`)

Epic register row 3. No spec/design pair by owner pace directive — the provenance-marked
`decision.md` replaces them. Artifacts at `.project/active/constraint-lifecycle-gate-b/`
(`decision.md`, `findings.md`, `upstream-filing.md`, `audit.md`, `briefs/`, `probes/`).

**Delivered.** Extension-time whole-graph V11 coverage check deleted from
`extend_graph_with_constraints` — the collector call, its raise, and its import name. Production
diff is one file, 11+/10−. Justified by a closed enumeration showing extension cannot introduce a
V11 offender. `collect_uncovered_params` retained for the generation gate (`cli/__init__.py:263`,
`:278`); `_validate_channel_references`, strict actual resolution, and both call sites unchanged.
No replacement wrapper. LC-E02 settled to its no-check branch, superseding lowering INV-6.

**Audit.** Pass with notes — `.project/active/constraint-lifecycle-gate-b/audit.md`. The
conclusion survives adversarial attack: no model-producible offender found, and the one in-memory
offender reproduced is the hand-forged object-layer shape decision.md already excludes. All gates
re-run and reproduced (suite 3009 passed / 38 skipped with license load verified by skip-reason
grep, `PYTHONOPTIMIZE=1` 14 passed, mypy/ruff zero delta vs `27425c0`, byte-identity with every
recorded snapshot source location unmoved). Kept evidence confirmed RED-able — restoring the 3
deleted lines flips 5 tests. Seven notes, all documentation/hygiene, none a correctness defect:
decision.md's claimed "duplicate names rejected at extraction" block is not in `src/` in that
form (F1); the guards actually doing structural work for QN disjointness
(`parameter_groups.py:407`, `:436`, `:460`) are uncited (F2); `upstream-filing.md` says
`status: filed` but both fusion-repo files are written-but-uncommitted (F3); corpus counts are
34/847 not 35/846 (F4); `shared_producer`'s snapshot `source_hash` is now stale, warning-only
(F5); the MODELED_DEFAULT branch mints `LIBRARY_DEFAULT` against docstring and record (F6); the
epic's Scope step 3 still reads as an open conditional (F7).

**Premise correction, carried.** A deliberately license-less full-suite run produced byte-identical
results on this machine, so "collected count looks full" is not a valid syside-license detector
here — the valid check is grepping for zero `no live syside license` skips. This contradicts the
recorded method in auto-memory `syside-license-key-explicit-env-needed`; that memory needs a
look before the next gate run relies on it.

### CONSTRAINT-LIFECYCLE Item 2 — Shared Producer Resolution and Gate A — CERTIFIED, pass with notes (independent audit 2026-07-19 at `039d66e`)

Epic register row 2. Spec, design (rev 2 + implementation notes), and `evidence.md` at
`.project/active/constraint-lifecycle-shared-resolution/`. RED coordinate `287afc4`. The design
carries the phased plan — there is no separate `plan.md`.

**Delivered.** One producer-resolution authority (`resolution/producer_resolution.py`): 21 declared
key forms in two tiers, one self-reference guard applied at every tier-1 hit, one terminal fork.
All three consumers — calculation, constraint, aggregation — build a request and read a result.
`input_resolver.py` deleted outright. Gate A live GREEN: a literal owned by a concrete `PartUsage`
resolves under its real QN and drives a real simkit verdict that flips with the literal.

**Validation.** Full suite 3003 passed / 0 failed; execution lane 17 passed; byte-identity gate
green with every pre-existing fixture byte-identical; **EP-key manifest zero-diff** across 34
fixtures / 273 entry points / 484 module inputs (the F4-trap control); `ruff src/` clean; `mypy`
72 errors, below the 76 baseline.

**Audit.** Pass with notes — `.project/active/constraint-lifecycle-shared-resolution/audit.md`.
Every gate re-run independently and reproduced (suite, `-O`, execution lane, byte identity, EP
manifest 34/273/484/0-diff, Gate A RED→GREEN, Item 1 acceptance SHA). All four spec and five epic
criteria verified. Eight findings, none a code defect: the recorded D2 residual names table rows
that do not actually conflict and the shipped split satisfies **both** old orders (F1); forced
difference 2 is claimed to have no corpus population and has 63 warnings across 17 of 34 fixtures
(F2); the design's key-form table disagrees with shipped `KEY_FORMS` on numbering and on the
chain-follow row's position (F3); `_resolve_binding_via_registry` survives SR-R41 unrecorded (F4);
`test_baselines.py` is not the byte-identity gate it is cited as (F5); the parity-class replacement
pin covers 1 key form of 21 and the "3037 → 3003" count does not reconcile (F6); plus two docstring
fixes (F7, F8). All correctable in artifacts. None blocks Item 3.

**Not delivered, referred.** SR-A02 / SR-R23 two-consumer convergence. The calculation consumer
cannot express the reference as written — extraction discards it, and for a self-named binding the
referent is the calc's own formal (design PC-4). I9 is falsified for that shape. Pinned
known-incomplete by `tests/fixtures/shared_producer/` + its `PROVENANCE.md`; the written-reference
carry is folded into **Item 4**'s coordinated agentic-mbse + codegen change set.

**Audit: Pass with notes** — every gate reproduced independently; all eight findings were record
corrections, now applied. The headline correction: D2 was **not** falsified. Both deleted ladders
are order-consistent subsequences of the unified table, and the alias-rung split (rows 4-5 before
the structured forms, row 10 after) reproduces both exactly. The original residual named the wrong
row (bare alias is row 10, not 5), mixed 235 calculation with 14 constraint requests into one
denominator of 249, and measured 44 hits where the rows it named yield 3. Rows 4/5/7/9 take zero
corpus hits. The one genuine inversion is in the aggregation ladder (alias before scoped) and is
also unexercised.

**Still open.** V11 widening to aggregation entry points stays Item 3's (PC-3, I10 preserved and
verified by a one-writer check). `param_group` on LocalTerm mints stays `None` — a classification
question ruled out of scope, recorded as a design residual for Item 4/10. SR-R16's stated basis
should be amended to order-dependence (PC-2) when the spec is next touched.

### CONSTRAINT-LIFECYCLE Item 1 — CERTIFIED after independent audit + remediation (2026-07-19)

**Candidate revision `287afc47ab06826de27c38e203ffffb45398f972`** (supersedes 28bc8b0 after audit remediation). Evidence:
`.project/active/constraint-lifecycle-occurrence-demand/evidence.md`. Audit:
`.project/active/constraint-lifecycle-occurrence-demand/audit.md`.

**Independent audit verdict: Certify (with recorded deviations).** Pass 1 at `28bc8b0` returned
Needs work on two blockers; both are closed at `287afc4` and re-verified first-hand.

1. **Silent value-loss regression — fixed.** A malformed literal at one resolution tier exited the
   whole tier loop, suppressing a valid literal on the tier below
   (`resolution/supplied_values.py:281`). The one-line `continue` restores predecessor
   fall-through: the auditor's reproduction now returns `42.0` at the candidate, matching
   `ecdc7285`. The RED claim was verified independently against a `git archive` of the pre-fix
   tree — the new regression test fails there and passes at the candidate.
2. **OD-A10 deviation — accepted as recorded.** The design's live 3/2/1 shape is not delivered;
   two structural obstacles were reproduced and are recorded in evidence deviation 9. The
   warning-order observation is delivered at the enrichment seam by
   `test_two_warnings_occur_in_order_within_one_batch`, and `plan.md:726` is relabelled `[~]` with
   an accurate split note. The auditor weighed the unmodelability claim independently and found the
   def-scoped/instance-scoped collision bind persuasive, with the limit on that judgement stated in
   the audit.

Deviation 6 is relabelled a design deviation; the `A -> B -> A` variant now has a public live node
(`cycle_indirect/`). F7 applied. F4/F5/F6 declined with reasons the auditor confirmed accurate.

**Anchor intact:** acceptance-file SHA-256 `aea7c821...eacb624b` verified from git bytes at
`287afc4`, and the file still has exactly one commit in its history — the admitted touch-and-revert
left no committed trace. New public nodes were added in a separate supplementary file.

**Carried forward, all disclosed:** tier-2 malformed-literal disposition asymmetry (pre-existing);
`source_location_mode=None` source-key path; the "referenced bindings" noun (blocked on the anchor);
`_owner_source` ambiguity downgrade; OD-A05 output-bytes and declaration-reversed variants; OD-A10's
live 3/2/1 shape.

All six public acceptance nodes plus the supplementary indirect-cycle node are GREEN on the
unchanged Phase 0 overlay (acceptance-file SHA-256 `aea7c821...eacb624b`), closing R-4, R-5, and
R-7. Full suite **3,012 passed, 26 skipped, 0 failed**; focused normal and `-O` gates 66 each
(all reproduced by the auditor at `287afc4`); affected regression union 162;
TEAx execution 2 passed with sibling overrides producing 4.0/6.0 and violated/satisfied
verdicts. Mypy holds at the 76-error baseline; Ruff clean; locks, snapshot v3, profile v4,
and every existing fixture/baseline byte unchanged.

What landed: verified usage/decision association replacing nullable-QN membership; one
all-or-nothing prepared batch owning every occurrence query and its transcript; explicit
part_def/calc_def/package dispatch with no default arm; structured `RecursiveContainmentError`
with per-path cycle detection; and one logical demand per normalized target with
post-resolution provenance. Deleted with no wrapper, flag, alias, or dead fallback:
`materialize_supplied_values` + nested route `_demand`, `collect_bare_actual_demand`,
`RecordingOccurrenceIndex`, the route-counted loop, and the `synth[target.qn]`
last-write-wins overwrite.

**Owner LOC ruling (2026-07-19, epic commit `a1435e1`)** retired every numeric LOC gate
epic-wide; simplicity is judged qualitatively. The Stop #4 condition raised at the end of
Phase 4 is dissolved. Final metrics are recorded informationally only (nine-file union
3,552 -> 3,818, net +266) in evidence.md §1.

**Deliberately still open, not claimed here:** R-8 unmappable warning locations (Item 4);
relocated whole-tree proof (Item 5); sealed-artifact/composed-thread proof (Item 13); Item
2's producer/exact-QN resolver, not absorbed. Same-checkout replay is regression-only and
non-certifying throughout. Eight recorded deviations, a review-confirmed collision-guard
defect and its fix, and a Phase 0 fixture-digest mis-recording correction are in evidence.md
§5-§7. Items 2-13 implementation has not started.

### CONSTRAINT-LIFECYCLE Item 0 — COMPLETE; LOCAL COMPATIBLE PIN (2026-07-19)

The owner rejected the branch-purity work around agentic-mbse `4ed2a07`. The committed
modeling-orchestrator work may remain in the PR #11 candidate. Item 0 now does only four things:
combine the current local and remote PR lines without dropping work, make the pinned package set
install together, record exact revisions/locks, and capture the production LOC baseline. It does
not require patch replay, branch surgery, wheel-payload attestation, a negative-control matrix, a
canonical `pin_id`, or another review cycle.

The direct implementation is complete. Agentic-mbse `515e08b` merges local `205debd` and remote
PR #11 tip `54a95d2` while retaining the modeling-orchestrator commit. The focused merge suite
passed 323/323. The pinned sysml-codegen environment imports agentic-mbse `0.1.2`, executable
profile v4, and codegen `0.1.0`; the actual teax-simkit `0.1.0` distribution builds and imports.
Exact revisions, lock digests, commands, and the five-repository production LOC baseline are in
`.project/active/constraint-lifecycle-candidate-pin/evidence.md`.

### Constraint Execution Lifecycle — RATIFIED; NEW REMEDIATION EPIC READY (2026-07-19)

The owner ratified the corrected lifecycle contract as the normative target architecture. The
focused correction re-review found it ratifiable after bounded edits; all 24 edits were applied and
mechanically verified. Ratification certifies no implementation. Candidate certification remains
blocked until register row 0 pins a compatible committed revision set and row 17 passes every
mandatory acceptance case on one artifact thread.

The old PR-wave remediation epic is superseded and frozen as partially completed. Items 1/2 remain
complete and Items 4/6 remain certified within their recorded scopes. Their evidence is inherited,
not automatically re-audited. Unfinished and newly discovered work is mapped into the new 14-item,
19–23 day P0 epic covering ratified register rows 0–17.

For Items 2–13, simplification is structural: delete the named duplicate/workaround paths, keep one
authority and one route, and do not replace removed machinery with a shim. Numeric line-count
baselines, budgets, caps, close gates, and code-growth deviations are not requirements. Item 1 was
already in flight when the owner made this correction; its artifacts remain untouched.

Active artifacts:

- `.project/concepts/constraint-execution-authoritative-lifecycle-contract.md`
- `.project/active/constraint-execution-lifecycle-contract/spec.md`
- `.project/research/20260719-134700_constraint-execution-lifecycle-contract-correction-rereview.md`
- `.project/backlog/epic_constraint_execution_lifecycle_remediation.md`
- `.project/backlog/epic_constraint_pr_wave_remediation.md` (superseded history)

The owner confirmed that delivery means updating the existing open agentic-mbse PR #11 first and
sysml-codegen PR #9 second, not opening a replacement upstream wave. The new epic now states that
objective in its executive summary, success criteria, Item 0, Item 13, and dependencies.

Pre-Item 0 preservation checkpoints requested by the owner:

- agentic-mbse `205debd` preserves the profile-v4 implementation and evidence above the committed
  modeling-orchestrator work at `4ed2a07`. Item 0 may merge that line directly with the PR #11
  remote tip `54a95d2`.
- stellarator `bceaf40a` preserves the WI-027 Gate-B capture blocker record.
- sysml-codegen `e217119` preserves the constraint remediation, evidence, ratified contract, and
  new epic.

No commit was pushed and no PR was updated. Item 1 now has an approved implementation contract,
approved technical design, and persistent implementation plan using the Item 0 revision set as its
starting pin. Next: execute Item 1 with `my-implement`.

### CONSTRAINT-WAVE Item 1 — Profile Semantics — COMPLETE; INHERITED BY NEW EPIC

Implementation and fresh audit evidence verify the approved ordering and polarity semantics,
source-identity rejection before mutation, four-route positive-IR continuity, compound diagnostic
sentinels, one neutral body with per-usage polarity, TEAx execution, package/skew controls, and the
shared Items 2/4/6 regression union in normal and optimized Python. After audit, the owner removed
agent-authored clean-overlay and pre-edit-hash gates and requested no re-audit. The replacement
lifecycle epic inherits this evidence and lands/pins it in Item 0. The absent provenance is recorded
without retroactive claims. Artifacts:
`../agentic-mbse/.project/active/constraint-wave-profile-semantics/`.

### CONSTRAINT-WAVE Item 4 — Snapshot Portability and Shape Gates — CERTIFIED (2026-07-19)

The fresh independent re-audit certifies Item 4. Every prior **Needs Work** finding remains closed:
live and replay collectors use distinct routes; the licensed node is ordered
live A, live B, replay A; the explicit loader matrix has 336 cases; the fixture transaction stages
and verifies full fixture and baseline manifests with 11 reproducible recovery/failure tests; and
BLOCK zero-call behavior plus exact canonical warning/excluded-record bytes are pinned. The
production fixture delta remains exactly 65+1 location lines across two snapshots.

Fresh licensed evidence: the complete relocation file passed 3/3, including live A/live B/replay A
and moved replay; Item 4 plus transaction tests passed 407/407 in normal and optimized modes; and
the independently run full suite passed 2,950 with 26 skips and 10 deselections. Fresh Ruff, format,
and diff checks pass. Prior frozen-overlay, fixture, baseline, 30-snapshot inventory, Item 2/6
overlap, and Item 3 isolation evidence remains preserved. The spec, Phase 5, epic criterion, and
backlog item are closed. Audit and evidence:
`.project/active/constraint-wave-snapshot-portability/{audit,evidence.md}`.

### CONSTRAINT-WAVE Item 6 — Seal and Verify Symlink Symmetry — CERTIFIED (2026-07-18)

Epic Item 6 (R-10) is independently certified in
`.project/active/constraint-wave-seal-symmetry/audit.md`. Seal, canonical/emitted verification,
generation, Step 9, and re-seal reject every symlink before target use. Fresh audit evidence
reproduced 23 historical RED nodes and six controls, then passed the 29-node candidate overlay,
76 focused tests and 22 audit probes in normal and optimized modes, and the 84-test package gate.
Verifier/fingerprint, static, fixture, and scope checks passed; licensed live nodes remain
unclaimed.

### CONSTRAINT-WAVE Item 2 — Generated Constraint Name Safety — COMPLETE (execution gate closed 2026-07-19)

The re-audit certified the license-free implementation. The missing-catalog fail-open is closed
with a structured `catalog_module_join` before renderer, writer, or orchestration mutation. Fresh
evidence passed the original validator/renderer/`run_codegen()` probe, 20 missing-catalog writer and
orchestration cases, 16 ordering permutations with a safe-order control, and all four independent
historical-impact nodes at `512786c`. Augmented focused normal and optimized gates passed 174/174;
Item 6 overlap passed 122 with 2 licensed skips; patch, static, diff, fixture, and isolation checks
passed.

**Execution gate closed 2026-07-19.** The one criterion the audit left open (real TEAx execution,
then blocked by missing `pandas`) was run green in the agentic-mbse venv (pandas 2.3.3, teax-simkit
on `sys.path`), fresh subprocesses, not mocked: pinned node `1 passed, 14 deselected`; satisfied
`(True, 'satisfied', 1.0, {'x': 2.0, 'limit': 3.0})`, violated `(False, 'violated', -1.0, {'x': 4.0,
'limit': 3.0})` (`evidence/collision-free-execution-tuples.txt`). Spec SC-9 and all three epic Item 2
success criteria are now met; the item is complete. Licensed Syside live/snapshot parity (design
I11) stays out of scope, tracked under Item 8. Audit + post-audit addendum:
`.project/active/constraint-wave-name-safety/audit.md`.

### Independent GAP-CLOSE completion audit + PR-wave code review (2026-07-18, evening)

Two deliverables, both agent-fan-out verified:

1. **Independent audit of GAP-CLOSE completion** (`.project/backlog/epic_gap_close_audit_independent.md`):
   the certified-partial status HOLDS. Items 1–4 re-confirmed against code with fresh test runs;
   pushed companion `54a95d2` byte-identical to the local gap-close worktree, no orchestrator
   contamination. Corrections: Item 5's "diff --check clean on both branch ranges" box was false of
   the pushed companion range (one archived-plan EOF blank line; cure uncommitted) — annotated in the
   epic; the partial pre-PR has in fact been EXECUTED (`512786c` pushed + both PRs commented
   2026-07-19T00:59/01:10Z), so the epic's old Next Action was stale — corrected. Still genuinely
   open: F1 external leg, and licensed full suites at the final commits (2,516-pass evidence is from
   the pre-cure candidate; the companion "1,506 passed" run exists only in the PR comment).

2. **PR-wave code review** (`.project/research/20260718-192048_constraint-exec-pr-wave-code-review.md`):
   four NEW High findings, all reproduced, all outside prior review coverage — PR #11 profile:
   ordering comparisons ADMIT string/boolean/enum operands (live-reproduced); `is_negated` never
   consulted → negated asserts admit inverted semantics (live-reproduced). PR #9: model formals named
   `value`/`status`/`verdict`/`self` shadow generated locals → silent margin corruption incl. sign
   inversion / runtime TypeError / SyntaxError; nullable-QN ADMIT filter in
   `collect_bare_actual_demand` crashes from-snapshot rebuild on a valid snapshot. Plus 8 Medium
   (named-excluded path leak into fingerprints, recursive-part silent truncation, demand overwrite,
   warning-pre-pass masking, seal/dangling-symlink gaps, loader raw KeyError, lost signed/unit
   defaults, TEAX_SIMKIT_PATH silent fallback) and a Low/latent tail. Recommendation: fix the four
   Highs before the wave merges (it is already held on F1); R-1/R-2 need an owner call on BLOCK vs
   IR-fold semantics. Nothing committed or pushed this session.

### GAP-CLOSE epic — LOCAL SCOPE CERTIFIED; PARTIAL PRE-PR MAY PROCEED (2026-07-18)

The final focused re-audit certifies all local and in-scope GAP-CLOSE work. F2 through F9 remain
certifiable, including exact warning bytes across repeated live, relocated live, and snapshot
replay. The hash-identified rebuilt companion wheel contains the corrected BLOCK/L6 severity and
asserted-outcome statements, and its guide is byte-identical to source.

TEAx explicit-path expansion, resolution, and validation now share the route-aware normalization
boundary; kept tests cover an injected `expanduser()` `RuntimeError` and a symlink loop. Fresh
focused audit selections passed 132 codegen tests normally, 110 under optimized Python, and 143
companion guide/profile tests. The rebuilt wheel hash is `160e7eb5…a8d4f`. External
`[GAP-CLOSE-F1-TEAX-NORMALIZATION]` remains open, so the epic is not complete. `my-pre-pr` may now
run only as an explicitly partial wave. No commit, push, PR comment, or close action occurred.
Merge order remains agentic-mbse PR #11 before sysml-codegen PR #9.

### GAP-CLOSE Item 3 — Model and seal boundary guards — CERTIFIED IN EPIC AUDIT (2026-07-18)

All four phases in `.project/active/gap-boundary-guards/plan.md` are implemented. Every
post-initialization declared-field assignment on the transactional Pydantic base now validates a
complete candidate before changing the live model, including constructor-defaulted fields. The
canonical and emitted package verifiers now reject internal and escaping directory symlinks with a
fatal `INVALID_PATH` diagnostic at the link path.

Pinned source-isolated evidence at exact HEAD `6db3212` is four independently defect-specific RED
nodes, followed by 4/4 GREEN over a candidate containing only the two production files. Focused
normal and optimized gates are 57 passed; broader is 53 passed. The unlicensed default full suite
is 2,213 passed with 23 failures and 96 errors confined to the known license-dependent families.
Ruff/format/diff checks pass, mypy remains at the 76-error baseline, and all 179 fixture hashes are
unchanged. Item 1–2 and unrelated dirty files were preserved. The final GAP-CLOSE re-audit retains
this certification; do not push or close outside the explicitly partial pre-PR wave.

### GAP-CLOSE Item 2 — Lowering outcome integrity — CERTIFIED IN RE-AUDIT (2026-07-18)

Epic: `.project/backlog/epic_gap_close.md`, Item 2. The stricter warning-byte route parity is now
pinned at the real lowering logger: repeated live, relocated live, and snapshot replay produce the
same two exact `root-0/model.sysml` warning strings. Lowering reports every
NON_NUMERICAL sibling exactly once before a BLOCK halt, while the halt still precedes concrete
records, catalog assembly, and package mutation. Anonymous excluded statements alone receive a
portable root-slot/file/line/column identity and 128-bit suffix across live, relocated, and snapshot
routes. Named IDs and eligible-anonymous bytes remain pinned to the coordinated baseline.

Isolated evidence uses codegen `6db3212`, companion `4ed2a07`, profile v3, and a frozen overlay;
four historical nodes are independently RED and the exact six-path candidate is 5/5 GREEN. Fixture
bytes and the migration guard are unchanged. Focused gates are 102 passed/8 license skips; broader
45/37; the default full suite is 2,206 passed with 23 failures and 96 errors confined to the known
license-dependent families. Ruff is clean and mypy remains at the 76-error baseline. Licensed live
shape/CLI atomicity legs are accurately unclaimed. `[ANON-ELIGIBLE-KEY]` remains open. The GAP-CLOSE
re-audit independently certified the exact warning-byte route criterion; do not push or close from
this item.

### GAP-CLOSE Item 1 — Runtime evaluation contract — CODEGEN LEG COMPLETE (2026-07-18)

Epic: `.project/backlog/epic_gap_close.md`, Item 1. All five phases in
`.project/active/gap-runtime-contract/plan.md` are implemented. Codegen now rejects all verified
case-fold, underscore-run, and quoted-hyphen predicate-name collisions deterministically before
any output mutation, while direct compilation rechecks the same invariant. Saved isolated evidence
at baseline `6db3212` reproduces each old `DID NOT RAISE` failure and the later-body overwrite.

F1 remains deliberately split: codegen tests characterize unchanged native propagation for div-zero,
zero-to-negative power, exponent overflow, nested connective, and the production-generated wrapper.
The narrowed docstring promises only that an adverse verdict does not itself raise. Licensed
`plant_values` live/snapshot trees were byte-identical; before/after changes were only that sentence
and its derived package contract. Focused gates are green; the default full suite recorded 2,169
passes with all failures/errors license-dependent, while licensed live/focused execution passed in
the companion environment. The final GAP-CLOSE re-audit certifies the local codegen/F2 scope.
`[GAP-CLOSE-F1-TEAX-NORMALIZATION]` remains an external open P0; do not claim evaluator
normalization or end-to-end F1 closure.

### Numerical constraint executable profile — ✅ COMPLETE: CERTIFIED, COMMITTED, PR WAVE UPDATED (2026-07-18)

**Audit verdict: Certify** (`.project/active/numerical-constraint-profile/audit.md`). All 8 spec
success criteria verified against code/tests, not just records: totality/execution, split-equality
outcomes, both-tools warnings, catalog `excluded_records` with the eligible⇔exclusion validator
(construction-probed unrepresentable), live/snapshot value parity, frozen golden untouched, v3 pin
in both repos (companion `05cde35`). Parent-remediation booking (`096c29f`) for the mid-run licensed
failure confirmed genuine.

**Committed and pushed 2026-07-18** as `da3b495` (separable remediation cures + ledger),
`9c0291c` (the v3 item + artifacts), `3f215ac` (touched-file formatting; the `constraint_inline`
baseline deliberately left as generator-emitted bytes). Pre-PR gates green: licensed suite
**2450 passed / 26 skipped / 8 deselected**; companion **1511 passed / 1 skipped**; ruff src
clean; mypy at the 76 baseline; no debug artifacts/secrets. PR #9 and PR #11 updated with
appended-commit comments. Only merge remains (see Up Next — the #11-first order is now
load-bearing). After merge: `/_my_close` archives this item and the remediation.

Dedicated CONSTRAINT-EXEC Item 3 contract correction:
`.project/active/numerical-constraint-profile/{spec,spec-review,design,design-review,plan}.md`.
Spec reviewed and revised in-session (owner resolved all findings; three-way rule: admitted
numerical claims execute, malformed numerical claims error naming the fix, non-numerical
statements warn in both tools and never block generation). Design approved after review — key
owner-ratified calls: numerical-claim **containment** decides force (mixed `(x > 0) and flag`
errors), one tagged exclusion payload on `ConcreteConstraint` projected into catalog
`excluded_records`, single v3 pin at shared lowering, location-fallback rendering. Plan is 5
phases, agentic-mbse first (profile v3 + answer key → L4/L6 → codegen re-pin → exclusion/catalog
+ re-capture → end-to-end families + gates).

All five phases are complete. Agentic-mbse profile v3 core landed as `b251e95`; L4/L6 consumers
and the exact compatible companion state landed as `05cde35`. Codegen now pins v3, renders fixes
on malformed numerical halts, warns once per non-numerical statement, validates a total exclusion
payload, and projects excluded statements into the constraint catalog. New live families prove
warn-and-continue with an admitted numerical sibling and error-force containment for
`(value > 0.0) and flag`; the warning, graph, and complete catalog are identical live/offline.

R4 proved the inherited-inline licensed failure predated Phase 3. Commit `096c29f` corrected the
parent remediation's invalid empty-design-attributes regression harness, and `aaa579e` refreshed
its stale inline baseline. Final licensed codegen evidence is **2450 passed, 26 skipped, 8
deselected**; optimized focused evidence is **125 passed**. The exact `05cde35` companion archive
passed **1491 tests, 1 skipped, 5 deselected**. Targeted mypy and touched-file Ruff/format passed.
The independent audit (Certify) closed this item; see the header block above for the commit and
PR-wave state.

### CONSTRAINT-EXEC code-quality remediation — ✅ CURES COMMITTED; D5 DISCHARGED BY THE V3 ITEM (2026-07-18)

All audit cures are now committed on `constraint-exec-epic`: the separable
package-verification/occurrence-ordering cures in `da3b495`, the entangled cures (profile/compiler
quantity parity, inline-leaf strict wiring, assignment validation) inside `9c0291c` with the v3
work that shares those files, and the R4 test-defect correction in `096c29f`/`8cc20d4`/`aaa579e`
(the inherited-inline "failure" was an invalid empty-`design_attrs` test harness, not a resolver
bug). The addendum's D5 contract choice is discharged by the numerical-profile item. The full
licensed suite (2450/26/8) is the first licensed whole-suite evidence over these cures. Ledgers
closed in `.project/active/constraint-exec-code-quality-remediation/{audit,plan}.md`. Archive via
`/_my_close` after the PR wave merges. The original in-progress record follows below.

The four decision-independent audit cures are implemented in the dirty worktree. Profile-v2
quantity references and the complete admitted arithmetic/ordering operator matrix now compile;
the committed `constraint_inline` snapshot renders and executes with its owner feature wired as a
module input; constraint/catalog assignment validation is transactional and catalog assembly
revalidates before filtering/fingerprinting; and package verification validates digest/path/
fingerprint semantics while normalizing artifact I/O failures. The active design addendum and
amended execution record are in
`.project/active/constraint-exec-code-quality-remediation/{design,plan}.md`.

Focused validation passed **149 tests with 13 license skips** in both normal and optimized Python.
The committed inline snapshot executed under the documented agentic-mbse/TEAx environment (**1
passed**). The exact companion profile suite at `82fef09` passed **113 tests**. Targeted mypy passed
on all five touched production files; touched-file Ruff/format, `git diff --check`, fixture
preservation, and the production placeholder scan passed.

The owner resolved the remaining contract choice on 2026-07-18: preserve the generated numerical
data path and narrow executable admission. The dedicated numerical-profile item is now implemented
and its final combined gates are green. The parent remediation still needs its independent audit
and closeout; the numerical implementation record is not self-certification.

#### Independent audit basis

The independent audit verified the formal-target binding and total occurrence-ordering cures. It
did not certify the full remediation. Exact companion profile v2 still admits quantity-reference
predicates the compiler rejects, while newly admitted non-real equality has no typed generated
input/evidence path. The committed inline-constraint fixture also lowers to a module whose
predicate leaf has no matching input.

Two local boundary gaps remain. Construction-time model validators can be bypassed by assignment,
which can silently drop a mutated constraint during catalog or graph assembly. Package verification
does not validate fingerprint derivation or artifact-path containment, and recorded artifact I/O
can still escape as a raw exception. The affected plan checkboxes were reopened and the unresolved
work is registered in `.project/backlog/BACKLOG.md`. Full evidence is in
`.project/active/constraint-exec-code-quality-remediation/audit.md`.

Independent focused validation passed in normal mode (**174 passed, 5 skipped, 7 deselected**).
The same changed scope under `python -O` produced **173 passed, 5 skipped**, plus the one unrelated
pre-existing assertion-dependent failure. Touched-file Ruff and formatting, `git diff --check`,
fixture preservation, and the placeholder scan passed. Targeted mypy remains non-green on the
imported project surface.

The implementing agent's broader, carried evidence remains: exact companion compatibility **92
passed**; combined remediation **189 passed, 18 skipped**; optimized remediation **138 passed, 18
skipped**; and the unlicensed full suite **2,107 passed, 197 skipped, 7 deselected, 23 failed, 96
errors**, with the failures/errors reported as license-dependent. The independent audit did not
rerun the full suite or reproduce the exact 92-test command, so these results are implementation
evidence rather than independent certification.

The initial remediation pass completed on 2026-07-14 as follows.

The independent code-quality review
(`.project/research/20260713-213722_constraint-exec-pr-code-quality.md`) was verified
finding-by-finding against the code (census numbers reproduced exactly; both "impossible"
model states construction-probed; unary-plus reachability traced through the agentic-mbse IR
builder). Verification disagreed with the review on two points only: graph-extension
*validation* is shared, not duplicated, and its "ordering" is an append counter, not a
reimplemented topo sort. Its pre-merge bar then landed as four commits on
`constraint-exec-epic`:

- `5785055` — ConcreteConstraint/Input model validators + rejection tests (tagged-union
  resolution fields; eligible ⇒ predicate_ir + evaluation_channel; expected_value derives
  from is_negated). Preserved pinned edge: MODELED_DEFAULT's `default_ir` may be None.
- `baca960` — both IR renderers: one-operand render now requires operator `-` (a modeled
  `+x` silently rendered as `(-x)` — reachable, not latent); arity + identifier validation
  in the predicate compiler (raw IndexError → PredicateCompileError).
- `c756fc7` — load-bearing asserts → explicit errors (version pins, same-IR, capture
  presence, eligibility dereferences, most-specific-PartDef) so they survive `python -O`.
- `05690f0` — resolver precedence-under-conflict pins (6 two-rungs-both-match tests) +
  path-grammar characterization (brackets, empty segments, chain-vs-source_name).

Reported gates at the remediation close: licensed suite **2364 passed / 23 skipped** (was 2330/23;
+34 new tests), `tests/fixtures` byte-identical throughout, Ruff clean on the remediation scope,
mypy at the 76 baseline. The independent audit verified touched production files as Ruff-clean; one
touched test file retains five pre-existing whole-file violations. The architectural remainder is
registered as `[CONSTRAINT-ARCH-UNIFY]` (P1) and
`[EXIT-PIN-SEAM]` (P3) in `BACKLOG.md` — merging PR #9 does not bless the current parallel
ladders / triple walker / mirrored live-offline phases as the permanent architecture.

### docs-explainer-refresh — ✅ COMPLETE: audited Certify, pushed to the open PRs (2026-07-13)

Post-CONSTRAINT-EXEC docs + explainer-brief refresh across four repos, run as a full
orchestrated pipeline (spec_review → design → design_review → plan → implement → audit; all
artifacts + stage briefs in `.project/active/docs-explainer-refresh/`). Audit
PASS-WITH-NOTES cured to **Certify**: the three cross-repo legs probe-verified by the
orchestrator (addendum in `audit.md`), Phase 5/7 notes reconstructed. Branches pushed
(sysml-codegen/agentic-mbse full; teax already carried `4c96b99` via a concurrent owner push)
with appended-commit comments on PRs #9 / #11 / teax#3; fusion-tea `bfff2b4f` stays local per
the merge sequencing in Up Next. All 7 phases landed as one commit per phase per repo:
- **sysml-codegen** (`constraint-exec-epic`): `0fad7bf` re-project stale surfaces onto HEAD
  (snapshot v3, ExpressionIR, ModuleKind, lowering phase); `78a6a7d` new doc 29 contracts/sealing
  + CON matrix family + recount to 32 families; `dbc60b8` `EXPLAINER_PROMPT.md` re-anchored + Gen-1
  banner; Phase-7 close-out commit (this one).
- **agentic-mbse** (`constraint-exec-epic`, PR #11): `9e24c93` decision-table reword + durable
  ConstraintFacts/ExpressionIR page.
- **teax** (`constraint-exec-epic`, PR #3): `4c96b99` document `PreparedEvaluator.entry_models`.
- **fusion-tea** (`main`): `bfff2b4f` drop `ToyPlantParams` alias + walkthrough retirement note.

Matrix recount landed at 32 families / 274 reqs / 73 test files (summary/Index/overview agree).
Discoveries surfaced (registered in `.project/backlog/BACKLOG.md`): `[V2-HTML-BUILD]` (the actual
v2 HTML build, [OWNER]: another agent), `[DOC19-DISPATCH-REAUDIT]`, `[MODULEKIND-DOC-SWEEP]`. See
the plan's Implementation Notes for the full per-phase record + the `is_droppable_constraint`
live-symbol deviation.

### PUSH-DOWN epic — INDEPENDENTLY AUDITED + REMEDIATED: CERTIFIED (2026-07-10)

Independent technical audit of PRs #8 (sysml-codegen) / #10 (agentic-mbse) found the code
functionally sound but the certification record over-claiming (SC-D Q4/R8 falsely checked;
Item 1's move not mechanical; mypy 97→98 misrecorded). All findings remediated same day —
full audit + per-finding remediation record:
`.project/backlog/epic_push_down_audit_independent.md`. Remediation highlights: Item 1
expression bodies restored to the mechanical-move originals with the test mocks upgraded to
the real syside shape; Q4 descoped with rationale (its live annotation bug in
dependency_backtracker fixed — surfaced by mypy the moment `py.typed` landed); R8
`# INTENTIONAL DIVERGENCE` marker added; `py.typed` added to agentic-mbse and the
TYPE_CHECKING mirror dataclasses deleted (sysml-codegen mypy 98→77 vs main's 97); TYPE_MAP
inventory tests de-self-certified; `**` added to shared SUPPORTED_OPERATORS; unary-minus
render deviation recorded in Item 4's audit. Post-remediation gates: 2138/4 + 1290/1 green,
ruff src clean, fixtures byte-identical. Epic and prior audit/pre_pr carry correction
addenda. **Note for the PRs: the remediation commits are not yet made/pushed** — both repos
have uncommitted working-tree changes on `push-down-item1-expression`.

### PUSH-DOWN epic — CERTIFIED (superseded by the 2026-07-10 independent audit above)

Epic: `.project/backlog/epic_push_down.md`. Epic audit:
`.project/backlog/epic_push_down_audit.md`.

All four PUSH-DOWN items are implemented and item-audited with `Certify` verdicts. The epic audit
certifies the top-level success criteria SC-A through SC-G against the source concept-design,
boundary research, TRUTH-DEBT sequencing ruling, and item audits. The reusable SysML semantic
helpers now live in agentic-mbse; sysml-codegen keeps transformation policy, Python rendering,
aliases, design overrides, scoping, pipeline assembly, and deferred template/virtual-binding work.
No pre_pr or PR preparation was run during the audit stage. Next stage is whole-epic pre_pr/PR
preparation only.

### PUSH-DOWN Item 4 — Aggregation Decomposition and Compatibility Gates — CERTIFIED

Epic: `.project/backlog/epic_push_down.md`. Artifacts:
`.project/active/aggregation-decomposition/{spec,spec-review,design,design-review,plan,audit}.md`.
Spec review and design review both reached Approved after revision. This item moves neutral
aggregation AST decomposition into agentic-mbse; sysml-codegen keeps Python rewriting, local
`AggregationExpressionData` assembly, pipeline-facing identifiers, alias handling, and downstream
resolution policy. No item-level PR closeout is planned because the user wants the whole PUSH-DOWN
epic implemented before PR.

Implemented `agentic_mbse.sysml.aggregation` with neutral aggregation decomposition, wrapper facts,
diagnostics, dispatch-order guardrails, and no sysml-codegen imports. `SumTerm`, `SingletonTerm`,
and `LocalTerm` now live in agentic-mbse and are re-exported by sysml-codegen as the same runtime
class objects. sysml-codegen's aggregation builder now delegates raw decomposition to the shared
module and renders local `AggregationExpressionData` through a compatibility adapter. The
aggregation-profile loop filed three future rows in agentic-mbse backlog:
`PUSH-DOWN-AGG-PROFILE-SUM-SHAPE`, `PUSH-DOWN-AGG-PROFILE-WRAPPER-SHAPE`, and
`PUSH-DOWN-AGG-PROFILE-LITERAL-SHAPE`.

Validation: agentic-mbse aggregation suite `12 passed`; shared expression/hierarchy/aggregation
suite `93 passed`; agentic-mbse full suite `1290 passed, 1 skipped, 33 deselected, 6 warnings`;
sysml-codegen local model/builder suite `166 passed`; sysml-codegen downstream compatibility suite
`202 passed, 1 skipped`; sysml-codegen full suite `2138 passed, 4 skipped`; sysml-codegen
`ruff check src/` clean; touched-file ruff clean in both repos; `git diff -- tests/fixtures` empty.
Audit: `.project/active/aggregation-decomposition/audit.md` certifies the item. Audit reran the
focused high-risk gates: sysml-codegen builder/model/literal/dispatch subset `190 passed`, and
agentic-mbse aggregation suite `12 passed`. Remaining caveat: project-wide mypy baselines are still
dirty but unchanged after cleanup (agentic-mbse 107, sysml-codegen 98). No item-level PR closeout was
performed; continue to the PUSH-DOWN epic audit and PR preparation only through the whole-epic flow.

### PUSH-DOWN Item 3 — Hierarchy Primitives and Data Models — CERTIFIED

Epic: `.project/backlog/epic_push_down.md`. Artifacts:
`.project/active/hierarchy-primitives-models/{spec,spec-review,design,design-review,plan}.md`.
Item 1 and Item 2 are implemented, audited, and committed in both repos. This item starts only
the hierarchy primitive/model split; no item-level PR closeout is planned because the user wants
the whole PUSH-DOWN epic implemented before PR.

Implemented shared `agentic_mbse.sysml.hierarchy` with primitive redefinition and multiplicity
extraction; moved `RedefinitionType`, `RedefinitionData`, and `MultiplicityData` into
agentic-mbse as field-identical standard-library models; sysml-codegen now re-exports the same
runtime class objects and delegates primitive extraction through compatibility wrappers. Design
overrides, aggregation, usage-type indexing, hierarchy orchestration, and `HierarchyExtractionResult`
remain local to sysml-codegen. Hierarchy-profile rows that require codegen policy were filed in
agentic-mbse backlog; missing instantiations remain covered by existing `L6_CALC_DEF_NO_INSTANTIATION`.

Validation: agentic-mbse hierarchy test `10 passed`; agentic-mbse full suite `1278 passed, 1 skipped,
33 deselected`; sysml-codegen focused hierarchy/model/dispatch suite `156 passed`; sysml-codegen full
suite `2127 passed, 4 skipped`; sysml-codegen `ruff check src/` clean; touched-file ruff clean in
agentic-mbse; `git diff -- tests/fixtures` empty. Remaining caveat: project-wide mypy baselines are
still dirty but unchanged for this item (agentic-mbse 107, sysml-codegen 98). Audit:
`.project/active/hierarchy-primitives-models/audit.md` certifies the item. No item-level PR closeout;
continue to PUSH-DOWN Item 4.

### PUSH-DOWN Item 2 — Qualified-Name Utility Split — CERTIFIED

Epic: `.project/backlog/epic_push_down.md`. Artifacts:
`.project/active/qualified-name-utility-split/{spec,spec-review,design,design-review,plan}.md`.
Spec review and design review are both Approved. Implementation is complete on the full
PUSH-DOWN epic branch in both repos, with no item-level PR closeout.

Moved pure qualified-name helpers into `agentic_mbse.sysml.qualified_names`; sysml-codegen now keeps
`sysml_codegen.core.qualified_names` as a compatibility shim and retains codegen-owned module,
channel, parameter, and owning-part builders locally. The `ITEM-SYNC-C8` backlog row was updated
instead of duplicated: the shared sanitizer dependency is gone, while the sibling-scope Level-6
collision collector remains filed.

Validation: agentic-mbse targeted qualified-name suite `21 passed`; agentic-mbse full suite
`1268 passed, 1 skipped, 33 deselected`; sysml-codegen targeted naming/shim suite `52 passed`;
sysml-codegen full suite `2122 passed, 4 skipped`; touched-file ruff clean in both repos;
sysml-codegen `ruff check src/` clean; `git diff -- tests/fixtures` empty. Remaining caveat:
project-wide mypy baselines are still dirty outside this item (agentic-mbse 107, sysml-codegen 98).
Audit: `.project/active/qualified-name-utility-split/audit.md` certifies the item. Next: continue
PUSH-DOWN Item 3.

### PUSH-DOWN Item 1 — Expression Reconstruction Push-Down — CERTIFIED

Artifacts: `.project/active/expression-reconstruction-push-down/{spec,spec-review,design,design-review,plan}.md`.
Spec review and design review are both Approved. Implementation is complete on
`push-down-item1-expression` in both repos.

Moved reusable expression reconstruction, feature-chain, chain-segment, and literal helpers into
`agentic_mbse.sysml.expression`; sysml-codegen now keeps
`sysml_codegen.extraction.expression_utils` as a compatibility shim. Level-6 C7 now uses shared
`is_literal_node`, and the expression-profile close-out filed three follow-up rules in
agentic-mbse backlog.

Validation: agentic-mbse full suite `1247 passed, 1 skipped, 33 deselected`; sysml-codegen full
suite `2119 passed, 4 skipped`; sysml-codegen snapshot-specific suite `87 passed`; touched-file
ruff clean in both repos; sysml-codegen `ruff check src/` clean; `git diff -- tests/fixtures`
empty. Remaining caveat: project-wide ruff/mypy baselines are still dirty outside this item
(agentic mypy 104, sysml-codegen mypy 97, sysml-codegen full ruff 332).

Audit: `.project/active/expression-reconstruction-push-down/audit.md` certifies the item. Next:
run `$my-pre-pr` for PR preparation.

### PIPELINE-TRUTH epic — ✅ COMPLETE (all 10 items landed and audited PASS, 2026-07-06)

**The generated package is the truth.** fusion-tea's models generate, wire, and execute
end-to-end from generated artifacts alone — TRUE ZERO V11 offenders (supplied-value
materializer, Item 2), run-C lcoe bit-exact ($270.1211779380445) with every workaround
deleted upstream (Item 3), constraint drop report subtype-aware incl. `assert` (Item 4),
13 silent-failure findings fixed by family (Item 5), 25 self-referential tests re-anchored
(Item 6), matrix 253 = 249 PASS + 4 UNTESTED-argued + 0 DEFERRED with F2/F4 resolved by
decision (Item 7), dead code cleared + REQ-AST-10 (Item 8), agentic-mbse taught+checked
(Item 9), docs + explainer prompt refreshed and caveats retired (Item 10). Gate:
2069 passed / 4 skipped / 5 xfailed; ruff src 17; mypy src 104. Epic + Lessons Learned:
`.project/backlog/epic_pipeline_truth.md`. Item-10 artifacts:
`.project/active/epic-close-docs/{spec,plan}.md`.

**Human actions outstanding (the only ones):**
1. **agentic-mbse companion PR** — branch `pipeline-truth-item4` is pushed to origin; open
   the PR from `.project/active/pipeline-truth-sync/COMPANION_PR_BODY.md` (base `upstream-findings-sync` while
   PR #7 is open; retarget to `main` on its merge).
2. **Merge PR #7** (the UPSTREAM-FINDINGS agentic-mbse companion, `upstream-findings-sync`) —
   still pending; the Item-4 companion bases on it until it merges.
3. **fusion-tea workaround-retirement PR** — open from
   `chore/retire-pipeline-truth-workarounds` (Item 3 end state).

### PIPELINE-TRUTH Item 9 — agentic-mbse Sync (Guidance, Validation, Companion Audit) — COMPLETE
Phases 0–5 landed 2026-07-06. **C7** (the one unbuilt check) WARNs on `attribute :>> attr =
<expr>` — the AttributeUsage redefinition codegen silently drops; test-first, cross-repo-clean.
**D1–D4/I5** teaching surfaces synced (whole-plant value idiom, secondary shapes, shallow chains,
subtype-aware asserts, Item-5 diagnostics). Prior-epic residue closed: R-F6 verified, R-C8 &
S-F3/S-F4 keep-filed, R-VENDOR & S-F5 declined/discharged, PR #7 stays the human's. Companion
audit (`extract_feature_refs`, `str(direction)`) — both COVERED/STABLE.
- **agentic-mbse** `pipeline-truth-item4`: commits `fa3b706` / `1fab4d6` / `9cc7ab4` (over Item 4's
  four). Suite **1240 passed / 1 skipped**; pushed to origin. Companion PR is the human's to open
  (B1 base-then-retarget: base `upstream-findings-sync` while PR #7 open, retarget to `main` on merge).
- **This repo:** 18-row traceability + acceptance in `.project/active/pipeline-truth-sync/close-out.md`;
  companion-audit evidence, plan, and `COMPANION_PR_BODY.md` alongside; S-F3/F4/F5 dispositions in `BACKLOG.md`.

### PIPELINE-TRUTH Item 3 — fusion-tea Acceptance & Workaround Retirement — CERTIFIED
Audit PASS-WITH-NOTES (`.project/active/fusiontea-acceptance/audit.md`, 2026-07-06). Crux
(runner multi-output completion) confirmed test-harness-only, zero `src/`. All 4 acceptance
tests pass; anchor + perturbed-lcoe (216.55528392479388) arithmetic re-derived independently;
retirement greps zero; both offender states zero with canonical Meier channels; SNAP-19 parity
green over 6 fixtures + fusion_tea leg (license live). Gates 2066/4/5, ruff 17, mypy 104.
Only note: fusion-tea teax executor not re-run in audit (needs their venv) — corroborated via
byte-identical wiring + in-repo executor. Next: fusion-tea PR from
`chore/retire-pipeline-truth-workarounds`.

### PIPELINE-TRUTH Item 5 — Silent-Failure Hardening — SPEC IN PROGRESS
Track B. Spec phase is a verification pass (R4): the D3 floor findings are static-read
verdicts reproduced/refuted before design. Verification table + spec:
`.project/active/silent-failure-hardening/spec.md`; live probes (python execution is
sandbox-blocked, so verdicts rest on code-trace + committed tests):
`.project/active/silent-failure-hardening/probes/`.

### PIPELINE-TRUTH Item 1 — Plant-Value & Blind-Spot Fixtures — IMPLEMENTED (awaiting audit)
Track A head (Items 2, 4, 5, 9 build on its fixtures). Fixtures + captures only, zero
`src/` production code. Spec/plan: `.project/active/plant-value-fixtures/{spec,plan}.md`.
Implemented across 6 commits on `pipeline-truth-epic` (Phases 0–5). Full suite: 2017
passed; ruff src 21 / mypy 109 (baseline unchanged). `/_my_audit` suggested next.

- **D6 gate (PASS):** `plant_values` trips V11 with 3 offenders on module
  `plantvaluesdesign__plant__cost_calc`, covering all three value-provision mechanisms —
  `driver_efficiency` (a, subtype-def literal via retype → redefinition 0.35),
  `target_cost` (b, override BLOCK → design_override 10.0), `chamber_cost` (c, plain one-hop
  cross-part attr with a usage-level DOTTED override → design_override 7.0). All three
  offenders are valueless EPs TODAY **and each carries a captured literal Item 2 flips it TO**
  (audit-F1 cure: (c) is no longer trip-only — the `:>> chamber.cost_per_unit = 7.0` override
  lands in `hierarchy_data.design_overrides`, pinned by
  `test_mechanism_c_plain_cross_part_attr_valueless_ep_with_flippable_literal`). This is the
  SC-1 before-state Item 2 flips; hand-computed after: `plant_cost = (target_cost + chamber_cost)
  / driver_efficiency = (10.0 + 7.0) / 0.35 = 48.571`, constraint `eta*gain>=threshold` →
  `0.35*40.0=14.0>=10.0` holds. Every operand is reproducible from the fixture source (see the
  plan's Phase-4 cure note for file:line).
- **Per-shape labels:** `plant_value_shapes` — CORRECT (bare default, 5-deep chain, quoted
  `'net cost'` output, Style-E, quoted return), DEGRADED (econ-param nested `:>>`,
  inherited-redefined-below), DIAGNOSTIC (non-float enum EP / Item 5). No extractor crash →
  no escape-hatch filings.
- **Rider (own commit):** `quoted_owner_formula` `net_margin`/`total_payout` design-attr →
  computed reclassification reviewed and CONFIRMED (prior-epic UPSTREAM-FINDINGS Item 7
  behavior, not a forward dep). `wi014_toy`/`self_named_binding_trap` = timestamp/path canon.
- **Capture surfaces:** `plant_values`, `plant_value_shapes`, `deep_cross_scope_probe` all
  full-pipeline (extraction snapshot + pipeline baseline). `deep_cross_scope_probe` gained
  its first committed snapshot (closed D1-F6 drift); un-broken by renaming `derived`→
  `derived_calc` (reserved KerML modifier).
- **Downstream handoffs:**
  - **Item 2 before-pin:** `tests/conformance/test_plant_values.py::test_plant_values_trips_v11_all_three_mechanisms`
    (the 3-offender set). Extended `spec_chain_twolevel` carries the value-carrying (c) +
    fan-out for Item 2's SC-B tolerance test.
  - **Item 4/5 substrate:** the `assert constraint viability` in `plant_values` is INVISIBLE
    to extraction today (pinned in `test_plant_values.py`); the non-float enum EP is in
    `plant_value_shapes` (`test_plant_value_shapes.py::test_shape9...`).
  - **Item 9 impact list:** finalized in `spec.md` "agentic-mbse impact — Item 9 accumulation
    list" (concrete fixture paths); deferred shapes in
    `.project/active/plant-value-fixtures/fixture-gap-register.md`.
- **Known degradation surfaced (filed):** multi-hop CHAIN `source_path` truncates to the
  first segment (why (c) is one-hop; `deep_cross_scope_probe` Pattern A pins it).

### PIPELINE-TRUTH Item 2 — Whole-Plant Cross-Part Value Resolution — CERTIFIED (PASS-WITH-NOTES, 2026-07-06)
Audit: `.project/active/whole-plant-resolution/audit.md`. 10→0 offenders verified structurally
(all clear by synthesis; 10 applied → 7 source-QN EPs via dedup, **zero** collision-defers).
One doc correction owed before close: the Phase-7 close-out misattributes the clearing path as
"collision guard defers, real wins" — no real-wins defer fired; fix the narrative (no code change).

Track A headline (gates fusion-tea). Value-fill via the supplied-value materializer
(`resolution/supplied_values.py`, REQ-SVM-01..04): a pre-pass synthesizes design
attributes for cross-part/in-part supplied values, keyed by source QN, merged into
`design_attributes` before the backtracker. Plan/design/spec:
`.project/active/whole-plant-resolution/`. **All 8 phases landed** across commits
2de8f60→(Phase 8), acceptance ladder held:
- **SC-1**: `plant_values` zero offenders; a/b/c → 0.35/10.0/7.0 on source-QN EPs; anchor
  `(10+7)/0.35=48.5714` hand-transcribed (INV-5).
- **SC-1d**: `'Flow Sub'` flips DEGRADED→8.0 via tier-2b direct-owner leg.
- **SC-4 (epic CSF)**: committed fusion-tea v2 snapshot (`tests/fixtures/fusion_tea`)
  → **TRUE ZERO** V11 offenders (8 cross-part a/b/c + 2 in-part d), full YAML emits
  license-free. Item 3 reuses this v2 capture + the SC-3 runner.
- **SC-3**: `tests/runtime/pipeline_runner.py` (pinned signature) executes twolevel to
  lcoe=100.0 within rel 1e-6.
- **SC-5**: four cross-part baselines byte-identical (catf_mfe, ife_plant); V11 raise-proof
  re-anchored to Shape 1 (`rated_cost.rate`).
- Suite 2056 passed / 4 skipped / 5 xfailed; ruff 17, mypy 104 (baselines unchanged).
- **Two documented deviations** (see plan Implementation Notes): materializer runs at the
  caller seam (not inside `build_computation_graph`, which post-dates the backtracker);
  precedence + renamed-consumer proven at the mechanism/real-fusion-tea level rather than
  via bespoke captured fixtures. `/_my_audit` suggested next.

### PIPELINE-TRUTH Item 4 — Subtype-Aware Enumeration & Constraint-Report Truth — AUDITED: PASS-WITH-NOTES (2026-07-06)
Track B head (no deps). Coordinated pair with agentic-mbse (R2): one adapter choke
point (`include_subtypes`), per-call-site decision table, constraint drop report fires
on assert constraints, REQ-EXT-09 re-anchored independently, snapshot constraint
serialization. Spec: `.project/active/subtype-enumeration/spec.md`. Audit:
`.project/active/subtype-enumeration/audit.md`.
- **Codegen side solid** — verified by artifact/source: collect/render split, REQ-EXT-09
  re-anchor with executable mutation check, full serialize→replay chain (from-snapshot
  report available), INV-B/D/E/G pins, dead-code deletions, docs rewrite, all 23 committed
  snapshots at v2, wi014 assert manifest committed.
- **Note 1 (gate disclosure):** the Phase-5 reviewed-diff gate under-itemized
  `self_named_rescue` — its v2 diff carries a `binding_type` reference→chain reclassification
  filed as "relativization." NOT Item-4-caused (Item 4 touches no binding code) but the
  gate's itemization is inaccurate; re-itemize + pin/justify the reclassification.
- **Note 2 (fusion-tea):** no committed fusion-tea snapshot exists in this repo, so the
  "wi014 AND fusion-tea" SC is only half-met here; the v2 hard-gate now rejects any external
  v1 fusion-tea snapshot until Item 2 re-captures it — carry to Item 2's SC-A/SC-4.
- **Note 3 (limit):** sandbox blocked all code execution + all agentic-mbse access, so both
  suites green, ruff/mypy (20/105 claimed), a live mutation run, and the entire agentic-mbse
  half (rows 5–8, decision table, TYPE_MAP, Level-3 circular-FAILS) are plan-recorded only,
  not re-executed. Needs a licensed/unsandboxed confirmation run before epic close.

### PIPELINE-TRUTH Item 8 — Dead Code & Cleanup Debt — IMPLEMENTED (2026-07-06)
**All 6 phases landed on `pipeline-truth-epic`** (`3314264`, `d5032c3`, `529dc74`, `3ec4efa`,
`024028b`, `b1dece5`). Tree GREEN: **suite 2000 passed / 4 skipped / 5 xfailed; ruff src 19;
mypy src 104** (both better than the 20/105 gate). SC-G clean: zero grep hits for all 12 deleted
symbols. Row-D aggregation-literal bug fixed under a passing byte-identity gate (reproduced RED
first on `agg_literal_probe`; REQ-AST-10 governs it). Count story: net **−5** passed (2005→2000) =
−11 deleted dead-symbol self-tests + 6 new pins/probe. Every D1 residue dispositioned to FILE/NO-OP
(`[SANITIZER-MERGE]`, `[SC11-IMPORT-REWRITE]`, `[GB-PARAMGROUPS-TYPING]`). Handoffs live:
`[ITEM7-PGD06]` activated + REQ-AST-10 flagged for Item 7; doc-19/doc-25 caveats to Item 10.
**Next: `/_my_audit`.** Full close-out in `.project/active/cleanup-debt/plan.md`.

<details><summary>original spec-stage description</summary>

Track B, no deps (schedule before PUSH-DOWN). One reviewed pass: delete two dead
templates + verify-then-delete four dead functions (DOCS-SCRUB-F1), fix four stale
docstrings (F3), fix the `_walk_aggregation_ast` literal-before-invocation dispatch bug
(R4 reproduce + byte-identity gate + literal-bearing fixture; retires doc-19 hedge), pin
the dotted-leaf alias edge (retires doc-25 hedge), disposition D1 residue F1–F5, assess
SC-11 import rewrite, drop 4 vacuous skipifs. Handoffs: `_deserialize_constraint_info`/
`extract_all_constraints` → Item 4; REQ-PGD-06 re-frame → Item 7; doc caveats → Item 10.
Sequencing: agg-fixture capture runs entirely before OR after Item 4's snapshot v2 bump,
not interleaved. Spec: `.project/active/cleanup-debt/spec.md`.

</details>

### PIPELINE-TRUTH Item 6 — Self-Referential Test Remediation — audited PASS-WITH-NOTES (2026-07-06)
Track B, no deps. Re-anchor the 25 §D5 flagged tests (7 HIGH + 10 MEDIUM + 8 LOW) to
hand-transcribed fixture literals; convert `test_localterm_sibling_agg_output` (MF-07)
from pass-or-skip to pass-or-FAIL; re-anchor REQ-REG-02 to on-disk paths; add SC-6
render pins + a tests/conformance anchoring note. EXT-09 handed off to Item 4. Matrix
rows are Item 7's. Spec: `.project/active/test-truth/spec.md`.
**Audit (`.project/active/test-truth/audit.md`):** anti-pattern gone (static sweep + 5
spot-checks); 5 literals independently confirmed vs committed snapshots; −26 count = param
reduction + 4 new fns, no fn deleted; all 25 dispositioned; EXT-09 handoff clean; doubling
notes present; README accurate. **Open (1 note):** the mutation spot-check (SC-2) could not
be reproduced at audit — pytest gated in the non-interactive stage context; corroborated
statically + by the orchestrator's live gate (2005/4/5) + the close-out's 3 RED→revert→GREEN.
Recommend one licensed reproduction to close SC-2.

### PIPELINE-TRUTH epic — DEFINED (Draft, awaiting scope review)
Shaped 2026-07-06 from `.project/active/NEXT_EPIC_PROMPT.md` via `/_my_epic_plan` with
the mandated 8-agent discovery sweep. Mission: the generated package is the truth —
fusion-tea generates/wires/executes end-to-end, zero bridges; every diagnostic fires on
the shape it claims; zero self-referential tests; REQ/matrix truth. 10 items,
~10.5–13.5 days, two tracks (headline: Items 1–3 fixtures → whole-plant resolution →
fusion-tea acceptance; truth track: Items 4–8 parallel; 9–10 close).
- Epic: `.project/backlog/epic_pipeline_truth.md`
- Evidence base: `.project/research/20260706_pipeline-truth-discovery.md` (D1–D7 +
  adversarial; 16 silent-failure sites, 25 tests-that-cannot-fail, the D6 fixture
  recipe reproducing 9/10 V11 offenders, subtype-blind enumeration verdict table incl.
  agentic-mbse's always-passing Level-3 validator)
- BACKLOG updated: PIPELINE-TRUTH added (P1), whole-plant item promoted out of Ideas,
  [CONSTRAINT-SILENCE] filed (P1, absorbed into Item 4), UPSTREAM-FINDINGS moved to
  Completed, PUSH-DOWN sequencing ruling recorded (after Items 5+8).
- Notable corrections made during discovery: the fusion-tea report's line-74
  capture-path claim is wrong (capture DOES run the constraint report; the silence was
  the assert bug itself), and constraints are NOT serialized into snapshots (the
  NEXT_EPIC_PROMPT claim was wrong; `_deserialize_constraint_info` is dead code).
- Next: user reviews scope/decomposition; then spec Item 1 (fixtures) and Item 4
  (subtype enumeration) — the two no-dependency track heads.

### docs-scrub — CERTIFIED and MERGED (PR #4, 2026-07-06)
Post-epic coherence pass over `docs/architecture/` on branch `docs-scrub` (off
`upstream-findings-epic`): 31 docs verified/corrected against HEAD; matrix now
248 = 236 PASS + 12 UNTESTED (SNAP/NC/REG rows added); thin docs 07/10/11/17/24
closed; 22/23 verified live, 26 marked Historical; gate byte-identical
(1989/4/5, ruff 21, mypy 109). Independent audit: Certify (3 gaps found+cured).
Follow-ups filed: BACKLOG DOCS-SCRUB-F1..F4 (F4 = resolve_input() has zero
production callers while its REQs are marked PASS). Artifacts:
`.project/active/docs-scrub/{spec,plan,fact-sheet,audit}.md`.

### Next-epic definition — EXECUTED (2026-07-06)
`.project/active/NEXT_EPIC_PROMPT.md` was executed; deliverables are the
PIPELINE-TRUTH entry above. The prompt file is kept for provenance.

### UPSTREAM-FINDINGS Epic — MERGED (PR #3, 2026-07-06)

All 12 items landed and audited PASS on branch `upstream-findings-epic`
(orchestrated run, 2026-07-05..06). PR: https://github.com/1cFE/sysml-codegen/pull/3

**One action for the human**: the companion agentic-mbse PR. Branch
`upstream-findings-sync` is pushed to origin (6 commits); the prepared PR body is
committed at `.project/active/AGENTIC_MBSE_PR_BODY.md` — create with:
`gh pr create --repo 1cFE/agentic-mbse --base main --head upstream-findings-sync --title "UPSTREAM-FINDINGS sync: validation checks + guidance for the newly supported subset" --body-file .project/active/AGENTIC_MBSE_PR_BODY.md`

Post-merge follow-ups already filed: BACKLOG P1 (remaining 10 fusion-tea
cross-part bindings), the stale-fixture drift chore, C7/C8/F6 in agentic-mbse's
backlog, and the fusion-tea coordination notes in the three release-notes files.


## Recently Completed

### 2026-07-13: CONSTRAINT-EXEC Epic — Constraint Execution and Design-Space Studies
- All 15 items (0–14) implemented, adversarially reviewed, and audit-certified across four
  repos in one orchestrated run; independent findings audit reproduced every sampled claim
  exactly (`completed/20260713_epic_constraint_execution_audit_independent.md`).
- Modeled `assert constraint` now lowers to Kleene-compiled graph modules + exact-schema report
  aggregator; snapshots carry constraint facts (v3); packages seal with verified-on-load
  contracts; crash-safe study layer (evaluator → store/runner → policy/query/CLI); IFE
  acceptance 2294/2301 + 7 model-favoring boundary rows ([OWNER] ratified); hand viability rule
  deleted. CE-F3 fixed post-run (teax `0d606a4`); CE-F1/F2 registered follow-ons.
- Gates at close: sysml-codegen 2330/23, mypy 76 baseline, ruff clean; agentic-mbse 1401/1;
  teax fully green 262 (pre-existing path bug also fixed, `1b63272`).

### 2026-07-08: TRUTH-DEBT Epic
- Archived all six audited items plus the epic ledger to `.project/completed/`.
- Retired the F4 aggregation cutover, resolved multi-hop chain support, matrix test gaps,
  inherited-attr classifier fix, matrix sweep residue, and D3 hygiene tail.
- Pre-PR gates: 2120 passed / 4 skipped / 0 xfailed; ruff src clean; mypy src 97;
  matrix 259 = 258 PASS + 1 UNTESTED.

### 2026-02-17: Phase 5 — E2E Pipeline Validation (5.2) — Checkpoint 5
- 16 conformance tests in `tests/conformance/test_pipeline_e2e.py`
- catf_mfe baseline generated: 42 modules (all CalcUsage), 8 EP groups
- Baseline comparison for all 4 models (solar_battery, catf_mfe, chain_spike, attr_expr_probe)
- REQ-PIPE-01 through REQ-PIPE-06 validated end-to-end
- Checkpoint 5: All 4 models match baselines — refactored pipeline composes correctly
- No production code changes — conformance-only

### 2026-02-17: Phase 5 (partial) — Orchestrator Step Ordering (C19)
- 39 conformance tests in `tests/conformance/test_orchestrator.py`
- Static analysis: `build_pipeline_context()` 10-step DAG ordering verified
- FORMULA removal safety net verified (zero natural overlap in fixtures; constructed overlap exercises logic)
- Registry 4-phase ordering: all aliases target Phase 1 canonical channels (solar_battery + catf_mfe)
- Pipeline invariants (PIPE-01–06) verified across 4 models (solar_battery, catf_mfe, chain_spike, attr_expr_probe)
- REQ-PIPE-07 baseline: 9 generation/ files import from extraction/analysis (Phase 7.6 target)
- No production code changes — conformance-only

### 2026-02-17: Phase 4 — Module Factory + Graph Assembly
- C14 CalcUsage Factory (48 tests), C15 FORMULA Factory (34 tests), C16 Aggregation Factory (32 tests)
- C17 Entry Point Classification (35 tests), C18 Graph Assembly (34 tests)
- Checkpoint 4 baseline comparison: solar_battery, chain_spike, attr_expr_probe match Phase 0 baselines
- All 3 module types verified (CalcUsage + FORMULA + Aggregation)
- Baseline normalization documented: CalcUsage compilability (snapshot serialization boundary), parameter ordering (dict iteration order)
- All design doc amendments applied (06-entry-point-classifier.md, 11-analysis-backtracker.md)

### 2026-02-17: Phase 3 — Analysis Components
- C11a Backtracker Conformance (43 tests), C11b Typed Dispatch Migration (17 tests)
- C12 Input Resolver (26 tests), C13 ParameterGroupDeriver (30 tests), X02 Dual Resolution (20 tests)
- Backtracker fully migrated to typed dispatch: scoped_lookup/sysml_qn_lookup/alias_lookup
- `_compat` dict, `resolve()`, `register()` removed from OutputRegistry
- 14 previously compat-only resolutions (12 catf_mfe + 2 solar_battery) now typed
- D3: Static analysis helpers extracted to `tests/helpers/static_analysis.py`

### 2026-02-17: Phase 2 — Core Infrastructure Spikes
- C08 Output Registry (32 tests), C09 Virtual Binding Rewrite (38 tests), C10 Aggregation Scoping (47 tests)
- 5 NewType wrappers + 3 typed registries implemented
- Phase 2 audit: 6 fixture coverage gaps investigated (C1-C6), 4 closed, 1 partially closed, 1 pending

### 2026-02-17: Phase TRR — Typed Registry Refactor (Design Docs)
- All 8 TRR design doc updates applied (docs 03, 04, 09, 10, 11, 15, 24, 27)
- New design intent doc: `27-typed-registry-refactor.md`

### 2026-02-17: Phase 1 — Foundation & Extraction Components
- C01-C07, all 49 requirement IDs verified

### 2026-02-17: Phase 0 — Test Infrastructure & Baselines
- Extraction snapshots for 6 models, pipeline baselines for 4 models

### 2026-02-10: COST-PATTERN Items 1-4
- Hierarchy-aware codegen: templates, redefinitions, aggregation, pipeline integration

---

## Up Next

1. **Merge the CONSTRAINT-EXEC PR wave** (human): agentic-mbse #11 FIRST — **now load-bearing,
   not just convention**: #9's codegen pins `executable-profile/v3` at runtime and refuses the
   pre-v3 profile, so merging #9 before #11 (at `05cde35`) breaks main. Then sysml-codegen #9;
   teax rwestwood89/teax#3 independent; after #11+#9 merge, push fusion-tea:
   `git -C ~/1cfe/fusion-tea push origin main` (4 acceptance commits waiting). Note: agentic-mbse
   local branch tip `4ed2a07` ("modeling workflow orchestrator", separate workstream) was
   deliberately NOT pushed — PR #11 was updated by ref to `05cde35`; that commit awaits its own
   owner. After the wave merges: `/_my_close` for numerical-constraint-profile + the remediation.
2. **pipeline_explainer_v2.html build** (`[V2-HTML-BUILD]`, P2): the refreshed
   `EXPLAINER_PROMPT.md` is landed and buildable — another agent picks this up.
3. **CE-F1/F2 follow-ons** (BACKLOG): direct TEAx consumption of codegen's embedded catalog with the
   alternate catalog schema/materializer removed, plus multi-channel CandidateBridge (teax). CE-F3
   is fixed.

---
