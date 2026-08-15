# Audit: Elaborator Breadth — Learning Tests + Dual-Run

**Verdict:** Needs Work
**Audited:** 2026-08-08
**Branch:** source-identity-epic
**Commit:** 6bed968

---

## The Point

This work must elaborate the supported SysML model into one occurrence-aware graph before
string-based identity is lost. One modeled source occurrence must become exactly one runtime
source across calculation, constraint, and aggregation consumers. Resolved KerML/SysIDE
referents must decide the edge, innermost redefinitions must win, and unsupported authored
forms must stop before generation. Item 5 must prove that breadth with kept learning tests,
the inherited 29-cell matrix, and a classified old-vs-new graph ledger over all 37 fixtures
while the old front end remains the shipped authority.

## Summary

The production graph seed and the named Phase-1/Phase-2 fixture behaviors are substantial and
green. The full suite passes, but the work is not certifiable: the product-lens ledger is
blocked by two paths that discard resolved identity and by the missing public projection, and
the audit reproduced an unsupported invocation binding becoming a clean unbound input.

## Product Judgment

This is the right architectural direction, but it is not yet the right completed piece of
work. The append-only ledger at `product-lens.md` has one block and is **BLOCKED** by
`audit-F1`, `audit-F2`, and `audit-F3`; no later resolution block exists. No separate live
ELABORATE-FIRST epic Product-Lens gate was present.

- `audit-F1`: feature-chain resolution reduces the resolved root to a leaf and searches
  enclosing paths by that name (`src/sysml_codegen/elaboration/elaborate.py:1133-1148`). A
  nearer same-named usage can capture a binding whose loaded referent is elsewhere. This
  contradicts the owner ruling that loaded resolved referents govern.
- `audit-F2`: `sum(...)` ignores the term's resolved identity and reconstructs candidates as
  `anchor + part name + attribute name` (`src/sysml_codegen/elaboration/elaborate.py:943-969`).
  Shadowing, retyping, or a non-local term can therefore select or miss the wrong source.
- `audit-F3`: production stops at a private `InstanceGraph`; no projection feeds the public
  `ComputationGraph`/generation route (`src/sysml_codegen/elaboration/__init__.py:1-10`). The
  owner-grade public mutation obligation cannot yet be observed.

Product smells **#4** (correctness depends on internal/rendered representation) and **#6**
(real-fixture breadth checks inspect a lenient partial internal route) fired in the product
lens. Smell **#5** also fires: the legacy compatibility test deliberately preserves
invocation-as-entry-point behavior even though the new front end must fail unsupported source
forms. These smells are unresolved and forbid certification.

## Findings

### Plan completion

- **Verified:** the Phase-1 spike-parity tests remain complete and green. The 16 licensed tests
  cover C25, C8, C24, C12/C13/C15, C11, C19, deep overrides, fixed multiplicity, self-binding,
  and graph stability (`tests/conformance/test_elaboration_spike_parity.py:85-272`).
- **Verified for their named fixtures:** sibling-channel identity and literal-only
  shadowing/equal-value independence (`tests/conformance/test_elaboration_sibling_channels.py:53-104`;
  `tests/conformance/test_elaboration_shadowing.py:48-94`). Those boxes remain checked.
- **Reopened:** the D1–D5 package claim, cross-package chains, specialization/retypes, FORMULA,
  and aggregation boxes. The source-identity and redefinition-order findings below contradict
  those broader claims even though their current fixtures pass.
- **Still open as written:** constraint catalog through projection, graph snapshot round-trip,
  the internal dual-run/diff tool, all 37 classified fixture rows, and the 29-cell checklist
  (`plan.md:72-91`). These are not placeholders; their production files and ledgers do not yet
  exist.
- **Process evidence gap:** each implementation-bearing Phase-2 test, findings file, and code
  change first appears in the same commit. The FORMULA findings explicitly record
  “Implementation first-pass” (`.project/research/20260807-171548_elaborator-computed-attributes.md:44-51`).
  Repository history therefore does not certify the plan's kept-test-before-implementation
  claim (`plan.md:26`).

### Spec conformance

- **R1 — Not met.** Graph nodes and edges exist for the covered shapes, but definition-borne
  chain/expression redefinitions are queued without their owning definition and applied in
  model order (`src/sysml_codegen/elaboration/elaborate.py:563-627,876-897`). They are not
  uniformly innermost-wins.
- **R2 — Not met.** C25 fan-out, equal-valued occurrence identity, and the named producer edges
  are verified. Chain-root and `sum(...)` reconstruction still lose resolved identity, while an
  unsupported FORMULA becomes a value-less entry-point candidate
  (`src/sysml_codegen/elaboration/elaborate.py:369-410`;
  `src/sysml_codegen/elaboration/graph.py:109-131`).
- **R3 — Not met.** Self-binding/indexed/operator-expression calculation bindings are screened,
  but an `InvocationExpression` is classified as `UNBOUND` without evidence
  (`src/sysml_codegen/extraction/usage_extractor.py:881-900`). The elaborator therefore cannot
  screen it (`src/sysml_codegen/extraction/source_evidence.py:165-170`). A live strict run on
  `invocation_binding_probe` returned `diagnostics=[]`, `unbound_params=('x', 'x')`, and
  `inputs={}` for the authored binding at
  `tests/fixtures/invocation_binding_probe/design.sysml:18-20`. Unsupported authored RHS forms
  must reach a blocking readiness outcome, never an input candidate.
