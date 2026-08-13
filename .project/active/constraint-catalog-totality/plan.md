# Implementation Plan: Canonical Usage Domain and Catalog Totality

**Status:** Draft
**Created:** 2026-08-12
**Last Updated:** 2026-08-12 (absorbs design rev 3 / O-1: the vacuous advisory is companion
authoring validation — new Phase 4C, PD2 rewritten, PD4/PD5 added, completion criteria span both
repos)
**Epic:** CONSTRAINT-SEMANTICS, Item 2
**Branch:** `item7-rebuild` (worktree `/home/reid/1cfe/sysml-codegen-item7-rebuild`; companion
worktree `/home/reid/1cfe/agentic-mbse-item7-rebuild`)

## Source Documents

- **Spec:** `.project/active/constraint-catalog-totality/spec.md`
- **Design:** `.project/active/constraint-catalog-totality/design.md` (rev 3) ← component detail,
  decisions D1–D10, the token vocabulary and precedence table, invariants 1–9, oracle coverage,
  *The Companion Advisory*, cross-repo landing order. **Do not re-derive any of that here; open the
  design.**
- **Design review:** `.project/active/constraint-catalog-totality/design-review.md` (F1–F12 resolved
  in rev 2; orchestrator finding **O-1** resolved in rev 3 — the vacuous advisory is companion
  authoring validation, not a codegen log line)
- **Stage brief:** `.project/active/constraint-catalog-totality/briefs/plan.md`

## The Point

Constraints are how these models enforce physics, which is what keeps design search viable. The
lifecycle contract already promises that **every authored constraint usage stays visible with
exactly one disposition** (invariants 1 and 28). The exact route does not keep that promise.

On `catf_mfe_d5`, 65 authored constraint usages produce 9 catalog carriers. The other 56 are
absent — not eligible, not excluded, nothing. The cause is structural: records only begin *after*
owner-to-scope expansion (`_build_constraint_nodes`, `elaboration/elaborate.py:997`), and a usage
whose owner yields zero scopes emits nothing. 51 of the 56 are owned by a `calc def`, which
`_scopes_for_owner` has no branch for (`elaborate.py:522-539`); 5 are owned by a `part def` whose
design parts are all untyped.

Because every downstream artifact descends from that already-truncated set, a totality gate written
against today's data would compare two projections of the same truncation and pass. So this item
moves the birth point of the record upstream of expansion: totality becomes a property of *where
records are born*, not a check bolted on later.

Until that lands, Item 3's coverage denominator, Item 5's disposition table, and Item 6's calc-def
gate decision all rest on a population that silently lost 86% of its members.

## Implementation Strategy

**Phasing rationale.** Three forces set the order:

1. **De-risk what has never run.** Moving the mint upstream of expansion runs classification over
   usages that never reached an instance. Two things could take elaboration down model-wide: an
   owner kind the closed map does not know (invariant 8), and a predicate walk on a non-reaching
   usage (invariants 5 and B3). Phase 2 lands the attachment/owner-kind split alone, against the
   whole corpus, before any record exists — so if the corpus holds a surprise, it surfaces in the
   cheapest possible phase.
2. **The owner's documented sequence.** Documentation corrections and expected outputs land
   **before** confirmation tests run. So the oracle's expectation files and the doc/requirement-row
   rewrites (Phase 7) precede the confirmation run (Phase 8), and expectations are authored from
   `.sysml` source, never reverse-engineered from what the code produced.
3. **The five-step cross-repo landing order** (design, *Cross-Repo Landing Order*, rewritten in rev
   3). Codegen's half is self-sufficient and may land first; the **companion carries invariant 61's
   advisory half and is part of this item**, not a follow-up; docs land before the sweep is deleted;
   the recapture is the last **fixture-committing** step; TEAx re-vendors afterwards as a named
   hand-off.

**Critical path.**

```
P1 characterization + spike
 → P2 attachment cause split + owner-kind refusal      (riskiest, no new records yet)
 → P3 usage tier: form gate, mint, dispositions, validate()   (the domain exists; 65 ≠ 9 flips)
 → P4 @inapplicable annotation
 → P4C companion advisory (agentic-mbse worktree) + the codegen pin it forces   ← both repos
 → P5 codec v3 + fail-closed
 → P6 catalog re-key + CATALOG_SCHEMA_VERSION 3.0.0 + totality preflight
 → P7 oracle (31 expectation files + scanner) → doc/requirement-row rewrites → retire the sweep
 → P8 single reviewed recapture (21 fixtures) → confirmation tests on committed bytes → gates
```

**This item does not close on codegen alone.** Invariant 61 splits the vacuous-gate obligation
across two surfaces: codegen's fingerprinted `non_reaching` disposition (Phase 3) and the
companion's authoring advisory (Phase 4C). Codegen may land first — invariant 59 makes its
enforcement independent — but the window costs author feedback, and treating the codegen half as
discharging invariant 61 is precisely the narrowing O-1 caught. Completion criteria are in
[Completion Criteria (Both Repos)](#completion-criteria-both-repos).

**First proof point.** End of Phase 3: `catf_mfe_d5` elaborates to **65** usage-tier records with
exactly one disposition each, 9 of them `eligible`, and generation still succeeds. That is the
headline number, and it is reachable before the codec, the catalog, or the preflight exist.

**Overall validation approach.** Every phase starts with its tests, has a named gate that must be
green before the next phase begins, and states what we then know works. The full licensed suite runs
at the end of Phases 2, 3, 6, and 8; the focused tests run every phase.

## What Does NOT Change

Check these at every phase gate — they are the fixed points the whole item is balanced on.

- **The frozen CATF twins' constraint syntax.** `catf_mfe_model` and `catf_mfe_d5` are not edited.
  The 65 carriers must appear with the fixtures exactly as authored, and `catf_mfe_d5` stays
  byte-reversal-pinned (`tests/.../test_d5_variants.py:29`).
- **`catf_mfe_d5` still generates**, with exactly 65 usage carriers (9 `eligible`) and no halt.
- **Generated baselines outside the recapture scope stay byte-identical.** Expect churn only from
  the catalog schema token, the widened/re-keyed `usage_records`, and `satisfy_reference` moving
  expanded satisfy rows (design, *Implementation Notes*). Anything else changing is a finding.
- **The four `all_satisfied` assertions in `tests/execution/`** — Item 3's, untouched.
- **BLOCK-halts-generation semantics for usages that DO expand** — `SI_CONSTRAINT_BLOCKED` inside
  the scope loop (`elaborate.py:1018-1029`) is unchanged.
- **The occurrence tier.** `ConstraintNode` gains nothing and loses nothing; `predicate_ir`
  authority stays there. Per-module generation, the report aggregator, name safety, and the same-IR
  guard all read `concrete_entries` and are untouched.
- **The companion repo** (`agentic-mbse`) — **one scoped change only**: the `vacuous_asserted_gate`
  advisory and its severity-map entry (D10, Phase 4C). The *domain* asks nothing of the companion —
  the cross-check at `elaborate.py:388-395` already forces a profile decision for every swept
  subtype. No other companion behavior moves.
- **Fixtures that carry no snapshot do not gain one** (D8).

## Plan-Owned Decisions

The design left three things to the plan. Decided here so the implementer does not re-open them.

- **PD1 — Expectation files: one per fixture, outside the fixture tree.** Path:
  `tests/expectations/constraint_population/<fixture_dir>.json`. One file per constraint-bearing
  fixture directory, not one consolidated file (a 31-fixture consolidated file makes every review
  diff a whole-corpus diff, and a per-fixture file is what the scanner's missing-file rule names).
  They live outside `tests/fixtures/` because the fixture directories are walked by the snapshot
  capture batch and the whole-tree portability tests; adding a non-model file inside them risks
  changing what those sweeps see.
- **PD2 — Diagnostic identities and wording.** Two new `ElaborationCode` members
  (`elaboration/diagnostics.py:10-27`) plus one advisory channel:
  - `SI_CONSTRAINT_UNATTACHED` — invariant 9 halt. Message shape:
    `constraint <usage_qn> (<declaration_id>) at <file>:<line> is asserted (<source_form>) but its
    owner <owner_qn> (<owner_kind>) provides no attachment: <reason_token>`. Names the usage **and
    the missing attachment**, as the spec requires. Also carries `classification_incomplete`.
  - `SI_CONSTRAINT_INCOMPLETE` — the totality/join refusal raised by `graph.validate()` and by
    `_preflight_constraint_totality`. Message shape:
    `constraint usage domain incomplete: <what> for <usage_qn> (<declaration_id>)`, where `<what>`
    is one of `no disposition`, `duplicate usage record`, `occurrence node joins no usage record`,
    `occurrence_count N disagrees with M nodes`, `catalog row joins no domain member`. Never a bare
    count mismatch.
  - **The codegen mint site emits no advisory at all** (rev 3 / D10, correcting this plan's earlier
    `logger.warning` routing, which O-1 named as the same narrowing one stage on). Codegen's half of
    invariant 61 is the fingerprinted record field `disposition.severity == "warning"` on a
    `non_reaching` / `owner_has_no_occurrences` record — that is what travels, what Item 3 reads,
    and what is route-invariant. The author-facing advisory is the companion's, as an `ADVISORY`
    extraction diagnostic (Phase 4C), rendered by codegen's existing sink. Do not add a codegen log
    line at the mint site: it is not the advisory, and building it invites the same "invariant 61 is
    satisfied" misreading. There is no warning severity on codegen's `Diagnostic` anyway (every
    graph diagnostic is blocking via `ElaborationDiagnosticError`), so `self._diagnose` is also
    wrong for this.
- **PD3 — Doc line anchors are re-located, never trusted.** The design's anchors
  (`modeling-assumptions.md:476-477`, `:489-496`, `01-extraction.md:20`,
  `verification-matrix.md:336`, `:214`) were taken at `ccf4c21` and earlier edits in the same file
  shift the later ones. Re-`grep` for the quoted text before each edit and record the actual line in
  `verification.md`.
- **PD4 — SURFACED: "codegen-side work is zero" is not quite true, and the two repos are not as
  loosely coupled as landing-order step 2 says.** Checked against in-tree authority, not assumed.
  `docs/architecture/reference/30-diagnostic-severity.md` is explicit that adding an entry to
  `EXTRACTION_DIAGNOSTIC_SEVERITY` "is a semantic change to snapshots already on disk. It therefore
  requires bumping `CONSTRAINT_FACTS_SCHEMA_VERSION`" (`agentic-mbse constraint_facts.py:54`,
  currently `constraint-facts/v2`). Codegen **pins that string** at `src/sysml_codegen/
  _upstream_pins.py:38`, and `tests/conformance/test_upstream_pins.py:27-33` compares the pin
  against the value imported from the **installed** companion. The dev environment installs the
  companion editable from the companion worktree, so the moment Phase 4C bumps the companion
  constant, the codegen suite goes red until the pin is updated.

  Consequences, carried into the phases rather than left as a note:
  1. Codegen-side work for the advisory is **one line plus its pin test**, not zero. It is in Phase
     4C's checklist, on the codegen side of the phase.
  2. "Order between the two repos is free" holds for *enforcement* (invariant 59) but **not for a
     green suite**: the companion bump and the codegen pin update must land in the same window, or
     every codegen run in between fails `test_upstream_pins.py`. Sequence within Phase 4C: companion
     change → codegen pin → both suites.
  3. Doc 30 itself becomes stale on landing — its severity table lists exactly one kind, and its
     REQ-DIAG-03 row says "both pins are synthetic because the writer table has no ADVISORY kind
     today." This item creates the first real `ADVISORY` kind. Both edits are added to the Phase 7b
     documentation set.

  None of this changes a design decision; it adds work the design's "codegen-side work: none" would
  have let the implementer miss.
