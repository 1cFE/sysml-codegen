# Design Review: Predicate Defect Hardening (CONSTRAINT-SEMANTICS Item 4)

**Design:** `.project/active/constraint-predicate-hardening/design.md`
**Spec:** `.project/active/constraint-predicate-hardening/spec.md`
**Review File:** `.project/active/constraint-predicate-hardening/design-review.md`
**Date:** 2026-08-13
**Verdict:** **Revise** (7 must-fix, all local to the design text or a key definition; no seam moves)

---

## The Point

A modeler writing an asserted physics gate must be stopped only by the product's real limits,
and when stopped, must be told what to write instead
(`rulings-20260812.md` Q8 **[INHERITED]**).

Neither holds today. The *supported* form — an inequality carrying a unit-annotated literal —
is refused by a bug that has nothing to do with the limit (`SI_OCCURRENCE_MISSING` against
`SI::metre`). The *unsupported* form — a feature chain in a predicate body — is refused with
`feature_chain: block_feature_chain`, naming no reference, no location, and no rewrite.

Item 5 rewrites 65 CATF constraints into the bindings-only recipe, and that diagnostic is the
instrument the migration is performed with. A tautology makes 65 rewrites a manual hunt. The
published promise at stake is `docs/architecture/modeling-assumptions.md:535` — "If the profile
BLOCKs an asserted constraint, the generation error names the exact construct to fix" — which is
false today for the chain block.

---

## Fundamental Assessment

**Sound.** This is the right piece of work and the right approach.

The design's core claim — both defects are failures of *reach*, not of policy — holds up under
code reading. The unit rule already exists with one owner (`extraction/unit_annotation.py:1-28`)
and is applied at exactly one site (`elaborate.py:757`, inside `_create_value_node`); the cure
adds call sites to that one rule rather than minting a second. Defect B adds a `message=`
argument at two companion sites that already hold the payload. No new abstraction survives the
review except one private renderer helper, which earns its place by making the ordering key
testable.

The four spec-stage product-lens findings are all discharged by the design: F1 (a *working
gate*, inequality demonstration — design's fixture plan and test plan), F2 (the fourth lane is
cured, D2), F3 (catalog carrier + assessed disposition + coverage in the test plan), F4 (the
`:535` promise cited by line, and the residue named). The lens's `:538` citation was stale;
`:535` is correct at HEAD (verified).

**Neither design-level smell fires.** No consumer compensates for a producer guarantee — the
split puts the message where the block is decided (companion) and the location where the source
is known (codegen), which is the correct owner on each side. No invariant changes hands: the
profile keeps deciding what is admitted, `unit_annotation.py` keeps owning the unit rule.

**One structural correction to the design's own risk ranking** (see Advisory A1): the profile
decision is computed at `elaborate.py:403` via `evaluate_identified_profile(identified)`, from
the companion's own extraction, *before and independent of* the reference walk. So D1 cannot
reach the profile's dimension checking by construction. B2 — labelled "the largest risk" — is
structurally not at risk from D1. That does not weaken the design; it means the risk section
points at the wrong thing.

---

## Dimensional Review

### 1. Spec Compliance
**Assessment:** Concerns

Every success criterion has a design element and a named test. Two gaps:

- **The residue list is incomplete.** Success criterion 3 requires that any block reason still
  unable to keep the `:535` promise be *named in the item's record*. The design's residue list
  ("The Message Shape") lists `block_real_equality_requires_tolerance`, `block_xor`,
  `block_implies`, `block_incompatible_dimensions`, `block_unknown_exact_unit`,
  `block_unit_conversion_required`, and assert-by-reference. It **omits `block_invocation`**,
  which is the first entry in the published block list
  (`docs/architecture/modeling-assumptions.md:481`). Must-fix M3.
- **Invariant 3 as written contradicts D2.** "Nothing newly admitted, nothing newly blocked" is
  true of the *profile's* admitted set (which this item does not touch) and false of codegen's
  readiness refusals, which D2 deliberately shrinks. An implementer reading the invariants
  literally has a conflict on the page. Must-fix M5.

