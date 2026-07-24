# Audit: Docs Lifecycle Sync (FINAL — all 5 phases)

**Verdict:** Pass with notes
**Audited:** 2026-07-24
**Branch:** docs-lifecycle-sync
**Commits:** b2e0fc3 (P1), 6909dea (P2), 9e40196 (mid-run audit + Finding-1a fix), 7849059 (P3), d4051ee (P4), 86bfc7c (P5)
**Baseline:** merged main — sysml-codegen `936315c`, agentic-mbse `f4ebdce`, teax `fa0e06a`
**Scope:** docs-only item — claims-vs-code truth, not test coverage. Phases 1–2 were certified
in `audit-midrun.md` (Pass with notes); this pass does not re-audit that ground except to
confirm Finding 1a's fix landed. It certifies Phases 3–5 and the six spec Success Criteria.

---

## Summary

The documentation is accurate against merged code everywhere I could reach it. Every
codegen-side citation in the new severity doc resolves to the exact symbol at the cited line;
the two new matrix rows are pinned by tests whose bodies genuinely assert the claimed behavior;
the matrix recount reconciles to the digit; all four spec exit greps are clean; the
EXPLAINER_PROMPT re-anchors — including the composed-proof anchor numbers — match their sources.
No defects were found in Phases 3–5, and Finding 1a from the mid-run is fixed.

One real limitation, not a defect: roughly half of doc 30's load-bearing citations point into
`agentic-mbse`, which is entirely outside this session's sandbox. I could not read them. That
includes the doc's most novel claim — the guard-2 severity cross-check at
`constraint_facts.py:374-385`. The codegen side that *consumes* those symbols checks out, which
corroborates the enum and field, but the cross-check behavior itself is unverified here. See
Note N1. The verdict is Pass with notes on the strength of that single unverified region; every
in-reach claim passed.

## Findings — by Success Criterion

### Criterion 1 — Register completeness (every row dispositioned with citation)
**Met.** `inventory.md` carries all four sweeps (A1–A5, B1–B6, C1–C10, D1–D6), the R5
override-honesty rows (R5a–c), the Phase-2/4/5 closure dispositions, the E1–E19 EXPLAINER
register, and the MG1–3 filed matrix-GAP candidates — each with a disposition and a code
citation. The mid-run audit spot-checked six dispositions across sweeps A–D and found them
trustworthy; the deferred rows (module_kind → Phase 2, severity → Phase 3, portability →
Phase 4) all show as closed in the later dispositions. The brief-vs-plan `module_kind`
boundary and the REQ-IR/REQ-DRA re-projection were surfaced, not silently resolved
(capture-fidelity rule 4).

### Criterion 2 — Severity doc `30-diagnostic-severity.md` (behavioral claims vs code)
**Met on the codegen side (exact); partially unverifiable on the agentic-mbse side — Note N1.**

Codegen-side claims, all confirmed at `936315c`:
- `screen_extraction_diagnostics` at `analysis/diagnostic_screen.py:51`; partitions by the
  `severity` field (`:56-65`), logs advisory first (`:67-68`), returns if no blocking
  (`:70-71`), else raises `CodeGenerationError` naming every blocking diagnostic (`:73-78`).
  `_render` degrades a missing location to `<no location>` (`:39-48`, literal at `:44`) — so
  advisory rendering cannot pre-empt the halt, exactly as the doc's ordering section claims.
- Two sinks, both before lowering: live route `orchestration/pipeline_builder.py:898` (right
  after `extract_constraint_facts` at `:896`); snapshot route
  `orchestration/snapshot_context.py:48` (before `build_full_graph_from_snapshot` at `:50`).
  Both exact.
- Guard 1, envelope half: `snapshot/loader.py:731` refuses `version != SNAPSHOT_FORMAT_VERSION`
  (in the `723-734` block). Shape gate `_validate_diagnostic` at `:586-604` requires `kind`,
  `message`, `severity` as present strings (`:588-591`) — matches the doc.
- Companion pin: `_upstream_pins.py:27` `CONSTRAINT_FACTS_SCHEMA_VERSION = "constraint-facts/v2"`
  (the `:24-27` pin block). Exact.

