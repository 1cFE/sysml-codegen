# Spec Review: PR-readiness cleanup

**Spec:** `.project/active/pr-readiness-cleanup/spec.md`
**Contract:** `claude-pack/commands/_my_spec.md`
**Review File:** `.project/active/pr-readiness-cleanup/spec-review.md`
**Date:** 2026-10-06

**Method.** Six read-only Opus reviewers each took one area:
- C2 and C5
- C3
- C4
- C6 and C7
- C1, C8, C9 and C10
- the functional test lanes

Each checked the spec's code claims against the code and hunted for regressions. The reviewer spot-checked the claims this review rests on. The reviewers' scratch evidence lives in this session's scratchpad, which is temporary. This review did not re-verify the July historical census or the lineage figures (Known Requirement 5).

**Owner direction for this review** `[OWNER-VERBATIM, 2026-10-06]`: "Look carefully at possible regressions from our fixes, and make sure we have success criteria (real functional tests, not just unit tests) to mitigate those risks"

---

## Reality Check

**Concerns.** The spec targets the right work. Every cleanup defect it names is real. The reviewers reproduced C1, C2, C3, C5, C6, C8 and C9, and simulated C4 end to end through real TEAx. Three things keep it from being a contract you can trust today:

- **A bad license reads as green.** When the key fails, the default suite turns every licensed test into a skip, so a run looks green while proving nothing. This happened during this review: the documented key had expired.
- **The criteria have no regression oracle.** Nothing requires capturing today's generated output before the code changes. The reviewers showed that template mutations pass the existing suite unchanged.
- **Several premises are wrong.**
  - C2's encoder change is not what stops invalid JSON.
  - C3's offset fix alone does not solve the customer's problem.
  - C4 changes an owner-accepted record the spec never mentions.

---

## Audit

### Lens 1 — Faithfulness

**L1-1 · Direct claim:** Two owner rulings lost their grade at this hop.
- **The rulings.** The single-completion-authority rule (Problem, third paragraph) and the fixture/customer convergence rule (Known Requirements, last bullet) are both `[OWNER 2026-08-16]` resolutions (`.project/active/elaborator-downstream/spec-review.md`, Resolutions L2-1 and L2-2).
- **The downgrade.** The downstream spec carried both as `[NEED]`. This spec carries them as `[INHERITED]`, which capture-fidelity treats as open to challenge on evidence.
- **The misrouting.** The last Known Requirement frames the convergence ruling as something to reconcile "against later authorized customer changes", and the Open Questions send that reconciliation to design. A conflict between two owner decisions belongs to the owner, not design (capture-fidelity law 4).
- **What needs to be true.** Both carry `[NEED]` with a path-cite to the ruling, and the conflict moves to an owner question (see L2-3).

**L1-2 · Direct claim:** C2 is a second line of defense, not the fix the research describes.
- **The research's claim.** `allow_nan=False` "stops the invalid JSON path".
- **The path is already closed on both routes.** It closes upstream, before any file is written.
  - Live route: `_computation_digest` serializes every projected field with `allow_nan=False` and raises a named `CodeGenerationError` (`orchestration/exact_pipeline_context.py:105-131`).
  - Snapshot route: the v6 snapshot encoder refuses NaN at capture (`snapshot/instance_graph.py:87`).
- **The reviewer's test.** It injected `inf` into a live graph, and `NaN` or `1e309` into a committed snapshot. Each was refused, and no output directory was created.
- **The gap.** No test pins either refusal; no test mentions "non-finite or non-canonical". SC2 as written tests only the encoder, so the behavior users depend on stays unpinned.
- The research's `model_contract.py:75` cite points at the constructor. The caller is at `:69-70`.

**L1-3 · Direct claim:** SC4 misdescribes what C4 touches, and misses an owner-accepted record.
- **"Located enum-refusal checks" is the wrong label.** `test_elaboration_fail_closed.py:158` is a positive check. It confirms seven enum redefinitions resolve as literals; it records no location and expects no refusal. The real located enum refusal is `test_feature_typing_integrity.py:96`, and C4 does not touch it. The `:158` test also breaks at `:146`, where `len(graph.calcs) == 7` becomes 6.
- **The occurrence contributes more than "two channels".** It adds 1 module, 2 channels, 4 entry points (27 → 23) and 2 output aliases (7 → 5). Every later `execution_order` shifts by one.
- **Two license-free tests break that the spec does not name.** Both are the `fusion_tea` cases in `test_v6_recapture_batch.py`: byte identity, and the projected outcome.
- **Fixing them edits an owner-accepted record.** The fix edits `tests/fixtures/v6_recapture_batch/batch.json`. That file's README opens "ACCEPTED v6 recapture batch — owner ruling 2026-08-11". The fix also edits row 15 of `.project/reference/elaborator-breadth-diff-ledger.md` (`graph 9/27/1/7` → `8/23/1/5`), which `scripts/capture_v6_batch.py:62` checks. The spec should name this change.
- **The core claim holds.** A license-free simulation removed the occurrence, then projected, generated and executed the fixture in real TEAx. LCOE came out exactly `270.1211779380445`. The other seven numeric channels and the constraint report were bit-identical, and nine exits remained.

