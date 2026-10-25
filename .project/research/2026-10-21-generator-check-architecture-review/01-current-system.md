# Architecture review, part 1: the current system (fact-finding)

**Written:** 2026-10-20. **Scope:** read-only fact-finding for an architecture review of EXEC-SUBSET-CONTRACT. No code was changed.

**Revisions read:** sysml-codegen worktree `subset-profile-screen` at `3ffcbc59` (Item 2b base `556cbedf`, branched from main `0c4b0281`); agentic-mbse worktree at main `e268357f`; dc3 checkout at `60b44d5`; dc3 baseline `808464d` read through `git archive`. Paths are relative to the named repository. "codegen" means sysml-codegen. Anything marked **(inferred)** was not proved by a run or a direct quote.

## Short answers

- **What cost time in dc3** was finding out late that the native idiom dc3 had built and audited (Oct 4-13) sat structurally outside the generator subset (B1-B3). The generator stopping at the first error made sizing that hard, and L6 staying silent on B1-B6 meant nobody knew earlier. The stop-at-first-error problem itself was worked around in one evening: five stub-and-retry runs, one worker reading the code, and one targeted probe.
- **Today's generator** still reports one refusal per run. Some stages already collect many findings (binding readiness, graph diagnostics, extraction diagnostics). The stages that produced dc3's one-at-a-time sequence still stop at the first problem: the expression inventory loop, the occurrence index, calc compilation, projection, and the nine preflights.
- **`sysml-codegen check`** gives `generate`'s answer: exit 0 builds, 1 refuses, 2 usage error. It writes nothing, then prints the rule-list screen's findings as information. On dc3 baseline it took 17.9 s, of which about 17.2 s is the screen. On dc3 HEAD it took 27.1 s.
- **The rule-list stack** in agentic-mbse is about 3,700 lines of new production code (Oct 18-19). On top of that are 1,172 lines that imitate codegen's occurrence logic: the 739-line port and its 433 lines of fact types. A permanent parity test holds the two together. Against the 246-case corpus, 136 recorded disagreements remain; 129 of them are the generator refusing while the list is silent.
- **Dependencies** run one way: codegen depends on agentic-mbse, never the reverse. dc3 has both installed editable from sibling checkouts. fusion-tea pins both by git revision. Both tools need the SysIDE license for live models.

## 1. The original problem in dc3

### What happened

- dc3 built a native AC/DC comparison under goal `conversion-path-efficiency`. On Oct 5 the owner amended the goal so that "A supported native comparison is sufficient; generated/study readiness must either be verified or explicitly parked with the failing seam identified" (dc3 `work/orchestration/goals/conversion-path-efficiency/goal.md:67`). The goal closed on Oct 13 with generated readiness "parked with its failing seam identified" (`:75`).
- The next goal, `study-ready-baseline`, needed the generated route. Its first round assumed "The blockers are mostly expression forms with identical rewrites" (dc3 `work/orchestration/goals/study-ready-baseline/trail.md:17`).
- T-001 inventoried the blockers. Its reason for running: "the generator stops at the first error (`evidence/G-000-generate-probe.log`), so the size and kind of the work is unknown" (`trail.md:33`). The approach was to probe "so later blockers are not hidden behind the first" (`trail.md:14`).
- Method (`evidence/T-001-blocker-inventory.md:7-10`): five sequential `generate` runs, stubbing each first error to reveal the next; a worker reading the code with unpinned probes; a coordinator probe for calc-usage assertions; and a static count combined with L6 output.
- The sequential runs each printed exactly one refusal (`evidence/T-001-probes/sequential-gen{1..5}.txt`, one line each): G-000 `product` (path_efficiency.sysml:52), then a conditional (`SI_EVIDENCE_INCOMPLETE`), then `size`, then `SI_MULTIPLICITY_UNRESOLVED`, then `SI_MULTIPLICITY_UNSUPPORTED`, then `SI_REDEFINITION_INVALID`.
- Probing stopped at run 5 "because further stubbing would change design meaning" (`T-001-blocker-inventory.md:7`). "Not reached: diagnostics behind B3 in the remaining facility structure, and anything in teax execution. The generator never got past elaboration." (`:26`)
- The largest category, B1 (164 calc-usage-owned assertions), was found by the separate coordinator probe, not by the sequential runs (`:16`). B2 came from the worker reading.
- Result: the round premise "is false" (`:33`). Three blockers are structural and "carry dc3's audited native idiom" (`trail.md:52-55`). The round closed `STRATEGY_BLOCKER` (`trail.md:45`).
- The owner chose an in-place rewrite. WI-008 rewrote the models into the subset and reached parity, worst relative error 2.1e-15 over 126 channels (`learnings.md:47-57`).

