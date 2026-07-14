# Spec Review: Constraint Module, Kleene Compiler, Aggregator, and Catalog Generation

**Spec:** `.project/active/constraint-generation/spec.md`
**Contract:** `claude-pack/commands/_my_spec.md`
**Review File:** `.project/active/constraint-generation/spec-review.md`
**Date:** 2026-07-12
**Reviewer note:** Orchestrated CONSTRAINT-EXEC run, Item 7. Fresh session; did not author the spec. Verified against upstream code and the S2/S4 spikes, not the spec's own word.

---

## Reality Check

**Sound.** The spec is pointed at the right work item, the Problem section is accurate, and the core requirements are directionally correct and honestly tagged. I checked the hard claims against code and spikes and most hold:

- Kleene requirements match S2's verified truth table (leaf-unknown on non-finite, the two rescue rules + `not unknown = unknown`, negated-polarity status, margin-sign flip, boundary-zero-no-sign). No overstatement — the spec makes no n-ary parity claim that S2 didn't earn.
- The headline/status literals match `s4_lib.py:626,636` byte-for-byte (`satisfied|violated|indeterminate`; `violation|indeterminate|all_satisfied|not_assessed`).
- Every catalog **source-record** field the spec inherits exists on `ConstraintUsageFact` (`.project/reference/agentic-mbse-landed/constraint_facts.py:124`): identity, `source.form`, `membership_kind`, `is_negated`, `scope`, `location`, and the referenced `constraint_definition`.
- `ConcreteConstraintInput.bound_channel` (the recorded producer binding) exists (`resolution/models.py:267`); the `parse_expression`/`serialize_expression` round-trip the compiler depends on is real (`expression_ir.py:133,220`).
- The Item-8 handoff sequencing (live/snapshot byte-identity for a constraint-bearing fixture can't be met until Item 8 makes facts load-bearing) is surfaced honestly rather than asserted as met — exactly the right call under capture-fidelity Law 4.

So this is a **Revise**, not a Rework. The defects below are concrete gaps and traceability slips, not a mis-framed work item. The load-bearing one is real: a whole success-criterion case (modeled-default formals) has no requirement and no mechanism behind it.

---

## Audit

### Lens 1 — Faithfulness

**L1-1 · Direct claim (must-fix):** Modeled-default formals are a success-criterion case with **no requirement, no mechanism, and no open question** behind them. Success Criteria (spec:45–48) lists "modeled-default formals" among the cases that must "execute correctly," but nothing in Known Requirements or Open Questions says *how a default becomes a runtime value*. Item 5 emits these as `ConcreteConstraintInput(resolution=MODELED_DEFAULT, default_ir=<serialized IR>)` (`resolution/models.py:247,269`), and S4 explicitly **did not exercise them** — "the probe's lowering refuses them" (S4 findings, "Not exercised here"). So there is zero proven shape. The design engineer is left to guess between materially different surfaces:
  - a minted **entry point** (like `DESIGN_ATTRIBUTE`) — appears in a parameter group and the JSON input template, user-overridable; or
  - a **compiled constant** baked into the module — fixed, invisible to inputs.

  These produce different generated packages and different parameter-group JSON. The spec must pin the runtime realization of a modeled default (or file it as an explicit Open Question with the two candidates named), and say whether `default_ir` flows through the same Kleene compile path as `predicate_ir`. As written, the "modeled-default formals execute correctly" criterion is not testable — there is no defined correct behavior to test against.

**L1-2 · Question to the user (should-fix):** The concrete-entry catalog requirement inherits **"response metadata"** (spec:160) but there is no such field on Item 5's `ConcreteConstraint` (`resolution/models.py:272–322` — no response/bound field), and the spec's [INFERRED] assembly note (spec:165) says the concrete entries come *from* those `ConcreteConstraint` records. Two problems:
  - **Where does it come from?** The concept means the response/bound decomposition of a *simple inequality* ("response and bound for a simple inequality," concept:104). That is derivable from `predicate_ir` structure at generation time, but the spec never says Item 7 derives it — it implies Item 5 already carries it, which it doesn't. Either name the derivation or drop the field from the concrete-entry list.
  - **Dropped force.** The concept marks it *"optional* response metadata" (concept:94,102). The spec lists it flat alongside required fields, hardening an optional into a required entry (capture-fidelity Law 2). Restore the "optional" qualifier or state the force.

  Same soft spot, lower stakes: the source record inherits **"display expression"** (spec:154) which is also not a stored fact field — it's renderable from the predicate IR. Fine to keep, but the spec should say it's rendered, not stored.

**L1-3 · Direct claim (minor):** The seam count is wrong and internally inconsistent with its own sources. The spec says "the **five** generation seams" (spec:24, 35, 240) and enumerates five buckets at spec:208 (module-wrapper, pipeline-yaml, registry, test-gen, stencil/backlog-report). But:
  - S4 and the Item 6 fail-loud test both say **"four calc-shaped generation seams"** (`tests/conformance/test_module_kind_faildloud.py:3`).
  - The actual fail-loud surface is **six** distinct `seam_name` strings raising `unrenderable_module_kind_error` (registry, module-wrapper, pipeline-yaml, stencil, backlog-report, test-gen) **plus** `_check_duplicate_output_paths` — seven test functions in that file.

  The count itself is cosmetic, but one omission is not: the spec's enumeration drops the **python-path / duplicate-output-path** seam that S4 flagged by name ("`_get_python_path` / `_check_duplicate_output_paths` assume `calc_def_qualified_name`," S4 "Seam findings"). A design working only from spec:208's five buckets could miss it. Fix: either point at `test_module_kind_faildloud.py` as the authoritative seam list (Item 7 inverts all of it), or add the path/duplicate seam to the enumeration. The "five" prose should be reconciled with the cited "four."

### Lens 2 — Problem & Approach

**L2-1 · If-then tradeoff (note, not a blocker):** The spec bundles four subsystems — Kleene compiler, constraint modules, aggregator, catalog — into one item. That is a lot for one spec, and normally I'd push to split. Here it's defensible **because** S4 proved them as one vertical slice end-to-end, and splitting the compiler from the module from the aggregator would break the only thing that makes the criteria testable (a modeled assertion that actually runs). Keep it bundled. Flagging only so the size is a conscious choice, not an accident.

**L2-2 · Direct claim (well-handled — recording, not flagging):** The `[NEED — settled, do not relitigate]` module-identity item (spec:99) is correctly graded. It traces to an `[OWNER]` gate (`identity-gate-evidence.md`: "GATE RESOLVED [OWNER]", Reid 2026-07-12), so it is settled-eligible under capture-fidelity, and it's grounded in a real runtime fact (a YAML instance cannot learn its own key — S4). This is the one place a spec most often invents-and-freezes a solution; here it didn't. No action.

### Lens 3 — Pipeline Risk

**L3-1 · Direct claim (must-fix):** The serialization-equality same-IR arm and the "compiles once at the definition level" [HARD] (spec:74–79) have **no success criterion or test that would catch a violation.** The wiring brief flagged that the compiler-side assertion must be *serialization-equality* — identical serialized `predicate_ir` strings compile identically — and the spec correctly states the property. But it's stated as prose, not as a checked obligation. Nothing in Success Criteria exercises it. Two consequences design needs pinned:
  - Add a criterion/test: two concrete constraints with byte-equal `predicate_ir` produce identical compiled predicate code (this is what makes "compile once" well-defined when the input is per-concrete `ConcreteConstraint.predicate_ir` records, not a def object).
  - Resolve the latent tension with L2-2's decision: with **class-per-concrete-assertion**, is the def-level predicate a single shared function that each class calls, or re-emitted per class from the identical IR? Both are valid *given* serialization-equality — but the spec should say the relationship exists and hand design the choice, because "compiles once at the definition level" and "one class per `constraint_id`" read as if in tension until you name the same-IR arm as the bridge.

**L3-2 · Rewrite request (should-fix):** The narrowed-exit success criterion (spec:49) is not specified to be *falsifying*. It reads "narrows the YAML exit and confirms the report channel is still an exit ancestor." The whole point (S4 carry-forward (1)) is that under the S4 mechanism — the exit captures *every* surviving output, so the report rides along incidentally — narrowing the exit would **drop** the report. A test that narrows the exit but still incidentally captures the report is vacuous: it passes without proving non-incidental ancestry. Sharpen the criterion so the narrowing must exclude the report channel from any capture-everything path — i.e., the test must **fail** if ancestry is only incidental. Design still picks the mechanism (Open Questions), but the spec should state the falsification condition so design doesn't build a green-but-empty test.

**L3-3 · Rewrite request (minor):** The five S4-unexercised cases are collapsed into a single bundled success criterion (spec:45–48). For four of them the backing requirement lives elsewhere and this is fine — zero-assertion aggregator has its own [HARD] (spec:129), the indeterminate point is covered by the Kleene [HARD] (spec:66), negated status by the polarity [NEED] (spec:87), multi-instance by the aggregator's "one required field per concrete assertion" (spec:129). The exception is modeled-default (L1-1). No named test *fixtures* are given for any of the five, which is acceptable for a spec (design picks fixtures) **as long as** each criterion is independently testable — which loops back to L1-1 being the only one that isn't.

### Lens 4 — Hygiene

No material findings. Tags are consistent, sources are cited on the [INHERITED] items, and the Non-Goals are decision-records (no prohibition-mode phrasing).

### Lens 5 — Reader Comprehension

No blocking findings. The module-identity paragraph (spec:99–109) is dense — decision, rejection, benchmark, and far-future-revisit in one block — but a tired engineer can still extract the decision on one read because it leads with "Module identity is class-per-concrete-assertion." Leave it.

---

## Engagement Summary

**Overall take:** Fundamentally sound and unusually honest about its own limits (the Item-8 handoff gate, the owner-graded settled tag). But it has one load-bearing hole — a success-criterion case with no requirement behind it — plus two obligations that are stated as prose and never turned into anything a test would catch. Fix those three and I'd trust it as the design contract.

**Must-fix (with why):**

1. **[L1-1]** Specify how a **modeled-default formal** becomes a runtime value — entry point vs compiled constant — and whether `default_ir` uses the Kleene compile path. *Why:* it's a success-criterion case with zero requirement, zero mechanism, and zero S4 evidence; the criterion isn't testable as written, and the choice changes the generated package surface.
2. **[L3-1]** Turn the **serialization-equality / compile-once** [HARD] into a checked criterion, and name the bridge between "compiles once at the definition level" and "one class per `constraint_id`." *Why:* it's the property that makes "compile once" well-defined given per-concrete `predicate_ir` inputs, and nothing today would catch a violation.
3. **[L3-2]** Make the **narrowed-exit test** falsifying — the narrowing must exclude the report from capture-everything so the test fails under incidental-only ancestry. *Why:* as worded, a vacuous test passes without proving the [HARD] guarantee.

**Should-fix:**

4. **[L1-2]** Resolve **"response metadata"**: it's not a field on Item 5's `ConcreteConstraint`, so say Item 7 derives it from the predicate structure (or drop it), and restore the concept's "optional" force. Same for "display expression" being rendered, not stored.

**Nice-to-have:**

5. **[L1-3]** Reconcile the **"five seams"** count with the cited "four," and make sure the python-path/duplicate-output-path seam S4 flagged is in scope (point at `test_module_kind_faildloud.py` as the authoritative list).
6. **[L2-1]** Confirm the four-subsystem bundle is a conscious sizing choice (it's defensible as the vertical slice).

---

## Resolutions

_(To be filled in as the owner/spec-agent resolves each finding. Keyed by ID.)_

---

**Verdict:** Revise (orchestration vocabulary: **Approved-with-must-fixes** — items L1-1, L3-1, L3-2 are the must-fix set; L1-2 should-fix; L1-3/L2-1 nice-to-have).
**Next Steps:** Record resolutions above, then re-run `/_my_spec` (or return to the spec-agent session) pointed at this review to incorporate. The reviewer does not edit the spec.
