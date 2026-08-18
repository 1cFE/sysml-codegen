# Phase 3 Audit — Make Codegen accept only closed evidence

**Verdict:** Needs Work
**Audited:** 2026-08-18
**Scope:** Phase 3 only. Codegen `stop-parser-impl-r2`, `b4e97dd` → `8cc1ef5` → `18597c3` →
`b316e3a` → `3a85831` → **`e3e1a39`**. Upstream Agentic `3f8bd58` (0.1.3 / `semantic-evidence/v2`),
read-only. Phases 1, 2, and 2b are closed and were not re-audited.
**Auditor:** independent, fresh context. Every number below was recomputed from the auditor's own
`git archive` extractions, never from the implementer's.
**Closing gate:** this is the dedicated adversarial audit plan rev 4 requires. All six weak variants
were attacked.

---

## The Point

The product is three steps and nothing else: parse the models with a SysML v2 parser, walk the
parser's resolved tree to reconstruct the math, write that math into TEAx Python. Every decision on
the way is read from the parser's own resolved evidence. An authored form the toolchain cannot honor
has exactly two honest outcomes — resolve it through the parser, or refuse by name before anything is
built. One modeled source occurrence becomes exactly one runtime source.

Phase 3 serves that by making Codegen incapable of *representing* weak evidence: one pre-graph
inventory acquires every production expression site's references, an authored index is refused before
a graph exists, and every consumer branches over a closed union rather than walking a raw expression
for itself.

---

## Summary

The architecture Phase 3 set out to build is there and it works. One pre-graph inventory is genuinely
first in the boundary, an `IndexedReferenceUse` cannot be converted into an exact one by any route I
could find, the deep-relationship path factory is total in production, the value-site unit policy
delegates every structural question to Agentic's primitive, and the ownership closure is real rather
than achieved by narrowing the scan. Every number in the completion record reproduces exactly,
including the declared archive SHA-256, which matched an independent `git archive` byte for byte.

It does not pass, for three reasons.

**A valid model crashes the public route.** A unit-annotated reference at an attribute value site —
`attribute mirror_len : Real = base_len [m];` — loads with zero SysIDE diagnostics and then dies out
of `sysml-codegen generate` with a raw `ExpressionInventoryError` traceback carrying no code, no
authored reference, no `file:line`, and no cause. It is Phase-3-introduced. Two lanes found it
independently.

**Two of the owner's five binding conditions on the tests-after deviation are unmet.** The
per-consumer inventory-bypass coverage does not exist — the test carrying that name calls one library
function five times with a different label — and the closed union is not pinned exhaustively at every
switch. The backstop can be deleted from all five consumer adapters, and four union arms removed, and
the entire 2206-test suite stays green.

**The ownership manifest has a granularity hole** that makes its own "an unannotated receiver can
never qualify" rule bypassable inside 20 rowed functions.

None of these is the defect the item exists to remove — the exact-evidence boundary itself holds. All
three are gaps between what the phase built and what it proved, plus one regression the proof gap let
through.

---

## Product Judgment

**Is this the right piece of work?** Yes. Closing Codegen's evidence boundary on a single pre-graph
inventory is the correct next move, and it retired the `audit3-F1` block that had stood since
2026-08-17: indexed-source refusal now covers the computed-attribute route it previously escaped, is
uniform across all six authored shapes probed, and identifies `IndexExpression` through the mapped
metatype adapter instead of `type(...).__name__`. That is recorded FIXED in the ledger with measured
evidence, not asserted.

**The ledger gate for this run is BLOCKED (audit-phase3-F4).** The lens run itself returned DISPOSED
on three findings; the auditor addendum appended after it records F4, the unit-annotated value-site
crash, as an owner-grade `[DON'T]` against P-003 and P-004 and bounded by P-001. A form the language
defines, that the product previously emitted, is now unauthorable with no stated replacement spelling
and no diagnostic. That is a `BLOCK` and it forbids Certify on its own.

**One structural smell fired and is not resolved.** *Two representations must be manually kept
synchronized* — the ALIAS-vs-COMPUTED_ATTRIBUTE role is decided twice, in two modules, by two
textually identical predicates applied to different nodes, with nothing pinning their agreement. That
smell is the direct cause of F4. Escalating it here does not resolve it; the fix is to compute the
role once.

