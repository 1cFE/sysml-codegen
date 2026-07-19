# Independent Audit: GAP-CLOSE Epic Completion Claims

**Verdict:** Certified-partial status CONFIRMED — the epic's own record is essentially truthful.
One checked box is false of the pushed ref (companion whitespace gate); two bookkeeping items are stale.
**Epic remains Needs Work**, exactly as recorded: external F1 normalization open, full-suite leg of the
wave gate open.
**Audited:** 2026-07-18 (independent re-audit; five verification subagents, one per item)
**Branches/commits:** sysml-codegen `constraint-exec-epic` @ `512786c` (pushed = origin);
agentic-mbse PR ref `origin/constraint-exec-epic` = `54a95d2` (local branch deliberately at `4ed2a07` + dirty tree)
**Prior record audited:** `.project/active/gap-closeout/audit.md` (the epic's own certification)

---

## Summary

Every item-level completion claim was re-verified against code with fresh test runs, not by trusting
records. Items 1–4 confirm cleanly. Item 5 confirms except for one falsely-checked criterion and the
honestly-open wave gate. The pushed companion commit `54a95d2` is byte-identical to the local
dirty-tree gap-close changes with zero contamination from the unpushed `4ed2a07` orchestrator work.
The item decomposition covers all ten findings and all nine hygiene notes from the source research;
out-of-scope filings (`[CONSTRAINT-ARCH-UNIFY]`, CI, `[ANON-ELIGIBLE-KEY]`) are intact.

Separately, the PR-wave code review run alongside this audit found new defects on the PR branches —
including two High profile defects and a reserved-name generation family. Those are **not** GAP-CLOSE
completion failures (they were never in the epic's scope) but they bear on the same merge decision.
See `.project/research/20260718-192048_constraint-exec-pr-wave-code-review.md`.

## Item verdicts

### Item 1 — Runtime contract (F1/F2): CONFIRMED
- F2 guard (`assert_unique_predicate_function_names`, `src/sysml_codegen/generation/modules.py:105-128`)
  compares the actual emitted names, so every sanitization collapse class is covered by construction.
  It runs in the CLI preflight before any output mutation on both live and from-snapshot routes, with
  an in-compiler recheck. Opposite-verdict collision tests are genuine; 60 + 9 focused tests green;
  no bypass path found.
- F1 codegen leg: native propagation characterized at compiler and production-wrapper level (2 execution
  tests green in the companion venv); docstring narrowed to the DP4 promise. External teax leg correctly
  open in spec, epic, and BACKLOG.
- Soft spot (non-blocking): the checked "no constraint report / partial evidence" criterion rests on
  teax serial-executor abort semantics by inference; no pipeline-level raising run asserts report
  absence in this repo.

### Item 2 — Lowering integrity (F4/F5): CONFIRMED
- Warning-before-halt ordering, anonymous identity mint (128-bit, portable location), collision error
  text, and route parity (live/relocated/snapshot exact warning bytes) all verified; pre-fix defects
  confirmed present at parent `6db3212` by reading the baseline code. 114 licensed focused tests green,
  fixture-clean, migration guard intact.
- New defect found (registered in the research doc, R-8): the F4 warning pre-pass can itself raise on
  an out-of-root anonymous referent, masking the BLOCK diagnostic and suppressing warnings — the F4
  guarantee is conditional on referent mapping succeeding.
- Residual (low): two anonymous statements at the identical file/line/column still hard-collide
  (deterministic hash, no per-sibling entropy).

### Item 3 — Boundary guards (F6/F9): CONFIRMED
- F6 initialization-state guard verified including defaulted-field candidates; rejected assignments
  leave models unchanged/serializable (probe + tests). F9 dir-symlink rejection verified for internal,
  escaping, nested, chained, and manifest-recorded cases, without descending. RED evidence overlay
  hash-matched and re-run (4/4 at pre-fix, green at HEAD); 58 + 53 + 6 tests green.
- New defect found (research doc R-10): dangling symlinks pass verification silently — the same threat
  class F9 closed, reopened via a mutable-target link. Latent, not-currently-live: `Field(exclude=True)`
  would break the complete-candidate premise; an assigning after-validator would recurse; in-place
  container mutation is out of the guard's scope by spec.

### Item 4 — Profile totalization (F7/F8, companion): CONFIRMED
- Pushed `54a95d2` byte-identical to the local gap-close changes (tracked and untracked files);
  no orchestrator contamination. F7 arity gate, F8 dimension-before-admit ordering, promoted-diagnostic
  rewrite (`block_non_numerical_containment`), codegen test sync, no-v4 ruling, and the 0.1.1 bump all
  verified in code. 116 companion + 3 licensed codegen sync tests green. Arity coverage confirmed total
  over the five connectives; no well-formed-input decision change found.
- Cosmetic: the contradictory-fact block reuses `block_derived_unit_unsupported`, which describes a
  different condition than it names.

### Item 5 — Closeout + wave gates (F3/F10/hygiene): CONFIRMED except one box
- F3: companion 0.1.1 (pyproject + `__version__`), codegen floor `agentic-mbse>=0.1.1`, main's companion
  is 0.1.0, resolver evidence recorded both directions — a metadata-only pre-v3 pairing is genuinely
  impossible.
- F10: all three durable surfaces teach v3 (spot-grepped); doc 27's lockstep claim corrected.
- Hygiene: exports, fingerprint docstring, loader comment, D5 reason+message warnings, validated teax
  discovery — all confirmed.
- **FINDING (false box):** Item 5's criterion "`git diff --check` clean on both repos' branch ranges"
  is `[x]`, but `git -C agentic-mbse diff --check main...54a95d2` exits 2
  (`.project/completed/20260713_executable-profile/plan.md:520: new blank line at EOF`). The cure
  exists only in the uncommitted local worktree; `54a95d2` did not include it. Trivial content,
  but the checked claim is false of the pushed ref. Same clause affects the epic's "artifact
  whitespace is clean" box.
- **FINDING (gate honesty, correctly open):** the codegen licensed full suite has never run at final
  commit `512786c`; the 2,516-pass evidence is from the pre-cure dirty candidate at `6db3212`. The
  records word this honestly and the conjunctive wave-gate box is correctly `[ ]`.
- **FINDING (evidence gap):** the fresh companion isolated run at `54a95d2` ("1,506 passed / 1 skipped /
  5 deselected") exists only in the PR #11 comment; the delta vs the certified 1,525/1/33 is not
  explained in any repo artifact.
- **FINDING (stale prose):** the committed `CURRENT_WORK.md` in `512786c` still says "No commit, push,
  PR comment, or close action occurred", and the epic's Next Action still says to run the partial
  pre-PR — both overtaken by `512786c` itself, which IS the executed partial wave (pushed, both PRs
  commented 2026-07-19T00:59/01:10Z with the F1-open caveat and the #11-first merge-order note intact).

## Epic-level assessment (against source documents)

The item decomposition fully covers the shaping intent of the two source research docs: F1→Item 1
(partial, external leg booked), F2→Item 1, F4/F5→Item 2, F6/F9→Item 3, F7/F8+hygiene-9→Item 4,
F3/F10+hygiene-2/4–8→Item 5; hygiene-1 (C901) and hygiene-3 (CI) explicitly out of scope with filings.
The owner's F1 ruling is respected: no arithmetic guards were added, propagation is characterized, and
no one claims F1 or epic completion. Merge order (#11 first) is load-bearing and stated on both PRs.

## Certification

- Epic Success Criteria boxes: all states verified correct as marked, with one exception — the
  "artifact whitespace is clean" clause inside the F10+hygiene box (and Item 5's diff-check box) is
  refuted for the companion pushed range. Annotated in the epic file.
- Wave-gate box `[ ]`: correct, and now partially stale as worded — the pushes/comments/merge-order
  legs are DONE; only the full-suites-at-final-commits leg remains.
- No checkbox was flipped by this audit; one correction annotation was added to the epic file.
  Nothing was committed or pushed.

**Not checked:** full licensed suites (deliberately — the gap is itself a finding); the teax evaluator
(does not exist to test); merge behavior; the four unrelated-workstream files in `4ed2a07`;
`.project/` narrative files beyond those cited; re-execution of the frozen RED overlay ceremonies
(corroborated structurally against baseline code instead, except Item 3's, which was re-run).