### What L6 said at the time

- At the baseline, L6 failed only on B8-type constraint codes (`L6_CONSTRAINT_MALFORMED_NUMERICAL`, dc3 `.project/active/toolkit-update/evidence/after-validate.txt:70-106`).
- The origin ticket: "Today L6 passes calc-usage-owned asserts, `product`/`size`/conditionals, sequence inputs, unresolved multiplicities, nested subsets and usage-subsetting composition. It also flags the two String spellings inconsistently." (agentic-mbse `.project/backlog/item_generator-subset-patterns.md:47`)
- dc3's raw learning: "do not read L6 silence as generator support" (dc3 `work/learnings/RAW_LEARNINGS.md:234`).

### What cost time, by candidate cause

| Candidate | Evidence | Reading |
|---|---|---|
| Not knowing early | The idiom was built Oct 4-13 under a native-only contract. T-001 found that B1-B3 were "the modeling idiom the closed goal deliberately built and audited" (`T-001-blocker-inventory.md:31`). The fix "reworks the closed goal's audited models and evaluators" (`:36`). | The largest cost. It was paid as rework in WI-008. |
| Generator stops at first error | Stated directly as T-001's reason to exist (`trail.md:33`). Five stub runs, and they could not finish (`T-001-blocker-inventory.md:7`). Origin ticket: "They appeared one per run, and a T-001 inventory needed stub-and-retry probing to find them all." (`item_generator-subset-patterns.md:32`) | Real, but bounded. Grounding, T-001, the WI-008 spec and design, the rewrite, the tests and the audit all carry dc3 commit times between 20:47 and 22:06 on Oct 13 (`7fb0cd9`, `c2bda1b`, `f87457c`, `2c7f6dd`, `25e8100`, `be457a4`). Commit times are not session times, and dc3 has only 26 commits, so this is an upper bound on how visible the work is, not a measurement **(inferred)**. |
| Misleading guidance and silent L6 | Epic root causes: "Language-valid examples became misleading execution guidance" and "Validator coverage was broader in presentation than in behavior" (agentic-mbse `.project/backlog/epic_executable-subset-contract.md:71,75`). | Contributed to not knowing early. |
| Process (deferral) | The epic: "generation deferral was not itself proof of a process violation" (`epic:56`). The epic also discounts the earlier claims: "Ten days describes elapsed project age… The earlier claims of about 20 runs and exactly 12 non-expert dispatches are not acceptance evidence" (`epic:54`). | Authorized. Not a cause by itself. |
| Silent wrong values (positional binding) | Found by a mutation test during WI-008 (`learnings.md:59-68`). | A separate hazard (Item 4), not a T-001 cost. |

## 2. The generator's route at branch HEAD

### Shape

- `generate` (`src/sysml_codegen/cli/__init__.py:456-505`) runs `load_source`, then `prepare` (read-only), then the destination check, then `emit_package`, which is the only step that writes. After that, `_report_after_the_seal` (`:508-523`) runs the screen and prints its section. The screen cannot change the result.
- `prepare` (`cli/prepare.py:211-234`) builds the exact pipeline context, which covers load, expression inventory, extraction, elaboration and projection. It then calls `prepare_graph` (`:237-290`), which runs nine preflights in a fixed order: generation metadata, exit-point types, constraint names, output paths, registry class names, constraint totality, constraint plan, coverage account, and parameter-field names.
- The answer is `Prepared` or `Refused` (`prepare.py:95-113`). `Refused` holds one step and one `Refusal`. A `Refusal` has an `items` tuple (`cli/refusal.py:57-60`), so one refusal record can carry several diagnostics when the stage that raised it collected them.

