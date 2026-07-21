# Audit: Canonical Embedded Catalog and Store Transition (Lifecycle Item 8)

**Verdict:** Certify — pass with notes
**Audited:** 2026-07-20
**Branch:** constraint-exec-epic
**Commits:** codegen `0e1b310` (Phase 1 `19b74ac` + docs), teax `a5594e1`, fusion-tea `667136fa` (branch `item8-fusion-embedded-catalog`)

---

## Summary

The item delivers its substance and every executable gate reproduces first-hand. Codegen's
embedded catalog now carries the five projected identity fields plus a deduped admitted-usage
tier; the `definition_qualified_name` FK is gated strictly on `definition_typed` and I confirmed
by live probe that a named-inline usage gets an honest `None` with no dangle. TEAx consumes the
embedded catalog through one seam, binds compatibility to the real `semantic_fingerprint`, and
fails closed on schema skew both directions. The alternate system — the byte-hash stand-in, the
standalone `constraint_catalog.json`, the fusion materializer — is genuinely gone, no shim, and
the reconstruction anti-patterns (QN-split, predicate-text search, hardcoded `source_form`) are
absent from every product path across all three repos. The six design-review Majors (F1–F6) are
landed in code.

Two moderate findings are **missing regression guards the spec and design explicitly named**, not
correctness defects: F1's named-inline test assertion is vacuous (the tripwire the design review
demanded is unarmed), and the INV-6 source-scan test that spec criterion #2 and the design's
Validation Approach both call for does not exist. The behaviours those guards would protect are
verified correct today; what's missing is the committed tripwire. Two minor notes follow. On that
basis: **Certify, pass with notes.**

## Reproduced gates (first-hand)

- **codegen full suite** (license loaded via `agentic-mbse/.env`): **3080 passed / 44 skipped /
  17 deselected** — matches evidence exactly. Catalog conformance tests ran non-vacuously (not
  skipped), confirming the license is live.
- **codegen catalog surface:** `test_catalog_usage_tier` (6), `test_catalog_definition_join` (4),
  `test_catalog_schema_version` (2) — 12 passed. Re-pin: `test_constraint_snapshot_portability`
  3 passed (`SNAPSHOT_MANIFEST_SHA256`).
- **teax full suite:** 286 passed (286 progress dots, exit 0, zero F/E) — matches evidence.
- **teax skew:** `test_model_contract_skew` 5 passed (newer/older/missing all fail closed).
- **fusion seam proof:** reran `prove_catalog_seam.py` myself → GREEN. schema 2.0.0, 1 eligible
  entry, `source_form=definition_typed`, `definition_qn=fusion_cycle::'Viability Threshold'`,
  verdict satisfied. Zero-entries guard is a real `SystemExit`.
- **fusion package tests:** 6 `test_import_and_run` passed (once the package is importable as
  `ife_tea`).

## Findings

### Plan completion

All three phases complete and verified. Phase 1 (codegen additive), Phase 2 (TEAx cutover +
deletion), Phase 3 (fusion regen → prove green → delete) all landed with the phase order honored.

### Spec conformance

- **SC "Catalog totality" — MET.** Each eligible entry carries `source_form`,
  `source_local_identity`, `owner_qualified_name`, `definition_qualified_name`, and the existing
  `usage_qualified_name` (`resolution/models.py:467-525`); the new `usage_records` tier exists
  (`ConstraintCatalogUsageRecord`). TEAx reads owner QN / definition QN / source form / usage
  identity / the join straight from the entry (`teax study/query.py:65-73`); no QN split, no
  predicate-text search, no hardcoded source form in any consumer. The four catalog tiers
  (source/usage/occurrence/excluded) are present in the regenerated IFE package; "result" is the
  runtime verdict, which the seam proof produced from the embedded catalog alone.
- **SC "Named alternate system gone, not shimmed" — MET IN SUBSTANCE, verification gap (see
  Code integrity F-B).** The byte-hash stand-in, the standalone `constraint_catalog.json`, the
  hand-authored fixture, and the fusion materializer are all deleted; reconstruction absent
  everywhere (grep-verified in codegen, teax, fusion). But the spec's stated verification — "a
  source-scan test asserts no surviving symbol (`CatalogView`, `_Catalog`) … and no reconstruction
  workaround" — is not delivered, and `CatalogView`/`_Catalog` survive as **repurposed**
  embedded-view symbols.
- **SC "Real identity, consumed as data" — MET.** `study/config.py:79-86` returns
  `load_model_contract(...).semantic_fingerprint`; no `hashlib` byte read remains; consumed as
  on-disk JSON (no `import sysml_codegen`). Guarded by
  `test_model_contract_skew.py::test_real_fingerprint_is_read_not_a_byte_hash`.
- **SC "Store never silently rebinds" — MET.** `study/store.py:147-151` `_check_compatibility`
  raises `IncompatibleStore` on any mismatch of the unchanged eight-field binding; only the
  fingerprint value's provenance changed. Gate shape untouched.
