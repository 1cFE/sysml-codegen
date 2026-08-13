# Product-lens ledger — constraint-coverage-policy (CONSTRAINT-SEMANTICS Item 3)

Append-only. Verdict blocks land verbatim; dispositions are recorded in the spec/design they amend.

---

## spec — 2026-08-12 — rev ec1ae2a (+ untracked `.project/active/constraint-coverage-policy/spec.md`)
Epic: CONSTRAINT-SEMANTICS, Item 3 (Coverage Report and TEAx Policy)

**Runner note:** `/home/reid/.claude/scripts/product-lens.md` and its pack source are outside this session's sandbox and could not be read. The §3 ledger format was recovered from the sibling ledgers `.project/active/constraint-semantics-contract/product-lens.md` and `.project/active/constraint-semantics-contract-amendments/product-lens.md` and followed. `/home/reid/1cfe/teax` is also unreadable here, so no TEAx-side claim in the WORK was verified against that repository.

**Point** (re-derived from SOURCES; the WORK was opened only after the sources were read):

1. Item 1 already fixed what every headline state *means*; Item 3 owns spellings, schema, and seam code only, and may not re-decide a meaning. [source: contract "Headline states and coverage truth" preamble, ADR-009 **Scope**; grade: agent/ratified]
2. No report or study label may claim more coverage than was assessed. Full satisfaction is a coverage claim over applicable **asserted** gates; inventory totality and feasibility coverage stay two separate totals. [source: invariants 32, 33, 61; LC-E10/E11/E12/E13; refinements L2-1/L2-2; grade: agent/ratified]
3. Coverage truth has exactly one authority — the embedded catalog — derived in one direction, never a second inventory, and TEAx consumes it with no adapter and no re-derivation of constraint context. [source: invariant 48, 40; LC-G07 (owner-sourced NEED); **D-3 owner-verbatim** "100% Option A. We need to purge this mess."]
4. Every state has a counterpart in both vocabularies across one seam; an unknown or unmapped headline fails closed with a named error, never a `KeyError` and never a fallthrough to satisfied or unconstrained. [source: invariant 46a, contract "Both vocabularies"; umbrella `[HARD]` L1-1]
5. Policy reads evidence, never writes it; partial coverage keeps for boundary, feed-strategy only by explicit auditable per-study opt-in, coverage lands in durable case records either way, and study identity is never silently reassigned across a catalog/report schema move. [source: invariants 41, 49, 50; Q6; grade: agent/ratified]

**Falsifier:** a run in which a constraint-bearing model still emits no report (or reads `unconstrained`/`not_assessed`) while it carries an applicable asserted gate; or coverage counts computed from anything other than the catalog; or a state that exists in one vocabulary with no counterpart; or an existing study store silently rebound across the report/catalog schema move.

### Findings

- **item3-F1 [DO] — the report-required trigger is published for only one of its two branches, and the missing branch is the one Appendix C names twice.** The spec's aggregator requirement reads "A constraint-bearing model with **no applicable asserted gate** still requires the zero-input aggregator and a not-assessed report" (`constraint-coverage-policy/spec.md:126-128`), and Success Criterion 3 pins only the descriptive-only shape (`:71-72`). The other zero-entry shape — applicable asserted gates present, **zero eligible concrete entries** — also produces no evidence inputs and so also needs a zero-input aggregator, but reads *partial coverage*. The contract states it three times: Appendix C "Excluded-only usages" ("a partial-coverage surface when any excluded usage is asserted", `constraint-execution-authoritative-lifecycle-contract.md:792`), Appendix C "Asserted vacuous gate" ("generation does not halt, and the report headline reads partial coverage", `:793`), and LC-E12 amended (`constraint-execution-lifecycle-requirements.md:326-333`). The spec's own `[INFERRED]` supersession of `ships_constraint_machinery` says the replacement "must be the invariant-32 trigger" (`:131-135`) but never states what that trigger *is* — and both candidate readings on the page (Item 2's "≥1 concrete entry" and the spec's "no applicable asserted gate") leave an asserted-vacuous-only model with no aggregator at all. That model is Item 5's post-migration CATF shape: today all 65 usages are bare `constraint`, and 5 of them are `owner_has_no_occurrences` (`constraint-catalog-totality/verification.md:19-28`). — source: invariants 32, 61; Appendix C:792-793; LC-E12 (agent/ratified) — **disposition:** state the report-required trigger once, positively (a report is required whenever the model authors any constraint usage), and add a success criterion pinning asserted-gates-with-zero-eligible-entries → zero-input aggregator → **partial**, distinct from the descriptive-only → not-assessed criterion.

