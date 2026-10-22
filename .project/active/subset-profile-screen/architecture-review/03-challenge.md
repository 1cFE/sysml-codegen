# Architecture review, part 3: adversarial challenge

**Written:** 2026-10-20. **Reads:** `01-current-system.md` (facts) and `02-alternatives.md` (options, recommends C + E1 + G). **Revisions:** sysml-codegen `3ffcbc59`, agentic-mbse `e268357f`, dc3 `60b44d5` with baseline `808464d` copied to the session scratchpad. No repository code was changed. Three read-only probes were run against codegen at `3ffcbc59`; their scripts are in the session scratchpad (`e1_step1_probe.py`, `time_prep_only.py`, `b1probe/`).

## Verdict first

The recommendation is **sound with changes**. Retiring the hand-kept rule list is defensible, and C (L6 asks the generator) is the right direction. But the case for it rests on one claim that is wrong: that E1 ("collect every problem within each step") gets dc3 to about three runs with no stubbing. Measured and read from the code, E1 as scoped would show dc3's cheap expression problems first and hide the three structural ones (B1-B3) behind them. Those structural ones are the whole of dc3's cost. The rule list is the only piece in either design that shows problems from every generator step in one run, and document 02 calls that gap "small". It is the gap.

Separately, both documents overstate what dc3's incident cost. The stop-at-first-error work took about 20 minutes of agent time, and the in-place rewrite about an hour. The response so far is four merged items and about 5,700 lines of production code. Any further spend, including the 12-20 days document 02 proposes, should be weighed against that.

## 1. The diagnosis

**One-error-per-run is overweighted in document 02.** Document 02 says the one-at-a-time answers "turned an inventory into a multi-day investigation" (02, section 1, point 3). The session that ran T-001 (dc3 session `63616b8e`, `~/.claude/projects/-home-reid-src-dc3/63616b8e-….jsonl`) shows the first `sysml-codegen generate` call at 20:26 UTC on Oct 13, the G-000 log cited at 20:39, the T-001 inventory file at 20:40, and the sequential probe logs and calc-usage probe cited at 20:46. The grounding commit `7fb0cd9` is 20:47. That is about 20 minutes of agent wall time, with subagents in parallel. Document 01's "one evening" is closer; even that is generous. I did not measure the owner's own time.

**The rewrite was also short.** WI-008's spec, design and review commit is 21:07 (`c2bda1b`), and its integration audit is 22:06 (`be457a4`). The cost the epic is built around is real, but it is hours of agent work plus the loss of an audited native idiom (fail-closed guards became non-fatal verdicts on the generated path, `T-001-blocker-inventory.md` B1). It is not ten days, which the epic itself already disowns (`epic:53`).

**What actually misled dc3 was L6, not the generator.** The first goal never ran the generator. It parked generation on L6's output: "L6 String extraction and Boolean predicate/containment unsupported … park generated/study readiness with exact failure evidence" (dc3 `conversion-path-efficiency/trail.md:310`), and the closing note lists "the L6 String-default and Boolean predicate/containment extraction seam (11 issues)" as the thing to repair "before generated packages or studies run" (`:338`). The L6 section was then titled "Architecture & Pipeline Readiness" (dc3 `.project/active/toolkit-update/evidence/after-validate.txt:67`). So the team read a short, specific L6 failure list as the full size of the generation gap. Document 02 lists "the feedback came late" first. The evidence says the feedback came on time and was wrong. That matters for C: under C, L6 would carry the generator's answer, which is correct but, without cross-step reporting, also short.

**Missing from both diagnoses:** the owner's Oct 5 amendment explicitly allowed parking generation (`goal.md:67`). Any "early generator probe" rule in G changes what a parked-generation goal must do. That is a workflow rule over an owner-granted permission, so it is an owner decision, not an Item 6 detail.

