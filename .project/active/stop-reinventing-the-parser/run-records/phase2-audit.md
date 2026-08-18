# Phase 2 Audit — Close the Agentic evidence contract

**Verdict:** Pass with findings
**Audited:** 2026-08-18
**Scope:** Phase 2 only. Agentic `stop-parser-evidence-r2`, `8d27fb3` → `40dee5c` → `4a3ec46` →
`144ae02`. Phase 1 is closed and was not re-audited.
**Auditor:** independent, fresh context. Reproduced from own extractions, not from the
implementer's.

---

## Summary

Phase 2 does what it claims. All 10 recorded Agentic red nodes are green, and none of them was
weakened to get there — five of the six reference-use nodes are byte-identical to their Phase-1
bodies and the sixth was *strengthened* (audit Minor 11). All seven ordered deletions are gone
from production, barrels, and lazy aliases with no wrapper, alias, or deprecation path. The
scoped strict gate returns zero. The fast-suite, mypy, and Ruff baselines match `A_base`
exactly, on numbers I recomputed at both commits. The package contract verifies from a wheel
built and installed in a fresh venv. The three flagged deviations all survive scrutiny.

The findings are real but none of them is the defect this item exists to remove. One is a Major
design-conformance gap: the "one shared depth budget" the design names for
`extract_expression_ir` and expression reconstruction was never wired to those two entries, and
both still blow the Python stack instead of raising `EXPRESSION_DEPTH_EXHAUSTED`. The rest are
Minors — an ownership-gate scope that is evadable in principle, one design bullet about unit
operands not implemented, a broad-catch skip in a licensed fixture, and two small record
inaccuracies.

---

## Findings

### Major

**M1 — The shared depth budget is not shared with two of the three entries the design names.**
`src/agentic_mbse/sysml/constraint_extraction.py:663` (`extract_expression_ir`) and
`src/agentic_mbse/sysml/expression.py:298` (`reconstruct_expression`) have **no depth budget at
all**: `grep -n depth src/agentic_mbse/sysml/constraint_extraction.py` returns nothing, and
`reconstruct_expression` carries no depth parameter or guard.

design.md `#one-total-inspection-operation` is explicit: *"One non-caller-selectable depth limit
is shared by `inspect_reference_uses`, `extract_expression_ir`, expression reconstruction reached
by extraction, and every other recursive production expression entry. Exhaustion raises
`EXPRESSION_DEPTH_EXHAUSTED`."* The Phase 2 checklist's "Owned acquisition" box names "shared
depth" as one of the things this phase must make the boundary own, and that box is checked.

Reproduced against a self-nesting non-live `OperatorExpression` double:

```
extract_expression_ir  -> RecursionError (NO DEPTH BUDGET)
reconstruct_expression -> RecursionError (NO DEPTH BUDGET)
```

Both should have returned `SemanticEvidenceCode.EXPRESSION_DEPTH_EXHAUSTED`. What *was* delivered
is `inspect_reference_uses` and `traverse_expression` sharing `MAX_EXPRESSION_DEPTH`
(`reference_use.py:54`, `expression.py:56`) — which is exactly what the completion record claims,
so the record is honest here and the checklist box is what overstates. Fix or reduce the design
bullet before Phase 3 consumes the depth contract.

### Minor

**m2 — The ownership gate's scope is evadable by a module that never imports the adapter.**
`tests/test_sysml/test_semantic_selector_ownership.py:66` decides scope with
`ADAPTER_IMPORT in path.read_text()` — a substring match over the whole file, not an AST import
check. Two consequences:

- A production module that *receives* a live SysIDE node as a parameter and reads
  `node.referent` needs no adapter import at all, so it falls out of scope and reads raw
  selectors freely. `test_no_production_module_reaches_syside_directly` does not close this: such
  a module would not import `syside` either.
- A module that merely mentions the adapter path in a comment or docstring is pulled into scope.
  Harmless direction, but the premise is textual rather than structural.