Two further smells were checked and cleared: no special category exempts a case whose user-visible
meaning is unchanged (`ExpressionSiteRole` is routing only, and the refusal is uniform across all six
consumer shapes), and correctness no longer depends on downstream knowledge of SysIDE's runtime
representation. A third fires weakly and is disposed: the off-route computed-attribute classifier
gained a hand-written fail-closed policy for a shape the elaborator owns positively, which is
hardening dead code rather than deleting it, but it is proved transitively unreachable from both
public raw-source arms and the spec dispositions those modules out of scope.

---

## Findings

### Major

**M1 — A valid, diagnostic-free model crashes the public generation route with no diagnostic.**

`attribute mirror_len : Real = base_len [m];` — and the feature-chain form `= inner.w [m]` — parses
clean (`extractor.diagnostics.validation == []`) and then raises out of `sysml-codegen generate`:

```
File ".../elaboration/elaborate.py", line 2343, in _resolve_aliases
    uses = self._inventory.require_exact(pending.site)
File ".../elaboration/expression_evidence.py", line 111, in require
    raise ExpressionInventoryError
ExpressionInventoryError: expression site alias 74a84a62-… is absent from the evidence inventory
```

Identical under `strict=True` and `strict=False`. The refusal carries **none** of the four elements
the phase's own gate requires: no code token, no authored reference, no root-relative `file:line`, no
cause chain. It names a UUID the modeller cannot map to anything they wrote.

Cause — the role is decided twice, on two different inputs:

- the enumerator applies `_is_plain_reference` to the **raw** `feature_value_expression`
  (`src/sysml_codegen/elaboration/expression_evidence.py:245,250-254`). A `[` annotation is an
  `OperatorExpression`, so the site is filed `COMPUTED_ATTRIBUTE`;
- the consumer applies the textually identical `_is_reference_expression` to the **unit-unwrapped**
  expression (`src/sysml_codegen/elaboration/elaborate.py:871,894,1017-1019`), so it looks up
  `ALIAS`.

The row is absent, `require` raises, and `ExpressionInventoryError` appears in no `except` clause at
the D7 boundary (`src/sysml_codegen/orchestration/elaborated_pipeline.py:171-218`). The second raise
site, `elaborate.py:2046`, has the same exposure.

Phase-3-introduced: `expression_evidence.py` is born at `b4e97dd`, and at `C_base` (`78a9beb`)
`_PendingAlias` carried the expression object itself, so there was no site key and no role to
disagree about. The suite is green because the only fixtures exercising `= ref [unit]`
(`tests/fixtures/constraint_binding_unit_annotation/model.sysml:62,77`) use the **binding** role,
which `_role_for_owner` keys by `owning_type` and which therefore never takes the expression-shape
branch (`expression_evidence.py:241-244`). Bindings are confirmed unaffected.

**What should change:** compute the role once — enumerate on the unwrapped expression, or key the
consumer off the raw one — and add a licensed public-route test over a real model carrying a
unit-annotated reference at an attribute value site and at a feature-chain value site. Separately,
contain `ExpressionInventoryError` at the D7 boundary so an internal-defect class can never reach a
user as a bare traceback.

**M2 — No per-consumer inventory-bypass test exists; the backstop is deletable from every consumer
with zero failures.**

`tests/unit/test_expression_evidence_boundary.py:161-171` is parametrized over
`list(ExpressionSiteRole)`, but the body is identical for all five parameters: it builds an inventory
holding an indexed use and calls `ExpressionEvidenceInventory.require_exact(site)`. The role is a
label on a frozen dataclass; the test never imports or invokes any consumer adapter. It is one
assertion on one library function repeated five times with a different UUID. The sibling at `:174`
has the same shape against `require_exact_binding_use`.

The five roles do not even map to five adapters. The real adapters are `_calc_dependencies`
(`elaborate.py:2099`), `_resolve_aliases` (`:2341`), `_resolve_computed_expressions` (`:2415`, which
serves **both** computed-attribute and constraint-predicate), and the binding pair `_binding_evidence`
(`:2023`) / `_resolve_bindings` (`:2500`).

Mutation proof, run against a 2206-passing baseline:

- replacing all three `self._inventory.require_exact(` with `self._inventory.require(` at
  `elaborate.py:2111,2343,2417` — a pure backstop deletion, behaviour-identical for exact input —
  produces **0 new failures**;
- dropping the indexed arm at `elaborate.py:2518-2520` and replacing
  `require_exact_binding_use(evidence)` with `evidence.use` at `:2530` produces **0 new failures**.

The plan's own stencil (`plan.md:796-804`) specifies the missing half exactly:
`invoke_consumer_with_inventory_bypassed(...)` then `assert downstream.entered_once`. It was never
implemented for any consumer. The existing conformance tests
(`tests/conformance/test_expression_evidence_integrity.py:532,561,591`) prove only the *inventory*
layer, via a spy on a single seam (`:456`).

This is the specific condition the owner attached to the tests-after deviation
(`plan.md:821-822`), and the plan says plainly that the audit does not substitute for a missing kept
test.

**What should change:** one test per adapter that bypasses only the inventory gate, injects an
`IndexedReferenceUse` into that adapter, and proves that adapter's own exhaustive branch refuses it —
distinguished from the inventory layer by control flow, as the design requires.

**M3 — The closed union is not pinned exhaustively at every switch; four arms are removable with zero
failures.**

The constructor half of the requirement is genuine — deleting either `__post_init__`
(`extraction/binding_source.py:79-81`, `:103-105`) or `binding_source_kind`'s final raise (`:160`)
kills its test. The exhaustiveness half is not. Applying four weakenings at once produced **0 new
failures across 2206 tests**:

1. `elaborate.py:2045-2047` — the unknown-reference-use-variant raise → `return ExpressionBindingSource(formal, None, None)`;
2. `elaborate.py:2054-2055` — deleting `_unsupported_code`'s indexed arm, so an indexed binding
   classifies as *supported*;
3. `elaborate.py:2527-2528` — deleting `_resolve_bindings`' closing `isinstance` raise;
4. `binding_source.py:178-180` — `require_exact_binding_use`'s Expression/Literal and unknown-value
   raises → `return None`.

Arm 2 is the alarming one: it silently reclassifies an authored index as supported.

**What should change:** a kept test per switch arm, or a single exhaustiveness harness that enumerates
the union and asserts every production switch raises on each non-handled member.

**M4 — The ownership manifest key is too coarse: an unannotated receiver qualifies by riding an
existing row.**

The manifest keys on `(module, function, selector, form)` (`SelectorRead`,
`tests/conformance/test_expression_evidence_ownership.py:67-74`). A row proves **one** receiver in
that function. A second read of the same selector in the same function, on an arbitrary unannotated
parameter, produces the identical tuple and is invisible to both the equality gate (`:692`) and the
collision-contract gate (`:716`).

Demonstrated two ways, independently:

- adding `_compile_boolean(n: ExpressionIR, raw_syside_node=None)` returning
  `str(raw_syside_node.operands)` in `generation/predicate_compiler.py` — all 17 ownership tests pass;
- inserting `_sneak = expr.referent` into `extraction/usage_extractor.py::_parse_reference_expression`,
  a function that already owns a `referent`/`direct` row — gate stays green.

This is exactly the shape the design forbids: *"an unannotated receiver can never qualify — it stays
an unowned raw read and stays red"* (`design.md#the-codegen-gate-keeps-repository-wide-scope`;
`plan.md:903-909`). The hole is per-selector, not total — adding a *different* selector to a rowed
function is still caught — and it requires editing a rowed function rather than adding a module,
which is the practical mitigation.

**What should change:** key the manifest on the read site (function plus receiver name, or a
source-position ordinal), not on the function alone.

### Minor

**m5 — One deep-path totality branch has no kept test, and its regression form survives mutation.**
Turning `binding_source.py:235-241`'s non-`Feature` raise into a `continue` — a silent middle-segment
drop returning a shortened path — leaves the focused battery green. The `None`-fact branch (`:243`)
and the `IndexExpression` branch (`:228`) both have kept tests and both die under the same treatment
(`tests/unit/test_expression_evidence_boundary.py:250,268`). The untested branch is unreachable in
production today — `:305` asserts the real parser only yields `Feature` segments — but the checklist
item "deep-path totality tests, including the missing middle segment" is two-thirds satisfied.