Provenance is carried faithfully. The spec's `[HARD]` unit rule survives whole with its owner
named (invariant 1). Spec Open Question 1 is resolved in the design as `[AGENT]` with the
orchestrator's rule cited, not silently upgraded. No `[INFERRED]` spec item is treated as fixed.

### 2. Pattern Consistency
**Assessment:** Pass

`_without_unit_annotation` (`elaborate.py:862-878`) is reused, not re-implemented — invariant 1
forbids a stray `operator == "["` test, which is exactly the failure mode this codebase has
already paid for once. The de-dup precedent is real: `_record_readiness`
(`elaborate.py:1867-1870`) collapses on `(formal, code)`. The fixture idiom (`Noop` calc def so
the pipeline has a module) matches `tests/fixtures/constraint_blocked_profile/model.sysml`
verbatim. The bare/annotated twin-fixture pattern matches
`tests/fixtures/unit_annotation_lanes/`.

### 3. Abstraction Quality
**Assessment:** Pass

One new named thing across two repos (`_render_block_reasons`). The justification given — the
ordering key becomes testable on its own — is the right reason, and `_build_constraint_nodes`
is already carrying the node-minting loop. Nothing here is over-built.

### 4. Duplication Avoidance
**Assessment:** Pass

D3's rejected alternative (codegen re-derives the written reference from the usage AST) is
correctly rejected: it would re-implement the profile's chain detection in the repo that does
not own the decision. D9 (no new `REASON_CODES` entry) is right — the reason did not change,
only its explanation was missing.

### 5. Data Structure Clarity
**Assessment:** Concerns

The de-dup key and the order key are the item's only real new data structure, and both have
defects:

- **The order key is not total and is not type-safe.** `(file, line, column, reason, message)`
  omits `construct`, which the de-dup key includes. Two entries surviving de-dup that differ
  only in `construct` sort as ties, and Python's stable sort then falls back to the companion's
  *walk order* — precisely the authority D5 rejects. Separately, "a missing location normalized
  to `""`/`-1`" handles a `None` **LocationFact**, but not a present `LocationFact` with a
  `None` `column` or `line`; comparing `None` with `int` raises `TypeError` at sort time.
  Must-fix M1.
- **D6 does not say what renders when the location is absent.** The design specifies the
  ordering behaviour for a missing location but not the rendered text. Must-fix M4.
- **`file` in the keys is presumably an absolute path** (D6 basenames it for *rendering* because
  absolute paths are a known baseline trap in this repo). Using the raw path in the sort and
  de-dup keys is defensible but inconsistent; basenaming in both is one line and removes the
  question. Advisory A4.

### 6. Route Safety
**Assessment:** Concerns

The three seams are explicit and correctly located. The unstated part is the *bound* on D1's
widening, which is what the concern about "other expression lanes" comes down to. Read at
`c93a5e3`:

- `_expression_references` has exactly two external callers: `:2220` is **`_resolve_aliases`**,
  and `:2286` is `_resolve_computed_expressions`. The design calls `:2220` the
  computed-attribute lane; that is wrong — computed attributes enter at `:2286` alongside
  predicates, and `:2220` is the typed-alias lane. Must-fix M6 (a) — a wrong lane inventory in
  the one paragraph that justifies the seam.
- The walk is **recursive** (`:2411`), so "at the head" means the unwrap fires at every node.
  That is what makes the cure work — the annotation is nested under the comparison operator, so
  an entry-level unwrap would be a no-op. **The design's D1 claim is correct**, and its ordering
  argument is correct too: `annotated_ast_value` returns the expression unchanged unless the
  operator is literally `[`, and `FeatureChainExpression`'s operator is not, so the
  chain-before-operator dispatch at `:2374-2377` cannot be preempted.
- **The alias and computed lanes are already unwrapped at the top level.** Both
  `_pending_aliases.append` (`:805`) and `_pending_expressions.append` (`:841`) sit inside
  `_create_value_node`, which unwrapped `expression` at `:757`. So D1 newly changes those two
  lanes only for a *nested* annotation (`= a * 2.0 [m]`), and changes the predicate lane
  wholesale (nothing unwraps there today). Every one of those shapes fails today with
  `SI_OCCURRENCE_MISSING` (or, in the alias lane, "does not contain one exact reference"), so
  the widening admits models that are currently refused and changes no currently-green
  behaviour — **unless** a `[`-annotation's second operand resolves to a user-model feature, in
  which case a real dependency edge would disappear. That bound belongs in D1 in writing.
  Must-fix M6 (b).