**Minor:** document 01 says L6 at the baseline "failed only on B8-type constraint codes". The same output also counts `L6_DESIGN_ATTR_UNEXTRACTABLE: 3` (B7) (`after-validate.txt:82`). Document 02's "L6 caught 2 of the 8 categories (B7, B8)" is the correct reading.

## 2. E1 does not deliver what document 02 says

Document 02 says B1 and B2 "fail in step 4, where errors are already collected", and that E1 gets dc3 to "about three 15-second runs with no stubbing" (02 section 2 and section 5). Three things are wrong.

**B1 is not collected.** Every constraint usage goes through `_owner_kind` (codegen `elaboration/elaborate.py:1481`), which raises at once for an owner kind outside its closed map (`:863-890`). A calculation usage is outside the map. The collecting path that document 02 points at, `_halt_on_error_dispositions` (`:1670-1710`), is never reached for B1. I confirmed this with a probe: a model with three calc-usage-owned assertions (two in one calc usage, one in another) refuses at HEAD with **one** refusal item, `SI_CONSTRAINT_UNATTACHED` / `elaboration_constraint_owner_unmapped`. dc3 has 164 of these.

**B2 fails in step 3, not step 4.** T-001 records sequence inputs as `SI_MULTIPLICITY_UNSUPPORTED` from `occurrence.py` `_multiplicity_indices` (`T-001-blocker-inventory.md`, row B2).

**Step 1 alone shows only the cheap problems.** I ran the step-1 loop read-only with a per-site catch (`e1_step1_probe.py`, which calls `_enumerate_sites` and `_acquire` from `expression_evidence.py:238-254`). On dc3 baseline it found 632 expression sites and 28 refusals: 23 unsupported function calls (`product` and `size`, B4/B5) and 5 missing targets (the conditionals, B6). All 28 are what the T-001 round premise called "expression forms with identical rewrites", the premise T-001 proved false. Under E1 the modeler's first answer would reinforce that premise.

**"No stubbing" is wrong.** E1 stops after the first step that found problems. To see step 3 the modeler must first fix or stub all 28 step-1 problems, and B4/B5 are bound to B2 while B6 has no identical rewrite (T-001 table). So the modeler makes design changes before seeing the structural blockers. Then step 3 (B3 and B2), where T-001 runs 3 and 4 hit the same site twice (`rack_power`: unresolved upper bound, then range after bounding), which no collector removes. Then `SI_REDEFINITION_INVALID` (run 5), then B1 one usage at a time. A realistic count is four or more runs, each requiring real model changes. The rule list did it in one run with no changes.

**E1's scope leaves out first-error stops that matter.** E1 covers steps 1, 3 and 5. Document 01's table also lists calc-def compilation (`elaborate.py:767-786`), constraint-profile association (`:661-700`), the slot index (`:609`), the constraint-owner check (B1), and projection (`project.py:150-165`) as stopping at the first problem. The 5-8 day estimate costs none of them. `occurrence.py` alone has 34 `raise` statements. I would put E1 with B1 included at 8-12 days, with the same ±50% document 02 applies.

**Collecting B1 can change acceptance.** `_owner_kind` raises for every calc-usage-owned constraint usage, asserted or not, because it is called before the asserted/unasserted split (`:1479-1498`). Turning that raise into a disposition, which is how B1 would join the collecting path, risks letting an unasserted calc-usage-owned constraint through, and it changes the refusal's site reason from `elaboration_constraint_owner_unmapped` to `elaboration_asserted_constraint_unattached`. The first is RG-1 territory, and the second changes the reported first refusal. This is inferred from reading, not tried.

**Where E1 is safe.** For a model that builds, nothing raises, so collecting cannot turn a build into a refusal. For a refused model, keeping the existing raise order makes the first item the same as today's. The risks are elsewhere: every one of the 169 refused corpus records changes shape (`refusal_records.json`), the report and `check` read `refusal.items` (`cli/report.py:105,167`), and later preflights running on a graph that failed an earlier preflight may add internal-defect noise. Downstream of a failed step, nothing is reported, which is honest (epic principle 5) but is exactly why E1 cannot replace cross-step visibility.

