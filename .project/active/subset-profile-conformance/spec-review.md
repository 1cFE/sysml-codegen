# Spec Review: Independent conformance corpus and per-site codes (EXEC-SUBSET-CONTRACT Item 2a)

**Spec:** `.project/active/subset-profile-conformance/spec.md`
**Contract:** `claude-pack/commands/_my_spec.md`
**Review File:** `.project/active/subset-profile-conformance/spec-review.md`
**Date:** 2026-10-18

---

## Reality Check

Sound. The spec is about the right work item. Its Problem section matches the epic's Item 2a and r3-proposal, and every R3 row routed to Item 2 appears in its R3 table (checked row by row against r3-proposal §§ 1–4; none dropped). The code claims I checked hold: the raise sites at `occurrence.py:180`, `elaborate.py:2345`, `project.py:812` and `calc_compat_renderer.py:115, :120`; `SUBSET_REASON_CODES`, `string_value_not_generated` and `Qualification` at `subset_profile.py:124, :141, :235`; the retired shapes still in the reason vocabulary (`subset_profile.py:132, :135`); `kerml-expert` exists. The problems are in how independence is guaranteed, which known losses are covered, two gate edges, and the size.

---

## Audit

### Lens 1 — Faithfulness

**L1-1 · Direct claim:** The silent-loss table leaves out known families. Epic scope 4 says "every known silent-loss family". The table lists one manual-stub family (PUSH-DOWN-EXPR-PROFILE-UNSUPPORTED-OPERATOR, account row for `calc_compat_renderer.py:115`). The site account Item 1 handed over records six more calc-def-output sites with the same behavior, each noted as "the contract does not report this … becomes a manual stub": invalid Python output (`:62`), a `sum` invocation in a calc def output (`:76`), an IR-unrepresentable form (`:78`), a Boolean or String literal (`:96`), a feature chain (`:103`), a non-member reference such as a library constant (`:109`), plus the unary-operator site (`:120`). They are already known, so "a family found during the work joins the table" does not cover them. The `sum` row matters most: `sum` is the one supported callable everywhere else, so a user has no reason to expect a stub. Either add these as one family ("calc def output becomes a `MANUAL_REQUIRED` stub", with a case per distinct cause) or state why each is not a loss.

**L1-2 · Question to the user:** The spec's Independence section says each record outcome rests on a 2a case (inherited from agentic-mbse ADR 0001 invariant 5). But ADR 0001 invariant 1 (`.project/adr/0001-subset-profile-capability-ownership.md:29` in agentic-mbse) says a non-`unconfirmed` outcome needs "a probe of the pinned generator whose observed code matches, or a corpus citation for `admitted`". So a record moved to `refused` on the strength of a 2a case alone (criterion B6, and new rules for ES-002/ES-008/ES-009/CALC-DEF-BARE-RESULT) breaks invariant 1 as written. The spec files this as "may need an amendment" under Open Questions. It does need one, or else every new `refused` record also needs a fresh Item 1-style probe, which is the "second live authority" the spec rules out. **Do you want 2a to draft an ADR 0001 invariant 1 amendment for you to file (and should filing it count under RG-3, which today names only the ADR 0012 amendment)? Or should new `refused` records keep carrying a probe citation alongside the case, accepting two evidence sets?** Either way, B6 and the rule rows depend on the answer, and the spec should say so rather than leave it as an open design question.

**L1-3 · Direct claim:** CALC-USAGE-BARE-RESULT-DROP can close as "deferred with the limit stated", with no owner. The epic's Item 2a success criterion requires "explicitly deferred with an owner". Add the owner.

Provenance is otherwise clean. The governing obligation is `[AGENT]` ratified in the brief and correctly absorbed as `[INFERRED]`. Settled items are owner-grade: RG-1..3 trace to `briefs/align.md` and the epic's `[OWNER]` gate line, P-0003's quote is verbatim (`.project/product/0003-no-workarounds-for-bad-models.md:27`), and the shape retirement cites the epic's record of the owner's call. Every `[INHERITED]` item cites a source I could find.

### Lens 2 — Problem & Approach

**L2-1 · Direct claim:** For two rules the screen and the generator share the same decision table, so "evidence independent of the screen" cannot hold for them, and the spec does not say so.

- The generator's callable refusal (ES-005) is raised in agentic-mbse's `reference_use.py`, which reads `invocation_allowlist.py`. The screen reads the same allowlist. ADR 0001 invariant 4 states this on purpose.
- Constraint-predicate eligibility comes from `executable_profile.py` for both sides (epic design principle 2; codegen imports it in 8 places).