**L1-4 · Direct claim:** SC11's "research baseline" for generated output does not exist.
- `/tmp/cleanup-research-artifacts/validation-evidence.json` holds only counts and log hashes.
- The earlier REPO-CLEANUP "850 hashes" comparison stored only equal/unequal flags (`/tmp/repo-cleanup-byte-results.json`).
- Nothing durable is in the repo.
- The comparison is cheap to rebuild. A reviewer ran archived `6872977` against HEAD over all 22 committed snapshots, license-free, in 21 seconds: 22/22 equal, 850 files, 3 refusals.

**L1-5 · Direct claim:** SC1's "named companion revision" has nothing to name.
- **No pin.** Codegen installs Agentic as an unpinned editable path (`pyproject.toml:64`, `uv.lock:8`).
- **Reads uncommitted files.** The guidance test reads Agentic's working tree (`tests/helpers/source_roots.py:15-22`), so an uncommitted Agentic edit can make SC1 pass.
- **Wrong identity in the research.** The research's Agentic revision `9e3a847` is not on Agentic main. It sits on the squash-merged `research-approval-empty-insights` branch; `git merge-base --is-ancestor 9e3a847 8f43a09` exits 1.
- **The failure is real at main.** It still reproduces at Agentic main `8f43a09`: 8 passed, 1 failed.

**L1-6 · Rewrite request:** The owner has now stated a regression requirement the spec lacks. The quote is at the top of this review: success criteria must include real functional tests, not just unit tests, against regressions from the fixes. Today's criteria are mostly unit-level or encoder-level (SC2, SC3, SC5, SC6). The spec agent should absorb the quote as a `[NEED]` and make the criteria satisfy it (see L3-1 through L3-6).

**Checked and sound:**
- The Problem's `[NEED]` quote matches the research word for word.
- ADR `0005` and products `0002`, `0005` and `0006` exist with the grades the spec gives them.
- The six absent test basenames and the matrix count (288 rows: 149 PASS, 138 RETIRED, 1 PARTIAL) are exact.

### Lens 2 — Problem & Approach

**L2-1 · Question to the user:** Where is the PR finish line?
- **This can't wait for design.** The spec parks the question and says it may go to design, but it decides what the PR *is*. That is a spec-stage question.
- **The spec has already half-committed.** SC9 adds `REQ-SI` rows, which is the old Item 8 criterion 13. SC10 records a disposition for all 21 Item 8 criteria. Calling the finish line "undecided" is not accurate.
- **Option 1: ship C1–C10 as a cleanup PR.** The composed proof, the copied-store refusal, the old/new lineage, and your external-use attestation stay open under Item 8. The `REQ-SI` rows show those cells as open, and the PR body names them. Cost: Item 8 stays open.
- **Option 2: add those assurance obligations to this PR.** Cost: they depend on your attestation and the customer branch. Neither fits "a few days".
- **Recommendation:** option 1.

**Which do you want?**

**L2-2 · Question to the user:** Does C3 fix only the byte offset, or also the rule that reads comment prose as a unit? The offset bug is real (`extraction/feature_metadata.py:96`), but the evidence says fixing it alone helps no one today.
- **Nothing current changes.** No committed fixture snapshot and no current customer model changes. The customer already worked around the bug by rewriting comments in ASCII (fusion-tea `models/stellarator_migration_ledger.md`, row F3, marked for revert).
- **On the real reproducer, the fix produced no real units.** On the pre-workaround stellarator models (fusion-tea `d04ed5bb`), the fix changed 41 declarations. It swapped the next line's prose for each declaration's own trailing prose: `interest_rate` n→i, `crf` overnight→capital, `p_tfcool` None→coil. The rule that takes the first word after `//` as the unit (`:104`) does the damage either way.
- **The prose rule already leaks into output today.** `Fraction` in `catf_mfe_gated` comes from `// Fraction of surface exposed` (`library/physics/geometry.sysml:181`). In the customer's model, `// T atoms` reads as tesla.
- **Option (a): offset fix only.**
  - Add a test that pins today's behavior for prose on the declaration's own line.
  - Split the backlog ticket.
  - State that C3 does not authorize the customer's F3 revert.
  - Cost: cheap, but no user-visible gain, and a small risk of new `SI_RENDERING_COLLISION` refusals on models with trailing prose comments.
