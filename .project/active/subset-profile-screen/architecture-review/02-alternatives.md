# Architecture alternatives: how a modeler learns early that the generator will refuse a model

Date: 2026-10-20. Author: architecture review agent, first-principles pass. No code was changed. Measurements were taken on isolated copies of dc3 under the session scratchpad.

## The answer first

Retire the hand-kept rule list. Replace it with three smaller pieces:

1. The validator runs the real generator, in its no-write mode, whenever the project says it targets generated code (option C).
2. The generator lists every problem it finds in each of its steps, instead of stopping at the first one (option E, first level).
3. The modeling guidance teaches only patterns the generator's own tests show it builds, and the modeling workflow runs the generator's check early, as soon as a project targets generation (option G).

In plain words: "When a project plans to generate code, the validator asks the generator itself and shows its answer. The generator reports every problem it finds in each step, not just the first. The guidance only teaches patterns the generator's tests prove it builds."

The rule list catches dc3's eight problems in one run today, and that is real value. But it is a second copy of the generator's decisions. It covers 9 rule families out of about 71 modeler-reachable refusal sites, and it is silent on 129 of the 169 refused corpus cases. Keeping it honest needs a permanent cross-repository test system. The things it buys (an answer without the generator installed, everything in one run) are cheaper to get in other ways. The main cost of the recommendation is that a project with no generator installed gets no generation answer at all. Only the owner can accept that, and it is the first question at the end.

## 1. What the real problem was

I read dc3 T-001 (`work/orchestration/goals/study-ready-baseline/evidence/T-001-blocker-inventory.md`), the five sequential probe logs, and the epic's "Why This Epic?" section. My reading is that dc3 had three separate problems. The epic treated them mostly as one ("the validator doesn't know the generator's rules").

1. **The feedback came late.** sysml-codegen was installed on October 3. The owner's October 5 amendment explicitly parked generation, and nobody ran the generator against the models until T-001 on October 13. By then the three structural idioms (B1 calc-owned guards, B2 variable-length sequences, B3 open part counts) were built into every design and had been audited. Any checker only helps if someone runs it while those choices are still cheap. Nothing in the workflow made that happen.
2. **The guidance taught refused patterns.** The epic traces the calc-owned assert comment "Executes" (agentic-mbse `dcb187ba`) and several conditional and function examples that were never qualified when the generator's supported subset narrowed. The modeler did what the docs said. A checker catches this after the fact. Correct guidance prevents it.
3. **The only authoritative tool answered one problem per run.** Each of the five probe runs reported exactly one refusal (`SI_EVIDENCE_INCOMPLETE`, then `size`, then multiplicity unresolved, then range, then redefinition). To see the next one, the coordinator had to stub out the last. B1 was found only by a separate probe. That turned an inventory into a multi-day investigation.

Two smaller facts matter as well. L6 caught 2 of the 8 categories (B7, B8). Its output suggested broader coverage than it had, which is a presentation and honesty problem. And B1-B3 have no identical rewrite, so even perfect early detection would have forced a design choice: either change the idiom or ask for generator support. Detection does not remove that choice. It moves it to day one.

The current design (the rule list) addresses problem 3, and problem 1 only for projects that run L6. Problem 2 is handled separately by Item 5. Problem 1 also needs a workflow step, because dc3 ran L6 and the parked-generation decision would have downgraded the findings anyway.

## 2. Facts that shape the options

These are measured or read from code, not estimated.

**How the generator refuses.** The generator's route is a fixed sequence of steps (`sysml_codegen/cli/prepare.py`, `PreparationStep`, and `orchestration/elaborated_pipeline.py:330`):

1. Read every expression in the model and check its references and function calls (`elaboration/expression_evidence.py:237`, `build_expression_evidence_inventory`). This loop raises on the **first** bad expression.
2. Check constraint extraction findings (`elaboration/extraction_screen.py`). This already reports **every** blocking finding at once.
3. Build the tree of part instances (`elaboration/occurrence.py:921`, `build_occurrence_index`). This raises on the **first** bad multiplicity (`occurrence.py:825-910`).
4. Build the calculation graph (`elaboration/elaborate.py:787`, `run`). Most refusals here are **already collected**: `_diagnose` appends to `graph.diagnostics` and `_finish_readiness` raises all readiness findings together (`elaborate.py:2822-2857`). Internal invariant errors still raise at once.
5. Projection, then nine generation checks in order (`prepare.py:237`, `prepare_graph`). Each check raises on its first problem, and the first failing check ends the run.

