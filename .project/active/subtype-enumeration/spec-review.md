# Spec Review: Subtype-Aware Enumeration & Constraint-Report Truth

**Spec:** `.project/active/subtype-enumeration/spec.md`
**Contract:** `claude-pack/commands/_my_spec.md`
**Review File:** `.project/active/subtype-enumeration/spec-review.md`
**Date:** 2026-07-06

---

## Reality Check

**Concerns (fixable) — the work item is right; one load-bearing claim is wrong.**

The spec is pointed at the correct problem, the mechanism (one adapter parameter, opt-in per call site) is sound, and the decision table is genuinely complete — every `elements_of_type` call in `src/` maps to a table row (verified below). But a `[HARD]` requirement rests on a false metamodel claim: the spec says a `RequirementUsage`-exclusion filter "correctly keeps `SatisfyRequirementUsage` *in*," and it does not — `SatisfyRequirementUsage` subclasses `RequirementUsage`, so the filter drops it. That is a must-fix. Two more must-fixes are coordination gaps the spec understates: the snapshot format-version bump forces a license-gated re-capture of all 20 committed snapshots, and the settled agentic-mbse checkout / dirty-tree branching procedure never made it into the spec. None of these unseat the item; they are targeted edits. **Revise.**

---

## Audit

### Lens 1 — Faithfulness

**L1-1 · Direct claim (MUST-FIX):** The spec rests a `[HARD]` semantic on a false type hierarchy. Line 100 asserts `SatisfyRequirementUsage ⊂ AssertConstraintUsage`, and lines 130–131 conclude the `RequirementUsage`-exclusion "also correctly keeps `SatisfyRequirementUsage` *in* … since it is reached as a `ConstraintUsage` subtype that is not a `RequirementUsage`."

Checked against the syside stub (`.venv/lib/python3.12/site-packages/syside/core/__init__.pyi`):

- `class SatisfyRequirementUsage(RequirementUsage)` — line 16063.
- `class RequirementUsage(ConstraintUsage)` — line 15686.
- `class AssertConstraintUsage(ConstraintUsage)` — line 886.

So `SatisfyRequirementUsage` **is** a `RequirementUsage`. It is not a subtype of `AssertConstraintUsage`. The `[HARD]` requirement (lines 125–131) states the fixed semantic as "assert **and satisfy** and require in, requirement out" — but that is unimplementable with the stated mechanism: an `is_instance("RequirementUsage")` exclusion drops `SatisfyRequirementUsage` along with every other `RequirementUsage`. The spec's own preferred exclusion mechanism therefore contradicts its own stated semantic.

This propagates. Rows 1, 6, and 7 all cite "assert/satisfy in, requirement out" and rows 6/7 explicitly "mirror row 1." All three, plus the `[HARD]` block at 125–131 and the metamodel-facts bullet at line 100, inherit the correction.

Two legal resolutions (this is a semantic call for the human, not a mechanical fix):

- **(a) Accept satisfy-excluded, and record it deliberately.** The simple `is_instance("RequirementUsage")` filter naturally drops satisfy. Defensible: no supported model uses `satisfy`. This is the cleaner option — it needs no new mechanism, only a corrected metamodel-facts bullet, a rewritten `[HARD]` semantic ("assert and require in; requirement **and satisfy** out"), and a decision-table note so the exclusion is a conscious choice, not an accident.
- **(b) Keep satisfy in.** Then the filter must be "exclude `RequirementUsage` **except** `SatisfyRequirementUsage`" (`is_instance("RequirementUsage") and not is_instance("SatisfyRequirementUsage")`). More machinery, for a shape no supported model uses.

Recommend (a) unless you know a near-term model that asserts via `satisfy`. Either way the false hierarchy claim cannot survive into the contract.

**L1-2 · Direct claim (MUST-FIX, cross-repo):** Open Question (1) — "which agentic-mbse checkout is canonical" (lines 232–237) — is settled, but the spec still carries it as open. The orchestrator verified `/home/reid/1cfe/agentic-mbse` is the only checkout and this project's editable install points there; the `agentic-mbse-repo-path` memory note records the same. The spec must carry the settled answer in (target `/home/reid/1cfe/agentic-mbse`, not `~/agentic-mbse`) and stop presenting it as a design-stage question. See also L3-3 for the missing dirty-tree procedure that belongs with it.

**L1-3 · Direct claim (positive — no action):** The decision table is complete against this repo's real call sites. Every `elements_of_type` call in `src/` maps to a row: `extractor.py:108`→row 1, `constraint_extractor.py:50`→row 2, `parameter_groups.py:102`→row 3, and the six `PartDefinition`/`PartUsage`/`CalculationDefinition`/`CalculationUsage` sites (`extractor.py:72,85`; `usage_extractor.py:260,296,549`; `hierarchy_resolver.py:596,672`; `pipeline_builder.py:120,121`)→row 4. Nothing on the codegen side escaped. Row 2's deletion premise also holds: `extract_all_constraints` has no caller in `src/` or `tests/` (only its own `__all__` entry). The agentic-mbse rows (5–8) could not be verified from this sandbox — the spec correctly flags line re-verification (`level3_dataflow.py:48` etc.), and R4's "the probe wins" governs.