Currently unexploited — I ran the selector scan over **all** modules with the scope removed and
`sysml/executable_profile.py` is the only out-of-scope hit, on `operands` alone. I confirmed that
read is genuinely neutral: `OperatorNode.operands: list[ExpressionIR]`
(`src/agentic_mbse/sysml/expression_ir.py:79`), and
`tests/test_sysml/test_executable_profile_hygiene.py:13` pins the module license-free. So
deviation 2's premise is true and the exemption is not hiding anything today. The gap is in how
the scope is *decided*, not in what it currently admits.

**m3 — A unit-annotation operand is emitted as a reference use, which the design forbids.**
design.md `#one-total-inspection-operation`: *"A structural unit annotation visits its value
operand and validates its shape but never emits the unit operand as a data reference."*
`inspect_reference_uses` emits it. Reproduced on `attribute unit_wrapped : Real = 3.0 [SI::metre]`:

```
inspect_reference_uses emits: [('SI::metre', 'SI::metre', 'StandardLibrary')]
design_reference_uses:       []
```

Filtering has been moved downstream into a document-tier policy
(`design_reference_uses`, `expression.py:83`). That covers the standard-library case and matches
`A_base`'s behavior, so nothing regressed — but a **project-scoped** unit (`3.0 [MyUnits::widget]`)
would survive the tier filter and appear as a design dependency, which is what the design bullet
exists to prevent. Phase 3 matters here: Codegen consuming `inspect_reference_uses` directly sees
the unit operand unless it repeats the tier filter. Not flagged in the completion record.

**m4 — A broad-catch skip can silently hollow out the licensed reference-use assertions.**
`tests/test_sysml/test_reference_use.py` (the `probe_expressions` fixture, and again in
`test_a_project_package_named_si_is_still_project_evidence`) wraps `SysideAdapter.load_model` in
`except Exception: pytest.skip(...)`. A fixture typo, a SysIDE API change, or a bad path skips
roughly a dozen licensed assertions and the file still reports green. Not firing today — I
confirmed `tests/test_sysml/test_reference_use.py` is **28 passed, 0 skipped** with the license
loaded, and the suite's single skip is the pre-existing
`test_adr002.py:289` "Requires fusion_modeling CATF models not in this repo". Narrow the catch to
the load failure the skip is for, or assert the model loaded.

**m5 — Two inaccuracies in the completion record.**
- The record says `test_semantic_selector_ownership.py` is "12 passed". It is **14 passed**
  (`test_reference_use.py` 28 is correct; 42 together).
- The record's artifact-isolated figure "the focused gates are 221 passed, 1 skipped" is not
  reproducible because the record never names the file set. My nearest reconstruction from the
  validation box's own list (reference-use, ownership, expression, aggregation, binding, ADR002,
  export, types, identity-contract, errors) is **212 passed, 1 skipped**. Name the set or drop
  the number.

**m6 — Dead production helper left behind by the migration.**
`src/agentic_mbse/validation/level2_structure.py:280` `_has_defined_value` lost its only
production caller when CHECK 3 migrated to `leaf.declares_value`. It survives only because
`tests/test_validation/test_level2_integration.py:106` asserts `hasattr`. Not one of the seven
ordered deletions, so not a contract breach — but it is a raw `feature_value_expression` read kept
alive by a `hasattr` test. Delete both, or record why it stays.

**m7 — One evasion branch of the selector scanner is untested.**
`_selector_reads` (`test_semantic_selector_ownership.py:95-103`) detects
`getattr(node, "operands")` as well as `node.operands`, but the anti-vacuity parametrization
`test_the_scanner_finds_each_reviewed_selector` only ever writes the attribute form. The `getattr`
branch could break and nothing would notice. Add the `getattr` spelling to the mutant set.

### Informational