So the generator already collects many errors inside some steps. It stops at the first error in steps 1 and 3, and between steps. The plural plumbing exists: `ElaborationDiagnosticError` carries a tuple of diagnostics.

**Where dc3's eight categories fall in that sequence.** B4, B5, B6 (function calls and conditionals) fail in step 1. B3 fails in step 3. B1 and B2 fail in step 4, where errors are already collected. B8 is in step 2 or 4. With step 1 and step 3 collecting all their errors, dc3's baseline would have needed about three runs instead of five-plus runs with stubbing. I did not run this; it is read from the code.

**How big the modeler-facing refusal surface is.** The Item 2a site account (`tests/expectations/subset_profile/site_account.csv`) lists 491 raise sites. Of these, 71 are classed as public capability refusals, meaning a modeler can reach them by a modeling choice. 179 are internal invariants, 92 are snapshot integrity, 64 relay plumbing, 55 environment, 14 malformed input and 16 unknown. Only 17 sites are in scope of the list's rules. The codegen side already names 87 refusal sites with stable reasons (`SiteReason`, `elaboration/diagnostics.py:40`).

**How well the list matches the generator.** On the 246-case corpus, 169 cases are refused by the generator. The list is silent on 129 of them (`tests/expectations/subset_profile/disagreements.json`): 33 are checks only the generator can make by design, 95 are known gaps, 1 is pending an owner decision. Seven more cases have a generator code the list cannot map. These cases were built to exercise refusal sites, so they overweight rare refusals compared with real models. On dc3's baseline the list does well: it reports 164 calc-owned assertions, 29 binding sources, 23 unsupported function calls, 15 part multiplicities, 5 conditionals, 1 string omission and 6 unconfirmed predicates, in one run.

**Speed.** On dc3's baseline (808464d, 23 files), loading takes 0.4 s, the generator refuses in under 0.1 s (it stops at step 1), and the list takes 18.1 s. On dc3's repaired tree (60b44d5, which generates), the full generator route takes 14.3 s and the list 12.5 s. L6 at level 6 takes about 18 s on the baseline. So running the generator costs about the same as running the list. Neither is fast enough to run on every keystroke in an editor.

**Some generator decisions already live in agentic-mbse and are not copies.** The generator calls agentic-mbse's `reference_use.inspect_reference_uses` (the "only `sum` is supported" decision behind B4/B5), `executable_profile` (constraint predicates, B8) and `constraint_extraction`. When L6 reports those, it runs the same code the generator runs. The copied logic is mainly the part-instance tree and the decisions that depend on it: `occurrence_extraction.py` (739 lines, a port of codegen's `occurrence.py`) and `subset_profile.py` (1,481 lines).

**Size of the list.** In agentic-mbse: `subset_profile.py` 1,481 lines, `occurrence_extraction.py` 739, `occurrence_facts.py` 433, `subset_facts.py` 339, `subset_extraction.py` 546, `subset_coverage.py` 107, `subset_advisories.py` 153, `conformance_case.py` 312, `subset_profile_rules.toml`, 154 packaged conformance cases, and about 13 test files. In codegen: `subset_screen.py` 181, `subset_profile_adapter.py` 157, about half of `cli/report.py`, and about 30 test files under `tests/conformance/subset_profile/` (2,866 lines), some of which test the generator rather than the list.

## 3. The options

Each option has a plain explanation of at most three sentences with no project jargon, as the owner asked. Where an option cannot be explained that way, I say so and count it against the option.

### A. Status quo: shared rule list in agentic-mbse, used by L6, also printed by `sysml-codegen check`

**Plain explanation.** The toolkit keeps its own written copy of the generator's rules and checks models against that copy, so the validator can warn without the generator installed. The generator's no-write check also prints what the copy says, next to its own answer. A large test suite in the generator's repository runs both on the same models to keep the copy in step.

