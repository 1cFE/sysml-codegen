# Audit: Canonical Usage Domain and Catalog Totality (CONSTRAINT-SEMANTICS Item 2)

**Verdict:** Needs-work
**Audited:** 2026-08-12
**Branch:** `item7-rebuild` (both worktrees)
**Commit:** codegen `ba756fb` (implementation tip `d03a415`), companion `bc69f04`
**Auditor environment:** `/home/reid/1cfe/item7-rebuild-venv/bin/python`, licence sourced from
`/home/reid/1cfe/agentic-mbse/.env`. Both trees clean at audit time; nothing was fixed.

---

## The Point

SysML models use constraints to enforce physics, so that automated design search stays inside
the space of designs that could actually be built. That only works if every constraint the
modeller writes is accounted for. Before this item, `catf_mfe_d5` — the richest model in the
corpus — authored 65 constraint usages and produced 9 carriers. The other 56 were not excluded
and not deferred; they were *absent*. Nothing recorded that they had ever been written.

Absence is worse than a bad answer, because it is invisible. Every downstream number rested on a
population that had silently lost 86% of its members, and the two requirement rows that were
supposed to catch this read PASS — because each specimen fixture happened to have a carrier.

So the point is: **every authored constraint usage gets exactly one visible disposition, and the
proof of that cannot come from the same machinery that lost them.** Two halves. Make the domain
total, and prove it with evidence that does not descend from the domain.

## Summary

The core of this item is genuinely done, and the hard part is done well. The domain is total at
65, minted before occurrence expansion, joined to the occurrence tier by identity, and carried
through a bumped v3 codec that fails closed. The manifest sweep is gone rather than kept in sync,
and the totality oracle is independent of the thing it checks — the circularity the spec named as
the central risk is genuinely closed. I reproduced the headline from the `.sysml` source without
touching the elaborator, and it holds exactly.

Three things stop me short of certifying. The completeness gate does not catch the mutation the
spec's second success criterion names, for the 56 members that are the whole reason the item
exists (**A1**). One shipped reference doc still teaches the pre-landing behaviour and names this
item as the future work that will fix it, which is the item's own recorded falsifier firing
(**A2**). And minting still raises model-wide on one path, which is the exact failure design
invariant 5 was widened to prevent, with two shipped docstrings asserting the opposite (**A3**).

None of these is a design flaw. A1 and A3 are gaps in enforcement at boundaries the design
identified correctly; A2 is a missed file. The item is close.

## Product Judgment

**Is this the right piece of work? Yes — emphatically, and the strongest evidence is what it
deleted.** `collect_constraint_manifest` is gone from `src/` and `tests/` entirely rather than
demoted to a synced second inventory, and the replacement oracle reads `.sysml` source through a
licence-free scanner that shares no code, no adapter, and no parse with the elaborator. The
temptation here was to build a second constraint inventory and compare the two; that would have
produced a green gate that could never detect the failure that mattered. The item refused it.

**Product-lens ledger gate: DISPOSED** (audit-F1..audit-F5 appended this session; see
`product-lens.md`). No owner-graded or `[HARD]` statement is contradicted by the *behaviour*.

**But the ledger's own recorded falsifier fired**, on audit-F1/**A2** below: "a landing in which
the tests pass while shipped documentation still describes the pre-landing behaviour." That
tests an `[OWNER]`-graded sequencing rule — "fix documentation and the test model to match … then
run tests to confirm" (`rulings-20260812.md:19-21`). It must be closed before this item closes.

**Two structural smells fired, and I am not resolving either here:**

- **Smell #2 (a special category exempts a case whose user-visible meaning is unchanged)** on
  **A3**. A malformed `@inapplicable:` doc comment — an authoring typo — erases the carriers of
  all 65 usages, while the user-visible meaning of those 65 constraints is unchanged.
- **Smell #4 (correctness depends on downstream knowledge of an internal representation)** on
  **A4**. Three generation seams read `constraint_catalog is not None` as a proxy for "this
  package has executable constraint content"; this item changed what that nullable means.

Smells #1, #3 and #5 are clear, and I verified #1 and #3 rather than accepting the record. The
oracle asserts by identity list over every comparable constraint-bearing fixture, not by count,
and the three routes are compared field for field rather than digest against digest.

