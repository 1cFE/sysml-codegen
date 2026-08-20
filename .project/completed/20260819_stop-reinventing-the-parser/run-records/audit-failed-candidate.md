# Audit: Exact occurrence derivation and evidence integrity

**Verdict:** Needs Work
**Audited:** 2026-08-17
**Audited chain:** Agentic `2171016d3e3e0805525aa4cf787c55c6293dd00c`; codegen
`78a9beb956f9b5a517c08836b067f0cb0dc4ccc6`; Fusion
`028f98741a2aea7c238beed961402857af82d15f`; direct-child evidence
`588d5f7c9013d98c838a376ab9c69c95ef444649`

---

## The Point

The product uses SysIDE's resolved semantic tree as the interpretation of a model. Codegen walks
that tree to derive exact concrete occurrences, reconstructs the modeled math, and emits executable
TEAx Python. It must not replace unresolved evidence with names, order, proximity, uniqueness,
shortened paths, de-indexed references, or caller-supplied defaults. Missing, ambiguous,
unsupported, or incomplete evidence must produce the required named diagnostic before a graph,
snapshot, package, or output mutation escapes.

The certification record has the same obligation. The audited result must be reconstructable from
the exact immutable producers and the approved runner. A historical result may remain historical,
but it cannot stand in for a required run of a replacement producer unless the approved evidence
contract explicitly permits that substitution and binds the result actually cited.

## Summary

The replacement commit topology, deterministic artifacts, exact Fusion pins, evidence lock, both
Fusion model trees, and all four mechanical auditor groups reproduce. The six findings from the
first Needs Work audit remain fixed on their intended routes.

The item still cannot certify. The fresh product-lens probe found an owner-grade indexed-reference
contradiction, and broad public-path probes found four more semantic fallbacks: B3 and B4 retain
bypass routes, deep-override target construction can silently shorten a modeled chain, and the B9
registry seam accepts an empty invariant value. The execution record is also not the output of the
committed runner.

### Owner disposition after this audit — PDF finding removed (2026-08-17)

**[OWNER-VERBATIM]** “do not rerun the PDF suite anymore. It's fine -- it is totally separate to
everything we doing. I have ZERO concerns about it. Please mark this SOMEWHERE so we never run it
again.”

This settled owner correction removes the Agentic deterministic slow PDF/HTML corpus command from
the evidence contract permanently. The suite is not to be invoked for this item or future parser
work. A replacement Agentic identity does not require a replacement PDF result; the historical
result is informational only. The audit's PDF provenance finding is therefore disposed and is no
longer a certification blocker. The semantic and committed-runner findings below remain open, so
the verdict remains **Needs Work**.

## Product Judgment

**This is the right work, but it is not yet the product described by P-003 and P-004.** The fresh
product-lens gate is **BLOCKED (`audit3-F1`)**. No later ledger block resolves it.

A licensed public-route probe placed `cells#(2).mass` in a computed attribute under
`cells : Cell[1]`. Exact `C_prod` produced a zero-diagnostic graph and aliased the out-of-range
reference to `cells[0].mass` instead of refusing with `SI_INDEXED_SOURCE_UNSUPPORTED`. The same
modeled reference therefore changes meaning by consumer category. Its detection also depends on
the runtime class name `IndexExpression`, not the mapped SysIDE metatype
(`A_final:src/agentic_mbse/sysml/expression.py:686-703`;
`C_prod:src/sysml_codegen/extraction/binding_evidence.py:255-268`).

This fires two controlling product smells:

- A special consumer category exempts a reference whose user-visible meaning is unchanged.
- Correctness depends on downstream knowledge of SysIDE's runtime representation.

The finding contradicts the owner-grade refusal rule in P-003/P-004 and the A5 requirement at
`spec.md:87`. It independently forbids certification even if the remaining rubric were green.

## Findings

### Plan completion

The chain-building work is mechanically complete, but the implementation and certification phases
are not genuinely complete:

1. **Phases 4 and 5 remain open.** A5 does not refuse every public consumer; B3/B4 have public
   bypasses; deep-reference construction can return partial success; and B9 accepts an empty or
   incorrect invariant value. The claims that all A/B consumers use one fail-closed route and that
   the B1-B9 forced-failure matrix is complete are false (`plan.md:660-694,733-760`).