- **R4 — Verified for the authored evidence.** Distinct occurrences remain distinct even when
  their literal values are equal (`tests/conformance/test_elaboration_shadowing.py:70-82`).
- **R5 — Not met.** `elaboration/project.py`, complete module/entry-point/catalog projection,
  and the generation-boundary acceptance are absent.
- **R6 — Not met.** The internal parallel entry point and graph-diff harness are absent.
- **R7 — Not met.** The inherited 29-cell matrix has not been executed on the new path.
- **R8 — Partially verified.** The new package avoided the rejected expanded-population shortcut
  by using declaration extraction with `expand_templates=False`
  (`src/sysml_codegen/elaboration/elaborate.py:699-702`). Final one-authority deletion remains
  Item 6 scope and was not assessed as an Item-5 omission.

### Design conformance

- **D1–D3 and D10:** implemented for the covered shapes: occurrence-path node IDs, staged graph
  construction, the shared def-context remap, declaration population, and shared evidence
  builders are present (`src/sysml_codegen/elaboration/graph.py:37-178`;
  `src/sysml_codegen/elaboration/elaborate.py:235-310,699-863`).
- **D4:** violated by nonliteral redefinition ordering. Only literal-vs-literal tier 2 retains
  owner specificity (`src/sysml_codegen/elaboration/elaborate.py:631-656`). Chain and expression
  candidates discard that owner before application.
- **D5:** violated by leaf-reanchoring a resolved chain root
  (`src/sysml_codegen/elaboration/elaborate.py:1133-1148`). Resolution must preserve the loaded
  referent and choose only its concrete occurrence.
- **D6:** partial. Arithmetic FORMULAs and the named aggregation fixtures become computed nodes,
  but unsupported terms degrade into value-less attributes and dependency dictionaries can
  overwrite distinct qualified sources under the same sanitized key
  (`src/sysml_codegen/elaboration/elaborate.py:483-525,979-995`). Distinct semantic sources must
  remain distinct and unsupported computations must block.
- **D7–D8:** incomplete. Constraint nodes exist, but catalog adaptation and mechanical projection
  do not.
- **D9:** incomplete. Calculation readiness findings are collected, but invocation RHS forms
  bypass evidence; unrecognized constraint RHS kinds also fall through without a finding
  (`src/sysml_codegen/elaboration/elaborate.py:822-863`). Every unsupported form must receive a
  named fail-closed disposition.

### Code integrity

- `src/sysml_codegen/extraction/usage_extractor.py:881-900` reuses `UNBOUND` for an authored
  invocation RHS, and `tests/conformance/test_silent_failure_family1.py:38-53` preserves that
  legacy interpretation. This is product smell #5 and a silent fallback. The new elaborator must
  distinguish “no RHS” from “unsupported RHS” before it creates graph inputs.
- `src/sysml_codegen/elaboration/elaborate.py:369-410` has a leaky contract: one helper creates
  a computed node, creates a normal attribute, or turns an unsupported computation into an empty
  source. Unsupported computation must have a named blocking outcome instead of becoming an
  ordinary node.
- `src/sysml_codegen/elaboration/elaborate.py:899-916` detects an alias cycle, logs a warning,
  then returns the cycle node as a usable source. An alias cycle violates the source invariant;
  it must not produce a fallback edge.
- `src/sysml_codegen/elaboration/elaborate.py:84-98,703-707,1048-1063` promises every offending
  binding but aggregates calculation findings only; constraint failures raise one at a time.
  The strict failure boundary must report the complete offending set it claims to carry.
- `src/sysml_codegen/elaboration/elaborate.py:490-525,979-995` keys computed dependencies by
  sanitized rendered names. Distinct qualified referents that render to the same key overwrite
  one another. Identity, not a display key, must decide deduplication.

No `TODO`, `FIXME`, `pass`, `NotImplementedError`, broad exception fallback, or new mypy error
was found in the audited implementation.

---

## Certification

Verified the checked spike-parity, sibling-channel, and literal-shadowing plan items and left
those marked. Reopened five contradicted plan items. No spec or epic success criterion was
marked. Updated `CURRENT_WORK.md` to `needs work` and recorded the blocked product-lens gate.

Validation run on commit `6bed968`:

- Focused elaborator + dispatch suite: **87 passed**.
- Full licensed repository suite: **3222 passed, 47 skipped, 18 deselected**.
- `ruff check src/`: **passed**.
- `mypy src/`: accepted **72-error baseline**, with no error in the new elaboration package.
- `git diff --check 7461b92..HEAD`: **passed**.

**Not checked:** public projection/generation behavior because the projection does not exist;
snapshot round-trip and relocated-snapshot behavior; the 37-fixture diff ledger; the 29-cell
matrix; downstream `agentic-mbse` changes; external consumer packages/studies; or test-first
chronology beyond evidence preserved in git and the findings documents.