### Lens 2 — Problem & Approach

**L2-1 · If-then tradeoff:** The item bundles two distinct pieces of work: (1) subtype-aware enumeration + the constraint report firing on asserts, and (2) constraint serialization + a snapshot format-version bump + live-vs-snapshot parity. Piece (2) is arguably the larger and riskier half (a schema change, a full re-capture, and a new parity surface — see L3-1). Bundling is defensible **if** you want the third success criterion (from-snapshot report) in this item, which the epic scoped here (Item 4, scope 6) and which is a stated prerequisite for the deferred constraint-execution epic. It is a problem **if** the format bump's re-capture cost (L3-1) turns out to dominate the 1–1.5 day estimate — in which case serialization is a clean split point. Not a blocker; flagging so the size is a conscious call before design, not a surprise during implement.

### Lens 3 — Pipeline Risk

**L3-1 · Direct claim (MUST-FIX):** The format-version bump's blast radius is understated. SC line 78–79 says "existing baselines byte-identical **except the deliberate snapshot format-version bump**." That framing implies one line changes. Reality:

- There are 20 committed `extraction_snapshot.json` files (`tests/fixtures/*/`). `SNAPSHOT_FORMAT_VERSION = 1` today (`snapshot/__init__.py:12`); the loader gates on it (INV-2, `loader.py:81`) and rejects a mismatch. Bumping to 2 means **every one of the 20 must be re-captured** — not diffed-and-kept — or they fail to load.
- Snapshots for models that carry constraints also gain the new constraint manifest, so those diffs are more than the version line.
- Re-capture runs live extraction via `scripts/capture_extraction_snapshots.py` — it needs the syside license. So this item triggers a **license-gated, repo-wide** snapshot regeneration, which the spec never states.

The spec should (a) state plainly that the bump forces re-capture of all committed snapshots and that this is license-gated, and (b) correct the "byte-identical except the version bump" phrasing — the majority of the 20 change by at least the version field, and the load-gate means there is no partial-rollout state where old and new snapshots coexist.

**L3-2 · Question to the user (sequencing):** Item 4 (Track B) and Item 1 (Track A, scheduled first) both write snapshots; Item 2 regenerates plant baselines. Item 1 *creates new fixtures + snapshots at format v1*; Item 4 bumps to v2 and re-captures everything. If they land in parallel branches, every snapshot file collides on merge, and Item 1's brand-new fixtures need re-capture at v2 anyway. The epic's "one item's regen at a time" mitigation names Items 2/5/8 — **not** Item 4 or Item 1, the two that actually create/rev the snapshot format. **Who owns the re-capture of the shared and Item-1 fixtures after the bump, and in what order relative to Items 1 and 2?** The spec should name the ordering, not leave it to merge luck.

**L3-3 · Rewrite request (MUST-FIX, cross-repo landing):** The companion-branch plan is not concrete enough to execute. The spec says "agentic-mbse companion branch (fix + fixtures + adapter decision-table docs)" (line 249) and cites `upstream-findings-sync` as precedent, but omits the operational constraint the orchestrator flagged: that repo is currently on `upstream-findings-sync` with a **dirty working tree** (unrelated in-flight work — `adr002.py` + two spec dirs). Item 4's implement stage must **branch from current HEAD and stage only its own files — no stashing, no picking up the dirty files.** Add this procedure to the spec (alongside the settled checkout from L1-2) so the implementer does not stash or co-mingle another workstream's changes.