**m6 — The disposition table is overwhelmingly a relabelling of pre-existing tests.** All 14
replacements exist, collect, and pass (15 nodes, one row parametrized ×2; nothing skipped). But **13
of 14 pre-date the deleting commit** — `b316e3a` added exactly one test, row 4's — and ten pre-date
the item entirely. Rows 1, 5, 7, and 9 name a test asserting something materially different from the
node it replaces: row 5's replacement asserts an alias target and says nothing about the live/frozen
owner-identity agreement that was the deleted node's whole point. Read literally, the owner's
"replacements land in the same commit that deletes the file" holds for 1 of 14; read as "the coverage
exists at the moment of deletion", it holds, since nothing was back-filled afterwards. The owner
should know which reading was used.

**m7 — Three rows name a weaker test than an available better one.** Rows 8, 12, and 13 point at
partial coverage while stronger same-fixture tests go uncited: `test_elaboration_aggregations.py:54,67,77,122`
(all four aggregation shapes, versus the one the row names),
`test_elaboration_contract_matrix.py:783` (the `self_named_binding_trap` fixture), and
`test_elaboration_shadowing.py:91` (the `shadowed_reference` control). Repointing costs nothing and
makes the table honest.

**m8 — The machine-readable ledger row did not land with the deletion.** At `b316e3a`, L-181 still
read `disposition: "retain"`, `replacement_proof_node: null`, and had no `deleted_test_nodes` key,
while the same commit set the Markdown row to `remove` — a token outside the ledger's vocabulary.
`check_ledger_4a.check_deleted_responsibility` (`scripts/check_ledger_4a.py:241`) therefore passed
**vacuously** at that commit. Both faces were made coherent one commit later in `3a85831`, and at HEAD
the row is correct: `state: executed`, `disposition: "delete"`, 14 deleted nodes, 14 replacement
nodes, `.md:628` agreeing.

**m9 — The collision-row declaring-type proof is a text substring, not a name resolution.**
`assert owner_type in annotation` (`test_expression_evidence_ownership.py:736-739`) compares against
`ast.unparse` output. Annotating a rowed receiver with a locally-declared decoy type whose name merely
*contains* the required string — `RawSysideExpressionIRNode` satisfying the `ExpressionIR` contract —
passes. The gate proves the annotation's spelling, not that the name binds to
`agentic_mbse.sysml.expression_ir`.

**m10 — Two of the five evasion mutants are vacuous, and the branch they fail to pin is
load-bearing.** `test_every_ast_evasion_mutation_is_discovered` (`:806`) asserts only that `found` is
non-empty and every read's function is `consume`; it never asserts the discovered form or selector.
Deleting the alias-`getattr` branch (`:480-481`) leaves all 17 tests green — while opening a real
escape: `SELECTOR = "operands"; getattr(node, SELECTOR)` in an adapter-free module is then
reclassified `dynamic-getattr` and filtered out entirely. Demonstrated end-to-end: with the branch
removed a real evader module passes; at HEAD it fails equality. HEAD is safe; the mutant does not
protect it.

**m11 — Four evasion forms outside the gate's mutant set slip through.**
`operator.attrgetter("operands")(node)`, `node.__getattribute__("referent")`, and
`vars(node)["referent"]` produce no `ast.Attribute` with a reviewed name and no `getattr` call, so
`_SelectorScanner` (`:470-485`) records nothing. Separately, only four selector names are watched
(`REVIEWED_SELECTORS`, `:33`), so reads of `feature_value_expression`, `result_expression`,
`owning_type`, `owned_redefinitions`, or `redefined_feature` are invisible. The allowlist is arguably
in-scope-by-design, but the completion record's "every raw selector has a reviewed owner with a real
proof artifact" is true only of those four names.

**m12 — Evidence errors keyed on a bare expression node carry no authored reference.** Agentic's
`_diagnostic_reference` reads `qualified_name` then `name`; an `OperatorExpression` has neither, so
the unit-arity refusal — and by construction the `RESOLVED_TARGET_MISSING` and operand-iteration
refusals — arrive with `reference=None` and render `consumer_display="<model>"`
(`orchestration/elaborated_pipeline.py:257`). Code token and location survive; the authored text does
not. Reached with one line of forcing:
`SI_EVIDENCE_INCOMPLETE | ref=None | loc=root-0/model.sysml:11`.

