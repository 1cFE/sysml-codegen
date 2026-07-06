# Spec Review: Silent-Failure Hardening (PIPELINE-TRUTH Item 5)

**Spec:** `.project/active/silent-failure-hardening/spec.md`
**Contract:** `claude-pack/commands/_my_spec.md`
**Review File:** `.project/active/silent-failure-hardening/spec-review.md`
**Date:** 2026-07-06

---

## Reality Check

**Sound, with correctable defects (Revise).** The spec is about the right work item, the
Problem section is accurate, the four-family framing holds against the code, the
coordination fences (Item 2 / Item 4) are clean, and the scope-beyond substrates are real.
The verification-pass discipline (R4) is genuinely executed, not performed.

But the spec was written *before* the orchestrator ran the probes live, and it has not
caught up:

- One finding (D3-11's output-half) is **refuted by the live run** yet still marked
  CONFIRMED, and Family 3 carries a `[HARD]` requirement to add validation that already
  exists.
- The Problem section's central epistemic hedge ("python execution is blocked… all
  verdicts rest on traces") is now **false** — probes ran live and changed several verdicts.
- The CONFIRMED count is **internally inconsistent** (the table has 14 confirmed rows; the
  Count line and the register both say 13).

None of these reframe the item. They are edits to the verification record. Verdict:
**Revise**.

---

## Audit

### Lens 1 — Faithfulness

**L1-1 · Direct claim (HIGH):** D3-11's output-half claim is refuted by the live probe.
The table row (spec:82) and Family 3 (spec:155-156, `[HARD]`) both state the `.output`
half of a backtracker target is "never validated" and require adding that validation. The
live run of `d311_usage_by_name.py` shows `find_required_modules(["power_calc.THIS_OUTPUT_DOES_NOT_EXIST"])`
**raises `TargetNotFoundError`** — the output half *is* validated. (My own trace of
`dependency_backtracker.py:244-254` shows the instance-name lookup raising; the observed
behavior means output validation exists on the path — either downstream of line 262 or the
probe's premise was off. Either way the spec's "never validated" is wrong.) This must be
**split**:
- Output-validation half → **NOT-REPRODUCED**; delete or reframe the Family 3 `[HARD]` at
  spec:155-156 (there is nothing to add).
- Instance-ambiguity half (`_usage_by_name` first-wins on colliding `power_calc`) → keep,
  but give it its own honest verdict. Note the code comment at
  `dependency_backtracker.py:151-154` calls these collisions "expected and benign" because
  internal processing uses qualified names — so design must decide whether the
  *user-facing target lookup* at line 248 warrants the require-unique-or-warn fix at all.

The same false claim lives in the register (verdict block line 123 lists D3-11 as
CONFIRMED; the D3-11 row at register:90 repeats "`.output` half never validated") — correct
it in place.

**L1-2 · Direct claim (HIGH):** The "Reproduction caveat (honest)" is stale. Lines 32-41
assert python execution "is blocked at the permission layer… every invocation form is
denied," and that all verdicts rest on code traces plus one committed live test (D3-2).
Since the spec was written, probes ran live (commit a9b3540 fixed a `parents[3]→[4]` path
bug): **SC-5, the self-named drift, D3-2, D3-4, and SC-4 are now live-confirmed; D3-11's
output-half is live-refuted.** The caveat as written understates confidence for the
confirmed findings and hides the D3-11 refutation. Rewrite it to state plainly: which
findings ran live and confirmed, which remain code-trace-only, and which were refuted. The
per-row Evidence cells (`(trace)` vs `(live)`) must be re-tagged to match the live run.

**L1-3 · Direct claim (MEDIUM):** The CONFIRMED count does not add up, three different ways.
- The **table** marks 14 rows as CONFIRMED / CONFIRMED-latent / CONFIRMED(live):
  D3-1,2,3,4,5,6,7,8,10,11,12,14,15,16.
- The **Count line** (spec:98-99) says "13 CONFIRMED/CONFIRMED-latent defects, 2
  RECLASSIFIED, 1 drift" — and reuses the "1" for drift.
- The **Problem section** (spec:22-27) says "13 of 16 as real defects… reclassifies 2…
  carries 1 as a real-but-unreachable code gap" — here the "1" is D3-3, held *out* of the 13.
- The **register** (research doc:123-124) says "13 CONFIRMED" but then lists **14** QNs
  (D3-1/2/3/4/5/6/7/8/10/11/12/14/15/16).

Pick one accounting for D3-3 (is it inside the confirmed count as CONFIRMED-latent → 14, or
a separate "unreachable" bucket → 13 + 1?) and make the table verdict column, the Count
line, the Problem section, and the register all agree. The L1-1 correction forces a recount
anyway, so do it in the same pass.

**L1-4 · Direct claim (MEDIUM):** The probes are presented as runnable-as-is; three are not.
Lines 39-41 say "the committed probe scripts under `probes/` reproduce each finding the
first time python execution is permitted," and Next Steps (spec:257-259) says design should
"run the probe scripts live to convert every CONFIRMED-latent trace into an executed
reproduction." But `d37_partname_merge`, `d38_caret_operator`, and `d310_leaf_redef`
fixtures contain **no calc def** (only `invocation_binding_probe` does), so
`build_pipeline_context` raises before the probe reaches its finding — confirmed against the
fixtures dir. State the gate honestly in the spec: those fixtures need a calc def added at
design-open, and D3-7 / D3-8 / D3-10 stay code-trace-only until then. (The orchestrator also
reports d3-1 didn't run despite its fixture carrying a calc def — design should confirm
what that probe still needs.)

### Lens 2 — Problem & Approach

**L2-1 · Direct claim (HIGH):** The byte-identical success criterion collides with D3-2's
own fix. SC (spec:54-56) carves out **only D3-8** as the byte-identical exception. But D3-2
(3+-segment chain truncation) is **live-reproduced on `deep_cross_scope_probe`, a committed
fixture** — the conformance test asserts the truncation. Fixing D3-2 (parse the full chain
*or* hard-diagnose) either rewires that fixture's output or emits a new warning on it —
**not byte-identical.** Either add D3-2 as a second explicit exception, or confirm
`deep_cross_scope_probe` has no generation baseline that the fix would move. The same risk
applies to any latent finding whose authored trip fixture becomes a permanent corpus
fixture (D3-3/6/7/8/10/15/16) — spell out which of those enter the baseline corpus.

**L2-2 · If-then tradeoff (MEDIUM):** D3-2's fix mode is left open in a way that contradicts
the Non-Goals. The `[NEED]` at spec:123-124 permits "either fully parsed (via
`extract_feature_chain_segments`) or hard-diagnosed." "Fully parsed" means **implementing
multi-hop chain support**, which the Non-Goals (spec:192-195) explicitly defer — "Loud
rejection is this item's contract; the features are deferred." If design reads the `[NEED]`
literally it could ship a feature the Non-Goal forbids. Constrain D3-2 to loud-reject to
match the contract, **or** make full-chain-parse a sanctioned exception (it's cheap —
`extract_feature_chain_segments` already exists). This interacts with L2-1: parse changes
output, reject adds a warning; either way the byte-identical claim needs the carve-out.