### Where it stops at the first problem, and where it collects

| Stage | File | Behavior |
|---|---|---|
| Parse | `orchestration/elaborated_pipeline.py:295-307` | One failure, with SysIDE's diagnostics rendered together |
| Expression inventory: every expression site, before anything else | `elaboration/expression_evidence.py:247-254`; the per-site check is agentic-mbse `sysml/reference_use.py:292` and the invocation refusal is at `:447` | **Stops at the first site.** `product`, `size`, conditionals and indexed references each raise. This is where dc3 runs G-000, 1 and 2 came from. |
| Calc-def compilation | `elaboration/elaborate.py:767-786` | Stops at the first calc def |
| Extraction diagnostics | `elaboration/extraction_screen.py:70-115` | **Collects** every blocking diagnostic into one raise |
| Constraint-profile association | `elaborate.py:661-700` | Stops at the first invariant |
| Slot index and occurrence index | `elaborate.py:609,614`; `elaboration/occurrence.py:825-912` (multiplicity), `:921` (`build_occurrence_index`) | **Stops at the first problem.** dc3 runs 3, 4 and 5 came from here. |
| Constraint owner metatype | `elaborate.py:882-890` | Raises. dc3's calc-usage-assert probe at `b5663c07` printed exactly one `SI_CONSTRAINT_UNATTACHED` (dc3 `evidence/T-001-probes/calc_usage_assert.log`). |
| Constraint dispositions | `elaborate.py:1670-1710` | **Collects**: "one diagnostic per usage" |
| Binding and expression resolution | `elaborate.py:2629, 2651, 2704, 2755, 2808` catch, record and `continue`; readiness findings collect and raise together at `:2822-2831`; graph diagnostics raise together at `:797-798` | **Collects** |
| Conversion to a refusal | `elaborated_pipeline.py:350-421` | Wraps each error class; one element unless the source collected several |
| Projection | `elaboration/project.py:150-165` (`_fail`), `:279` | Mostly stops at the first problem |
| Nine preflights | `prepare.py:251-290` | **Stops at the first.** The order is kept on purpose: "every check that ran before it at the base still reports first for a model with several faults" (`:284-286`). Spec line 93 makes the same first-refusal code a condition. |

### Refusal sites

- The site account (`tests/expectations/subset_profile/site_account.csv`) has **491 rows**, one per raise or factory site that the scanner finds under `src/sysml_codegen/`.
- By role: 179 internal invariant, 92 snapshot integrity, 71 public capability, 64 relay or plumbing, 55 environment, 14 malformed input, 16 unknown.
- By disposition: 418 handled elsewhere, 56 explicit follow-up, 17 in scope.
- The CSV header lists the scanner's blind spots. They include refusals returned as values, helpers with many callers counted as one row, silent omissions, computed codes, and dynamic dispatch.
- So there are about 71 public capability sites a valid model can reach, out of 491 raise sites.

### How hard it would be to collect all independent refusals in one run (inferred, from reading the code)

- **Easy: the expression inventory.** The sites are independent of each other. Catching per site, collecting, and raising once after the loop would show dc3's B4, B5 and B6 together. `ExpressionEvidenceInventory` needs every row, so a failed site has to stop the route after the loop, not before it.
- **Moderate: calc compilation and the preflights.** These are independent per calc def and per check. The cost is the deliberate first-refusal ordering. Collecting would change the refusal record, and under RG-1 the owner has to approve that change (`briefs/align.md`, spec line 93).
- **Hard: the occurrence index.** It expands a tree recursively. A bad multiplicity means that subtree has no known count, so anything beneath it is dependent. Collecting would mean skipping the subtree, marking what is beneath it "not assessed", and continuing with sibling subtrees. The agentic-mbse port already does this (`occurrence_extraction.py` turns aborts into `FactFailure`), so there is a working pattern to copy.
- **Structural limit:** elaboration needs the inventory and the occurrence index before it can build anything. Findings that depend on a failed stage cannot honestly be reported. That matches epic principle 5 ("do not invent downstream findings").
- I did not prototype any of this, and I did not estimate it in days.

## 3. `sysml-codegen check` at HEAD

