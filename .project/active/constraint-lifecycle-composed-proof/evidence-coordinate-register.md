# Evidence-Coordinate Register — Lifecycle Item 13 (Composed Public Lifecycle Proof)

**Status:** Draft (Stage 1 of 3: manifest / work order)
**Owner:** Reid W
**Created:** 2026-07-20
**Branch:** constraint-exec-epic
**Register row:** 17 (strictly last; Items 0–12 are its predecessors)
**Authority:** `.project/concepts/constraint-execution-authoritative-lifecycle-contract.md`
(ratified 2026-07-19) — Appendix C mandatory acceptance matrix and the LC-I09 evidence
coordinate (companion spec `constraint-execution-lifecycle-contract/spec.md:420`).
**Stage brief:** `briefs/manifest.md`.

---

## What this document is

This is the **execution stage's work order**. It enumerates all **41** mandatory acceptance
cases from Appendix C, gives each its full LC-I09 evidence coordinate, and classifies each as
**inherit / rerun / compose**. Its completeness is the deliverable: no skipped cell, no
private-seam substitute, no stale-revision evidence counted. No failure discovered downstream
is fixed in Item 13 — it returns to its owning register row (the epic's dependency discipline
governs). This stage certifies nothing; it defines what the execution stage must run.

---

## The pinned revision set (LC-I09 revision/lock coordinate — global to every case)

Every case below inherits this revision/lock coordinate. A cell that observes anything at a
different revision does not certify (`contract:343`).

| Repo | Pinned commit | Provenance |
|---|---|---|
| sysml-codegen | `7526665` | Item 12 implementation (register row 16). HEAD `0dac91e` = Item 12 audit + this brief; the pin is the certified implementation commit, not HEAD. |
| agentic-mbse | `4c18d61` | Stable since Item 4; unchanged through Items 5–12. Companion profile lock `executable-profile/v4`. |
| teax | `c342b10` | Item 11 candidate (filled at commit; **not yet pushed** — Item 13 owns the push, per `constraint-exec-v3-pr-wave` memory and epic row 17 scope 7). |
| fusion-tea | `2422e715` | IFE consumer, branch `item8-fusion-embedded-catalog` (+ ife regen commits). |
| stellarator | `c4dcdf27` + `c2f10960` + `342cc799` | Demo consumer, branch `feat/stellarator-mbse-demo`. Code frozen at `c2f10960`; `342cc799` is the diagnostic-snapshot refresh. |

**Locks:** frozen `uv` resolution of the pinned triple installs together; profile lock
`executable-profile/v4`; companion/runtime-contract versions have one source and fail closed on
skew (invariants 14, 39). Exact package version strings (`agentic-mbse`, `sysml-codegen`) are
read from Item 0 `constraint-lifecycle-candidate-pin/evidence.md` at execution and re-asserted
via the frozen import/version check; do not restate them from memory.

**Open-predecessor coordinate — global:** **NONE.** Register rows 0–16 are all certified
(Items 0–12; `constraint-lifecycle-legacy-identity` closes row 16 at `7526665`). Every case
therefore records "open predecessors: NONE." Any downstream discovery that reopens a row makes
row 17 non-certifiable until that row re-closes.

**Non-certifying (global, `contract:341`, LC-I09):** a lower-layer synthetic `ConcreteConstraint`,
a private adapter/bridge/materializer/wrapper, a filtered offender set, a hand-authored contract
or catalog fixture, and same-machine path cancellation. None may stand in for a public-seam
observation. "Live" = source extraction through the public CLI; "snapshot" = **relocated** replay
(two checkout roots, never same-machine cancellation); runtime rows follow the exact package
sealed by that generation.

---

## Classification rule (how inherit / rerun / compose were assigned)