- **A new error route opens.** `_without_unit_annotation` converts a malformed annotation's
  `ValueError` into `ElaborationInvariantError(SI_EDGE_DANGLING)`. Placed inside the walk, that
  exception now escapes through callers that catch only `_UnsupportedExpressionError`
  (`:2286-2295`), so a malformed annotation anywhere in a predicate becomes a hard elaboration
  refusal rather than a readiness finding. That is probably the right answer, but it is an
  unstated route change. Must-fix M7.
- **D2's widening is also larger than stated.** Unwrapping the binding expression at `:1652`
  cures `in tol = 0.05 [m]` (the literal case the design describes) *and* newly admits
  `in tol = other_feature [m]`, which today falls to `expression_evidence` →
  `SI_EXPRESSION_SOURCE_UNSUPPORTED` and after the cure classifies as a reference binding.
  Genuine expression sources stay refused — verified: `annotated_ast_value` returns `a + b`
  unchanged because its operator is `+`, so `_binding_evidence` (`:1839-1846`) still falls
  through to `expression_evidence` and `_unsupported_code` (`:1848-1858`) still maps it to
  `SI_EXPRESSION_SOURCE_UNSUPPORTED`. The reference-under-annotation case is consistent with the
  rule and is arguably a bonus, but it is a second newly-admitted shape and should be named (and
  ideally pinned by the fixture). Must-fix M6 (c).

### 7. Bets & Decisions Integrity
**Assessment:** Concerns

Each bet states a falsifier and a discriminating probe — the right shape. Three problems:

- **B2's failure mode is unreachable through D1, and the design ranks it as the largest risk.**
  The profile verdict is computed at `elaborate.py:403` from the companion's own extraction of
  the usage, entirely independent of the codegen reference walk that runs later in resolution.
  So "the fix silently disables `block_incompatible_dimensions`" cannot happen via D1. The
  incompatible-unit fixture is therefore a **regression guard, not a discriminator** — it would
  pass whether or not the walk drops the unit, which is exactly the "test that passes only
  because it selects one interpretation" shape the spec-stage lens flagged at item4-F1. Keep the
  fixture (it is cheap and it pins the companion path), but say what it actually guards, and
  move the genuine unit-loss risk to where it lives: D2's binding lane, where the annotation is
  the carrier of both value and unit, guarded by P3. Advisory A1 — but the honesty correction to
  B2 and to "Potential Risks" is must-fix M2's sibling and should land with the revise.
- **A hidden bet, now surfaced:** *the rendered detail contains no newline.* Two existing
  consumers depend on it —
  `tests/conformance/test_elaboration_payload_identity.py:243` matches
  `"SI_CONSTRAINT_BLOCKED.*blocked_guard.*block_real_equality_requires_tolerance"` where `.`
  does not cross a newline, and `project.py:97` folds the same detail into `ProjectionError`'s
  message for the `pytest.raises` at `:265`. The design's message examples are shown wrapped
  across lines in the doc; if that wrapping reaches the string, D7's "this test is not edited"
  is false. Must-fix M2.
- **D4's supporting citation is unsupported.** The design says the row count is what "the Item 2
  disposition contract, the coverage account (`generation/coverage.py`), and
  `test_elaboration_payload_identity.py:250`" count on. `generation/coverage.py` contains no
  reference to diagnostics at all; coverage counts catalog rows and dispositions. The decision
  is still right — `test_elaboration_payload_identity.py:250` (`len(blocked) == 1`) and
  `tests/unit/test_constraint_usage_record_mint.py:94` (asserts *no* `SI_CONSTRAINT_BLOCKED`
  row) both hold it — but the citation should be corrected rather than carried into the plan.
  Advisory A2.

Confirmed against code, in the design's favour:

- **D7 holds.** All three assertions at `test_elaboration_payload_identity.py:236-266` are
  regex/substring matches over one diagnostic; the fixture (`assert constraint exact { value ==
  5.0 }` in `tests/fixtures/constraint_blocked_profile/model.sysml`) blocks on
  `block_real_equality_requires_tolerance`, not a chain, so it keeps the companion default
  message and gains only a trailing ` [file:line]`. No edit needed — conditional on M2.