## 3. Option C's hidden costs

Most of the worries in the brief turn out smaller than they sound. Two do not.

- **Runtime is a wash, and better on refused models.** Measured on this machine, interpreter start plus imports is 0.04 s. The generator route alone takes 0.50 s wall on dc3 baseline (load 0.39 s, `prepare` 0.01 s) and 14.75 s on the repaired tree (`prepare` 14.27 s). Today's list takes 12.6-17.2 s on the same trees (01 section 3). So C does not slow L6, provided `check` stops running the screen. This only holds after 2b's screen half is removed (02 step 1).
- **License in a child process is fine.** agentic-mbse calls `load_dotenv()` into the process environment (`cli/__init__.py:333-334`), and a child inherits it. Not run end to end.
- **Version skew does not "disappear".** Document 02 says C "always uses the generator version the project will actually run". That holds only if L6 finds the codegen in the project's own environment. A PATH lookup can find a global or `uvx` install instead. The runner should prefer `sys.executable`'s sibling `sysml-codegen`, then a configured path, and print the codegen version it used.
- **Windows and CI.** `shutil.which` handles `.exe`. Neither consumer runs validation in CI today: dc3 has no `.github`, and fusion-tea's only workflow is `notify_visualization.yml`. Low risk now.
- **AI skills run L6 often.** 23 references to `agentic-mbse validate` across shipped skills and templates. With codegen installed and the target unset (dc3's case), C would run the generator on every L6 run. That costs about what the list costs today.
- **"No answer without codegen installed" is acceptable for both consumers** (both install it, dc3 from `b2c853f` on Oct 3, fusion-tea by pin). It is untested for a standalone agentic-mbse user who reads the shipped generator-subset guidance and has no generator. That user can't generate either, so the loss is small.
- **Real cost 1: C answers late in the steps, like `generate`.** C adds nothing to cross-step visibility. Everything in section 2 applies.
- **Real cost 2: the deletion list breaks Item 4.** `parameter_redefinition_extraction.py` imports `safe_location` from `occurrence_extraction` (`:39`) and `_element_ref` and `_IdentityError` from `subset_extraction` (`:53`). That module feeds `validation/positional_check.py:25`. Document 02 says "keep Item 4: all of it" and also "delete `subset_*`". The dependence is shallow (two helpers), so moving them is cheap, but it must be in the plan.

**Document 02 underrates D (a Python API).** It says D is for "later, only if a consumer asks". Both consumers already import codegen internals: fusion-tea `tests/ife_execution.py:5` and `tests/test_codegen_teax_acceptance.py:12` call `run_codegen`; dc3 `exploration/ac_dc_baseline/studies/study_route.py:20` imports `sysml_codegen.study`. The "public surface constrains refactoring" cost is already being paid without a promise. A side effect worth knowing: on this branch `run_codegen` runs the screen after every generate, refused or not (`cli/__init__.py:503-523`), so fusion-tea's test suite would pay about 3 s per `catf_mfe` model (01 section 3) once it moves to this codegen.

## 4. The honest case for keeping the rule list

- **It sees across steps.** It reported B1-B8 in one dc3 run, including the 164 B1 assertions, because it does not need step 1 to pass before looking at step 4 (01 section 6). Nothing in C + E1 does that. Only E2 (continue across steps, 15+ days, high risk) does.
- **It has never refused a model the generator builds** on the corpus (0 `screen_refuses_generator_builds` of 136 disagreements). Where it speaks, it is right. Its weakness is silence (129 of 169 refused corpus cases), and the L6 text says so.
- **It carries remedies per pattern**, which C has to rebuild (document 02 proposes one remedy per `SiteReason`, 87 members, of which only the 71 public-capability ones need user-facing text).
- **Its speed argument is the wrong way round.** On refused models the generator answers in 0.5 s and the list in 17 s. Speed is not a reason to keep it.
- **It has an expiry date the documents do not name.** Two owner-held generator changes are queued: `[CALCDEF-GATE-IMPLEMENTATION]` and `[SCALAR-FUNCTION-VOCABULARY]`. They would make the `calc-owned-assertion` and `invocation-callable` rules wrong in the bad direction: the list would refuse models the generator builds, and modelers would rewrite good models. So "freeze the list" (02 question 2) is only safe until the first of those lands.

So keeping the full list is mostly sunk cost. Its one unique capability, seeing the structural problems in one run, is real, and it covers exactly three families: calc-owned assertions (B1), sequence inputs (B2) and open part multiplicities (B3). Those are also the three that guidance alone can prevent.

## 5. Options both documents missed

- **G + plain `check`, without the L6 runner.** The workflow gate in G already runs `sysml-codegen check`. Doing C on top adds JSON output, a subprocess runner and L6 wording changes (3-5 days) to show the same answer inside L6. "L6 checks the SysML; `check` asks the generator; the workflow runs both when the project targets generation" is simpler to explain than "L6 runs the generator for you". C can follow if modelers keep missing the gate.
- **A short, static list of the generator's structural limits in the guidance.** Three sentences: assertions go on parts, not calc usages; part counts are exact; calc inputs are scalars. If dc3's modeler had read these on Oct 4, B1-B3 would not have been built. This is G's cheapest piece and could ship before anything else.
- **A project test that says "this model generates".** fusion-tea already does this with `run_codegen` in pytest. A `tests/models/test_generates.py` template, installed when `execution-target = "generated"`, would put the generator's answer into the project's normal test run with no L6 change. It depends on D becoming a supported entry point.
- **E1 step 1 alone, now.** Half a day (02 estimate, and the probe shows the loop is independent per site). It turns dc3's first three runs into one. It is worth doing whatever else is chosen, as long as nobody claims it solves cross-step visibility.

## 6. Spot checks

Document 01 (all confirmed unless marked):

- 136 disagreements: 95 + 33 + 1 `generator_refuses_screen_silent` (129) and 7 `code_unmapped`. Confirmed.
- 246 corpus cases. Confirmed. 169 refused, 77 generated.
- 491 site-account rows and the role counts. Confirmed. Cross-tab: public capability is 17 in scope, 40 explicit follow-up, 14 handled elsewhere.
- Load 0.38 s and `prepare` 0.01 s on the baseline. Reproduced as 0.39 s and 0.01 s.
- About 3,700 and 5,700 lines of production code. Confirmed from `wc -l` (5,592 for the eleven listed files, plus `fact_refs.py` and `invocation_allowlist.py`).
- `subset_profile.py:125` version string, `execution_target.py:176-192` table, `pyproject.toml:24` and `:121-122`, `prepare.py:95-113`, `refusal.py:57-60`, `report.py:204-210` quirk. All confirmed.
- **Partly wrong:** "L6 failed only on B8-type constraint codes". B7 was also counted (section 1).
- **Right, but easy to misread:** the table row "Constraint dispositions … Collects" is true of that function, but B1 never reaches it.

Document 02:

- 169 refused cases, silent on 129, split 33 / 95 / 1. Confirmed.
- 87 `SiteReason` members (`diagnostics.py:40`). Confirmed.
- `elaborate.py` 2,857 lines, `occurrence.py` 1,072, `run` at `:787`, `_finish_readiness` collecting at `:2822-2832`. Confirmed.
- The five probe codes in sequence. Confirmed against `sequential-gen{1..5}.txt`.
- **Wrong:** "B1 and B2 fail in step 4, where errors are already collected" (section 2).
- **Wrong:** "about three runs … no stubbing" (section 2).
- **Wrong:** "a multi-day investigation" (section 1).
- **Mislabeled:** "the list takes 18.1 s". 18.1 s is the whole L6 run from Item 3's evidence; the list alone took 17.2 s (01 section 3).
- **Overstated:** "about 54 of the 71 modeler-reachable sites have no rule". 40 are explicit follow-ups and 14 are handled elsewhere, and document 01 says reachability was not checked. "9 rule families against 71 sites" compares families with sites.
- **Understated:** "about 30 test files (2,866 lines)". 33 files and 2,866 lines, plus 2,992 lines of helpers in `tests/helpers/subset_profile/`.
- **Missed dependency:** the occurrence port and `subset_extraction` are used by Item 4 (section 3).

## 7. Changes I would make to the recommendation

1. **Correct the E1 claims.** State that E1 shows one step's problems per run, that dc3 would need four or more runs with real model changes between them, and that the structural problems arrive last. Add calc compilation, constraint association and the constraint-owner check (B1) to E1's scope or say they are out, and re-estimate.
2. **Treat B1 collection as an owner gate.** It touches `_owner_kind`'s closed map and may change what refuses.
3. **Ship the structural-limits guidance first.** It is the cheapest fix for the actual dc3 failure mode, and it does not depend on any code.
4. **Make C optional, after G and plain `check`.** If kept, the runner finds codegen in the project's own environment and prints the version it used.
5. **Set the list's retirement date by the queued generator changes,** not by the side-by-side run. Freeze it now. Delete it, or at least its `calc-owned-assertion` and `invocation-callable` rules, before `[CALCDEF-GATE-IMPLEMENTATION]` or `[SCALAR-FUNCTION-VOCABULARY]` merges.
6. **Move Item 4's two helpers out of the list modules** before deleting anything.
7. **Remove the screen from `generate` regardless of the decision.** It adds 17 s to a refused dc3 run that takes 0.5 s without it, and it reaches consumers through `run_codegen`.
8. **Restate the cost of the problem next to the cost of the fix.** About 20 minutes of agent inventory and an hour of rewrite on one consumer, against 12-20 more days.

## 8. Questions only the owner can answer

1. **How much did dc3's incident cost you, not the agents?** The session record shows about 20 minutes of agent inventory and an hour of rewrite. If your own cost was similar, the cheapest options (guidance, E1 step 1, plain `check` in the workflow) may be enough, and the rest of the epic should shrink. If it was days of your attention, the cross-step capability is worth more.
2. **Is seeing every structural problem in one run a requirement?** If yes, only the rule list (for its families) or E2 delivers it, and retiring the list loses it. If guidance that prevents B1-B3 is enough, retire the list.
3. **Is collecting more refusals per run your call under RG-1?** It does not change which models build if done carefully, but it changes every refusal record, and collecting B1 touches a closed map whose raise currently refuses unasserted calc-usage-owned constraints too.
4. **Should a parked-generation goal still run one generator check early?** Your Oct 5 amendment allowed parking. G would require a probe anyway, which narrows that permission.
5. **Which comes first, the queued generator changes or the list's deletion?** If either owner-held change lands while the list is live, the list starts refusing models the generator builds.
6. **Should codegen promise a Python entry point (D)?** Both consumers already import `run_codegen` and `sysml_codegen.study`. A promise would let a "this model generates" project test ship as a template.

## Not checked

- I did not run L6, the test suites, `generate` end to end, or `check` on fusion-tea.
- I did not prototype E1 beyond the read-only step-1 loop. Step 3 and later run counts are read from code and T-001 logs.
- I did not find where `SI_REDEFINITION_INVALID` in run 5 is raised (candidates in `occurrence.py:58` and seven sites in `elaborate.py`), so whether E1 would collect it is unknown.
- Session timestamps measure agent wall time from first mention, not the owner's time, and subagent transcripts were not read.
- I did not run L6 as a child process to confirm license inheritance end to end.