- **Option (b): also restrict comment-derived units to an explicitly marked form.**
  - This fixes the customer's actual problem, and it fits product `0003` (no invented behavior).
  - Cost: it drops `Fraction` and may drop bare `m³/s`. `catf_mfe_gated` then needs a recapture, and you need to make the compatibility call.
- **Recommendation:** (a) for this PR, with (b) filed as its own item, because (b) needs your compatibility ruling and a licensed recapture. Either way this is your call at spec time, not design's.

**Which?**

**L2-3 · Question to the user:** What does "converge" mean for the fixture now?
- **It matches the August 16 customer exactly.** With lines 99–119 of `hif_driver.sysml` removed, all 11 fixture files are byte-identical to fusion-tea `9e1ff87bb:models/` (2026-08-16). That is the post-R-2 customer your L2-2 ruling referred to.
- **Today's customer has moved on.** `8efe17e05` has diverged since 2026-09-10:
  - 33 pinned channels against the fixture's 9, with 7 shared;
  - driver efficiency 0.28 against 0.35;
  - new price calcs and a `net_positive` constraint.
- **Converging with today's customer** would mean copying current customer physics into the fixture, which is a Non-Goal.

**Is your ruling satisfied by convergence with the August 16 customer, recorded as the fixture's provenance?**

**L2-4 · If-then tradeoff:** The customer will not see this PR.
- **The pin.** fusion-tea and its sibling checkouts pin codegen `8a758e92` through a uv git source, a sealed wheel, and `tests/test_dependency_provenance.py`.
- **What that means.** The PR cannot break the customer, so "good working state" is a codegen-only claim. A later repin will carry PRs #13 and #15 and this cleanup all at once.
- **If** "good working state" includes the customer, the spec needs one customer check. Either regenerate a customer package with the candidate wheel and compare `semantic_fingerprint`, or run `test_codegen_teax_acceptance.py` from an archived fusion-tea copy. Neither needs a repin or an edit to fusion-tea.
- **If not**, the PR body should say the customer stays on `8a758e92` and record the repin as an obligation.
- **Two regressions would only appear at repin** (L3-4): a format change that moves the fingerprint, and lost handwritten code.

### Lens 3 — Pipeline Risk

**Regression coverage at a glance.** Each row: the fix, how it could regress, whether today's suite would catch that, and the functional evidence the spec should require.

| Fix | How it could regress | Caught today? | Evidence the spec should require |
|---|---|---|---|
| C2 | Fingerprint moves if the fix goes through Pydantic (exponent format). A refusal gets mislabelled after a partial write. | No. Codegen fixtures have no exponent-form floats. | Finite bytes unchanged across the full float range. A named refusal at the public route, before any write (L3-4, L3-5). |
| C3 | Fix lands on the wrong line. Own-line prose becomes a unit, causing new collisions. Committed snapshots go stale. | No. The unit-lane tests need the license and skip silently without it. Nothing compares committed snapshots to live output. C7 cannot see this. | Licensed check that no committed snapshot is stale. A real-model regression through both routes (L3-3). |
| C4 | Recapture absorbs unrelated drift. An owner-accepted record is edited silently. | Partly (channel pins). | Unchanged-fixture recapture byte check first. An exact graph difference. A named batch amendment (L3-3, L1-3). |
| C5 | Rendered bytes drift. A guard refuses constraint packages. Handwritten code is overwritten. | The guard case, yes. Drift and preservation, no. | Whole-package oracle captured before any change. Preservation checked in a real package (L3-2, L3-4). |
| C6 | Real load failures still skip behind a false license probe. | No. | Zero license skips. Unconditional failure on model load errors (L3-1, L3-8). |
| C8–C10 | Provenance guards weaken when retargeted. Tag references dangle. | Partly. | Guards keep equal force. A check for tag references (L3-9). |

**L3-1 · Direct claim:** The criteria do not guard against the false green a failed license produces, and this review hit exactly that.
- **What happened.** On 2026-10-06 the key in `agentic-mbse/.env` expired. That is the key home `CLAUDE.md:38` names. With it, `import syside` (0.8.4) raises "License expired".
- **Fixed 2026-10-07.** A newer, valid key was in `fusion-tea/.env`, and the owner copied it into `agentic-mbse/.env`. With it, syside imports, and `test_elaboration_fail_closed.py` passes 17 of 17 where the expired key skipped all 17.
- **A misleading message.** Agentic's `get_syside` (`agentic_mbse/sysml/syside_adapter.py:65`) rewrites the expiry error as a missing-key error.
- **What the suite showed under the expired key.** On unmodified `main`, the default suite reported about 1,110 passed, 1,012 skipped ("no live syside license"), 21 failed, and one collection error. A subset run was silently green.
- **The licensed baseline.** Re-run 2026-10-07 at `6872977` with the valid key: 2,139 passed, 1 failed, 9 skipped, 96 deselected, and zero license skips. The failure is the known C1 guidance check (`project_templates/MODELING_PROCESS.md.template`). The 9 skips are the parity golden gaps (L3-8). The 96 deselected are the real-TEAx lane, not yet re-run under the valid key.
- **The loophole.** SC11's "every skip explained" is satisfied by "no live syside license".
- **What needs to be true:**
  - A working license is an explicit precondition for SC3, SC4 and SC11.
  - The final run shows zero license skips under `-rs`.
  - Its skip set is exactly the expected one.
  - The evidence record says which key file the run used.

