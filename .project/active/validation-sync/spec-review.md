# Spec Review: agentic-mbse Sync — Guidance & Validation (Item 12)

**Spec:** `.project/active/validation-sync/spec.md`
**Contract:** Epic `epic_upstream_findings.md` Item 12 + cross-cutting R2
**Review File:** `.project/active/validation-sync/spec-review.md`
**Date:** 2026-07-06

---

## Reality Check

**Sound.** This spec's one job is to consolidate eleven items' recorded agentic-mbse
impact into one sourced, dispositioned table with nothing silently dropped (R2). It does
that. I cross-verified every row against every source recording — Items 1/3/4 specs, Item 5
close-out, Item 7 spec+release-notes, Items 8–11 specs/release-notes/audits, plus the
plant-fixtures audit and plan — and every recorded impact lands in a row with a disposition.
The two subtle sources (alias-surfacing audit Obs. 1→F5, Obs. 2→F3) are attributed
correctly. The contract-facing claims the checks mirror (V4 unknown-operator, V8
anonymous-return, V11 params-coverage, `**`/functions unsupported) all check out against
`docs/architecture/modeling-assumptions.md`. The Item-8 trap distinction (extraction is
finite/degenerate; recursion is evaluation-time) and the L6 false-positive enumeration are
confirmed verbatim in the plant-fixtures audit (`plant-fixtures/audit.md:165-170`,
`plant-fixtures/plan.md:746-762`).

The findings below are targeted, not structural. They're about where filed items land, one
soft impact that may have slipped, and a sizing call — not about the table being wrong.

---

## Audit

### Lens 1 — Faithfulness

**L1-1 · Question to the user:** Item 7's recorded agentic-mbse impact had **three** parts,
not one. F2 captures the V11 model-side-mirror candidate. But the Item 7 spec's third bullet
(`warning-reconciliation/spec.md:298-300`) asked to "confirm at close-out whether the
def-owned design-attribute shape (empty `parent_part`) is worth a guidance note
(part-def-owned design attributes are supported)." Item 7 has **no close-out**, and its
`release-notes.md` dropped the agentic-mbse-impact section entirely — so that question was
never resolved and does not appear anywhere in the consolidated table. This is exactly the
R2 failure mode the table exists to prevent (a recorded-but-undispositioned impact), even
though the item is soft ("worth a note?"). **Is this a deliberate no-impact call, or a
dropped thread? If the def-owned design-attribute shape warrants a MODELING_GUIDE line, it
needs a D-row; if not, it should sit in the "recorded as no-impact" paragraph so the trail
is complete.**

**L1-2 · Direct claim:** The header (spec line 8) states the implementation branch "already
carries the A-2 stencil fix." V1 (line 91) contradicts that certainty: it makes reading the
fix back a **[HARD]** gate precisely because it "landed... per plan but never read back."
Stating it as established fact in the header while V1 treats it as unverified is a small
internal inconsistency. Reword line 8 to "expected to carry the A-2 stencil fix (V1 confirms)"
so the header doesn't assert what the spec's own gate exists to check.

### Lens 2 — Problem & Approach

**L2-1 · If-then tradeoff:** The scope guard commits the **whole floor** — C1–C6 + D1–D7 +
V1–V2 + F1–F5 — to 1–1.5 days, and flexes only C7/C8. But the floor is six new/corrected
validation checks, each with a negative fixture, plus seven doc sections, executed in a repo
whose L1–L6 layout, check-function naming, and fixture format are all **unconfirmed** (the
spec is honest about this — Open Questions #1). Six checks-plus-fixtures in an unread
validation runner in 5–8h is aggressive. The guard's escape is "anything bigger than a small
check-plus-fixture gets filed" — which does technically cover a floor row that turns out
hard (C6 is the named example). **So the mechanism is there.** The question is whether you
want the floor itself treated as flex-under-pressure: if three floor checks turn out to need
rework against the real runner, the guard would file them and the "floor" shrinks. Is that
the intent — floor = "build what fits, file the rest, C1–C6 are just first in line" — or is
some minimal subset (say C1 self-named + C3 constraint, the two with existing negative
fixtures already in-repo) a hard must-land regardless? Worth stating which checks are
non-negotiable so the plan's sizing pass can't quietly file all of them.

### Lens 3 — Pipeline Risk

**L3-1 · Question to the user:** The FILE rows don't each name a destination, and the
command's own check flags this. SC-6 promises everything out-of-scope is "filed as an
agentic-mbse (or sysml-codegen) backlog item" — but only **F2** says which ("agentic-mbse
backlog"). F1 (vendor note), F3 (shape-B leaf-collision), F4 (redefinition/design_override
surfacing), and F5 (positive unresolvable-warning test) just say "file as backlog" with no
repo and no path. This matters more than it looks:
  - **F3/F4/F5 are sysml-codegen concerns** (filename disambiguation, channel surfacing, a
    codegen test), but Item 12 **executes in the agentic-mbse repo**. Whether that implement
    session can even write to sysml-codegen's `BACKLOG.md` (cross-repo) is unaddressed. An
    item "filed" into a repo the session can't reach is a soft drop — the exact R2 failure.
  - **F1** (the syside vendor note) has no home at all — is it an agentic-mbse backlog line,
    a report, or a note to Sensmetry? The spec says "file the note" but not where.