- **item3-F2 [DO] — the inherited "BLOCK stays in the denominator" clause is unreachable under invariant 1, and the spec carries both without noticing.** Known Requirements reproduce the contract's form-not-predicate test verbatim: "an asserted usage whose predicate is `BLOCK`ed or classified `NON_NUMERICAL` stays in the denominator as an unassessed gate" (`spec.md:106-109`). Invariant 1 as amended by Item 1 says "A `BLOCK` on an **asserted** usage halts the model" (`constraint-execution-authoritative-lifecycle-contract.md:130-135`), and Appendix C's "ADMIT + NON_NUMERICAL + BLOCK mix" cell says "one halt before mutation" (`:794`). A halted model generates no package and no report, so the BLOCK half of that requirement can never be exercised; only the `NON_NUMERICAL` half is live. The spec's Non-Goals separately keep "Changing BLOCK-halts-generation semantics" (`:191`), so it holds both sides without reconciling them. An implementing agent reading this page will write a fixture for "asserted + BLOCKed predicate → partial coverage" that cannot be generated. — source: contract invariant 1 (amended) vs "Headline states and coverage truth":439-445 (both agent/ratified) — **disposition:** surface it, do not resolve it (capture-fidelity law 4). Move it into "Surfaced, not resolved" alongside the epic scope-4 note, and scope the live requirement to `NON_NUMERICAL` until Item 1's authority rules on whether the BLOCK clause is dead text or invariant 1 is narrower than written.

- **item3-F3 [DO] — the all-inapplicable edge has two published answers and Item 3 writes the code that picks one.** Appendix C's "Asserted vacuous gate" cell says a usage carrying an explicit inapplicability disposition "drops out of the feasibility denominator and the headline reads **full satisfaction** when every remaining gate passed" (`:793`). State 5 says "the model has constraint usages but **no applicable asserted gate at all**" reads **not assessed** (`:459-460`). A model whose only asserted gates are all dispositioned inapplicable satisfies both: zero remaining gates all vacuously passed, and zero applicable asserted gates. The spec reproduces the inapplicability rule (`spec.md:111-115`) and the state list (`:100-105`) without noticing they cross, and its Open Questions do not list this. Item 3 implements the precedence function, so it will decide by accident. — source: contract Appendix C:793 vs states 5/precedence:459-464; invariant 61 (agent/ratified) — **disposition:** add it to "Surfaced, not resolved" or to Open Questions with the two readings named, so design rules it explicitly rather than in code.

- **item3-F4 [DO] — the migration question stops at generated packages and never reaches the study stores the item is about to change.** Success Criterion 5 requires coverage counts and catalog linkage to persist "in durable case records" on both policy paths (`spec.md:76-78`), and the open question covers "already-generated packages and captured baselines" for the `ConstraintReport` and package-contract version bump (`:207-208`). Neither names existing durable study stores, whose records were written against catalog `2.x` and a report with no coverage block. Invariant 50 requires an explicit transition — a migration proving old and new artifact equivalence, or the old store archived as lineage with a new store begun — and states "Identity is never silently reassigned" (`:301-305`); LC-G07A mirrors it (`constraint-execution-lifecycle-requirements.md:408-410`). With TEAx also re-vendoring `ACCEPTED_CATALOG_SCHEMA_VERSIONS` to `3.0.0` in this item, resume/query across the boundary is exactly the case invariant 50 governs. — source: invariants 48, 50; LC-G07A (agent/ratified) — **disposition:** extend the migration open question to durable study stores and name invariant 50's two permitted routes, so design cannot land a silent rebind.

- **item3-F5 [DO] — invariant 41 is cited for its read-only half and dropped for its enforcement half, over a surface this item is adding.** The study requirement carries "Policy consumes evidence read-only. It cannot mutate status, margin, observations, identity, or catalog linkage" (`spec.md:158-159`). Invariant 41's full text adds the mechanism and a live defect: "enforce this by deep freeze or defensive isolation. **Current nested models violate it**" (`:269-271`). This item adds a nested coverage block (counts plus a reason histogram) to `ConstraintReport` — new nested mutable surface on exactly the models the contract records as already violating the rule. The spec neither carries the enforcement obligation nor declares it out of scope, and Appendix C's "Nested evidence mutation attempt" cell (`:824`) has no counterpart in the success criteria. — source: invariant 41; Appendix C:824 (agent/ratified) — **disposition:** either state that the new coverage block is frozen/isolated to the same standard, or record the pre-existing violation as explicitly out of scope so the new fields are not quietly enrolled in it.

- **item3-F6 [DO, low] — the load-bearing half of invariant 32 is paraphrased away.** The spec cites invariant 32 for the zero-input aggregator but drops its first clause: "the aggregator is structurally retained as an exit ancestor whenever a constraint report is required" (`:232-235`; LC-E10 repeats it, `constraint-execution-lifecycle-requirements.md:305-310`). Retention is what the *zero-input* case actually needs — an aggregator with no inputs is exactly the node ordinary reachability pruning drops, so "generate it" without "retain it as an exit ancestor" is half the obligation. — source: invariant 32; LC-E10 (agent/ratified) — **disposition:** one clause added to the existing requirement; no new section.

