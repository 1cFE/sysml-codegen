# Independent Audit: PUSH-DOWN Epic (PR #8 + companion PR #10)

**Verdict:** Certify (after 2026-07-10 remediation — see "Remediation record" at the end).
Original verdict: Needs Work — the code was functionally sound and every gate green, but the
certification record over-claimed: two SC-D hazards were certified as resolved that were not
done, and Item 1's move contained undocumented behavior changes in an epic whose contract is
"moves, not behavior changes." All findings were remediated or honestly recorded the same day.
**Audited:** 2026-07-10 (independent of the 2026-07-08 epic audit; that audit's SC-D verdict
is contradicted below)
**Branches:** `push-down-item1-expression` in both repos
**Commits:** sysml-codegen `940d321` (= PR #8 head), agentic-mbse `48b5274` (= PR #10 head)

---

## Method

Five parallel audit agents, one per epic item plus one for cross-cutting criteria (SC-D,
SC-F, SC-G, dependency direction, PR scope). Each agent read the item's spec/design, then
compared every moved function body against the pre-move original (`git show main:...`),
verified re-export identity at runtime, and checked test migration for fires-on-shape truth.
Every major finding below was then re-verified first-hand by the orchestrating auditor.
Gates were re-run live, not read from records. Item audit.md verdicts were not trusted.

## Gate results (re-run this session, at the PR heads)

- **Suites:** sysml-codegen 2138 passed / 4 skipped; agentic-mbse 1290 passed / 1 skipped /
  33 deselected. Both match the recorded counts exactly.
- **Baselines:** `git diff main...HEAD -- tests/fixtures` empty in both repos — byte-identical,
  and neither PR touches a fixture file.
- **Ruff:** sysml-codegen src clean. agentic-mbse has 1 error (`extraction/index.py:146`,
  N806) that pre-exists on main in a file this branch never touches.
- **Mypy:** agentic-mbse 107 (= recorded baseline). sysml-codegen **98 vs main's 97** — a
  real +1 introduced by this branch (see finding 5). SC-E's "mypy src ≤ 97" is violated by one.

## Item verdicts (this audit's, not the prior record's)

| Item | Prior audit | This audit | Why |
|---|---|---|---|
| 1. Expression push-down | Certify | **Needs Work** | Non-mechanical move: 2 undocumented behavior changes (findings 2–3) |
| 2. Qualified-name split | Certify | **Needs Work** | Split itself is faithful; mandated R8 marker missing + false SC-D (finding 4) |
| 3. Hierarchy primitives | Certify | **Certify** | Faithful move, identity + TYPE_MAP verified; 2 minors |
| 4. Aggregation decomposition | Certify | **Certify** | Neutral, REQ-AST-10 order preserved, adapter equivalent; 3 minors |
| Cross-cutting | SC-A..G all certified | **SC-D FAIL**, rest pass | Q4 never done; Q6/R8 never done; both certified as resolved |

---

## Findings

### Major

**1. SC-D Q4: the `BindingInfo` rename never happened; the epic and the prior epic audit
certify it as done.**
`src/sysml_codegen/extraction/usage_extractor.py:55` still declares `class BindingInfo`
(exported in `__all__`); `ExtractedBindingInfo` exists nowhere; the file has zero commits
since the epic started. The collision is live: `analysis/dependency_backtracker.py:31`
imports `agentic_mbse.sysml.types.BindingInfo` for annotations while the runtime objects in
that path are the local dataclass. Yet `epic_push_down.md` SC-D is checked `[x]` naming
"sysml-codegen `BindingInfo` renamed (Q4)", and `epic_push_down_audit.md` says "SC-D:
verified." No item spec/plan/audit records a Q4 disposition at all.
*Fix:* do the rename (design: `ExtractedBindingInfo`), or record an explicit deviation and
un-check the claim. Either way the current record is false.

**2. Item 1 move is not mechanical: membership filter semantically widened.**
`agentic-mbse src/agentic_mbse/sysml/expression.py:552` and `:592` — the original gated the
memberships fallback on exact `type(membership).__name__ == "Membership"` with
`member_element` checked *under* it; the moved code flattens this to
`== "Membership" or hasattr(membership, "member_element")`, accepting every Membership
subtype the original deliberately skipped. Fires only on referent-less nodes, so committed
fixtures are unaffected (byte-identity held), but it is a changed conditional recorded
nowhere — plan, design, and prior audit are silent.
*Fix:* restore the exact-name check, or record the widening as intentional with rationale.

**3. Item 1: test-double attributes leaked into shared production code.**
`expression.py:580-581, 587-588` (`extract_feature_chain_name`) and `:619-620, 629-630`
(`extract_feature_chain_segments`) add `instance_name` / `attr_name` fallback branches.
These attributes exist on no syside node — only on agentic-mbse's
`MockFeatureChainExpression` (`tests/test_sysml/conftest.py:76`), and several new Item-1
tests pass only because of them. On real models the branches are dead code; the tests anchor
to the mock's shape, not SysML's. Violates the design's "move code mechanically first" rule
and is recorded nowhere.
*Fix:* give the mocks real `operands`/`target_feature` shapes and delete the branches, or
record the divergence. Prefer the first — shared semantics code should not know about test
doubles.

**4. SC-D Q6/R8: the `# INTENTIONAL DIVERGENCE` comment was never added; certified as done.**
Zero hits for "INTENTIONAL" in sysml-codegen src; `expression_compiler.py` is untouched on
the branch. Mitigation: the pre-existing docstring on `_sanitize_name`
(`expression_compiler.py:167-177`) already explains the no-reserved-word-suffix divergence,
so the practical risk is low — but the design refresh looked at exactly that state and ruled
the pre-flight "still open, not done," and the epic checked it `[x]` anyway.
*Fix:* add the one-line marker, or amend SC-D honestly.

### Minor

**5. SC-E mypy ceiling exceeded: 97 → 98.** The six `no-any-return` errors in
`expression_utils.py` moved out with the code, but the thin wrappers left behind
(`hierarchy_resolver.py:222, 277-320`; `extractor.py:404`) now return values mypy sees as
`Any`, because agentic-mbse ships no `py.typed` marker (PEP 561). Net +1. The pre_pr report
calls 98 "existing baseline," which is inaccurate — main is 97. Root-cause fix: add
`py.typed` to agentic-mbse; that also retires the `TYPE_CHECKING` mirror dataclasses
(finding 8) and the whole `import-untyped` family.

**6. R6 docstring cross-reference is one-way.** `extract_feature_chain_name` points at
`get_reference_name` (`expression.py:568`), but `get_reference_name` (`:329`) has no reverse
pointer and still references a sysml-codegen-internal helper. SC-D counts R6 as done;
half-done. Related trap: three literal predicates now coexist in the shared module
(`is_literal_expression` :254, `is_literal_type` :285, `is_literal_node` :635) with no
mutual disambiguation, and the codegen shim aliases `is_literal_expression = is_literal_node`
— the same name has different semantics per package. Two docstring lines close it.

**7. Self-certifying TYPE_MAP inventory tests (Items 3 and 4).**
`agentic-mbse tests/test_sysml/test_hierarchy.py:295-303` and
`tests/test_sysml/test_aggregation.py:230-256` verify the AST-walk type inventory against a
fake map built from the inventory itself — true by construction. The real protection is
`test_adapter.py`'s hardcoded list (verified complete today), but nothing ties the inventory
to it, so a new `is_instance` string added to the shared modules passes both tests unproven.
Assert inventory ⊆ real `_get_type_map()` keys.

**8. `TYPE_CHECKING` mirror dataclasses are an unpinned drift surface.**
`sysml-codegen src/sysml_codegen/extraction/data_models.py:27-91` re-declares the six shared
models field-by-field for mypy only. Runtime identity is pinned by tests; the mirror is not —
if agentic-mbse changes a field, mypy keeps checking the stale mirror. Superseded entirely by
the `py.typed` fix (finding 5).

**9. Item 4 unary-minus render divergence, unrecorded.** Old code compared the raw operator
enum (`operator == "-"` is False for `syside.Operator.Minus`), so real nodes rendered
`-(x)`; the new path str-normalizes at decompose and renders `-x`
(`aggregation.py:239`, `hierarchy_resolver.py:300-301`). Python-identical semantics,
unpinned edge, arguably a fix — but it deviates from the "exact reproduction" bar and is
recorded nowhere. Record it (or pin it with a test).

**10. Shared `SUPPORTED_OPERATORS` omits `**`** (`aggregation.py:40-58`) while codegen's
`AGG_PYTHON_OPS` supports it. No codegen impact today (the adapter ignores shared operator
diagnostics), but a future profile rule built on the shared facts would false-positive on a
compilable `x ** y` aggregation. Add `**` or document the intent.

**11. P1-exception documentation missing.** The design (R4) required documenting
`build_element_qualified_name`'s duck-typed AST traversal as a deliberate P1 exception in
the new module's docstring; `agentic-mbse qualified_names.py` says nothing about it.

**12. SC-F inventory only by pointer-chasing.** Tier 2c is durably deferred in the epic, but
the epic names 2 of 4 post-refactor functions plus a literal "..."; the full inventory
(`_find_instantiation_paths`, `_create_virtual_calc_usage`, `_expand_template_calc_usages`,
`_build_part_usage_index`) lives only in the concept design's refresh note. Not silently
dropped, so SC-F passes — but re-file the complete list in one durable place.

### Notes

- `InvocationNode.wrapper_disposition` (`aggregation.py:134`) is never assigned — dead field.
- Conformance dispatch tests hardcode the `../agentic-mbse` sibling path with no existence
  guard (`test_ast_dispatch_invariant.py:44-59`). Fails loudly, but CI-fragile.
- Shim `__all__` gained `SysideAdapter` (`expression_utils.py:41`), absent from the old
  `__all__`; no importer uses it through the shim. Harmless.
- Load-bearing comments (spike-Q5 `cached_lower_bound` rationale) survive only in the
  codegen wrapper, not next to the moved behavior in `hierarchy.py`. Cosmetic.

---

## What certifies cleanly (verified with evidence)

- **SC-A/SC-B substance:** every moved body in qualified_names, hierarchy, and aggregation is
  byte- or behavior-equivalent to main's original (modulo the Item 1 deviations above);
  dispatch orders preserved, including REQ-AST-10 literal-before-invocation; re-exports are
  the same runtime class objects (`is`-verified) across all five consumer layers;
  `extract_feature_chain_segments` exported pre- and post-move; `hierarchy_resolver.py` is a
  genuine thin wrapper with codegen policy (design overrides, Python rewrite, aliases,
  `AggregationExpressionData`) staying local.
- **Boundary:** zero `sysml_codegen` imports anywhere in agentic-mbse src/ or tests/; zero
  codegen identifiers (EQN/PQN/channel/module, Python source) in the shared modules;
  design overrides, usage-type indexing, `HierarchyExtractionResult`, orchestration all
  stayed in sysml-codegen. Q8: `constraint_report.py` untouched, disposition recorded.
- **SC-G:** all 10 profile rows in agentic-mbse BACKLOG.md are substantive (rule + fixture
  shape + severity + rationale, none title-only); ITEM-SYNC-C8 updated, not duplicated; the
  one implemented rule (Level-6 C7 → shared `is_literal_node`) is behavior-preserving and
  expressed over shared facts, not a codegen import.
- **TYPE_MAP:** complete inventory of `is_instance` strings in all moved code verified
  against the adapter whitelist — all present; the adapter hard-error contract is live.
- **Q5 rename:** `is_literal_node` vs the pre-existing semantic `is_literal_expression` —
  both present, distinct, no caller silently switched semantics.
- **R2 fold-in:** `binding.py` now calls the shared `extract_literal_value`; the deleted
  private copy was body-identical.
- **Dataclass ruling (P3 exception):** moved models are stdlib dataclasses, field-identical
  (programmatic `dataclasses.fields` comparison), enum values identical.
- **SC-E except mypy:** suites green at recorded counts, ruff within baseline, zero fixture
  churn — the "moves, not behavior changes" claim holds on the committed corpus.

## Epic-level assessment against source documents

The shaping intent (boundary research P1–P6 + concept design two-phase strategy) is
delivered: agentic-mbse now answers "what does the model mean" (expression text, names,
hierarchy primitives, aggregation structure) without any dependency inversion, sysml-codegen
keeps transformation policy, and the checking stack can build the codegen-compatible profile
from shared facts. The two-phase ordering, dataclass ruling, permanent-shim containment, and
Tier-2c deferral were all honored. What fell short is not the architecture but the record:
the epic certified pre-flight hazards that were skipped, and Item 1's "mechanical move"
absorbed small unreviewed rewrites.

## Required to flip to Certify

1. Q4: rename `usage_extractor.BindingInfo` → `ExtractedBindingInfo` (or record the
   deviation and correct SC-D). (finding 1)
2. Item 1: revert the membership widening + mock-only branches, or record both as
   intentional divergences; fix the mocks either way. (findings 2–3)
3. Q6/R8: add the `# INTENTIONAL DIVERGENCE` marker. (finding 4)
4. Correct the record: SC-D checkbox and the 2026-07-08 epic audit's "SC-D: verified" line;
   pre_pr's "98 = existing baseline" mypy claim. (findings 1, 4, 5)
5. Recommended, cheap: `py.typed` in agentic-mbse (retires findings 5 and 8), the two
   docstring cross-refs (6), inventory-⊆-TYPE_MAP asserts (7), record the unary-minus edge
   (9), add `**` to `SUPPORTED_OPERATORS` (10).

## Certification

Checked: all four items' moved code against pre-move originals; re-export identity at
runtime; both full suites, ruff, mypy (vs a main worktree), fixture byte-identity; SC-A
through SC-G including all ten profile backlog rows and the TYPE_MAP whitelist; both PR
scopes file-by-file. Not marked: no epic checkboxes were changed by this audit — SC-A/B/F/G
were verified as substantively met, SC-C was verified except where noted, SC-D and SC-E are
disputed above and their existing `[x]` marks should be corrected by whoever fixes the
findings. Items 3 and 4 certify as-is; Items 1 and 2 need the small fixes listed.

---

## Remediation record — 2026-07-10 (same session)

Dispositions, by finding number:

1. **Q4 (major)** — DESCOPED with recorded rationale (collision is annotation-only,
   predates the epic; full rename is future hygiene). The one live consequence was fixed:
   `dependency_backtracker.py` now imports the correct local
   `extraction.usage_extractor.BindingInfo` for its annotations, with a disambiguating
   comment. Notably, this exact bug surfaced as a mypy `[arg-type]` error the moment
   `py.typed` landed — the hazard was real. Epic SC-D text rewritten to the true
   dispositions; prior epic audit carries a correction addendum.
2. **Membership widening (major)** — FIXED: bodies restored to the pre-move exact-gate
   originals in `agentic_mbse.sysml.expression`.
3. **Mock-only branches (major)** — FIXED: `instance_name`/`attr_name` branches deleted;
   `MockFeatureChainExpression` now models the real syside shape (`operands[0]` +
   `target_feature`), so the Item-1 tests pass against the mechanical bodies.
4. **Q6/R8 marker (major)** — FIXED: `# INTENTIONAL DIVERGENCE` comment added above
   `expression_compiler._sanitize_name`.
5. **Mypy 98 (minor)** — FIXED at the root: `py.typed` added to agentic-mbse; four stale
   `type: ignore[import-untyped]` comments removed; sysml-codegen mypy now **77** (main
   was 97). Pre_pr report carries a correction addendum.
6. **R6 one-way cross-ref (minor)** — FIXED: `get_reference_name` docstring now points at
   the chain helpers; `is_literal_node`/`is_literal_expression` docstrings disambiguate
   each other.
7. **Self-certifying TYPE_MAP tests (minor)** — FIXED: both inventory tests now assert
   against the real `SysideAdapter._get_type_map()`.
8. **TYPE_CHECKING mirrors (minor)** — FIXED: deleted; direct typed imports under
   `py.typed`.
9. **Unary-minus divergence (minor)** — RECORDED as an accepted deviation in the Item 4
   audit addendum (no code change; new behavior matches the previously tested rendering).
10. **`**` omission (minor)** — FIXED: added to shared `SUPPORTED_OPERATORS`.
11. **P1-exception docstring (minor)** — FIXED: module docstring note in
    `agentic_mbse.sysml.qualified_names`.
12. **SC-F inventory (minor)** — FIXED: full four-function Tier-2c inventory written into
    the epic's SC-F.
    Notes: dead `InvocationNode.wrapper_disposition` field also removed.

**Post-remediation gates:** sysml-codegen 2138 passed / 4 skipped, ruff src clean, mypy 77,
fixtures byte-identical to main; agentic-mbse 1290 passed / 1 skipped, mypy 107 (unchanged
baseline), touched-file ruff clean (the two remaining repo ruff/import-sort errors pre-exist
on main in files this branch never touches). With the record corrected and the code
deviations reverted, the epic **certifies**.
