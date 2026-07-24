# Spec: TEAx Constraint Evidence Durability (Lifecycle Item 11)

**Status:** Draft
**Owner:** Reid W
**Created:** 2026-07-20
**Complexity:** HIGH
**Branch:** constraint-exec-epic (codegen); TEAx work lands on TEAx `07eb0ac`+
**Register:** epic rows 13–15; contract rows 41, 45, 46, 46a, 51 (+ 49/52 as guardrails)

---

## Problem

TEAx turns a generated package's constraint outputs into durable study evidence. Three things in
that path are unsound today, and all three are grounded in the code at TEAx `07eb0ac`.

1. **The report read is unconditional, so a constraint-free package dies.** Both evaluator routes
   do a bare `result.outputs["constraint_report"]`:
   - prepared/in-memory: `evaluation/evaluator.py:132` (`REPORT_CHANNEL` at `:27`)
   - file-backed/persisting: `evaluation/evaluator.py:203`

   A package with no constraints produces no `constraint_report` channel, so this raises
   `KeyError: 'constraint_report'`. Codegen is free to omit constraint-only modules/catalog for
   byte-stable constraint-free generation (contract 46a), so a constraint-free package is *valid
   input* — and TEAx crashes on it instead of returning empty evidence.

2. **Authoritative evidence is mutable.** `ModelEvidence` (`evaluation/evidence.py:45`) is a frozen
   `StrictBaseModel`, but frozen only blocks top-level field reassignment. Underneath:
   - `report: Any` (`evidence.py:58`) holds the **live generated report object**, attached unchanged
     by `project(...)` (`evaluation/projection.py:42`). The generated report types are plain
     `pydantic.BaseModel`, **not frozen** — in the f1 fixture, `ConstraintEvaluation`
     (`.../f1_arithmetic/.../schemas/constraint_types.py:13`) exposes mutable `status`
     (`:18`) and `margin` (`:19`), and `ConstraintReport` (`:23`) is likewise unfrozen.
   - `responses` and `outputs` are plain dicts built in `projection.py:28–36`; their items are
     mutable even though the model is frozen.

   So downstream policy/study code can reach in and change status, margin, observations, or the
   headline of evidence that is supposed to be authoritative. Contract row 41 names this exact hole
   ("Current nested models violate it"). Today only an *ordering accident* protects the persisted
   copy: the runner serializes evidence to JSON (`study/runner.py:134`, `encode_evidence`) **before**
   it calls `policy.assess(...)` (`:136`), so a mutating policy cannot corrupt the on-disk artifact.
   That protection is incidental, not designed, and it does not protect the in-memory evidence the
   policy itself reads.

3. **The expected failure phase is not pinned, and one phase is dead.** `EvaluationPhase.OUTPUT_WRITE`
   is defined (`evaluation/failure.py:23`) but never emitted: `_normalize_run_failure`
   (`evaluator.py:56–66`) always stamps `MODULE_EXECUTION`, on **both** the in-memory and the
   file-backed (persisting) route (`evaluator.py:131`, `:202`). Item 6's F1 evidence already recorded
   `OUTPUT_WRITE` as defined-never-emitted and left it for Item 11. Separately, the arithmetic-shape
   fixtures assert *a* failure but do not pin *which phase* each shape must fail in, so phase truth
   rests on evaluator agreement rather than a fixed expectation.

Two adjacent surfaces are healthy and are inventoried so the work does not disturb them: the
persistence/harvest path (`study/evidence_io.py`, `study/store.py`, `study/query.py`) and the
`not_assessed` vocabulary (`evaluation/evidence.py:16`, `study/policy.py:36`). The gaps there are
*coverage*, not *defect* — see Success Criteria.

## Success Criteria

- [x] A **constraint-free** generated package (no `constraint_report` channel, valid EntryPoint
      pipeline) evaluates to **empty constraint evidence** — no `KeyError` — through **both** the
      prepared and the file-backed route. This is coordinate one (RED today).
- [x] An **excluded-only** package (constraints present but all excluded → zero eligible) produces
      the exact `not_assessed` headline surface, distinct from the constraint-free empty-evidence
      surface. Zero-usage (constraint-free) and zero-eligible (excluded-only) are different axes and
      each has its own coordinate.
- [x] A nested mutation attempt on evidence — `evidence.report.results[i].status = ...`,
      `evidence.report.results[i].margin = ...`, `evidence.responses[...] = ...` — **cannot** change
      the authoritative in-memory evidence or the persisted artifact. Enforced by deep-freeze or
      defensive isolation of the envelope, generated report, nested results, observations, status,
      and margin *before* policy can access them.
- [x] The exact completed report JSON persists and harvests for **satisfied**, **violated**,
      **indeterminate**, and **assessment_failed**, each carrying package identity
      (`executable_fingerprint`), and remains compatibility-bound (fingerprint-scoped, never merged
      across fingerprints).
- [x] Phase / module / cause / report parity between the prepared and file-backed routes uses
      **fixture-pinned expected phases** per arithmetic shape — not phases established by the two
      evaluators merely agreeing.
