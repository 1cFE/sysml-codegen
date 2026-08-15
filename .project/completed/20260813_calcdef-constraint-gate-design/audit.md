# Audit: CONSTRAINT-SEMANTICS Item 6 — Calculation-Definition Gate Capability Design

**Verdict:** Certify
**Audited:** 2026-08-13
**Branch:** `item7-rebuild`
**Commit:** `7369b3e`
**Delivery type:** Design / Planning

---

## The Point

Physics constraints must produce trustworthy design-search evidence. For this capability, one
asserted calculation-definition constraint usage expands into one check per concrete calculation
occurrence. The authored usage remains one coverage member, while every occurrence remains a
distinct result that can be joined back to its exact calculation. The governing product frame is
owner-originated; the per-occurrence and two-tier rules are `[AGENT] (ratified by owner,
2026-08-12)`, not owner-originated settled rules
(`.project/active/constraint-semantics-contract/rulings-20260812.md:11-20,25-35`).

The delivery must design that behavior through the existing exact instance-graph authority. It
must not implement production behavior in Item 6, reconstruct attachment from rendered names, or
create another occurrence inventory
(`.project/backlog/epic_constraint_semantics_contract.md:872-930`).

## Summary

Item 6 is certified as a design/planning delivery. The probe, spec, revised design, three-round
independent review, and follow-on implementation item cover every Item 6 success criterion and
deliverable. The provenance correction regraded all eleven unsupported `[NEED]` requirements to
source-qualified `[INFERRED]` without changing their substantive clauses; no manufactured owner
grade remains in the delivery artifacts.

No production Item 6 implementation was required or performed. The proposed production symbols,
diagnostics, and version bumps remain absent, as expected. All future implementation acceptance
boxes in `spec.md` remain open.

## Product Judgment

**This is the right piece of work. Product-lens gate: CLEAR.** The full ledger contains the earlier
spec `CLEAR` block and the independent audit `CLEAR` block; neither records a blocking finding
(`product-lens.md:3-41`). The live epic product-lens gate is also `CLEAR`
(`.project/backlog/epic_constraint_semantics_contract.md:118-135`). No unresolved earlier `BLOCK`
exists.

The design keeps one graph/catalog authority, exact occurrence identity, complete per-occurrence
results, and fail-closed joins. None of the five audit code/test smells fired. The design-review
smells are also disposed: the instance graph retains invariant ownership, and the consumer does not
compensate for a producer guarantee. The final independent design review is **Approve** and records
no owner/`[HARD]` contradiction or ownership ambiguity
(`design-review.md:521-565`).

## Findings

### Plan completion

Item 6 has no `plan.md`. That is appropriate for its authoritative **Design / Planning** type. The
filed `implementation-item.md` is the required follow-on plan, not an executed production plan.

All deliverables are present and verified:

| Deliverable | Audit result |
|---|---|
| `probes/findings.md`, executable probe, and zero/one/multiple models | Reproduced; exact attachment evidence is complete for the probe's stated scope. |
| `spec.md` | Carries the future public contract, source grades, non-goals, and parked premise conflict. |
| `product-lens.md` | Every ledger block scanned; effective gate is `CLEAR`. |
| `design.md` | Implementation-ready architecture and file/acceptance manifest cover the required behavior. |
| `design-review.md` | Rounds 2 and 3 are present; Round 3 resolves the remaining findings and ends `Approve`. |
| `implementation-item.md` | File-level scope, prerequisite gates, immutable-pin rules, phases, estimate, and public acceptance matrix are complete. |
| Epic back-reference | Item 6 names the artifact home, required reading, deliverables, and six success criteria. |

### Spec conformance

#### Authoritative Item 6 success criteria