- **PD5 — Companion seam anchors are UNVERIFIED from this session, and must be confirmed before
  editing.** The companion worktree `/home/reid/1cfe/agentic-mbse-item7-rebuild` is outside this
  session's allowed working directory; every read of it was refused, so this plan could not check
  the design's line anchors any more than the design session could. What *is* checked, in-tree:
  - The **symbols** are real and codegen imports them today — `DiagnosticSeverity`,
    `ExtractionDiagnosticFact`, `ConstraintFacts` from `agentic_mbse.sysml.constraint_facts`
    (`src/sysml_codegen/elaboration/extraction_screen.py:25-32`), and
    `CONSTRAINT_FACTS_SCHEMA_VERSION` (`tests/conformance/test_upstream_pins.py:12`).
  - The **shape** is corroborated by `docs/architecture/reference/30-diagnostic-severity.md`, which
    cites `DiagnosticSeverity` at `constraint_facts.py:57-68`, the closed
    `EXTRACTION_DIAGNOSTIC_SEVERITY` map at `:78-82`, `severity_for_kind` at `:78-95`, the
    `__post_init__` severity assignment at `:230-233`, and the schema constant at `:54` — the same
    anchors the design cites, at companion merged main `f4ebdce`.

  So the anchors are second-hand but doubly sourced. Phase 4C step C0 re-confirms them against the
  companion worktree HEAD **before** any edit; if they have moved, fix the anchors in the phase and
  record the correction — the seam and the decision stand either way, only the line numbers are at
  risk.

---

## Phase 1: Characterization + De-Risk Spike

### Goal

Reproduce the failure as a test that stays in the tree, and confirm the one behavior the design
depends on but has not observed (`@inapplicable:` doc-comment reachability at elaboration). Nothing
in `src/` changes.

### Assumption Under Test

That a `ConstraintUsage`'s documentation is reachable during elaboration the way it is at extraction
(`extraction/extractor.py:803-814`), and that the multi-comment join behaves as the design's
Implementation Notes assume. If it does not, D2's mechanism needs rework before any code is written.

### Test Stencil (Write This First)

```python
# tests/conformance/test_constraint_usage_domain_totality.py  (NEW)
# RED on purpose until Phase 3. Do not weaken it to make the tree green.

def test_catf_mfe_d5_authored_population_is_total(catf_mfe_d5_graph):
    """65 authored usages → 65 domain members. Today: 9 carriers, 56 absences."""
    records = catf_mfe_d5_graph.constraint_usages          # does not exist yet
    assert len(records) == 65
    assert sum(1 for r in records.values()
               if r.disposition.kind == "eligible") == 9
```

### Changes Required

**See design.md for:** *The Point* / *Research Findings* (the 65→9 measurement and its cause),
*De-risk first* (the spike's two questions).

- [x] Create `tests/conformance/test_constraint_usage_domain_totality.py` with the stencil above.
      Run it; record the exact failure mode (attribute absent) in the plan's Implementation Notes.
      **It stays failing through Phases 1–2.**
- [x] Run `/_my_spike` on one annotated fixture: add a `/* @inapplicable: reason */` doc comment to
      a scratch copy of a constraint usage, and confirm at elaboration (a) the comment body is
      reachable from the `ConstraintUsage` element, (b) `.strip().strip("*").strip()` + `\n`-join
      reproduces the extraction-side shape, (c) a second comment body lands on a later line of the
      join. Record the answers in `verification.md`.
- [x] Re-measure and record: constraint-bearing fixture directories (design says 31 at `ccf4c21`),
      snapshot-bearing fixture directories (design says 21). These are counts recorded at execution,
      not targets.

### Validation

**Automated:**
- [x] `uv run --extra dev pytest tests/conformance/test_constraint_usage_domain_totality.py` → fails
      for the expected reason (no `constraint_usages` on the graph), not an import or fixture error.

**Manual:**
- [x] Spike answers recorded. If (a) is false, **STOP and surface it** — D2's mechanism assumption
      is broken and the design has to move before Phase 4.

**What We Know Works After This Phase:** the failure is reproduced by a test that will fail again if
it ever regresses, and D2's only unobserved dependency is either confirmed or surfaced.

---

## Phase 2: Attachment Cause Split + Owner-Kind Refusal

### Goal

Make emptiness explain itself (`_attachment(owner) -> (scopes, cause)`) and turn the owner-kind
map's silent fallback into a refusal (invariant 8). Land it against the whole corpus **before** any
record depends on it.

### Why now

This is the riskiest change per unit of code. The owner-kind refusal can fail elaboration on any
corpus model with an unmapped owner kind, and the cause split is what the whole severity rule keys
on (B2). Both are cheap to revert here and expensive to unpick in Phase 3.

### Assumption Under Test

B2 — that emptiness decomposes into exactly three causes (`owner_absent`,
`owner_kind_unattachable`, `owner_has_no_occurrences`) — and that no corpus fixture carries a
constraint owner kind outside the closed map.

### Test Stencil (Write This First)

```python
# tests/unit/test_constraint_attachment_cause.py  (NEW)
def test_attachment_reports_cause_for_each_empty_shape(elaborator):
    assert elaborator._attachment(None) == ((), "owner_absent")
    assert elaborator._attachment(calc_def_owner)[1] == "owner_kind_unattachable"
    assert elaborator._attachment(untyped_part_def)[1] == "owner_has_no_occurrences"
    assert elaborator._attachment(occupied_part_def)[0]        # non-empty, cause None

def test_unmapped_owner_kind_refuses_by_name(elaborator):
    with pytest.raises(ElaborationInvariantError, match="owner kind"):
        elaborator._owner_kind(SomeUnmappedOwner())
```

### Changes Required

**See design.md for:** *Component Overview* (`_attachment`), *Required Invariants* 8, *Potential
Risks* (cause mis-split).

- [x] `elaboration/elaborate.py:522-539` — replace `_scopes_for_owner` with `_attachment(owner)`
      returning `(scopes, cause)`; `cause` is `None` when scopes are non-empty. Update the one call
      site at `:1004`.
- [x] `elaboration/elaborate.py:1177-1182` — the owner-kind map's `.get(..., type(owner).__name__
      .lower())` fallback becomes a refusal naming the unmapped kind. Extract it as `_owner_kind`
      so the mint and `_constraint_metadata` share one authority.
- [x] `elaboration/diagnostics.py` — add `SI_CONSTRAINT_UNATTACHED` and `SI_CONSTRAINT_INCOMPLETE`
      (PD2); nothing raises `SI_CONSTRAINT_INCOMPLETE` until Phase 3.

### Validation

**Automated:**
- [x] Focused: `pytest tests/unit/test_constraint_attachment_cause.py` → pass.
- [x] **Full licensed suite** (`set -a; source /home/reid/1cfe/agentic-mbse/.env; set +a`) → no new
      failures, **zero license-skip lines**. This is the phase where an unmapped owner kind in the
      corpus would appear.
- [x] `ruff check src/` and `mypy src/` → zero new.

**Manual:**
- [x] Confirm no generated baseline moved (`git status` on `tests/fixtures/`, baseline dirs clean).

**What We Know Works After This Phase:** every empty attachment carries its reason, no owner kind is
graded by accident, and the corpus contains no owner kind outside the closed map.

---

## Phase 3: The Usage Tier — Form Gate, Mint, Dispositions, `validate()`

### Goal

The domain exists. One `ConstraintUsageRecord` per authored `ConstraintUsage`, minted pre-expansion
inside the existing loop (D9), each with exactly one disposition from the precedence rule, with
per-record structure asserted in `graph.validate()`.

### Assumption Under Test

B1 (the pre-expansion sweep sees every authored usage), B3 (form classification is total and cannot
raise), and B5 (the severity rule leaves `catf_mfe_d5` generating). This is the phase where the
headline flips.

### Test Stencil (Write This First)

```python
# tests/unit/test_constraint_usage_record_mint.py  (NEW)
def test_mint_never_raises_for_non_asserted_form(plain_usage_with_unrepresentable_predicate):
    """Form gate runs BEFORE the predicate walk — invariant 5, not catf_mfe_d5's luck."""
    graph = elaborate(model)                       # must not raise SI_REDEFINITION_INVALID
    record = graph.constraint_usages[decl_id]
    assert record.disposition.kind == "excluded"
    assert record.disposition.reason == "unassessed_form"

