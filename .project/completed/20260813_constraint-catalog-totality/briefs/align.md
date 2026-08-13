# Align record — CONSTRAINT-SEMANTICS Item 2 (orchestrated run, 2026-08-12)

**Owner instruction at launch:** run `/_my_orchestrate` on
`.project/backlog/epic_constraint_semantics_contract.md` Item 2, "no need for check-ins."
The Align checkpoint is therefore recorded here rather than held for a reply, and the run
proceeds autonomously. Reserved-gate handling below is the orchestrator's reading of the
epic's recorded decisions, not new owner input.

## Reading of the work item

Item 2 (Canonical Usage Domain and Catalog Totality) makes the instance-graph/embedded-catalog
authority — the same one used by live and snapshot generation — own the **complete authored
constraint-usage domain before occurrence expansion**, so the 56-of-65 CATF usages that today
vanish pre-catalog become visible carriers. One disposition per usage (executable / excluded
with reason / non-reaching with reason), severity by cause, an explicit vacuous-inapplicability
mechanism, a non-circular generation-time completeness gate, codec/snapshot/sealing
carry-through, and re-graded REQ-EXT-09 / REQ-CL-04. Report/TEAx changes are Item 3's;
calc-def gate execution is Item 6's design.

Intent behind it (epic + umbrella spec): a design search must be able to trust generated
feasibility evidence — that starts with the inventory being total and un-fakeable. The gate
must compare dispositions against a domain recorded *before* expansion, never two projections
of the same truncated set (spec-review L3-2).

## Reserved gates

- **None reserved for this item.** The owner checkpoint in this epic (all-65 disposition
  table + tolerances) belongs to Item 5 and is not consumed here.
- The **vacuous-inapplicability mechanism** (model annotation vs reviewed catalog-level
  acceptance) is explicitly deferred to *this item's design* by the umbrella spec (L2-2) —
  an execution-tier decision to make and record, not a gate to hold.
- The **snapshot-schema decision** is Item 2's per the epic's evidence-invalidation register:
  if the canonical-domain representation changes the schema, this item owns one reviewed
  final-schema 37-fixture recapture.

## Provenance and conflicts noted at orient

- Behavioral requirements are `[INHERITED: constraint-semantics-contract/spec.md]`; the
  six-item slicing is `[AGENT] (ratified by owner, 2026-08-12)`. Stage briefs mark which
  statements are inherited authority vs orchestrator inference.
- The parked D-2 vs D-4/SRC-01 premise conflict (umbrella spec, lens spec-F6) stays parked;
  nothing in Item 2 resolves it.
- No `[HARD]` in scope smells inherited-but-unreal: BLOCK-halts-generation is verified
  shipped behavior; the frozen-twin byte pins are ratified.

## Run shape

Pipeline for a single clear code item: `spec` → `spec_review` → `design` → `design_review` →
`plan` → `implement` → `audit`. Close and pre_pr stay with the owner. One commit per stage
and decision; briefs committed under `briefs/`.