For these rules, generator and screen agree by construction about *which* callables or predicates are supported. Conformance can only test the parts that differ: contexts, ownership, instantiation. Criterion B5's mutation ("disable that site in the generator") has two problems here. The site lives in agentic-mbse, not codegen. And disabling the shared table flips both sides together, so no mismatch appears. The spec should state the limit, and say that the mutation for these rules targets the context logic each side owns separately, not the shared table. Otherwise design will either write a mutation that cannot fail or claim independence that does not exist.

**L2-2 · Question to the user:** The 17–27 day figure is too low for what this spec asks. It was made by subtracting the preparation-path and snapshot line from the Item 2 re-estimate (`evidence/re-estimate.md`). The lines that remain never priced several things the spec requires:

- the silent-loss families with seam assertions and controls (epic scope 4; not in the re-estimate at all), and more if L1-1 is accepted;
- the String fixture set and the RG-2 recommendation (D3);
- classifying all ~200 directories under `tests/fixtures/` and screening every generating one (B4), plus the refusal-totality check over every refusing fixture (C3);
- inventory mutations for new exception classes, helpers and computed mappings (E2), and screen-side recognition mutations (B5's second half);
- stable reasons and witnesses for 91 public sites (42 in scope + 39 follow-ups + 10 naming collisions; E3), where the re-estimate priced 81;
- the dc3 re-run (F3), the diagnostic renderer (A4), the record-citation mechanism (L1-2) and any package bump (L3-5).

My rough read is closer to 25–35 days. Most of the extra uncertainty sits in group E. One cut keeps the intent intact: keep E1/E2 (a new unaccounted raise site fails a test, which is drift detection), and give per-site stable reasons and witnesses only to sites that witness a shared rule or a recorded disagreement. Move the rest of E3/E4 (the 10 naming collisions, codegen-only follow-ups, triage of the 46 unknown sites) to a follow-on item. Those serve 2b's readiness claim and the inventory more than "the contract matches the generator". **Do you want the spec cut that way, or kept whole with an honest re-estimate?**

### Lens 3 — Pipeline Risk

**L3-1 · Direct claim:** No criterion requires the screen's outcome and the generator's outcome to agree on every case. This is the guard against circularity, and it is missing in one direction.

- C3 covers "generator refuses, screen must refuse or a disagreement is recorded".
- B4 covers "generator generates, screen must not refuse", but only for directories under `tests/fixtures/`. Conformance cases are not required to live there (the epic puts them under `tests/conformance/subset_profile/`).
- B2 requires that refused records have a refusing case. It does not forbid the screen reporting `refused` on a case the generator generates.

The failure this allows: someone widens a rule, the screen now reports `refused` on an admitted near-neighbor case, and they update that case's stored screen expectation to `refused`. Every check still passes, because each side matches its own stored expectation. A second form of the same gap: the Independence requirement forbids computing expectations at test time, but it does not stop the screen's expected outcome being captured once from the screen and committed. That is the screen checking itself one step removed. What needs to be true: for every case, the stored screen outcome and the stored generator outcome agree under the codegen mapping, or the pair is in the disagreement record. This turns the screen's expectation into something constrained by the generator, not an independent golden value. The spec should also say who or what reviews expectations, since "reviewed artifacts" has no named reviewer in an agent-run pipeline.

**L3-2 · Direct claim:** The "a stable site-level reason is not RG-1" carve-out only works for sites that already raise an `ElaborationCode`. E3 applies to every `public_capability` site, and two kinds have no code today:

- The calc-def-output stub sites (L1-1). They raise `CompilationError`, which is caught at `expression_compiler.py:291`, and generation succeeds with a stub. A "stable reason with a witness" means either a new diagnostic on a successful run, or turning the stub into a refusal. The second is RG-1. The first changes output and is not covered by the carve-out's condition.
- Builtin-exception sites (the epic counts 130 builtin candidates). If E4 finds one reachable, giving it a stable reason turns a crash into a diagnostic, which changes the exit behavior and the error the user sees.

The spec should say how each kind is handled: a non-refusing marker that stays outside RG-1, or an RG-1 recommendation with today's behavior pinned.

**L3-3 · Rewrite request:** B1 is not evaluatable at 2a's close. Its second sentence ("this stays true after Item 2b adds the screen to `generate`") is a constraint on 2b. Its first sentence passes trivially today because `generate` never calls the screen (no codegen module imports `subset_profile`). Restate B1 as what 2a delivers: a test that makes the screen raise and runs the generator half, which 2b's spec then inherits as a tripwire.

**L3-4 · Rewrite request:** B2 and B6 accept `omitted` as an observed outcome, but the generator half only reports "generated" or "refused". Seeing an omission takes a seam assertion. D1 requires seam evidence and says a name search over output does not count on its own. But D1 applies only to the D families, and Item 1 certified the three site rules' `omitted` contexts with a unique literal absent from output, which is a name search. Apply D1's seam rule to every `omitted` or `excluded` record outcome, not only to the D families.

**L3-5 · If-then tradeoff:** A2 says the agentic-mbse requirement admits no published version that lacks the contract. agentic-mbse's `pyproject.toml` still reads `0.1.3`, the same as codegen's `AGENTIC_MBSE_PACKAGE_VERSION`, which `_upstream_pins.py` describes as the "published agentic distribution". **If** 0.1.3 was published before Item 1 merged, A2 forces a version bump and a publish. Then "whether the package requirement needs a bump" is not an open question, and publishing is an outward-facing act that RG-3 does not name. **If** 0.1.3 was never published with the old content, a bump may not be needed. I could not check agentic-mbse's history from this session. The spec should find out which, and if a publish is needed, mark it as an owner action.

**L3-6 · Question to the user:** B4 says that when the screen refuses a generating fixture, "the contract is narrowed". That always sides with the generator. Under P-0003, a generating fixture the screen refuses might be the generator accepting a bad model. **Should B4 route that case the way G1/G2 are routed (pin the behavior, ask `kerml-expert`, recommend under RG-1) when the shape is doubtful under KerML/SysML v2, and narrow the contract only when the shape is valid?**

### Lens 4 — Hygiene

Nothing material.

### Lens 5 — Reader Comprehension

**L5-1 · Rewrite request:** B2's second sentence uses "SA-1" with no definition or pointer, and the sentence packs three alternatives into one clause. A3 is one long paragraph holding three separate tests (keys match, no-refusal entries, every pair witnessed). Define SA-1 or cite where it lives. Split A3 so each test is its own point.

---

## Engagement Summary

**Overall take:** The work item is right, the R3 table is complete, and the gate calls are mostly sound: changing the contract to match the generator really is not RG-1, because nothing user-facing reads the screen yet. The weak spot is the thing the spec exists for. One direction of screen/generator agreement is unguarded (L3-1), and two rules share their decision table with the generator, so independence cannot hold there and the spec doesn't say so (L2-1). The scope is also larger than its estimate (L2-2).

**Here's what I need you to weigh in on:**

1. **[L2-2]** Cut or re-estimate. My recommendation: keep the inventory drift test (E1/E2), keep per-site reasons only for sites that witness a shared rule or a recorded disagreement, and move the rest of group E to a follow-on item. Otherwise accept roughly 25–35 days.
2. **[L1-2]** ADR 0001 invariant 1 blocks moving records to `refused` on 2a cases. Draft an amendment for you to file (and count it under RG-3), or keep probe citations alongside cases?
3. **[L3-6]** When the screen refuses a fixture that generates, should the spec always narrow the contract, or route doubtful shapes through `kerml-expert` and RG-1 the way G1/G2 are routed?
4. **[L3-1]** Add a per-case agreement criterion (stored screen and generator outcomes agree under the mapping, or appear in the disagreement record). No decision needed from you unless you disagree. It is the core circularity guard.
5. **[L2-1, L3-2]** State the shared-table limit for invocation and constraint-predicate rules, and say how stub sites and builtin-exception sites get stable reasons without crossing RG-1. No decision needed from you unless you want stub-to-refusal changes considered now.
6. **[L1-1]** Add the six other calc-def-output stub causes to the silent-loss families. No decision needed from you unless you consider stubs not a loss.

---

## Resolutions

*(None yet. Record the owner's decisions here, keyed by finding ID, for the spec agent to incorporate.)*

---

**Verdict:** Revise
**Next Steps:** Once resolutions are recorded, re-run `/_my_spec` (or return to the spec-agent session) and point it at this review to incorporate. The reviewer does not edit the spec. Not checked in this review: agentic-mbse git history (the 0.1.3 publish question, L3-5), Item 1's spec for the definition of SA-1, and the product-lens beyond reading its ledger.