- **What it does:** `cmd_check` (`cli/__init__.py:94-123`) and `run_check` (`:126-142`). It first checks that `agentic_mbse` imports; if not, it exits 1 with an environment message. Then it loads once, runs `prepare`, optionally runs the destination check (`--output`, inspected but never written), and then `subset_screen.assess_screen` on the same load. It never imports `cli/emit` (`:28-29`).
- **Arguments** (`:357-381`): `--models` or `--from-snapshot` (one is required), `--output`, `--package-name`, `-v`. There is no JSON or machine-readable output.
- **Exit codes:** 0 if `generate` would build, 1 if it would refuse (environment failures included), 2 from argparse for usage errors. The screen never changes the code (`:94-99`; spec Success Criterion 13).
- **What it prints** (`cli/report.py:131-212`):
  - The generator's one refusal record, or "Generator: builds (N modules)".
  - A screen summary line with the profile version, the verdict, counts by outcome, and how many checks were not assessed. A clear verdict carries "(over the implemented rules; not a promise the generator accepts the model)".
  - Each refused, unconfirmed or candidate-refusal finding as a WARNING, followed by its remedy.
  - One count line for admitted findings, and one line per rule for omitted or excluded findings.
  - Each check that was not assessed.
  - At most one disagreement line.
  - `generate` prints the same screen section after the seal.
- **The screen is not assessed** for snapshots, parse errors, profile-version skew, import failure, or a screen crash (`subset_screen.py:43-49, 84-110`).
- **No readiness claim.** Phase 10 removed READY and exit 3 (spec line 106; `product-lens.md:141`).
- **Runtime, measured today** with `.venv/bin/sysml-codegen`, licensed, one run each:
  - dc3 baseline `808464d`: exit 1, 17.9 s wall, 234 MB peak memory, 541 output lines. Split by phase: load 0.38 s, `prepare` 0.01 s (it refuses at the inventory), screen 17.2 s. The generator printed one refusal (`product`). The screen printed 236 refused, 32 omitted, 6 unconfirmed, and 50 not assessed. Output saved at `/tmp/claude-1000/-home-reid-src-agentic-mbse/757488b6-d865-4d53-baa0-842d9ebab104/scratchpad/check-dc3-base.txt`.
  - dc3 `60b44d5` (repaired): exit 0, 27.1 s. `prepare` 14.3 s, screen 12.6 s. Verdict clear; 15 admitted, 30 omitted.
  - Item 2b's earlier numbers: `generate` 4.19 s on `catf_mfe_d5` and 3.84 s on `catf_mfe_gated` (`evidence/baseline.md:39`), with about 3 s of fact extraction added per `catf_mfe` model (`design.md:69`).
- **Observed quirk:** a refused finding is labeled "matches the generator's `<code>` at `<place>`" whenever the codes are equal, even when the places differ. On dc3 baseline, the binding-source finding at `ac_facility.sysml:213` is reported as matching the generator's `product` refusal at `path_efficiency.sysml:52` (`report.py:204-210`).

## 4. The rule-list stack

### agentic-mbse modules (production, under `src/agentic_mbse/sysml/` unless noted)

| Module | Lines | Added | Role |
|---|---|---|---|
| `subset_profile.py` | 1481 | Oct 18 | The pure evaluator, rule-record loader, `SUBSET_PROFILE_VERSION = "subset-profile/v2"` (`:125`), `PACKAGED_RULES` |
| `subset_profile_rules.toml` | 671 | Oct 18 | 9 rules (binding-source, calc-owned-assertion, calc-usage-result, conditional-expression, constraint-predicate, indexed-reference, invocation-callable, part-multiplicity, string-value-omission), with shapes, admissions and generator evidence |
| `subset_extraction.py` | 546 | Oct 18 | `extract_subset_facts`. It mostly calls the same helpers the generator calls; its docstring table maps each fact to the generator code it mirrors (`:14-30`) |
| `subset_facts.py` | 339 | Oct 18 | Fact types |
| `occurrence_extraction.py` | 739 | Oct 18 | The occurrence port. "agrees with the generator by imitation, not by shared code" (`:4-5`), mirroring codegen `elaboration/occurrence.py` function by function (`:13-25`) |
| `occurrence_facts.py` | 433 | Oct 18 | Occurrence fact types |
| `conformance_case.py` | 312 | Oct 18 | The conformance-case format |
| `subset_advisories.py` | 153 | Oct 19 | L6 advisories |
| `subset_coverage.py` | 107 | Oct 19 | The coverage-limit statement (`subset-coverage/v2`) |
| `fact_refs.py` | 59 | Oct 18 | Fact identities |
| `invocation_allowlist.py` | 56 | Oct 18 | Allowed callables |
| `subset_cases/` | 154 case folders, 1.9 MB | Oct 18-19 | Packaged cases |
| `validation/subset_presentation.py` | 578 | Oct 18-20 | How L6 presents the results |
| `validation/execution_target.py` | 233 | Oct 18-20 | The target setting and the severity table |