**i8 — ADR002's Method 3 now classifies from a runtime class name.**
`validation/adr002.py` compares `leaf.owner_kind == "CalculationDefinition"`, and `owner_kind` is
`type(owner).__name__` (`reference_use.py:231`). Design `#delete-the-permissive-production-surface`
explicitly sanctions "owner-kind evidence", so this is conformant — but it is an exact-type
comparison that a SysIDE subclass would miss, where the same fact already carries a
mapped-metatype `owner_is_definition`. The owner relation also moved from `element.owner` to
`element.owning_type`; not recorded as a deviation, and the base's Method-3 tests used
`MockCalculationDefinition` doubles that likely never exercised the branch they claimed to.

**i9 — `test_aggregation.py` softened three whole-dataclass equality assertions** to
identifying-field comparisons (`_neutral`, line ~122). The stated reason is sound — the exact
evidence fields now always populate, so hand-written whole-value equality is no longer writable —
and exact-evidence retention is separately covered by the new
`test_aggregation_retains_exact_root_members_and_leaf`. Noted, not counted against the phase.

**i10 — Defensive default contradicting its own docstring.** `_document_tier_name`
(`reference_use.py:263`) ends in `or ""` while its docstring says a target that cannot produce a
tier "is a named adapter failure, which propagates". Dead today, because
`SysideAdapter.document_tier` raises on every missing/unknown path — but if it ever returns, an
empty tier reads downstream as "not standard library".

**i11 — The Agentic ownership manifest is test constants, not a checked-in document.**
design.md `#documentation-and-backlog-obligations` asks for a manifest whose rows name the raw
selector, typed owner, route state, and public failure proof. What exists is
`REVIEWED_SELECTORS` / `REVIEWED_MODULES` in the ownership test. The Phase-2 checklist only asked
for the test, so this is not a Phase-2 breach — carry it to close.

---

## Reproduction results

All runs from my own clean extractions, never the implementer's. `git archive` of `144ae02` →
`/tmp/stop-parser-rev2/p2audit-agentic-mbse`, and of `2171016d` (`A_base`) →
`/tmp/stop-parser-rev2/p2audit-base-agentic-mbse`. Both paths carry the `agentic-mbse` string the
baseline path test requires. License sourced into the environment; never copied anywhere.

### Scope and worktree integrity (obligation 1)

| Check | Result |
|---|---|
| Agentic worktree HEAD | `144ae02`, `status --porcelain` empty ✓ |
| Codegen worktree | `d257ef109065832f629ea5c90c8faa11b7c47fa7`, clean, `git diff HEAD` empty ✓ |
| `/home/reid/1cfe/agentic-mbse` | `fcee56d6…`, branch `self-binding-replacement`, clean ✓ |
| `/home/reid/1cfe/sysml-codegen` | branch `stop-reinventing-the-parser`, clean ✓ |

Both user-checkout digests match `entry-status.md` (empty status). The three commits touch 28
files, all inside the Agentic tree; nothing outside it moved. No Critical.

### Red-to-green quality (obligation 2)

All 10 recorded nodes run green in one invocation: **10 passed in 0.25s**.

`git diff 8d27fb3 144ae02 -- tests/test_sysml/test_reference_use.py` shows the only edits inside
the six recorded nodes are (a) the module docstring and (b)
`test_an_indexed_use_cannot_form_an_aggregation_term`, which was **strengthened** — Phase 1 passed
the `IndexedReferenceUse` *class* and caught bare `Exception`; it now constructs a real instance,
requires `SemanticEvidenceError`, asserts the carried reference and location, and adds a paired
positive proving the refusal is about the index. The other five bodies are unchanged. The four
ownership nodes kept their names and assertions; the file only gained scope and coverage. **No
test was weakened or substituted.**

### Anti-vacuity mutation runs

Performed in a throwaway copy (`/tmp/stop-parser-rev2/p2mut-agentic-mbse`), never in the worktree:

| Mutation | Result |
|---|---|
| `_reaches_the_parser` → `False` (scope admits nothing) | `test_the_scanned_module_set_admits_neither_everything_nor_nothing` **FAILED** ✓ |
| `_reaches_the_parser` → `True` (scope admits everything) | that test **and** `test_raw_selector_reads_stay_inside_the_owned_boundary` **FAILED** ✓ |
| Re-added `BindingInfo.references` to `types.py` | `test_no_permissive_class_attribute_survives` **FAILED** with `['sysml/types.py::BindingInfo.references']` ✓ |