def test_precedence_satisfy_owned_by_calc_def_is_step_one(model):
    record = elaborate(model).constraint_usages[decl_id]
    assert (record.disposition.kind, record.disposition.reason) == (
        "excluded", "out_of_scope_satisfy")      # not non_reaching — step 1 wins
```

### Changes Required

**See design.md for:** *Core Concept*, D1 / D5 / D9, the **Token Vocabulary** section (the ordered
precedence rule and the full disposition table — implement it exactly, in that order), *Required
Invariants* 1, 2, 3, 5, 6, 7, *Component Overview*.

- [x] `elaboration/graph.py` — add `UsageDisposition`, `Inapplicability` (field only for now, always
      `None` until Phase 4), `ConstraintUsageRecord` with the field list from the design's Component
      Overview, and `InstanceGraph.constraint_usages: dict[DeclarationId, ConstraintUsageRecord]`.
- [x] `elaboration/elaborate.py:1119-1224` — split `_constraint_metadata` so the form/identity half
      is callable without the predicate-IR and definition-identity half. Add the sixth source form
      `satisfy_reference`, tested **before** the `plain_usage` fall-through (`:1136-1137`).
- [x] `elaboration/elaborate.py:997-1004` — mint the record at the top of the per-usage loop, before
      the scope loop; the scope loop's `ConstraintNode`s take form and identity from the record. Set
      `occurrence_count` after the scope loop.
- [x] Same file — implement the precedence rule (form gate → expansion cause → profile eligibility)
      as one function returning a `UsageDisposition`, and the severity derivation (asserted forms are
      `definition_typed`, `inline`, `named_usage_reference`; no non-asserted form ever yields
      `error`).
- [x] Same file — invariant 1: assert `graph.constraint_usages` keys equal
      `self._constraint_associations` keys, where both are in scope.
- [x] Same file — the invariant-9 halt (`SI_CONSTRAINT_UNATTACHED`) for `error`-severity
      dispositions. **No advisory is emitted here** (PD2): the `warning` severity on the record is
      codegen's entire half of invariant 61; the author-facing advisory is Phase 4C's, in the
      companion.
- [x] `elaboration/graph.py:246+` (`validate()`) — invariant 2 (exactly one disposition, closed
      vocabulary, severity matches the table) and invariant 3 (join both directions by
      `declaration_id`; `eligible` with `occurrence_count == 0` fails), raising
      `SI_CONSTRAINT_INCOMPLETE`.

**New fixtures** (all under `tests/fixtures/`, all needing an expectation file in Phase 7):
- [x] `plain_usage` whose predicate would raise `SI_REDEFINITION_INVALID` if walked (invariant 5).
- [x] Asserted usage owned by a `calc def` → halts, diagnostic names usage + missing attachment.
- [x] Asserted usage on a detached (zero-occurrence) part def → warning-grade `non_reaching` /
      `owner_has_no_occurrences`, generation continues. (The *advisory* on this same fixture is
      asserted in Phase 4C, companion-side.)
- [x] **Containment fixture** (invariant 9, used by Phase 4C): a part def that **is** typed by a
      part usage which is itself never instantiated. Codegen must grade it
      `owner_has_no_occurrences`; the companion must stay silent on it. Build it here, assert the
      codegen half here, assert the companion half in 4C.
- [x] Plain constraint whose predicate would BLOCK if asserted → generates, `excluded` /
      `unassessed_form`.
- [x] `satisfy` owned by a `calc def` → `out_of_scope_satisfy` (precedence step 1).
- [x] `BLOCK`-decision usage reaching no instance → `non_reaching`, **no** `SI_CONSTRAINT_BLOCKED`.

### Validation

**Automated:**
- [x] Phase 1's characterization test now **passes**: 65 records, 9 `eligible`, on `catf_mfe_d5`.
- [x] Focused: mint, precedence, severity-by-cause, non-raising-mint tests → pass.
- [x] **Full licensed suite** → no new failures, zero license-skip lines. Snapshot round-trip tests
      still pass (the tier is not yet in the codec, so snapshot-loaded graphs have an empty domain —
      if `validate()` refuses that, Phase 5 has to move up; record it).
- [x] `ruff`/`mypy` zero-new.

**Manual:**
- [x] `catf_mfe_d5` generates end to end and both twins stay byte-pinned.

**What We Know Works After This Phase:** the domain is complete by construction on the live route,
the precedence rule resolves the co-firing cases, minting does not raise for non-asserted forms, and
the headline 65 is real.

---

## Phase 4: `@inapplicable:` Annotation (D2)

### Goal

An explicit, fingerprinted inapplicability decision carried on the usage record, read once at
elaboration, never re-read downstream.

### Assumption Under Test

That the strict parse fails closed on a near-miss (invariant 6: carrying an `Inapplicability` never
rewrites kind, reason, or severity — including for the halting case).

### Test Stencil (Write This First)

```python
def test_inapplicable_annotation_does_not_rewrite_disposition(annotated_vacuous_gate):
    record = elaborate(model).constraint_usages[decl_id]
    assert record.inapplicability is not None
    assert (record.disposition.kind, record.disposition.reason,
            record.disposition.severity) == ("non_reaching", "owner_has_no_occurrences", "warning")

def test_malformed_annotation_halts(model_with_typo_marker):    # "@inapplicable" with no ": reason"
    with pytest.raises(ElaborationInvariantError):
        elaborate(model)
```

### Changes Required

**See design.md for:** D2, *Required Invariants* 6, *Implementation Notes* (the parse is defined
against the `_extract_documentation` seam, not against "the doc comment"), *Potential Risks*.

- [x] `elaboration/elaborate.py` — read the usage's joined documentation at mint time; parse a first
      line matching exactly `@inapplicable: <reason>`; record an `Inapplicability` on the record.
- [x] Halt cases: a first line beginning `@inapplicable` that does not match the shape; the marker
      appearing on a **later** comment body of the join. Both are named halts, never no-ops.
- [x] Fixtures: an annotated vacuous asserted gate; a malformed annotation; a later-comment marker.
- [x] Confirm an annotated asserted **unattachable** gate still halts (invariant 6 — marking it does
      not suppress invariant 9).

### Validation

**Automated:**
- [x] Focused annotation tests pass, including both halt shapes.
- [x] The annotation's presence moves the graph fingerprint (assert on the fingerprint before/after).
- [x] `ruff`/`mypy` zero-new.

**What We Know Works After This Phase:** inapplicability is explicit, fingerprinted, and structurally
incapable of changing an asserted usage's coverage role.

---

## Phase 4C: The Companion Advisory (invariant 61's other half)

**Repo:** `/home/reid/1cfe/agentic-mbse-item7-rebuild` (companion), plus one pinned line in codegen.

### Goal

Land the `vacuous_asserted_gate` advisory as an `ADVISORY` `ExtractionDiagnosticFact` in the
companion's authoring-validation channel, so an author gets feedback at authoring time — the half of
invariant 61 that codegen's disposition does not discharge (D10, O-1).

### Why now

It needs Phase 3's vacuous fixtures to test against, and it is independent of the codec, catalog,
and preflight work in Phases 5–6. Landing it here keeps the two halves close together rather than
letting the codegen half "finish" alone, which is the failure mode O-1 named.

### Assumption Under Test

That the seam is exactly what the design says (PD5 — anchors are second-hand), that adding a kind
costs a companion schema-version bump plus a codegen pin and nothing more (PD4), and invariant 9's
containment direction: the companion's structural trigger is a **strict subset** of codegen's
vacuous set, so the advisory can only ever be missing, never false.

### Test Stencil (Write This First)

```python
# companion: tests/.../test_vacuous_asserted_gate_advisory.py  (NEW)
def test_vacuous_asserted_gate_emits_one_advisory(detached_owner_model):
    facts = extract_constraint_facts(detached_owner_model)
    (diag,) = [d for d in facts.diagnostics if d.kind == "vacuous_asserted_gate"]
    assert diag.severity is DiagnosticSeverity.ADVISORY      # writer-side map, never author-supplied
    assert USAGE_QN in diag.message and OWNER_QN in diag.message
    assert diag.location is not None                          # renderer prints file:line:column

