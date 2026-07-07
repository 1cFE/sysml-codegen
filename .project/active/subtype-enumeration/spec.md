# Spec: Subtype-Aware Enumeration & Constraint-Report Truth

**Status:** Draft
**Owner:** Reid W
**Created:** 2026-07-06
**Complexity:** HIGH (cross-repo coordinated pair; snapshot format-version bump; two load-bearing semantic decisions; ~5 CONFIRMED-BLIND sites — the LOC is small but the coordination and truth surface are not)
**Branch:** pipeline-truth-epic (agentic-mbse lands on a companion branch — see Related Artifacts)
**Epic:** PIPELINE-TRUTH, Item 4

---

## Problem

Model-wide enumeration in both repos uses syside's exact-type element query, which never
matches subtypes. The single mechanism (`SysideAdapter.elements_of_type` →
`nodes(kind, include_subtypes=False)`) is blind to every subtype of the type it is asked
for, while `is_instance` on the same adapter *is* hierarchy-aware. That asymmetry produces
diagnostics that cannot fire on the shapes they claim to cover:

- **The constraint drop report is silent for exactly the shape fusion-tea uses.** `assert
  constraint` parses to `AssertConstraintUsage` (a `ConstraintUsage` subtype). The report
  (`extractor.py:108`) queries exact-type `ConstraintUsage`, so it sees zero of them; both
  the per-item INFO loop and the summary WARN gate on a non-empty list (`extractor.py:123`),
  so the report is *completely silent* when a model's only constraints are asserts. The
  orchestrator reproduced this license-free: `ife_plant.sysml:155` yields 0 `ConstraintUsage`,
  1 `AssertConstraintUsage`. Item 1-of-UPSTREAM-FINDINGS' criterion "wi014_toy emits the
  constraint diagnostics" was never true for its `assert constraint` at `toy_plant.sysml:51`.

- **The conformance test that should catch this cannot fail.** `REQ-EXT-09`'s test
  (`tests/conformance/test_extractor.py:894-899`) computes its expected count with the *same query
  the implementation uses* — a tautology structurally unable to detect the blindness. This is the
  canonical instance of the anti-pattern R1 bans; this item re-anchors it.

- **The same pattern breaks an agentic-mbse validator outright.** `level3_dataflow.py:48`
  queries the *abstract* metaclass `Import`. `Import` never instantiates — every import is a
  concrete `MembershipImport` or `NamespaceImport` — so the query matches nothing, the
  dependency graph is always `{}`, and circular-dependency validation *structurally always
  passes* ("Documents analyzed: 0"). It is a validator that cannot fail.

- **Constraints can never be reported from a snapshot.** The drop report runs on the live
  syside model only. It is not invoked on the `generate --from-snapshot` path, and constraint
  data is never serialized: `PartDefinitionData.constraints` is a stub (`extractor.py:159`,
  always `[]`), the serializer writes no constraint fields, and `_deserialize_constraint_info`
  (`loader.py:275`) has zero callers — dead code. A snapshot-first workflow loses constraint
  visibility permanently.

The fix surface is small and singular: syside's `include_subtypes=True` exists and is never
passed. The risk is not the plumbing — it is deciding *what a subtype-aware sweep should
surface at each call site*. Flipping `include_subtypes` globally would, for example, make
`RequirementUsage` (a `ConstraintUsage` subtype) appear in constraint sweeps and count as a
"dropped constraint," which it is not. The decision must be made per call site and recorded,
not defaulted.

## Success Criteria

- [ ] Generating wi014_toy **and** the committed fusion-tea snapshot emits the constraint drop
  report including the assert-shaped constraint at `toy_plant.sysml:51`, with counts anchored
  independently of the production query (hardcoded / fixture-source grep).
  <!-- AUDIT 2026-07-06: wi014 leg MET (committed snapshot manifest + test_snapshot_contract.py:92). fusion-tea leg NOT MET here — no committed fusion-tea snapshot in this repo; depends on Item 2 regen on v2. Left unchecked (conjunction). See audit.md Note 2. -->

- [x] The constraint drop report is available on the `generate --from-snapshot` path (constraints
  serialized into the snapshot and the report replayed), not only on the live path.
  <!-- AUDIT 2026-07-06: verified by artifact — snapshot_context.py:45 replays render; INV-B committed-snapshot test (test_snapshot_contract.py:92) license-free. -->

