# Audit: Exact occurrence derivation and evidence integrity

**Verdict:** Needs Work
**Audited:** 2026-08-18
**Branch:** codegen `stop-parser-impl-r2`; agentic `stop-parser-evidence-r2`; fusion `stop-parser-fusion-r2`
**Audited chain:** `A_final` `3f8bd587af40f05b929dd56645901dada7daea37`; `C_prod`
`707346d616e508e55103c9246b63d172ed6a862b`; `F_final` `2243b7ce116c0a12fb0c09a81262c5c2ec879f69`;
`C_evidence` `a184133b99f7f71451c0b4af5a33b709f988eca2`; artifacts
`/tmp/stop-parser-rev2/artifacts-final-v3`

---

## The Point

The product is three steps and nothing else: parse the model with a SysML v2 parser, walk the
parser's resolved semantic tree to reconstruct the authored math, and emit that math as executable
TEAx Python. Every decision on the way is taken from the parser's own resolved identity — never from
a spelling, a Python class name, a count, a position, or a caller-supplied substitute. One modeled
source occurrence becomes exactly one runtime source.

An authored form the toolchain cannot honor has exactly two honest outcomes: resolve it through the
parser, or refuse **by name, before a graph, snapshot, package, or output mutation escapes**, naming
what the modeller wrote and where they wrote it. A form the language defines but the generator has
not implemented gets a distinct unsupported-capability diagnostic that does not blame the model.

That obligation is the whole item. Sources: `.project/product/P-003-no-workarounds-for-bad-models.md`
and `P-004-product-identity-parse-walk-emit.md` (owner-verbatim), with
`P-002-exact-owner-anchoring.md` as the exact-occurrence companion.

## Summary

The occurrence-derivation lane (A1–A6) is delivered and genuinely proved: every fallback election is
gone, each row has real-model positive and refusal cases, and the every-and-only mutation criterion is
carried by real TEAx execution on both the fixture matrix and the actual Fusion model tree. The
evidence chain is real too — I reproduced the topology, all sixteen artifact and evidence hashes, and
the mechanical auditor independently, and confirmed the auditor refuses mutated inputs rather than
rubber-stamping them. Nine of the ten Lane B rows are met, several with better proof than the row asked
for.

It fails on refusal quality — the half of the product's promise that says an unhonorable form is
refused **by name**, naming what the modeller wrote and where. A non-`sum` invocation such as
`max(cell.capital_cost, 1.0)` now refuses *after* the graph is built, with no authored reference and
no `file:line`, under a code that blames the model; at `C_base` the same model produced a pre-graph
diagnostic carrying both. Alongside it, the decision that makes a reference fan out across occurrences
moved from an exact declaration identity to the function's **name**. And that invocation case is one
of five: the readiness lane renders code-and-name only, two refusal codes name nothing locatable, and
two **committed fixtures** exit the public CLI with a bare eight-frame Python traceback. Two smaller
gaps sit behind those: B6's own site still resolves types through the permissive unqualified table,
and the shipped reconciliation ledger carries neither the disposition mapping the spec's criterion
names nor correct proof citations for three of its sixteen rows.

The item's other open weak variant, "skipped inventory", was attacked and **held** — the route is
structurally closed, and 155 models produced zero inventory misses.

None of this is unfixable, and none of it touches the artifact machinery. It is a bounded remediation
round on the elaboration boundary plus two evidence-document corrections.

## Product Judgment

**Is this the right piece of work? Yes — and it is mostly done right.** The item removed the whole
class of "choose an occurrence by proximity, order, or uniqueness" defects and replaced it with
derivation from parser identity, with real-model proof on both the positive and the refusal side. The
pre-graph evidence inventory is load-bearing rather than decorative, an indexed reference cannot lose
its index because `IndexedReferenceUse` carries no path at all, and the registry derives its wrapper
set from the graph with a typed refusal. That is the product's point working.