That passes the test, but only because it hides the hard part. The honest version needs a fourth sentence: the copy covers some rules, says nothing about the rest, and its silence does not mean the model is fine. Users read silence as approval, which is why L6 needs "Coverage limit" lines and a `CLEAR is relative` disclaimer. Counts against it.

**Parts and where they live.** Rules and decisions in agentic-mbse `sysml/subset_profile*.py` and `subset_profile_rules.toml`. The part-instance tree copy in `sysml/occurrence_extraction.py`. L6 presentation in `validation/subset_presentation.py` and `level6_architecture.py:1026`. Codegen's mapping in `subset_profile_adapter.py`, `subset_screen.py`, `cli/report.py`. The agreement test system in codegen `tests/conformance/subset_profile/` and `tests/expectations/subset_profile/`.

**Data flow.** Model files → agentic-mbse fact extraction → rule evaluation → L6 output. Separately, model files → generator route → refusal; the same load → rule evaluation → printed under the generator's answer. In CI: corpus cases → both → disagreement records checked against `disagreements.json`.

**Catches early.** All nine rule families in one run, without the generator installed, with remedy text. On dc3 that is B1-B8.

**Misses.** About 54 of the 71 modeler-reachable refusal sites have no rule. Anything a future generator change adds, until someone writes a rule. 129 of 169 refused corpus cases.

**Cost to build.** Done.

**Cost to maintain.** High and permanent. Every generator change that adds, removes or moves a refusal needs a coordinated change in two repositories: the rule, a case, the evidence pin, the agreement record, possibly the profile version. Two owner-held generator changes are already queued (CALCDEF-GATE-IMPLEMENTATION, SCALAR-FUNCTION-VOCABULARY), and each will need this. The part-instance tree is kept in two places with a permanent parity test (ADR 0001 end condition (ii)). Item 2a alone was estimated at 25-35 engineer-days. Closing the 95 known gaps would be a similar order of work again.

**Risks.** The copy drifts in either direction. If it refuses something the generator builds, modelers rewrite good models. If it is silent on something the generator refuses, modelers trust a clear result. Users read silence as approval, whatever the docs say. Each new generator capability is slowed by the two-repository change.

**Keeps.** Everything.

**Migration.** None.

### B. `check` shows only the generator's answer; L6 keeps the list

**Plain explanation.** The generator's no-write check reports only the generator's own answer. The validator keeps its copy of the rules, as in A. Simple to explain.

**Parts.** As A, minus the list printing in codegen `check` (`subset_screen.py`, the screen half of `cli/report.py`).

**Data flow.** As A, but `check` output is only the generator route.

**Catches and misses.** L6 the same as A. `check` reports one refusal per run, the same as `generate`. Before Item 2b, a modeler could get the same answer by running `generate` into a scratch folder. So `check` adds a clean exit code and no writes, nothing more.

**Cost to build.** Small, 1-2 days: delete the screen half of `check` and its tests (`test_assess_screen.py`, `test_shared_load_screen.py`, `test_report_form.py` in part).

**Cost to maintain.** Almost the same as A. The agreement test system has to stay, or the list stops being checked against the generator at all.

**Risks.** As A. This is a presentation choice inside A, not a different architecture. It removes the only place where a user sees the list and the generator side by side.

**Keeps and discards.** Discards the screen half of 2b. Keeps 1, 2a, 3, 4, 5.

**Migration.** Remove the screen call in `run_check` (`cli/__init__.py:126`) and its report lines.

### C. L6 runs `sysml-codegen check` when the project targets generation; retire the list

**Plain explanation.** When a project says it will generate code, the validator runs the generator in a mode that writes nothing and shows the generator's answer. If the generator is not installed, the validator says it could not check and how to install it. Simple, and the answer is the generator's own by construction.

