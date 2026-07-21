# Spec Review: Docs + Explainer-Brief Refresh (post-CONSTRAINT-EXEC)

**Spec:** `.project/active/docs-explainer-refresh/spec.md`
**Contract:** `claude-pack/commands/_my_spec.md`
**Review File:** `.project/active/docs-explainer-refresh/spec-review.md`
**Date:** 2026-07-13

---

## Reality Check

**Sound.** The spec is pointed at the right work item — correct the doc surfaces CONSTRAINT-EXEC
left stale and re-anchor the explainer brief, as a targeted survey-driven sweep. Every home-repo
`[HARD]` claim checks out against HEAD (verified below), the Problem section is materially
accurate, and design would not be misled by treating this as the contract. The findings below are
refinements to auditability and one real coverage gap — none are Rework-level.

**Code-claim verification (sysml-codegen HEAD, this session):**

- `SNAPSHOT_FORMAT_VERSION = 3` — confirmed, `snapshot/__init__.py:19`.
- `ModuleKind` has five values incl. `CONSTRAINT` / `REPORT_AGGREGATOR` — confirmed,
  `resolution/models.py:161-170`.
- `ExpressionAST` / `build_expression_ast` / `compile_expression` — zero hits in `src/`. Confirmed gone.
- Contracts/seal symbols present — `ModelContract`/`PackageContract` (`contracts/models.py`),
  `seal_package` (`contracts/seal.py:57`), `cmd_seal` CLI (`cli/__init__.py:704`). Confirmed.
- `overview.md` says "29 requirement families" (`overview.md:218`); `verification-matrix.md:13`
  says 31. Discrepancy confirmed.
- Cited matrix rows still carry retired symbols: REQ-AST-06 (`:96`) and REQ-CA-02 (`:144`) both
  reference `build_expression_ast()`/`compile_expression()`; REQ-SNAP-09 (`:506`) narrates V1/V2.
  Confirmed.

**Verification boundary:** the agentic-mbse and teax repos are outside this session's sandbox
(reads blocked). The cross-repo staleness claims (decision-table terms, `MODELING_GUIDE.md:280`,
teax `entry_models`) are taken on the survey's authority per its explicit trust-but-spot-check
instruction. Every home-repo spot-check held, which raises confidence in the survey overall — but
the cross-repo deliverables (SC-4, SC-5, SC-7) rest on evidence I could not independently confirm.

---

## Audit

### Lens 1 — Faithfulness

**L1-1 · Direct claim (positive):** The `[HARD]` block is fully accurate against HEAD — all six
code claims verified. Provenance is clean: both `[NEED]` items carry `[OWNER] 2026-07-13`, the
first with a verbatim quote, and the `[INHERITED]` items cite the archived Item 5/8/14 artifacts.
Nothing is tagged `[HARD]` that is really one option among several, and nothing settled is
agent-originated. No faithfulness defect here.

**L1-2 · Question to the user:** The three cross-repo deliverables (SC-4 agentic-mbse, SC-5 teax,
SC-7 fusion-tea) rest entirely on survey findings I could not verify from this sandbox. The survey
says "trust-but-spot-check," and every sysml-codegen spot-check held — but the survey was run in a
single owner session. **Are you confident the agentic-mbse and teax findings were checked against
those repos' HEADs (not just skimmed), or should the implementer re-spot-check those two before
editing?** This is the one place the "do not re-survey" instruction has no home-repo safety net.

### Lens 2 — Problem & Approach

**L2-1 · Direct claim:** The first success criterion has a header/body scope mismatch. The header
reads **"No doc contradicts HEAD"** — an absolute, repo-wide guarantee. The body scopes it to "the
specific stale claims inventoried in `staleness-survey.md`." These are different bars. Read
literally, the header is a full-docs scrub, which Non-Goals explicitly excludes. An auditor could
fail an implementer for a stale doc the survey never covered; an anxious implementer could think
they must verify all 28 reference docs. The bet of this spec is *targeted*, and the criterion
should say so in its header, not just its body. Rename/reframe so the checkable claim is "the
surveyed inventory + named gap areas are corrected," not "no doc anywhere contradicts HEAD."