2. **Phase 9 remains open.** Final `independent-green.json` was assembled by an external staging
   script instead of
   emitted by `verification/run_independent_green.py` (`plan.md:1001-1056`).
3. **Phase 10's topology checks pass, but its required-run evidence claim does not.** The retained
   auditor proves hashes and internal record consistency. It does not authenticate the subprocess
   results that the external staging script supplied.

Phases 1/2, deterministic artifact construction, Fusion's current two-root proof, the six-path
child topology, and the four structural auditor groups remain verified. Any production repair will
create a new dependent identity chain under the plan's rollback rules.

### Spec conformance

| Success criterion | Result | Independent evidence |
|---|---|---|
| A1-A6 modeled result or named refusal | **Gap** | A5 can silently de-index a computed-attribute reference; product-lens `audit3-F1`. |
| B1-B10 exact evidence or named failure | **Gap** | CI-2 through CI-5 below reproduce public B3/B4, partial-target, and B9 fallbacks. |
| P-002 one modeled source to one runtime source | **Gap** | The indexed probe names one occurrence and reaches a different occurrence rather than refusing. |
| Public mutation proof for positive A1-A4/A6 shapes | Verified | Existing live/snapshot every-and-only matrix remains valid for its covered positive shapes. |
| Total L-01-L-14/U-1-U-2 reconciliation | **Gap** | The row set is total, but L-03/L-08/L-09/L-12 overstate current behavior (`C_evidence:verification/reconciliation-ledger.md:11,16-20`). |
| Immutable before/after output baseline | Verified | Artifact and expected-transition hashes reconstruct; this does not authenticate every run record. |
| Exact diagnostic authority | **Gap** | Raw `RuntimeError`/`RecursionError` can escape B3/B4 paths without code, reference, location, or cause. |
| Indexed-expression and output-alias follow-ups | Verified | Both follow-ups remain separately owned; the filing does not excuse A5's required refusal. |
| Agentic supported-shape guidance | Verified | The pinned guidance remains present. |
| Fusion checked against final rules | Verified for the audited models | Both maintained roots execute live/snapshot and mutation proofs; they do not cover the failing indexed shape. |
| P-003 close reconciliation | Open | Close was excluded from this stage. |
| Downstream remains blocked until close | Open gate | No downstream design/implementation was authorized; this Needs Work verdict keeps the block in place. |

The first `[HARD]` premise is violated where exact resolved segments are discarded or an indexed
reference is rebound. The other two `[HARD]` premises remain intact: codegen still owns concrete
occurrence materialization, and enumeration-value `::` support remains. The owner-grade `[NEED]`
fail-closed rule is not met. Non-goals were otherwise respected.

### Design conformance

D1-D4's occurrence structures, D6's direct `DocumentTier` authority, and the intended public bridge
exist. The following design invariants do not hold across all public consumers:

- **D5/D7:** Agentic owns typed operand/target evidence, but unit unwrapping, binding evidence, and
  deep-override construction reinterpret raw parser fields. The public bridge catches the typed
  errors but not the raw failures those routes produce.
- **D4/D8:** A5's valid-but-unimplemented index must refuse before graph construction. The computed
  attribute route erases it instead.
- **D9:** The CLI preflight is correctly fail-before-write, but the exported registry boundary does
  not establish or validate that its supplied type set equals the graph-derived set.
- **D10 and the immutable-run design:** the direct-child and artifact boundary is acyclic, but the
  required source-suite execution and committed-runner provenance are incomplete.

These are implementation deviations, not design tradeoffs recorded by the approved review.

### Code integrity

#### CI-1 — Indexed evidence can be erased on a public expression route

The kept A5 tests exercise input-directed binding evidence. A computed attribute reaches
`_expression_references`, where the index is not classified as the unsupported source and the graph
can bind it as an ordinary occurrence (`C_prod:src/sysml_codegen/elaboration/elaborate.py:2548-2600`).
Both index detectors use `type(...).__name__ == "IndexExpression"`
(`A_final:src/agentic_mbse/sysml/expression.py:686-703`;
`C_prod:src/sysml_codegen/extraction/binding_evidence.py:255-268`).