Under the audit rubric a fired-and-unresolved smell forbids Certify regardless of the rubric
below. Combined with A1 — a stated success criterion measurably unmet — the verdict is Needs-work.

---

## Findings

Severity: **HIGH** = a stated success criterion or design invariant is not met.
**MEDIUM** = a real defect or unstated behaviour change, narrow blast radius.
**LOW** = accuracy, robustness, or hygiene.

### A1 — Removing a non-reaching carrier from the shipped catalog does not fail generation — HIGH

**Spec success criterion 2** (`spec.md:68-69`): "Removing or duplicating any carrier fails
generation with a named, usage-identifying completeness diagnostic."

Duplication holds. Removal holds **only for carriers that reach an occurrence** — 9 of the 65.
Removing a row whose `occurrence_count == 0` generates successfully and silently, on both
fixtures I tried:

```
constraint_domain_detached_owner (2 rows)
  removed row occ=0  -> generation=True   (silent)
  removed row occ=1  -> generation=False  "catalog row joins no domain member for
                                           constraint_domain_detached_owner::Live::reached_gate"
catf_mfe_d5 (65 rows, 9 reaching)
  removed row occ=0  -> generation=True   (silent)
  removed row occ=1  -> generation=False  "catalog row joins no domain member for
                                           CATFMFEVacuum::catf_vacuum_pumping::PumpingSpeedConsistency"
```

**The 56 unguarded rows are exactly the population this item exists to make visible.**

The cause is structural and both layers miss it for the same reason. At the graph layer,
`validate()` joins occurrence nodes to records (`test_an_orphaned_occurrence_node_is_refused_at_the_graph`,
`tests/conformance/test_constraint_catalog_totality.py:139-146`) — a record with no node has
nothing to orphan. At the catalog layer, `_preflight_constraint_totality`
(`src/sysml_codegen/cli/__init__.py:317-380`) checks the catalog against *itself*: duplicates,
entries joining no row, disagreeing counts. A removed non-reaching row leaves the catalog
internally consistent, so nothing fires.