- [x] `OUTPUT_WRITE` is either **emitted honestly** by the file-backed persisting route on a real
      output-write failure, or the phase is **collapsed** (removed) so no defined-never-emitted phase
      survives. One or the other, decided against a fixture, not left dangling.
- [x] The duplicate/generic report adapters and the incidental encode-before-policy protection
      (`runner.py:134` ordering) are removed once the explicit durability mechanism owns immutability;
      exactly one durability mechanism remains and one unconditional-read path is gone.

## Known Requirements

- **[INHERITED]** Absence of a constraint report is empty constraint evidence, not a `KeyError`,
  through both evaluator routes; codegen stays free to omit constraint-only modules for byte-stable
  constraint-free generation. Source: contract 46a
  (`.project/concepts/constraint-execution-authoritative-lifecycle-contract.md:255`).
- **[INHERITED]** A completed constraint module returns authoritative evidence; downstream code
  cannot change the envelope, generated report, nested results, observations, status, or margin —
  enforced by deep freeze or defensive isolation. Source: contract 41 (`:242`).
- **[INHERITED]** Prepared and file-backed evaluators normalize a module failure identically, name
  the exact phase/module, preserve the original exception as cause, and return equal report content
  for equivalent completed executions. Source: contract 45 (`:250`).
- **[INHERITED]** The public file-backed route persists and harvests the exact report plus package
  identity with no consumer schema adapter. Source: contract 46 (`:253`).
- **[INHERITED]** `assessment_failed` is a distinct evidence-preserving study state; a policy failure
  does not erase successful model evidence or masquerade as model execution failure. Source: contract
  51 (`:272`); already realized at `runner.py:137–147` and must be preserved.
- **[HARD]** Both report reads (`evaluator.py:132`, `:203`) and the projection reads of
  `report.headline` / `report.results` (`projection.py:28–30`) must tolerate an absent report. The
  generated package genuinely omits the channel — this is forced by codegen output, not a choice.
- **[HARD]** The generated report and its nested results are plain unfrozen `pydantic.BaseModel`
  (`constraint_types.py:13,23`). TEAx cannot make codegen freeze them, so the durability mechanism
  must live on the TEAx side at the projection boundary (`projection.py:42`), by deep-freeze or by
  copying into a TEAx-owned immutable structure.
- **[NEED]** Excluded-only zero-eligible packages evaluate to the exact `not_assessed` surface while
  zero-usage packages yield empty evidence — the two are proven as distinct coordinates.
- **[NEED]** Expected failure phase is pinned per arithmetic shape by the fixture, and `OUTPUT_WRITE`
  is settled (emitted honestly or collapsed) rather than left defined-never-emitted.
- **[INFERRED]** The four completed-status coordinates persist/harvest through the existing store
  path (`store.commit_case` → `evidence_io.encode_evidence`/`decode_evidence` → `query.StudyQuery`)
  without a new adapter — the healthy path is extended with coverage, not replaced.

### Fixture inventory (exists vs. author)

Generated-package fixtures are epic-sanctioned and come from codegen. Grounded against TEAx
`07eb0ac`:

- **Constraint-free (valid EntryPoint):** **AUTHOR.** No existing fixture is constraint-free — all
  three package fixtures (`sealed_package`, `zero_channel`, `f1_arithmetic`) carry a
  `constraint_report` channel. `zero_channel` is zero-*entry*-channel but constraint-*bearing* (Item
  9 firewall, `constraint-lifecycle-multi-entry/audit.md:56`). Item 9's zero-entry template fix means
  a constraint-free variant can now emit a valid EntryPoint pipeline — extend that work.
- **Excluded-only (zero-eligible → `not_assessed`):** **AUTHOR.** No fixture exercises the
  `not_assessed` headline end-to-end today.
- **Four-status arithmetic shapes:** **MOSTLY EXISTS, needs phase-pinning + assessment_failed.**
  `f1_arithmetic` already carries cases for satisfied (`safe_satisfied.json`), violated
  (`safe_violated.json`), indeterminate (`nonfinite_indeterminate.json`), and arithmetic-failure
  shapes (`division_by_zero`, `exponent_overflow`, `nested_division`, `zero_negative_power`). What is
  missing is a *fixture-pinned expected phase* per shape and a coordinate that drives
  `assessment_failed` (today only reachable via the injected `reject_candidate_ids` policy seam,
  `study/policy.py:59–66`, not a fixture).

### Deletion inventory (file:line, to be confirmed at design)

Candidates for removal once the explicit durability mechanism lands. Each is *identified* here;
whether each is deleted, collapsed, or kept is a design call (see Open Questions):

- **One of the two unconditional report reads / the read pattern itself** — `evaluator.py:132`,
  `evaluator.py:203`. These become a single report-absence-tolerant read (one mechanism, not two
  copies of the same bare `[REPORT_CHANNEL]`).
- **The incidental encode-before-policy ordering** — `runner.py:134` sits before `:136` purely to
  protect the persisted copy from a mutating policy. Once deep-freeze/isolation owns immutability,
  that ordering is no longer load-bearing and the coupling should be removed.