- **SC-1 — Exact attachment without a second authority: verified.** The licensed probe exited zero
  with `probe_status: PASS`, exact match counts `0/1/2`, and
  `rendered_names_used_for_lookup: false`. The repeated-use case produced two composite attachment
  identities but one current constraint identity, proving the required identity extension without
  proposing another inventory (`probes/probe_calcdef_attachment.py:106-208`;
  `probes/findings.md:8-53,117-183`).
- **SC-2 — Required behavioral breadth: verified in design.** Zero/one/many, sibling repeated
  definitions, literal/design-attribute/producer actuals, modeled defaults, defaultless supply,
  polarity, failure at first/middle/last positions, graph-v4 snapshot round-trip/refusal, receipts,
  fingerprints, and seals all have named mechanisms and public observations
  (`design.md:212-294,387-412`).
- **SC-3 — Usage/result identity: verified in design.** One usage record remains the authored
  authority; concrete catalog rows carry canonical calculation identity; graph, catalog, wrappers,
  aggregator, expected IDs, results, and TEAx joins share one `NodeId.sort_key()`-derived order.
  Missing, duplicate, extra, malformed, or reordered joins refuse rather than hide an occurrence
  (`design.md:248-277,435-449`).
- **SC-4 — Cause-based diagnostics and dispositions: verified in design.** Valid zero occurrence,
  malformed owner, invalid formal mapping, partial expansion, `ADMIT`, `BLOCK`, plain,
  requirement-side, and nonnumerical cases have distinct dispositions and named failures. A
  structural failure cannot be recast as `owner_has_no_occurrences` or a plain exclusion
  (`design.md:227-246`; `implementation-item.md:133-161`).
- **SC-5 — Follow-on backlog item: verified.** The item gives exact codegen and TEAx file scope,
  existing-versus-new tests and fixtures, Item 8 ownership and start gate, full dependency SHAs,
  producer-first pin order, a 7–9 day estimate, phased exits, and customer-shaped public acceptance
  tests (`implementation-item.md:43-71,184-323,339-404`).
- **SC-6 — Independent review: verified.** Round 3 resolves Item 8's independent ownership and the
  expected-ID carrier. Its final verdict is **Approve**, with no remaining owner/`[HARD]`
  contradiction or ownership ambiguity (`design-review.md:521-565`).

#### Tagged child-spec requirements

Every tagged requirement was traced into the revised design and follow-on item:

- **Eligibility, polarity, and atomic expansion** map to the separate inline/definition-typed paths,
  profile dispositions, once-only polarity, and all-or-nothing local batches
  (`spec.md:92-113`; `design.md:163-186,212-246`).
- **Exact attachment and bidirectional identity** map to the one-level qualified `NodeId`, canonical
  codec, sole total order, exact owner-derived match set, and usage-to-result-to-calculation joins
  (`spec.md:115-138`; `design.md:69-124,227-229,248-277`).
- **Explicit, producer-backed, defaulted, and defaultless sources** map to one centralized
  `CalculationInputRef` dereference law and public fixtures that assert shared source identity and
  generated field counts (`spec.md:140-170`; `design.md:126-186,393-412`).
- **Cause-based disposition and inapplicability rules** map to the diagnostic table and pre-output
  refusal matrix (`spec.md:172-196`; `design.md:231-246,400-410`).
- **Snapshot, version, projection, catalog, receipt, fingerprint, and sealing rules** map to graph
  v4, envelope v6, projector v2, catalog 4.0.0, runtime 2.0.0, exact refusal, and the separately
  owned recapture sequence (`spec.md:198-237`; `design.md:279-294,414-433`).
- **Usage-level coverage and occurrence-complete results** map to the single ordered gate sequence,
  unchanged Item 3 report contract, worst-state preservation, rendered expected-ID receipt, and
  fail-closed TEAx join (`spec.md:239-263`; `design.md:248-277`).

The eleven requirements previously mislabeled `[NEED]` now appear as source-qualified
`[INFERRED: ...]` at `spec.md:132,150,157,168,181,212,215,222,247,254,257`. A direct search finds
zero `[NEED]` tags. Their requirement clauses are unchanged. The correction removes the authority
upgrade without weakening the contract.