"Skew in each direction, answerable from the doc alone": **yes.** The section "What happens on
severity skew — in each direction" is self-contained: it names all three guards (version gate →
severity cross-check → unknown-kind refusal), states the exact-equality reasoning that makes
ahead and behind refuse identically, and describes the cross-check refusing in either direction.
A reader needs nothing outside the doc to answer it.

The three agentic-mbse-resident guards/claims — `DiagnosticSeverity` enum (`:57-68`), the
`EXTRACTION_DIAGNOSTIC_SEVERITY` one-entry table (`:78-82`), `severity_for_kind` unknown-kind
refusal (`:87-95`), the `__post_init__` writer-set severity (`:230-233`), `_diagnostic_from_dict`
guard-2 cross-check (`:362-386`, refuse-either-direction at `:374-385`), and `parse`'s
exact-equality fact-version gate (`:397-408`) — **could not be read** (Note N1).

### Criterion 3 — Matrix REQ-SNAP-21/22 + the 276/275 recount
**Met.** Both rows exist and are PASS. I read the cited test bodies; they pin the claimed
behavior, not just the symbol names:
- **REQ-SNAP-21** (referent shape gate). `test_source_referent_shape_gate.py` asserts a clean
  v5 load (`test_committed_v5_snapshot_loads_clean`) and three loud rejects —
  `test_absolute_source_file_rejected` and `test_snapshot_dir_relative_source_file_rejected`
  (`pytest.raises(SnapshotFormatError, match="portable")`) and `test_stale_version_rejected`
  (`match="version"`). Envelope half `test_snapshot_v5_gate.py` covers both skew directions
  (`test_both_envelope_skew_directions_fail_closed`) and that every committed snapshot loads at
  v5. The gate call site is real: `_validate_source_referents` defined at `snapshot/loader.py:912`,
  called at `:837`.
- **REQ-SNAP-22** (whole-tree portability). `test_whole_tree_portability.py::test_catf_mfe_whole_tree_two_root_portable`
  places the same snapshot at two distinct absolute roots and asserts `_diff_paths(...) == []`
  (byte-identical tree) and `_absolute_hits(...) == []` (no checkout-absolute path) — the
  license-free primary. `test_anonymous_admitted_relocated_graph_portable` is the licensed
  relocated-anonymous leg. Both match the row's wording.
- **Recount reconciles exactly.** Summing the 32 per-family index annotations: Σtotal = 276,
  Σpass = 275, Σuntested = 1 (the single `(7/8 pass, 1 untested)` family, REQ-PGD-06), families =
  32 — matching the summary block (`:9-14`) to the digit. The two mandated corrections landed:
  DM `(9/9 pass)` (`:41`) and RES `(8/8 pass)` (`:61`), and SNAP `(22/22 pass)` (`:62`). The
  `test_input_resolver.py` dead-test citation was replaced (D6); the `REQ-PR-*` family is
  surfaced as a filed GAP in the DRA banner (`:218`), not silently added.
- *Minor, non-defect:* REQ-SNAP-21 says the `unknown`/`hierarchy` sentinels "pass through." I
  confirmed the reject tests and the clean-load test; I did not see a dedicated assertion that
  exercises a sentinel value specifically. The behavior is covered by the clean-load path and
  the gate code; noted only so the certification's edge is honest.

### Criterion 4 — EXPLAINER_PROMPT re-anchors (spot-check ~8 of E1–E19)
**Met.** Spot-verified nine:
- E1 banner → "post-CONSTRAINT-LIFECYCLE, merged main", branch `main`, "Three epics landed"
  (`EXPLAINER_PROMPT.md:1,4-9`). ✓
- E2/E-build composed-proof anchors — checked against
  `.project/completed/20260720_constraint-lifecycle-composed-proof/`: **41/41** (release-readiness
  `:3,:31`; manifest `:16`), **IFE 2,301-point grid** (release-readiness `:50`; evidence register
  `:395,:646`), **stellarator five verdicts / six bit-exact anchors** (release-readiness `:51,:93`;
  evidence register `:628` "six anchors OK", `:631` "bit-exact vs oracle reldev 0.00e+00"). The
  prompt's phrasing at `:27-30` matches all three. ✓