**Product-lens ledger gate: BLOCKED (`audit-final-F1`).** The run I appended to
[product-lens.md](product-lens.md) is `audit-final`; it re-derived the Point independently and
returned a `BLOCK` on the invocation route, with `audit-final-F2` through `F5` disposed. I verified
`F1` myself on the public route rather than accepting it, and the reproduction is in Finding 1 below.
The finding is graded against owner-verbatim `P-003`/`P-004` and contradicts two of the spec's own
success criteria, so it forbids Certify. Finding 2 is the same contradiction on four further shapes,
found by attacking the plan's own open weak variant; it is owner-grade for the same reason and blocks
on its own.

Every earlier block in the ledger is resolved by citation and I re-checked each: `design-F1` (design
rev 2), `audit3-F1` (fixed at exact production identity, independently confirmed), `audit-phase3-F4`
(fixed, confirmed by code reading at `C_prod`), `audit-phase4-F1` (fixed, confirmed).
`audit-phase4-F2` is partially fixed — route force is now per cell, but the cell-naming assertion still
passes on any non-empty string — and is carried forward here as Finding 6.

**Structural smells that fired and are not resolved by this judgment:**

- *A special category exempts a case whose user-visible meaning is unchanged.* The `>= 3` segment-count
  carve-out added to the off-route computed-attribute classifier keeps a golden baseline green in a
  module no production code imports (Finding 5).
- *Correctness depends on downstream knowledge of an internal representation.* Two `type(...).__name__`
  decisions survive on the public route (Finding 4), and `owner_kind` — a Python class name — crosses
  the package boundary as a string and decides an ADR-002 validation outcome (Finding 7).
- *A test passes by selecting one route.* Ten consumer-matrix cells and the registry/exit-type lane are
  proved on hand-built input rather than a parsed model (Finding 6).

Escalating these into this judgment is what the rubric requires; it does not resolve them. Findings 4,
5, 6 and 7 are DISPOSE-grade — they are real and located, but none is an owner-grade contradiction on
its own.

## Findings

### Plan completion

Phases 1, 2, 2b, 3, 4 and 5 are recorded complete, each with an independent audit or re-audit, and I
spot-verified the identities and the closing evidence rather than the narrative. Three boxes remain
unchecked, and all three are honest:

- **Phase 3 closing gate, weak variant "Missing diagnostic provenance"** (`plan.md:1000`) — left open
  for this independent audit to attack. **It is now EXPLOITED**; see Finding 1. The plan's own rule
  applies: a weak variant the audit succeeds in exploiting returns to the owning phase.
- **Phase 3 closing gate, weak variant "Skipped inventory"** (`plan.md:992`) — attacked and
  **REFUSED**; the route is structurally closed and 155 models produced zero inventory misses. Details
  under Finding 2. This box is closable; I have checked it.
- **Phase 5 checkout-integrity equality** (`plan.md:1265`) — cannot be closed because
  `run-records/entry-status.md` never recorded entry digests for Fusion, TEAx and 1costingfe. The
  record says so plainly and invents no equality. I independently confirmed all five checkouts match
  the recorded *final* state (TEAx, 1costingfe and Agentic clean at their pins; Fusion still on
  `item8-fusion-embedded-catalog` at `be1ee7c0` with the recorded dirty digest
  `d8a9922b…`). The limitation stands; the disclosure is correct.

The Phase 5 record's own numbers hold up. Every one of the ten artifact SHA-256 values and all six
evidence-file hashes recompute exactly, and the 21 runner lanes in `verification/independent-green.json`
match the plan table one-for-one.

### Spec conformance

**Lane A — occurrence derivation: all six rows MET.**