**L2-2 · If-then tradeoff (positive):** The core bet — targeted sweep over full scrub — is sound
**if** the survey is complete, and the spec correctly files "full scrub" as a Non-Goal with its own
item shape. The only residual risk is survey completeness (L1-2). Given that, the framing and
sizing are right: this is one coherent MEDIUM item, not something that should split further.

### Lens 3 — Pipeline Risk

**L3-1 · Direct claim (coverage gap):** The `[INHERITED]` cautions have no success-criterion hook.
The spec correctly states in Known Requirements that (a) the `lower_constraints_enabled` flag story
is *history*, (b) `collect_constraint_manifest` survives deliberately, and (c) CE-F1/CE-F2 are open
follow-ons so docs must describe current embedded-catalog / single-channel-bridge reality. But none
of the eight success criteria would catch a violation. An implementer writing the new ModuleKind /
contracts / lowering docs could satisfy every success criterion and still write "constraints can be
dropped via the flag" or "the manifest collector was removed" or document CE-F1's standalone
`constraint_catalog.json` as if it shipped — reintroducing exactly the contradictions this item
exists to kill. These cautions need to be operationalized as checkable bars (e.g. a criterion:
"new docs describe the flag as landed-and-empty history, name `collect_constraint_manifest` as
surviving, and reference CE-F1/CE-F2 as unshipped follow-ons"), not left only in the requirements
prose.

**L3-2 · Rewrite request:** SC-6 (`EXPLAINER_PROMPT.md` truthful/buildable) mixes a mechanically
auditable checklist with an aspirational whole-document bar, and the two aren't separated. The
checkable parts are concrete: named caveats retired (grep "constraints are dropped",
`resolve_input()`), the eight constraint-exec artifact areas slotted per the survey's mapping,
re-anchored off `pipeline-truth-epic` HEAD. The aspirational part — "**no claim contradicted by
HEAD**" across a large prose brief — is not mechanical; it requires reading every claim. Both
belong, but the criterion should split them so an auditor knows the tractable procedure (retire
these caveats, slot these eight areas, re-anchor) versus the judgment call (spot-read remaining
claims). As written it reads as one uniformly-checkable bar, which it is not.

**L3-3 · Question to the user:** SC-7 and Non-Goals both touch the one allowed code change (the
fusion-tea `ToyPlantParams` alias). SC-7 says "drop (or mark historical)"; Non-Goals scopes code
changes to exactly this. That's consistent. But the alias removal is the only runtime-affecting
edit in an otherwise docs-only item, in a repo on `main` (not the epic branch). **Is dropping the
alias in scope for this item's landing, or would you rather the implementer default to the
"mark historical" comment path to keep this item docs-pure?** Naming the default avoids a
non-interactive implementer guessing.

**L3-4 · Direct claim (minor, positive):** The deferred Open Questions are genuinely design-stage
(matrix family shape, contracts doc numbering, agentic-mbse doc depth, Gen-1 HTML banner). None is
a spec-stage question being punted — each depends on structure design will settle, and the brief
confirms the owner delegated them. No defect.

### Lens 4 — Hygiene

**L4-1 · Rewrite request (optional):** SC-3's parenthetical "(shape of the family is design's
call)" and SC-4's "(depth is design's call …)" restate the Open Questions inline. Not wrong, but
the same deferral now lives in two places; if one moves the other can drift. Consider letting Open
Questions own the deferrals and keeping the success criteria to the checkable minimum ("a family
exists," "a durable `docs/` home exists"). Low priority.

### Lens 5 — Reader Comprehension

**L5-1 · Rewrite request:** SC-1 and SC-6 are each a single ~6-line sentence packing many
`file:line` cites, REQ IDs, and semicolon-chained clauses. For the implementer they're usable
reference density; for the human reviewer deciding whether to sign the contract, they're hard to
skim once. Consider breaking SC-1 (snapshot / expression-symbols / family-count) and SC-6 (retire
caveats / slot eight areas / re-anchor) into nested checkable sub-bullets. This also directly
serves the audit: sub-bullets are what an auditor ticks off. Moderate — the content is right, the
packaging fights a one-read skim.

---

## Engagement Summary

**Overall take:** The spec is faithful and well-grounded — every home-repo `[HARD]` claim verified
against HEAD, provenance is clean, and the targeted-sweep bet is the right one. It's a Revise, not
an Approve, for three reasons: one success criterion promises more than the item delivers (absolute
"no doc contradicts HEAD" vs a survey-scoped sweep), the `[INHERITED]` cautions that this whole item
exists to enforce have no success-criterion that would catch their violation, and the explainer bar
blurs a mechanical checklist into an aspirational whole-doc claim.

**Here's what I need you to weigh in on:**

1. **[L3-1]** The flag-is-history / collector-survives / CE-F1-F2-unshipped cautions live only in
   the requirements prose — nothing in the success criteria would fail a doc that violates them.
   Add a criterion that makes these checkable, or accept that an audit against the success criteria
   alone won't catch a reintroduced "constraints are dropped" story.
2. **[L2-1]** Rescope SC-1's header from the absolute "No doc contradicts HEAD" to the actual bar —
   the surveyed inventory + named gap areas — so it doesn't read as the full scrub Non-Goals excludes.
3. **[L3-2]** Split SC-6 into its mechanically-auditable parts (caveats retired, eight areas slotted,
   re-anchored) and the judgment-call part ("no claim contradicted by HEAD"), so the auditor has a
   tractable procedure.
4. **[L1-2]** Confirm the agentic-mbse and teax survey findings were checked against those repos'
   HEADs — they're the three deliverables with no home-repo verification, and the sandbox blocks
   independent confirmation here.
5. **[L3-3]** Decide the default for the fusion-tea alias — drop it, or the docs-pure "mark
   historical" path — so a non-interactive implementer doesn't guess on the item's one code change.

---

## Resolutions

Recorded by the orchestrator (2026-07-13, autonomous run; owner delegated all non-reserved
decisions at Align). All spec edits applied same day.

- **[L3-1] — Fixed.** New success criterion added ("New/edited docs keep the inherited
  history straight") operationalizing the three `[INHERITED]` cautions as checkable bars
  (flag = landed history; collector not removed; CE-F1/F2 as open follow-ons).
- **[L2-1] — Fixed.** SC-1 header rescoped to "The surveyed inventory is corrected" with an
  explicit not-a-scrub scope note; body split into sub-bullets (also discharges L5-1 for SC-1).
- **[L3-2] — Fixed.** SC-6 split into a *mechanical checklist* (caveats grep-clean, eight
  areas slotted, re-anchored) and a *judgment bar* (spot-read, no claim contradicted by HEAD).
  While editing, corrected an anchor slip: the original said "re-anchored off
  `pipeline-truth-epic` HEAD," which is the brief's *stale* anchor per the survey; the target
  is current HEAD (constraint-exec-epic).
- **[L1-2] — Verified by the orchestrator** (this session has all four repos in reach): the
  decision-table retired vocabulary is live at `:13,:18,:35` with `constraints.md:338`
  linking in; `MODELING_GUIDE.md:280` still says "not executable"; agentic-mbse `docs/` has
  zero ConstraintFacts/ExpressionIR hits; teax `docs/evaluation-and-study.md` has zero
  `entry_models` hits while `evaluator.py:107` defines it; fusion-tea walkthrough + aliases
  present. Survey confirmed at HEAD; one refinement — the alias has *three* sites
  (`bench_prepare_once.py:36,61`, `run_viability_study.py:135`) plus a stale comment
  (`run_viability_study.py:130`), now cited in SC-7.
- **[L3-3] — Decided: drop the alias** (not the docs-pure comment path), recorded in SC-7
  with the teax-CE-F3 sequencing caveat. Execution-detail tier; the scripts are exploration
  drivers, not CI-gated.
- **[L4-1] — Declined** (low priority; duplication is two stable pointers, drift risk small).
- **[L5-1] — Applied to SC-1 and SC-6** via the splits above.

Continuing without a re-review round: every fix is an objectively verifiable application of
the review's own instructions (pipeline rule: record the verification and continue).

---

**Verdict:** Revise
**Next Steps:** Record resolutions above, then re-run `/_my_spec` (or return to the spec-agent
session) and point it at this review to incorporate. The reviewer does not edit the spec. The
underlying work item is sound — these are tightening edits to auditability and one coverage gap,
not a redirection.
