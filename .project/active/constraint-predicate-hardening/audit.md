# Audit: Predicate Defect Hardening (CONSTRAINT-SEMANTICS Item 4)

**Verdict:** **Certify-with-residuals** — conditional on the Requested live probes (R1–R6)
returning as the author reported.
**Audited:** 2026-08-13
**Branch:** `item7-rebuild`
**Range:** codegen `f3b3131..89fc38f` (Item 4 commits: `f3b3131`, `acfba0b`, `098ea65`,
`284f716`, `1b94c4b`, `3459127`, `89fc38f`); companion `0a52942` (**not readable from this
session**)
**Audit sandbox:** codegen tree readable; **no code execution**, **no companion reads**. Every
runtime number below is author-reported and marked as such.

---

## The Point

A modeler writing an asserted physics gate must be stopped only by the product's real limits,
and when stopped, must be told what to write instead. Neither held. A modeler writing the
*supported* form — an inequality carrying a unit-annotated literal — was refused by a bug that
has nothing to do with any limit (`SI_OCCURRENCE_MISSING` raised against `SI::metre`, because
the predicate reference walk recursed into the `[` annotation's unit operand). A modeler
writing an *unsupported* form — a feature chain in a predicate body — was refused with
`feature_chain: block_feature_chain`, which names no reference, no location, and no rewrite.

This ladders into Item 5, which migrates all 65 CATF constraints into the bindings-only recipe.
The blocked-chain diagnostic is the instrument that migration is performed with: a tautology
makes 65 rewrites a manual hunt. The published promise being discharged is
`docs/architecture/modeling-assumptions.md:535`.

## Summary

The implementation is disciplined and matches the design closely. Both cures are one existing
rule reaching two more lanes through the existing `_without_unit_annotation` wrapper — no second
rule, no structural `operator == "["` test anywhere (invariant 1 holds). The renderer
(`elaborate.py:320-366`) implements D5's single normalized key and D6's omit-on-absent
rendering exactly as written. The evidence trail is unusually good: the red run is captured
verbatim and internally consistent, the probe verdicts are recorded with their measurements,
and the one place the design's bet turned out false (B2 on the binding lane) is written up
rather than quietly absorbed.

The residuals are about the *record and the pins*, not the shipped behavior: one red-first
characterization was rewritten rather than merely unmarked and that deviation is missing from
the consolidated list; two tests' docstrings claim more than the tests check; and the item's two
most consequential surfaced findings sit only inside a folder that `/_my_close` will archive,
where Item 5's author will not look.

## Product Judgment

**Is this the right piece of work? Yes.** The item removes a bug that blocked the product's own
supported authoring shape and replaces a tautology with an actionable message, immediately
before the item that consumes that message 65 times. Nothing was widened: the profile's
admitted set is untouched in both directions (invariant 3 as scoped by M5), and codegen's
readiness-refused set shrinks by exactly the shapes D1 and D2 name.

**Product-lens ledger gate: DISPOSED, not BLOCKED**, at both recorded entries
(`product-lens.md:164` spec stage, `:217` design stage). Scanning every block in the ledger, not
only this run: item4-F1 through item4-F4 are all `[DO]`, none reaches BLOCK grade, and the
design stage records each as discharged — F1 by the inequality/working-gate fixture, F2 by D2
curing the fourth lane, F3 by the catalog/coverage assertions, F4 by the corrected `:535`
citation. I re-checked F1 and F2 against the landed code and they are genuinely discharged:
`test_the_cured_predicate_is_a_working_gate` asserts an assessed catalog row rather than the
absence of an error code, and the rewrite the message advertises
(`in outer_radius = bioshield.outer_radius;`) is a plain chain binding, which Q4 admits and
which D2 did not need to touch. The epic's live Product-Lens gate carries no unresolved BLOCK.

*Runner note, graded honestly:* `~/.claude/scripts/product-lens.md` is outside this session's
sandbox (the same refusal the spec- and design-stage entries record), and this run is
non-interactive with subagent spawning barred, so this is the auditor re-deriving the point and
re-checking the ledger's findings against the implementation — **not** an independent third lens
run. Weaker evidence than a fresh run, and stated as such.

**Structural smells — one fires, and it is resolved here, not left in a rubric.**

- *A test that passes only because it selects one interpretation:* **fires weakly, on the
  invariant-7 twin comparison (F2 below).* The test compares twin fixtures whose only wiring
  rows come from the `Noop` calc def and the `gap_width` attribute; the constraint — the one
  site D1 newly reaches — contributes no module input, so the comparison cannot observe the edge
  loss its docstring claims it would catch. **Resolved in this judgment:** the invariant it
  names is true by construction (the second operand of `[` is a unit), the design said so
  (M6b/invariant 7), and no supported authoring shape can produce the failure — so the item
  cannot land the defect the test was meant to catch. It is a precision-of-claim defect in the
  docstring, not a hole in the product. It does not block certification.
- *Two representations kept in sync:* does not fire. One rule, one owner
  (`extraction/unit_annotation.py`), three call sites all routed through
  `_without_unit_annotation` (`elaborate.py:806`, `:1701`, `:2432`).
- *A special category exempting a case whose meaning is unchanged:* does not fire. The oracle's
  `REFUSED_BY_DESIGN` entry for `predicate_unit_annotation` was **removed** when D1 landed
  (`test_constraint_population_oracle.py:68-75`), forced by the file's own rule 4 — the exemption
  shrank rather than grew.
- *Correctness depending on downstream knowledge of an internal representation:* does not fire.
  Codegen's assertions match the chain text, the `in … =` fragment, and the location — never the
  companion's full sentence (`test_blocked_chain_diagnostic.py:10-13`).

---

## Findings

Severity: **Medium** = fix before close. **Low** = record and decide.

### F1 (Medium) — a red-first characterization was rewritten, not merely unmarked, and the consolidated deviation list omits it

`tests/conformance/test_predicate_unit_annotation.py:105`.
`test_the_annotated_and_bare_twins_produce_identical_module_inputs` was renamed to
`…_wire_up_identically` **and its assertion replaced** in `acfba0b` — the same commit that
removed its `xfail` marker. Before: `sorted((param_name, source.source_type))` over all module
inputs. After: `[(module_index, source.source_type)]` plus an entry-point value dict.

The red is not fake — the captured failure for that row (`probes/red-evidence.md:126-143`) is
the real `SI_OCCURRENCE_MISSING` raise, so the row was red for Defect A. But **the assertion
that is now green is not the assertion that was red**, and the new one drops `param_name`
entirely, so it no longer observes *which* input received which source kind.

It is disclosed — `plan.md` Phase 2 "Issues / deviations" states it plainly, with a sound
reason (the twins are two packages, so generated identifiers could never compare equal). What
is missing is that `verification.md:240-264` presents its deviation list as complete ("All are
recorded in plan.md's Implementation Notes at their phase. In one place:") and this one is not
in it. A reader auditing red-first integrity from `verification.md` alone would not learn that
a characterization changed shape between red and green.

**What should change:** add it as deviation 8 in `verification.md`, and restore name-level
comparison in `_input_wiring` using the unqualified tail
(`module_input.param_name.rsplit("__", 1)[-1]`) — see probe R5.

### F2 (Low–Medium) — the invariant-7 pin cannot observe the edge loss its docstring claims

`tests/conformance/test_predicate_unit_annotation.py:105-113`. The docstring says "If the `[`
second operand ever resolved to a user-model feature rather than a library element, the
annotated twin would come up an edge short here." It would not. In
`tests/fixtures/predicate_unit_annotation/model.sysml` the annotated sites are both inside the
`gap_guard` constraint, and a constraint contributes no `PipelineModule` input — the only rows
`_input_wiring` sees come from the `Noop` calc def. The `_entry_point_values` half does pin the
annotated attribute value (`gap_width = 0.5 [m]` → `0.5`), which is real but is the
already-cured `_create_value_node` lane, not the lane D1 opened.

Invariant 7 is unfalsifiable by construction (design M6b says so), so this is a claim-precision
problem, not a coverage hole.

**What should change:** the docstring states what the test actually pins (twin wiring shape and
the annotated attribute's value), and names the invariant as structurally rather than
empirically held.

### F3 (Low) — the M7 test does not drive the route it documents, and its name says it does

`tests/conformance/test_predicate_unit_annotation.py:141-152`. The test builds
`_ExactElaborator.__new__(_ExactElaborator)` and calls `_expression_references` directly on a
synthetic `_MalformedUnitAnnotation`. That pins the raise. M7's actual claim is that the
`ElaborationInvariantError` **escapes** the `except _UnsupportedExpressionError` at
`elaborate.py:2337-2338` and becomes a hard refusal — which the test never reaches. The name
`test_a_malformed_annotation_in_a_predicate_hard_refuses` asserts an end-to-end route the body
does not exercise; no predicate is involved.

I confirmed the escape statically: `_expression_references` has exactly two external callers
(`elaborate.py:2271` in the alias lane, `:2337` in the computed/predicate lane) and only `:2337`
catches anything, and it names only `_UnsupportedExpressionError`. So M7 is correct — the test
just does not prove it.

**What should change:** rename to say it pins the walk's refusal, or drive the real caller.

### F4 (Low) — D2's "genuine expression sources stay refused" bound is pinned by one shape

`tests/conformance/test_constraint_binding_unit_annotation.py:84-86` covers `in tol = a + b;`
only. The design's bound names arithmetic *and* invocations. The unwrap is operator-keyed
(`extraction/unit_annotation.py:53` returns anything whose operator is not `[` unchanged), so
the risk is low — but the design named a set and one member is tested.

**What should change:** one more binding row (an invocation source) in the fourth-lane fixture,
or the design's stated bound narrowed to what is pinned.

### F5 (Low) — a live gate now reads an artifact in `.project/completed/`

`tests/unit/test_coverage_ledger_agreement.py:29` now points at
`.project/completed/20260813_constraint-coverage-policy/expected-coverage.md`. **Nothing else
was swept in with the repair** — I diffed the file across the whole range and it is the path
plus a four-line comment, with the ledger's content untouched, exactly as claimed
(deviation 7). The repair is correct and minimal, and it was genuinely forced: Item 3's close
(`cec3f03`) moved the artifact and left this module raising `FileNotFoundError` at collection,
which took the whole suite's collection down.

The residual is structural: a live agreement gate whose authority document lives in a directory
the convention treats as frozen. The next item that changes fixture coverage must either edit a
closed artifact or let the ledger go stale.

**What should change:** an owner decision on where the ledger lives — a durable home outside
`active/`/`completed/`, or an explicit note that this archived file stays editable.

### F6 (Low) — the only working authoring route for a unit-carrying gate is recorded in a fixture header, not where a modeler looks

`tests/fixtures/predicate_unit_annotation/model.sysml:23-32` and `verification.md:103-109`
record two facts a modeler needs: a one-sided `gap_width >= 0.25 [m]` blocks on
`block_ordering_category_pair` (bare `Real` is category `real`, an annotated literal is
`quantity`), and the obvious alternative — a declared quantity type on the attribute — is
refused by codegen as an unsupported exact type. So the *only* supported spelling annotates
both operands. Item 5 is about to write 65 gates.

`docs/architecture/modeling-assumptions.md` §8 gained "What a block tells you" but does not
state this authoring rule. (The underlying dimension-only-typing limit is not new — the ratified
concept records it — but its practical consequence for authoring is.)

**What should change:** one sentence in §8's real-equality/idiom area, or a note in the epic's
Item 5 scope.

### F7 (Medium) — the B2-false surfacing is loud, but not where Item 5 will find it

Press-point 5, answered on the merits. The finding **is** surfaced correctly in substance: a
unit written on a constraint usage binding (`in tol = 0.05 [m];`) is dimensionally inert to the
profile, because a bound formal takes its operand category from the definition's declared type
and the binding's annotation never reaches `classify_ordering`. It was *measured*, not inferred
(probe P3c binds a length against a time and the profile admits it). It is labelled under
capture-fidelity §4, the dependent conclusion is parked ("this item neither widens nor narrows
the profile"), the design's bet B2 is explicitly named as false for that lane, and nothing was
silently resolved. That is the rule applied correctly, three times over:
`verification.md:204-218`, `plan.md` Phase 3 notes, `reason-codes-reconciliation.md:87-92`.

**The gap is placement.** All three homes are inside
`.project/active/constraint-predicate-hardening/`, which `/_my_close` archives. The durable
artifact Item 5's spec author reads is the epic
(`.project/backlog/epic_constraint_semantics_contract.md`), and its Item 5 section (`:676`+) is
unamended. The same applies to the second surfaced limit — the location is the constraint
usage's line, not the offending term's — which Item 5 will hit on every long predicate.

This matters more than it looks: the blessed tolerance-band recipe *is* this shape, so a wrong
unit in a band binding is admitted silently by a gate whose whole purpose is to catch wrong
physics.

**What should change, before close:** carry both findings into the epic's Item 5 **Current
State** / **Required Reading**, as one line each with a path-cite back to the item folder.

---

## Verified, as positives worth recording

These were checked against the diff, not against the design's prose.

- **D1's widening bound holds.** `_pending_aliases.append` (`elaborate.py:853`) and
  `_pending_expressions.append` (`:889`) both sit inside `_create_value_node`, *after* its
  unwrap at `:806` — so the alias and computed lanes were already top-level-unwrapped and D1
  newly changes them only for a nested annotation. The third append (`:1160`, the constraint
  predicate lane) had no unwrap, and is newly reached wholesale. Exactly M6b.
- **The dispatch-ordering safety argument holds.** `annotated_ast_value`
  (`extraction/unit_annotation.py:51-58`) returns the expression unchanged unless it is an
  `OperatorExpression` whose operator is `[`, and passes `None` straight through — so the
  head unwrap at `elaborate.py:2432` cannot preempt the `FeatureChainExpression`-before-
  `OperatorExpression` dispatch at `:2435`, and the `None` guard at `:1701` is safe.
- **M7's escape route is real.** Two external walk callers (`:2271`, `:2337`); only `:2337`
  catches, and only `_UnsupportedExpressionError`. `SI_EDGE_DANGLING` escapes both.
- **D2 is one unwrap, at one site** (`:1701`), feeding both `_binding_evidence` and the literal
  read, as designed. No new classification branch.
- **D5/D6 implemented as designed** (`elaborate.py:320-366`): one key
  `(basename, line, column, reason, construct, message)` for both de-dup and order, each field
  normalized at construction, `column` never rendered, suffix omitted when `file` is empty or
  `line` is absent.
- **D7 honored.** `tests/conformance/test_elaboration_payload_identity.py` has **no diff** in
  the range.
- **Marker arithmetic reconciles exactly.** The `f3b3131 → 89fc38f` test diff removes 5 markers
  in `test_predicate_unit_annotation.py`, 3 in `test_constraint_binding_unit_annotation.py`,
  4 in `test_blocked_chain_diagnostic.py`, and one module-level `pytestmark` covering the 8
  tests in `test_render_block_reasons.py` — **20**, matching the red run's 20 failures exactly.
  No marker was removed without a corresponding red row, and no red row survives marked.
- **The red capture is internally consistent.** The progress line (`FFFF.F` / `FFF.` /
  `FFFF....` / `FFFFFFFF`) sums to 20F/6P, matches the 20 `FAILED` summary rows, and matches the
  named 6-green table file by file. The four distinct failure signatures (the
  `SI_OCCURRENCE_MISSING` raise, the two `KeyError`s, the tautology string, the
  `ImportError`) are each the right failure for their row.
- **Deviation 2 is design-consistent and the plain lane is not orphaned.** The design's premise
  (plain + blocked catalogs unassessed, so read the detail there) was factually wrong: a plain
  constraint never consults the profile at all and emits no block reasons, so there would be no
  detail to read. Switching to asserted + non-strict elaboration is the only way to read the
  string, and `test_an_asserted_blocked_chain_still_halts` keeps the Item 2 halt pinned. The
  plain half stays pinned by `tests/fixtures/constraint_domain_plain_forms`, which exists.
- **Message truth holds.** The advertised rewrite `in outer_radius = bioshield.outer_radius;` is
  a plain chain binding — admitted under Q4, and untouched by P3's finding (which concerns
  *unit-annotated* bindings being inert, not refused). Invariant 6 correctly did not fire.
- **Invariant 8 (single line) is pinned at the one place that builds the string**
  (`test_render_block_reasons.py:85-91`) and at the rendered fixture
  (`test_blocked_chain_diagnostic.py`), and `_render_block_reasons` joins only with `"; "`.
- **Frozen twins and whitespace.** No commit in the range touches
  `tests/fixtures/catf_mfe_model` or `tests/fixtures/catf_mfe_d5`;
  `git diff --check f3b3131~1 89fc38f` is clean.
- **Concurrency, checked not assumed.** `4e5bc71` (epic Item 7) accounts for the entire epic-file
  diff in the range — Item 4 added nothing there. The Item 3 archival target
  `.project/completed/20260813_constraint-coverage-policy/expected-coverage.md` exists at HEAD,
  so deviation 7's repair still resolves. `CURRENT_WORK.md` left untouched.

---

## Requested live probes

The orchestrator runs these and appends an addendum. Every criterion marked *author-reported*
below turns on R1–R4.

**R1 — codegen suite, at `89fc38f`.**
```
cd /home/reid/1cfe/sysml-codegen-item7-rebuild
set -a; source /home/reid/1cfe/agentic-mbse/.env; set +a
/home/reid/1cfe/item7-rebuild-venv/bin/python -m pytest -q -rs
```
*Discriminating:* `2010 passed, 0 failed, 34 skipped, 79 deselected, 0 xfailed, 0 xpassed`, and
the `-rs` skip reasons are all content-shape (`test_calc_compat_parity.py`,
`test_computed_attribute_golden.py`) with **zero** license skips. Any license-skip line means
the reported run was not a full run and criteria 1–5 revert to unverified.

**R2 — codegen lint, at `89fc38f`.** `ruff check src` → **12**; `mypy src` → **55**.
*Discriminating:* any number above baseline fails the zero-new gate (spec `[HARD]`).

**R3 — companion baseline, the one the spec never stated (brief point 6).** Do **not** accept
"identical set with the change stashed." Establish the baseline at the pre-change commit
directly:
```
git -C /home/reid/1cfe/agentic-mbse-item7-rebuild worktree add /tmp/amb-bc69f04 bc69f04
cd /tmp/amb-bc69f04
set -a; source /home/reid/1cfe/agentic-mbse/.env; set +a
/home/reid/1cfe/item7-rebuild-venv/bin/python -m ruff check src | tail -1
/home/reid/1cfe/item7-rebuild-venv/bin/python -m mypy src | tail -1
/home/reid/1cfe/item7-rebuild-venv/bin/python -m pytest -q 2>&1 | grep -E "^FAILED|passed|failed"
```
then the same three at `0a52942`.
*Discriminating:* ruff `1` → `1`, mypy `108` → `108`, and the **failing node IDs** (not the
count) identical between the two commits. A count match with a membership change would mean a
new failure masked an old pass.

**R4 — the companion change, read directly (D3/D9, unreadable from this session).**
```
git -C /home/reid/1cfe/agentic-mbse-item7-rebuild show 0a52942
git -C /home/reid/1cfe/agentic-mbse-item7-rebuild diff --check bc69f04 0a52942
```
*Discriminating:* the diff touches `src/agentic_mbse/sysml/executable_profile.py` only; adds a
`_feature_chain_message`-style helper plus `message=` at **both** chain-block sites (`:535-537`
and `:702-707` — one site alone means half the lane is uncured); **no edit to `REASON_CODES`**
(D9); `diff --check` clean. If a reason code was added or the second site was missed, D9 or
scope item 3 is not discharged.

**R5 — F1's discriminator: is the twins comparison hiding a real difference?** In
`tests/conformance/test_predicate_unit_annotation.py`, change `_input_wiring`'s row to
`(index, module_input.param_name.rsplit("__", 1)[-1], module_input.source.source_type)` and run
that file.
*Discriminating:* still passes → the rewrite was a naming artifact as claimed and the stronger
assertion can simply be kept. Fails → the twins differ in wiring and the rewritten assertion is
concealing it, which promotes F1 to a blocking finding.

**R6 — D1 blast radius, measured rather than argued.** At `89fc38f`, delete the single unwrap
line `expression = self._without_unit_annotation(expression)` at
`src/sysml_codegen/elaboration/elaborate.py:2432` and run the full suite (R1's command).
*Discriminating:* the only failures are Item 4's Defect-A rows
(`test_predicate_unit_annotation.py`) — confirming no currently-green behavior anywhere in the
suite depends on the widening, which is the empirical version of design bound M6b. Any *other*
file failing means D1 changed behavior the design did not account for. Revert after.

**R7 (optional, backs F6).** Elaborate a one-sided variant of `predicate_unit_annotation`
(`gap_width >= 0.25 [m]`, LHS unannotated).
*Expected:* blocks on `block_ordering_category_pair`. Confirms the fixture header's authoring
claim before it is copied into `modeling-assumptions.md`.

---

## Criterion-by-criterion

Spec success criteria (`spec.md:59-89`). "Static" = verified by reading code/tests/diffs in this
session. "Author-reported" = the implementation is verified static, the *run* is not.

| # | Criterion | Evidence | Status |
|---|---|---|---|
| 1 | Annotated predicate elaborates without `SI_OCCURRENCE_MISSING`; unit behavior unchanged both directions | Cure at `elaborate.py:2432`, bound verified against `:806`/`:853`/`:889`/`:1160`; `test_predicate_unit_annotation.py` unmarked; incompatible twin test present; `test_unit_annotation_values.py` untouched | **Static ✓** / run author-reported (R1) |
| 2 | End state is a working gate, pinned positively; inequality, not `== <literal> [unit]` | `test_the_cured_predicate_is_a_working_gate` asserts `disposition_kind == "eligible"`, `assessed_gate_count == 1`; fixture predicate is `gap_width [m] >= 0.25 [m]` | **Static ✓** / P1 verdict author-reported (R1) |
| 3 | The `:535` promise is true; any reason that cannot keep it is named in the record | `modeling-assumptions.md:551-554` rewritten; §8 "What a block tells you" added; `reason-codes-reconciliation.md` covers all 23 `block_*` against the orchestrator's own verbatim `REASON_CODES` read | **✓** — the promise is rewritten to what is true (1 names the fix, 11 the shape, 10 reason-only, 1 mixed, all 23 gain a location), and the residue is named, not implied |
| 4 | Blocked chain names the written reference and states the supported rewrite | `test_blocked_chain_diagnostic.py:56-69`; rewrite is a plain chain binding, i.e. a supported form | **Static ✓** / rendered string author-reported (R1); companion half needs R4 |
| 5 | Multi-chain: each distinct reference, deterministically | `count == 2` over 3 occurrences; byte-identity across runs; `_render_block_reasons` key verified line by line at `elaborate.py:320-343` and pinned by 8 unit tests incl. `None` line/column and construct-only-difference | **Static ✓** / run author-reported (R1) |
| 6 | Kept characterizations committed before the fixes, each demonstrated red | `f3b3131` precedes every fix commit; 20 markers removed reconcile exactly with 20 captured red rows; capture is verbatim and self-consistent | **✓ with F1** — red-first integrity holds; one row's assertion was rewritten between red and green (disclosed in `plan.md`, missing from `verification.md`) |
| 7 | No regressions, esp. `test_unit_annotation_values.py` and `test_elaboration_payload_identity.py:236-266` | `test_elaboration_payload_identity.py` has **no diff** in the range (D7 honored, verified); `test_unit_annotation_values.py` likewise untouched | **Static ✓** / green run author-reported (R1) |
| 8 | Focused + full suites, `ruff` 12, `mypy` 55, `git diff --check`, exact counts recorded | `git diff --check` verified clean by me; counts recorded per phase in `plan.md` and consolidated in `verification.md` | **Partly ✓** — counts *recorded* ✓, whitespace ✓; the numbers themselves need R1–R3, and the **companion baseline was never stated in the spec** (R3) |

Epic Item 4 criteria (`epic_constraint_semantics_contract.md:646-652`) map onto spec 1, 4+5, 7,
and 8 respectively; same statuses.

Design decisions D1–D9 and invariants 1–8: all honored. D1's lane inventory, M6b's widening
bound, M7's refusal route, D2's single unwrap and its two admitted shapes, D3's split, D4's row
count, D5's key, D6's rendering, D7's untouched test, D8's mechanism, and D9's no-new-reason-code
were each checked against the diff. D9's companion half is the only one I could not read (R4).

---

## Certification

**Certify-with-residuals.** The shipped behavior is what the spec asked for, built the way the
design said, with an evidence trail that is honest about its own limits. The product-lens ledger
gate is DISPOSED with no unresolved BLOCK at item or epic level, and the one structural smell
that fired is resolved in the Product Judgment above rather than left sitting in a rubric.

**Conditions on the certification:**

1. **R1–R4 return as reported.** Every suite count, lint number, and rendered string in
   `verification.md` is author-reported; I could not execute anything. R3 in particular replaces
   an unstated companion baseline with a measured one, and R4 is the only way to see the
   companion half of D3/D9.
2. **F7 is discharged before close** — carry the B2-false finding and the usage-line location
   limit into the epic's Item 5 section. As written, both die in the archive.
3. **F1's deviation 8 is added to `verification.md`**, and R5 decides whether the rewritten
   assertion should be strengthened back.

F2, F3, F4, F5, F6 are record-and-decide: none changes behavior, each is a claim, a pin, or a
placement that should be tightened.

**Tracking marked:** spec criteria 1, 2, 3, 4, 5, 6, 7 marked as verified-static (criterion 6
carries F1 as a noted residual); criterion 8 left unmarked pending R1–R3. Epic Item 4 criteria
1 and 2 marked; 3 and 4 left unmarked pending probes, and the Item 4 heading is **not** given ✅
because the verdict is conditional. `CURRENT_WORK.md` deliberately not touched — a concurrent
owner session holds an uncommitted edit to it.

**Not checked:**
- **Anything requiring execution.** No test was run, no count reproduced, no lint invoked. All
  suite/lint/probe numbers are the implementer's.
- **The entire companion side.** `/home/reid/1cfe/agentic-mbse-item7-rebuild` is unreadable from
  this session. `0a52942`'s content, the two block-site edits, the `REASON_CODES` non-change, and
  the companion lint/suite baselines are unverified (R3, R4). The companion-evidence file and the
  reconciliation's 23-row table rest on the orchestrator's earlier read, which I could not
  re-confirm.
- **TEAx.** `/home/reid/1cfe/teax` was not read; "untouched, on `constraint-semantics-item3`" is
  author-reported.
- **The generated-output layer.** I traced elaboration and diagnostics. Whether the new fixtures
  produce sane generated packages beyond the catalog/coverage assertions was not examined.
- **The reconciliation's per-reason grades.** The claim that 11 of 23 carry explicit actionable
  messages rests on companion source I cannot open; I checked the table's totals and internal
  consistency, not its content.
- **Whether `predicate_unit_annotation_incompatible` remains a genuine block** after any future
  profile change — it is a companion-path guard by design, and design review A1 already recorded
  that it discriminates nothing on the codegen side.

---

## Orchestrator addendum — requested live probes executed (2026-08-13)

All probes run by the orchestrator (full permissions) at codegen `89fc38f` + companion
`0a52942`, licensed interpreter, mutations reverted after measurement.

- **R1 — PASS.** Full licensed codegen suite: **2010 passed, 34 skipped, 0 failed, 79
  deselected**; `-rs` shows 34 skip lines, **zero** matching "license". Criteria 1–5's runs
  are no longer author-reported.
- **R2 — PASS.** `ruff check src` → **Found 12 errors**; `mypy src` → **55 errors in 11
  files**. Zero-new holds.
- **R3 — PASS.** Companion control done as a single-file swap (the whole diff is one file):
  suite at tip and with `executable_profile.py` at `bc69f04` both give **10 failed / 1821
  passed / 1 skipped**, and the failing **node IDs are byte-identical** (diff empty). Lint at
  the baseline profile: ruff **1**, mypy **108 in 26 files** — same as tip. The companion
  numbers are pre-existing; zero-new holds. File restored, tree clean.
- **R4 — PASS.** `0a52942` touches only `src/agentic_mbse/sysml/executable_profile.py`
  (+42/−3): one `_feature_chain_message` helper, passed at **both** chain-block sites; zero
  added lines mention `REASON_CODES`; `git diff --check bc69f04 0a52942` clean.
- **R5 — F1 stays a residual; NOT promoted.** The strengthened assertion (leaf param name in
  the row) **fails**, but the printed wirings show why: both twins have identical edges
  (`(0, entry_point)`, `(1, module_output)`); the only difference is the constraint module's
  identity param (`predicate_unit_annotation_the_host_gap_guard_<hash>` vs
  `…_bare_…_<hash>`), which embeds the *package* name with no `__` separator, so the probe's
  `rsplit("__", 1)` cannot strip it. A naming artifact exactly as the implementer disclosed;
  no edge is concealed. The probe as specified could not have passed for any correct
  implementation of two differently-named packages.
- **R6 — PASS, with one precision.** Deleting the unwrap at `elaborate.py:2432` fails exactly
  **7** tests: 5 in `test_predicate_unit_annotation.py` plus 2 population-oracle rows
  parameterized over the same `predicate_unit_annotation` fixture
  (`test_constraint_population_oracle.py` re-elaborates every fixture). All 7 are
  Item-4-fixture-scoped; **no pre-existing behavior anywhere in the suite depends on the
  widening** (2003 passed otherwise). The audit's "only `test_predicate_unit_annotation.py`"
  expectation was too narrow by one file, not wrong in substance.
- **R7 — PASS.** The one-sided variant (`gap_width >= 0.25 [m]`, LHS unannotated) refuses
  with `SI_CONSTRAINT_BLOCKED … block_ordering_category_pair: ordering '>=' requires
  Integer/Real operands or two Quantity operands; got real/quantity. Rewrite both operands as
  one admitted numerical pair. [model.sysml:53]` — the fixture header's authoring claim is
  true, and the rendered message carries reason, categories, rewrite, and location.

**Effect on the verdict:** Certify-with-residuals stands. Criterion 8 and the
author-reported runs are now independently verified; F1 is confirmed a record-completeness
residual (not concealment); F7's placement cure remains open for the cure pass.