What must change: make exact metatype evidence and indexed-source refusal common to every public
expression consumer. Keep licensed live and snapshot tests proving the authored reference and
root-relative location, no graph/snapshot, and one `SI_INDEXED_SOURCE_UNSUPPORTED` diagnostic.

#### CI-2 — B3 still has raw operand and depth bypasses

Unit annotation handling reads raw `operands` before the typed Agentic walk
(`C_prod:src/sysml_codegen/extraction/unit_annotation.py:45-58`;
`C_prod:src/sysml_codegen/elaboration/elaborate.py:1025-1040,2548-2559`). A `[` operator whose
operand property raises produces raw `RuntimeError`. Separately, `_expression_references` recursively
calls itself with no depth bound; 1,500 nested mapped operators produced raw `RecursionError`
(`C_prod:src/sysml_codegen/elaboration/elaborate.py:2593-2600`). The bridge does not catch either
raw exception (`C_prod:src/sysml_codegen/orchestration/elaborated_pipeline.py:153-207`).

Agentic itself correctly names operand iteration and depth exhaustion
(`A_final:src/agentic_mbse/sysml/expression.py:42-54,70-118`). What must change: route these public
paths through that owner and prove exact diagnostics plus no graph/snapshot for unit-wrapper failure
and depth exhaustion. The current mock lacks `operator = "["`, so it selects the passing route
(`C_prod:tests/conformance/test_expression_evidence_integrity.py:57-64`).

#### CI-3 — B4 input bindings retain a second weaker reference interpretation

`reference_evidence` reads `referent` through `resolved_target_fact` and permits a supported
FeatureReference with `semantic_reference=None`
(`C_prod:src/sysml_codegen/extraction/binding_evidence.py:197-231`). Binding resolution later raises
raw `RuntimeError("supported reference binding has no exact semantic path")`
(`C_prod:src/sysml_codegen/elaboration/elaborate.py:2082-2090,2618-2620`). The repaired forced test
calls `_expression_references` directly and therefore does not exercise this binding lane
(`C_prod:tests/conformance/test_expression_evidence_integrity.py:74-85`).

What must change: make supported binding evidence use the one typed FeatureReference owner and make
the absent semantic path structurally impossible. Prove the actual pending-binding path through
live, admitted, and snapshot entry points with exact code/reference/location/cause and no graph.

#### CI-4 — Deep-literal target construction silently shortens modeled paths

`_reference_from_elements` filters out every element for which `resolved_target_fact` returns
`None`, and refuses only when all elements are absent
(`C_prod:src/sysml_codegen/elaboration/elaborate.py:1082-1149`). A valid-missing-valid sequence
reproduced as a two-segment reference. That is successful partial traversal and silent target loss.

What must change: require one typed exact fact for every modeled segment and refuse on the first
missing segment. Add a public deep-override regression that proves the target chain is every-and-only
and that incomplete evidence cannot mutate a graph.

#### CI-5 — B9 accepts a contract-equivalent empty invariant value

The exported generator now requires `exit_point_primitive_types` syntactically, but it trusts any
list the caller supplies (`C_prod:src/sysml_codegen/generation/registry.py:240-246,382-390`). Passing
`[]` for a graph with a root `float` output renders a registry with neither the primitive import nor
`CUSTOM_SCHEMA_TYPES`. The kept direct-call test checks only omission and `TypeError`
(`C_prod:tests/conformance/test_module_kind_faildloud.py:273-280`). The public CLI preflight itself is
correct (`C_prod:src/sysml_codegen/cli/__init__.py:319-338,1259-1309`).

What must change: derive the required set at the registry boundary or validate exact equality with
the graph-derived set. Test empty, incorrect, and duplicate inputs through every exported seam.

#### CI-6 — Final run evidence was constructed outside the committed runner