**L3-2 · Direct claim:** No regression oracle exists before the code changes, and the spec does not require one.
- **Mutations go unnoticed today.** The reviewers mutated five templates: module wrapper, pipeline YAML, implementation stencil, parameter-group schema, and multi-output model. The license-free failure set stayed identical to `main`'s. A mutation of the implementation stencil changed zero bytes across all 19 generated packages.
- **So C5 drift would be invisible.** A cosmetic or rendering regression from C5 would not show today.
- **The ordering is wrong.** C7 would build the oracle, but the research orders C5 before C7, and SC7 does not say when its expected output is captured.
- **What needs to be true:**
  - Complete generated output for all 22 committed snapshots is captured at `6872977` before any code change: every file and every refusal outcome.
  - That capture is stored durably, in the repo.
  - The candidate's output matches it, apart from a reviewed list of intended differences. For C4 that list is exactly six `fusion_tea` files: both contracts, `inputs/hif_driver_params.json`, `pipeline.yaml`, `schemas/hif_driver_params.py`, and the generated runnable tests.
- **Why this one.** It runs license-free in about 21 seconds. It is the cheapest and strongest functional regression check available.

**L3-3 · Direct claim:** The planned C7 gate cannot see C3, or any change on the live route.
- **Snapshot generation never re-reads units.** Units are sealed into each snapshot (`snapshot/instance_graph.py:228`).
- **Parity tests don't help.** Every live-vs-snapshot parity test captures both sides fresh in the same run (`test_exact_route_fingerprint_stability.py:177`, `test_exact_route_generated_package.py:77`).
- **Only a manual script compares committed to live.** Nothing compares committed snapshots against fresh live extraction except `scripts/assess_v6_snapshot_churn.py`, which is manual and needs the license.
- **C4's recapture has a quieter risk.** Sixteen extraction, elaboration or snapshot commits have landed since the last capture (`09fdae1`, 2026-08-17), and no test runs `capture_v6_batch.py --verify`. Any drift would ride in silently with the recapture.
- **What needs to be true, under a license:**
  - No committed snapshot is stale against live extraction, except the intended `fusion_tea` recapture.
  - Unit maps are unchanged across the C3 fix.
  - Recapturing the *unchanged* fixture first reproduces the committed snapshot byte for byte (`7d30e7e6…`).
  - The C4 graph difference is exactly one occurrence, 12 attributes and 1 calc. A license-free simulation predicts the resulting digest (`6d8e5845…`).
  - The C3 regression uses a real model. It goes through both live and from-snapshot generation, with a multibyte shift that crosses to the next line, on a declaration a calc actually consumes. The license-free arithmetic test stays as a supplement.

**L3-4 · Direct claim:** Three regression paths from C2 and C5 reach customer bytes, and no current criterion would catch them.
- **C2 implemented through Pydantic.**
  - Pydantic writes `1e16` where stdlib `json.dumps` writes `1e+16`. That moves `semantic_fingerprint`, and every TEAx study store then refuses to resume (`simkit/study/compatibility.py`).
  - Codegen fixtures have no exponent-form defaults. Customer contracts do: 15 in `stellarator_tea`, 9 in `aries_integrated`.
  - So SC2's "finite bytes stay identical" can pass on codegen fixtures while the customer's fingerprints move.
- **C5 is larger than the 27 errors.**
  - mypy's `check_untyped_defs` is off. Annotating the 16 untyped functions exposes 11 more `str | None` errors, in `stencils.py`, `modules.py`, `test_gen.py` and `preservation.py`.
  - They come from the optional `PipelineModule.calc_def_name` (`resolution/models.py:235-236`). All 29 constraint and report-aggregator modules carry `None` there.
  - A guard at the wrong level would refuse every package with constraints. Existing license-free tests catch that case.
  - A guard raised after the output directory is cleared (`cli/__init__.py:1278`) would leave a partial tree labelled as an internal defect.