- [ ] agentic-mbse Level 3 produces a **non-empty** dependency graph on a fixture with imports,
  and a seeded circular-import fixture **FAILS** the circular-dependency check (the first time
  that check can fail).
- [x] `REQ-EXT-09`'s test **fails** when the underlying query is deliberately broken (a mutation
  check documented inside the test), covers both the summary WARN and the per-owner INFO across
  calc-def, part-def, **and part-usage** owners, and asserts the assert-shaped constraint on
  wi014_toy is reported.
  <!-- AUDIT 2026-07-06: verified by source — test_extractor.py:969 mutation check via injectable include_subtypes; independent literal 65; part-usage leg :934. Not executed (sandbox). -->
- [x] `require constraint` is certified reported and pinned permanently (it is a plain
  `ConstraintUsage` under `RequirementConstraintMembership` — already visible; the pin locks
  that in).
  <!-- AUDIT 2026-07-06: verified — item4_require fixture + test_extractor.py:990. -->
- [x] The `EnumerationUsage`-as-attribute decision is recorded and pinned by a test on the
  existing enum-bearing fixtures (whichever way it lands).
  <!-- AUDIT 2026-07-06: verified by code — parameter_groups.py:102 keeps exact-type AttributeUsage (row-3 opt-OUT). Pin test not executed. -->
- [ ] Per-call-site subtype decision table published in the agentic-mbse adapter docs, mirrored
  by a pointer here; every new/changed diagnostic has a fires-on-shape test (independently
  anchored) **and** a silent-on-clean test (R1 addition).
- [x] The R4 verification table is complete — every CONFIRMED-BLIND site reproduced by a failing
  probe before design touched it; the discovery register updated in place.
  <!-- AUDIT 2026-07-06: verified as artifact — design.md:43-49 + plan.md Phase-0 (all rows CONFIRMED-live); _probe.py committed. -->

- [ ] Both repos' suites green (R2 coordinated pair). Item 4 owns a **repo-wide snapshot
  re-capture** — all 20 committed `extraction_snapshot.json` at format v2, one reviewed commit,
  license-gated, capture-script only (R3). The reviewed-diff gate: after re-capture every snapshot
  is byte-identical to before **except the version field and, for constraint-bearing models, the
  new constraint manifest** (there is no old/new coexistence — the loader hard-gates the version).

## Known Requirements

### The mechanism

- **[HARD]** The subtype-aware capability is added at **one** adapter choke point:
  `SysideAdapter.elements_of_type` gains an `include_subtypes` parameter that passes through to
  syside `nodes(kind, include_subtypes=...)`. No call-site-by-call-site query rewrites for the
  base capability. (D4: the fix surface is one parameter, not fifteen patches.)
- **[HARD]** The adapter default stays `include_subtypes=False`. This is an **opt-in per call
  site**, not a global default flip (R1; epic risk row). Every existing call site's behavior is
  unchanged unless it explicitly opts in — so the only behavior changes are the ones this spec's
  decision table enumerates.

### The decision table (spec-time decision (a) — REQUIRED artifact)

Metamodel facts this table rests on (confirmed against the syside stub
`.venv/.../syside/core/__init__.pyi`; SysML/KerML abstract syntax):

- `AssertConstraintUsage ⊂ ConstraintUsage` — `assert constraint foo {…}` produces
  `AssertConstraintUsage`, a direct `ConstraintUsage` subtype.
- `SatisfyRequirementUsage ⊂ RequirementUsage` (verified in the stub, line 16063) — the `satisfy`
  form is a **`RequirementUsage` subtype, NOT an `AssertConstraintUsage`**. The `RequirementUsage`
  exclusion below therefore drops it; that is deliberate (see the satisfy note under the table).
- `require constraint foo {…}` inside a requirement produces a **plain `ConstraintUsage`**
  reached via a `RequirementConstraintMembership`. There is **no** `RequireConstraintUsage`
  metaclass — the assumed/required kind lives on the membership, not on a distinct usage type.
  So `require`/`assume` constraints are **already visible** to an exact-type `ConstraintUsage`
  query.
- `RequirementUsage ⊂ ConstraintUsage` — a `RequirementUsage` is a `ConstraintUsage` subtype,
  but it is a requirement, not a dropped executable predicate.