- **D3's payload claim holds** (P4 verdict, orchestrator's static read: `chain_segments`
  includes the root, and `source_name` carries the full authored text as a second carrier).
- **D2's mechanism claim holds.** `expression` is read at `:1652` and used by `_binding_evidence`
  (`:1656`) and `extract_literal_value` (`:1657`); one unwrap at `:1652` covers both, and
  nothing else in `_collect_bound_members` reads the raw expression. (The design cites `:1651`;
  cosmetic — Advisory A5.)

### 8. Reader Comprehension
**Assessment:** Pass

"Both defects are the same failure of *reach*, not of policy" is the right frame, stated before
the mechanism. The three-seam ASCII map, the worked message examples, and the invariant list
each give a reader something to hang the details on. A reader unfamiliar with the item can skim
this once and come away with the model. No coined jargon standing in for an explanation.

---

## Issues by Severity

### Critical
None. No finding moves a seam or changes the item's shape.

### Major (must-fix before implement)

- **M1 — the order key is not a total order and can raise at sort time (D5).** Add `construct`
  (make the order key the full de-dup identity), and normalize *each* field independently —
  `file or ""`, `line if line is not None else -1`, `column if column is not None else -1` —
  rather than only the whole-`LocationFact`-is-`None` case. As written, a `LocationFact` with a
  `None` column sorts `None` against `int` and raises `TypeError`; and two entries differing only
  in `construct` fall back to the companion's walk order, which D5 explicitly refuses to trust.
- **M2 — state that the rendered detail is a single line, with no newline.**
  `test_elaboration_payload_identity.py:243` and `project.py:97` → `:265` both depend on it
  (regex `.` does not cross a newline). D7's "not edited" claim is conditional on this. Add it to
  the invariants, and have the D3 fixture assert `"\n" not in detail`.
- **M3 — the residue list omits `block_invocation`** (`modeling-assumptions.md:481`). Success
  criterion 3 requires every reason that still cannot keep the `:535` promise to be named.
- **M4 — D6 does not say what renders when `location` is `None`.** Specify it (recommend: omit
  the ` [file:line]` suffix entirely rather than render a placeholder), so the message is a
  function of the payload and not of the renderer's mood.
- **M5 — invariant 3 contradicts D2 as written.** Scope it: *the profile's* admitted set is
  unchanged in both directions; codegen's readiness-refused set shrinks by exactly the
  unit-annotated binding forms D2 names.
- **M6 — D1/D2's reach is mis-stated in three places, and the widening bound is unstated.**
  (a) `:2220` is `_resolve_aliases`, not the computed-attribute lane; computed attributes enter
  at `:2286` with predicates. (b) Both the alias and computed lanes are already unwrapped at the
  top level by `_create_value_node` (`:757`), so D1 newly affects those lanes only for *nested*
  annotations — all of which fail today. State the bound: no currently-green behaviour changes,
  with the one exception that a `[`-annotation whose second operand resolves to a *user-model*
  feature would lose a real dependency edge. (c) D2 newly admits
  `in x = <reference> [m]` as well as the literal form; genuine expression sources
  (`a + b`) stay refused, verified. Name the second admitted shape.
- **M7 — D1 opens a new hard-refusal route.** Inside the walk, `_without_unit_annotation` raises
  `ElaborationInvariantError(SI_EDGE_DANGLING)` on a malformed annotation, which escapes callers
  that catch only `_UnsupportedExpressionError` (`:2286-2295`). Decide it explicitly (a hard
  refusal is defensible) and record it as a stated route, not a side effect.

### Minor (advisory)

- **A1 — re-rank the risks and re-state B2.** The profile runs at `elaborate.py:403` from
  companion facts, independent of the walk, so D1 cannot disable dimension checking. The
  incompatible fixture guards the companion path (worth keeping); the real unit-loss exposure is
  D2's binding lane, guarded by P3. As a corollary, P2's "Admits → D1 is the wrong seam" branch
  is close to dead code — run it once as cheap insurance, but do not gate step 2 on it. That
  reorders "De-risk first: P2, then P1" toward P1 and P3.