**m13 — The closed site set and role routing have no test at all.** Nothing exercises
`_enumerate_sites` (`expression_evidence.py:202`) or `_role_for_owner` (`:231`); the duplicate-row
test monkeypatches both away (`test_expression_evidence_boundary.py:151-156`). Neither the "roles are
disjoint by construction" claim nor the site set's completeness is pinned. This is M1's coverage root
cause.

**m14 — A `ConstraintDefinition` body is not in the closed site set.** `_enumerate_sites` covers
features carrying `feature_value_expression` plus `ConstraintUsage.result_expression`; a constraint
*definition* body is neither. A def body carrying `h.cells#(2).mass` is not refused by the inventory
and dies later at `SI_EDGE_DANGLING`, naming the wrong thing — the exact failure mode the inventory
exists to remove. Bounded: the same model refuses identically with the index replaced by a literal, so
part-typed constraint-definition inputs are independently unsupported and nothing wrong can ship
through it today.

**m15 — The qualified-predicate rendering seam is a positive capability change admitted on hand-built
IR only.** `predicate_reference_name` (`generation/constraint_name_safety.py:97`) now binds Python by
the exact target's local name, so `comp_a::length > 0.0`, which died at `b4e97dd` as an unsafe
identifier, now generates. Its two named pins build `FeatureReferenceFact`/`IdentityFact` by hand. The
completion record's claim that "the public six-consumer mutation test … pin[s] the result"
(deviation 2) is inaccurate — `test_combined_named_source_reaches_every_and_only_its_consumers`
asserts on the `InstanceGraph` and never renders Python. The behaviour is correct on inspection (the
emitted module binds `length`, and two qualified targets sharing one local name refuse at projection
with `SI_RENDERING_COLLISION`), but the evidence claim in the record should be corrected and a
public-route generation pin added.

**m16 — `PUBLIC_RAW_SOURCE_ARMS` is a prose tuple.** The reachability walk
(`_transitively_reachable_modules`, `:670-689`) is genuinely mechanical and catches a two-hop indirect
chain, but its root set (`:405-412`) is hand-written with the comment "B1 says this set is finite;
these are its members" and no test proves those two are the only public raw-source arms. No hole
today — the exclusion also holds from the `cli` root, 65 modules reached, none off-route.

**m17 — Two `SourceFile.referent` rows have no read-site check of their own.**
`SourceAdmission._verify_staged_files` and `SourceAdmission.staged_to_referent` rest on the class-level
`SourceAdmission.files` annotation (`:733-735`). Permitted by the design's "parameter **or**
attribute" wording, and the receivers are genuine module-local `self.files` iterations, but the
linkage between that annotation and those two reads is asserted nowhere.

**m18 — The focused-battery figure is not traceable.** "126 passed, 1 deselected" names areas but not
a selection, and brute-forcing subsets against the target returns over 10,000 distinct file sets that
hit it exactly. Phase 1 solved this for the D1-D4 battery by recording its 15 paths, which is why that
number reproduced on the first attempt; Phase 3 did not carry the habit forward. Substance is green —
a declared 13-file battery covering every named area gives 282 passed, 1 deselected, nothing red.

**m19 — Two unnecessary function-local imports.** `generation/predicate_compiler.py:151` and `:246`
defer `from ...constraint_name_safety import predicate_reference_name`, one of them inside a recursive
walk. There is no cycle to justify it: `constraint_name_safety` does not import `predicate_compiler`,
and importing both at module scope succeeds. A deferred import with no cycle hides the module's real
dependency.

### Informational

- **i20 — "renaming `referent` changes sealed bytes" is false.** The serialized key is the string
  literal `"referent"` in `SourceFile.envelope_data` (`extraction/source_manifest.py:121-125`), not
  the field name; a full field rename left envelope bytes untouched. The rename guard is worth having,
  but the record's justification for it is wrong.
- **i21 — "repository-wide" means package-wide.** `PACKAGE_ROOT` is `src/sysml_codegen`. `scripts/`
  still holds live raw selector reads outside any inventory. Unshipped probes, and the scope matches
  Phase 1's.
- **i22 — closure-proof resolution is `hasattr`, not pytest collection.** Pointing a row at a module
  constant passes. Inherited verbatim from the sibling the Phase-1 finding named as the model to
  adopt; the implementer did what was asked.