- **SC "Skew fails closed, both directions" — MET.** `study/model_contract.py:45-52` raises the
  named `IncompatibleCatalogSchema` before any field read; `raw.get("catalog_schema_version")`
  yields `None` (no `KeyError`) and newer/older/missing all fail the `ACCEPTED_CATALOG_SCHEMA_VERSIONS`
  membership test. Five RED-first tests confirm both directions.
- **SC "RED-first public surface" — MET, with the F1 sub-case gap in Code integrity F-A.** The
  fields, usage tier, direct-consumption path, and skew guard each have RED-first tests exercised
  through public seams.

### Design conformance — the six F1–F6 Majors

- **F1 (FK gated strictly on `definition_typed`) — CODE CORRECT, test guard vacuous.**
  `constraint_lowering.py:1209-1216` sets `definition_qn` iff `usage.source.form ==
  "definition_typed"`, else `None`. Live probe: `constraint_inline` (a named-inline eligible
  usage) yields `def_qn=None`, no dangle; `constraint_multi_instance` and `wi014_toy` yield
  resolved non-dangling FKs. Mechanism verified. **But** the test that is supposed to guard it
  (Code integrity F-A) never exercises the named-inline case.
- **F2 (anonymous dedup by full identity) — MET.** `_assemble_usage_records` keys on
  `(usage_qualified_name, source_local_identity)` (`generation/constraint_catalog.py:150-176`);
  `test_usage_tier_distinguishes_two_anonymous_usages_by_local_identity` proves two `"<anonymous>"`
  usages yield two rows.
- **F3 (rewire honesty) — MET.** D2 reframed "1:1 replacement" to same-cardinality/changed-key;
  TEAx re-keys on the full QN, reads the new `usage_records` (not the per-definition
  `source_records`), and `predicate_ir` stays single-authority on the occurrence tier
  (`test_usage_tier_does_not_carry_predicate_ir`).
- **F4 (re-seal, not rm) — MET, exceeded.** The sealed_package fixture was fully **regenerated**
  (a stronger action than re-seal — evidence "scope surprise" records the fixture was ancient, not
  merely covered). Its `package_contract.json` `artifact_hashes` lists only the files that exist
  (`model_contract.json`, `generation_manifest.json`, `verify.py`); no `constraint_catalog.json`
  orphan; manifest coherent — the Item-7 verifier is not broken.
- **F5 (INV-6 scoped) — MET in prose.** Design INV-6 is scoped to the reconstruction anti-pattern,
  not a blanket QN-split ban. (The *test* that would enforce it is missing — F-B.)
- **F6 (single `SNAPSHOT_MANIFEST_SHA256` re-pin) — MET.** Portability test passes at the new pin;
  the full suite is green, so no other conformance/seal/anchor pin moved. Graph baselines
  unmoved (catalog is `exclude=True`).

### Code integrity

- **F-A (moderate, non-blocking) — F1's named-inline regression guard is vacuous, and the test
  docstring overclaims.** `tests/conformance/test_catalog_definition_join.py:21,45` parametrizes
  only `constraint_multi_instance` and `wi014_toy`. My live probe shows **both are 100%
  `definition_typed`**, so the test's `else` branch — the assertion that a non-`definition_typed`
  entry carries `None` — never executes. The test's own docstring (`:3-7`) claims named-inline
  coverage ("Named-inline eligible constraints … carry `None`, not a dangling self-reference"),
  which is aspirational: no named-inline entry reaches it. The unit test
  `test_entry_carries_none_definition_qn_for_inline` (`test_catalog_usage_tier.py:97`) only checks
  that assembly projects a hand-set `None`; it does not exercise the lowering gate. A regression
  that set the FK from `effective_source.qualified_name` unconditionally (the exact bug F1 was
  raised about) would pass every committed test. **Fix:** add `constraint_inline` to the
  parametrize list — the fixture exists and I confirmed it arms the branch. Trivial; the code is
  already correct.
- **F-B (moderate, non-blocking) — the INV-6 source-scan test the spec and design both name does
  not exist.** Spec success-criterion #2 requires "a source-scan test [that] asserts no surviving
  symbol of the alternate catalog schema (`CatalogView`, `_Catalog`) … and no reconstruction
  workaround," and the design's Validation Approach (`design.md:308`) commits to a "source-scan
  test for INV-6." Neither codegen nor teax has one (confirmed: evidence's RED list is
  skew/usage/join/schema only; grep finds no source-scanning test). The reconstruction is in fact
  absent (I verified by grep across all three repos), so this is a missing tripwire, not a live
  defect. Compounding: `CatalogView`/`_Catalog` survive as repurposed embedded-view symbols
  (`teax study/query.py:24-73`), so the spec's literal "no surviving symbol" is met only if read
  as "no surviving *alternate-schema* symbol." The design rewired rather than deleted — a
  defensible call — but that spec-vs-design shift on criterion #2, and the dropped source-scan
  test, are not explicitly reconciled in the design's Non-Goals or handoff. **Fix:** either add the
  named source-scan test (it would need to assert the *reconstruction* patterns are absent, not the
  `CatalogView` symbol, given the rewire), or record in the design that the symbol-deletion framing
  was superseded by the rewire and the guard reduced to the grep-verified reconstruction ban.