| Row | Evidence |
|---|---|
| A1 | `_select_occurrences` gone (absence pinned at `tests/unit/test_elaboration_import_boundaries.py:216`); derivation at `elaboration/elaborate.py:2170-2237` + `occurrence.py:449-514`; five required cases at `tests/conformance/test_occurrence_domain_derivation.py:56-165` on a real fixture, refusals asserting code, authored reference and `root-0/model.sysml:52` |
| A2 | `elaborate.py:2286-2369`; positives and both refusals at `tests/conformance/test_occurrence_calc_domain_derivation.py:46-203`; producers filtered to the consumer domain first, so no sole-candidate arm survives |
| A3 | `_resolve_leaf` gone, no descendant search anywhere in `src/`; the four required shapes at `tests/conformance/test_definition_owned_reference_positions.py:49-102` |
| A4 | `elaborate.py:2252-2264`, `occurrence.py:421-447`; package-scope positive and consumer-scope refusal both present (`test_occurrence_domain_derivation.py:70`, `tests/unit/test_elaboration_containment_address.py:144`) |
| A5 | `expression_evidence.py:186-215,252-278`; `SI_INDEXED_SOURCE_UNSUPPORTED` with `consumer is None`, authored reference and root-relative location, proved pre-graph by spies across five public arms (`test_expression_evidence_integrity.py:521,1100-1180`) |
| A6 | owner-qualified writer filter at `occurrence.py:572-648`, refusal at `:726`; unrelated sole candidate correctly excluded (`tests/fixtures/multiplicity_writer_authority/model.sysml:22-26`) |

**The every-and-only mutation criterion is met**, and by real execution rather than graph assertions:
`tests/execution/test_occurrence_derivation_mutation_teax.py:43-211` runs four occurrence shapes
through TEAx on live and snapshot routes, and `fusion-tea/tests/test_occurrence_mutation_teax.py`
does the same on the actual Fusion model tree with exact consumer-port and moved-output set equality.
One narrow hole: no mutation passes through an occurrence derived from a *root-usage* modeled bound
(`tests/fixtures/occurrence_execution_matrix/runtime.sysml:60-61` has no consumer), and the whole
mutation lane is excluded from the default test command by `pyproject.toml:46`.

**Lane B — nine of ten rows MET; B6 PARTIAL.** B1, B2, B3, B4, B5, B7, B8, B9 and B10 are met, each
with proof of the type its row demands — forced adapter failure, real `FeatureChainExpression`
subtypes, a forced failing iterator proved at every consumer on both public arms, a real user package
named `SI`, forced missing-identity redefinition cases, and both retained licensed probes with their
verdicts committed (`verification/probes/b8-real-verdict.json`, `b10-verdict.json`). B6 is the
exception; see Finding 3.

**Other criteria.** P-002 holds. The criterion "Ill-formed models receive diagnostics naming the
reference, source file and line … valid but unimplemented forms receive a distinct
unsupported-capability diagnostic that does not blame the model" is **not met** (Findings 1 and 2);
it holds on the indexed and occurrence routes, which are the ones the item's tests cover, and fails on
five others. Both required backlog rows
plus `[DEEP-QUALIFIED-OUTPUT-WIRING]` are filed in `.project/backlog/BACKLOG.md:30,36,42`. The
agentic guidance (`docs/patterns/plant-idiom.md` at `A_final`) states the supported shapes, the
context each needs, the refusal-versus-limitation distinction, and — verbatim — "The semantic owner
class is one input to this derivation. It does not determine the result by itself." Fusion models were
verified and left unedited; `F_final` changes only `pyproject.toml`, `uv.lock` and three test files,
and pins `C_prod` exactly. The reconciliation-ledger criterion is only partly met (Finding 8).

**Non-goals respected.** No strategy objects, registries, compatibility layers or second resolution
architecture were added; P-002 was not weakened; `::` references were not blanket-refused; indexed
evaluation was not implemented.

### Design conformance

The implementation follows the design's one-architecture diagram: one evidence-acquisition route per
semantic fact, a private immutable `ContainmentAddress`, a private producer index, `ReferenceUse` as a
closed union beside `ExpressionIR`, and a separate total factory for deep redefinition paths
(`extraction/binding_source.py:15-20,245`). No flag or fallback selects the retired behavior.