The gate is not vacuous. Deviation 2's anti-vacuity claim is verified, not accepted.

### Deletion closure (obligation 3)

Independent sweep over `src/`, `docs/`, `tests/`, `scripts/` for all seven ordered deletions plus
the three helper names: **zero live uses in `src/` and zero in `docs/`**. The only `src/` hit is
one prose comment at `sysml/types.py:191` describing what was removed. Test hits are the gate's
own name lists and docstrings. No wrapper, alias, deprecation path, or re-implementation.

`design_reference_uses` (`expression.py:83`) is not `extract_feature_refs` under a new name: it is
a three-line tier-policy filter returning closed-union values.

All eight migrated consumers inspected (`aggregation.py` ×2, `binding.py`, `adr002.py`,
`expression.py`, `constraint_extraction.py`, `hierarchy.py`, `level2_structure.py`,
`level6_architecture.py`). None reconstructs the weak route locally. `level6_architecture.py`
additionally *removes* two `except Exception: return None` swallows. `level2_structure.py`'s
`leaf.declares_value` is semantically identical to the `_has_defined_value` it replaced (both are
`bool(feature_value_expression)`).

### Boundary quality (obligation 4)

- Closed union `ReferenceUse = ExactReferenceUse | IndexedReferenceUse` ✓ (`reference_use.py:128`)
- `IndexedReferenceUse` carries `reference` and `location` only; `hasattr(use, "path")` is False,
  verified on a live indexed node ✓
- One total inspection operation; `inspect_reference_uses` takes only `expression` ✓
- `ExactSemanticPath.__post_init__` enforces non-empty segments, `segments[0] is root`,
  `segments[-1] is leaf` ✓
- `IndexExpression` dispatch is the mapped metatype: `SysideAdapter.get_type("IndexExpression") is
  syside.IndexExpression` returns True on the live runtime, and `reference_use.py` contains zero
  `__name__ ==` comparisons ✓
- `DocumentTier` is the sole document authority; `SysideAdapter.document_tier` raises
  `DOCUMENT_TIER_MISSING` / `DOCUMENT_TIER_UNKNOWN` rather than defaulting ✓ (see i10)

```
uv run mypy --strict src/agentic_mbse/errors.py src/agentic_mbse/sysml/reference_use.py
→ Success: no issues found in 2 source files   (exit 0)
```

### The three flagged deviations (obligation 5)

**Ownership-gate scoping — sound premise, evadable mechanism.** Verified above (m2). Scope rule,
not an exemption; no module is excused a selector it actually reads today.

**Constraint-fact golden — correct re-anchoring, nothing else touched.** Semantic diff of
`tests/fixtures/constraint_fact_shapes/production_facts.json` (single-line JSON, so the
`git diff --numstat` 1/1 is 8 changed lines under pretty-print): exactly 4 values changed, all
`source_name`. Checked against the fixture source: `type_units.sysml:27` authors `Color::red`,
`:28` authors `Mode::on`, `:39` authors `missing_value`, `:43` authors the second `Color::red`.
The new values are the authored spellings; the old ones were rendered terminal names and a
`<placeholder Feature>`. Every other byte unchanged.

**`BindingType` move — a layering fix, not a shim.** Verified at runtime:
`sysml.types.BindingType is sysml.data_models.BindingType is sysml.BindingType` → True; members
`{CHAIN: chain, EXPRESSION: expression, LITERAL: literal, REFERENCE: reference, UNBOUND: unbound}`
identical to `A_base`; still in `types.__all__` and the `sysml` barrel.

### Package / artifact contract (obligation 6)

```
pyproject version = 0.1.3 ; agentic_mbse.__version__ = 0.1.3
uv lock --check → Resolved 157 packages (consistent)
uv build --wheel → agentic_mbse-0.1.3-py3-none-any.whl
```