- **`EvaluationPhase.OUTPUT_WRITE`** — `failure.py:23`, if the decision is to collapse rather than
  emit. Also the runner's `MODULE_EXECUTION`/`OUTPUT_WRITE` comment (`runner.py:119`) and
  `_normalize_run_failure`'s fixed `MODULE_EXECUTION` (`evaluator.py:62`).
- **Any generic/duplicate report adapter** — none named `*adapter*` survives in `simkit/` today
  (only `io/readers.py` "Input adapters", unrelated). The "generic/duplicate report adapter" the
  epic targets is the duplicated bare-read + projection duck-typing pair, not a class literally named
  Adapter. Confirm at design that no consumer-side report reshaper is being introduced.

## Non-Goals

- Reinterpreting verdicts as study policy (firewall; contract 49, out of scope).
- Recreating a consumer-specific catalog or report schema (D-3 settled; contract 48). The harvest
  reads codegen's embedded catalog (`study/query.py`) — no standalone schema is reintroduced.
- Item 12's legacy `grandfathered_off` / `tracking_key` closure (contract 53, row 16) — separate
  item.
- Changing codegen's report emission or forcing codegen to freeze its report models. The fix is
  TEAx-side.

## Open Questions / Deferred to design

- **Deep-freeze vs. defensive isolation (mechanism).** Contract 41 allows either. Copy-into-a-TEAx-
  owned-immutable-structure vs. recursively freezing the live pydantic report in place are both
  admissible; the choice (and where it sits relative to `projection.py:42`) is design's.
- **Emit vs. collapse `OUTPUT_WRITE`.** The file-backed route genuinely persists
  (`persist_outputs=True`, `evaluator.py:199`), so a real output-write failure *is* reachable there
  and could be stamped `OUTPUT_WRITE` honestly — but if no fixture can force a write failure without
  contrivance, collapsing the phase is the honest alternative. Decide against a fixture at design.
- **Empty-evidence shape for constraint-free.** What `ModelEvidence` looks like with no report:
  empty `responses`, empty/real `outputs`, and `report=None` vs. a sentinel empty report. The
  headline vocabulary has no "empty" member today (`evidence.py:16`); design picks the representation
  and how `encode_evidence`/`query` render it.
- **Where report-absence is detected** — at the evaluator read, in `project(...)`, or both. Affects
  how many of the two read sites change.

## Provenance correction (surfaced — capture-fidelity Law 4)

The spec brief states: *"Opening RED is already reproduced: Item 9's constraint-free probe hit
`KeyError: 'constraint_report'` in `evaluate()` (recorded in Item 9's codegen-gap-zero-entry finding
and evidence) — invariant 46a live."*

**This premise is not supported by Item 9's own record.** Item 9's evidence explicitly firewalls
constraint-free report out of its scope:

- `constraint-lifecycle-multi-entry/evidence.md:138` — *"Item 9 does not touch the
  `FileBackedEvaluator` route (Item 11) or constraint-free report."*
- `constraint-lifecycle-multi-entry/audit.md:56–57` — *"zero" = zero entry channels, not
  constraint-free report.*
- `codegen-gap-zero-entry.md` records a **different** RED — the zero-*entry*-channel EntryPoint
  rejection (`Pipeline must declare exactly one EntryPoint module`), fixed in codegen — **not** a
  `constraint_report` KeyError.

So **46a is not yet reproduced end-to-end.** It is grounded here by code inspection (the unconditional
reads at `evaluator.py:132` and `:203` provably `KeyError` on a report-less outputs mapping), and no
constraint-free fixture exists to run it against. Reproducing coordinate one — authoring the
constraint-free fixture and driving both routes to a real `KeyError`, then to green — is Item 11's
**first implementation step (RED-first)**, not an inherited fact. Recorded as a correction, not an
instruction; dependent claims (that RED is "done") are parked until the fixture exists.

---

## Related Artifacts

- **Epic:** `.project/backlog/epic_constraint_execution_lifecycle_remediation.md` (Item 11, rows 13–15)
- **Required Reading:**
  - `.project/concepts/constraint-execution-authoritative-lifecycle-contract.md` (contract rows
    41, 45, 46, 46a, 51 — the runtime/studies invariants)
  - `.project/active/constraint-lifecycle-evidence-durability/briefs/spec.md` (stage brief)
  - `.project/active/constraint-lifecycle-multi-entry/` (Item 9: `evidence.md`, `audit.md`,
    `codegen-gap-zero-entry.md` — the zero-entry template fix and the constraint-free firewall)
- **Ground-truth chain:** codegen `b987869`, agentic-mbse `4c18d61`, teax `07eb0ac`,
  fusion-tea `2422e715`, stellarator `c4dcdf27`+
- **Design:** `.project/active/constraint-lifecycle-evidence-durability/design.md` (to be created)

---

**Next Steps:** After approval, proceed to `/_my_design`. First design decisions: the immutability
mechanism, the empty-evidence representation, and the `OUTPUT_WRITE` emit-vs-collapse call — each
tied to a fixture. RED-first: author the constraint-free fixture and reproduce the 46a `KeyError`
before any fix.