- Production total for the stack (`sysml/` modules, TOML, and the two validation modules): about 5,700 lines. Excluding the two Item 3 presentation modules and the occurrence port with its fact types, it is about 3,700 lines. Supporting code: about 2,800 lines of scripts (`scripts/subset_profile/`, `scripts/l6_subset/`) and about 3,700 lines of tests and helpers.
- In codegen, the consuming code is `subset_profile_adapter.py` (157 lines, reason-to-code mapping), `subset_screen.py` (181), `cli/report.py` (218) and `_upstream_pins.py` (79). Tests: about 5,900 lines in `tests/conformance/subset_profile/` and `tests/helpers/subset_profile/`, plus 2.5 MB of expectations and fixtures.
- Item 4's `parameter_redefinition_*` (559 lines) belongs to the same epic but is the positional-binding check, not the rule list.

### What it duplicates from the generator

- **Occurrence logic:** a 739-line port plus 433 lines of fact types, against codegen's `elaboration/occurrence.py` (1,072 lines). This was a deliberate choice (ADR 0001 "A (ii)", agentic-mbse `.project/adr/0001-subset-profile-capability-ownership.md:17,34`).
- **Refusal decisions:** the 9 rules restate, for the shapes they cover, what codegen decides in its own code. Facts mostly come from shared helpers. Expression sites, for example, go through the same `inspect_reference_uses` that codegen's inventory calls.
- **The model load and fact extraction:** `check` and `generate` run them a second time. `check` reuses the load but not the generator's elaboration.

### Tests that keep the two in agreement

- **Occurrence parity:** `tests/conformance/subset_profile/test_occurrence_parity.py` in codegen, licensed. It covers the 34-model seed, 37 corpus fixtures, and every conformance case, plus a mutation that drops one index inside `_multiplicity_indices` (`:1-40`).
- **The 246-case corpus:** `tests/expectations/subset_profile/cases/` (246 JSON files). `test_check_matches_stored_answers.py` and `test_report_form.py` (check and generate give the same answer on all 246), along with agreement, mutation, witness and site-account tests (33 test files).
- **`disagreements.json`:** 136 entries. 129 are `generator_refuses_screen_silent`; 7 are `code_unmapped` (5 `constraint_predicate_blocked`, 2 `binding_source_self_reference`). Resolutions: 102 `reproduced_gap`, 33 `codegen_owned`, 1 `rg1_pending`. 0 are `screen_refuses_generator_builds` (`product-lens.md:11`).
- **Version pin:** codegen `_upstream_pins.py` pins `SUBSET_PROFILE_VERSION`. A mismatch makes the screen "not assessed" (`subset_screen.py:122-128`).

### Every consumer of the list

| Consumer | Where | What it uses |
|---|---|---|
| L6 | agentic-mbse `validation/level6_architecture.py:36-37, 1026-1028`; `subset_presentation.py:37` | `extract_subset_facts` and `evaluate_subset_profile` on every L6 run |
| codegen `check` and `generate` | `subset_screen.py:113-158`, `cli/report.py`, `subset_profile_adapter.py` | The same pair, after `prepare`, as information |
| codegen elaboration | 5 imports of `agentic_mbse.sysml.subset_profile`, 1 of `subset_extraction` (grep over `src/sysml_codegen`) | Mostly vocabulary and adapter use; the screen does not decide refusals |
| Shipped guidance | agentic-mbse `README.md:19`, `skills/model-validation/SKILL.md:28-30` | Hand-written prose naming `subset-profile/v2` and the 9 rules. SKILL.md:30 still says asking sysml-codegen "is a separate, future step that does not exist yet" |
| Item 5 (rendered `docs/patterns/generator-subset.md` and the example harness) | Not built. No `docs/patterns/generator-subset.md` exists, and agentic-mbse's `shipped-example-contract` branch has no commits beyond main besides wrap-up | Planned consumer (epic Item 5 scope 4) |
| Scripts | `scripts/subset_profile/*`, `scripts/l6_subset/run_consumers.py` | Evidence runs |