- **C5 narrowing in `preservation.py:175`.** If it changes the expected signature, customer handwritten implementations are judged "signature changed", backed up, and overwritten with stubs. No committed snapshot exercises preserved handwritten code. Only a customer acceptance run would catch this.
- **What needs to be true:**
  - Finite contract bytes are unchanged across the full finite float range, exponent forms included.
  - Any new refusal is a named error raised before output is cleared.
  - Existing handwritten implementations survive regeneration in a real package.
  - `contracts/verify.py` is untouched, so `TRUSTED_VERIFIER_SHA256` (`contracts/versions.py`, vendored into TEAx) does not move.

**L3-5 · Rewrite request:** SC2 should pin what the user sees at the public route, not only the encoder.
- **The outcome.** A model or snapshot carrying a non-finite value is refused by name, before any output is written, on both routes.
- **A small existing mislabel.** The snapshot route labels this refusal `SI_INTERNAL_DEFECT` (`snapshot/envelope.py:552`). The spec could take it or file it.
- **One more writer to scope.** `generation/entry_point.py:130` also writes input JSON without `allow_nan=False`. The spec should say whether it is in scope.

**L3-6 · Direct claim:** The real-TEAx lane can silently test the wrong code.
- **Where it gets codegen.** It imports codegen from an archived root named by a `CODEGEN_EXECUTION_PROVENANCE` manifest, not from the working tree.
- **The trap.** Running it against the research's archive proves nothing about the candidate.
- **What needs to be true.** SC11 says the manifest is built from the PR candidate commit.

**L3-7 · Direct claim:** SC7's gate as worded conflicts with other checks and over-trusts a single mutation.
- **Whitespace conflict.** Generated stubs carry trailing whitespace; `fusion_tea` alone has 36 `git diff --check` hits. SC11's whitespace check would flag committed expected output, and stripping the whitespace breaks the byte match.
- **Test collection and lint.**
  - Generated packages include `tests/test_implementations_runnable.py`, which imports `simkit`. Committed under `tests/` without an exclusion, it breaks pytest collection.
  - Ruff would lint or rewrite expected files. The existing golden already fails `ruff check` with 5 errors.
- **One mutation proves too little.** "A real template mutation fails the gate" proves the gate runs, not what it covers. No committed snapshot exercises stub generation, handwritten preservation, smart regeneration, or non-float outputs.
- **Version churn.** `generator_version` in `package_contract.json` would churn every expectation on each version bump.
- **What needs to be true:**
  - The expected output sits outside test collection, lint and whitespace checks.
  - The gate fails on at least one mutation per named shape, plus one mutation in rendering code.
  - Its uncovered paths are listed.
- How the output is stored is design's choice.

**L3-8 · Direct claim:** Several C6 and SC11 specifics are wrong or weaker than they look.
- **The skip C6 would tighten is in dead code.** It is at `tests/conftest.py:139-140`, not `:144`, inside `sample_extractor`, which has no users. In fact none of the 12 root-conftest fixtures has a user, and `expected_outputs_path` points to a missing directory. The right move is deletion.
- **The license probe can be wrong.** "Once a valid license is established" relies on a probe (`conftest.py:24-37`). If `chain_spike_model` ever stops loading under a valid license, about 1,004 tests skip as unlicensed.
- **The skip branch doesn't need the probe.** A `load_models()` result of False means the model has errors, never a license problem. That branch can fail unconditionally.
- **The nine parity skips are not "explained."** Those fixtures are simply missing from the golden file. At least four of them have calculation output expressions: `gate_a`, `shared_producer`, `crosspart_rollup_twolevel`, `modeled_default_fidelity`. That is a coverage gap.
- **More markers in Agentic.** Agentic carries 14 more `snapshot_exclude` markers and 2 tests for them. The spec should say whether they are in scope.
- **C6 and C9 are coupled.** REQ-EXT-07 (`verification-matrix.md:396`) rests on the metadata self-check that C6 removes, so the two must move together.
- **SC11 misses one ledger check.** It runs the ledger `paths` and `surface` checks but not `replacements`. C4 edits `test_customer_fixture_lenient_diagnostics_are_accounted_for`, which three ledger-4a rows cite as replacement proof. That test's name must not change.