**L2-3 · Question to the user (MEDIUM):** Can D3-3 and D3-16 actually be given a
fires-on-shape test? Both are CONFIRMED-latent with "no fixture triggers" (D3-3, spec:74)
and "not confirmable live… reachability narrow" (D3-16, spec:87). The cross-cutting R1
`[HARD]` (spec:182-187) requires *every* diagnostic to land with a fires-on-shape test whose
expectation is independently anchored. If D3-3's shape is unreachable without a parser bug,
what input does that test feed? Either these are closed-by-construction (the totality fix
removes the gap, and there's no reachable shape to assert on — say so), or they need a
synthetic/partial-SysML trip that the spec should name. Don't promise a fires-on-shape test
the item can't author.

### Lens 3 — Pipeline Risk

**L3-1 · Rewrite request (LOW):** SC-4 and SC-5 are `[HARD]` requirements with no matching
success criterion. The Success Criteria list (spec:44-59) covers the families and the
verification table, but nothing would catch a regression of "sanitizer is injective at key
construction" (SC-4 A1) or "non-float EP gets a diagnostic, never a silent `None`" (SC-5).
The cross-cutting R1 SC covers them implicitly; make it explicit — the contract flags a
`[HARD]` that no success criterion would catch if violated.

**L3-2 · Question to the user (LOW):** When is the register's disposition column updated?
The first SC (spec:45-47) requires "the discovery register's D3 disposition column updated
in place to match" — as part of this verification pass. But the register still shows every
row's Disposition as "Item 5" (research doc:80-95), with the verdicts in a *separate* prose
block; and SC (spec:57) plus register:130-131 say the column is "discharged in full at item
close." Two SCs disagree on timing. Decide whether the per-row column update is a spec-pass
deliverable or a close deliverable. (Regardless, the L1-1 and L1-3 corrections mean the
register's verdict block needs editing *now* — it currently states a refuted claim and a
wrong count.)

**L3-3 · Direct claim (LOW):** D3-12 and SC-5 share a downstream drop path. D3-12
(default-expr `except: return None`, `parameter_groups.py:192-193`) and SC-5 (non-float EP
`float()→None`, same module) both end in "param silently omitted," and the spec
cross-references them (D3-12 evidence cell). Fine to keep both — the *root causes* differ —
but flag for design: fix the two roots without double-patching or leaving a gap at the
shared omission site.

### Lens 4 — Hygiene

**L4-1 · Rewrite request (LOW, optional):** A few line cites drift from the code
(`_classify_entry_points` is at `graph_builder.py:425`, spec cites `:482`; `parameter_groups`
lives under `analysis/`, not `generation/`). These are Item-2-owned or minor and don't
change any verdict — fix opportunistically during the L1 edits, don't spend a pass on them.

### Lens 5 — Reader Comprehension

**L5-1 · Rewrite request (LOW-MEDIUM):** The "Reproduction caveat (honest)" block
(spec:32-41) is one dense paragraph doing three jobs at once — the sandbox limitation, why a
trace is airtight, and where the probes live. Combined with the L1-2 staleness, ask for it
to be re-decomposed against the live run into three plain points: what ran live and
confirmed, what stays trace-only (and why the trace suffices), and what the live run
refuted. This is a comprehension fix and an accuracy fix in one edit.

---

## Engagement Summary

**Overall take:** The spec does the hard part right — the verification pass is real, the
family choke points check out against the code, and the fences around Items 2 and 4 are
clean. Its problem is that it froze before the probes ran: it still marks a live-refuted
finding as CONFIRMED, still claims python was never executed, and miscounts its own
confirmed list. These are record-keeping edits, not a rethink. **Revise.**

**Here's what I need you to weigh in on:**

1. **[L1-1]** D3-11 must be split: the "`.output` half never validated" claim is refuted
   live (the lookup raises `TargetNotFoundError`) — reclassify that half NOT-REPRODUCED,
   delete the Family 3 `[HARD]` that adds validation, and keep only the instance-ambiguity
   half with its own verdict. Fix the register to match.
2. **[L1-2, L5-1]** Refresh the "Reproduction caveat" and the per-row Evidence tags to the
   live run — SC-5, drift, D3-2, D3-4, SC-4 confirmed live; D3-11 output-half refuted. The
   "python is blocked" framing is no longer true.
3. **[L2-1, L2-2]** Byte-identical vs D3-2: fixing chain truncation on the committed
   `deep_cross_scope_probe` fixture is not byte-identical. Decide the D3-2 fix mode
   (loud-reject to honor the Non-Goal, or sanctioned full-parse) and carve it out of the
   byte-identical SC — the way D3-8 already is.
4. **[L1-3]** Reconcile the CONFIRMED count (table says 14, Count line and register say 13,
   Problem section implies 13+1). Pick D3-3's home and make all four places agree.
5. **[L1-4]** Three probe fixtures (d37/d38/d310) have no calc def and can't run as-is.
   State that gate honestly and keep D3-7/D3-8/D3-10 labeled code-trace-only until the
   fixtures are repaired at design-open.
6. **[L2-3]** Decide whether D3-3 and D3-16 (unreachable / narrow) can carry the required
   fires-on-shape test, or are closed-by-construction with nothing to assert on.

---

## Resolutions

_(Filled in during Stage 5, keyed by finding ID.)_

---

**Verdict:** Revise
**Next Steps:** Once resolutions are recorded here, re-run `/_my_spec` (or return to the
spec-agent session) and point it at this review to incorporate. The reviewer does not edit
the spec. The register corrections (L1-1, L1-3) travel with the spec-agent edit, not this
review.