- E3 snapshot v5 in L1 (`:70`). ✓
- E12 deleted-not-unwired resolver: `:240-246` states `input_resolver.py` was **deleted** and
  "that symbol no longer exists." Confirmed against src — `grep` for
  `input_resolver|resolve_input|AGG_STRATEGIES|DesignAttributeLookup` over `src/` returns **zero**
  hits; `resolve_producer` is live in `resolution/producer_resolution.py`. The claim is accurate
  (deleted, not merely unwired). ✓
- E13 lowering anchored to `resolve_producer` + strict `TerminalPolicy` fork (`:268-271`). ✓
- E17 counts "276 = 275 PASS + 1 UNTESTED, 32 families" (`:314`) — matches the matrix. ✓
- EXPLAINER exit greps clean: no `constraint-exec-epic`, `post-CONSTRAINT-EXEC`,
  `docs-explainer-refresh`, `backlog/epic_`, `04-input-resolver`, `format v3`, or bare `274`. ✓
- Scope guard held: the prompt still describes building the HTML as its *subject*
  (`[V2-HTML-BUILD]` is owner-assigned; the item only makes the input truthful) — no build was
  attempted. ✓

### Criterion 5 — All four spec exit greps run fresh
**Met.** Run at `936315c`:
1. `input_resolver|resolve_input|AGG_STRATEGIES|DesignAttributeLookup` over `docs/architecture/`
   → **zero live claims.** Residual = dated history only: doc 24 "Dated history" block
   (`24-…:140,145,146`) and the matrix deletion note (`verification-matrix.md:218`). Allowed by
   the criterion.
2. `is_computed_attribute|is_aggregation` over `docs/architecture/` → **zero live claims.**
   Residual = `09-data-models.md:71,301`, the retirement narrative (register C9). Allowed.