**L3-9 · Direct claim:** C8–C10 edit text that tests pin, and the spec protects some kinds of checks but not provenance checks. Known Requirement 3 protects typing, licensing, refusal and guidance checks. It does not protect provenance guards, and those are exactly what C10 rewrites.
- **Close provenance is pinned to text.** `test_register_contract.py:223-236` pins strings in `CURRENT_WORK.md` and the epic file: the parser-close strings, two SHAs, "Needs Work", and the diagnostic-debt tag. It also pins a path that has since been purged.
- **The backlog test reads only first occurrences.** `:184-220` checks only the first entry for each backlog tag. That entry must contain "AGENT" and must not contain "settled". Deduplicating the P1 and P3 entries can break the test, or quietly settle the P1/P3 conflict while it still passes.
- **C8's docs are pinned too.** `:126-144` pins terms in exactly the documents C8 rewrites.
- **Doc deletion hits a floor.** `test_reference_doc_distinctness.py` needs at least 15 numbered docs. Deleting 02, 06, 18 and 26 leaves exactly 15.
- **Dangling references.** Removing backlog tags leaves dangling references in the matrix (`:30`, `:71`) and in `modeling-assumptions.md:397`.
- **Matrix counts are unguarded.** Only one test reads the matrix, and it checks only one row. SC9's corrected counts will drift again with nothing to stop them.
- **What needs to be true:**
  - Provenance guards keep equal force when retargeted.
  - No backlog tag reference dangles.
  - The matrix counts come from something that can be rerun.

**L3-10 · Direct claim:** Nothing keeps the drafts out of the PR, and isolating the branch can lose the spec itself.
- **Current state.** Sixteen mental-alignment drafts are staged on `main`. The spec, research and product lens are untracked. `CURRENT_WORK.md` and `BACKLOG.md` have unstaged edits.
- **Both obvious options fail.** A clean worktree from HEAD drops the spec and the research. Branching in place carries the staged drafts, and any commit without a pathspec includes them.
- **Half the research's rule was dropped.** The rule was "no unrelated mental drafts included or discarded". SC10 kept only the "discarded" half.
- **What needs to be true.** The PR diff contains no `.project/mental-alignment/` file, and the drafts stay exactly as they are.

**L3-11 · Rewrite request:** SC11 and SC12 mix outcomes with process.
- **The process parts.** "Record commands, dependency revisions…" and "Independent final review covers…" are instructions for how to work, not states of the product.
- **Keep the outcomes.** For example: "the evidence record names each identity and separates fresh results from inherited ones."
- **Move the rest.** The review choreography belongs in the plan.

### Lens 4 — Hygiene

**L4-1 · Rewrite request:** The research's line citations have drifted, and design will inherit them.
- The CLI help strings are at `cli/__init__.py:1045`, `:1082` and `:1092`, not `:1046` and `:1075`.
- The overview's report claim is at `overview.md:47`.
- The conftest skip is at `:139`.
- The caller of `canonical_json` is at `model_contract.py:69`.
- The research's README list misses `README.md:14`, `:17` and `:24`, which use non-existent `~/sysml-codegen` and `~/agentic-mbse` paths.

The spec doesn't need line numbers. It shouldn't call the research an exact index while these are off.

### Lens 5 — Reader Comprehension

**L5-1 · Rewrite request:** The success criteria can't be read without the research open. Each criterion packs five to ten obligations and leans on coined terms the spec never defines:
- "remaining-owner mutation"
- "located enum-refusal", which is also wrong (see L1-3)
- "every-and-only"
- "composed-proof"
- "durable lifecycle/Item-3 authorities"
- "self-binding guidance contract"

SC11 alone lists eleven checks. Each criterion should lead with a plain outcome the reader can verify, and each coined term should be defined in plain words or linked to its home. SC11 should become a short list.

---

## Engagement Summary

**Overall take:** This is the right cleanup, and the defects it names are real; reviewers reproduced or simulated almost every one. As a contract against regressions, though, it is weak:
- It has no oracle captured before the fixes.
- Its criteria test encoders and unit functions, not public routes and real packages.
- A failed license makes the suite look green, and nothing in the criteria catches that.
- A few premises need correcting before design builds on them.

**Here's what I need you to weigh in on:**

1. **[L2-1]** Where is the PR finish line? Recommended: a cleanup PR with Item 8's assurance left visibly open. The alternative is that this PR also carries the composed proof, the lineage and the attestation.
2. **[L2-2]** What is C3's scope? Recommended: the offset fix plus a test pinning today's prose behavior, with the prose-unit rule filed separately. The alternative is tightening the prose rule now, accepting the loss of `Fraction` and a recapture of `catf_mfe_gated`.
3. **[L2-3, L1-1, L1-3]** Does convergence with the 2026-08-16 customer (`9e1ff87bb`) satisfy your L2-2 ruling? And do you approve amending your accepted v6 recapture batch record (the `fusion_tea` row, `9/27/1/7` → `8/23/1/5`) as part of C4?
4. **[L2-4]** Should the PR's acceptance include one customer check: regenerate with the candidate wheel and compare fingerprints, or run the acceptance suite from an archived copy? Or should the PR body just record that the customer stays on `8a758e92`?
5. **[L1-6, L3-1, L3-2, L3-3, L3-4]** Do you accept this functional regression floor?
   - Complete generated output for all 22 committed snapshots, captured at `6872977` before any code change, with the candidate matching it except for reviewed differences.
   - A licensed check that no committed snapshot has gone stale.
   - A final licensed run with zero "no live syside license" skips.
   - Refusal tests for non-finite values at the public route.
   - Handwritten code preserved through regeneration in a real package.