Installed into a fresh venv (`uv venv` + `uv pip install <wheel>`):

```
dist 0.1.3 | __version__ 0.1.3 | semantic-evidence/v2
codes ok: True                     (INDEXED_REFERENCE_UNSUPPORTED, EXPRESSION_DEPTH_EXHAUSTED)
boundary importable: True          (all four names, present in sysml.__all__)
BindingInfo has references: False | reference_uses: True
surviving deleted symbols: []
```

### Completion-record accuracy (obligation 7)

Recomputed at both commits from my own extractions:

| Claim | `A_base` measured | `144ae02` measured | Verdict |
|---|---|---|---|
| Fast suite 18 / 1883 / 1 | 18 failed, 1841 passed, 1 skipped | **18 failed, 1883 passed, 1 skipped** | ✓ |
| Failure set is exactly the declared 18 | — | `diff` of sorted FAILED lists: **identical, 18 nodes** (17 `test_web_backend.py`, 1 `test_equations.py`) | ✓ |
| mypy 101 → 101 | 101 errors in 21 files | 101 errors in 21 files | ✓ |
| Ruff 119 → 119 | 119 | 119 | ✓ |
| Neither baseline described as green | — | correct, both stated as nonzero | ✓ |
| `test_reference_use.py` 28 passed | — | 28 | ✓ |
| ownership 12 passed | — | **14** | ✗ (m5) |
| "focused gates 221 passed, 1 skipped" | — | set unnamed; nearest 212/1 | unverifiable (m5) |
| Wheel markers / deleted symbols absent | — | reproduced above | ✓ |

**Manual inspection 1** reproduced against a live licensed model:

```
sum(cells.mass) → ExactReferenceUse form=chain 'cells.mass' ('cells','mass') plural=True
  root Probe::Rack::cells owner Probe::Rack PartDefinition tier Project
  leaf Probe::Cell::mass  document ✓  source_location ✓  members ('mass',)
  operator/literal fields carried: []
  SumTerm from it: leaf Probe::Cell::mass, root Probe::Rack::cells
cells#(2).mass → IndexedReferenceUse 'cells#(2).mass' @ line 9, has path: False
  adr002 reference_is_dynamic: True for both variants
  decompose_aggregation_expression → INDEXED_REFERENCE_UNSUPPORTED
```

**Manual inspection 2** reproduced: `SysideAdapter.get_type("IndexExpression") is
syside.IndexExpression` → True. The measured authored text `'cells#(2).mass'` matches the record
exactly.

The `A_base` "already at 0.1.3" claim is correct — the version obligation was satisfied before the
phase and verified from the wheel rather than re-performed. Honest.

### Minors 5 and 11 (obligation 8)

**Minor 5 — closed.** `PERMISSIVE_SYMBOLS` now names all seven ordered deletions plus the three
Phase-1 helpers. `BindingInfo.references` gets its own class-scoped scanner because a bare
`references` is too common to name-scan; `test_the_class_attribute_scanner_is_not_vacuous` proves
the scanner finds the field in `BindingInfo` and nowhere else, and my M3 mutation proved it goes
red for the real thing. `test_every_ordered_deletion_is_covered_by_a_gate` pins the two scanners
against the design's ordered-deletion set, which addresses the drift that caused the finding
rather than only its symptom.

**Minor 11 — closed.** Constructed `IndexedReferenceUse`, narrowed `pytest.raises(
SemanticEvidenceError)`, asserted code, reference, and location, plus a paired exact-use positive
proving refusal precedes term construction. Reading `build_aggregation_term`
(`reference_use.py:534`) confirms the ordering structurally: `require_exact_reference_use` raises
before any `SingletonTerm` is constructed.

### Vacuity sweep (obligation 9)

Grepped every added/modified test assertion for empty iteration, over-broad catch, and
self-comparison. Two broad catches found, both the licensed-fixture skip in m4. No `assert True`,
no self-comparison, no loop that can iterate zero times into a passing assertion. Two
`assert ... is not None` additions sit inside a loop over a tuple already length-asserted, so they
cannot vacuously pass. One softening (i9) with a stated and sound reason.