def test_companion_trigger_is_a_subset_of_codegen_vacuous(typed_but_never_instantiated_model):
    """Invariant 9: silence here is CORRECT — codegen still grades it vacuous."""
    facts = extract_constraint_facts(typed_but_never_instantiated_model)
    assert not [d for d in facts.diagnostics if d.kind == "vacuous_asserted_gate"]

# codegen: tests/conformance/test_extraction_diagnostic_screen.py  (EXTEND)
def test_sink_renders_new_advisory_kind_without_halting(caplog, facts_with_vacuous_advisory):
    screen_extraction_diagnostics(facts)                      # must not raise
    assert "vacuous_asserted_gate" in caplog.text             # warning grade, generation continues

def test_disposition_is_identical_with_the_advisory_suppressed(model):
    """Invariant 59 independence: codegen does not consult the advisory."""
    assert elaborate(model).constraint_usages == elaborate(model, advisories_suppressed=True).constraint_usages
```

### Changes Required

**See design.md for:** D10, **The Companion Advisory** section (where / grade / message / trigger /
why the two sets cannot be equal), *Required Invariants* 9, *Potential Risks* (advisory reach,
two-repos-one-obligation).

**C0 — Confirm the seam before editing (PD5).** This plan could not read the companion worktree.
- [x] Open `agentic_mbse/sysml/constraint_facts.py` in the companion worktree and confirm:
      `DiagnosticSeverity` (BLOCKING | ADVISORY, design cites `:57-68`); the closed
      `EXTRACTION_DIAGNOSTIC_SEVERITY` map (`:78-82`) and `severity_for_kind` (`:78-95`);
      `ExtractionDiagnosticFact` with `severity: field(init=False)` set in `__post_init__`
      (`:230-233`); `CONSTRAINT_FACTS_SCHEMA_VERSION` (`:54`, expected `constraint-facts/v2`).
- [x] If any anchor has moved, **record the correction in the Implementation Notes and proceed** —
      the seam and D10 stand; only line numbers were second-hand. If a *mechanism* differs (e.g.
      severity is no longer writer-side), STOP and surface it: D10 rests on that.

**C1 — Companion change:**
- [x] Add the diagnostic kind `vacuous_asserted_gate` with an `ADVISORY` entry in
      `EXTRACTION_DIAGNOSTIC_SEVERITY`. Severity stays writer-side; no reader-side table appears
      anywhere (REQ-DIAG-01).
- [x] Emit it from the companion's constraint validation on the structural trigger: **an asserted
      constraint usage whose owning `part def` is typed by zero part usages in the model.** Do not
      reach for occurrences — the companion has no occurrence index, and reimplementing one is the
      second-representation smell this item removes.
- [x] Message names the usage qualified name **and** the detached owner qualified name; `location`
      carries the usage's source position so codegen's `_render` prints `file:line:column`.
- [x] Bump `CONSTRAINT_FACTS_SCHEMA_VERSION` `constraint-facts/v2` → `constraint-facts/v3` — adding
      a kind to the closed map requires it (`docs/architecture/reference/30-diagnostic-severity.md`,
      "The severity type / Severity is set by the writer").
- [x] Companion tests: emission + grade on the vacuous fixture; the containment case stays silent;
      the map stays closed.

**C2 — Codegen side (small, but not zero — PD4):**
- [x] `src/sysml_codegen/_upstream_pins.py:38` — pin `constraint-facts/v3`. Land it in the same
      window as C1, or `tests/conformance/test_upstream_pins.py` fails on every codegen run in
      between (it compares against the *installed* companion, which is the editable worktree).
- [x] Extend `tests/conformance/test_extraction_diagnostic_screen.py` with the assertion that the
      **existing** sink (`elaboration/extraction_screen.py:56-73`) renders the new kind at warning
      grade and does not halt. This is an assertion about behavior we did not write, which is the
      point of routing the advisory here — no sink change.
- [x] Independence check (invariant 59): codegen's disposition for the vacuous fixture is
      byte-identical with the advisory present and suppressed.

### Validation

**Automated:**
- [x] Companion focused tests pass, run **in the companion worktree**
      (`/home/reid/1cfe/agentic-mbse-item7-rebuild`) with the license sourced.
- [x] Codegen: `test_upstream_pins.py` green (pin matches the bumped companion), extended screen
      test green, independence check green.
- [x] `ruff`/`mypy` zero-new **in both repos**.

**Manual:**
- [x] Run codegen on the vacuous fixture and read the log: one warning line naming the usage and the
      detached owner, with `file:line:column`, and generation completes.

**What We Know Works After This Phase:** invariant 61 has both halves — a fingerprinted disposition
that travels, and an author-time advisory that does not — the advisory can only under-fire, never
over-fire, and codegen's grading does not consult it.

---

## Phase 5: Codec v3 + Fail-Closed

### Goal

The tier travels. `instance-graph/v2` → `v3`, `constraint_usages` in the graph key set, no v2 reader.

### Assumption Under Test

That fail-closed needs no new code — the existing exact version comparison
(`snapshot/instance_graph.py:927-932`) and exact key-set check (`:933-937`) already refuse both bad
shapes.

### Test Stencil (Write This First)

```python
def test_v2_payload_fails_closed(v2_snapshot_bytes):
    with pytest.raises(SnapshotError, match="instance-graph/v3"):
        decode_instance_graph(v2_snapshot_bytes)

def test_v3_missing_constraint_usages_fails_closed(v3_bytes_without_tier):
    with pytest.raises(SnapshotError):
        decode_instance_graph(v3_bytes_without_tier)
```

### Changes Required

**See design.md for:** D4, *Research Findings* (the codec is exact-match on both version and key
set), *Architecture*.

- [x] `snapshot/instance_graph.py:68` — `INSTANCE_GRAPH_SCHEMA_VERSION = "instance-graph/v3"`.
- [x] `:893-908` encode + `:933-982` decode — carry `constraint_usages`; add it to the exact graph
      key set at `:936`. Round-trip must preserve every record field, disposition, and
      inapplicability.
- [x] Fail-closed tests build their payloads in memory / a temp dir. **No committed fixture bytes
      are touched in this phase** — the recapture is Phase 8.
- [x] Three-route parity test (live vs in-place snapshot vs relocated snapshot), asserting the
      domain **field for field, record for record**, on a fixture carrying `@inapplicable:`
      annotations. During this phase it captures to a temp directory; its committed-fixture form
      runs in Phase 8.

### Validation

**Automated:**
- [x] Focused codec tests pass; parity passes against temp-dir snapshots.
- [x] Full suite: snapshot-consuming tests that read **committed v2 fixtures now fail by design**.
      List them and confirm every failure is a v2-version refusal, not a logic error. They go green
      at Phase 8's recapture. Record the list in `verification.md`.
- [x] `ruff`/`mypy` zero-new.

**What We Know Works After This Phase:** the tier survives a round trip field for field, live and
snapshot agree including the live-only annotation read, and both malformed shapes fail closed.

---

## Phase 6: Catalog Totality + The Fifth Preflight

### Goal

`catalog.usage_records` becomes the whole domain, keyed by `declaration_id`, and the domain ↔
catalog ↔ entry join is gated at the fail-before-mutate boundary.

### Assumption Under Test

That a `ConstraintCatalog` with `usage_records` populated and `concrete_entries` / `source_records`
empty constructs and fingerprints deterministically — a combination that has never existed
(design, *Implementation Notes*).

### Test Stencil (Write This First)

```python
def test_calc_def_only_model_still_gets_a_catalog(calc_def_only_graph):
    catalog = project(graph).constraint_catalog
    assert catalog is not None                       # None only when the DOMAIN is empty
    assert catalog.usage_records and not catalog.concrete_entries

def test_preflight_names_the_usage_on_a_misjoin(graph):
    graph.constraint_usages[a].declaration_id = other_decl_id     # mutate the GRAPH, not bytes
    with pytest.raises(CodeGenerationError, match=str(a)):
        _generate_package_from_graph(...)