The committed runner executes commands, retains stdout/stderr, hashes
`stdout + "\n" + stderr`, probes imports, and writes the report
(`C_prod:verification/run_independent_green.py:303-355,383-410`). The retained external
`final-identities/stage_phase9_evidence.py:31-100` instead accepts caller-supplied status, output
hashes, and import files; sets each expected value equal to the supplied value; adds fields the
committed runner never emits; and writes final evidence directly. For passing pytest rows,
`output_sha256` is the JUnit-file hash, not the committed runner's stdout/stderr hash. No
`run-reports/*.stdout` or `*.stderr` record is retained, and the staging script is outside the
evidence lock.

What must change: produce the final report with the committed immutable runner, or land and approve
a reconstructable retained-measurement protocol whose inputs and transforms are themselves locked.
The final auditor must authenticate subprocess status, output, and import probes rather than only
checking a self-consistent record.

No additional material TODO, placeholder, swallowed broad exception, or skip-selected semantic
route was found. The old registry aliases at `generation/registry.py:401-403` remain compatibility
shims without in-repository callers; they are relevant to B9 because each exported seam must enforce
the same invariant, but they are not a separate finding. No `feedback_*` project memory was present.

### Historical findings

All six findings from the first Needs Work audit remain fixed on their intended routes: exact
diagnostic reference/location rendering, narrowed occurrence-identity catches, B10 helper cleanup,
single scalar-map ownership, direct proof of both Fusion model roots, and honest non-green baseline
wording.

The three findings from the second Needs Work audit are not fully fixed on public paths:

- B3 is typed in Agentic and in the selected computed-expression test, but CI-2 bypasses it.
- B4 is typed in the selected computed-expression test, but CI-3 and CI-4 retain weaker consumers.
- B9 rejects an omitted argument, but CI-5 accepts the equivalent empty or incorrect value.

## Certification Evidence

### What reproduced

- `C_evidence^` is exact `C_prod`, and its diff is exactly the six approved evidence paths.
- All audited Agentic, codegen, Fusion, and evidence worktrees are clean at their exact commits.
- A fresh deterministic artifact rebuild matched the retained build record for all five archives,
  three wheels, and the codegen history bundle.
- Fusion project and lock files pin exact full `A_final`/`C_prod` identities and exact wheel hashes;
  no editable, sibling-path, or `C_evidence` dependency is present.
- A fresh `verification/audit_evidence.py` run reported `parent_and_paths`,
  `codegen_reconstruction`, `fusion_pin`, and `artifacts_and_lock` PASS.
- The retained topology suite passed 18/18 in a fresh rerun.
- The fresh Fusion proof passed 23/23 with zero skips. It covers both `models/` and
  `exploration/ife_e2e/models/`, live and snapshot generation, real TEAx, exact consumer ports, and
  every-and-only gain/availability mutation.
- The 20 submitted run rows are internally arithmetically consistent, all eight retained JUnit
  hashes/counts match their files, and their wording keeps nonzero baselines non-green. Thirteen
  harness attempts remain nonverdicts, and the 15 paid/network cases remain explicitly unrun.

### Agentic PDF disposition

The owner disposition above supersedes the audit-time PDF finding. The suite is permanently outside
the parser-work evidence contract and must not be run again. Its old result is historical only.

## Certification

**Needs Work.** Product-lens `audit3-F1`, CI-2 through CI-5, and the untrusted final run-record
construction block certification. Spec success criteria 1, 2,
3, 5, and 7 remain or are reopened. Criteria 4, 6, 8, 9, and the bounded Fusion portion of 10 remain
verified. Criteria 11 and 12 remain open for close. The epic heading and done-state checkboxes stay
open.

**Not checked:** The Agentic PDF suite was intentionally not rerun. The 15 paid/network cases were
not run. Full Agentic/codegen/Fusion suites and project-wide static commands were not rerun by this
audit. A supplemental focused codegen command passed 30 nodes and skipped two licensed nodes because
that shell did not carry the license; an Agentic unit attempt failed collection for the same reason.
Both are harness nonverdicts, not certification evidence. Retained JUnits/baseline classifications
were inspected; the topology suite, mechanical auditor, and fresh licensed Fusion proof were
executed. No fix, merge, push, close, or pre-PR action was performed.