The design's documentation obligations are discharged: reference documents 00, 01, 08, 19, 20 and
`overview.md` updated, REQ-REG-09 re-pointed at `test_generation_exit_type_preflight.py` with PASS,
diagnostic documentation for all four new codes, the stale `deep_cross_scope_probe/design.sysml:75`
comment corrected, and the selector-ownership manifest checked in as executable data
(`tests/conformance/test_expression_evidence_ownership.py`) in both repositories.

One deviation the design did not sanction: the design's own census ledger records L-13 as
"Backlog only" and L-14 as "Out of scope", and requires
`verification/reconciliation-ledger.md` to copy that table with exact test IDs. The shipped ledger
drops the mapping and presents both rows as proved (Finding 8).

### Code integrity

Findings 1 through 7 below are the code-integrity and product-drift results, ordered by severity.
Lower-value observations recorded without a finding: a stale code citation in
`tests/conformance/test_predicate_unit_annotation.py:6-7` pointing at the deleted
`_expression_references`; back-compat aliases `generate_registry_from_graph` /
`generate_registry_function` (`generation/registry.py:399-400`) whose only callers are the re-export
list and one test; and `_copy_required` in `verification/run_independent_green.py:534` losing its last
call site in this range.

---

**Finding 1 — A supported authored form now refuses after the graph, with no provenance, under a code
that blames the model. (owner-grade; BLOCKS certification)**

`src/sysml_codegen/elaboration/project.py:688-692`, and the deletion at
`src/sysml_codegen/elaboration/elaborate.py` of `C_base`'s `_SUM_FUNCTION_ID` guard
(`78a9beb:elaborate.py:163,2588`).

Measured at `C_prod`, license loaded, real model through `sysml-codegen generate`. Model: `Bank` with
`part cell : Cell[1]` and `:>> capital_cost = max(cell.capital_cost, 1.0);`.

```text
ERROR: Code generation failed: exact graph projection failed:
SI_SNAPSHOT_INVALID: unsupported invocation survived on 'NonSumSingularProbe__the_bank__capital_cost'
```

The refusal carries no authored reference (`max(cell.capital_cost, 1.0)`), no root-relative
`file:line`, and no cause chain; it fires at projection, after the graph is built; and
`SI_SNAPSHOT_INVALID` tells a modeller their model is invalid when the truth is that the generator has
not implemented that invocation. At `C_base` the identical shape raised `_UnsupportedExpressionError`
inside `_expression_references` and surfaced as a **pre-graph** readiness diagnostic
`SI_EXPRESSION_SOURCE_UNSUPPORTED` carrying reference and location (`78a9beb:elaborate.py:2452-2462`).
This is a regression introduced by this range, on the exact property the item exists to guarantee, and
it exploits the plan's open weak variant "Missing diagnostic provenance" (`plan.md:1000`).

Behind it, the plurality decision moved from identity to spelling:
`agentic-mbse@3f8bd58:src/agentic_mbse/sysml/reference_use.py:355-364` returns
`function.name == "sum"`, where `C_base` compared the reload-stable declaration UUID of
`NumericalFunctions::sum`. Whether a reference fans out to every modeled occurrence is now decided by
what the function is called. I could not author a user-defined function literally named `sum` that
SysIDE 0.8.4 accepts in this position, so the fan-out harm is unproven in practice; the
identity-to-spelling regression itself is not in doubt, and projection's later
`function_qn != ["NumericalFunctions", "sum"]` check is the only thing standing behind it.

What should change: restore a pre-graph refusal for an unsupported invocation, carrying the authored
reference and root-relative location under an unsupported-capability code rather than
`SI_SNAPSHOT_INVALID`; and decide plurality from the resolved function declaration's identity, not its
name. Kept tests: a licensed public-route model with a non-`sum` invocation asserting that diagnostic
on every public arm.

**Finding 2 — Named-refusal provenance is not a property of the public boundary. Five shapes drop it,
and two committed fixtures produce a bare Python traceback. (owner-grade; BLOCKS certification)**