```

### Changes Required

**See design.md for:** D1 (catalog re-key), D3 (gate home), *Required Invariants* 3 and 4,
*Implementation Notes* (`CATALOG_SCHEMA_VERSION`, "mutate the graph, not the bytes").

- [ ] `resolution/models.py:474-503` — `ConstraintCatalogUsageRecord` gains `declaration_id` (the new
      identity and dedup key), `disposition`, `inapplicability`; docstring updated from
      "admitted (eligible)" to the whole domain.
- [ ] `elaboration/project.py:1084-1146` — `_build_constraint_catalog` renders every domain member;
      dict keyed on `declaration_id`, replacing the `(usage_qualified_name, display_name)` pair at
      `:1145-1146`; the `None` return at `:1084-1085` keys on the **domain** being empty, not
      `graph.constraints`.
- [ ] `contracts/versions.py:18` — `CATALOG_SCHEMA_VERSION = "3.0.0"`, docstring saying what broke
      (population widened, key changed) and how a consumer recovers the old set
      (`disposition.kind == "eligible"`). Update the pin in
      `tests/conformance/test_catalog_schema_version.py:19`.
- [ ] `cli/__init__.py:1064-1079` — add `_preflight_constraint_totality(graph)` as step 1.8, beside
      1.5–1.7, **before** `_clear_output_directory`. Join by `declaration_id` only; refuse, never
      repair.
- [ ] Mutation tests: remove a disposition, duplicate a usage record, misjoin one — each at the
      in-memory graph level, each failing generation with a diagnostic naming the declaration id and
      QN.

### Validation

**Automated:**
- [ ] Focused: catalog totality, catalog constructibility, three mutation shapes, schema-version pin.
- [ ] **Full licensed suite** → baseline churn appears here. Every moved baseline must be explained
      by exactly one of: the catalog schema token, the widened/re-keyed `usage_records`, or
      `satisfy_reference` moving an expanded satisfy row. Anything else is a finding — stop and
      investigate.
- [ ] `ruff`/`mypy` zero-new.

**Manual:**
- [ ] `catf_mfe_d5` generates; its catalog carries 65 usage rows, 9 `eligible`.

**What We Know Works After This Phase:** the catalog is total, the join is checkable by identity end
to end, and a removed/duplicated/misjoined carrier fails generation by name before anything is
written.

---

## Phase 7: Oracle, Then Docs, Then Retirement — In That Order

### Goal

Stand up the independent totality oracle, correct the shipped documentation and requirement rows
against it, and only then delete the manifest sweep. The internal order is the owner's
docs-before-tests rule and landing-order step 3, and it is not negotiable.

### Assumption Under Test

That the expectation files, authored from `.sysml` source, agree with the domain — the one check in
this item that is **not** derived from the thing it checks.

### Test Stencil (Write This First)

```python
# tests/conformance/test_constraint_population_oracle.py  (NEW)
@pytest.mark.parametrize("fixture_dir", CONSTRAINT_BEARING_FIXTURES)
def test_domain_matches_reviewed_expectation(fixture_dir):
    expected = load_expectation(fixture_dir)          # identity LIST, not a count
    actual = [row_identity(r) for r in elaborate(fixture_dir).constraint_usages.values()]
    assert sorted(actual) == sorted(expected)

def test_every_constraint_bearing_fixture_has_an_expectation_file():
    missing = [d for d in scan_fixture_dirs() if declares_constraints(d) and not has_expectation(d)]
    assert not missing, f"no expectation file: {missing}"   # a gap is loud, never silent coverage
```

### Changes Required

**See design.md for:** D6, D7, the **Oracle Coverage** section (what a file holds, the scanner's
matching rule, the missing-file rule, the known false-positive/negative classes), *Implementation
Notes* (the documentation edit set).

**7a — Oracle (lands first):**
- [ ] Author one expectation file per constraint-bearing fixture directory at
      `tests/expectations/constraint_population/<fixture_dir>.json` (PD1). Rows: usage QN, display
      name, owner QN, source file, source line — **read from the `.sysml` source**, never dumped
      from the domain. `catf_mfe_d5` has 65 rows.
- [ ] License-free scanner: strip `//` and `/* … */` first, then match statement-initial
      `constraint`, `assert`, `require constraint`, `assume constraint`, `satisfy`, excluding
      `constraint def`. Emits keyword + name + line and compares to the expectation rows.
- [ ] The scanner walks **every** fixture directory; a constraint-bearing directory with no
      expectation file is a failure naming the directory.
- [ ] Document the scanner's known false-positive/negative classes in its module docstring, verbatim
      from the design's Oracle Coverage — and that when scanner and expectation file disagree, the
      expectation file is re-derived by hand from source.

**7b — Documentation and requirement rows (land before deletion; re-locate anchors per PD3):**
- [ ] `docs/architecture/modeling-assumptions.md` ~`:476-477` — drop the "today a usage that reaches
      no instance gets no carrier at all" parenthetical; state the disposition instead.
- [ ] Same file ~`:489-496` — replace the pending-proof paragraph and the
      `collect_constraint_manifest` population subject with the domain and the reviewed
      expected-population oracle.
- [ ] `docs/architecture/reference/01-extraction.md:20` — REQ-EXT-09 rewrite per D6: the domain is
      every `ConstraintUsage` **including** `RequirementUsage` and `satisfy`; the satisfy exclusion
      is a disposition *inside* the domain. The subject stops being "swept by
      `collect_constraint_manifest`"; the new evidence pointer names the oracle test.
- [ ] `docs/architecture/verification-matrix.md` ~`:336` — REQ-EXT-09 row + grade against the new
      evidence; ~`:214` — REQ-CL-04 row, PARTIAL note replaced by what the new tests prove.
- [ ] `docs/architecture/reference/30-diagnostic-severity.md` (added by PD4, stale on Phase 4C
      landing): add the `vacuous_asserted_gate` / ADVISORY row to the severity table, which
      currently lists exactly one kind; update the `CONSTRAINT_FACTS_SCHEMA_VERSION` value; and fix
      the REQ-DIAG-03 evidence note that says "both pins are synthetic because the writer table has
      no ADVISORY kind today" — this item creates the first real one, so the pins can cite it.
      Re-`grep` for "synthetic" and for `constraint-facts/v2` across `docs/` to catch every copy.

**7c — Retirement (only after 7b is committed):**
- [ ] Delete `collect_constraint_manifest`, `_classify_constraint_kind`, `_constraint_owner_kind`
      (`extraction/extractor.py:98-139`), `ConstraintManifestEntry`, `ConstraintKind`
      (`extraction/constraint_report.py`), and the 7 call sites in
      `tests/conformance/test_extractor.py`.
- [ ] Grep the tree for remaining references (docs included) → zero.

### Validation

**Automated:**
- [ ] Oracle suite green across all constraint-bearing fixtures, including the new Phase 3/4
      fixtures.
- [ ] Missing-file rule proven: temporarily rename one expectation file → the suite fails naming
      that directory. Restore.
- [ ] Post-deletion: full suite green, `ruff`/`mypy` zero-new.

**Manual:**
- [ ] Confirm the doc commit precedes the deletion commit (`git log --oneline`) — landing-order
      step 3.
- [ ] Spot-check three expectation files against their `.sysml` source by hand.

**What We Know Works After This Phase:** totality is proven against evidence that does not descend
from the domain, every shipped row cites a live test, and nothing dead is stranded.

---

## Phase 8: Single Reviewed Recapture, Confirmation, and Gates

### Goal

Capture the 21 snapshot-bearing fixtures once at the final schema, run the confirmation tests
against those committed bytes, and record every count.

### Assumption Under Test

That the schema is settled — a second recapture is what the Item 7 register forbids. Do not enter
this phase with any open schema question from Phases 3–6.

### Test Stencil (Write This First)

```python
# committed-fixture forms of the Phase 5 tests
def test_three_route_parity_on_committed_snapshot(fixture_with_annotations):
    live = elaborate(fixture).constraint_usages
    inplace = load_snapshot(fixture / "instance_graph_snapshot.json").constraint_usages
    relocated = load_snapshot(copy_to_tmp(fixture)).constraint_usages
    assert live == inplace == relocated          # field for field, record for record
```

### Changes Required

**See design.md for:** D8 (21, not 37), *Implementation Notes* (recapture protocol), *Cross-Repo
Landing Order* steps 4 and 5, the Item 7 evidence-invalidation register entries.

- [ ] Recapture with `scripts/capture_v6_batch.py` across every snapshot-bearing fixture. Record the
      actual count (expected 21).
- [ ] **Timestamp-churn protocol:** diff every changed fixture; revert the ones whose only change is
      `captured_at`. What remains must be the schema token plus `constraint_usages`.
- [ ] Point the Phase 5 parity and fail-closed tests at the committed bytes; the v2 fail-closed test
      keeps a synthetic v2 payload (there is no committed v2 fixture left to read).