- **A2 — correct D4's citation.** `generation/coverage.py` does not count diagnostics. The row
  count is held by `test_elaboration_payload_identity.py:250` and
  `tests/unit/test_constraint_usage_record_mint.py:94`.
- **A3 — D8's red evidence is a commit-message claim, not a machine check.** The mechanism is
  sound (strict xfail keeps both trees green; XPASS forces the marker's removal in the fix
  commit, so the pairing cannot silently rot). But "recorded in the commit message" is
  unfalsifiable after the fact. Capture the marker-removed failure *output* into the item's
  close record, not just a sentence.
- **A4 — basename `file` in the de-dup and order keys too**, not only in the rendering (D6), so
  no key carries a checkout-dependent absolute path.
- **A5 — line-number drift:** the binding expression is read at `:1652`, not `:1651`.
- **A6 — `written_text` loses the annotation for the reference case too.** D2's stated
  consequence covers the literal (`"0.05"` not `"0.05 [m]"`); the same applies to
  `reference_evidence`'s CST read after the unwrap. Extend the note.

---

## Recommendations

1. Fix the two key definitions first — M1 (total, type-safe order key) and M2 (single-line
   invariant). Those are the only findings that would produce a flaky or failing landing rather
   than a documentation gap.
2. Correct the reach paragraphs, M6 (a)/(b)/(c) and M7, in D1/D2. The seams are right; the
   justification text is what is wrong, and the plan stage will read it as ground truth.
3. Close the two spec-criterion gaps: M3 (`block_invocation` in the residue) and M5 (scope
   invariant 3 to the profile).
4. Say what renders with no location (M4).
5. Re-state B2 and the risk order per A1, and correct D4's citation per A2. The design is more
   robust than it claims on B2; saying so accurately keeps the implement stage from spending its
   de-risking budget on the wrong probe.

Everything else stands. The seams (walk head, binding read, companion `message=`), the split of
responsibility across the two repos, the one-diagnostic-richer-detail decision, the fixture
plan, the landing order, and D7's "no test edit" all survive the code check.

---

## Resolutions

_(Stage 4 — to be filled in with the owner's/orchestrator's calls. Nothing recorded yet.)_

---

**Overall:** **Revise**
**Next Steps:** Record resolutions above, then return to the design-agent session (or re-run
`/_my_design`) pointed at this review to incorporate. The reviewer does not edit the design.
All seven must-fix items are edits to `design.md` text or to the D5 key definition; none
requires re-deciding a seam, so a second full review is not warranted — a diff read against
M1–M7 is enough.

---

## Reviewer's evidence note

Codegen citations were opened this session at `c93a5e3`:
`extraction/unit_annotation.py:44-57`; `elaborate.py:403`, `:753-841`, `:862-878`, `:1097-1108`,
`:1652-1662`, `:1839-1858`, `:1860-1892`, `:2220`, `:2286-2295`, `:2371-2412`, `:2454-2470`;
`project.py:97`; `generation/coverage.py` (grep, no diagnostic references);
`tests/conformance/test_elaboration_payload_identity.py:236-266`;
`tests/unit/test_constraint_usage_record_mint.py:80-95`;
`tests/fixtures/constraint_blocked_profile/model.sysml`;
`tests/fixtures/unit_annotation_lanes/model.sysml`;
`docs/architecture/modeling-assumptions.md:475-490`, `:535`.
Companion claims were taken from `probes/companion-evidence.md` (orchestrator-verified at
`bc69f04`); this sandbox cannot read that checkout. Nothing was executed — no license-gated run
was made, so every behavioural claim here is a static read.

The product-lens was carried from the spec-stage ledger
(`.project/active/constraint-predicate-hardening/product-lens.md`) and re-checked against the
design rather than re-run as a subagent (this session's standing instruction bars spawning
agents unprompted). All four findings (item4-F1..F4) are discharged by the design; the ledger's
one fired smell (code-absence criterion) is cured by the design's working-gate test plan, and it
is noted above that the incompatible-unit fixture reintroduces a weaker version of the same
shape (Advisory A1). Neither structural smell fires. **Gate: DISPOSED — nothing blocks.**