- `Import` is abstract; concrete subtypes are `MembershipImport` and `NamespaceImport` only.
- `EnumerationUsage ⊂ AttributeUsage`.

**[HARD]** The item ships this decision table. Each row is opt-in/opt-out with rationale and a
pin:

| # | Repo | Call site | Base type | Decision | Rationale | Pinned by |
|---|------|-----------|-----------|----------|-----------|-----------|
| 1 | codegen | `extractor.py:108` `report_dropped_constraints` | `ConstraintUsage` | **include_subtypes=True, EXCLUDE `RequirementUsage`** | `assert` (`AssertConstraintUsage`) and `require`/plain are dropped predicates and must be reported; `RequirementUsage` — and its `satisfy` subtype — are requirement-side and excluded (a blanket flip would over-report them). Satisfy-out is deliberate (see satisfy note) | wi014 assert pin + REQ-EXT-09 re-anchor (fires-on-shape) + silent-on-clean |
| 2 | codegen | `constraint_extractor.py:50` `extract_all_constraints` | `ConstraintUsage` | **DEAD — delete (coordinate Item 8); its docstring is false** | zero callers (grep); docstring line 4 claims "constraint, assert constraint, and require constraint" support while the query is exact-type-blind. Deleting removes the false claim at the root. If design elects to keep it for a future consumer, it must become subtype-aware and its docstring corrected in the same change | n/a (deletion) — else same pins as row 1 |
| 3 | codegen | `parameter_groups.py:102` design-attr sweep | `AttributeUsage` | **KEEP exact-type (opt-OUT); document + pin `EnumerationUsage` invisible** | an enum-valued attribute *is* a user-configurable value, but making it an entry point needs non-float EP typing, which is Item 5's scope; no supported model currently needs an enum EP wired (fusion-tea's `wall_type` is one hop from, not in, the offender set). Flipping now would silently mint mistyped entry points | pin on solar_battery `costing.sysml` + catf_mfe `types.sysml` |
| 4 | codegen | `extractor.py:72,85`; `pipeline_builder.py:120-121`; `hierarchy_resolver.py:596,672`; `usage_extractor.py:260,296,549` (`PartDefinition`/`PartUsage`/`CalculationDefinition`/`CalculationUsage`) | those | **KEEP exact-type (opt-OUT)** | no supported model produces connection/interface/view/case/analysis subtypes; enabling them is explicitly Out of Scope | decision-table record only (no code change) |
| 5 | agentic-mbse | `level3_dataflow.py:48` import sweep | `Import` (abstract) | **include_subtypes=True (or query `MembershipImport`+`NamespaceImport`); ALSO fix the `imported_namespace` guard so `MembershipImport`s are not skipped** | abstract-type query matches zero → dep graph always `{}` → circular check always passes; the secondary guard bug drops MembershipImports even once the type is fixed | fires-on-shape: seeded circular-import fixture FAILS the circular check + produces a non-empty dep graph. silent-on-clean: an **acyclic** import fixture PASSES (non-empty graph, no false-positive cycle) |
| 6 | agentic-mbse | `level4_constraints.py:113` constraint sweep | `ConstraintUsage` | **include_subtypes=True, EXCLUDE `RequirementUsage`** (mirror row 1) | undercounts assert constraints today | fixture pin (fires-on-shape + silent-on-clean) |
| 7 | agentic-mbse | `level6_architecture.py:602` non-executable assert WARN | `ConstraintUsage` | **include_subtypes=True, EXCLUDE `RequirementUsage`** (mirror row 1) | assert constraints never receive the non-executable WARN | fires-on-shape + silent-on-clean |
| 8 | agentic-mbse | the 4 `AttributeUsage` enum sites (parameter_groups equivalents) | `AttributeUsage` | **KEEP exact-type (opt-OUT)** (mirror row 3) | same enum reasoning; keep the two repos' semantics aligned | pin on an enum-bearing agentic-mbse fixture |

- **[HARD]** Rows 1/6/7 require reporting `ConstraintUsage` **including** its predicate subtypes
  while **excluding** `RequirementUsage`. `include_subtypes=True` on `ConstraintUsage` sweeps in
  `RequirementUsage`, so the call site must subtract it (an `is_instance("RequirementUsage")`
  filter, or an adapter `exclude` capability). Mechanism is a design choice; the fixed semantic is
  **assert and require in; requirement AND satisfy out**.
