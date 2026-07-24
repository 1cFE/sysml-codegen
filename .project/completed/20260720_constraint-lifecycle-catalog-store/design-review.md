# Design Review: Canonical Embedded Catalog and Store Transition (Lifecycle Item 8)

**Design:** `.project/active/constraint-lifecycle-catalog-store/design.md`
**Spec:** `.project/active/constraint-lifecycle-catalog-store/spec.md`
**Review File:** `.project/active/constraint-lifecycle-catalog-store/design-review.md`
**Date:** 2026-07-20
**Reviewer:** independent (fresh session); verified in codegen (`14d4901`), teax (`98a6d07`), agentic-mbse (`4c18d61`), fusion-tea (`bfff2b4f`).

---

## Fundamental Assessment

**Sound.** The core move is right and it is the simple one: codegen already computes owner QN,
definition QN, usage short name, and source form, then throws them away at the catalog *entry*
projection boundary; TEAx rebuilds them by QN-splitting, predicate-text search, and a hardcoded
source form. The fix — project the fields at the loss boundary, let TEAx read the embedded catalog
straight from `model_contract.json`, delete the alternate schema/materializer/stand-in — removes a
whole parallel system rather than adding machinery. It composes with the Item 4/7 version-pin and
seal rails instead of duplicating them. No simpler design meets the spec: the alternative (recover
the fields consumer-side) is exactly what is being deleted.

So this is **Approve-with-revisions**, not Rework. The findings below are precision and correctness
defects in specific mechanisms (the FK rule, the usage-tier dedup key, the "1:1" framing, two
mis-grounded inventory lines, one over/under-stated blast radius, one over-broad invariant). Each is
fixable by tightening a rule or correcting a cite; none touches the architecture.

**De-risk gate (B4) — CONFIRMED, thin.** The committed IFE package
(`fusion-tea/exploration/ife_e2e/generated/contracts/model_contract.json`, clean at `12d88636`,
regenerated live via codegen) carries exactly **one** eligible `concrete_entries` row
(`hif_plant_pkg__hif_plant__viability__…`, `expected_value: True`). Phase 3 is not blocked upstream —
the IFE study can run GREEN on the embedded catalog. Caveat: the margin is exactly one. If that
single viability constraint ever stops being eligible, the study runs on zero cases. Worth stating in
the phase-3 gate so a future zero is read as a regression, not an empty pass.

---

## Dimensional Review

### 1. Spec Compliance
**Assessment:** Concerns

The design carries the spec's outcomes — five projected fields, the admitted-usage tier, direct
consumption, real fingerprint, fail-closed skew, phased RED-first. Three compliance defects:

- **The FK rule (D1) does not match the code it cites** — see Finding F1. The spec requires a real
  `definition_qualified_name` with the def→usage join carried on the entry; D1's stated mechanism
  populates a *dangling* value for named-inline usages.
- **The file:line inventory is mis-grounded in two places** (F4). The spec's own stated value is that
  "a missed consumer becomes a broken deletion," so a wrong cite is a compliance defect, not a nit.
- **INV-6 regressed the spec's precise phrasing** (F5). Spec success-criterion #2 scopes the ban to
  *reconstruction* workarounds (`rsplit("::")` on a QN to recover a join, predicate-text search,
  hardcoded source form). The design's INV-6 flattened that to "No product path splits a QN," which
  is false at HEAD.

Provenance handling is otherwise faithful: D-3 stays settled and unre-opened; the `[SURFACED]` fusion
target conflict (brief pinned `-stellarator-mbse-demo`; grounded evidence points at
`fusion-tea/exploration/ife_e2e`) is resolved by the orchestrator ruling the design records at
`design.md:22-23`, not silently — correct under capture-fidelity law 4.

### 2. Pattern Consistency
**Assessment:** Pass (one minor)

`CATALOG_SCHEMA_VERSION` in `contracts/versions.py` fits the existing codegen-owned constant pattern
(`RUNTIME_CONTRACT_VERSION`), and a TEAx-side `ACCEPTED_CATALOG_SCHEMA_VERSIONS` beside
`ACCEPTED_RUNTIME_CONTRACT_VERSIONS` mirrors the vendored-and-checked cross-repo rail exactly. No new
module, no second mechanism — D3's "no duplicated version machinery" holds. The single-seam
`load_model_contract` (D4) follows the "one reader owns the version check" shape already used for the
seal. Minor: D3's "a drift test already guards the pin" is imprecise — see Minors.

### 3. Abstraction Quality
**Assessment:** Concerns

The three-tier shape (definition / usage / occurrence) with a definition-QN FK is the right
decomposition. But two abstractions are underspecified:

- The **usage tier's identity key** is left implicit as `usage_qualified_name` (INV-2), which is not a
  unique per-usage identity for anonymous usages (F2).
- The **"1:1 replacement" abstraction** (D2) papers over a real access-pattern change on the TEAx side
  (F3): the join key type changes, and the new tier sits next to an existing same-role
  (`source_records`) tier with different grain.

### 4. Duplication Avoidance
**Assessment:** Concerns

The design accepts one deliberate duplication (entry-level identity vs. usage-tier identity, D2) and
guards it with INV-2 — reasonable, owner-directed. But a second, un-named duplication appears once you
follow the inline case: `predicate_ir` already lives on every `concrete_entry` (guarded by
`assert_same_ir`), and the usage tier would carry it again. The design should name one authority for
`predicate_ir` rather than emit two copies (F3, part c).

### 5. Data Structure Clarity
**Assessment:** Concerns

Field-level clarity is good, but three data-shape questions are unresolved:

- What is the usage tier's dedup key when `usage_qualified_name == "<anonymous>"`? (F2)
- What is `definition_qualified_name`'s exact null contract across the source-form ladder? "None for
  inline" is stated but contradicted by the cited mechanism (F1).
- The join key's *type* changes from TEAx's short `usage_name` to codegen's full
  `usage_qualified_name`; codegen entries carry no `source_usage` field at all (F3, part a). The
  design describes this as reading "the entry FK" without noting the key type moves.

### 6. Route Safety
**Assessment:** Concerns

Fail-closed skew (INV-4) and no-silent-rebind (INV-5) are structurally sound: the eight-field
compatibility binding is exact-equality checked at store open (`study/store.py:147-151`), so changing
the fingerprint *value* alone forces a new lineage — confirmed, shape unchanged, only provenance
changes. The one route defect is INV-6's over-broad source-scan (F5), which either false-positives
across ~10 legitimate codegen QN-splits or gets watered down to catch nothing.

### 7. Bets & Decisions Integrity
**Assessment:** Concerns

- **B1** (definition_typed FK resolves to a source record) — **holds for definition_typed**:
  `_referenced_definition` (`constraint_lowering.py:915-935`) resolves against `facts.definitions`,
  the same set `source_records` is built from. But the bet's grounding **glosses the inline arm**,
  where the design's own D1 rule would produce a dangling FK (F1). The bet is true; the decision that
  rests on it is mis-stated.
- **B2** (five identity fields invariant across a usage's occurrences) — **holds**: the multi-instance
  loop (`constraint_lowering.py:1209-1324`) sets identical `usage_qualified_name`/`source_local_identity`/
  `source_form`/`owner_kind`/`owner_qualified_name` across occurrences, varying only
  `owner_instance_path` and `constraint_id`. Dedup collapses them correctly — *for named usages*.
- **B3** (only the alternate readers consume the standalone file) — **mostly true, one miss**: the
  sealed_package's `package_contract.json` seal manifest lists `constraint_catalog.json` in its
  `artifact_hashes` (F4a). Deleting the file without re-sealing breaks the Item-7 verifier.
- **B4** (IFE package emits ≥1 eligible entry) — **CONFIRMED** from committed state (exactly one).
- **Hidden bet surfaced:** the design bets `usage_qualified_name` is a unique per-usage identity and
  that TEAx's index key matches codegen's entry key. Both are false in reachable shapes — anonymous
  usages (F2) and the short-name-vs-QN key gap (F3). These are the most expensive kind because they
  are unstated.

### 8. Reader Comprehension
**Assessment:** Pass

The design reads well. The core concept — "stop the information loss at the projection boundary" —
is stated plainly before the mechanism, and the three-tier model is easy to hold. Bets carry explicit
"if false → what fails" clauses. No comprehension-blocking jargon. The prose is not the problem here;
the mechanism precision is.

---

## Issues by Severity

### Critical
- None. The approach is sound and B4 is confirmed; nothing blocks proceeding to a revised design.

### Major
- **F1 — D1's FK rule is mis-stated; named-inline usages get a dangling `definition_qualified_name`.**
  D1 says set the field "from `effective_source.qualified_name` where `_verified_predicate_source_key`
  already has it (None for inline)." But that key builder has a *non-None* `effective_source.qualified_name`
  for **named inline** usages too: for `form == "inline"`, `_verified_effective_predicate_source`
  (`constraint_lowering.py:943-944`) returns `usage.identity` — the usage's own QN — and the ladder at
  `:647-649` emits `inline:<usage_qn>`. `source_records` are built only from `facts.definitions`
  (`constraint_catalog.py:77-83`), so a usage QN is not among them. Implemented literally, a named
  inline eligible constraint gets `definition_qualified_name = <its own usage QN>` → dangling FK,
  violating INV-1 and falsifying B1 for that case. **Fix:** gate the assignment strictly on
  `usage.source.form == "definition_typed"` (None otherwise), and add a *named inline* eligible
  constraint to INV-1's test — not just definition_typed + anonymous inline. (Priority 2.)

- **F2 — the usage-tier dedup key breaks for anonymous usages.** INV-2 dedups "one `usage_records[]`
  row per distinct `usage_qualified_name`." Anonymous eligible usages all carry
  `usage_qualified_name = "<anonymous>"` (`constraint_lowering.py:1128`, set on the entry at `:1313`).
  Two distinct anonymous eligible constraints therefore collide on the key: either they collapse to
  one row (silent data loss) or they trip INV-2's identity-equality assertion (their
  `source_local_identity`/locations differ), aborting generation. **Fix:** dedup the usage tier by the
  usage's *true* identity — `usage_qualified_name` **plus** `source_local_identity` (or the underlying
  `ConstraintUsageFact` identity) — and state that anonymous usages are distinguished by
  `source_local_identity`. The occurrence tier is already safe (keyed by `constraint_id`, which folds
  in location for anonymous, `:1141-1153`).