---

## Resolutions

- **[L2-1]** Owner ruling, 2026-10-07: Item 8's four remaining assurance pieces are out of scope, each for the owner's stated reason. `[OWNER-VERBATIM]` quotes:
  - **End-to-end proof (downstream SC6–SC7): not required.** "I was doing ALL of fusion-tea's stellarator demo (full run-goal, end to end harness work) with this, so I have no concerns that this is working."
  - **Copied-store refusal (downstream SC9): not required.** "no, I don't really care about that"
  - **Lineage record (downstream SC8): descoped.** "no, descope that feature"
  - **External-use attestation (downstream SC12): not required.** "no, I don't care. we ended up rebuilding all of the models and rerunning everything"
  - **July impact report (downstream SC10–SC11): retired.** Owner, asked whether the rerun also retires the impact report: "Retire it". One line records that the July study outputs are superseded by the rebuilt models and rerun. The July files stay as they are; no census, consumer list, or fusion-tea write-up correction.
  - **Effect on the spec (L2-1).** The Open Questions "PR finish line" and "Historical evidence" are settled. The Known Requirement preserving the 2,294-of-2,301 verdict and its retained-store bounds is replaced by the one-line supersession record. `[AGENT]` consequence for the spec agent to confirm: Item 8 has no proof work left, so the cleanup's SC9 (`REQ-SI` rows) and SC10 (an outcome for each of the 21 old criteria) can close Item 8 in this PR.
- **[L2-2]** Owner ruling, 2026-10-08: codegen stops reading units from declaration comments. `[OWNER-VERBATIM]` "throw it away". This is the owner's final call after two same-day intermediate answers ("remove it", then "yes brackets only."), given once the reviewer established that nothing validates comment units anywhere.
  - **Why (facts the ruling rests on).** agentic-mbse's guidance asks authors to write `// [units] - Description` (`agentic-mbse docs/patterns/syntax-reference.md:59,63`), but no agentic-mbse validation level reads `//` comments or checks units (`src/agentic_mbse/validation/level1-6`). Codegen guesses the unit from the comment's first word. Its only effect beyond a docstring label is the shared-input consistency check (`elaboration/project.py:498-507`), which refuses a model when two readers of one input carry different labels, with a message that does not mention units. Nothing checks units along a producer-to-consumer dataflow.
  - **What goes.** All three unit guessers in `extraction/feature_metadata.py`: the comment reader (`:81-120`, and with it the wrong-line byte-offset bug), the doc-text reader (`:154`), and the type-to-unit table (`:13-35`). The last two were added by owner answer `[OWNER-VERBATIM]` "yes remote them" (read: remove), on the measured fact that neither produced a unit in any of the 47 models. The `// [units]` convention remains a note for human readers; agentic-mbse guidance needs no change.
  - **What stays.** Parser-native units on written values (`= 40.0 [W]`), which agentic-mbse resolves to real SI units and its constraint checker already uses (`sysml/expression_facts.py:39-48`, `sysml/executable_profile.py:76-79`).
  - **Corrected reviewer claim.** Quantity types are not an alternative today. Codegen refuses `ISQ::*Value` attribute types (`elaboration/elaborate.py:2081-2085`).
  - **Measured effect (2026-10-07, live licensed route, comment reader on vs off, 47 models).** No model's outcome changes. Customer IFE: no change. Customer MFE: 68 labels drop from generated descriptions (kg 51, s 3, and 14 wrong `T` from `// T atoms`). Test models: only `catf_mfe_gated` changes, losing 59 labels; its committed snapshot needs a licensed recapture and it enters the regression oracle's reviewed-difference list (L3-2). One more is affected but could not be measured live: `catf_mfe_d5` has no source files at HEAD (collapsed by REPO-CLEANUP Move C; `scripts/make_d5_variant.py catf_mfe_model catf_mfe_d5` regenerates them). Its committed snapshot carries the same comment-derived unit set as `catf_mfe_gated` (MW, m, Dimensionless, m³/s, K, Pa, T, Fraction), so it goes stale too and needs its sources regenerated and a licensed recapture. A brackets-only variant was also measured and rejected: it turned `catf_mfe_gated` from generating to refused.
  - **Effect on the spec.** SC3 becomes removal of the comment reader. The Open Question "Unit-comment compatibility" is settled. The spec's statement that existing bare comment units cannot be discarded as incidental cleanup is superseded: they are dropped by owner decision. Backlog `UNIT-SCRAPE-BYTE-OFFSET` is resolved by removal.
  - **Customer.** Nothing changes while fusion-tea stays pinned. At a repin its generated docs lose those labels, and its ASCII comment workaround (`models/stellarator_migration_ledger.md`, row F3) is no longer needed.