## 5. Dependency direction and install footprint

- **codegen depends on agentic-mbse:** `pyproject.toml:24` declares `"agentic-mbse>=0.1.3,<0.2"`, and `[tool.uv.sources]` (`:121-122`) points at `../agentic-mbse` as an editable install. Codegen's `src/` imports agentic-mbse in 30 files (SysIDE adapter, expression IR, reference_use, executable_profile, subset_profile, installer).
- **agentic-mbse does not depend on codegen.** Its dependencies (`pyproject.toml:22-30`) don't list it. No module imports it, and ADR 0001 invariant 3 forbids that ("No agentic-mbse module imports sysml-codegen", `:31`). The reason given is that the reverse import would be a cycle (`:21`).
- **dc3:** `pyproject.toml:7-9` lists `agentic-mbse[extract-full,web]==0.1.3`, `sysml-codegen==0.1.1` and `teax-simkit==0.1.0`. `[tool.uv.sources]` (`:23-27`) makes all three editable path installs from `../agentic-mbse`, `../sysml-codegen` and `../teax/packages/teax-simkit`. `.venv/bin` has both `agentic-mbse` and `sysml-codegen`. dc3 therefore runs whatever the sibling main checkouts hold.
- **fusion-tea:** both packages pinned by git revision (`pyproject.toml:36-37`: agentic-mbse `44338882`, codegen `8a758e92`). There is no `.venv` in the checkout today.
- **teax:** no dependency on either package (checked `pyproject.toml` and `packages/teax-simkit/pyproject.toml`).
- **Neither consumer sets `execution-target`** (grep of both `pyproject.toml` files).
- **License:** both tools need `SYSIDE_LICENSE_KEY` to parse live models. agentic-mbse imports SysIDE lazily, so only parsing needs the license (`syside_adapter.py:12-14, 53-71`). Codegen: "Live parsing and snapshot capture require a valid `SYSIDE_LICENSE_KEY`", while `generate --from-snapshot` is license-free (`README.md:14-22`, `CLAUDE.md:29-38`).

### Could L6 run `sysml-codegen check` as a subprocess?

**(inferred)** Nothing in the import rule blocks it, because a subprocess is not an import. ADR 0001 rejected codegen-owned policy "because L6 and guidance could not consume it without a reverse dependency" (`:38`). I found no design that considered a subprocess: I grepped the epic, Item 1's design, and Item 3's spec and design for "subprocess" and found nothing. Doing it would need:

- **Finding the executable:** `sysml-codegen` on PATH, or in the same venv. Any environment with codegen also has agentic-mbse, but not the reverse. A missing codegen must read as "not checked", never as a pass (epic Item 6 scope 1 already says this).
- **Machine-readable output:** `check` prints log lines only, with no JSON option (`cli/__init__.py:357-381`). L6 would have to parse text, or codegen would need a structured-output flag.
- **Avoiding double work:** `check` always runs the screen, which takes 12-17 s on dc3, and L6 already evaluates the same rules. There is no flag to skip the screen. The model would also be parsed twice.
- **Version alignment:** under dc3's editable installs both tools move together. Under fusion-tea's pins they move separately; the profile-version pin then marks the screen not assessed but still gives the generator's answer.
- **The license:** the same license L6 already needs.
- **Wording:** L6 currently bans any readiness wording (Item 3 `spec.md:158`, "Only the future `sysml-codegen check` (Item 2) could support that claim").

## 6. What L6 shows today for each execution target (Item 3)