- **[HARD] Satisfy note (deliberate exclusion — decision (a)).** `SatisfyRequirementUsage` is a
  `RequirementUsage` subtype, so the `RequirementUsage` exclusion drops `satisfy` assertions along
  with requirements. This is accepted deliberately, not by accident: (i) no supported model uses
  `satisfy`; (ii) `satisfy` is semantically requirement-side — an assertion *about* a requirement,
  not a free-standing dropped predicate; (iii) the zero-found sentinel's scanned-vs-matched counts
  (below) keep the exclusion **observable** rather than silent — a swept-and-excluded `satisfy`
  shows up in the "scanned" total. The day a supported model asserts via `satisfy`, this note makes
  the choice visible so it can be revisited (the alternative is an "exclude `RequirementUsage`
  except `SatisfyRequirementUsage`" filter — more machinery, deferred until a model needs it).

### The diagnostics (R1 addition — every new/changed diagnostic)

- **[HARD]** Each new/changed diagnostic lands with (a) a test proving it FIRES on the shape it
  claims, with an **independently-anchored** expectation, and (b) a test proving it stays SILENT
  on clean input. Expectations computed by the code under test are banned (the REQ-EXT-09
  anti-pattern).
- **[HARD]** Re-anchor `REQ-EXT-09` (`tests/conformance/test_extractor.py`, class runs 888-923):
  replace the self-referential `expected` (lines 894-899) with a count derived independently — a
  hardcoded literal for catf_mfe or a grep of the fixture source. Add the missing
  **part-usage-owner** leg. Add a
  wi014_toy pin asserting the `assert constraint` at `toy_plant.sysml:51` is reported. Document
  a **mutation check** in the test: deliberately breaking the query (revert to exact-type /
  drop the subtype sweep) must make the test fail.
- **[HARD]** Zero-found sentinel on the report (R1 addition): a summary line "scanned N
  `ConstraintUsage` (incl. subtypes), reported M droppable (K assert, J require/plain), excluded
  E requirement/satisfy" replaces silence. "Scanned" counts the full `ConstraintUsage` subtree;
  "reported" counts droppables after the `RequirementUsage` exclusion; "excluded" surfaces what the
  filter dropped — so a swept-and-excluded `satisfy` or requirement is observable, not silent, and
  an empty result is distinguishable from a blind query. (This is what keeps the report honest even
  when a model genuinely has no droppable constraints.)
- **[NEED]** `require constraint` is certified reported and permanently pinned: it is already a
  plain `ConstraintUsage`, so certification is a fixture row + pin, not a code fix. Add or confirm
  a `require constraint` fixture shape and pin it is reported.
- **[NEED]** The `EnumerationUsage` decision (row 3/8) is pinned by a test on the existing
  enum-bearing fixtures, whichever way it lands, so the choice is deliberate and locked.

### Constraint serialization (spec-time decision (b) — RESOLVED: serialize)

**Decision: adopt the epic recommendation — serialize constraints into the snapshot and replay
the report on the `generate --from-snapshot` path.** (The alternative, deferral, is rejected: it
would leave the third success criterion — the from-snapshot report — impossible, and constraint
serialization is a stated prerequisite for the deferred constraint-execution epic.)

- **[HARD]** The `generate --from-snapshot` path must run the constraint drop report from
  serialized data. Today it cannot: the report reads the live syside model, which is absent
  offline.
- **[INFERRED]** Mechanism (design chooses; recorded reasoning): serialize a **model-wide
  dropped-constraint manifest** at the snapshot top level — a list of records carrying
  `{owner_kind, owner_name, owner_qualified_name, constraint_name, constraint_kind
  (plain/assert/satisfy/require), source_line}` — and have the from-snapshot context replay
  `report_dropped_constraints` from it. Preferred over reusing `PartDefinitionData.constraints`
  (the current stub) because the report is model-wide and owner-kind-aware, and a per-part-def
  field would miss calc-def-owned and part-usage-owned constraints. Design may still choose to
  populate `PartDefinitionData.constraints` instead if it can cover all three owner kinds; the
  requirement is only that the from-snapshot report is faithful to the live report.
- **[HARD]** This bumps `SNAPSHOT_FORMAT_VERSION` 1 → 2 (`snapshot/__init__.py:12`). The loader
  hard-gates on it (INV-2, `loader.py:81`) and rejects a mismatch, so there is **no coexistence
  state**: every one of the **20 committed `extraction_snapshot.json` files** (`tests/fixtures/*/`)
  must be **re-captured**, not diffed-and-kept, or it fails to load. Re-capture runs live extraction
  via `scripts/capture_extraction_snapshots.py` and is therefore **license-gated**. The dead
  `_deserialize_constraint_info` is wired to the chosen mechanism or deleted (coordinate with Item
  8, which lists it).
- **[HARD]** Item 4 **owns the repo-wide re-capture**: one reviewed commit re-capturing all 20
  committed snapshots on format v2, using the selective/full capture tooling Item 1 adds (the
  `--fixtures` name-filter is an Item-1 deliverable). The reviewed-diff gate is precise: after the
  re-capture, every snapshot is **byte-identical to before EXCEPT the version field and, for
  constraint-bearing models, the new constraint manifest**. (This corrects the earlier
  "byte-identical except the version bump" framing — most of the 20 change by at least the version
  field, and constraint-bearing ones by the manifest too.)
- **[HARD] Sequencing (orchestrator ruling — implement stages serialize on one working tree).**
  Order: **Item 1 implement → Item 4 implement → Item 2 implement.** Item 1 creates new fixtures +
  snapshots at v1 and adds the `--fixtures` capture filter; Item 4 then bumps to v2 and re-captures
  everything (including Item 1's new fixtures); Item 2 afterward regenerates only its plant-fixture
  baselines on v2. One item's regen at a time (R3). This is why Item 4 — not Items 2/5/8 — owns the
  format rev.
- **[HARD]** Live-vs-snapshot parity: the from-snapshot constraint report must match the live
  report for the same model (same owners, kinds, counts). (Feeds Item 3's parity work, which the
  adversarial pass flagged as structurally absent for constraints.)

### Verification-first (R4 — REQUIRED spec/pre-design artifact)

- **[HARD]** Before design fixes anything, reproduce each CONFIRMED-BLIND site with a failing
  test or live probe against real fixtures (never mocks). Epic R4 mandates the in-spec verification
  table only for Items 5 and 7, so for Item 4 the table is **produced at design open** (see Next
  Steps), not carried in this spec — each row records finding → probe → CONFIRMED / NOT-REPRODUCED
  / RECLASSIFIED. Update the discovery register (§D4) in place as findings are confirmed or struck.
  A finding that does not reproduce is reclassified with evidence, not fixed.

### Docs (R4 step 4 — same-change)

- **[HARD]** `modeling-assumptions.md` §8 reworded to match reality: it currently claims the
  pipeline "scans the whole model for constraint usages and reports them," which overclaims until
  this lands. New text: the report covers `ConstraintUsage` including `assert`
  (`AssertConstraintUsage`) and `require`/plain predicate shapes, **excludes `RequirementUsage`
  (and its `satisfy` subtype)** as requirement-side, and is available on both the live and
  from-snapshot paths.
- **[HARD]** `reference/01-extraction.md` `REQ-EXT-09` row updated (the "counted structurally"
  verification text is the anti-pattern; replace with the independent anchor + the part-usage leg
  + the assert pin).
- **[HARD]** The decision table is published in the agentic-mbse adapter docs (the D4-mandated
  home), with a pointer from this repo's extraction reference.
- **[NEED]** BACKLOG `[CONSTRAINT-SILENCE]` retired when this item closes (it is the finding of
  record until then).

### agentic-mbse landing (R2 — settled checkout + companion-branch procedure)

- **[HARD]** Canonical checkout is **`/home/reid/1cfe/agentic-mbse`** — the only checkout, and the
  one this project's editable install points to. **Not** `~/agentic-mbse` (the epic/CLAUDE.md
  reference is stale). All agentic-mbse work targets `/home/reid/1cfe/agentic-mbse`.
- **[HARD]** That tree is currently **DIRTY** with unrelated in-flight work (`adr002.py` + two spec
  dirs) sitting on branch `upstream-findings-sync` (whose PR was never created — that is Item 9's
  residue, not this item's). Companion-branch procedure: **create the Item-4 companion branch from
  current `upstream-findings-sync` HEAD, and stage ONLY Item-4 files** — `syside_adapter.py`,
  `level3_dataflow.py`, `level4_constraints.py`, `level6_architecture.py`, and the new
  fixtures/tests/docs. **Never `git stash` and never stage the dirty files** — do not co-mingle the
  other workstream's changes.
- **[HARD]** Re-verify the agentic-mbse line numbers against the live repo before editing —
  `level3_dataflow.py:48`, `level4_constraints.py:113`, `level6_architecture.py:602`, adapter
  `syside_adapter.py:214`. Every agentic-mbse requirement in this spec is derived from the discovery
  register (§D4), not a direct read (this spec-authoring session was sandboxed out of that repo);
  R4's "the probe wins" governs over any single line number.

## Non-Goals

- **Constraint execution.** No boolean-output modules, no assertion channels, no compiling
  predicates. This item makes the drop *loud and true*; execution is a deferred epic. Serializing
  constraints here is a prerequisite for that epic but does not start it.
- **Enabling connection / interface / view / case / analysis extraction** (decision-table row 4).
  No supported model uses them; the table records the deliberate exact-type choice so the day one
  appears, the query is a conscious change.
- **Making `EnumerationUsage` an entry point.** Row 3 keeps it invisible-and-documented; the
  non-float entry-point diagnostic that would make enabling it safe is Item 5's.
- **The other silent-failure sites** (D3's 16) — Item 5. This item owns only the D4
  enumeration-blindness family and the constraint report.

## Open Questions / Deferred to design

- **Exclusion mechanism for rows 1/6/7** — call-site `is_instance("RequirementUsage")` filter vs
  an adapter `exclude` set. Design decides; the semantic (assert and require in; requirement AND
  satisfy out) is fixed.
- **Serialization carrier** — dedicated top-level dropped-constraint manifest vs populating the
  `PartDefinitionData.constraints` stub. Design decides against the "covers all three owner kinds"
  and "faithful to live report" constraints above.
- **Dead `extract_all_constraints` (row 2)** — delete outright here vs hand to Item 8's dead-code
  sweep. Either is legal; coordinate so it is deleted once, not twice, and so its false docstring
  does not survive this item.
  *(The agentic-mbse checkout, dirty-tree branching, and line re-verification are now settled — see
  "agentic-mbse landing" under Known Requirements above; they are no longer open questions.)*

---

## Related Artifacts

- **Epic:** `.project/backlog/epic_pipeline_truth.md` (Item 4; R1/R2/R4; Success Criteria SC-D, SC-H)
- **Required Reading:** discovery register `.project/research/20260706_pipeline-truth-discovery.md`
  §D4 (verdict table + TYPE_MAP audit) and the "Orchestrator verifications" block (snapshot-path
  corrections); BACKLOG `[CONSTRAINT-SILENCE]`; `docs/architecture/reference/01-extraction.md`;
  `docs/architecture/modeling-assumptions.md` §8; agentic-mbse adapter + `level3_dataflow.py:48`,
  `level4_constraints.py:113`, `level6_architecture.py:602`
- **Coordinated pair (R2):** agentic-mbse companion branch at `/home/reid/1cfe/agentic-mbse` (fix +
  fixtures + adapter decision-table docs) — see the settled "agentic-mbse landing" procedure under
  Known Requirements; accumulated for Item 9 sync
- **Memory:** `verify-then-fix-protocol` (R4 discipline), `plant-idiom-fixtures` (wi014_toy shape),
  `agentic-mbse-repo-path` (canonical checkout + sandbox gotcha)
- **Design:** `.project/active/subtype-enumeration/design.md` (to be created)

---

**Next Steps:** After approval, proceed to `/_my_design` — which must open with the R4 verification
table (reproduce each CONFIRMED-BLIND site with a failing probe) and settle the three
design-deferred mechanism choices above (exclusion filter, serialization carrier, dead-code
disposition). The agentic-mbse checkout and companion-branch procedure are already settled (see
"agentic-mbse landing"); design still re-verifies the agentic-mbse line numbers against the live
`/home/reid/1cfe/agentic-mbse` tree before editing it.