Finding 1 is one instance of a family. Attacking the plan's open "Missing diagnostic provenance" weak
variant on real models through the public CLI at `C_prod` produced four more, each reproduced with the
license loaded:

- **A bare traceback, no code token at all.** `sysml-codegen generate --models
  tests/fixtures/anonymous_return` exits 1 with an eight-frame Python stack trace ending in
  `ValueError: Calc def 'AnonReturn' has an anonymous 'return' …`. `tests/fixtures/zero_output_calc`
  does the same. The cause is narrow: `extraction/extractor.py:252` and `:263` raise a plain
  `ValueError`, which is not among the five exception classes `elaborate_loaded_extractor` contains
  and which `run_codegen` does not catch either. Both are **committed fixtures**, so this is not an
  exotic shape. I reproduced this one myself.
- **The readiness lane renders code and name only.** `ElaborationError.__str__`
  (`elaborate.py:127-132`) formats `code: usage_qn.param`, and `ReadinessFinding`
  (`extraction/source_evidence.py:52-58`) has no location field at all, so its `detail` — which holds
  the authored text — is dropped. All three `ReadinessCode` values are affected; e.g.
  `SI_EXPRESSION_SOURCE_UNSUPPORTED: ExprSrcLib__Asm__c1.a`.
- **`SI_REDEFINITION_INVALID` names nothing** (`elaboration/occurrence.py:279`): "applicable
  definition writers have no unique most-specific owner", with no reference, no location, and not even
  the attribute or the two conflicting definitions.
- **`SI_CONSTRAINT_UNATTACHED` leaks a parser repr** (`elaborate.py:731-735`): the owner prints as
  `syside.core.QualifiedName(['ItemConstraintLib', 'Payload'])` rather than
  `ItemConstraintLib::Payload`, with no location.

The capture arm is no better on the invocation shape — `snapshot --models` fails at the same
`project.py:688-692` site, so `--from-snapshot` is unreachable — and it is worse on paths: a
parse-time refusal there prints the private staging path
(`/tmp/sysml-codegen-sources-…/root-0/model.sysml:17:13`), which no longer exists when the user reads
the message.

What should change: make provenance a boundary property rather than a per-code habit — every public
refusal carries a code token, the authored reference, a root-relative `file:line`, and its cause, with
one kept test per public arm asserting the four elements are present for every reachable code. The two
committed-fixture tracebacks are the first repair.

**Weak variant "Skipped inventory": REFUSED BY NAME — could not be exploited.** The route is
structurally closed, not merely guarded: the enumerator selects sites from the same
`Feature`/`include_subtypes`/`qualified_name is not None` predicate the writer selection uses
(`expression_evidence.py:289-292` against `elaborate.py:748-758`), the other three lookups key on
`declaration_id_for`, which itself refuses a QN-less element (`identity.py:72-76`), and `inventory` is
keyword-only with no default on the single private graph builder. Empirically, 155 models — all 145
committed fixture roots plus ten hand-authored shapes — were driven through `elaborate_model_paths`
with the lookup instrumented: **zero inventory misses**. Deleting one site from a mutated copy
produced the correct containment, `SI_EVIDENCE_INCOMPLETE` naming the authored expression and
`root-0/model.sysml:117`. The `plan.md:992` box is legitimately closable.

**Finding 3 — B6's own site still maps types through the permissive unqualified table. (spec gap)**