- [ ] Add the Item 7 evidence-invalidation register entries to
      `.project/backlog/epic_constraint_semantics_contract.md` (or the register's home): paused Item
      7 snapshot-route observations taken against v2 bytes; byte-identity comparisons on the 21
      recaptured fixtures; any Item 7 evidence citing `collect_constraint_manifest` as the
      population definition.
- [ ] **HAND-OFF (not work this item performs):** record in the epic's cross-repo notes that TEAx
      must re-vendor `ACCEPTED_CATALOG_SCHEMA_VERSIONS` to include `3.0.0` **after** this repo
      lands. B3 forbids TEAx importing this repo, so nothing here can enforce it. **While it is
      pending, TEAx fails closed on every newly generated package** — loudly, which is the intended
      direction. Do not bump TEAx first: that makes TEAx accept a schema no generator produces.

### Validation — the final gates, named

- [ ] Focused tests: totality, mint/precedence, severity-by-cause, non-raising mint, annotation,
      mutation ×3, codec fail-closed ×2, three-route parity, catalog constructibility, oracle,
      companion advisory (emission + grade), containment direction, independence, upstream pin.
- [ ] **Full licensed codegen suite**, run in `/home/reid/1cfe/sysml-codegen-item7-rebuild`:
      `set -a; source /home/reid/1cfe/agentic-mbse/.env; set +a` then
      `uv run --extra dev pytest tests/` → green, and **verify zero license-skip lines** (a green
      run with skips is not a full run).
- [ ] **Full licensed companion suite, run in the companion worktree**
      `/home/reid/1cfe/agentic-mbse-item7-rebuild` (not in this repo, and not against the
      `/home/reid/1cfe/agentic-mbse` main checkout) — same license sourcing, green, zero
      license-skip lines. The companion now carries the Phase 4C change, so this run is load-bearing
      evidence, not a formality.
- [ ] `ruff check src/` → zero new. `mypy src/` → zero new.
- [ ] Fixture diff review complete under the timestamp-churn protocol.
- [ ] `git diff --check` clean.
- [ ] `verification.md` written with **exact counts**: usage carriers on `catf_mfe_d5` (65) and
      `eligible` among them (9); constraint-bearing fixture count (re-measured); expectation-file
      count; recapture count (expected 21); focused/full test counts; ruff and mypy before/after;
      the doc line anchors actually edited (PD3); the Phase 5 v2-refusal list, now resolved; the
      companion commit SHA for Phase 4C and the `constraint-facts` version on both sides of the pin.

**What We Know Works After This Phase:** codegen's half is complete — live, in-place snapshot, and
relocated snapshot agree on the domain; old shapes fail closed; the requirement rows cite evidence
that fails if a pre-expansion usage vanishes. Closing the **item** also needs Phase 4C landed in the
companion; see below.

---

## Completion Criteria (Both Repos)

The item is done when all of these hold. Codegen may land first; it does not close alone.

**sysml-codegen (`item7-rebuild`):**
- [ ] `catf_mfe_d5`: 65 usage carriers, 9 `eligible`, generation succeeds, both twins byte-pinned.
- [ ] Domain minted pre-expansion, one disposition each, join checkable by `declaration_id` end to
      end, gated at the fail-before-mutate boundary.
- [ ] v3 codec, catalog `3.0.0`, single reviewed recapture, oracle over every constraint-bearing
      fixture, doc + requirement rows corrected, manifest sweep retired.
- [ ] `_upstream_pins.py` matches the companion's bumped `CONSTRAINT_FACTS_SCHEMA_VERSION` (PD4).
- [ ] All gates above green, counts in `verification.md`.

**agentic-mbse (`agentic-mbse-item7-rebuild`):**
- [ ] `vacuous_asserted_gate` emitted at `ADVISORY` grade, naming usage and detached owner, with a
      location; severity writer-side in the closed map; schema version bumped; companion tests and
      full licensed companion suite green.

**Spanning both:**
- [ ] Invariant 61 has both halves — the fingerprinted disposition and the authoring advisory.
      Codegen's disposition alone does **not** discharge it (O-1).
- [ ] Invariant 9's containment direction proven: companion trigger set ⊆ codegen vacuous set.
- [ ] Invariant 59 independence proven: codegen's disposition is identical with the advisory
      suppressed.

**Deliberately outside the item, tracked as hand-offs:** TEAx's `ACCEPTED_CATALOG_SCHEMA_VERSIONS`
re-vendor (landing-order step 5), and the residual invariant-9 gap — a vacuous gate whose owning
part def is typed by a never-instantiated usage gets codegen's disposition and no author advisory.
That residual is accepted by design, not a defect to fix here.

---

## Environment Setup

**See CLAUDE.md.** Two things bite in this item specifically: licensed runs need
`set -a; source /home/reid/1cfe/agentic-mbse/.env; set +a` (there is no `.env` in this repo, and a
missing key silently degrades the suite into a fake baseline), and generated baselines / fixture
snapshots are **format-exempt** — never `ruff format` them; byte-identity gates depend on those
bytes.

**Two worktrees.** Codegen work is in `/home/reid/1cfe/sysml-codegen-item7-rebuild`; Phase 4C's
companion work and the companion suite run in `/home/reid/1cfe/agentic-mbse-item7-rebuild` — the
paired worktree, not the `/home/reid/1cfe/agentic-mbse` main checkout (which is only where the
licence `.env` is read from). The companion is installed editable, so a companion edit is live in
the codegen suite immediately — that is what makes the PD4 pin window real.

## Risk Management

**See `design.md#potential-risks` for the full analysis.** Phase-specific mitigations:

- **Phase 2 — cause mis-split (B2) / unmapped owner kind.** The owner-kind refusal lands alone,
  against the full corpus, before anything depends on it. If the corpus holds an unmapped kind, it
  fails by name in the cheapest phase.
- **Phase 3 — newly-reached classification (B3).** The form gate before the predicate walk is the
  mitigation; the `plain_usage`-with-raising-predicate fixture is what proves it rather than
  relying on `catf_mfe_d5`'s luck (design's recorded fact under B5). Real behavior change: a model
  with an asserted, malformed, non-reaching gate now fails generation — as a named
  `classification_incomplete` halt, with every other usage still carrying a visible record.
- **Phase 4C — the pin window (PD4).** The companion schema bump turns the codegen suite red until
  `_upstream_pins.py` is updated, because the pin test reads the installed (editable) companion.
  Mitigation: land C1 and C2 in one window and run both suites before moving on.
- **Phase 4C — second-hand anchors (PD5).** Step C0 confirms the seam against the companion worktree
  before any edit; a moved line number is a correction, a moved *mechanism* is a stop-and-surface.
- **Phase 4C — half-built invariant 61.** Codegen can pass every test with the companion half
  missing. Mitigation: the completion criteria span both repos, and the advisory is a phase in this
  plan rather than a follow-up.
- **Phase 4 — magic string in prose.** Fails closed on a near-miss; the spike in Phase 1 confirms
  the seam before the parse is written.
- **Phase 5/8 — a second recapture.** Do not enter Phase 8 with an open schema question. If one
  appears mid-Phase-8, stop and resolve it before capturing.
- **Phase 6 — unexplained baseline churn.** Only three causes are legitimate. A fourth means
  something moved that should not have.
- **Phase 8 — TEAx skew.** Fail-closed by construction, ordered as a hand-off, cannot be enforced
  from here.

## Scale Note (Honest)

The design estimates ~11h of execute+validate, i.e. a ~2-day item. This phasing is consistent with
that **with one caveat**: Phase 7a — hand-authoring and reviewing expectation files for all 31
constraint-bearing fixtures from `.sysml` source — is the largest single block of manual work in the
item and is not compressible without weakening the oracle (a dumped expectation file proves
nothing). If the corpus re-measure in Phase 1 comes back materially above 31, or the fixtures turn
out to be large, say so at that point rather than absorbing it silently.

Phase 4C is new since the design's estimate and adds roughly half a day: one companion diagnostic
kind with its trigger and tests, the schema bump, the codegen pin, three cross-repo assertions, and
a second full licensed suite run in the companion worktree. It is small work spread across two
repos, which costs more in context-switching than in code. Call the item **~2.5 days** now, not 2.

## Implementation Notes

[TO BE FILLED DURING IMPLEMENTATION]

### Phase 1 Completion
**Completed:** 2026-08-12

**Actual Changes:**
- Created `tests/conformance/test_constraint_usage_domain_totality.py` (3 nodes: the 65/9
  headline, one-disposition-each, and the two-tier `declaration_id` join with arity).
- No `src/` change.

**Gate:** the file fails with `AttributeError: 'InstanceGraph' object has no attribute
'constraint_usages'` — the expected failure mode, not an import or fixture error. Licensed run
(the fixture loaded live), so the failure is real elaboration.

**Corpus re-measure (recorded at execution, not targets):** 31 constraint-bearing fixture
directories, 21 snapshot-bearing fixture directories. Both agree with the design's `ccf4c21`
measurement, so Phase 7a's scale note stands as written.