The chain advanced **~97 commits**. Every item except Item 12 certified at a codegen commit
**earlier than the pin `7526665`** (Item 1 at agentic-mbse `515e08bb`/TEAx `d545701`; Item 2–11
each at their own earlier codegen commit — see each item's `evidence.md`). Applying the brief's
strict rule ("evidence at a superseded revision REQUIRES rerun"):

- **compose** — the observation includes a **post-generation runtime step** (trusted load,
  prepared/file-backed evaluate, persist, resume, query), a **runtime verdict/margin**, the two
  **consumer acceptances** (IFE, stellarator), the **cross-repo runtime-skew** boundary, or a
  **negative mutation executed on the final sealed thread**. These were never run as one sealed
  artifact thread on the pinned set — the contract's core claim is that a certified component is
  not evidence the untested composition works (`contract:22`, proof standard `contract:321`).
  Coordinate: one sealed thread `generate → seal → trusted-load → evaluate → persist → query`,
  on live A / live B / relocated, at the pinned set.
- **rerun** — the case is **codegen-internal** (authoring-validation halt, lowering, graph,
  extension, catalog, generation-plan, seal preflight/provenance, name-safety, byte/portability
  checks, structural code audit, test-infra) and its last certification is at a codegen commit
  **before `7526665`**. The execution stage re-observes it on `7526665` with its own fixture.
- **inherit** — reserved for a case whose **entire surface is frozen at the pinned set and was
  certified there**, verified by `git log -- <surface> <audit_rev>..7526665` returning empty.
  **Result: zero cases inherit.** The only pin-resident item is Item 12, whose determinations
  (resume/query identity, row 35) are query-runtime and therefore compose. Every other surface
  is at a superseded codegen rev. Populating "inherit" with anything here would count
  stale-revision evidence, which the brief forbids. This is the honest, conservative outcome.

**Tally: inherit 0 · rerun 22 · compose 19 · total 41.**

---

## LC-I09 semantic coordinate fields (per case)

Beyond the global revision/lock/open-predecessor/non-certifying coordinate above, each case
records the varying semantic fields (companion spec `spec.md:420`):
**owner kind · source form · source-originated polarity · anonymity · actual presence/source ·
occurrence/override shape · both public routes (live + relocated) · sealed artifact-identity
thread.** The blocks below give these per case, plus the primary fixture, the certifying audit
(for context), the classification, and the execution action.

---

## Master classification table

| # | Case (Appendix C) | Owning row/item | Class | Primary fixture |
|---:|---|---|---|---|
| 1 | Zero constraint usages | 13 / Item 11 | compose | constraint-free package (regen at `7526665`) |
| 2 | Excluded-only usages | 13 / Item 11 | compose | excluded-only (`constraint_non_numerical`, `constraint_blocked_*`) |
| 3 | ADMIT + NON_NUMERICAL + BLOCK mix | 4 / Item 4 | rerun | `constraint_malformed_mixed` + `constraint_blocked_profile` + `constraint_non_numerical` |
| 4 | Positive/negated × inline/definition-typed | 1 / Item 1 | compose | `constraint_inline` + definition-typed + live `assert not` |
| 5 | Shared definition × mixed polarity | 1 / Item 1 | compose | shared-def mixed-polarity (author if absent) |
| 6 | One definition × multiple occurrences | 1 / Item 1 | compose | `constraint_multi_instance` |
| 7 | Per-occurrence distinct overrides | 1 / Item 1 | compose | `constraint_occurrence_demand/overrides` |
| 8 | Anonymous admitted + anonymous excluded | 1 / Item 1 | rerun | `constraint_occurrence_demand/anonymous` + `anonymous_return` |
| 9 | Anonymous admitted with actual × snapshot | 1,5 / Items 1,5 | rerun | `constraint_occurrence_demand/anonymous` (relocated) |
| 10 | Shared calc/constraint demand across files | 1,2 / Items 1,2 | rerun | `constraint_occurrence_demand/shared` |
| 11 | Recursive containment | 1 / Item 1 | rerun | `constraint_occurrence_demand/cycle` + `cycle_indirect` |
| 12 | Non-finite multiplicity | 1 / Item 1 | rerun | `non_finite_literal` |
| 13 | Producer-channel actual | 1,2 / Items 1,2 | rerun | `constraint_occurrence_demand/constraint_only` |
| 14 | Literal design-attribute actual (D-2) | 2 / Item 2 | rerun | `gate_a` + `gate_a_package_owner` |
| 15 | Modeled-default formal | 2,4 / Items 2,4 | compose | `modeled_default_fidelity` |
| 16 | Ambiguous/defaulted producer resolution | 12/2,10 | rerun | `two_same_leaf_producers` + `sibling_channel_ambiguity` |
| 17 | Signed/unit default + unsupported wrapper | 4 / Item 4 | rerun | `modeled_default_fidelity` + unsupported-wrapper |
| 18 | Definition-owned assert through redefining usage | 2 / Item 2 | compose | definition-owned redefining (author if absent) |
| 19 | Pre-existing V11 + unrelated constraint | 3 / Item 3 | rerun | Item 3 gate-b fixture |
| 20 | Potential extension-introduced V11 (Item 3B) | 3 / Item 3 | rerun | Item 3 gate-b decision + 2 kept test files |
| 21 | Relocated snapshot | 5 / Item 5 | rerun | `ife_plant` + `constraint_multi_instance` snapshots (full-tree) |
| 22 | Malformed snapshot sections | 5 / Item 5 | rerun | malformed-section snapshot fixtures |
| 23 | Reserved/model/generated name collisions | 8/gen | rerun | name-collision fixture |
| 24 | Missing catalog with constraint modules | 8/gen | rerun | missing-catalog negative fixture |
| 25 | Catalog/profile/runtime schema skew | 8,7 / Items 8,7 | compose | schema-skew fixtures (codegen+companion+runtime) |
| 26 | Generation-plan nested mutation | 8/gen | rerun | `constraint_plan` preflight fixture |
| 27 | Out-of-root warning then BLOCK | 4,5 / Items 4,5 | rerun | out-of-root warning fixture |
| 28 | Mixed satisfied/violated/indeterminate population | 11 / Item 11 | compose | multi-verdict population fixture |
| 29 | Four exceptional-arithmetic shapes | 11 / Item 11 | compose | Item 11 arithmetic fixtures (4 shapes) |
| 30 | Successful/violated/indeterminate file-backed reports | 15 / Item 11 | compose | Item 11 file-backed report fixtures |
| 31 | Trusted verifier bootstrap | 8 / Item 7 | compose | Item 7 verifier-bypass + skew fixtures |
| 32 | Seal/verify symlink and provenance | 9 / Item 7 | rerun | Item 7 seal/symlink/provenance fixtures |
| 33 | Nested evidence mutation attempt | 14 / Item 11 | compose | Item 11 evidence-immutability fixture |
| 34 | Canonical embedded catalog + multi-entry package (D-3) | 10,11 / Items 8,9 | compose | Item 9 multi-entry + Item 8 embedded catalog |
| 35 | Resume/query across incompatible fingerprints | 16 / Item 12 | compose | Item 12 identity/fingerprint fixtures |
| 36 | Zero-entry and excluded-only entry-channel shapes | 11 / Item 9 | compose | Item 9 bridge zero/one/multiple channel fixtures |
| 37 | Fact-consumer mutation | 13 / Items 2,4 | rerun | fact-consumer behavioral tests |
| 38 | Remediation simplification | all / Items 1–12 | rerun | structural sweep (no fixture) |
| 39 | Invalid explicit simkit path (test infra) | 7 / Item 6 | rerun | Item 6 simkit-path test helper |
| 40 | IFE grid | 12 / Item 10 | compose | `fusion_tea` / `ife_plant`; fusion-tea `2422e715` |
| 41 | Stellarator design point (D-1/D-2) | 12 / Item 10 | compose | stellarator `c4dcdf27`/`c2f10960`/`342cc799`; WI-027 |

("Owning row" = Appendix E remediation register row; "Item" = lifecycle item. Fixtures naming
`author if absent` must be authored at execution as public-seam fixtures — a hand-authored
*contract/catalog* fixture is non-certifying, but a public SysML source fixture is the normal input.)

---

## Per-case evidence coordinates

Format per case: **owner kind · source form · polarity · anonymity · actual · occurrence ·
routes · artifact thread · action.** Global coordinate (revisions/locks/open-predecessor=NONE/
non-certifying list) applies to all and is not repeated.

### 1. Zero constraint usages — **compose**
- owner: n/a (no constraint usages) · source: none · polarity: none · anonymity: n/a · actual: none · occurrence: none.
- routes: live A, live B, relocated — all must yield byte-identical constraint-free generation (no constraint catalog/modules; bytes unchanged vs baseline).
- artifact thread: sealed constraint-free package loads/evaluates in TEAx through **both** prepared and file-backed evaluators with **empty constraint evidence** (invariant 46a; no `KeyError`).
- action: regen constraint-free fixture at `7526665`; run both evaluators on the sealed package; byte-diff generation. Cross-ref full-tree byte check §Byte-checks.

### 2. Excluded-only usages — **compose**
- owner: PartUsage(s) · source: inline/definition · polarity: n/a (excluded) · anonymity: named + anonymous · actual: none demanded · occurrence: single.
- routes: live + relocated: portable exclusions; no silent omission; catalog retains one visible `not_assessed` disposition per usage.
- artifact thread: sealed package evaluates in TEAx to a `not_assessed` report surface via the zero-input aggregator (invariant 32).
- action: regen excluded-only fixture at pin; assert exclusion portability + `not_assessed` report through the sealed thread.

### 3. ADMIT + NON_NUMERICAL + BLOCK mix — **rerun**
- owner: PartUsage · source: inline (three siblings) · polarity: positive · anonymity: named · actual: as modeled · occurrence: single.
- routes: live + relocated. Codegen-only: warnings render in order, then **one halt before any target mutation**; **no compiler call**.
- artifact thread: none (halts pre-generation).
- action: re-observe halt-before-mutation at `7526665`. Negative mutation N1 (BLOCK boundary).

### 4. Positive/negated × inline/definition-typed — **compose**
- owner: PartUsage · source: inline **and** definition-typed; includes live `assert not constraint` · polarity: positive **and** negated (source-originated) · anonymity: named · actual: present · occurrence: single.
- routes: live (public CLI, incl. `assert not`) + relocated.
- artifact thread: selected positive-predicate bytes unchanged facts→compiler (invariant 5); evaluation yields **complementary truth/status/margin** with polarity applied exactly once (invariant 6).
- action: sealed-thread evaluate; assert IR/raw-value preservation and complementary verdict/margin sign per form.

### 5. Shared definition × mixed polarity — **compose**
- owner: PartUsage(s) sharing one definition · source: definition-typed · polarity: mixed positive/negated per usage · anonymity: named · actual: present · occurrence: multiple usages.
- routes: live + relocated.
- artifact thread: **one** neutral compiled predicate body; each usage retains its own polarity and **margin sign independent of catalog sort order** (invariant 29) — verify margin sign is not taken from whichever entry sorts first.
- action: author shared-def mixed-polarity fixture if absent; sealed-thread evaluate both usages.

### 6. One definition × multiple occurrences — **compose**
- owner: PartUsage with finite multiplicity · source: definition-typed · polarity: positive · anonymity: named · actual: present · occurrence: **multiple finite**.
- routes: live + relocated.
- artifact thread: distinct execution IDs / modules / result channels per occurrence (invariant 17); a legitimate shared producer is **recorded** in the catalog, not silently collapsed.
- action: `constraint_multi_instance` at pin; sealed-thread evaluate; assert distinct results + recorded sharing.

### 7. Per-occurrence distinct overrides — **compose**
- owner: PartUsage · source: definition-typed · polarity: positive · anonymity: named · actual: **per-occurrence override** · occurrence: multiple with distinct actuals.
- routes: live + relocated.
- artifact thread: every occurrence resolves its own value → **distinct verdict**; no collapse is observationally hidden.
- action: `constraint_occurrence_demand/overrides` at pin; sealed-thread evaluate; assert distinct verdicts.

### 8. Anonymous admitted + anonymous excluded — **rerun**
- owner: PartUsage · source: inline · polarity: positive/none · anonymity: **anonymous** (both dispositions) · actual: none spurious · occurrence: single.
- routes: live + relocated (catalog/disposition level; no runtime verdict required).
- artifact thread: both dispositions visible in catalog; **no spurious actual demand**.
- action: `constraint_occurrence_demand/anonymous` + `anonymous_return` at pin; re-observe catalog dispositions.

### 9. Anonymous admitted with actual × snapshot — **rerun**
- owner: PartUsage · source: inline · polarity: positive · anonymity: **anonymous with actual** · actual: present (nullable-QN risk) · occurrence: single.
- routes: **public live AND relocated replay** both lower the actual with **no nullable-QN crash or identity drift** (route named in title pins the historically-failing snapshot coordinate).
- artifact thread: lowering only; identity stable across routes.
- action: relocate the anonymous fixture to a second root; re-observe lowering on both routes at pin.

### 10. Shared calc/constraint demand across files — **rerun**
- owner: PartUsage across files · source: mixed · polarity: positive · anonymity: named · actual: producer-channel · occurrence: single.
- routes: live + relocated.
- artifact thread: graph-level — one **intended** producer retained; exact parameter group survives deterministically with **no overwrite** (invariant 19–20).
- action: `constraint_occurrence_demand/shared` (constraint_route + calc_route) at pin; re-observe producer retention + param-group survival.

### 11. Recursive containment — **rerun**
- owner: PartUsage (recursive owner) · source: definition-typed · polarity: positive · anonymity: named · actual: n/a · occurrence: **recursive**.
- routes: live + relocated (codegen halt).
- artifact thread: none — **named cycle error with full owner path**; no partial instance index (invariant 18).
- action: `constraint_occurrence_demand/cycle` + `cycle_indirect` at pin. Negative mutation N2 (occurrence-expansion boundary).

### 12. Non-finite multiplicity — **rerun**
- owner: PartUsage · source: definition-typed · polarity: positive · anonymity: named · actual: n/a · occurrence: **non-finite**.
- routes: live + relocated (codegen halt).
- artifact thread: none — **named cardinality error**; no partial occurrence expansion.
- action: `non_finite_literal` at pin. Negative mutation N3 (cardinality boundary).

### 13. Producer-channel actual — **rerun**
- owner: PartUsage · source: definition-typed · polarity: positive · anonymity: named · actual: **producer channel** · occurrence: single.
- routes: live + relocated.
- artifact thread: graph — producer retained through the constraint root **before live pruning** (invariant 23).
- action: `constraint_occurrence_demand/constraint_only` at pin; re-observe root retention pre-prune.

### 14. Literal design-attribute actual (D-2) — **rerun**
- owner: **concrete PartUsage owning the attribute** · source: definition-typed · polarity: positive · anonymity: named · actual: **direct literal design attribute, self-named** · occurrence: single.
- routes: live + relocated.
- artifact thread: direct resolution under **real QN** via the shared producer/exact-QN path, reusing the QN-keyed typed entry point; **no passthrough calculation** (D-2, invariant 21).
- action: `gate_a` + `gate_a_package_owner` at pin; re-observe direct resolution. Also exercised in stellarator (case 41) — the isolated cell still runs on its own fixture.

### 15. Modeled-default formal — **compose**
- owner: PartUsage · source: definition-typed · polarity: positive · anonymity: named · actual: **omitted formal → modeled default**, plus an override variant · occurrence: single.
- routes: live + relocated.
- artifact thread: default applies; **override changes verdict** (invariant 19, 22) — verdict requires the sealed runtime thread.
- action: `modeled_default_fidelity` at pin; sealed-thread evaluate default and override; assert verdict change.

### 16. Ambiguous/defaulted producer resolution — **rerun**
- owner: PartUsage · source: definition-typed · polarity: positive · anonymity: named · actual: **two same-leaf candidate design attributes + defaulted-fallback shape** · occurrence: single.
- routes: live + relocated.
- artifact thread: **fails generation with a named ambiguity/producer error, OR resolves only under exact QN** — **no verdict from a guessed/defaulted binding while V11 is clean** (invariant 26). This is the cell that proves producer-completeness independently of V11.
- action: `two_same_leaf_producers` + `sibling_channel_ambiguity` at pin. Negative mutation N4 (producer-completeness boundary).

### 17. Signed/unit default + unsupported wrapper — **rerun**
- owner: PartUsage · source: definition-typed · polarity: positive · anonymity: named · actual: **`-0.1` signed default, `[MW]` unit default; unsupported wrapper present** · occurrence: single.
- routes: live + relocated.
- artifact thread: lowering — explicit `-0.1` and `[MW]` survive verbatim; the **unsupported wrapper never invents a value** (invariant 4, 20; Item 4 default fidelity).
- action: `modeled_default_fidelity` + unsupported-wrapper fixture at pin; re-observe default survival + wrapper exclusion.

### 18. Definition-owned assert through redefining usage — **compose**
- owner: **definition owns the assert; redefining usage** · source: definition-typed · polarity: positive · anonymity: named · actual: redefined via usage · occurrence: single.
- routes: live + relocated.
- artifact thread: definition source and redefining occurrence/actual identity remain **distinct** (invariant 27) and produce the **expected verdict**.
- action: author definition-owned-redefining fixture if absent; sealed-thread evaluate; assert identity distinctness + verdict.

### 19. Pre-existing V11 + unrelated constraint — **rerun**
- owner: PartUsage · source: definition-typed · polarity: positive · anonymity: named · actual: present · occurrence: single; **a pre-existing V11 uncovered input unrelated to the constraint**.
- routes: live + relocated.
- artifact thread: extension **succeeds** (does not reject the unrelated pre-existing offender, invariant 24); **final generation remains strict** (zero whole-graph V11 uncovered → this model still fails final generation on the unrelated offender, invariant 26).
- action: Item 3 gate-b fixture at pin; re-observe extension-success + final-generation strictness.

### 20. Potential extension-introduced V11 (Item 3B) — **rerun**
- owner: n/a (structural) · source: n/a · polarity: n/a · anonymity: n/a · actual: n/a · occurrence: n/a.
- routes: codegen structural. **Item 3 determination: vacuity proven — extension cannot introduce a new V11 uncovered input; the extension-time differential-check call was deleted** (gate-b audit: "Complete — vacuity proven, delete branch executed"; no replacement wrapper/differential/flag).
- artifact thread: none.
- action: re-confirm at `7526665` that the deleted check is **still absent** (grep + the 2 kept gate-b test files pass); restoring the 3 deleted lines must flip **5 of 14** kept tests red (the deletion-persistence negative, mutation N15). If any extension-created-V11 shape is discovered, it is a **finding returned to Item 3**, not fixed here.

### 21. Relocated snapshot — **rerun**
- owner: multiple · source: mixed · polarity: mixed · anonymity: mixed · actual: mixed · occurrence: mixed.
- routes: **relocated replay** vs live must agree on decisions, diagnostics, retained producers, graph/catalog values, fingerprints, and the **full generated tree bytes**; **no checkout-absolute bytes anywhere** (invariants 34, 35).
- artifact thread: pre-runtime byte parity.
- action: full-tree byte parity `ife_plant` + `constraint_multi_instance` snapshots relocated to a second checkout root; absolute-path scan over the entire tree. Cross-ref §Byte-checks. Note `captured_at` churn on re-capture (memory `byte-identity-captured-at-churn`): run the timestamp-only diff + revert protocol so only genuine drift shows.

### 22. Malformed snapshot sections — **rerun**
- owner: n/a · source: n/a · polarity: n/a · anonymity: n/a · actual: n/a · occurrence: n/a.
- routes: relocated (each malformed required shape).
- artifact thread: each malformed section **fails before reconstruction** with section/field context and recapture guidance.
- action: malformed-section snapshot fixtures at pin. Negative mutation N5 (snapshot-reconstruction boundary).

### 23. Reserved/model/generated name collisions — **rerun**
- owner: n/a · source: model with colliding names · occurrence: n/a.
- routes: live + relocated.
- artifact thread: **deterministic pre-output failure; target untouched** (invariant 30).
- action: name-collision fixture (reserved, model, generated scopes) at pin. Negative mutation N6 (name-safety boundary, pre-output).

### 24. Missing catalog with constraint modules — **rerun**
- owner: n/a · source: constraint model · occurrence: n/a.
- routes: live + relocated.
- artifact thread: **named pre-output failure; no renderer/writer/orchestration mutation** (invariant 26, 31).
- action: missing-catalog negative fixture at pin. Negative mutation N7 (catalog-coverage boundary, pre-output).

### 25. Catalog/profile/runtime schema skew — **compose**
- owner: n/a (cross-repo version axis) · source: n/a · occurrence: n/a.
- routes: n/a — spans codegen catalog, companion profile, and TEAx runtime-contract versions.
- artifact thread: **older/newer combinations fail closed in both directions before semantic use** (invariants 14, 39, 50).
- action: build skew fixtures across the pinned triple; assert both-direction fail-closed before package code runs. Negative mutation N8 (version-skew boundary).

### 26. Generation-plan nested mutation — **rerun**
- owner: n/a · source: n/a · occurrence: n/a.
- routes: live + relocated.
- artifact thread: **written semantic contents equal the preflight-validated plan** (invariant 31); writers do not change semantic contents.
- action: `constraint_plan` preflight fixture at pin; assert written == validated plan.

### 27. Out-of-root warning then BLOCK — **rerun**
- owner: PartUsage out of root · source: inline · polarity: positive · anonymity: named · actual: present · occurrence: single.
- routes: live + relocated.
- artifact thread: portable **out-of-root warning renders and does not mask the later BLOCK halt** (invariants 15, 34).
- action: out-of-root warning fixture at pin; assert warning portability + non-masking of halt.

### 28. Mixed satisfied/violated/indeterminate population — **compose**
- owner: PartUsage(s) · source: mixed · polarity: mixed · anonymity: named · actual: present · occurrence: multiple.
- routes: live + relocated.
- artifact thread: headline precedence **violation → indeterminate → satisfied → not assessed** (invariant 33) with **every ordinary output retained** (invariant 42).
- action: multi-verdict population fixture at pin; sealed-thread evaluate; assert headline precedence + output retention.

### 29. Four exceptional-arithmetic shapes — **compose**
- owner: PartUsage · source: inline · polarity: positive · anonymity: named · actual: present · occurrence: single (four arithmetic shapes).
- routes: live + relocated.
- artifact thread: **both evaluators agree on phase/module/cause and complete report content** — not merely one shared failure wrapper — with the **expected phase per shape pinned by the fixture**, not established by mutual agreement (invariants 44, 45).
- action: Item 11 four arithmetic fixtures at pin; run prepared + file-backed; assert per-shape phase from fixture. Exec env per memory `teax-simkit-execution-env` (agentic-mbse venv + sys.path insert; not teax `.venv`).

### 30. Successful/violated/indeterminate file-backed reports — **compose**
- owner: PartUsage · source: inline · polarity: mixed · anonymity: named · actual: present · occurrence: single (three statuses).
- routes: file-backed public route.
- artifact thread: **verified identity, exact JSON persistence, routing, and harvest with no consumer schema adapter** for every completed status (invariant 46).
- action: Item 11 file-backed fixtures at pin; persist + harvest all three statuses; assert exact JSON + package identity, no adapter.

### 31. Trusted verifier bootstrap — **compose**
- owner: n/a · source: n/a · occurrence: n/a.
- routes: runtime load.
- artifact thread: a verifier **modified to return unconditional success is rejected before any package code runs**; **verifier-version skew also fails closed** (invariant 39).
- action: Item 7 verifier-bypass + version-skew fixtures at pin. Negative mutation N9 (trusted-bootstrap boundary, before package execution).

### 32. Seal/verify symlink and provenance — **rerun**
- owner: n/a · source: n/a · occurrence: n/a.
- routes: codegen seal (both).
- artifact thread: **every forbidden link fails symmetrically**; adding a foreign file then re-sealing **cannot make it codegen-originated** (invariant 37).
- action: Item 7 seal/symlink/provenance fixtures at pin. Negative mutation N10 (seal-provenance boundary).

### 33. Nested evidence mutation attempt — **compose**
- owner: PartUsage · source: inline · polarity: positive · anonymity: named · actual: present · occurrence: single.
- routes: runtime + persistence.
- artifact thread: mutation of generated report/results/status/margin/observations **cannot change authoritative or persisted evidence** (invariants 41, 49) — enforce by deep freeze / defensive isolation.
- action: Item 11 evidence-immutability fixture at pin; attempt nested mutation; assert authoritative + persisted evidence unchanged. Negative mutation N11 (evidence-immutability boundary).

### 34. Canonical embedded catalog + multi-entry package (D-3) — **compose**
- owner: PartUsage(s), multi-entry · source: definition-typed · polarity: positive · anonymity: named · actual: multiple typed entries · occurrence: multiple.
- routes: live + relocated.
- artifact thread: **stock codegen/TEAx path — no alternate catalog schema, materializer, or wrapper** (D-3, invariants 28, 48). TEAx consumes the embedded model-contract catalog directly.
- action: Item 9 multi-entry + Item 8 embedded-catalog fixtures at pin; sealed-thread evaluate through stock seams; assert no alternate schema/materializer/wrapper is touched.

### 35. Resume/query across incompatible fingerprints — **compose**
- owner: n/a · source: n/a · occurrence: n/a.
- routes: study/query runtime.
- artifact thread: executable or semantic/catalog mismatch **rejects resume/query or starts an explicit new lineage; no silent reassignment** (invariant 50). (Item 12 is the only pin-resident item, but this is a query-runtime observation on the sealed thread → compose, not inherit.)
- action: Item 12 identity/fingerprint fixtures at pin; attempt resume/query across mismatched fingerprints. Negative mutation N12 (identity-rebind boundary).

### 36. Zero-entry and excluded-only entry-channel shapes — **compose**
- owner: PartUsage(s) · source: mixed · polarity: mixed · anonymity: named · actual: **zero / one / multiple typed channel mappings** · occurrence: mixed.
- routes: study bridge runtime.
- artifact thread: zero/one/multiple typed channel mappings **validate completely**; **excluded-only constraints do not invent inputs** (invariant 47).
- action: Item 9 bridge fixtures (zero/one/multiple) at pin; run study bridge; assert complete channel supply + no invented inputs.

### 37. Fact-consumer mutation — **rerun**
- owner: n/a · source: n/a · occurrence: n/a.
- routes: codegen/agentic-mbse behavioral tests.
- artifact thread: **removing or changing each load-bearing fact consumer fails a behavioral test; a static consumer-map edit cannot satisfy it** (invariant 13).
- action: fact-consumer behavioral tests at pin (codegen `7526665` + agentic-mbse `4c18d61`). Negative mutation N13 (fact-consumer boundary).

### 38. Remediation simplification — **rerun**
- owner: n/a (structural code audit) · source: n/a · occurrence: n/a.
- routes: structural sweep across all repos at the pinned set.
- artifact thread: named superseded mechanisms are **removed, not shimmed**; **no duplicate authority or parallel route remains** (LC-I08; line counts are not proof — memory `loc-gates-retired`). Named targets to confirm deleted: three resolution ladders (Item 2), fusion catalog materializer + alternate TEAx catalog schema + QN/predicate-text reconstruction (Item 8, D-3), WI-027 D7 passthroughs (Item 10, D-2), grandfather skip-lowering + dead `tracking_key` (Item 12), Gate B extension-time check (Item 3).
- action: structural sweep at pin; confirm each named path absent with no replacement shim/authority.

### 39. Invalid explicit simkit path (test infrastructure) — **rerun**
- owner: n/a · source: n/a · occurrence: n/a.
- routes: codegen test infra.
- artifact thread: the codegen test helper **fails rather than falling through to sibling discovery** (Item 6/F1 scope).
- action: Item 6 simkit-path helper test at pin. Negative mutation N14 (test-infra boundary).

### 40. IFE grid — **compose**
- owner: plant PartUsages · source: definition-typed · polarity: positive · anonymity: named · actual: producer + design attributes · occurrence: multiple; modeled `>=`.
- routes: live + relocated on the FINAL set through **stock seams**.
- artifact thread: exact final candidates, **2,301 points**, modeled `>=`, **unchanged anchors**; sealed IFE package through generate→seal→load→evaluate→persist. No private adapter (the historical 2,294+7-via-adapter evidence is non-certifying).
- action: `fusion_tea`/`ife_plant` at fusion-tea `2422e715` + pinned codegen/teax; run 2,301-point acceptance through stock seams; assert unchanged anchors. Cross-ref memory `item3-fusiontea-acceptance-facts` (2,301, per-consumer gain key, abs-path parity gotcha).

### 41. Stellarator design point (D-1/D-2) — **compose**
- owner: five constraint PartUsages, multi-entry · source: definition-typed · polarity: mixed · anonymity: named · actual: producers + direct literal design attributes (D-2) · occurrence: multiple.
- routes: live + relocated on the FINAL set.
- artifact thread: **fully representable graph** (every modeled/computed dependency has a graph producer; ordinary design inputs enter only through the generated typed input boundary), **WI-027 D7 passthroughs removed**, **no post-build mutation / private bridge / placeholder / alternate catalog / consumer wrapper**, **five verdicts**, **unchanged numerics**, **handwritten code sealed** (D-1, D-2).
- action: stellarator `c4dcdf27`+`c2f10960`+`342cc799` + pinned codegen/teax; sealed-thread run; assert five verdicts + unchanged numerics + WI-027 D7 removal. WI-027 design must point to the contract (D-2) before acceptance.

---

## Negative mutations manifest (each must fail at its intended boundary, before a later failure can mask it)

| ID | Case | Mutation | Intended failure boundary |
|---|---:|---|---|
| N1 | 3 | Model asserts a BLOCK usage among ADMIT/NON_NUMERICAL siblings | Named model halt before any target mutation; no compiler call |
| N2 | 11 | Recursive containment owner | Named cycle error with full owner path; no partial index |
| N3 | 12 | Non-finite multiplicity | Named cardinality error; no partial occurrence expansion |
| N4 | 16 | Two same-leaf design attributes + defaulted fallback | Named ambiguity/producer error at generation while V11 clean; no guessed verdict |
| N5 | 22 | Each malformed required snapshot section | Fails before reconstruction with section/field context |
| N6 | 23 | Reserved/model/generated name collision | Deterministic pre-output failure; target untouched |
| N7 | 24 | Constraint modules with missing catalog | Named pre-output failure; no renderer/writer mutation |
| N8 | 25 | Older/newer catalog·profile·runtime schema | Fail closed both directions before semantic use |
| N9 | 31 | Verifier patched to return unconditional success; verifier-version skew | Rejected before any package code runs |
| N10 | 32 | Forbidden symlink; foreign file added then re-sealed | Symmetric link failure; foreign file cannot become codegen-originated |
| N11 | 33 | Mutate nested report/results/status/margin/observations | Authoritative + persisted evidence unchanged |
| N12 | 35 | Resume/query across incompatible executable or semantic/catalog fingerprint | Reject or start explicit new lineage; no silent reassignment |
| N13 | 37 | Remove/change each load-bearing fact consumer | Behavioral test fails; static map edit cannot satisfy |
| N14 | 39 | Invalid explicit simkit path | Test helper fails; no fall-through to sibling discovery |
| N15 | 20 | Restore the 3 deleted Gate B extension-check lines | 5 of 14 kept gate-b tests flip red (deletion-persistence proof) |
| N16 | (inv. 53) | Grandfathered skip-lowering snapshot on the normal product path | Fails closed at generate; legacy inspection is non-executable/non-certifying |

N16 covers invariant 53 (superseded Item 12 behavior); it is not an Appendix C row but the brief
requires the composed run to still exercise inherited superseded-item behavior.

---

## Full-tree byte checks

1. **Live A vs Live B** — two independent checkout roots, identical generated-tree bytes (forbids same-machine path cancellation; proof standard).
2. **Live vs relocated snapshot** — full generated tree byte-identical (case 21, invariant 35).
3. **Absolute-path scan** — the entire generated tree (IDs, fingerprints, contracts, generated code, docstrings, reports, catalogs, reconstructed snapshot fields) contains **no checkout-absolute path** (invariant 34, Item 5). Note: live `--models` module-docstring byte parity was only indirectly pinned in Item 5 (its N1) — the composed run must pin it directly on the licensed live route.
4. **Constraint-free byte stability** — case 1 generation bytes unchanged vs baseline.
5. **IFE unchanged anchors** — case 40.
6. **Stellarator unchanged numerics** — case 41.

Protocol notes (memory): generated baselines/fixtures are **format-exempt** (`generated-baselines-format-exempt`) — never ruff-format them; a full re-capture rewrites every `captured_at` (`byte-identity-captured-at-churn`) — run the timestamp-only diff + revert so only genuine drift surfaces.

## Final repository quality gates (Item 13 scope 5)

| Gate | At pin | Baseline / note |
|---|---|---|
| Focused suite (constraint lifecycle) | codegen `7526665` | green |
| Optimized suite (`PYTHONOPTIMIZE=1`) | codegen `7526665` | **2 pre-existing failures** are the accepted baseline (Item 4: "2 failed, 3038 passed, exactly the two named") — record, do not treat as regression |
| Full licensed suite | codegen `7526665` | Item 12 baseline "3115 passed, 47 skipped"; re-run at pin. License via `SYSIDE_LICENSE_KEY` in `~/1cfe/agentic-mbse/.env` — `set -a; source` it (memory `syside-license-key-explicit-env-needed`), else a fake 23F/96E baseline |
| Lint (ruff check) | all repos | baseline clean |
| Format (ruff format) | src only | **exempt** generated baselines/fixtures/`baseline_outputs` |
| Type (mypy) | src | baseline clean |
| Fixture diff review | all | review generated-tree diffs; expect only the new Item-13 fixtures + `captured_at` churn |
| agentic-mbse suite | `4c18d61` | companion profile/skew gates |
| teax suite | `c342b10` | exec env per memory `teax-simkit-execution-env` (agentic-mbse venv + sys.path insert; teax push via HTTPS) |
| fusion-tea consumer | `2422e715` | IFE acceptance |
| stellarator consumer | `c4dcdf27`/`c2f10960`/`342cc799` | five-constraint acceptance |

---

## Completeness attestation (this manifest's own bar)

- **41 / 41** Appendix C cases enumerated (rows 1–41 above map 1:1 to Appendix C top-to-bottom).
- **Classification:** inherit 0 · rerun 22 · compose 19 = 41. Zero inherits is the conservative
  result of the strict rule (every non-Item-12 surface is at a superseded codegen rev; Item 12's
  surface is query-runtime → compose). Any inherit added later must carry a passing
  `git log -- <surface> <audit_rev>..7526665` freeze check.
- **Open predecessors:** NONE (rows 0–16 certified). This is a precondition for row 17; if any
  reopens, row 17 cannot certify until it re-closes.
- **16 negative mutations** manifested (N1–N16), each bound to its case and failure boundary.
- **6 full-tree byte checks** and the **final quality-gate matrix** manifested.
- **Discipline:** no failure found downstream is fixed in Item 13 — it returns to its owning row.
  No private-seam substitute, filtered-offender, hand-authored contract/catalog fixture, or
  same-machine cancellation counts. Fixtures marked "author if absent" (cases 5, 18) must be
  public SysML source fixtures, not hand-authored contract/catalog fixtures.

**Next stage:** `/_my_plan` — sequence the 22 reruns + 19 composes + 16 mutations + byte/quality
gates into the execution order, then execute and produce `release-readiness.md`.

---

## Stage 2 execution — RERUN results (2026-07-20)

**Status:** 22 / 22 reruns executed and recorded · **PASS 22 · findings 0 · unexpected skips 0**.
Compose group and negative-mutation group **not** started (stage stops before compose, per brief).

### Environment (as-run)

- **Codegen surface = pin `7526665` exactly.** HEAD is `0921e05` (Item 12 audit + Item 13
  manifest docs). `git diff 7526665 HEAD -- src tests` is **empty** (0 lines) — every change
  since the pin is under `.project/` only. Every rerun below therefore observes the pinned
  codegen surface. (Confirmed: full diff touches only `CURRENT_WORK.md`, the two Item-13 briefs,
  the Item-12 audit, `BACKLOG.md`, and the epic doc.)
- **agentic-mbse** at `4c18d61` (matches pin; only untracked `.orchestrate-logs/`).
- **License** loaded from `~/1cfe/agentic-mbse/.env` (`set -a; source`), key length 37.
- **Frozen version re-assertion** (register's requirement, versions read from Item 0
  `constraint-lifecycle-candidate-pin/evidence.md`):
  `uv run --frozen python -c "import importlib.metadata as m; ..."` →
  **sysml-codegen `0.1.0`**, **agentic-mbse `0.1.2`**, imports OK. Matches Item 0
  (agentic-mbse `0.1.2` / `executable-profile/v4`; sysml-codegen `0.1.0` requires
  `agentic-mbse>=0.1.2`).
- Command shape per case (codegen root unless noted):
  `set -a; source ~/1cfe/agentic-mbse/.env; set +a && uv run --frozen pytest <selection> -rs -q`.
  `-rs` surfaced **no** skip lines in any run (all summaries pure "N passed"). Selections chosen
  as the conformance/unit test(s) that exercise each case's named fixture(s).

### Per-case rerun scoreboard

| # | Case | pytest selection | Result |
|---:|---|---|---|
| 3 | ADMIT+NON_NUMERICAL+BLOCK mix | `tests/conformance/test_constraint_non_numerical.py` | **4 passed** |
| 8 | Anonymous admitted + excluded | `tests/conformance/test_return_style_extraction.py tests/conformance/test_constraint_occurrence_demand_acceptance.py` | **17 passed** |
| 9 | Anonymous admitted w/ actual × snapshot | `tests/conformance/test_constraint_snapshot_portability.py` | **3 passed** |
| 10 | Shared calc/constraint demand across files | `tests/conformance/test_shared_producer_convergence.py` | **2 passed** |
| 11 | Recursive containment | `tests/conformance/test_constraint_occurrence_demand_supplementary.py tests/conformance/test_part_instance_index.py` | **12 passed** |
| 12 | Non-finite multiplicity | `tests/conformance/test_diagnostic_screen.py` | **8 passed** |
| 13 | Producer-channel actual | `tests/conformance/test_constraint_occurrence_demand_acceptance.py tests/unit/test_logical_demand_resolution.py` | **21 passed** |
| 14 | Literal design-attribute actual (D-2) | `tests/conformance/test_gate_a_owner_classification.py` | **4 passed** (exec leg `tests/execution/test_gate_a_execution.py` = 1 deselected by marker — runtime, belongs to compose) |
| 16 | Ambiguous/defaulted producer resolution | `tests/conformance/test_producer_completeness_acceptance.py tests/conformance/test_sibling_channel_ambiguity.py` | **6 passed** |
| 17 | Signed/unit default + unsupported wrapper | `tests/conformance/test_modeled_default_fidelity.py tests/conformance/test_default_lane_disagreement.py` | **10 passed** |
| 19 | Pre-existing V11 + unrelated constraint | `tests/conformance/test_gate_b_generation_gate.py` | **3 passed** |
| 20 | Extension-introduced V11 vacuity (Item 3B) | `tests/unit/test_constraint_graph_extension.py` + grep | **11 passed**; Gate B extension-time differential check **absent** (grep for `differential\|extension.time.*check\|_check_extension` in `src/` returned empty → still deleted). N15 (restore-3-lines flips 5/14) deferred to the mutation group. |
| 21 | Relocated snapshot | `tests/conformance/test_whole_tree_portability.py tests/conformance/test_constraint_snapshot_portability.py` | **5 passed** |
| 22 | Malformed snapshot sections | `tests/unit/test_snapshot_envelope_gate.py tests/conformance/test_snapshot_contract.py` | **344 passed** |
| 23 | Reserved/model/generated name collisions | `tests/unit/test_constraint_name_safety.py tests/conformance/test_constraint_name_safety_routes.py` | **26 passed** |
| 24 | Missing catalog with constraint modules | `tests/conformance/test_module_kind_faildloud.py tests/unit/test_silent_failure_family2.py` | **16 passed** |
| 26 | Generation-plan nested mutation | `tests/conformance/test_constraint_generation_integration.py tests/unit/test_cli_generation.py` | **57 passed** |
| 27 | Out-of-root warning then BLOCK | `tests/conformance/test_constraint_lowering.py tests/unit/test_constraint_usage_preparation.py` | **70 passed** |
| 32 | Seal/verify symlink and provenance | `tests/unit/test_verify_package.py tests/conformance/test_seal_step9.py` | **51 passed** |
| 37 | Fact-consumer mutation | *(agentic-mbse `4c18d61`)* `tests/test_sysml/test_constraint_fact_shapes.py tests/test_sysml/test_constraint_facts_severity.py` | **21 passed** |
| 38 | Remediation simplification (structural sweep) | `tests/conformance/test_dead_code_removal.py tests/conformance/test_catalog_no_reconstruction.py` + structural greps | **6 + 2 passed**; named superseded paths absent in `src/`: `tracking_key` (empty), resolution ladders (empty), WI-027 D7 passthroughs (`passthrough` empty; remaining `D7` hits are current design-decision labels), predicate-text reconstruction (only the "never a predicate-text reconstruction" FK comment). Fusion catalog materializer: no `materializer` symbol; remaining `material*` hits are unrelated (`_occurrence_materialized_qn`, list materialization). |
| 39 | Invalid explicit simkit path (test infra) | `tests/unit/test_teax_discovery.py` | **6 passed** |

**Rerun tally: 22 executed · 22 PASS · 0 findings · 0 unexpected skips.**

Negative mutations referenced by rerun-case actions (N1–N7, N10, N13, N14, N15) are **not**
executed here — the mutation group is a separate manifest deliverable sequenced after the reruns.
Each rerun above re-observed its case's *non-mutated* behavior on the pinned surface.

### "Author if absent" fixtures (cases 5, 18) — authored this session

The brief/task instructed authoring the two "author if absent" public SysML source fixtures.
**Classification note (surfaced):** cases 5 and 18 are **compose**-classified in the master
table, not rerun. This session authored their fixtures only (fixture authoring is compose-prep,
not compose execution); their sealed-thread evaluation stays with the compose group.

- **Case 5** — `tests/fixtures/constraint_shared_polarity/` (model.sysml + PROVENANCE.md). One
  shared `constraint def`, two named usages of opposite polarity (`assert constraint pos_bound`
  + `assert not constraint neg_bound`), actuals from a producer channel. **Validated:**
  `sysml-codegen generate` exits 0 and emits both `...posboundconstraintmodule.py` and
  `...negboundconstraintmodule.py` — a valid public-seam input.
- **Case 18** — `tests/fixtures/constraint_def_owned_redefining/` (model.sysml + PROVENANCE.md).
  Definition-owned assert (typed by a shared constraint def) with the nested actual redefined at
  the usage via `:>> source.reading = 80.0` (the `order`/`overrides` idiom). **Validated:**
  parses; Step 3.5 extracts the redefinition ("1 design overrides"). Full generation **halts**
  at constraint-actual resolution — `panel.v: unresolved actual 'source.reading' (strict mode,
  INV-2, no entry-point synthesis)` — the same class as the sibling `order`/`overrides`
  redefinition probes (both also halt generation; exercised at extraction/acceptance level).

  **SURFACED (capture-fidelity law 4):** case 18's coordinate says the redefining-usage actual
  should resolve and produce the expected verdict. At pin `7526665` a `:>>`-redefined design
  attribute feeding a constraint actual is **not minted as an entry point** and does not resolve
  at generation. Whether that is intended (compose-stage cross-part wiring, Items 9–11) or a
  **finding for Item 2** (case 18's owning row) is for the **compose stage** to decide. Stage 2
  surfaced it; it did **not** touch production code (stage discipline).