---

## Not checked

- The slow PDF/HTML corpus and the 15 paid/network cases — outside validation by owner direction;
  never invoked.
- Phase 1's own contract, and any Codegen-side behavior. The Codegen worktree was read-only.
- Whether `docs/patterns/plant-idiom.md`'s seven pre-existing shapes are still accurate; only the
  new "indexed form is valid SysML, and not implemented" section was verified present and correct.
- The design's close-out obligations (backlog rows, `deep_cross_scope_probe` comment, P-003
  status, epic wording). Those are not Phase 2's.
- Cross-repository behavior of `semantic-evidence/v2` under a real Codegen consumer — that is
  Phase 3's proof, by construction.

---

## Fit for Phase 3?

**Yes, with M1 and m3 carried in.** The contract Phase 3 needs is real: one closed union, an
indexed variant with no path to read, one total inspection operation, mapped metatype dispatch,
and a package that ships all of it under `semantic-evidence/v2`. I verified each of those against
a live model and an installed wheel, not against the record.

Two items should travel with the phase boundary rather than wait:

- **M1** because Phase 3 makes Codegen accept only closed evidence, and "one shared,
  non-caller-selectable depth budget" is part of what closed evidence means. Either wire
  `extract_expression_ir` and expression reconstruction to `MAX_EXPRESSION_DEPTH`, or amend the
  design bullet to say what was actually built.
- **m3** because Codegen consuming `inspect_reference_uses` directly will see the unit operand as a
  reference. Today the tier filter hides it; a project-scoped unit would not be hidden.

Neither blocks starting Phase 3. Neither is the substitution defect this item exists to remove —
that one is closed, structurally, and I could not find a route around it.

---

# Addendum — targeted confirmation of the fix round