- **No slop / failure-honesty defects.** The skew guard raises a named error, not a default. The
  usage-tier assembly asserts eligibility invariants rather than silently coercing. No broad
  excepts, no compat shims, no optional-param-papering introduced.

### Deletion reality (all three repos)

- **codegen:** additive only; no deletion targets. `CatalogView`/`_Catalog`/byte-hash/materializer
  never lived here.
- **teax:** byte-hash stand-in → real fingerprint (no `hashlib`); standalone `constraint_catalog.json`
  reader/writer gone; no hand-authored fixture under `tests/`; reconstruction absent. `CatalogView`/
  `_Catalog` **repurposed** (see F-B).
- **fusion-tea:** `materialize_constraint_catalog.py` deleted in `667136fa` (96 lines, no importers);
  committed `generated/contracts/constraint_catalog.json` removed; `run_viability_study.py` rewired
  to `StudyQuery(store, PACKAGE_DIR)` with a real zero-entries guard; reconstruction absent.

### Batteries / untouched surfaces

- Batteries reproduced at all three candidates (see "Reproduced gates").
- Items 1–7 surfaces untouched: the full codegen suite (3080) includes all prior-item conformance;
  teax 286 includes Item-7 seal/verifier tests. No Item-7 pin moved but `SNAPSHOT_MANIFEST_SHA256`.
- Store no-silent-rebind gate preserved (eight-field binding, unchanged shape).
- **stellarator repo untouched at `bceaf40a`** with its uncommitted Gate-B filing intact (modified
  `20260719-082509_gate-b-root-cause…md` + untracked research files; HEAD unmoved).

### Evidence honesty

- The **wi014_toy full-regen scope surprise** is recorded plainly (evidence "Scope surprise"):
  the sealed_package fixture was ancient, so Phase 2 required a full regeneration, not the re-seal
  F4a assumed. Honest, and the stronger action.
- The **Item 9 handoff** (MultiChannelEvaluator staleness from the 4→3 channel decomposition) is
  recorded, not absorbed: flagged in `prove_catalog_seam.py:11-15`, the Phase-3 commit message, and
  evidence "Out-of-scope divergence." Deferred to Item 9, not force-fixed.

---

## Certification

Verified first-hand and reproduced: all three batteries (codegen 3080, teax 286, fusion seam proof
+ 6 package tests), the F1 mechanism by live probe, F2/F3/F4/F5/F6 in code and tests, the both-way
skew guard, the store gate shape, the deletion reality across all three repos, the stellarator
untouched state, and evidence honesty on the two disclosed surprises. Spec success criteria 1, 3,
4, 5 verified met; criterion 2 met in substance with a missing verification test (F-B); criterion
6 met with the F1 sub-case guard gap (F-A).

Marked: spec success criteria 1/3/4/5/6 (`- [x]`); criterion 2 left with a note. Epic Item 8 not
yet ✅-marked pending the owner's call on whether F-A/F-B (missing guards, behaviour verified
correct) block or ride as follow-ups — both are one-test fixes.

**Notes (minor, non-blocking):**
- **N1 — seam-proof reproducibility.** `prove_catalog_seam.py` fails closed on a package tree where
  the package's own pytest has run: a stale `generated/tests/.pytest_cache/` trips the Item-7 seal
  verifier's EXTRA-file check (`SealVerificationError`). Not an Item-8 defect — a consequence of
  strict sealing — but a future reproducer must clean build artifacts first. Worth a one-line note
  in the script or evidence.
- **N2 — Item-9 breadcrumb.** The MultiChannelEvaluator staleness note lives in the sibling
  `prove_catalog_seam.py` and the commit message, not inside `run_viability_study.py` itself, whose
  docstring still describes the retired 4-channel decomposition as current. A reader opening only
  that file gets no warning it will crash on the missing `hif_driver_params.json`. Honestly recorded
  elsewhere (not silent), but a missing inline marker.

**Not checked:**
- The RED-first *pre-change* failure state was not independently reproduced by revert this pass;
  the tests are confirmed GREEN through public seams and the evidence records the RED. (Prior epic
  audits reproduced RED by revert; skipped here on budget, as the mechanisms are code-verified.)
- Full-suite per-line license-skip grep (confirmed the license is live via the catalog conformance
  tests running non-vacuously and `SYSIDE_LICENSE_KEY` set; did not enumerate every skip reason in
  the 3080-test run — the 44 skips match the Item-7 licensed baseline).
- mypy / ruff not re-run this pass (evidence claims 72 mypy unchanged, ruff clean on changed files;
  the changed surface is small and the full suite is green).
- agentic-mbse not diffed (item touches codegen/teax/fusion only; no agentic-mbse change claimed).
- The 2,301-point acceptance sweep (explicitly Item 13's bar, not this item's) — the seam proof's
  representative-run scope label is honest and I confirmed it.
- The PR push (Item 13's; nothing pushed this session).