**L3-4 · Direct claim (internal inconsistency):** The `[HARD]` verification-first requirement (lines 183–187) says to reproduce each CONFIRMED-BLIND site "and record it in **the verification table below**." There is no table below — the spec ends the section with prose, and Next Steps (lines 256–258) defers the table to the *opening of design*. So the cross-reference is dangling. Epic R4 only mandates the in-spec verification table for Items 5 and 7, so deferring it to design is legal for Item 4 — but then the `[HARD]` wording must say the table is produced at design open, not "below." Reconcile the requirement text with the Next Steps deferral (and with SC line 76–77's "before design touched it").

**L3-5 · Direct claim (under-pinned, minor):** Row 5's silent-on-clean leg is implicit. The `[HARD]` at lines 135–138 requires *every* new/changed diagnostic to carry both a fires-on-shape and a silent-on-clean test. Row 5 pins "non-empty-dep-graph fixture + seeded circular-import fixture FAILS" — that is the fires-on-shape leg. The silent-on-clean leg (an **acyclic** import fixture must **pass** the circular check, i.e. not false-positive) is only implied by "non-empty-dep-graph fixture." Make the acyclic-passes assertion explicit for row 5 so it matches the standard the other rows are held to.

### Lens 4 — Hygiene

**L4-1 · Rewrite request:** The REQ-EXT-09 test path is cited wrong throughout. The spec writes `test_extractor.py:895-899` and `test_extractor.py:893-922` (Problem bullet, and lines 139, 196). The file is `tests/conformance/test_extractor.py`; the self-referential `expected` block is lines 894–899 and the class runs 888–923. There is no `tests/unit/test_extractor.py` with this test. A downstream agent will grep the cited path and miss. Correct the path (and the line span) at every occurrence.

### Lens 5 — Reader Comprehension

No blocking findings. The spec is dense but well-structured; the decision table carries its own rationale column, and a tired engineer can find the work and the bets on one read. (One small note, not a finding: the zero-found sentinel wording "scanned N … matched 0" at line 145–148 reads slightly muddled — "scanned" counts the full `ConstraintUsage` subtree while "matched" counts droppables after excluding requirements; a one-clause clarification would help, but it does not block comprehension.)

---

## Engagement Summary

**Overall take:** The item is sound and the decision table is genuinely complete — but the spec rests a `[HARD]` requirement on a false type hierarchy (`SatisfyRequirementUsage` is a `RequirementUsage`, so the exclusion drops satisfy, contradicting "satisfy in"), and it understates two coordination costs: a license-gated repo-wide snapshot re-capture from the format bump, and the settled-checkout / dirty-tree companion-branch procedure. All three are targeted fixes, not a rework.

**Here's what I need you to weigh in on:**

1. **[L1-1]** The satisfy metamodel error. Pick the resolution: **(a)** accept satisfy-excluded and record it deliberately (recommended — no supported model uses `satisfy`), or **(b)** keep satisfy in with an exclude-except-satisfy filter. Whichever you pick, the metamodel-facts bullet, the `[HARD]` semantic line, and rows 1/6/7 rationale all get rewritten.
2. **[L3-1, L3-2]** The format-version bump forces re-capture of all 20 committed snapshots (license-gated) and collides with the snapshot work in Items 1 and 2. Decide the sequencing and who owns the shared re-capture, and correct the "byte-identical except the version bump" framing.
3. **[L1-2, L3-3]** Carry the settled agentic-mbse checkout (`/home/reid/1cfe/agentic-mbse`) into the spec and add the concrete companion-branch procedure: branch from current `upstream-findings-sync` HEAD, stage only Item 4's files, no stashing.
4. **[L3-4]** Reconcile the dangling "verification table below" reference — either add the table to the spec or fix the `[HARD]` wording to say it is produced at design open.
5. **[L4-1]** Fix the REQ-EXT-09 test path (`tests/conformance/test_extractor.py:894-899`) everywhere it is cited.

---

## Resolutions

*(Filled in during Stage 5 as the human resolves findings. Keyed by ID.)*

- **[L1-1]**
- **[L1-2]**
- **[L2-1]**
- **[L3-1]**
- **[L3-2]**
- **[L3-3]**
- **[L3-4]**
- **[L3-5]**
- **[L4-1]**

---

**Verdict:** APPROVED-WITH-CHANGES (Revise)

**Must-fix list:**

1. **Fix the `SatisfyRequirementUsage` metamodel error** (L1-1). Correct line 100 and lines 125–131; propagate to rows 1/6/7. Choose resolution (a) satisfy-excluded-and-documented or (b) exclude-except-satisfy. A `[HARD]` requirement cannot rest on a false hierarchy.
2. **State and sequence the snapshot format-bump re-capture** (L3-1, L3-2). Say plainly the bump re-captures all 20 committed snapshots (license-gated, load-gated), correct the "byte-identical except version bump" phrasing, and name the ordering/ownership against Items 1 and 2.
3. **Carry the settled checkout in and add the dirty-tree companion-branch procedure** (L1-2, L3-3): target `/home/reid/1cfe/agentic-mbse`; branch from current HEAD, stage only Item 4's files, no stashing.
4. **Reconcile the "verification table below" reference** (L3-4) with the Next Steps deferral to design open.
5. **Fix the REQ-EXT-09 test-path citations** (L4-1) to `tests/conformance/test_extractor.py:894-899`.

Recommended (not blocking): make row 5's silent-on-clean (acyclic-passes) pin explicit (L3-5); consider whether serialization is a clean split point if the format-bump cost dominates the estimate (L2-1).

**Next Steps:** Once resolutions are recorded here, re-run `/_my_spec` (or return to the spec-agent session) and point it at this review to incorporate. The reviewer does not edit the spec. After the metamodel fix in particular, re-check that rows 1/6/7 and the `[HARD]` semantic line all read consistently with the chosen satisfy resolution.

ARTIFACT: .project/active/subtype-enumeration/spec-review.md