**Confirmed:** 2026-08-18
**Target:** `stop-parser-evidence-r2` `144ae02` → **`68bca37`** ("fix: close the Phase 2 audit
findings"), record updated at docs commit `719dce1`.
**Scope:** confirmation of the closures by execution only. Not a re-audit of Phase 2.
**Method:** fresh `git archive` of `68bca37` → `/tmp/stop-parser-rev2/p2fix-agentic-mbse`, own
`uv sync`, license loaded. Mutations in a separate extraction with its own environment.

**Result: every finding in scope is confirmed closed.** M1, m2, m3, m4, m5, m6, m7, and i10 all
verified by execution. No regression. Phase 2 is fit for Phase 3 with no carried findings except
i11, which is a close-out obligation by design.

---

## A harness correction that matters for reading this addendum

My first de-wiring attempt copied the previous extraction *including its `.venv`*, and that venv's
package finder still resolved to the **original** tree. Under pytest the mutated file was never
imported:

```
LOADED FILE: /tmp/stop-parser-rev2/p2fix-agentic-mbse/src/.../constraint_extraction.py   # not the mutant
GUARD LINE IN LOADED SOURCE: ['if ctx.depth >= MAX_EXPRESSION_DEPTH:']                    # unmutated
```

So the intermediate "tests still pass on the de-wired build" observation was an artifact of my
harness, not a property of the tests. Every mutation reported below was redone in
`/tmp/stop-parser-rev2/p2mut2-agentic-mbse` — a fresh `git archive` with its own `uv sync` — and
the loaded path was asserted before each run.

---

## Per-finding confirmation

### M1 (Major) — **Confirmed closed.**

My original self-nesting reproduction, rerun verbatim at `68bca37`:

```
extract_expression_ir  -> SemanticEvidenceCode.EXPRESSION_DEPTH_EXHAUSTED
reconstruct_expression -> SemanticEvidenceCode.EXPRESSION_DEPTH_EXHAUSTED
```

Both previously raised `RecursionError`.

**One shared, non-caller-selectable budget.** `MAX_EXPRESSION_DEPTH = 100` is defined once
(`reference_use.py:54`) and *imported*, never redefined, by `expression.py:12` and
`constraint_extraction.py:55`. Grep over `src/` finds exactly one assignment and three consuming
guards (`reference_use.py:285`, `expression.py:56` and `:310`, `constraint_extraction.py:699`).
Public signatures carry no depth knob: `extract_expression_ir(expression, *, diagnostics)`;
`reconstruct_expression`'s `_depth` and `traverse_expression`'s `_current_depth` are
underscore-prefixed recursion counters, the convention already in the tree.

**The four kept tests discriminate a de-wiring.** Two mutations, each in an isolated extraction
with the loaded path asserted:

| Mutation | Result |
|---|---|
| `constraint_extraction.py:699` guard → `if False:` | `test_the_shared_budget_covers_expression_ir_extraction` **FAILED** and `test_no_recursive_production_entry_reports_a_bare_recursion_error` **FAILED**, both on `RecursionError: maximum recursion depth exceeded` — the exact defect M1 named. 2 failed, 3 passed. |
| `expression.py:310` guard → `if False:` (IR guard restored) | `test_the_shared_budget_covers_expression_reconstruction` **FAILED** and the set test **FAILED**. 2 failed, 3 passed. |

Each wiring is caught by its own test *and* by the set test, which is the right shape given M1's
defect was two entries never wired at all.

### m3 — **Confirmed closed, and the double is adequate.**

The unit operand is no longer emitted at the boundary. Live, against the same model I used to
raise the finding:

```
inspect_reference_uses: []      # was [('SI::metre', 'SI::metre', 'StandardLibrary')]
design_reference_uses:  []
```

**Shape validation survives.** `_unit_annotation_value` (`reference_use.py:316`) recognises a
structural `[` annotation, refuses a wrong arity and a non-feature-reference unit operand with
`EXPRESSION_KIND_UNSUPPORTED`, refuses an unresolved unit referent with `RESOLVED_TARGET_MISSING`,
and then walks only the value operand. `test_a_malformed_unit_annotation_is_refused_by_name`
covers it, and a new live probe attribute (`local_scale [SI::metre]`) proves the value operand is
still visited rather than the whole annotation being muted.

**On the implementer's flag.** I probed the reachability claim independently at SysIDE 0.8.4 with
two spellings the implementer did not list — a project `attribute def` used as a unit, and a
project `attribute` typed by a standard unit type. Both are refused by the parser
(`Referent must be a feature but is AttributeDefinition`; `Invalid quantity expression, expected a
measurement unit as the second argument`). That corroborates the flag: the authored form
`3.0 [MyUnits::widget]` is not reachable through a real model today.

**Is the closure adequate?** Yes. The double varies exactly one field from a case that *is* proved
live. `test_a_unit_annotation_never_emits_its_unit_operand` pins the structure against a real
model with a real `SI::metre`; `test_a_project_scoped_unit_is_not_emitted_either` reuses the same
`MockOperatorExpression(operator="[")` shape and changes only the document tier — then asserts the
tier really is `Project`, so the test would be meaningless if the double were mis-built, and
additionally asserts the value operand is still emitted. The double is not standing in for the
mechanism; it is isolating the one variable the live model cannot supply. The test records the
measurement and why the double is the only route. Nothing further is needed.

### m2 — **Confirmed closed on the mechanism; the residual I named is unchanged and still
unexploited.**

`_reaches_the_parser` now reads the adapter import off parsed `Import`/`ImportFrom` nodes
(`test_semantic_selector_ownership.py:75-98`) instead of a substring match.
`test_the_import_scope_is_structural_not_a_substring_match` covers both directions — a docstring
naming the adapter yields no import, and both `import X` and `from X import Y` do. The two
original anti-vacuity guards are untouched and still in the file.

The other half of my finding — a module that receives a live SysIDE node as a *parameter* and
reads a raw selector without importing anything — is inherent to an import-keyed scope and is not
closed. I re-ran the unscoped selector sweep at `68bca37`: `sysml/executable_profile.py` on
`operands` remains the only out-of-scope reader, and it is still the neutral `ExpressionIR` field.
Nothing to act on; recording it so the scope premise stays visible.

### m4 — **Confirmed closed.** `pytest.skip` and `except Exception` are both **absent** from
`tests/test_sysml/test_reference_use.py` (grep returns only the explanatory comment at line 185).
`_require_a_clean_load` (line 182) asserts the model produced no error diagnostics, so a parse
error in probe source now fails rather than silently hollowing out the licensed assertions.

### m5 — **Confirmed closed, both corrections reproduced.**

- Ownership count: record now says **14** (plan.md:1219, with a note that it first read 12). I
  measure `test_semantic_selector_ownership.py` at **20 passed** now (14 + the 6 nodes this fix
  round added), and `test_reference_use.py` at **32 passed**. Both match the record.
- The unreproducible "221 passed" is replaced by a **named** set. Reproduced exactly:
  `pytest tests/test_sysml/ tests/test_validation/ tests/test_errors.py` → **834 passed,
  1 skipped**. The single skip is the pre-existing `test_adr002.py:289` external-model skip.

### m6 — **Confirmed closed.** `_has_defined_value` is gone from `src/` entirely (grep over the
whole tree returns only the two lines in `test_level2_integration.py`), and the former `hasattr`
assertion is inverted at line 114 to `assert not hasattr(level2_structure, "_has_defined_value")`
with a comment saying why. Absence is pinned, not merely achieved.