- **F3 — the "1:1 replacement of TEAx's `_source_records[usage_name]` index" understates the rewire.**
  Cardinality is right ("one row per admitted usage, deduplicated across occurrences"), but it is not
  drop-in: (a) **join key type changes** — TEAx keys on the *short* `usage_name` (e.g. `"affordable"`)
  and reads `entry["source_usage"]`; codegen's embedded `concrete_entries` carry the *full*
  `usage_qualified_name` and have **no `source_usage` field**, so `_Catalog` must re-key and change the
  lookup. (b) **name/grain collision risk** — codegen's embedded catalog *already* has a
  `source_records[]` tier, but per-**definition** (`{definition_qualified_name, formal_names}`),
  lacking `usage_name`/`source_form`/`owner_qn`; TEAx must read the new `usage_records`, never that
  existing tier. (c) **inline population + predicate_ir authority** — for inline-form models the
  per-definition `source_records` is *empty* (it fills only from `facts.definitions`), so
  `usage_records[]` must emit inline rows itself, and since `predicate_ir` already lives on each
  `concrete_entry`, the design must name one authority rather than duplicate it. **Fix:** reframe D2
  from "1:1 replacement" to "same cardinality, changed key and grain," and specify (a)/(b)/(c).
  (Priority 4.)

- **F4 — the deletion inventory is mis-grounded in two places, and misses a seal coupling.**
  (a) **Seal coupling:** `sealed_package/…/contracts/package_contract.json` lists
  `contracts/constraint_catalog.json` among its `artifact_hashes` (25 artifacts). Deleting the file
  without regenerating the seal (new `package_contract.json` + `executable_fingerprint`) orphans a
  covered hash and fails the Item-7 verifier's coverage/integrity check. The design's "delete the
  fixture" line must become "re-seal the fixture package," and it must say so because that touches
  Item-7-certified machinery. (b) **Wrong line cites:** the spec/design cite
  `f1_arithmetic/generate_fixture.py:222/242` as alternate-catalog targets; line 222 is
  `source_form="inline"` and line 242 is a design-attribute leaf split (`.split("__")[-1]`), both
  unrelated. The actual alternate-catalog references are `:190` (import `assemble_constraint_catalog`),
  `:257` (`graph.constraint_catalog = assemble_constraint_catalog(...)`), and the docstring at `:321` —
  and that generator uses codegen's *real* assembly, so "fix to carry real fields" may be pointed at
  the wrong code entirely. Re-ground before the deletion lands. (Priority 3.)

- **F5 — INV-6's source-scan test is unsound as stated.** "No product path splits a QN … (source-scan
  test)" is false at HEAD: codegen legitimately splits QNs in ~10 sites, including
  `core/qualified_names.py:52-53`, `orchestration/pipeline_builder.py:266,330,344,419`,
  `extraction/usage_extractor.py:470,994`, `generation/modules.py:36`, `generation/stencils.py:31`,
  and even `analysis/constraint_lowering.py:973,1300,1304` (formal short-name derivation). A literal
  scan for `rsplit("::")`/`split("__")` false-positives across the codebase. **Fix:** scope INV-6 to
  the *reconstruction* anti-pattern (recovering owner/definition QN or the def→usage join *from a
  usage QN*, predicate-text substring search, hardcoded `source_form`) — restore the spec's
  criterion-#2 phrasing rather than the flattened version.