`src/sysml_codegen/extraction/extractor.py:363` looks the typing target's qualified name up in
`SYSML_TO_PYTHON` (`src/sysml_codegen/core/type_mapping.py:12-21`), which still carries bare keys
`"Real"`, `"Integer"`, `"String"`, `"Boolean"`. A user type declared at the root namespace and named
`Real` has `qualified_name == "Real"` and is accepted as `float` — the simple-name defect B6 names,
in a narrower form. The refusal message two lines below promises the opposite ("expected one of
`ScalarValues::Boolean`, …"). This is a knowing carve-out, not an oversight: `cafd4cb` introduced the
derived qualified-only view `QUALIFIED_SYSML_TO_PYTHON`, pointed the elaborator at it
(`elaborate.py:1975`), and left the extractor on the permissive table. Blast radius is limited because
the elaborator refuses such a type downstream, but the B6 site itself does not meet "uses exact
qualified typing". What should change: read the qualified-only view here too, and add a root-namespace
lookalike to the B6 fixture.

**Finding 4 — Two `type(...).__name__` decisions survive on the public route, one failing open.**

`src/sysml_codegen/extraction/extractor.py:246` gates the anonymous-`return` refusal on
`type(owning_membership).__name__ != "ReturnParameterMembership"`. It fails **open**: if SysIDE renames
the class or the model uses a subtype, the refusal stops firing and a garbage-named output channel
ships. `src/sysml_codegen/elaboration/elaborate.py:730` grades a constraint owner by
`type(owner).__name__` against a closed map; it fails closed, but a valid model whose constraint owner
is a subtype of a mapped kind is refused wrongly. Neither site is named in the B-row ledger or any
transition row, and both are pre-existing rather than introduced here — but they are the pattern the
item removed everywhere else, and `elaborate.py:730` is the site behind the known Gate-A
owner-classification issue. What should change: file them as a named follow-up row before close, or
route both through the mapped-metatype adapter.

**Finding 5 — A segment-count carve-out was added to keep an off-route classifier's baseline green.**

`src/sysml_codegen/extraction/computed_attribute_extractor.py:179-190` adds
`len(reference_chain) >= 3 → UNRESOLVABLE`. `extract_computed_attributes` has no caller under `src/` —
only tests — so this is new production logic written into dead code so that a golden baseline keeps its
old answers after `attribute_refs` became exact. It also makes the `EXPOSE_CHAIN_TENTATIVE` gate at
`:239` unreachable for the exact three-segment case its own comment cites. A two-segment chain with the
identical authored meaning still takes the old path, so the new category exempts a case whose
user-visible meaning is unchanged. What should change: delete the module and its tests, or give the
branch a modeled-evidence justification and record the carve-out in the transition ledger.

**Finding 6 — The closure matrix asserts more real-model force than it has.**

`tests/conformance/test_expression_evidence_integrity.py:1396-1404`
(`test_every_consumer_cell_names_a_proof`) still passes on any non-empty string, and `:1382` checks
exemption reasons for truthiness only, so an empty-in-substance cell can pass as covered — the
undelivered half of `audit-phase4-F2`. Ten of twenty consumer-matrix cells are proved by injecting a
hand-built expression through a monkeypatched `_acquire` (`:93-107,957-973,1030-1042`); the
`chaining_features` closure proof is fully monkeypatched
(`tests/unit/test_expression_evidence_boundary.py:544-560`); and the registry and exit-type lanes run
entirely on hand-built `ComputationGraph`s, with the "every exported seam" parametrization exercising
the same function object three times. Separately, the 460-line `test_source_identity_extraction.py`
deletion removed real-model coverage of cross-owner consumers sharing one exact referent and of
aggregation terms retaining exact targets — both P-002's own subject — with no replacement. What
should change: make the cell assertion structural, and restore those two real-model proofs.

**Finding 7 — An ADR-002 validation outcome is decided by a URL substring, a Python class name, and a
`return True` fallback.**

`agentic-mbse@3f8bd58:src/agentic_mbse/validation/adr002.py:342-393`. Method 1 classifies by
`"library/" in leaf.document_url` / `"designs/" in leaf.document_url`, which
`reference_use.py:256-264` explicitly forbids in words ("a URL, path, package name, or qualified name
has no classification role"). Method 3 now reads `leaf.owner_kind == "CalculationDefinition"`, where
`owner_kind` is `type(owner).__name__` (`reference_use.py:232`) — this range **replaced** a mapped
`SysideAdapter.is_instance` call with the class-name string. The final `return True` asserts the
reference *is* a calc output when every signal is absent, exempting it from the V2 check. To be exact:
the URL branch and the `return True` fallback are pre-existing and were carried forward; the
metatype-to-class-name substitution is this item's. It is validation, not the generation route, so it
is DISPOSE-grade — but it is the item's own anti-pattern reintroduced. What should change: classify
from the resolved owner's mapped metatype, delete the URL branch, and make total absence of evidence a
refusal.

**Finding 8 — The shipped reconciliation ledger neither carries the required mapping nor cites three of
its rows correctly. (spec gap)**

`verification/reconciliation-ledger.md`. The spec's criterion is that every census row maps "to an A/B
row, an explicit disposition above, or a separately filed follow-up", and the design
(`design.md:1878`) requires the ledger to copy that table with exact test IDs. The shipped ledger has
three columns — Row, Final proof, Production identity — with no A/B-row column, no disposition column,
and test *files* rather than node ids. The mapping exists only in `design.md:1859-1877`, which is not
the artifact an independent auditor is handed. Three rows are wrong or overstated:

- **L-14** (parameter groups named after source files) is recorded in the design as out of scope, kept
  rendering policy. The ledger gives it a "Final proof",
  `tests/conformance/test_output_schema_contract.py`, which covers multi-output schema shape and was
  not touched by this item.
- **L-13** (output-alias first-wins) is recorded in the design as backlog-only. The ledger names a
  documentation-contract test whose relevant node proves only that the backlog row was *filed*.
- **L-05** (skipped redefinition endpoint) names `tests/conformance/test_feature_typing_integrity.py`,
  which contains zero redefinition, slot-index or feature-slot coverage. The real B7 proofs are in
  `tests/unit/test_elaboration_occurrence.py:260,291,328`.

Two adjacent citation errors sit in `verification/expected-transitions.md`: the B8 row at `:28` names
`tests/conformance/test_semantic_evidence_boundary.py`, a file that has never existed in this
repository's history, and the B6/B7 row at `:32` names a file with no B7 coverage. Nothing validates
these citations — the probe-fixture lock hashes the ledger's bytes but does not resolve its test names.
What should change: add the disposition and A/B-row columns, correct the five citations to real test
node ids, and add a check that every cited path exists.

**Finding 9 — Four self-comparisons and one redefined pin weaken the evidence chain's independence.
(DISPOSE)**

At audit time the run-count check compares `counts` to `expected_counts` written by the same producer
and never recomputes from the retained JUnit (`verification/audit_evidence.py:519-523`); the real
constant comparison runs only at capture time (`run_independent_green.py:150-156`).
`tests/conformance/test_evidence_artifact_topology.py:1016-1039` asserts `REQUIRED_RUN_IDS` against a
verbatim copy of itself. `tests/conformance/test_probe_fixture_lock.py:238-240` re-reads the file it
was parsed from. And `verification/build_artifacts.py:496-508` re-runs `git archive` with an empty
prefix and compares *that*, then writes the pinned value rather than the measurement into the manifest,
while the auditor only checks it is well-formed hex (`audit_evidence.py:186-190`) — so the shipped
archive bytes are no longer bound to the external pin. Also `run_independent_green.py:364` dropped `-I`
from the import probe, so a module could resolve out of user site-packages and be recorded as artifact
provenance, and the `costingfe-pytest` skip policy pairs a fixed reason with the repo-wide node pattern
`tests/.*` (`:1044-1049`). What should change: recompute counts from the retained JUnit at audit time,
derive one `REQUIRED_RUN_IDS` copy from the other, restore the pin against the shipped archive, restore
`-I`, and narrow the skip pattern. None of this invalidates the current run — I reproduced every
artifact and evidence hash and the auditor refuses mutated inputs — but each is a leg that would not
catch a future divergence.

**Finding 10 — The two retained probes can no longer be executed against the code they certify.
(DISPOSE)**

`.project/active/stop-reinventing-the-parser/probes/b8_resolved_fact_totality.py:11` imports
`feature_chain_facts`, a symbol this item deleted and now pins absent; `probes/b10_document_origin.py:52`
calls `_source_file(..., model_paths=[...])`, a parameter this item removed and now forbids by AST
gate. The spec asks for retained probes and the files and their hash lock are retained, so the rows are
satisfied as measurement records — but neither can be re-run to re-measure its verdict, which is
exactly what a future challenger would want. What should change: state that plainly beside the
verdicts, or port the probes to the final API.

---

## Certification

**Checked and verified independently, not read from the record:**

- Topology: `C_evidence^ == C_prod`; the changed-path set is exactly the six evidence files; `F_final`
  pins `C_prod` and never `C_evidence`; `a184133` appears nowhere in the Fusion tree.
- Hashes: all ten artifact SHA-256 values and all six evidence-file hashes recomputed and matched.
- The committed auditor returned PASS on all four groups from a clean invocation, and **refused**
  three adversarial inputs — a wrong `C_evidence`, a wrong `F_final`, and a byte-mutated wheel (exit 2
  with a named hash mismatch) — so it is not vacuous.
- A licensed run of the seven Lane A/B conformance suites at `C_prod`: **188 passed, zero skips**. The
  same file without the license key gives 7 failed / 112 skipped, which proves the licensed arms
  genuinely ran.
- Both weak-variant attacks the plan left open, on real models through the public CLI: "skipped
  inventory" refused (155 models instrumented, zero misses, plus a site-deletion mutation proving the
  containment), "missing diagnostic provenance" exploited five ways.
- The five external checkouts against their recorded final state.
- A full suite run from this worktree: 2362 passed, 13 failed, 34 skipped, 2 errors, with five modules
  unable to collect. Every failure and error is a documentation or evidence-contract test conditioned
  on the missing `STOP_PARSER_ARTIFACT_SOURCE_INPUTS` manifest — **no product-code test failed**, and
  the isolated-artifact run in the record is the authoritative one. Worth noting only because the
  suite is not runnable from a plain worktree without that environment.

**Marked:** nothing. No spec success criterion checkbox was changed, no plan phase box was checked, and
the epic was not touched. The item's own success-criteria list was already marked complete by the
implementation run; I have not unmarked it, but this audit's findings mean two of those criteria
(diagnostic provenance for valid-but-unimplemented forms; the reconciliation ledger) are not met as
written. `CURRENT_WORK.md` is updated to "needs work".

**Not checked:**

- The 21-command isolated battery was not re-executed. I verified the record's internal consistency,
  the runner's identity, and the retained output hashes; I did not rebuild the wheelhouse or re-run
  Fusion, TEAx or 1costingfe.
- The Fusion 58-failure baseline is asserted as historical but no retained artifact measures it at the
  frozen parent `824a876e`, so "exact historical baseline" rests on the failure text, not on a
  pre-change measurement. I did not reconstruct it.
- `C_prod` and `A_final` are on no remote, so `F_final`'s git pins cannot resolve for anyone but this
  machine. That is the owner's reserved push, not a defect, but the chain is locally reproducible only.
- Generated-package runtime behavior beyond the mutation lanes, the snapshot-format internals, and the
  three off-route extraction modules the spec explicitly excluded.
- Agentic's PDF/HTML corpus and the 15 paid/network cases, both owner-excluded.
- I did not review the ~2,077 lines of `usage_extractor`'s hand-rolled expression walkers that the
  ownership manifest exempts by `route_state="off-route"`; the exemption is the spec's, but its size is
  worth an owner's attention.

**Next step:** a remediation round owning Findings 1, 2, 3 and 8, then a targeted re-audit of those
four before close. Findings 4, 5, 6, 7, 9 and 10 are DISPOSE-grade and can be carried as named
follow-up rows if the owner prefers. `elaborator-downstream` stays blocked until the item closes.

The scope is bounded and none of it touches the artifact chain: one refusal path restored to pre-graph
with an unsupported-capability code, one plurality decision moved back to declaration identity, one
boundary that guarantees four provenance elements on every public refusal, one type-table lookup, and
two evidence documents corrected.