3. Nested-override honesty → `modeling-assumptions.md:354-361` carries the explicit limitation
   ("nested-occurrence overrides are not captured correctly … do not read this section as
   promising nested-occurrence override capture"). No doc claims capture works. ✓
4. Version literals → clean; no stale `format v3`/`v1`/`v2` or mismatched profile/schema literal
   in `docs/architecture/`. ✓

### Criterion 6 — Cross-cutting
**Met (spot-checked; see Not-checked for the exhaustiveness limit).**
- **No release-readiness claims added.** Grep for `release.ready|ready for release|production.ready|
  release readiness|certified for release` over doc 30, doc 04, the matrix, and EXPLAINER_PROMPT
  returns nothing. The composed-proof archive's `release-readiness.md` is the closed record and
  stays in `completed/`; none of it was echoed into the docs.
- **Corrections shrank/amended in place.** doc 24 keeps the deleted architecture only inside a
  marked "Dated history" block; matrix `:218` is a marked deletion note; EXPLAINER §7's "Retired …
  do NOT present as open" is decision-record framing, not an instruction anchoring future agents
  on the retired claim. No "used to say X" prose outside marked dated-history. Consistent with
  capture-fidelity rule 3.
- **New docs linked from neighbors + index.** Doc 30 is linked inbound from `27-snapshot-generation.md:88`,
  `28-constraint-lowering-and-catalog.md:17`, and the deep-dive index `00-pipeline-overview.md:234`;
  index rows 28/29/30 are all present (`:232-234`). Doc 04's inbound `04-input-resolver` links were
  repointed (Phase 2). Finding 1a fix confirmed: `04-producer-resolution.md:60` now reads "Sole
  input to the self-reference guard; the entry-point QN rule prefixes it with `param_name` …" — the
  incorrect "and to the entry-point QN rule" clause is gone.

## Notes

**N1 (advisory — certification scope, not a defect): the agentic-mbse half of doc 30 is
unverified here.** All access to `/home/reid/1cfe/agentic-mbse` is blocked from this session
(Bash `cd`/`grep`/`sed`, the Read tool, and a dispatched Explore subagent all failed on the
working-directory sandbox; the repo is not mounted and this run is non-interactive so no approval
flow is possible). That leaves seven load-bearing doc-30 claims unread, most importantly the
guard-2 severity cross-check (`constraint_facts.py:374-385`) — the doc's "fuller-than-brief"
finding and the backstop the whole skew story rests on. Indirect corroboration is real but
partial: codegen imports `DiagnosticSeverity` and branches on its `BLOCKING`/`ADVISORY` members
(`diagnostic_screen.py:28,59,64`), and `_upstream_pins.py:27` pins `constraint-facts/v2`, so the
enum, the field, and the schema version exist as the doc describes. The cross-check *behavior* has
no codegen shadow and remains unconfirmed. To fully certify doc 30, re-run this check from a
session with agentic-mbse `f4ebdce` in scope.

## Certification

Checked and confirmed against merged main (`936315c` codegen; composed-proof archive):
- Doc 30 — all **codegen-side** citations (sink, two routes, ordering/`<no location>`, envelope
  version gate, shape gate, companion pin) and the self-containedness of the skew section.
- Matrix — REQ-SNAP-21/22 row wording against the actual test bodies; the gate call site; the full
  276/275/1/32 recount including the DM/RES/SNAP index corrections.
- EXPLAINER — nine E-register re-anchors incl. the composed-proof anchor numbers against the
  archive, the deleted-not-unwired resolver claim against src, and the count reconciliation.
- All four spec exit greps, fresh.
- Cross-cutting: no release-readiness claims in touched docs; in-place amend discipline; doc-30
  inbound links; Finding 1a fix.

**Not checked:**
- **The agentic-mbse half of doc 30** (Note N1) — seven citations including the guard-2 cross-check.
  Sandbox-blocked; the single reason this is Pass with notes rather than Certify.
- **Phases 1–2 deliverables** beyond confirming Finding 1a landed — certified in `audit-midrun.md`;
  not re-audited here.
- **Exhaustive prose read** of every touched doc. The mechanical exit greps are clean and the
  new/rewritten load-bearing sections (doc 30, doc 04:44-66, matrix SNAP rows, EXPLAINER re-anchors)
  were read in full, but I did not re-read every reframed sentence in docs 03/05/overview/24 or the
  one-line reference fixes swept in Phase 2 (those were in `audit-midrun.md`'s not-checked list too).
- **The B2/B3 GAP surfaces** (written_qualifier, trust manifest) and the MG1–3 filed matrix-GAP
  candidates — these are recorded owed-writing/filing decisions, explicitly not required by this
  item; I confirmed the cited symbols exist but did not audit coverage.
- **Any test-suite / byte-identity behavior** — out of scope for a docs-only item.

ARTIFACT: .project/active/docs-lifecycle-sync/audit.md

---

## Orchestrator addendum — N1 CLOSED (2026-07-24)

The audit session's sandbox could not read agentic-mbse; the orchestrator session can. All
seven doc-30 citations into `agentic-mbse` verified **exact** at merged main `f4ebdce`
(file is src-layout: `src/agentic_mbse/sysml/constraint_facts.py`; doc 30 cites the module
path, which is fine):

- `:54` `CONSTRAINT_FACTS_SCHEMA_VERSION = "constraint-facts/v2"` — exact.
- `:57-68` `DiagnosticSeverity(str, Enum)`, two members BLOCKING/ADVISORY, transport-only
  docstring — exact.
- `:78-82` writer table `EXTRACTION_DIAGNOSTIC_SEVERITY`, exactly one entry
  (`non_finite_literal` → BLOCKING) — exact.
- `:87-95` `severity_for_kind` refuses unknown kinds (ValueError, closed set) — exact.
- `:230-233` `severity` is `init=False`; `__post_init__` derives from the writer table at
  construction — exact.
- `:374-385` guard-2 severity cross-check in `_diagnostic_from_dict`: reconstruction
  re-derives severity and raises on stored-vs-table disagreement in either direction
  (invalid stored value raises at `:365-369`; valid-but-disagreeing raises at `:381-385`) —
  exact, matches the doc's "refuse rather than silently prefer either side."
- `:397-408` exact-equality schema_version gate — exact.

With N1 closed by direct verification, no open findings remain. Verdict effectively
**Certify** (stage verdict "Pass with notes" retained above as the audit-session record).