The three remaining `[HARD]` requirements are supported by current interface facts: defaultless
unbound formals project as required public inputs; changing the graph identity requires a graph
schema bump; and the current catalog lacks exact calculation-node identity
(`spec.md:160-163,218-230`). The design obeys all three.

The eleven checkboxes at `spec.md:44-88` describe the future production capability. They are not
Item 6 design-delivery completion boxes and remain unchecked.

### Design conformance

The delivery follows the one-authority architecture and the review-approved decisions:

- attachment completes inside elaboration while exact owner/formal indexes coexist;
- qualified graph identity includes the full calculation occurrence;
- one dereference law feeds validation, cycles, selection, topology, projection, and decode;
- inline and definition-typed formals use distinct exact resolution paths;
- graph/catalog/result ordering comes from one total-order oracle and one structured receipt;
- Item 8 retains independent unit-lane certification and conditional v3 recapture ownership;
- a later, separately authorized Item 6 owns formal provenance and graph-v4 recapture;
- report and evidence schemas remain Item 3's contract.

No silent deviation was found between `design.md` and `implementation-item.md`. The dependency
commits exist: codegen evidence baseline `cc14cf07630ed06c7f5cd16bff14cc055709138d`, agentic-mbse
`0a529426f7dfb163a8e03e8a5d3a0cb394d217cf`, and TEAx
`5b70ae9231949476139b157ea47b240bdb855641`. The intentionally unavailable Item 8-containing
codegen start SHA is an explicit future start gate, not a missing Item 6 deliverable.

The lower-authority profile-`BLOCK` denominator wording remains visibly parked. The design pins the
existing build halt and creates no fictional post-halt report (`design.md:481-487`). This is not an
unresolved owner/`[HARD]` contradiction and does not block this design certification.

### Code integrity

No production Item 6 code exists to certify, as required. Read-only searches confirm the proposed
`CalculationInputRef`, qualified `NodeId`, three `SI_CONSTRAINT_CALC_*` diagnostics, graph v4,
projector v2, catalog 4.0.0, and structured expected-ID carrier have not landed. Current behavior
still reports calc-definition owners as `owner_kind_unattachable`, which is the capability gap this
design hands off.

The scratch probe is focused and failure-honest. It uses exact IDs for every decision, asserts
unexpected edges and duplicate formal roots, and contains no broad exception, silent fallback,
rendered-name lookup, or production mutation (`probes/probe_calcdef_attachment.py:36-236`). Python
compile and ruff both pass. No abstraction-quality, fallback, or product-drift smell was found.

---

## Certification

Certified the Item 6 design/planning delivery and marked only its six authoritative epic success
criteria plus its item heading/status. The future implementation boxes in `spec.md` remain open.

Checks performed:

- licensed probe reproduction: PASS, exact scenario counts `0/1/2`;
- scratch probe `py_compile`: PASS;
- scratch probe ruff: PASS;
- independent audit product lens: `CLEAR`; full ledger and epic gate scanned;
- declared codegen and TEAx path census: all existing paths present; absent paths are exactly the
  intentionally new tests/fixtures;
- dependency commit existence: all three full SHAs verified;
- local Markdown links: 5 checked, 0 broken;
- provenance cure: 11 source-qualified `[INFERRED]`, 0 `[NEED]`;
- `git diff --check`: PASS;
- read-only status/diff scope: Item 5 fixture/project dirt, `CURRENT_WORK.md`, and temporary review
  output were excluded and left unchanged by this audit.

**Not checked:** The future production implementation, Item 8 landing, graph-v4 recapture, public
live/in-place/relocated acceptance matrix, full codegen or TEAx suites, and publication pins. Those
claims belong to the separately authorized follow-on implementation and its own audit. No close,
archive, commit, push, or `pre_pr` action was performed.