### m7 — **Confirmed closed.** `test_the_scanner_finds_a_dynamic_getattr_read` is parametrized over
all four reviewed selectors in the `getattr(node, "<selector>", None)` form, and
`test_the_scanner_ignores_an_unrelated_getattr` covers the negative. The `getattr` detection branch
is now exercised in both directions.

### i10 — **Confirmed closed.** `reference_use.py:263` is
`return str(SysideAdapter.document_tier(element).name)`. The `or ""` fallback is gone, so a
tier-less target propagates the named adapter failure its docstring already promised.

### i8 — left as-is, as the audit allowed. i11 — carried to close, by design.

---

## Regression check at `68bca37`

| Gate | Result |
|---|---|
| `test_reference_use.py` | **32 passed** |
| `test_semantic_selector_ownership.py` | **20 passed** |
| Named artifact set (`test_sysml/`, `test_validation/`, `test_errors.py`) | **834 passed, 1 skipped** |
| `mypy --strict errors.py reference_use.py` | **Success, no issues** (exit 0) |
| `mypy src/` baseline | **101 errors in 21 files** — unchanged from `A_base` |
| `ruff check src/ tests/` baseline | **119 errors** — unchanged from `A_base` |
| Fast suite (`-m "not slow"`, licensed) | **18 failed, 1893 passed, 1 skipped** |
| Fast-suite failure set | `diff` against my recorded `A_base` list: **identical, 18 nodes** |
| Codegen worktree | `d257ef109065832f629ea5c90c8faa11b7c47fa7`, 0 dirty |
| `/home/reid/1cfe/agentic-mbse` | `fcee56d6…`, 0 dirty |
| `/home/reid/1cfe/sysml-codegen` | branch `stop-reinventing-the-parser`, 0 dirty |

The pass count rises 1883 → 1893 by exactly the ten nodes this fix round added. The 18 failures are
still the same optional-dependency baseline, node for node. The PDF/HTML corpus and the paid/network
cases were never invoked.

---

## Fit for Phase 3?

**Yes, without carried findings.** M1 and m3 — the two I said should travel with the phase boundary
— are closed at the boundary rather than downstream, and both closures are proved by execution:
M1 by rerunning the original reproduction and then killing each wiring to show the kept tests
discriminate, m3 by a live model plus a double that isolates the one variable SysIDE 0.8.4 will not
parse. i11 (the ownership manifest's document form) remains a close-out obligation and is not a
Phase-3 blocker.

**Not checked in this pass:** anything outside the eight findings and the regression table. This is
a confirmation pass, not a re-audit; the Phase 2 verdict above stands on its own evidence.