- **F6 — INV-3's blast radius is both overstated and under-specified.** The design frames
  re-baselining as "large… re-capture all byte-identity baselines" (`design.md:199,235`). On codegen
  that is overstated: `tests/fixtures/baseline_outputs/*/computation_graph.json` do **not** move —
  `ComputationGraph.constraint_catalog` is `Field(default=None, exclude=True)` (`resolution/models.py:561`),
  so the catalog is never serialized into graph baselines; there are no committed contract/catalog
  fixtures under `tests/`; and snapshots don't carry these fields. Meanwhile the design fails to name
  the **one** pin that actually breaks: `tests/conformance/test_constraint_snapshot_portability.py:54`
  `SNAPSHOT_MANIFEST_SHA256` (asserted at `:317`), which hashes a manifest embedding
  `catalog_fingerprint` / `semantic_fingerprint` / `model_contract_bytes` — all of which move, and it
  runs **license-free**, so it fails in ordinary CI the moment Phase-1 fields land. The risk is
  inverted: the plan will budget a big re-capture that isn't there and may miss the single real pin.
  **Fix:** correct INV-3 to name the portability pin and drop the "every baseline" framing on the
  codegen side. Positive: no Item-7 seal/manifest/anchor test breaks — they recompute and assert
  relations, and the verifier-hash anchors (`TRUSTED_VERIFIER_SHA256`, `REVIEWED_VERIFY_SHA256`) are
  catalog-independent. (Priority 6.)

### Minor
- **D3 drift-test phrasing.** "A drift test already guards the pin" conflates two modules: the existing
  drift test (`tests/conformance/test_upstream_pins.py`) covers `_upstream_pins.py`, not
  `versions.py`, and `RUNTIME_CONTRACT_VERSION` has no drift test of its own. `CATALOG_SCHEMA_VERSION`
  fits the file and pattern but inherits no existing guard — it needs a **new** drift test (the
  TEAx-vendored-set-vs-source skew check D3 already commits to). Only "already guards" is wrong.
- **Schema-version fingerprint placement (priority 5).** The design doesn't say whether
  `catalog_schema_version` sits inside the fingerprinted `unfingerprinted` payload
  (`contracts/model_contract.py:59-66`). If inside, a schema bump changes `semantic_fingerprint`
  (probably intended); if outside, it rides alongside without perturbing identity. State it.
- **B4 margin.** The IFE package emits exactly one eligible entry — confirmed green, zero slack. Note
  in the phase-3 gate so a future zero reads as a regression, not an empty pass.
- **Keep the one embedded-catalog guard.** `tests/evaluation/test_f1_arithmetic_fixture.py:41-44` is
  the only regression guard on the embedded `concrete_entries` shape. The Phase-2 rewire must keep that
  shape stable; don't sweep it up as "just an alternate-system test."

---

## Recommendations

1. **Tighten D1 (F1):** state the rule as `definition_qualified_name` is non-None **iff**
   `source_form == "definition_typed"`; add a named-inline eligible constraint to INV-1's test.
2. **Fix the usage-tier dedup key (F2):** dedup by full usage identity
   (`usage_qualified_name` + `source_local_identity`), not `usage_qualified_name` alone; make it a
   test with ≥2 anonymous eligible constraints.
3. **Reframe D2's "1:1 replacement" (F3):** same cardinality, changed key type (short → full QN),
   distinct tier from the existing per-definition `source_records`, inline rows populated, one named
   `predicate_ir` authority.
4. **Re-ground the deletion inventory (F4):** name the re-seal of the sealed_package fixture; correct
   the `generate_fixture.py` line cites (190/257/321, and re-check whether it is even an
   alternate-system target).
5. **Scope INV-6 (F5)** to the reconstruction anti-pattern; restore the spec's criterion-#2 wording.
6. **Correct INV-3's blast radius (F6):** name `SNAPSHOT_MANIFEST_SHA256` as the one codegen pin that
   moves; drop the "every baseline" framing.
7. Fix the D3 drift-test phrasing and decide the schema-version fingerprint placement (Minors).

---

## Resolutions

_To be filled in when the owner engages. Non-interactive review; recorded verdict below._

---

**Overall:** Approve-with-revisions
**Next Steps:** Record resolutions here, then re-run `/_my_design` (or return to the design-agent
session) pointing it at this review to incorporate F1–F6 and the Minors. The reviewer does not edit
the design. No architecture change is required; the revisions are rule-tightening and inventory
correction. Max two rounds — one revision pass should close these.