**Parts and where they live.**
- Codegen: `sysml-codegen check --format json` prints a machine-readable result (exit code, each refusal's code, site reason, location, message, and the generator version). New, about 100 lines in `cli/report.py`.
- agentic-mbse: an L6 step that finds the `sysml-codegen` executable on the project's PATH or venv, runs it as a separate process with a timeout, parses the JSON and turns each refusal into an L6 issue. New, about 200-300 lines in `validation/`. No import of codegen, so ADR 0001 invariant 3 (no import) holds without a copy.
- The `execution-target` setting from Item 3 decides when it runs: `generated` runs it and refusals are errors; `native` skips it; unset runs it if installed and shows warnings.

**Data flow.** L6 → subprocess `sysml-codegen check --models <path> --format json` → generator route (load, prepare) → JSON → L6 issues.

**Catches early.** Everything the generator refuses, including the 33 generator-only checks and the 95 gaps, with zero drift. It always uses the generator version the project will actually run, so version skew between L6 and the generator disappears.

**Misses.** Alone, it shows one refusal per run (that is why E pairs with it). Nothing without the generator installed. Not editor-time: about 15 s on dc3.

**Cost to build.** About 3-5 days: JSON output, L6 runner, tool-missing and timeout handling, tests with a fake executable, docs and skill text.

**Cost to maintain.** Low. A small JSON format between two tools, kept stable with a version field. Nothing to update when the generator's rules change.

**Risks.**
- A project targeting generation without the generator installed gets no answer. That is honest, but it is a change from today, where L6 says something either way.
- Subprocess failures (wrong venv, missing license) must show as "could not check", never as a pass. Item 3's check-failure handling already makes that distinction.
- Remedy text currently lives in the rule list. It has to move to the generator (one remedy per `SiteReason`, 87 entries) or be lost.

**Keeps.**
- Item 2b: the read-only `prepare` route and `check` itself; this option depends on them. The screen half is removed.
- Item 2a: per-site reasons (`SiteReason`), the site account, and the corpus cases as plain generator regression tests (each case's expected refusal). Discards the agreement, disagreement and screen-mutation tests and the occurrence parity test.
- Item 3: the `execution-target` setting, root discovery and check-failure handling. The list presentation is replaced.
- Item 4: all of it. The positional binding check is about native meaning, not generator support.
- Item 5: the fence inventory and corrected examples. Its "render the doc from rule records" step changes source (see G).
- Item 1: discards the rule list, the part-instance tree copy and the rule evaluator. Keeps nothing of the decision layer, apart from the matrix of B1-B8 boundaries as documentation.

**Migration.** (1) Add JSON output to `check`. (2) Add the L6 runner behind `execution-target`. (3) Run both side by side on dc3 baseline, dc3 repaired and fusion-tea, and record the difference. (4) Move remedy texts into codegen keyed by `SiteReason`. (5) Delete the list and its tests in both repositories, supersede ADR 0001, and amend P-0001.

### D. Codegen exposes a Python API that consumer projects and tooling import

**Plain explanation.** The generator offers a function: give it a model folder and it returns the list of problems, without writing anything. A project's own tests or tools can call it directly. Simple.

**Parts.** `sysml_codegen.cli.prepare.load_source` and `prepare` already are this API in practice. Making it public means a stable module (say `sysml_codegen.api.check(paths) -> CheckResult`), documented return types and a compatibility promise.

**Data flow.** Consumer test or tool → import → `prepare` → result object.

**Catches and misses.** The same as C. It cannot be used by L6 itself, because agentic-mbse must not import codegen (ADR 0001 invariant 3; codegen ADR 0007).

**Cost to build.** 1-2 days to wrap and document. **Cost to maintain.** Moderate: a public Python surface constrains refactoring of `prepare` and the refusal types, which are still changing.

**Risks.** Freezes internal types too early. Two ways to get the same answer (CLI and API) can drift in small ways, such as destination checks or logging.

**Keeps and discards.** As C.

**Migration.** Optional, after C. Useful for a consumer's pytest suite ("this model must generate"), which dc3's study tooling could use. Not a replacement for C, because it does not reach L6 or the skills.

### E. The generator reports every independent problem in one run

**Plain explanation.** The generator checks a model in a fixed series of steps. Within each step it now lists every problem it finds instead of stopping at the first. It still stops after the first step that found problems, and says which later steps it did not reach. Simple at the first level. The second level, described below, is not.

**Two levels.**
- **E1, collect within each step.** Step 1 (expression check): wrap the per-expression loop in `build_expression_evidence_inventory` so each site's error is recorded and the loop continues. Then raise once with all of them. The sites are independent, so this is safe. Step 3 (part-instance tree): record a bad multiplicity, skip that part's subtree, continue with siblings, and raise once at the end, saying which subtrees were not checked. Step 4 already collects most refusals. Step 5: run the nine generation checks independently where they do not depend on each other, and report all failures. Only the constraint plan and coverage check depend on each other. `Refused` (`prepare.py:107`) changes from one refusal to an ordered list whose first entry is today's single refusal.
- **E2, continue across steps.** Carry on to later steps with the failing parts marked as unusable. This would have shown all of dc3's categories in one run. It needs every later step to handle missing parts without reporting false follow-on errors, across `elaborate.py` (2,857 lines) and `project.py`. I cannot explain how it decides what is safe to continue past in three plain sentences. That counts against E2.

**Parts.** All inside codegen: `elaboration/expression_evidence.py`, `elaboration/occurrence.py`, `cli/prepare.py`, `cli/refusal.py`, plus the snapshot route, which shares elaboration.

**Data flow.** Unchanged, except a refusal carries a list.

**Catches early.** Everything the generator refuses, several at a time. dc3's baseline would have taken about three runs under E1 (expressions; then multiplicities; then the calc-owned assertions and bindings, which are already collected), instead of five-plus with stubbing and a separate probe.

**Misses.** Under E1, problems behind an earlier step's failure. Problems under a skipped subtree.

**Cost to build.** E1 about 5-8 days, including tests and the refusal-record change. Step 1 is half a day. Step 3 is 2-3 days. Step 5 is 1-2 days. Records and corpus expectations are 1-2 days. E2 is 15+ days, and the risk is high.

**Cost to maintain.** Low for E1. New refusal sites follow the "record and continue" pattern where the step allows it.

**Risks.**
- The accept/refuse answer must not change, only how many refusals it lists. The corpus's `refusal_records.json` and the "first refusal is unchanged" property can enforce that.
- Changing what the generator reports may still be an owner's call under the constraint "any change to what the generator accepts/refuses is the owner's". I read it as not covered, because no model changes from build to refuse or back, but I flag it.
- Skipped subtrees must be reported, or a later run surprises the modeler.

**Keeps.** Everything in 2a that tests the generator. Feeds C.

**Migration.** Step by step, each guarded by the corpus: step 1, then 3, then 5.

### F. Generate the rule list from codegen instead of writing it by hand

**Plain explanation.** I cannot give one honestly. The short version, "the generator's code produces the toolkit's rule list automatically", is not true. The generator's refusals are branches inside a graph builder that depend on the part-instance tree and on earlier steps. They are not data that can be exported. What can be generated is the vocabulary (names, codes, remedy texts, documentation tables), not the checks. That fails the test, and it counts against F.

**Parts.** A build step in codegen that writes `SiteReason` names, remedy texts and documentation tables to a data file that agentic-mbse ships.

**What it would buy.** One place for remedy and documentation text, which C needs anyway (remedies move to codegen). It does not remove the copied detection logic, so all of A's drift risk remains.

**Cost.** Build 2-3 days for the vocabulary. Maintaining the detectors is unchanged from A.

**Verdict.** Useful as a piece of C or G (one remedy table, rendered into the docs). Not an architecture by itself.

### G. Fix it at the source: correct guidance plus an early generator check in the modeling workflow

**Plain explanation.** The shipped examples only teach patterns that the generator's own tests show it builds, and each example names the test that proves it. When a project plans to generate code, the modeling workflow runs the generator's check as soon as the first model pieces exist and at each step after. If generation is deliberately put off, the plan records that and still runs one early check to find structural surprises. Simple.

**Parts.**
- Item 5's fence inventory in agentic-mbse, but with the "executable example" evidence coming from codegen's corpus (a case per recommended pattern), not from rule records.
- `docs/patterns/generator-subset.md` rendered from codegen's remedy and site-reason table (F's useful part), plus the tested working patterns.
- Skill text in `skills/plan-model`, `implement-model`, `model-validation` and `orchestrate-modeling`, and in `MODELING_PROCESS.md.template`: a generated-target project runs `sysml-codegen check` (or L6 under C) at the end of each implementation phase; parked generation still requires one early probe (Item 6 scope 2).

**Catches early.** Problem 2 (wrong teaching) at its source. Problem 1 (late feedback) by making the check a phase gate. It catches nothing automatically on its own. It depends on C or plain `check` for the answer.

**Cost to build.** Item 5 is already scoped. The change of evidence source is about 2-4 days of re-plumbing. Skill and template text is 2-3 days, which is Item 6's scope already.

**Cost to maintain.** Low to moderate: examples break loudly when the generator changes, which is the intended outcome.

**Risks.** Workflow rules are only followed if the skills are used. dc3 ran under orchestration, so this would have reached it.

**Keeps.** Items 5 and 6, re-pointed at the generator rather than at the list.

### H. (Found) Move the generator's own checks into agentic-mbse and have both tools call that one copy

This is ADR 0001's end condition (i), which was not chosen.

**Plain explanation.** Move the generator's model checks into the shared toolkit library, delete them from the generator, and have both the generator and the validator call the one copy. Simple to say. Hard to do.

**Parts.** The part-instance tree (`occurrence.py`, 1,072 lines; its port already exists as `occurrence_extraction.py`), the expression inventory, and the refusal branches of `elaborate.py` that a modeler can reach (71 sites), all moved into agentic-mbse. The generator becomes a consumer of shared decisions.

**Catches early.** Whatever is moved, without the generator installed, with no drift for that part.

**Cost to build.** Large. I estimate 25-40 engineer-days. Every moved site is a chance to change what the generator accepts, which is an owner gate per change. It also reverses where much of codegen's core lives.

**Cost to maintain.** Moderate: one copy, but every generator capability change becomes a change in agentic-mbse, released before codegen.

**Risks.** The highest of all options, because it rewrites the core of the generator to move code. The pieces that cannot move cleanly (the 33 generator-only checks: naming collisions, coverage account, projection) stay behind, so L6 is still incomplete.

**Verdict.** It is the right answer only if "a validator answer without the generator installed" is a hard requirement. Otherwise it is the most expensive way to remove the copy.

### I. (Found) Guidance only

**Plain explanation.** Fix the docs and examples, and do nothing else. Simple. It addresses problem 2 only. It is cheap (Item 5) but leaves late feedback and the one-at-a-time answers in place. It is not enough alone. It is a necessary part of every option.

### Editor-time integration

I considered running a check while the modeler types. Both the list and the generator take 12-18 s on dc3, so neither fits keystroke-time feedback. A save-time or on-demand run of C in an editor task is possible but adds nothing architectural beyond C. Not pursued.

## 4. Side by side

| Option | Plain to explain | Single source of truth | dc3 runs to see all eight | Needs generator installed | Build | Ongoing upkeep |
|---|---|---|---|---|---|---|
| A status quo | Only with a caveat | No (copy + parity tests) | 1 (via L6) | No | done | high, two repositories per generator change |
| B check-only output | Yes | No | 1 (via L6) | No | 1-2 d | ≈ A |
| C L6 runs check | Yes | Yes | ~5+ alone; ~3 with E1 | Yes | 3-5 d + deletion | low |
| D Python API | Yes | Yes | as C | Yes | 1-2 d | moderate (public surface) |
| E1 collect per step | Yes | Yes | ~3 | Yes | 5-8 d | low |
| E2 continue across steps | No | Yes | ~1 | Yes | 15+ d | moderate, risky |
| F generated list | No | Vocabulary only | as A | No | 2-3 d | ≈ A |
| G guidance + workflow gate | Yes | Yes (examples tested by generator) | prevention | Yes, for the gate | 4-7 d (mostly Items 5 and 6 already) | low-moderate |
| H move checks to shared lib | Yes | Yes | 1 for what moved | No | 25-40 d | moderate |

The "~3 runs" figures are read from code, not measured.

## 5. Recommendation

Do **C + E1 + G**, with guidance (I) inside G. Retire the rule list. Do D later only if a consumer asks for it.

Why:

- **It matches the owner constraint.** "The generator's own route alone decides whether a model generates." Under C, the only thing that ever tells a modeler "this will not generate" is that route. Under A, a second implementation also says it, and it can disagree.
- **It addresses all three real problems.** Late feedback: the workflow gate in G plus L6 under C. Wrong teaching: G. One-at-a-time answers: E1, which is cheap because the generator already collects errors inside step 4 and the step 2 screen.
- **It removes a permanent cost instead of paying it forever.** The list needs a coordinated two-repository change for every generator capability change, and two such changes are already queued. Its coverage is 9 families against about 71 reachable sites. Closing that gap is another Item-2a-sized effort with no end state.
- **The list's two advantages are cheaper to get another way.**
  - "Works without the generator installed": a project that targets generation will install the generator to generate, and dc3 had it installed from day one. A project that does not target generation does not need the answer.
  - "Everything in one run": E1 gets dc3 from five-plus runs with stubbing to about three 15-second runs with no stubbing. The remaining gap is small next to the days lost to late feedback.
- **Sunk cost.** Items 1 and 2a are most of the epic's effort, and this recommendation discards the list half of them. That is not a reason to keep them. The parts that test the generator itself survive: per-site reasons, the site account, and the corpus as regression tests. So does everything in Items 3, 4 and 2b except the list presentation.

**The recommendation in three plain sentences.** When a project plans to generate code, the validator asks the generator itself, in a no-write mode, and shows its answer. The generator lists every problem it finds in each step instead of stopping at the first. The guidance only teaches patterns the generator's own tests prove it builds, and the modeling workflow runs that check early.

**Order of work.**
1. Hold the merge of 2b's screen half. Merge `prepare` and `check` without the list printing (option B's deletion), because C needs a clean `check`.
2. E1 step 1 (expression loop), then step 3 (part tree), then step 5 (generation checks). Each is guarded by the corpus refusal records with the first refusal unchanged.
3. `check --format json` and a remedy text per `SiteReason`.
4. The L6 runner behind `execution-target`. Run it side by side with the list on dc3 baseline, dc3 repaired and fusion-tea, and record the differences.
5. Re-point Item 5's evidence and the rendered subset doc at codegen's corpus and remedy table. Add the workflow gate text (Item 6 scope 1-2).
6. Delete the list (agentic-mbse `subset_*`, `occurrence_extraction`/`occurrence_facts` if nothing else uses them, the case store; codegen `subset_screen.py`, `subset_profile_adapter.py`, agreement tests). Supersede ADR 0001, amend P-0001 and the epic's success criteria.