**Not findings (checked, clean):**
- No owner-graded statement is contradicted. D-1 (no post-build seam), D-2 (direct design-attribute actuals), and **D-3** (canonical embedded catalog, no consumer materializer) are untouched; the spec's one-direction derivation requirement (`:123-125`) is the correct D-3/invariant-48 posture and repeats no second inventory.
- The `[OWNER-VERBATIM]` design-search quote (`:51-53`) reproduces `rulings-20260812.md:13-15` exactly, at the owner's emphasis, and is carried as the governing obligation rather than paraphrased.
- The owner-directed sequence is graded `[NEED]` (`:180-183`), the correct concept→spec absorb mapping for the rulings' `[OWNER]` grade, and it explicitly forbids reverse-engineering expectations from current behavior — the strongest single line in the spec, and pointed at the right risk.
- Q6's default dispositions are reproduced exactly against the umbrella (`spec.md:151-157` vs `constraint-semantics-contract/spec.md:238-243`), including the auditable-opt-in and the record-regardless clause.
- Invariant 61 / LC-E13 (asserted vacuous gates) are carried even though the epic's Item 3 Required Reading predates them and omits both — the spec caught the gap on its own.
- The epic scope-4 vs LC-E10 divergence is surfaced under law 4, not silently reconciled (`:218-224`), and the second-hand TEAx citations are flagged as needing re-grep before reliance (`:225-230`).
- The Item 1 audit M-1 hand-off (four `all_satisfied` assertions in `tests/execution/`) is carried into Success Criteria as an eighth criterion rather than lost between items.
- The `ships_constraint_machinery` supersession is marked `[INFERRED]`, attributed to the docstring that anticipated it, and required to stay in one place — no second rule, no silent drift.

**Gate: DISPOSED (item3-F1..item3-F6)** — nothing blocks. No owner-grade statement and no Item 1 ruling is contradicted; the spec's provenance discipline is clean throughout. **item3-F1 is the one to fix in the spec text**, because it is a missing obligation rather than an under-specified one: as written, the item can ship with the asserted-but-zero-eligible model still emitting no report, which is the epic's own Current-State defect surviving the item that exists to remove it. F2 and F3 are surfacing obligations (two published rules that cross), and both belong in "Surfaced, not resolved" before design, not in design's judgment. F4 and F5 are contract clauses cited by number but carried by half. The recurring shape across F1, F5, and F6 is the same: an invariant is cited for the clause the spec needed and trimmed of the clause that makes it enforceable — quoting the invariants whole would close all three.

---

### Spec-side disposition record (2026-08-12, same session)

- **item3-F1 → fixed in spec.** The report-required trigger is now stated once and positively ("a
  report is required whenever the model authors any constraint usage at all"), with both zero-input
  branches named and their differing headlines. A new success criterion pins
  asserted-gates-with-zero-eligible-entries → zero-input aggregator → partial coverage, separate from
  the descriptive-only → not-assessed criterion. The `ships_constraint_machinery` supersession now
  points at that stated trigger instead of at an unstated one.
- **item3-F2 → accepted in substance, corrected in detail.** The finding's premise is one step too
  strong: `SI_CONSTRAINT_BLOCKED` is raised inside the scope loop (`elaborate.py:1018-1029`), so an
  asserted `BLOCK`ed usage halts only when it expands to at least one scope. A `BLOCK`ed asserted
  usage that reaches no instance catalogs `non_reaching` and does stay in the denominator — Item 2's
  design says so explicitly. So the clause is live for the non-reaching case and dead for the
  expanded case, which is a reconcilable reading rather than a crossed rule. Recorded that way in the
  requirement itself, with the warning that a fixture for "asserted + BLOCKed + reaches an instance →
  partial" cannot be generated. Not moved to "Surfaced, not resolved", because nothing is left
  unresolved once the two cases are separated.
- **item3-F3 → surfaced, not resolved.** Added to "Surfaced, not resolved" with both readings and
  their sources named, and with the observation that Item 3 writes the precedence function and will
  otherwise pick one by accident. Both readings are agent-grade Item 1 text; this spec does not
  choose.
- **item3-F4 → fixed in spec.** Invariant 50 / LC-G07A now appears as an `[INHERITED]` requirement
  naming its two permitted routes for existing durable study stores, and the schema-migration open
  question explicitly extends to those stores.
- **item3-F5 → fixed in spec.** An `[INFERRED]` requirement states the new nested coverage block is
  frozen or defensively isolated to invariant 41's standard, and that fixing the pre-existing
  nested-model violation elsewhere is out of scope — so the new fields are not quietly enrolled in
  it.
- **item3-F6 → fixed in spec.** Invariant 32's exit-ancestor retention clause is carried as its own
  requirement line beside the zero-input trigger.