**Spike answers (D2's unobserved dependency) — probes under `/tmp/spike_inapp/`:**
- (a) **CONFIRMED, with a scope limit.** A `ConstraintUsage`'s `doc /* … */` arrives as a
  `Documentation` owned member, `SysideAdapter.is_instance(member, "Comment")` is true, and it is
  reachable from the element at elaboration exactly as at extraction.
- (b) **CONFIRMED.** The body arrives already trimmed of the comment delimiters;
  `.strip().strip("*").strip()` is a no-op on it and reproduces the extraction-side shape.
- (c) **CONFIRMED.** Two `doc` comments produce two `Documentation` members in source order, and
  the `\n`-join puts the second on a later line
  (`'first body\n@inapplicable: second body'`) — so the design's "marker on a later comment body
  is a malformed-annotation halt" rule is implementable as written.

**SURFACED — the scope limit on (a), which the design did not anticipate.** Documentation is
reachable for every constraint-usage body shape *except* an **inline predicate**. For
`assert constraint c { doc /* … */ <expr> }` SysIDE attaches no `Documentation` member at all;
instead the usage ends up with the predicate `OperatorExpression` **duplicated** (two identical
children where an undocumented inline constraint has one). Verified against an undocumented
control on the same shape. Consequences:
1. `inline` is an asserted form, so a vacuous *inline* gate cannot be marked `@inapplicable:`,
   and D2's "a near-miss halts rather than silently doing nothing" cannot fire there — the marker
   is gone before elaboration sees the element. This is the one silent no-op D2 exists to prevent.
2. The author-side workaround is real and cheap: give the usage a non-expression body
   (`assert constraint c : SomeDef { doc /* @inapplicable: … */ }`), which the spike confirms
   works, including for an otherwise-empty body.
3. **Mitigation taken in this item (deviation, recorded in Phase 7a):** the license-free oracle
   scanner also greps `.sysml` source for an `@inapplicable` marker and fails when a marker in
   source produced no `Inapplicability` on the domain record. That converts the silent no-op into
   a loud corpus-wide test failure without inventing a parser.
4. The duplicated-predicate parse artifact is an upstream SysIDE observation, not this item's to
   fix. Recorded here so a later reader does not re-derive it.

This does not trip the plan's STOP criterion: (a) is confirmed — documentation *is* reachable at
elaboration — so D2's mechanism stands. What moved is its reach, and the reach is now guarded.

**Deviations:** one, the scanner-side `@inapplicable` marker check above (additive to Phase 7a).

### Phase 2 Completion
**Completed:** 2026-08-12

**Actual Changes:**
- `elaboration/elaborate.py:522` — `_scopes_for_owner` becomes `_attachment(owner) -> (scopes,
  cause)` over the three-cause split. `_scopes_for_owner` survives as a one-line accessor
  returning `[0]`, because there are **four** call sites, not the one the plan named (`:567`,
  `:863`, `:915`, `:1004`); only the constraint one can act on the cause. Keeping the accessor is
  what stops the branch logic being written twice.
- `elaboration/elaborate.py` — `_owner_kind(owner)` extracted as a static method with the closed
  map plus `NoneType -> "absent"` and `PartUsage -> "part_usage"`, refusing an unmapped kind by
  name (invariant 8). `_constraint_metadata` now calls it.
- `elaboration/diagnostics.py` — `SI_CONSTRAINT_UNATTACHED` and `SI_CONSTRAINT_INCOMPLETE` added.
- New fixtures (Phase 3 will assert against them; authored here because Phase 2's cause test needs
  two of them): `constraint_domain_calc_def_owner`, `constraint_domain_detached_owner`,
  `constraint_domain_containment`, `constraint_domain_plain_forms`,
  `constraint_domain_block_non_reaching`, `constraint_domain_satisfy`,
  `constraint_domain_satisfy_calc_def`. All seven load clean.
- New test `tests/unit/test_constraint_attachment_cause.py` (6 nodes): the three empty causes, the
  non-empty no-cause case, the unmapped-kind refusal, and the `absent` spelling.

**Gate:** focused 6/6 pass. **Full licensed suite: 1695 passed / 34 skipped / 65 deselected**,
**zero** `no live syside license` lines, with only the three intentional Phase-1 RED nodes
failing. That is +6 against the recorded 1689-pass baseline and exactly the six new nodes. `ruff
check src` **14** (baseline 14), `mypy src` **57 errors in 11 files** (baseline 57). No generated
baseline or fixture snapshot moved (`git status` shows only the two `src/` files and the new test).

**What this buys:** the whole corpus contains no constraint owner kind outside the closed map, so
invariant 8's refusal is safe to leave in and B2's three-cause split is confirmed against real
data rather than assumed.

**Issues — SURFACED, environment, and it contradicts the plan's Environment Setup section.**
`uv run --extra dev pytest` (the CLAUDE.md command, and the command the plan and brief both name)
resolves `agentic_mbse` to the **main checkout** `/home/reid/1cfe/agentic-mbse`, not the companion
worktree. Under it the suite does not even collect: `test_exact_constraint_route.py` fails to
import `preflight_identified`. The correct interpreter is the task-specific venv
`/home/reid/1cfe/item7-rebuild-venv/bin/python`, whose editable `.pth` reads
`/home/reid/1cfe/agentic-mbse-item7-rebuild/src`. This is the F2 class recorded in
`CURRENT_WORK.md` recurring. Consequences carried forward:
- **Every gate in this item runs `/home/reid/1cfe/item7-rebuild-venv/bin/python -m pytest`**, never
  `uv run`. The licence sourcing is unchanged.
- **PD4's premise still holds, and is now checked rather than assumed**: the companion worktree
  *is* the installed companion under the correct interpreter, so the Phase 4C pin window is real.
  It would have been invisible under `uv run`, which is the worse failure — the pin test would
  have compared against a companion nobody was editing.

**Deviations:** `_scopes_for_owner` retained as an accessor (four call sites, not one); the
owner-kind map gained `NoneType` and `PartUsage` entries the design's four-entry map lacked, both
required for the map to be closed rather than merely narrower.

### Phase 3 Completion (landed together with Phase 5 — see the reordering note)
**Completed:** 2026-08-12

**Actual Changes — codegen:**
- `elaboration/graph.py` — `UsageDisposition`, `Inapplicability`, `ConstraintUsageRecord`,
  `InstanceGraph.constraint_usages`, the closed `SOURCE_FORMS` / `DISPOSITION_REASONS` /
  `ASSERTED_SOURCE_FORMS` vocabularies, and `expected_severity(reason, source_form)` as the one
  severity derivation both the mint and `validate()` read.
- `elaboration/graph.py` `validate()` — `_validate_constraint_usage_domain`: closed vocabulary,
  one disposition, derived severity, `eligible` with zero occurrences, and the two-directional
  `declaration_id` join with arity. Raises `SI_CONSTRAINT_INCOMPLETE`, never a bare count.
- `elaboration/elaborate.py` — `_constraint_source_form` (six forms, `satisfy_reference` added
  ahead of the `plain_usage` fall-through), `_membership_kind`, `_mint_constraint_usage_record`,
  `_usage_disposition` (the ordered precedence rule), `_non_reaching_reason`,
  `_assert_minting_totality` (invariant 1), `_halt_on_unattached_constraints` (invariant 9).
  `_constraint_metadata` now reuses the two extracted classifiers instead of repeating them.
- The mint runs at the top of `_build_constraint_nodes`'s existing per-usage loop (D9), and
  `occurrence_count` is set from the attachment's scope count.

**Gate:** focused mint tests 8/8, totality 4/4, codec 5/5, parity 3/3. `ruff check src` **14**,
`mypy src` **57** — both at baseline.

**The headline, measured: 65 domain members on `catf_mfe_d5`, split
51 `owner_kind_unattachable` / 5 `owner_has_no_occurrences` / 9 `unassessed_form`.** The 51/5
split matches the research's cause account exactly. Generation still succeeds and no usage grades
`error`, because every one of the 65 is a non-asserted form.

**SURFACED — the design's and this plan's "9 eligible" is factually wrong.** Measured at the
parent commit, `catf_mfe_d5`'s catalog carried **9 `excluded_records`, 0 `usage_records`, and 0
`concrete_entries`**. The 9 was always the count of *visible dispositions*, not of eligible
constraints: all 65 authored usages are bare `constraint`, so the 9 that expand grade
`excluded` / `unassessed_form` and the fixture has **zero** eligible constraints. This is the same
observation the design already recorded under B5 ("all 56 are bare `constraint`") applied to the
whole 65 rather than the invisible 56. Consequences:
- The correct headline is **65 members, 9 with `occurrence_count > 0`, 0 `eligible`**. Every
  "9 eligible" in the design, this plan, and the completion criteria should read that way.
- It strengthens the item's premise rather than weakening it: the pre-item usage tier was not
  merely truncated on this fixture, it was **empty**.
- Nothing mechanical moves. The totality claim, the precedence rule, and the severity table are
  all unaffected.
- Pinned by `test_catf_mfe_d5_authored_population_is_total` and
  `test_catf_mfe_d5_dispositions_split_by_the_precedence_rule`, both of which carry the correction
  in their docstrings.

**SURFACED — invariant 5's `classification_incomplete` has no constructible corpus trigger.**
Implemented as designed (`_non_reaching_reason` classifies an asserted non-reaching usage inside a
`try` and converts an `ElaborationInvariantError` into the disposition), but neither of its two
paths can be reached with this upstream: `extract_expression_ir` returns an `UnsupportedNode` for
every unrecognized construct and `None` only for a `None` expression, so the
`SI_REDEFINITION_INVALID` raise at `elaborate.py:1186` is dead today; the definition-identity
`SI_EDGE_DANGLING` path needs a profile/live disagreement no fixture can author. The disposition
is therefore reachable by construction and pinned by the vocabulary, not by a behavioural fixture.
Recorded rather than faked with a mock.

**Deviations:** none in mechanism. Two in evidence: the `plain_usage`-with-raising-predicate
regression fixture the design asks for cannot exist (above), so `constraint_domain_plain_forms`
pins the form gate with a would-BLOCK predicate instead; and the `9 eligible` assertions are
written to the measured truth.

### Phase 5 (codec v3) — PULLED FORWARD into the Phase 3 landing
**Why, and it is the plan's own contingency.** Phase 3's validation clause says: "if `validate()`
refuses [a snapshot-loaded graph with an empty domain], Phase 5 has to move up; record it." It
does — the join check reports `occurrence node joins no usage record` for every constraint in
every committed snapshot, which took 156 nodes red. So the codec landed in the same window.

**Actual Changes:**
- `snapshot/instance_graph.py` — `INSTANCE_GRAPH_SCHEMA_VERSION = "instance-graph/v3"`;
  `_constraint_usage_to_data` / `_constraint_usage_from_data`; `constraint_usages` added to the
  encode payload and to the decode key set. Fail-closed needed no new code, as D4 predicted.
- `snapshot/envelope.py:399` — the envelope's own exact inner-graph key set was a **second** copy
  of the codec's collection list and had to move with it. The design did not name this file; it is
  found, not assumed.
- `orchestration/elaborated_pipeline.py` — **a real defect, not bookkeeping**: the capture route
  rewrites `source_file` to a portable referent on attrs, calcs, and constraints but not on the
  new usage tier, so sealed bytes carried the capture machine's staging path and live and snapshot
  disagreed. Fixed by extending `_rewrite_sources_as_referents`; pinned by
  `test_the_sealed_routes_carry_a_portable_source_referent`.
- `tests/conformance/test_snapshot_v6_routes.py` — the route-parity digest masks `source_file`;
  the mask now covers `constraint_usages` for the same reason it covers the other three tiers.
- `tests/conformance/test_elaboration_graph_roundtrip.py` — the two literal `instance-graph/v2`
  pins moved to v3.
- New `tests/conformance/test_constraint_usage_domain_codec.py` (5 nodes: version, round trip
  field for field, v2 refusal, missing-tier refusal, fingerprint coverage) and
  `test_constraint_usage_domain_parity.py` (3 nodes: three-route field-for-field parity against a
  temp-dir capture, a non-vacuous-comparison guard, and referent portability).

**SURFACED — a premise conflict between two of the brief's non-negotiables, and how it is
resolved.** "Phase gates are real: do not start a phase until the previous phase's gate is green"
and "the single reviewed recapture is the LAST fixture-committing step" cannot both hold literally
here: the committed v2 fixtures cannot load until they are recaptured, and recapturing now would
move the recapture off the end. Resolution, recorded rather than taken silently:
- The recapture **stays at Phase 8**, single and reviewed, per the landing order and the Item 7
  register.
- The intermediate gate is redefined honestly as **"no failure outside the frozen v2-refusal
  list"**, and that list is committed at
  `.project/active/constraint-catalog-totality/v2-refusal-list.txt` — **61 nodes**, enumerated by
  node id, every one traced to committed snapshot bytes that predate `constraint_usages`. Any new
  failure is still caught, so the gate keeps its teeth.
- Checked, so the "recapture once" promise is not a hope: nothing in Phases 4, 4C, 6, or 7 changes
  the instance-graph payload. Phase 4 writes `inapplicability` only for annotated models and no
  snapshot-bearing fixture is annotated (D8); Phase 4C bumps the companion's
  `CONSTRAINT_FACTS_SCHEMA_VERSION`, which the envelope authority does **not** record (it records
  `agentic_mbse_version`, the package version); Phases 6 and 7 touch projection and extraction
  only. The schema is settled.

**Full licensed suite at this gate: 1647 passed / 34 skipped / 65 deselected / 34 failed +
27 errors**, and all 61 failing nodes are the frozen list. Down from 156 at the moment the
join check first landed.

### Phase 4 Completion
**Completed:** 2026-08-12

**Actual Changes:**
- `elaboration/elaborate.py` — `_INAPPLICABLE_MARKER` and `_ExactElaborator._inapplicability`,
  read at mint time off the usage's joined documentation. Two named halts: a first line that
  begins with the marker but is not `@inapplicable: <reason>`, and the marker on any later line
  of the join. Both raise `SI_CONSTRAINT_INCOMPLETE`; neither is a no-op.
- Four fixtures: `constraint_domain_inapplicable` (annotated vacuous gate),
  `_malformed` (marker with no reason), `_late_marker` (marker on a second `doc` body), and
  `_unattachable` (annotated **and** owned by a `calc def`, which must still halt).
- New `tests/unit/test_constraint_inapplicability.py` (7 nodes) and two more parity nodes.
- `tests/conformance/test_constraint_usage_domain_parity.py` now runs on the annotated fixture,
  which is what the design asks for: the annotation read is the one live-only elaboration step,
  so it is the concrete way live and snapshot could diverge while both seal cleanly.

**Gate:** focused 7/7 + parity 4/4 + codec 5/5. Full licensed suite **1663 passed / 34 skipped /
65 deselected**, and **no failure outside the frozen 61-node v2-refusal list**. `ruff check src`
14, `mypy src` 57 — both at baseline.

**Deviation — `Inapplicability` carries the reason and nothing else.** The design's sketch was
open; the first cut carried `source_file` and `source_line` too, and the three-route parity test
caught it immediately: a second copy of a source path inside the fingerprint that the capture
route did not rewrite, so live and sealed bytes disagreed. That is the same defect
`exclusion_location` already taught this repo. The annotation is written on the usage, so the
record's own `source_file` / `source_line` already locate it, and dropping the duplicate is
strictly better than teaching a second rewrite site.

**Deviation — a sixth named exemption in the F30 boundary guard.**
`tests/unit/test_elaboration_import_boundaries.py` denies string selectors across the six
boundary files by default, and the annotation parse is genuinely string work. It is exempted by
name with the reason recorded inline: it reads author-written prose and touches no identity — the
record it lands on was keyed by `declaration_id` before the parse runs. The guard's own mechanism
is per-function naming, so this does not widen it for anything else.

**Carried from Phase 1, unresolved by design:** an `inline`-form vacuous gate still cannot be
annotated, because SysIDE drops a `doc` comment inside an inline predicate body. Phase 7a's
scanner is what makes that loud.

### Phase 4C Completion
**Completed:** 2026-08-12
**Companion commit:** `bc69f04` in `/home/reid/1cfe/agentic-mbse-item7-rebuild` (branch
`item7-rebuild`, on top of Item 1's `dcb187b`).

**C0 anchor confirmation (PD5): the mechanism is exactly as designed; three line numbers moved.**
Confirmed against the companion worktree HEAD before any edit:
- `CONSTRAINT_FACTS_SCHEMA_VERSION` at `:54` — as cited, value `constraint-facts/v2`. ✓
- `DiagnosticSeverity` (BLOCKING | ADVISORY) at `:57` — as cited. ✓
- `EXTRACTION_DIAGNOSTIC_SEVERITY`, the closed writer-side map, at `:78` — as cited, and its
  comment already states that changing an entry requires a schema bump. ✓
- `severity_for_kind` at `:87` (design cited `:78-95`, which spans both). ✓
- `ExtractionDiagnosticFact` at `:217` with `severity: field(init=False)` set in `__post_init__`
  at `:234-235` (design cited `:230-233`). ✓
No mechanism differs, so D10 stands and no stop-and-surface was triggered. The moved anchors are
recorded here, per PD5's instruction.

**C1 — companion:**
- `constraint_facts.py` — `"vacuous_asserted_gate": DiagnosticSeverity.ADVISORY` in the closed
  map, with the reason recorded inline; `CONSTRAINT_FACTS_SCHEMA_VERSION` → `constraint-facts/v3`.
  Severity stays writer-side; no reader-side table appears anywhere.
- `constraint_extraction.py` — `_ASSERTED_FORMS`, `_typed_part_definition_ids(model)` (the
  structural stand-in for instantiation, computed once per sweep), and
  `_vacuous_asserted_gate_fact(...)` returning the fact or `None`. The emit decision is at the
  sweep's call site; the helper only builds the fact. The message names the usage QN **and** the
  detached owner QN, and `location` carries the usage's position, so codegen's `_render` prints
  `file:line:column`.
- Three fixtures under `tests/fixtures/vacuous_asserted_gate/` and
  `tests/test_sysml/test_vacuous_asserted_gate_advisory.py` (5 nodes: emission + grade + location,
  the containment silence, non-asserted silence, the map staying closed, and the schema bump).
- `production_facts.json` regenerated. Diffed key by key: **exactly two changes** — the schema
  token, and one real advisory firing on a genuine vacuous gate in the companion's own
  `type_units.sysml` fixture. The advisory works on data nobody wrote for it.
- Four version pins in three companion test modules moved to v3, and the skew-direction
  parametrization moved from `v1`/`v3` to `v2`/`v4` so both directions still straddle the current
  version rather than one of them accidentally becoming the supported one.

**C2 — codegen (small, but not zero, exactly as PD4 predicted):**
- `_upstream_pins.py:38` → `constraint-facts/v3`, with the v2→v3 reason recorded beside the
  v1→v2 one.
- `tests/conformance/test_extraction_diagnostic_screen.py` — three new nodes: the existing sink
  renders the new kind at warning grade without halting; generation completes with the advisory
  present; and the independence check (invariant 59) — the domain is identical with
  `screen_extraction_diagnostics` stubbed out, so codegen's grading demonstrably does not consult
  the advisory. **No sink change was needed**, which is what routing the advisory through the
  companion bought.

**PD4's pin window was real and was closed inside the phase.** C1 and C2 landed together; between
the companion bump and the codegen pin, `test_upstream_pins.py` compares against the installed
(editable) companion and fails. Confirmed the install points at the worktree — see the Phase 2
environment note, which is what made this checkable rather than assumed.

**Gate — both suites, both licensed:**
- **Codegen** (`/home/reid/1cfe/sysml-codegen-item7-rebuild`): **1666 passed / 34 skipped /
  65 deselected**, zero `no live syside license` lines, **no failure outside the frozen 61-node
  v2-refusal list**. `ruff check src` 14, `mypy src` 57 — baseline.
- **Companion** (`/home/reid/1cfe/agentic-mbse-item7-rebuild`, run in that worktree):
  **1821 passed / 1 skipped / 5 deselected / 10 failed**. The 10 are the pre-existing baseline,
  verified by stashing the change and re-running at HEAD: identical set, 1816 passed. So the
  change is **zero new failures**. The single skip is `Requires fusion_modeling CATF models not
  in this repo`, not a licence skip — zero `no live syside license` lines. `ruff check src` 1
  before and after; `mypy src` 108 errors in 26 files before and after — zero new on both.

**Deviations:** none. The regenerated golden and the version-pin updates are consequences of the
schema bump, not choices.

### Phase 5 Completion

### Phase 6 Completion

### Phase 7 Completion

### Phase 8 Completion

---

**Status**: Draft → In Progress → Complete
**Next Step:** `/_my_implement`