This is the acknowledged cost of the Phase 6 deviation (`plan.md:1313-1320`): "the preflight's
subject is the catalog, not the domain," because `_generate_package_from_graph` takes a
`ComputationGraph` and is deliberately authority-neutral. The reasoning is sound; the consequence
was not followed through. Design invariant 4 ("exactly one `usage_records` row per domain
member") is stated as a producer obligation in `_build_constraint_catalog`, never as a check.

**What should change:** the domain→catalog cardinality needs one check that is not
catalog-internal. Either the sealed `ExactPipelineContext` — which already re-decodes and
re-projects on every read and holds both sides — asserts the count, or the preflight receives the
domain size. Not for me to design.

**Caveat, stated fairly:** no live defect produces this today. Projection is deterministic and
the context re-projects, so the mutation is reachable only by a *future* projection defect. This
is defense-in-depth that does not defend. It is HIGH because the criterion is explicit and the
unguarded set is the item's headline population, not because packages are shipping wrong today.

### A2 — A live reference doc still teaches the pre-landing behaviour and names this item as its fix — HIGH

`docs/architecture/reference/28-constraint-lowering-and-catalog.md:56-59`:

> *(Target state for the owner-kind half: today an owner kind with no expansion branch — a
> `calc def` owner — yields no occurrence and therefore no catalog record at all.
> CONSTRAINT-SEMANTICS Item 2 closes that.)*

False at HEAD. A calc-def-owned usage now mints a record with `non_reaching` /
`owner_kind_unattachable`, and it is 51 of `catf_mfe_d5`'s 65 — measured this session. The same
paragraph is stale twice more: `:48-50` says a `requirement_def` owner is "cataloged with one
record, `eligible=False`", where the disposition vocabulary is now `excluded` /
`out_of_profile_owner`; and `:46` contradicts `:57` on calc-def expansion.

The doc carries **no** retiring banner (`:1-16`) and is **not** in CLAUDE.md's retired list
(03, 04, 05, 07, 10, 11, 12, 13, 17, 24, 25, plus 09 mixed), so a reader treats it as current —
while it documents `analysis/constraint_lowering.py`, which no longer exists
(`src/sysml_codegen/analysis/` holds only `source_referent.py`).

This is the `[NEED]` doc-correction obligation (`spec.md:254-259`) and the item's own falsifier.
Item 1's two forward pointers *were* correctly retired — `modeling-assumptions.md:473-496` now
teaches the landed behaviour — and both matrix rows were re-anchored. This one file was missed.

**What should change:** correct `:44-59`. If doc 28 is in fact a retired-stack document, give it
the banner and add it to CLAUDE.md's list — but do not leave a live-looking doc naming this item
as future work.

### A3 — Minting raises model-wide on the inapplicability path, violating design invariant 5 — MEDIUM

Design invariant 5 (`design.md:403-411`), widened in rev 2 in response to design-F1 precisely to
close this: **"Minting never raises, for any form."** The rationale, from the lens finding that
forced it: a raise during minting means "*no* usage in that model carries a disposition, which is
the absence-not-disposition failure this whole item exists to end."

`_mint_constraint_usage_record` evaluates `self._inapplicability(usage)` inline as a constructor
argument (`src/sysml_codegen/elaboration/elaborate.py:1151`), and `_inapplicability` raises
`ElaborationInvariantError` on a marker written on a later documentation line (`:1183-1188`) and
on a malformed marker shape (`:1194-1198`). That propagates out of `_build_constraint_nodes` and
converts at `:255-266` into a single model-wide `ElaborationDiagnosticError`.

Confirmed by the item's own tests, which assert the model-wide type:
`tests/unit/test_constraint_inapplicability.py:56` and `:63` both expect
`ElaborationDiagnosticError`. Corroborated structurally — `constraint_domain_inapplicable_late_marker`
and `constraint_domain_inapplicable_malformed` sit in the oracle's `REFUSED_BY_DESIGN` set
precisely because they produce no domain at all.

**Two shipped docstrings assert the opposite of the code.** `elaborate.py:1116-1124`: "the record
is built from identity metadata alone … even then the failure arrives as this record's disposition
rather than as a bare error that leaves every other usage without a carrier." And `:1254-1259`:
"the predicate walk and the definition cross-check are the only two paths that can fail."

The halt itself is right — a malformed marker should stop the run. What is wrong is that it stops
it the way invariant 5 forbids. The mechanism to do it correctly is already built and already
error-grade: `classification_incomplete` (`graph.py:288`, `elaborate.py:1263-1266`,
`_halt_on_unattached_constraints:1297-1319`) keeps the halt while every other usage keeps its
record.

**What should change:** route the two `@inapplicable` parse failures through a per-usage
disposition and keep the halt — or, if the model-wide raise is deliberate, correct both docstrings
to say so and record why this path is exempt from invariant 5.

### A4 — `constraint_catalog is not None` changed meaning; three generation seams read the old one — MEDIUM

`project.py:1087` now returns `None` only when the *domain* is empty, rather than when expansion
produced nothing. Correct, and the fix the item needed. But that nullable gates three things that
mean "this package has executable constraint content": emission of `schemas/constraint_types.py`
(`cli/__init__.py:429-436`), the registry's `ConstraintEvaluation` / `ConstraintReport` imports
and group names (`generation/registry.py:353-360`), and the predicate-name preflight
(`cli/__init__.py:388-392`).

Measured on `constraint_domain_satisfy_calc_def`, a calc-def-only fixture:

```
catalog is None?                       False
usage_records: 2   concrete entries: 0
generation:                            True
ships schemas/constraint_types.py:     True
registry imports ConstraintEvaluation/ConstraintReport: True
```

Before this item that fixture produced no catalog and therefore shipped neither. It now ships a
constraint evidence schema and a report type it can never populate. Whether that is right is a
real product question — a study arguably *should* see a zero-coverage report — but nothing states
it either way, and the comment above the gate still reads "A constraint-free corpus writes nothing
here (INV-7)" (`cli/__init__.py:427-428`), which no longer distinguishes constraint-free from
authored-but-none-reaching.

The one test for this shape stops at projection and never generates
(`tests/conformance/test_constraint_catalog_totality.py:68-75`), and no baseline fixture has it,
so no byte gate would have caught the change.

**What should change:** state which meaning the gate carries, add a generation-level test for the
usage-only package, and correct the INV-7 comment.

### A5 — The oracle's 18-fixture exemption set is asserted, not checked — LOW

`REFUSED_BY_DESIGN` (`tests/conformance/test_constraint_population_oracle.py:43-64`) removes 18 of
the 42 constraint-bearing fixtures from the domain comparison under one collective justification,
and is referenced only at its definition and to build `COMPARABLE` (`:87`). **No test asserts that
a member actually refuses.** A fixture that starts elaborating cleanly would stay silently exempt.

**I tested all 18 and every one currently refuses** (`ElaborationDiagnosticError` ×14,
`ElaborationError` ×4 — `catf_mfe_model`, `gate_a`, `gate_a_package_owner`, `plant_values`,
`shared_producer`). So the exemption set is accurate today; this is latent drift, not a live hole,
which is why it is LOW rather than HIGH.

It is not hypothetical for this epic, though. `constraint_domain_calc_def_owner` is exempt
precisely because the asserted calc-def-owner case halts today, and Q2 stages that capability to
execute later. When it lands, that fixture will elaborate and the oracle will not notice it
stopped being checked. Rule 2 still guards the file against source drift (`:107-109`), so this
narrows the domain claim rather than holing it.

**What should change:** add the fourth rule — every `REFUSED_BY_DESIGN` member must raise.

This also disposes of the "deleted `item4_require` coverage" concern carried into this audit:
`item4_require` is exempt because it genuinely refuses (`ElaborationDiagnosticError`), not because
coverage was quietly dropped.

### A6 — CLAUDE.md still says four preflight checks; there are five — LOW

`CLAUDE.md:64` enumerates constraint name safety, duplicate output paths, params coverage (V11),
and registry class-name collisions. This item added Step 1.8, the constraint totality preflight
(`cli/__init__.py:317-380`, invoked at `:1156`). Same falsifier family as A2, one line.

### A7 — The product-lens ledger has no plan-stage or implement-stage entry — LOW

`product-lens.md` holds exactly two stage entries: spec (`:6`) and design (`:145`). The lens was
not run at plan or implementation. Recorded here rather than passed over silently, per the
instruction to surface it. The audit-stage entry appended this session partly compensates —
it is the first lens pass over actual code — but it is one pass at the end, not the running check
the pipeline intends.

### A8 — Verification.md's stale-nodeid signal, resolved — informational, no action

`.pytest_cache/v/cache/lastfailed` at audit time held 23 entries dated 2026-08-12 21:32,
including three that looked like this item's own mutation tests
(`test_generation_refuses_a_broken_join_by_name_before_writing[removed-disposition|duplicated-record|misjoined-count]`).
**Those node ids no longer exist** — the tests were renamed into individual cases. I re-ran the
module: 14 passed. The cache was stale, not a hidden red. Recorded so the next reader does not
re-investigate it.

---

## Probe evidence

All probes run at codegen `ba756fb` / companion `bc69f04` under
`/home/reid/1cfe/item7-rebuild-venv/bin/python` with the licence sourced. Independent scripts
except where noted.

### Environment claims (verification.md:44-51) — CONFIRMED

The documented interpreter resolves the companion **worktree**, not the main checkout:

```
companion: /home/reid/1cfe/agentic-mbse-item7-rebuild/src/agentic_mbse/__init__.py
codegen:   /home/reid/1cfe/sysml-codegen-item7-rebuild/src/sysml_codegen/__init__.py
```

### Probe 1 — the headline — CONFIRMED, and corroborated from source

**Source-side, without touching the elaborator.** `catf_mfe_d5` has 70 lines containing
`constraint`, of which 5 are comments → **65 authored usages**. Every one is the inline
`constraint Name { … }` form; zero `assert`, zero `constraint def`. This independently confirms
both the 65 and verification.md's correction that the fixture has **zero eligible** constraints.

**Elaborator-side:**

```
usage_records:  65
reaching(occ>0): 9
eligible:        0
by reason: {owner_kind_unattachable: 51, owner_has_no_occurrences: 5, unassessed_form: 9}
by kind:   {non_reaching: 56, excluded: 9}
by severity: {info: 65}      by form: {plain_usage: 65}
occurrence-tier nodes: 9     join ok: True
```

The 51/5/9 split matches the research's cause account exactly. All-`info` severity is why the
frozen twin still generates.

**Shipped, not just in-memory:** generation succeeds and `contracts/model_contract.json` carries
`/constraint_catalog/usage_records` with **65** rows at `catalog_schema_version 3.0.0`, each row
carrying `disposition_kind`, `disposition_reason`, `disposition_severity`, `declaration_id`,
`owner_kind`, `owner_qualified_name`, and a human-readable `disposition_detail`.

**Twins untouched:** `git diff --check` clean, tree clean, `test_d5_variants.py` passes in the
full suite.

### Probe 2 — totality mutation — PARTIALLY CONFIRMED → finding A1

Duplication refuses by name, writes nothing:

> `constraint usage domain incomplete: duplicate usage record for
> constraint_domain_detached_owner::Detached::vacuous_gate (1aac10a3-233b-5ab1-8eae-b1de07cb430f)`

Removal refuses only for reaching rows. See **A1** for the full matrix. The item's own
`test_the_refusal_names_the_usage_not_just_a_count` is identity-shaped, not message-fragment-only
— it asserts both `row.usage_qualified_name` and `row.declaration_id` appear in the diagnostic
(`test_constraint_catalog_totality.py:220-221`), which I confirmed. The "message-fragment-only"
concern carried into this audit does not hold.

### Probe 3 — severity by cause — CONFIRMED on all three shapes

| fixture | outcome |
|---|---|
| `constraint_domain_inapplicable_unattachable` | **HALTS**: `SI_CONSTRAINT_UNATTACHED` naming usage, declaration id, location, and "is asserted (definition_typed) but its owner …" — usage *and* missing attachment, per contract invariant 9 |
| `constraint_domain_detached_owner` | `non_reaching` / `owner_has_no_occurrences` / **warning**, elaborates, **plus** the companion `[advisory/vacuous_asserted_gate]` naming usage and detached owner with a location |
| `constraint_domain_plain_forms` | `blocked_if_asserted` → `excluded` / `unassessed_form` / **info**, occ=1, generates and catalogs unassessed; no advisory, correctly |

Invariant 6 also confirmed incidentally: on `constraint_domain_inapplicable`, the marked usage
carries `Inapplicability(reason='no build of this variant is planned')` while its disposition
stays `non_reaching` / `owner_has_no_occurrences` / warning — the annotation does not rewrite it.

*Observation, not a finding:* an author who marks a gate `@inapplicable:` still receives the
companion advisory, because the companion cannot see the marker. That is a direct consequence of
invariant 59's independence, not a defect.

### Probe 4 — three-route parity — CONFIRMED, field for field

`constraint_domain_inapplicable` (the annotation-bearing fixture), live vs in-place snapshot vs
snapshot relocated to an unrelated deep temp path. All fields on all members agree across all
three, **except** `source_file`:

```
live:      ///home/reid/1cfe/sysml-codegen-item7-rebuild/tests/fixtures/.../model.sysml
in-place:  root-0/model.sysml
relocated: root-0/model.sysml
relocated domain contains an absolute checkout path: False
inapplicability survives all three: 'no build of this variant is planned' (×3)
```

`source_file` is the deliberately route-dependent field, masked and separately asserted for
portability in `test_constraint_usage_domain_parity.py:10-13` — documented, not a hidden
exemption. The annotation surviving all three routes is the load-bearing result: it is a
live-only elaboration step, so this is the fixture where live and snapshot would diverge if it
were re-read downstream instead of sealed.

### Probe 5 — companion advisory and invariant 59 independence — CONFIRMED

The advisory fires at `advisory` grade without halting (see probe 3). With
`_vacuous_asserted_gate_fact` suppressed at the writer, codegen's encoded domain is
**byte-identical** (5410 bytes, `True`). Codegen's disposition does not depend on the companion's
advisory.

### Probe 6 — oracle loudness — CONFIRMED, both halves, restored

93 oracle nodes, matching verification.md.

- **Deleted `wi014_toy.json`** → fails by name in three places:
  `AssertionError: no expectation file: ['wi014_toy']`, plus
  `test_the_expectation_file_still_matches_its_source[wi014_toy]` and
  `test_the_domain_matches_the_reviewed_expectation[wi014_toy]`.
- **Corrupted one `source_line`** (51 → 9999) → 2 failed, 91 passed, both failures naming the
  usage and showing the exact tuple diff.
- **Restored** → 93 passed, `git status` clean.

### Probe 7 — fail-closed — CONFIRMED

```
committed schema: instance-graph/v3
v2 schema token           REFUSED: SI_SNAPSHOT_INVALID: unsupported instance graph schema
                                   'instance-graph/v2'; expected 'instance-graph/v3'
constraint_usages stripped REFUSED: SI_SNAPSHOT_INVALID: document.graph has missing keys
                                   ['constraint_usages'] and unknown keys []
```

Exact-match version rule, named diagnostic, and the new tier is part of the closed key set rather
than an optional field.

### Probe 8 — suites and gates — CONFIRMED, matching verification.md exactly

| gate | verification.md | reproduced |
|---|---|---|
| codegen full licensed | 1826 passed / 34 skipped / 65 deselected / 0 failed | **identical** |
| codegen licence-skip lines | 0 | **0** |
| companion full licensed | 1821 passed / 1 skipped / 5 deselected / 10 failed | **identical** |
| companion licence-skip lines | 0 | **0** |
| codegen `ruff check src` | 12 (baseline 14) | **12** |
| codegen `mypy src` | 55 (baseline 57) | **55 in 11 files** |
| `git diff --check` | clean | **clean, exit 0** |

**The companion's 10 failures are genuinely pre-existing and unrelated.** All ten fail with
`FileNotFoundError: [Errno 2] No such file or directory: 'python'` — they shell out to a bare
`python` that is not on PATH in this environment. They are CLI/script-invocation tests
(`test_cli.py`, `test_index.py`, `test_sysml_quality_checks.py`,
`test_validation/test_integration_regression.py`); none touches constraint facts, the advisory, or
the severity map. I confirmed this by cause rather than by stashing.

**Focused modules re-run:** 127 passed across the six modules I selected (totality, parity,
oracle, catalog totality, inapplicability, upstream pins). Verification.md's 155 spans eleven
modules; I did not run the full eleven, so that figure is corroborated in part, not reproduced.

---

## The two recorded deviations, weighed

### Scanner-derived expectation files — ACCEPTABLE

The design asks for files "authored by reading the `.sysml` source, reviewed as source-derived"
(`design.md:475-478`). They were generated by the licence-free scanner and then checked
(`verification.md:132-142`).

**Accept.** The load-bearing property is independence *from the domain*, and it holds completely:
the scanner shares no code, no adapter, and no parse with the elaborator, so the circularity the
spec identified as the central risk is closed regardless of who typed the rows. What is weaker is
independence between the scanner and the files — the drift rule cannot catch a scanner bug present
at generation time.

The mitigation is real and I weighted it: the scanner and the domain were compared on all 42
fixtures *before* any file was written, agreeing with zero differences on the 24 that elaborate,
and the two disagreements found were scanner bugs that were fixed. That is a stronger check than
hand-typing 42 files would have produced, because hand-typing has its own error rate and no
cross-check. The residual risk — a scanner bug that coincidentally matches an elaborator bug on
all 24 fixtures — is small and would require the two independent implementations to be wrong the
same way.

The deviation is recorded plainly in both `plan.md` and `verification.md`, with its weakness named
rather than argued away. That is the behaviour the capture-fidelity rules ask for.

### Phase 5 pull-forward and the 61-node frozen refusal list — ACCEPTABLE

Phase 5 (codec v3) moved into the Phase 3 window because Phase 3's own recorded contingency fired:
the join check reported "occurrence node joins no usage record" for every constraint in every
committed v2 snapshot, taking 156 nodes red (`plan.md:1128-1176`).

**Accept.** Two brief non-negotiables genuinely could not both hold — committed v2 fixtures cannot
load until recaptured, and recapturing early would move the single reviewed recapture off the end
of the item. The implementer surfaced the conflict rather than resolving it silently, which is
exactly rule 4 of the capture-fidelity discipline, and resolved it the conservative way: the
recapture stayed at Phase 8, and the intermediate gate was redefined as "no failure outside the
frozen list", with the list committed at `v2-refusal-list.txt` (61 nodes, enumerated by node id).

That keeps the gate's teeth — any *new* failure still fails the phase — and the list is now
discharged to zero, which I confirmed by the clean full-suite run. The one real cost is recorded
honestly: Phase 6's baseline-churn check could not run in that window, "recorded here so it is not
mistaken for having been checked" (`plan.md:1340-1344`).

---

## The three "left open" items, weighed

1. **`inline`-form vacuous gate cannot be marked `@inapplicable:`** — does **not** block. This is
   upstream parser behaviour (SysIDE drops a doc comment inside an inline-predicate body), it is
   guarded rather than hidden by
   `test_every_authored_inapplicable_marker_reached_the_domain`, and a working author workaround
   exists. Correctly scoped out.
2. **`classification_incomplete` has no constructible corpus trigger** — does **not** block on its
   own, and I agree with the choice to record it rather than fake it with a mock. But note it
   interacts with **A3**: the one error-grade minting path that would prove invariant 5 works is
   unreachable, and the one minting path that *does* raise violates it. Closing A3 would give this
   branch its first real exercise.
3. **The residual invariant-9 gap** (a vacuous gate under a typed-but-uninstantiated part gets the
   disposition but no advisory) — does **not** block. Closing it means reimplementing occurrence
   resolution in the companion, which is the second-representation smell this item removes. The
   containment direction is pinned from both sides, so the gap can only ever be a missing advisory,
   never a false one. Accepting this is the right call.

Item 4 (the two `.project/concepts/` references to `ConstraintManifestEntry`) is correctly left —
they are decision records of a superseded era, and REQ-EXT-09 names the retired sweep deliberately,
to say what the row was re-anchored *from*. I confirmed that wording at
`verification-matrix.md:336`.

---

## Rubric

### Plan completion

All eight phases have completion notes and the deviations are recorded in the implementer's own
words rather than smoothed over. Phase 5's empty `### Phase 5 Completion` heading
(`plan.md:1283`) is a formatting artifact — its content lives in the pull-forward block above it.
No placeholder code or TODOs found in the item's changed surface.

### Spec conformance

| Success criterion | Verdict |
|---|---|
| 65 carriers, zero absence, twins byte-pinned | **Met** — reproduced from source and from the elaborator; catalog ships 65 rows |
| Removing or duplicating any carrier fails generation | **Not met** — duplication yes; removal only for the 9 reaching rows (**A1**) |
| Severity by cause across the three shapes | **Met** — all three reproduced (probe 3) |
| Inapplicability explicit, fingerprinted, cannot silently change coverage role | **Met** — travels through the v3 codec, survives relocation, does not rewrite the disposition |
| Three routes agree; old/malformed shapes fail closed | **Met** — field-for-field parity; v2 and stripped-tier both refused by name |
| REQ-EXT-09 / REQ-CL-04 cite non-self-referential tests, self-contradiction gone | **Met** — both rows re-anchored to the oracle and read PASS; REQ-EXT-09's domain-vs-carrier contradiction resolved by the D6 row rewrite |
| No shipped documentation describes pre-landing behaviour | **Not met** — Item 1's two forward pointers were corrected, but doc 28 was missed (**A2**); CLAUDE.md preflight count stale (**A6**) |
| Manifest sweep's fate recorded and executed; oracle named | **Met** — zero hits in `src/` and `tests/`; oracle is the 42 expectation files + licence-free scanner |
| Focused tests, full suites, ruff/mypy zero-new, `git diff --check`, counts recorded | **Met** — every figure reproduced exactly (probe 8) |
| One reviewed final-schema recapture if the schema changed | **Met as recorded** — 21 snapshot-bearing fixtures, single recapture; see *Not checked* |

Non-goals respected. I found nothing built outside scope: the four `all_satisfied` assertions in
`tests/execution/` are untouched, the occurrence tier is unchanged, and no parallel inventory was
created.

### Design conformance

Invariants 1, 2, 3, 4, 6, 7, 8 and 9 (design-local) are implemented where the design placed them,
and I verified 3, 4, 6 and 9 by probe. D1, D2, D4, D5, D6, D7, D8, D9 and D10 were followed;
PD3, PD4 and PD5 were each discharged with the actual line numbers re-checked rather than trusted.

Two deviations from design:

- **Invariant 5 is violated on the inapplicability path (A3)** — the one substantive design
  deviation, and it is undocumented as a deviation.
- **Invariant 4 is a producer obligation, never a check (A1)** — the design says the catalog holds
  exactly one row per domain member; nothing enforces it across the domain↔catalog boundary for
  non-reaching rows.

The design's stated boundaries otherwise hold: elaboration decides dispositions, projection
renders without classifying, and the preflight refuses without repairing.

### Code integrity

No god functions, no parameter sprawl, no broad `except Exception`, no compatibility shims. Both
schemas were bumped rather than dual-read, which is the honest choice. The closed owner-kind map
replacing the `type(owner).__name__.lower()` fallback (invariant 8) is a genuine improvement, and
it surfaced a real correction during recapture (`partusage` → `part_usage` on three fixtures) that
the plan had not anticipated and the implementer surfaced rather than absorbed.

Two failure-honesty findings, both already filed: **A3** (a raise where the design requires a
disposition) and **A4** (a nullable whose meaning changed under three readers). The docstrings at
`elaborate.py:1116-1124` and `:1254-1259` are the sharper problem in A3 — a future reader will
trust them.

---

## Certification

**Verdict: Needs-work.** Three things must close:

- **A1** — the domain↔catalog cardinality check for non-reaching rows. Spec success criterion 2 is
  measurably unmet for 56 of the 65 members the item exists to make visible.
- **A2** — `docs/architecture/reference/28-constraint-lowering-and-catalog.md:44-59`. A doc edit,
  not a design question, and the item's own recorded falsifier.
- **A3** — either route the two `@inapplicable` parse failures through a per-usage disposition, or
  correct the two docstrings and record why the path is exempt from invariant 5.

**A4** should be resolved before close (state the gate's meaning, add the generation-level test,
fix the INV-7 comment). **A5**, **A6** and **A7** are small and can travel.

I want to be clear about proportion. This is a strong item. The central risk — proving totality
with evidence that descends from the truncated set — is genuinely closed, and closed the expensive
way, by deleting the second inventory rather than synchronising it. Every headline number in
`verification.md` reproduced exactly, including the correction the implementer volunteered against
their own design's premise. The findings above are gaps at the edges of a correct design, not a
wrong approach.

**Tracking artifacts deliberately not updated.** Per the instruction not to fix anything, I did not
mark checkboxes in `spec.md`, `plan.md`, or the epic, and did not touch `CURRENT_WORK.md`. The
spec-conformance table above records which criteria I verified as met; `/_my_close` should apply
them once A1–A3 are closed. The audit-stage entry **was** appended to `product-lens.md`, as
explicitly requested, flagged with its reconstructed-method provenance.

**Not checked:**

- **The recapture diff itself.** I confirmed all 21 snapshot-bearing fixtures decode at v3 and that
  the parity/oracle/codec gates pass over them, but I did not re-review the 21-fixture diff key by
  key, nor independently re-derive the count of 21 against the 96 fixture directories. The claim
  that no fixture changed by timestamp alone is taken from the record.
- **Verification.md's 155 focused-test figure.** I ran six of the eleven modules (127 passed). The
  remaining five modules were exercised only inside the full-suite run.
- **The companion in depth.** I ran its full suite, diagnosed the 10 pre-existing failures by
  cause, and probed the advisory's grade and independence. I did not audit the companion's
  `Eligibility` enum totality, its severity-map closure, or its schema-bump surface beyond the
  pin test.
- **Generated package correctness.** I confirmed generation succeeds and that the catalog ships 65
  rows; I did not execute a generated package under real TEAx/simkit, and did not verify the TEAx
  `ACCEPTED_CATALOG_SCHEMA_VERSIONS` hand-off, which is out of this repo by design.
- **Item 7 evidence-invalidation register.** I confirmed three entries are claimed filed in the
  epic; I did not audit whether they are complete against what this landing actually invalidated.
- **Byte-identity of baseline outputs.** Phase 6's baseline-churn check could not run in the frozen
  window, and I did not run it retrospectively.
- **Snapshot authenticity.** The envelope digest is unkeyed by design; I verified coherence and
  fail-closed behaviour, not provenance.
- **`git log` / commit-boundary review.** Git was unavailable for most of this session; I verified
  tree state and HEAD but did not review the per-commit landing order beyond what the record claims.