The exact path can stay deferred (the repo structure is unconfirmed), but the **repo per
row** is answerable now: assign each FILE row to agentic-mbse-backlog vs
sysml-codegen-backlog, and note which need cross-repo write access so the plan can sequence
them. **Where does each of F1/F3/F4/F5 land?**

**L3-2 · Rewrite request (minor):** C2 folds two different dispositions into one row — a
**FAIL** (anonymous `return`, mirrors V8) and a **WARN** (body-assignment form, loses
auto-impl) — under one "Return-style output check" heading with two fixtures. The R2 floor
is "a negative fixture for **every** check, shown to catch its trap." Merged like this, the
plan could build one check and one fixture and call C2 done, leaving the WARN leg unproven.
Ask the spec to either split C2 into two rows (FAIL-check + WARN-check) or state explicitly
that it's one check emitting two severities with a fixture pinning each leg — so the plan
can't under-deliver the WARN.

### Lens 4 — Hygiene

No material issues. Disposition codes are defined up front, sources are cited per row, and
the "recorded as no-impact" and "not agentic-mbse work" paragraphs close the trail on Items
2/6/7-matcher and the fusion-tea coordination items. This is a well-kept table.

### Lens 5 — Reader Comprehension

No blocking finding. The spec is long, but the structure carries it: the table is the
deliverable and reads as one, the Problem section states the drift-cuts-both-ways framing
plainly, and the scope guard is concrete. A tired engineer can find the floor, the flex, and
the filings on one pass.

---

## Engagement Summary

**Overall take:** The central check passes — the consolidated impact table is complete and
accurately sourced, with no per-item recording silently dropped. The spec is Revise-level,
not Rework: the gaps are about where filed items land, one soft Item-7 impact that may have
slipped, and whether the floor is honestly sized — not about the table being wrong.

**Here's what I need you to weigh in on:**

1. **[L3-1]** Assign each FILE row (F1, F3, F4, F5) a destination repo now. F3/F4/F5 look
   like sysml-codegen backlog items, but Item 12 runs in agentic-mbse — flag which need
   cross-repo write access so a filing can't fall between the two repos.
2. **[L1-1]** Decide the Item-7 def-owned-design-attribute guidance note: does it earn a
   D-row, or move to the no-impact paragraph? Right now it's recorded upstream but absent
   from the table — the one thread that may have slipped the R2 net.
3. **[L2-1]** Say which floor checks are non-negotiable. The guard can file any hard row,
   including C1–C6 — is that intended, or is a minimal subset a hard must-land?
4. **[L3-2]** C2 merges a FAIL and a WARN into one row; split it or state it's one check with
   a fixture per severity, so the WARN leg gets its proving fixture.
5. **[L1-2]** Reword header line 8 — it asserts the A-2 fix "already" landed, which V1 treats
   as unverified.

---

## Resolutions

*Resolved 2026-07-06; spec.md updated in place.*

- **L3-1 (FILE destinations):** Every FILE row now names a repo + path. F1/F2 →
  agentic-mbse backlog (implement session, `upstream-findings-sync`). F3/F4/F5 → this repo's
  `.project/backlog/BACKLOG.md`, written during Item 12's close-out step (runs in
  sysml-codegen). Added a "Filing homes" paragraph making explicit that no filing crosses a
  boundary the writing session can't reach.
- **L1-1 (Item-7 def-owned design-attribute note):** Added as row **D8** (BUILD-DOC, a
  one-line note alongside the retyping pattern), with the recorded soft/"no note needed"
  history noted and a plan escape to downgrade it. No longer absent from the table.
- **L2-1 (floor/flex boundary):** Scope guard now names four **non-fileable** must-land
  checks — C1 (self-named FAIL), C2a (return-style update), C4 (no-instantiation FAIL), C3
  (constraint WARN) — the traps that actually bit fusion-tea. Everything else (C5, C6, C2b,
  C7, C8) may file. Mirrored as a `[HARD]` requirement.
- **L3-2 (C2 split):** C2 split into **C2a** (accept + anonymous-return FAIL, own fixture)
  and **C2b** (body-assignment WARN, own fixture). The WARN leg can no longer go unproven.
- **L1-2 (A-2 phrasing):** Reframed per the resolution that A-2 **is committed** (`6dbdf1b`).
  Header, Problem bullet, V1, and the `[HARD]` requirement now treat A-2 as landed; V2 (the
  skill sweep for anything *else* stale) is the load-bearing gate, not re-verifying A-2.

**Disposition:** all five findings addressed. Ready for `/_my_plan`.

---

**Verdict:** Revise — the work item is sound and the table is complete; nail the FILE
destinations, resolve the Item-7 thread, and make the floor/flex boundary explicit before
this becomes the plan's contract.

**Next Steps:** Once resolutions are recorded here, re-run `/_my_spec` (or return to the
spec-agent session) and point it at this review to incorporate. The reviewer does not edit
the spec.