- **The setting:** `[tool.agentic-mbse] execution-target = "generated" | "native"` in `pyproject.toml`. `validate --execution-target` overrides it for one run, and `init --execution-target` writes it (agentic-mbse `README.md:27-30`; ADR 0003).
- **The severity table** (`validation/execution_target.py:176-192`), shown as unset / generated / native:
  - Refused: warning / **error** / folded into one INFO summary.
  - Unconfirmed, excluded, omitted: warning / warning / summary.
  - Unverified: warning / **error** / warning.
  - Check failure: error under every target.
  - 4 legacy codes are lowered into the summary under native: `L6_MISSING_QUALIFIED_NAME`, `L6_ANONYMOUS_RETURN`, `L6_BODY_ASSIGNMENT_IMPL_LOSS`, `L6_CALC_DEF_NO_INSTANTIATION` (`:203-221`).
- **Unset** adds a note saying generator findings are warnings because no target is set (`subset_presentation.py:58-61`). The CHANGELOG says the run "never says generated-ready".
- **Native** prints one INFO line: "N refused, N unconfirmed, N omitted, N excluded, N unassessed constraints, N advisories, N legacy; all listed in --json-report" (`subset_presentation.py:474-484`).
- **Every target** prints the verdict line, ending "not a generation check" (`:205-220`), and a "Coverage limit" line listing rule families with no rule yet and the follow-up site count, 70 after 2a (`:226`; epic line 160).
- **dc3 baseline under generated** (Item 3 evidence `20261020_l6-subset-profile/evidence/dc3-baseline-l6.md`): exit 1 in 18.1 s. 236 refused, 32 omitted, 6 unconfirmed, 50 unverified. Each of B1-B8 appears with a location and a remedy. B8 is "unconfirmed" because B1 shadows it.

## 7. Effort

| Item | Estimate recorded | Calendar | Commits | Diff |
|---|---|---|---|---|
| Epic original | ~10 days for all six items, later disowned (`epic:9, 326`) | | | |
| 1: profile (agentic-mbse PR #30, `ccd57d83`) | ~12-15 engineer-day equivalent of work done (`20261018_exec-subset-profile/evidence/re-estimate.md`) | Oct 15-18 ("4 days", CHANGELOG) | 60 | +138,651 lines, mostly probe fixtures and evidence |
| 4: positional check (PR #31, `ebb3d467`) | "Re-estimate for semantic boundary cases" | Oct 18 ("0 days") | 39 | +12,006 |
| 3: L6 and target (PR #32, `1a3d67c6`) | "Re-estimate after Item 1" | Oct 18-20 ("2 days") | 58 | +27,356 |
| 2a: conformance (codegen PR #22 `0c4b0281`; agentic-mbse PR #33 `e268357f`) | ~25-35 engineer-days (`epic:164`) | Oct 18-20 | 56 codegen + 23 agentic-mbse | codegen +16,311; agentic-mbse +7,879 / −12,739 (the site account moved to codegen) |
| 2b: check (this branch, unmerged) | 6.5-9 engineer-days, "a guess" (spec line 7) | Oct 20 | 47 since main `0c4b0281` (34 since `556cbedf`) | src and tests +8,155 / −1,520; `src/` alone +1,969 / −1,126 |
| 5, 6 | Re-estimate later | Not started | | |

The work was done by agents. Calendar days and commit counts do not measure human effort, and the re-estimate says so (`re-estimate.md`, "Agent wall-clock is not a reliable guide").

## Not checked

- I did not run `generate`, the test suites, or L6 myself. The L6 numbers come from Item 3's recorded evidence. I ran `check` twice and timed it three ways, once each, on one machine.
- I did not check which of the 71 public-capability sites a valid model can actually reach, and I did not check the 16 unknown-role sites.
- I did not prototype collecting multiple refusals. Section 2's difficulty ratings come from reading the code.
- I did not read dc3's WI-008 design, review or audit, and I did not read the session transcripts, so active modeling time in dc3 is not established.
- I did not inspect fusion-tea's installed environment (no `.venv`), and I did not check whether its pinned revisions contain the stack.
- I did not read codegen ADR 0007 or the new ADR 0018 on sysml-codegen main (`8396cb23`) beyond their titles.