Rough total: 12-20 engineer-days, of which 4-7 is work Items 5 and 6 already planned.

## 6. Decisions only the owner can make

1. **Is it acceptable that a project gets no generation answer unless sysml-codegen is installed?** This is the crux. If yes, C works and the list can go. If no, the choice is between A (keep paying for the copy) and H (move the generator's checks into the toolkit, 25-40 days). I recommend yes, because every project that needs the answer has to install the generator anyway to generate.
2. **Retire the list, or freeze it as it stands until C and E1 ship?** I recommend freezing it now (no new rules, no gap-closing) and deleting it after the side-by-side run in step 4.
3. **Does E1 count as a change to what the generator refuses?** It changes how many refusals one run reports, not which models build. I read it as outside the owner-held constraint, but it is the owner's call.
4. **Supersede ADR 0001 and rewrite the epic's critical success factor.** Today it reads "one L6 run accounts for B1-B8", which presumes the list. It would become: "a generated-target project gets the generator's own answer from L6 or the workflow, listing all problems per step".
5. **Stop work on Item 2a's open owner gates that only serve the list** (RG-1's twelve candidate accept/refuse changes need review on their own merits, separate from the list).

## 7. What I did not check

- I did not implement or run E1. The "about three runs for dc3" figure is read from the step order and which step each category fails in, not measured.
- I did not read projection (`elaboration/project.py`) or the snapshot route in detail. Both may have first-error stops I have not costed.
- I did not check whether `occurrence_extraction.py` and `occurrence_facts.py` have users other than the list. If they do, they stay.
- I did not run L6 or `check` on fusion-tea, or read Item 3's and Item 5's designs in full.
- I did not confirm that every target project that sets `execution-target = "generated"` installs sysml-codegen in the same environment as agentic-mbse. A different venv would need a configurable executable path.
- I did not measure subprocess start-up overhead separately. It is inside the 14-18 s figures.
- The day estimates are mine, from reading the code, and have not been reviewed. Treat them as plus or minus 50%.
- I did not check whether the SysIDE licence check behaves differently when codegen runs as a child process of L6.