- **i23 — Informational 12's fix is an allowlist described as structural.** `FIXTURE_METADATA_ROWS`
  is a one-element tuple; the required behaviour holds and a future verification-code row is caught,
  but the comment claims more than the mechanism does.
- **i24 — the mypy baseline's reference point.** "30 errors in 8 files, unchanged" holds against
  `b4e97dd`. Against `78a9beb` — `C_base` in the manifest, and the reference for the `occurrence.py`
  diff — it is 49 in 15. The 49→30 improvement landed pre-Phase-3. The record is correct; two commits
  are both called a base.
- **i25 — the recorded unit-form list is one short.** Sweeping the fixtures finds 20 distinct compound
  forms, not 19; the extra is `[μSv/hr]` (`catf_mfe_d5/library/components/shield.sysml:142`),
  doc-comment-only, the same class the record already carves out for `[W/(m·K)]`.
- **i26 — the real-model deep-override contract test covers exactly one relationship.** Its filter at
  `test_expression_evidence_boundary.py:318` inspects only *anonymous* features. I counted the
  fixture: 1 anonymous carrier, 0 named, so the filter excludes nothing today and the test is not
  vacuous — but a named carrier in a future fixture would be silently skipped.
- **i27 — `BoundFormal.qualified_name` defaults to `""`.** `binding_source.py:194-198` substitutes an
  empty string when the parser supplies no qualified name, on an identity field that feeds
  diagnostics. Fail-open on a field whose absence should probably be named.
- **i28 — out-of-scope dynamic `getattr` is invisible by design.** An adapter-free
  `def consume(node, k): return getattr(node, k)` records nothing (`:547-548`). Stated in the
  docstring as deliberate; recorded so the residual stays visible.

---

## Reproduced numbers

Every figure in the completion record was recomputed from the auditor's own extraction. The archive
SHA-256 `269d74da…9e0bf3` matched an independent `git archive e3e1a39` byte for byte.

| Claim | Recorded | Measured | Verdict |
|---|---|---|---|
| Focused evidence/binding/compiler/unit/conversion/ownership battery | 126 passed, 1 deselected | 282 passed, 1 deselected (declared 13-file selection) | Not traceable as written (m18); substance green |
| Former clean-suite failure set after correction | 167 passed, 25 skipped | 167 passed, 25 skipped | CONFIRMED |
| D1-D4 + retained harness, 15 Phase-1 paths | 162 passed | 162 passed | CONFIRMED |
| `git diff 78a9beb -- elaboration/occurrence.py` | empty | 0 lines (also 0 vs `b4e97dd`) | CONFIRMED |
| Fresh-extraction full suite | 1 failed, 2361 passed, 34 skipped, 94 deselected; 2490/2396 | identical to the item | CONFIRMED |
| Sole failure is `test_every_consumer_cell_names_a_proof`; no collection errors | yes | yes | CONFIRMED |
| Scoped strict mypy, two boundary modules | Success, 0 issues | Success, 0 issues | CONFIRMED |
| Repo-wide mypy baseline | 30 errors in 8 files, unchanged | 30/8 at both `e3e1a39` and `b4e97dd` | CONFIRMED (i24) |
| Targeted Ruff over changed `.py` | clean | All checks passed, 29 files | CONFIRMED |
| Artifact topology/history battery | 21 passed | 21 passed | CONFIRMED |
| Compound-unit falsifier, five models | `42/9/[SI_SELF_BINDING]`, `42/9/[]`, `58/3/[]`, `7/1/[]`, `1/0/[]` | all five triples identical; zero `SI_EVIDENCE_INCOMPLETE`; expose module 15/15 | CONFIRMED |
| `density = 9400 [kg/m^3]` stop case | no longer refuses | elaborates | CONFIRMED |
| `deep_cross_scope_probe` | `SI_OCCURRENCE_MISSING`, snapshot absent | strict refuses with that code; fixture dir holds only the two `.sysml` files | CONFIRMED |
| Pins: Codegen 0.1.1, Agentic 0.1.3, `semantic-evidence/v2` | consistent | consistent across `pyproject.toml`, `_upstream_pins.py`, `uv.lock`; `uv lock --check` passes | CONFIRMED |