- **[L2-3, L1-3]** Question withdrawn by the reviewer, 2026-10-08; no owner judgment is involved. `[AGENT]` C4 deleting `hif_driver_instance` carries out the owner's existing ruling (`.project/active/elaborator-downstream/spec-review.md`, Resolution L2-2, 2026-08-16). Updating the fixture's counts in `tests/fixtures/v6_recapture_batch/batch.json` and breadth-ledger row 15 (`graph 9/27/1/7` → `8/23/1/5`) is a mechanical consequence of that ruling, not a new decision; the owner was informed 2026-10-08. The post-C4 fixture is byte-identical to fusion-tea `9e1ff87bb:models/` (2026-08-16); record that as the fixture's provenance. Whether codegen's tests should also prove the *current* customer model is the separate L2-4 question.
- **[L2-4]** Owner ruling, 2026-10-08: find out before the PR whether the new codegen breaks the current customer models. `[OWNER-VERBATIM]` "Now. find out now, before we PR". Asked as a judgment: learn now, inside this PR, or at the next fusion-tea pin update.
  - **Effect on the spec.** A new success criterion: the PR candidate generates fusion-tea's current models (every model family fusion-tea generates, IFE and MFE) and fusion-tea's own acceptance tests pass against them, at a named fusion-tea revision, without modifying fusion-tea. Known expected differences: MFE's generated docs lose 68 unit labels (L2-2), and fingerprints change. Any other difference is a finding.
  - **Baseline now (2026-10-08).** Customer fusion-tea `582f6f932`, generated with its pinned codegen `8a758e92` (agentic-mbse `c37ff53b`) and with codegen `main` `6872977` (agentic-mbse `8f43a09`), same fusion-tea venv, same TEAx (`/home/reid/1cfe/teax`), license loaded. **Packages are byte-identical** for all three customer cases (IFE canonical subset 55 files, IFE exploration tree 55 files, MFE 443 files; compiled caches excluded). Both IFE packages execute in stock TEAx with the same package fingerprint and the same values on all 35 output channels. This fits the code delta: 114 commits lie between the pin and `main`, but they change only 18 source files (+20/−2,693 lines, almost all retirement). fusion-tea's own codegen-dependent tests (`test_codegen_teax_acceptance.py`, `test_occurrence_mutation_teax.py`, `tests/models/test_ife_*`) give the same result under both codegens: 6 acceptance failures in both, which compare against stale expected channel sets (`test_codegen_teax_acceptance.py:142`) and match fusion-tea's own 2026-10-07 pre-PR report. They are fusion-tea test debt, not codegen regressions. fusion-tea's model-family tests (`tests/models/test_model_family_spines.py`, 15 tests, including the IFE and MFE mutation-reaches-every-and-only-its-consumers checks and the MFE live-equals-snapshot check) pass 15/15 under both. Method: an archived copy of fusion-tea's committed tree, the new codegen and agentic-mbse placed ahead of the venv's on `PYTHONPATH`; fusion-tea's working tree and venv were not modified. Scripts: session scratchpad `ft_check/`.
- **[L1-6, L3-1, L3-2, L3-3, L3-4]** Adopted, 2026-10-08, without a separate question: this regression floor is the concrete form of the owner's original request, quoted at the top of this review (`[NEED]`, owner-stated: success criteria must include real functional tests against regressions from the fixes). The specific checks are `[INFERRED]` answers to that need:
  - Before any code change, save the complete generated output of all 22 committed snapshots at `6872977`, including refusal outcomes, durably in the repo. The candidate must match it except for a reviewed list of intended differences (C4's six `fusion_tea` files; C3's dropped labels in `catf_mfe_gated` and `catf_mfe_d5`).
  - Under the license, no committed snapshot is stale against live elaboration except the intended recaptures. Source-collapsed fixtures (`catf_mfe_d5`) need their sources regenerated first.
  - The final licensed run shows zero "no live syside license" skips, and its skip set is exactly the expected one.
  - Non-finite values are refused at the public route, before any output is written.
  - Handwritten code survives regeneration in a real package.
  - The customer differential from L2-4.

---

**Verdict:** Revise
**Next Steps:** Once resolutions are recorded here, re-run `/_my_spec` (or return to the spec-agent session) and point it at this review to incorporate them. The reviewer does not edit the spec.