**No license-related silent skip.** All 34 skips come from two data-driven modules
(`test_computed_attribute_golden.py`, `test_calc_compat_parity.py`). Every license-gated module ran
for real — `test_elaboration_expose_shapes.py` reported 15 passed, not skipped.

---

## The six weak variants — the closing gate

| # | Variant | Verdict |
|---|---|---|
| 1 | Skipped inventory | **EXPLOITED — M1.** The inventory itself cannot be skipped (`_build_instance_graph` takes it keyword-only with no default, is private and unexported, and its sole caller builds it first). The reachable form is a consumer asking for a row the enumerator never produced. |
| 2 | Indexed-to-exact conversion | **REFUSED BY NAME.** Every attempt refused: indexed use, legacy fact, IR node, duck-typed lookalike, plain string, and both wrong-variant binding constructors. `grep -rn "ExactReferenceUse(" src/` returns nothing — Codegen production never constructs one — and `IndexedReferenceUse` has no path field to steal. Both layers independently mutation-pinned (removing the resolver branch takes the battery to 7 failures; removing the pre-graph refusal to 9). |
| 3 | Shortened deep paths | **REFUSED in production, one branch untested (m5).** The factory materializes once and iterates every segment with three raises and no `continue`. Two of three totality branches die under mutation; the non-`Feature` branch survives. |
| 4 | Adapter-free selector reads | **REFUSED for the named mutant, four other forms slip (m10, m11, M4).** A real adapter-free `def consume(node): return node.referent` written to disk fails manifest equality, which is the plan's stated kill criterion. Narrowing the scan to the rejected adapter-import technique is also caught. |
| 5 | Malformed unit arity | **REFUSED BY NAME.** `unit_annotated_value` is policy only — no `try`, no metatype test, no operand indexing. Forcing arity 3 through a real `= 0.2 [m]` model yields `SI_EVIDENCE_INCOMPLETE … unit annotation carries 3 operands`. Exactly one `except SemanticEvidenceError` exists between the call site and the boundary. |
| 6 | Missing diagnostic provenance | **EXPLOITED — M1 (zero of four elements), plus m12 (reference lost on expression-keyed errors).** The four indexed and occurrence refusal paths surveyed all carry code, authored reference, root-relative location, and cause correctly. |

---

## Design conformance

The architecture matches D7 and its sub-decisions.

- **One conversion boundary.** `elaborate_admitted_sources` delegates to `elaborate_loaded_extractor`
  (`orchestration/elaborated_pipeline.py:135`), so live, admitted, and capture share it. The inventory
  is the first statement inside (`:163`), ahead of extraction, elaboration, and graph allocation.
- **Refusal precedes occurrence resolution.** `_acquire` raises on the first `IndexedReferenceUse`
  (`expression_evidence.py:193-198`), before any consumer or `OccurrenceIndex.resolve_address`.
- **Closed bindings valid by construction.** All four variants exist with the right fields; an exact
  binding with no path cannot be constructed; the raw `RuntimeError` arm is gone.
- **Deep paths total.** `exact_path_from_relationship` (`binding_source.py:203`) never filters and
  never returns a shortened path.
- **Diagnostic codes.** `_EVIDENCE_CODES.get(..., SI_EVIDENCE_INCOMPLETE)`
  (`elaborated_pipeline.py:245-258`) matches D8's table, which maps both incomplete deep paths and
  depth exhaustion to `SI_EVIDENCE_INCOMPLETE` and keeps `SI_INDEXED_SOURCE_UNSUPPORTED` distinct.
- **Value-site policy over the shared primitive.** `unit_annotated_value`
  (`expression_evidence.py:257-271`) delegates every structural question to Agentic's
  `unit_annotation_value` and does not catch its arity refusal, exactly as ruling 2 requires.
- **Scoped strict.** Zero issues on both boundary modules.

Two deviations from the design as written, both recorded above: the per-consumer bypass proof the
design names as a required second layer was not built (M2), and the collision-row proof obligation is
weaker than the design's wording in two ways (M4, m9).

---

## Ownership closure — the 20-row measurement

The measurement reproduces exactly, and the closure is real rather than achieved by narrowing:

```
b4e97dd (Phase 3 start): discovered 23, reviewed  4, unowned 20   ← the owner's 20-row failure
d257ef1 (Phase 2 end)  : discovered 29, reviewed  4, unowned 25
e3e1a39 (HEAD)         : discovered 24, reviewed 24, unowned  0
```

Discovery is AST-based, not textual, and is not adapter-scoped; rewriting it to the rejected
adapter-import scope fails two tests. The 24 rows recount exactly: 4 live contextual owners, 11
neutral `ExpressionIR.operands` sites, 5 `SourceFile.referent` sites, 4 off-route. The plan's "six"
versus the record's "eleven" is modules versus read sites, not scope drift — the 11 sites live in
exactly those 6 modules.

**What the record does not say plainly: not one of the 20 reads was migrated.** The closure is 16
typed reclassifications plus 4 mechanical exclusions. Both are permitted by the plan's "by migration
**or** mechanical exclusion", `usage_extractor` is excluded rather than hidden — its rows still appear
in the discovered set carrying `route_state="off-route"` — and the exclusion is transitively checked
and holds from the stricter `cli` root as well. But the phrasing in the completion record reads as
though reads were removed, and none were.

Carried Phase-1 findings, all verified closed by mutation: **Minor 6** resolves proofs to real tests
(a bad name fails); **Minor 7** is genuinely transitive (a two-hop chain is caught where a
direct-import check would miss it); **Minor 8** parses the ledger row and checks both hashes as exact
cell equality (a hash moved to another row fails); **Informational 12** classifies structurally enough
that a future verification-code row is caught.

---

## Certification

**Verdict: Needs Work.** Certify is forbidden on two independent grounds: the product-lens ledger gate
for this run is **BLOCKED (audit-phase3-F4)** by an owner-grade contradiction, and a structural smell
(two representations manually kept synchronized) fired and is not resolved. Independently, two of the
five owner conditions on the accepted tests-after deviation are unmet, and the plan states that the
audit does not substitute for a missing kept test.

**What was verified and marked.** Phase 3's changes-required boxes for the inventory and exact
resolver, closed bindings, total deep paths, the value-site policy, the single public conversion, the
dependency contract, the disposition table, and all four carried Phase-1 findings are checked. The
validation boxes are checked except the two weak variants that were exploited. The missing-kept-tests
box and the ownership-closure parent box are left unchecked, with their verified sub-items checked.

**Recommended order of work:** M1 first — it is a live regression on a valid model, and fixing the
duplicated role decision also closes m13's coverage gap. Then M2 and M3, which are the owner's
outstanding conditions. M4 and the Minors can follow, and m14's site-set boundary is better recorded
in Phase 4's closure table than fixed here.

**Not checked:**

- **Phases 4 and 5 — not started.** No registry closure, natural-route matrix, ledger rows A5a/A5b,
  documentation sweep, or immutable artifact chain work exists. This audit says nothing about them.
  `test_every_consumer_cell_names_a_proof` remains the declared Phase-4 deferral and the sole
  substantive suite failure; the 20-of-24 empty consumer closure table was not evaluated as coverage.
- **Item-level spec conformance.** This is a phase audit. Lane A/B rows, the A1-A6 occurrence
  contract, the U-1/U-2 census reconciliation ledger, and the item's success criteria were not
  assessed except where Phase 3 touched them.
- **The Agentic upstream** was read but not re-audited; `3f8bd58` is cleared by the Phase 2 audit
  addendum and taken as given.
- **The owner-excluded suites** — the Agentic slow PDF/HTML corpus and the 15 paid/network cases —
  were not invoked, per the standing instruction.
- **`C_base` end-to-end execution.** M1's regression claim rests on the source diff and on
  `expression_evidence.py`'s birth commit, not on running `78a9beb`, which cannot import against the
  pinned Agentic.
- **The five expose-shapes tests' failing state at the stop** could not be reproduced without checking
  Agentic back to `68bca37`, outside the read-only mandate. Confirmed green at `e3e1a39` and at
  `b4e97dd` against the current upstream, which supports the record's claim that the fix is
  upstream-supplied.
- **`ruff format`** was not run as a gate; the repo is broadly non-conformant to it and nobody claimed
  otherwise.
- **Generated-package runtime execution.** No generated package was executed against a real simkit;
  correctness claims here are about elaboration, projection, and rendering, not runtime behaviour.
