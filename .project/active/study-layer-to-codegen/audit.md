# Audit: Move the study layer to sysml-codegen (WRAP-SPLIT Item 3)

**Verdict:** Needs Work — one Blocker (F1), narrow and with a ruled remedy. SC9 is pending the rehearsal. Once F1's fix lands and a targeted re-check passes, this item reads as **Certify with follow-ups**.
**Audited:** 2026-10-12, by a fresh session that authored none of the work.
**Branch:** `study-layer-to-codegen` (base `aa35f06`)
**Commit:** `ff893fd` (clean tree). `src/` and `pyproject.toml` are unchanged since `f44c991`, the install transcript's commit. `src/sysml_codegen/study/` is unchanged since `aac1290`, the parity run's commit. So the stored evidence applies to HEAD.

---

## The Point

The study capability (the `run-study` skill, its runbook and record template, the study-policy rulebook, and the tools under fusion-tea's `scripts/study/` plus `integrate.py`) existed only inside fusion-tea, and nothing installed it. A new modeling project that uses sysml-codegen and teax could not run a study without hand-copying fusion-tea files.

- [OWNER] (epic header, 2026-10-06): the study layer ships from sysml-codegen, which owns the generated-package contracts the tools read. [OWNER-VERBATIM] "ported and generalized … installed like everything else".
- [AGENT] (orchestrator, uncontested): the bar is a working capability in a fresh target, not copied files. A target installs sysml-codegen, runs `sysml-codegen install-commands`, and can then run a study from intake to a committed record and hand it to a second agent, with nothing from fusion-tea.
- [NEED] The owner's shape survives:
  - a lightweight skill, a runbook, a policy rulebook and tools;
  - indicators inform and never gate;
  - intake is collaborative;
  - one skill serves the executing and administrator roles;
  - an axis nothing pushes back on is surfaced as a sign the model is underdeveloped.
- [NEED] fusion-tea loses no information. Every fusion-specific line removed from the shipped text has a fusion-tea home before the removal merges.
- [INFERRED] Tool behaviour moves byte-faithfully except for the closed list B1–B13 (ADR-0007's lesson). `integrate` judges any target, not just fusion-tea.

## Summary

The work is the right piece of work, and it is well built.

- `sysml_codegen.study` is a clean, bounded package. One module (`roots.py`) answers every "where is it" question and is the one environment reader. One module (`declarations.py`) turns fusion-tea's hard-coded facts into strict, default-free target data. The installer is a thin, lazily loaded layer over agentic-mbse's, guarded by an API pin.
- The port is byte-faithful where it claims to be. Every hunk of the eight ported modules maps to the import rewrite, B1–B13, or an SC5 docstring edit, and parity re-reports byte-identically.
- Every suite I asked for re-ran green. Every evidence claim I spot-checked reproduced.

One defect blocks: B13's rule lets one environment variable switch off gate 7 (F1). The orchestrator has ruled the remedy. The other findings are advisory. The most important of them is that the item's follow-ups exist only inside the item folder, which close deletes (F2).

## Product Judgment

**Is this the right piece of work? Yes.** The product-lens (block "audit — 2026-10-12", appended to `product-lens.md`) re-derived the point independently and found no [DON'T] at owner, owner-verbatim or [HARD] grade. Gate: CLEAR.

- **The owner's shape holds in the shipped text.**
  - `SKILL.md` is 58 lines and delegates to the runbook, policy and tools.
  - Only mechanical conditions stop a study (`runbook.md:13`; policy template § 9).
  - Intake is flexible, with "no questionnaire" (`SKILL.md:44`).
  - One skill has both modes (`SKILL.md:25-38`).
  - The owner-verbatim "nothing pushes back" rule ships (`runbook.md:56`; policy template `:137`).
- **The dry run proved it end to end.** An unresisted axis came back `no_constraint_response`, the operator ruled, and the model-development finding was filed. A cold administrator then wrote the synthesis from the record alone (`evidence/dry-run/run-20261012/RESULT.md`).
- **No glue route or era pin is presented as general practice.**
  - The glue disclosure is conditional, with "glue ledger: none" as the expected case (`runbook.md:94`).
  - The era pin is a conditional disclosure only (`runbook.md:139`; `record-template.md:317`).
  - The fixture route is stock teax with no glue.
- **Earlier lens blocks.** Every earlier finding (spec-F1–F6, design-F1–F5) is still resolved in the code. The one exception is spec-F5's product-ledger entry, which is planned for close and not yet written (F2).
- **Structural smells.** One fired in a way that matters: gate 7 reads a setting the environment controls (F1). Gate 4's fixed `*.snapshot.json` glob makes a target know an internal rule (`integrate.py:1132-1141`). That one is a named design follow-up (DD19) and is folded into F2. The B13 "special category" smell is the closed-list item itself, with its caveat stated, so it is accepted.

## Blockers

**F1 · Blocker · One environment variable can switch off gate 7's read-coverage check.**

- *The defect.* B13 counts reads under the interpreter's time-zone search path as runtime reads. The observer takes that path from `zoneinfo.TZPATH` (`src/sysml_codegen/study/read_coverage.py:93-94`), and `classification` returns `runtime-observed` for anything under it (`:137`). `zoneinfo.TZPATH` comes from the `PYTHONTZPATH` environment variable when that is set. `seam_env` hands the caller's environment to the route driver.
- *Reproduced.* `PYTHONTZPATH=/` gives `zoneinfo.TZPATH == ('/',)` (`.orchestrate-logs/audit-probes/7.txt`). With that root, every read outside the package that is not declared counts as `runtime-observed`, so an undeclared read of a project data file passes gate 7. A `CANDIDATE` can then certify a route that read a dependency nobody declared. The gate fails open.
- *Why it matters beyond gate 7.* ADR-0017 says `roots.py` is the study package's one environment read. That holds as text, because the conformance grep sees only sysml-codegen source, but not in effect: the standard library reads this variable for the observer.
- *Cause.* The orchestrator's own wording of B13 ("follow `zoneinfo.TZPATH`"), as the orchestrator has ruled [AGENT, 2026-10-12]. The implementation follows B13 exactly.
- *Remedy, as ruled.*
  - B13 follows the interpreter's build-time default, `sysconfig.get_config_var("TZPATH")`, which no environment variable overrides, and ignores entries that are not absolute paths. On uv's CPython and on `/usr/bin/python3.12` the default holds the same four directories (`7.txt`).
- *What the fix pass must also touch.*
  - `tests/study/test_read_coverage.py:113-140` makes the rule fire by setting `PYTHONTZPATH`. That test pins the fail-open mechanism as intended behaviour, so it must be rewritten. Add a test that `PYTHONTZPATH` does not widen the runtime roots.
  - The spec's B13 receipt-consequence paragraph and `evidence/parity/preloads.json` list a `zoneinfo` preload group, measured because the observer imports `zoneinfo` before observation. If the fix drops that import, re-measure the preload set and amend that paragraph.
  - Re-run parity. The plan's own trigger fires, because `read_coverage.py` changes.
  - Re-run the teax lane: gate 7, gate 8 and `CANDIDATE` on the station all go through this observer.

## Advisory

These do not block. They are ranked by importance.

**F2 · Follow-ups and the product-ledger entry exist only in the item folder, which close deletes.**

- *The concern.* `.project/README.md:44-52` says close means record, then delete the item folder. None of this item's follow-ups is in `.project/backlog/BACKLOG.md`, and grep finds no match. The study-layer product-ledger entry the spec and design promise at close (spec `:239`, design `:457`) is not in `.project/product/INDEX.md`, which lists 0001–0006.
- *What would be lost.*
  - F-DR1 (a resume path for a stopped record). RESULT.md says "filed as a follow-up", but it is filed nowhere durable.
  - DD12's `sysml-codegen study check-record`.
  - DD19's kept smells, including gate 4's `--snapshot` flag. The README's snapshot command writes `instance_graph_snapshot.json`, which gate 4's glob rejects (product-lens audit-F2).
  - The plan's "Proposals, not applied".
  - F3, F4 and F5 below.
- *If unaddressed.* The follow-ups vanish into git history, and P-004's parse-walk-emit definition goes on reading as if it excludes a layer the README now claims.
- *What should change.* At `/_my_close`, file each follow-up in the backlog and add the product entry with `product.sh`, citing the owner's 2026-10-06 decision.

**F3 · A literal copy of the record template fails the runbook's own placeholder check.**

- *The concern.* `record-template.md:3` says to copy the file and drop only the text below END OF RECORD. The copied preamble holds `<` at `:3`, `:9`, `:13` and `:15`. The step-15 Check counts every `<` in `record.md` and must print 0 (`runbook.md:171-172`).
- *Effect.* It fails safe: a bad record is never passed. But an executor who follows the template exactly trips the check. A record that states a constraint as `x < y` cannot pass at all. That rule is inherited from fusion-tea's record test; the collision with the preamble comes from the new Check lines (DD12).
- *Missed by the dry run.* The dry-run agent quietly rewrote the preamble: its record holds no `<`. RESULT.md does not record that, so the dry run missed this finding.
- *What should change.* Move the preamble below END OF RECORD, or state that it is not copied. File this with F2.

**F4 · F-DR2 names the wrong cause.**

- *The concern.* F-DR2 says the fixture route lacks a points-based entry. It has one: `run_points` (`tests/fixtures/study_station/studies/study_route.py:44`). The grid was fixed because the dry-run brief named only `execute_baseline` and `run_grid` (`evidence/dry-run/brief.md:29`).
- *The real gap is in the shipped contract.* It leaves the point runner open: "and whatever runs the study's points" (`runbook.md:261`). So a route that fixes its grid in code satisfies the contract and still defeats step 7's rule that the window is chosen after the oracle scan (`runbook.md:83`).
- *What should change.*
  - Correct F-DR2's wording.
  - Requiring the point runner to take step 7's window would change study semantics. That is the owner's or orchestrator's call, as a follow-up.

**F5 · Two inherited error paths in `integrate` report a caller's mistake as a seam fault.**

- *The paths.* Both were found where the `index` mypy override hides errors.
  - A `--census-file` that is valid JSON of the wrong shape, or lacks `derived_against_semantic_fingerprint`, raises `KeyError` or `TypeError` at `integrate.py:1206-1221`. That reaches the catch-all at `:1621` and comes back as `seam-internal-error`, exit 2.
  - A baseline result without `executed_under.store_id` raises `KeyError` at `:1298`. That escapes the `ToolError`-only handler at `:1350`, also exit 2.
- *Effect.* Neither fails open. Each says "the seam broke" for a caller's error. Both are byte-faithful to `b06585709`, so fixing them belongs after adoption, outside this move.
- *What should change.* Map these to gate-4 `input-invalid` and gate-7 `could_not_run`. File with F2.

**F6 · ADR-0015's invariant is wider than the library rule the code implements.**

- *The concern.* Called as a library, `identity.build_sealed` resolves the root from the working directory's work tree, not the package's (`roots.py:82-86`, `:169-179`). The runbook says so (`runbook.md:244`). ADR-0015 states "the same from any working directory" with no library exception (`.project/adr/0015-study-root-anchors-to-the-package-work-tree.md:28`).
- *Effect.* A route run by hand, with the working directory in another repository, writes `..` paths into `package_identity.json`, and no check compares them. Under `integrate` and `run_route` the root is pinned from the package, so the tools' own paths are safe.
- *What should change.* Narrow the ADR to command-line documents and state the library rule, or anchor `build_sealed` on its `package_root` (inside B1). This is product-lens audit-F3.

**F7 · B1's refusals reach three cases that design DD2 said would fail "as before".**

- *The cases.*
  - A `--package` path whose nearest existing ancestor is outside every work tree now exits 2 with "no project root", where it used to exit 1 naming the missing file (`roots.py:189-194`, `:205-210`).
  - `indicators --print-fingerprint` for a package outside every work tree exits 2 (`indicators.py:962`), though it cites no root-relative path.
  - `integrate` with `--package` missing, run from a directory outside every work tree, exits 2 with no return. Its message calls the working directory "the package" (`roots.py:192`).
- *Effect.* Each is a B1 refusal the design accepts in principle (premise conflict 4 lists the B1 exits), and none fails open. DD2's sentence overclaims.
- *What should change.* Amend DD2's wording or the message. Optionally, exempt `--print-fingerprint` from the root check.

**F8 · The shipped text has a little fusion residue, and six lines have no read-through verdict.**

- *What is clean.* SC5(a)'s identifier grep passes. The skill, runbook, record template, annex template and guide are clean.
- *Residue in the policy template* (`src/sysml_codegen/assets/project_templates/STUDY_POLICY.md.template`):
  - `:16`: an unlabelled parenthetical, "(beta ≤ limit, wall load ≤ limit, TBR ≥ floor, rec_frac ≤ knee)";
  - `:17`: "a confinement scaling must hold", unlabelled;
  - `:29`: "geometry (R, a, kappa) … density" inside the [OWNER] rule. Read-through row SP-7 calls this a labelled example, but it is not labelled. It is owner-graded, so any rewording goes to the owner;
  - `:54` and `:78`: "oracle-mirrored at 1e-9", fusion-tea's practice stated as general;
  - `:82`: "the analyses layer";
  - `:153`: "source quarantine", a rule the template does not have;
  - `:6` lists the fill-ins as §§ 6, 7, 8 and 10, but § 1 also has one (`:21`).
- *Elsewhere.*
  - `integration-guide.md:200`: "The numbering is the requirements'" points at fusion-tea's seam requirements.
  - `runbook.md:130` names goal-process stages with no citation and no fallback.
- *Lines with no read-through verdict:* POL `:17`, `:80` (`p_nrl`/`p_input`, inside a labelled example), `:82`, `:153`, `runbook.md:130` and `integration-guide.md:200`.
- *Smaller slips.*
  - `runbook.md:259` omits the required `--package` on `--print-fingerprint`.
  - `teax-completion.md:58` names `generate_scenario.py --generate-inputs`, which does not exist in sysml-codegen. That line predates the item, but the file now ships to every project.
- *Effect.* None of this misleads a non-fusion reader into fusion practice. A tired reader would trip on the jargon. The owner's bar (fusion vocabulary only in labelled examples) is met at intent but not to the letter.
- *What should change.* One text pass, with the six read-through rows added. It can ride with F1's fix pass.

**F9 · sysml-codegen reads `Installer.files`, which `installer/v1` does not cover.**

- *The concern.* `cli/install.py:131-132` passes `relative in installer.files` to choose the conflict message. The agentic-mbse comment that defines `installer/v1` does not list `files`.
- *Effect.* If agentic-mbse changes `files`, the message could name the wrong reason; the action (skip) would not change. The plan records this.
- *What should change.* Add `Installer.files` to the `installer/v1` comment at agentic-mbse's next API revision, or read the manifest file directly.

**F10 · Merge-prep items are still open (O5).**

- `cli/install.py:42` `INSTALLER_API_REVISION = "0843fe2"` and the README must both move to the agentic-mbse merge SHA. A test holds them equal.
- `.project/adr/INDEX.md` will conflict at the merge with `main` (ADRs 0011–0014). Resolve it with `adr.sh index`.
- ADRs 0015–0017 are [AGENT], approved by the orchestrator, not owner-ratified.
- The fusion-tea branch `study-layer-adoption` is unpushed. SC10's homes exist only in that worktree until the owner pushes it.

## Findings Detail

### Plan completion

All phases are verified complete: A and 1–6, with every checkbox already ticked by the implementers.

- Each phase's deliverables exist at HEAD.
- Each recorded deviation is declared in Implementation Notes.
- No placeholder code or TODO turned up in the new modules.

Orchestrator steps:

- O1 (SC1), O2 (SC4) and O4 (SC10) ran, and their evidence is committed.
- O3 (SC9) is running.
- O5 is open (F10).

Cuts: none applied, as the plan records. `CANDIDATE` is reached.

### Spec conformance

| Criterion | Result | How checked |
|---|---|---|
| SC1 fresh install from wheels | Met | The install transcript shows 25 of 25 checks at `f44c991` / `db032d6`, and `src/` is unchanged since. The wheel rebuilt from `git archive HEAD` lists the 7 assets and 7 schemas (`audit-probes/5.txt`). `test_install_commands` (27) is green in the suite. |
| SC2 ownership on re-install | Met | `test_install_commands` covers refresh, preserve, prompt, policy kept and `--force`, and coexistence both ways with `agentic-mbse init`. The transcript's re-run and init-order checks pass. The agentic-mbse installer diff is design Appendix B exactly (`agentic-mbse-branch.diff:119-224`). |
| SC3 tools complete and fail closed | Met | Suite and teax lane re-run green (28 passed, including `CANDIDATE` with all ten gates). Each tool's fail-closed cases cite their docstring lines (plan Phase 2 notes). F1 is a separate correctness defect in gate 7's allowance, not an SC3 gap on the fixture. |
| SC4 dry run from installed files | Met | `check_record.py` re-run on the record passes 5 of 5, and its self-test agrees with the shipped Check lines (`4.txt`). The administrator synthesis exists. Ready-made pieces are named. One missed finding (F3); F-DR dispositions are below. |
| SC5 shipped text and tools are generic | Met, with F8 | (a) `test_generic_text` is green in the suite. (b) The read-through was sampled at about 45 of 126 rows; all matched their verdicts but SP-7, and six lines have no row (F8). |
| SC6 compatibility surface | Met | `test_compat_surface` (33, all 32 consumer names) is green. |
| SC7 tool identity; old records valid | Met | Schema `diff -r` against `b06585709` is empty (run by the auditor). `test_tool_identity` is green, including the pre-move documents and the sha256 pins. |
| SC8 integrate judges any target | Met | `test_integrate_declared` is green. `declarations.py` refuses a gate without `checked` and has no default (`:122-130`). An undeclared gate raises `unasked` (`integrate.py:986-999`). The edit map found `REQUIRED_ENV`, the toolchain keys and gate 1b's order as specified. |
| SC9 rehearsed adoption runbook | **Pending** | The rehearsal is running. The runbook draft was reviewed for hazards (below). |
| SC10 no loss for fusion-tea | Met | 74 moved rows, each in exactly one of 15 ledger rows. The rows landed verbatim in agentic-mbse `db032d6`. `check_anchors.py` at fusion-tea `699b0a74d` gives 74 found, 0 missing (`q3.txt`). About 40 rows were content-checked: the information is preserved, not just the anchor. No silent drops. |
| SC11 suites pass | sysml-codegen part met; agentic-mbse part not re-run | Full suite: 2741 passed, 9 skipped, 1 failed (the known self-binding test), 124 deselected (`1.txt`). ruff clean; mypy clean in 85 files (`2.txt`). The agentic-mbse suite (2214 passed, 18 failing on optional extras) rests on the implementer's record; I did not re-run it. |
| SC12 byte-faithful parity | Met | Re-reporting Phase 6's stored runs from a copy of the evidence is byte-identical to the committed `report.md`, `results.json`, `cases/` and `preloads.json` (`2b-parity.txt`, empty `2b-parity-diff.txt`). F1's fix will require a re-run. |

**Requirements beyond the SCs.**

- **The owner's shape: held** (Product Judgment).
- **B1–B13: all present, and no edit falls outside them.**
  - The 79 hunks over `cc81258..HEAD` classify as: import rewrite 8; B-items 44; SC5 or B-made-false docstrings 27; outside the list 0.
  - `cc81258` itself is byte-identical to the staged originals.
- **The dependency stays one-way.** The agentic-mbse diff has no mention of `sysml_codegen`.
- **The study package reaches the rest of sysml-codegen only lazily,** through `snapshot.capture` (`integrate.py:1147`).
- **Non-Goals were respected.** No committed record was touched, and no fusion-tea main checkout or pin was changed.

### Design conformance

The code follows the design. Components sit where the Component Overview puts them. DD1–DD20 are followed.

Declared deviations, each with its reason in the plan:

- `require_project_root` takes a required anchor, and the override is kept apart from the command-line pin.
- `IntegrateDeclaration.gates` is a read-only `Mapping`.
- integrate reads `TEAX_SIMKIT_PATH` from the seam's environment dictionary.
- `prompt_decision` takes `managed`.
- `pinned_project_root` was added (a B1 refinement).
- Nine route modules, not eight, recorded in the design's amendment.

No undeclared deviation was found. The invariants hold except where F1 bends two of them:

- **I13 / ADR-0017 (one environment read).** A standard-library module now reads an environment variable that changes a gate's verdict.
- **I7 (`CANDIDATE` means all ten gates passed).** Gate 7's pass can be produced through `PYTHONTZPATH`.

### Code integrity

**Engineering quality: good. `sysml_codegen.study` is a package sysml-codegen can own.**

- **`roots.py`** (210 lines, fully typed): one job, its rules stated in the module docstring and enforced in code.
  - Refusals carry both paths and the remedy. git's own message passes through on unexpected failures.
  - Process-wide state is two globals and one cache, all reset by `use_project_root(None)`.
  - Minor: a missing `git` binary would raise `FileNotFoundError`, not `RootError`.
- **`declarations.py`** (201 lines, fully typed): strict validation, no default `checked`, targets confined to the project root, messages free of absolute paths. No slop.
- **`cli/install.py`** (173 lines): a thin layer over agentic-mbse's `Installer`.
  - It is lazily imported, with the API pin checked before anything is written.
  - Project documents follow the create-once rule and do not write through a symlink.
  - The one leak is `Installer.files` (F9).
- **`cli/study.py`** (27 lines): a pure dispatcher.
- **Ported modules** keep fusion-tea's style by design.
  - `integrate.py` is 1,663 lines (a named DD19 smell).
  - `read_coverage.py` is untyped.

**The mypy overrides, named** (`pyproject.toml:53-105`). The audit probe ran mypy with `--check-untyped-defs --disallow-untyped-defs` on `study/`: 53 errors in 6 files (`6.txt`). Checking the bodies of the untyped functions surfaced no error beyond the codes below, so the untyped-def override hides no defect of its own.

| Override | Module | What it hides (HEAD lines) | Verdict |
|---|---|---|---|
| `disallow_untyped_defs = false` | all eight ported | 29 `no-untyped-def`: read_coverage 12 (`:29`–`:256`), verify 12 (`:87`–`:493`), preflight 3 (`:310, :317, :366`), integrate 2 (`:229, :616`) | Looseness only. The probe checked their bodies. |
| `disable_error_code = ["attr-defined"]` | identity | `:262` `.get` on `object` | Looseness. Unreachable, because the contract is validated first. |
| `disable_error_code = ["arg-type", "no-any-return"]` | indicators | arg-type `:617` (a `None` key, guarded at `:618`) and `:903`. no-any-return `:134` (Phase 1 record; not re-probed) | Looseness. |
| `disable_error_code = ["index", "no-any-return"]` | integrate | index `:1169`, `:1210-1221`, `:1298`, `:1388-1389`. no-any-return per Phase 1 record | **`:1210-1221` and `:1298` hide the two real, inherited misreports in F5.** The rest is looseness over validated documents. |
| `disable_error_code = ["no-any-return"]` | manifest | `:402` (Phase 1 record) | Looseness. The manifest is schema-validated. |
| `disable_error_code = ["arg-type", "assignment", "attr-defined"]` | preflight | arg-type ×7 at `:383-417` (guarded by `unavailable()`); assignment `:313`; attr-defined `:126, :136` | `:126`/`:136` is real but cosmetic: a non-object `model_contract.json` gives an `AttributeError` traceback, still exit 1 with no document. The rest is looseness. |
| `disable_error_code = ["index"]` | verify | `:507` | Looseness. The contract is asserted at `:500`. |
| `ignore_missing_imports` | simkit, simkit.*, yaml | `indicators.py:40` (yaml has no stubs); simkit is imported lazily | Looseness. |
| ruff per-file ignores | integrate (E501, N818), preflight (N818), read_coverage (E501), verify (E501) | Long lines; `SeamBlocker` / `GateFailure` names | Style only. |

The new modules (`roots`, `census`, `declarations`, `cli/study`, `cli/install`) carry no override and no ignore.

**Failure honesty.** F1 is the one fail-open. F5 and preflight `:126`/`:136` misattribute errors but fail closed. I found no broad `except` added by the port; the one at `integrate.py:1621` is inherited and reports exit 2 by contract. No backward-compatibility shim without a caller was found. The fusion-tea wrappers are drafts for adoption, not shipped code.

### The dry run's findings (F-DR1–F-DR3)

- **F-DR1 (no resume path): agree with the disposition.** Changing the record lifecycle is outside the closed list, and the text is inherited. But "filed as a follow-up" is not yet true anywhere durable (F2).
- **F-DR2 (fixed grid): disagree with the diagnosis, agree it is not a shipped-text defect today.** The fixture has `run_points`; the brief chose `run_grid`. The real issue is the open route contract at `runbook.md:261` (F4).
- **F-DR3 (report wording): agree.** The administrator role caught it, as the owner intended.
- **Missed by the dry run:** the template-preamble placeholder collision (F3).

### Hazards the owner faces at adoption (runbook draft `evidence/fusion-tea-runbook.md`)

Riskiest first.

1. **Step 4, the pin move, is the riskiest step, and it cannot be rehearsed.**
   - What it does: it hand-edits `uv.lock`, then runs `uv sync --frozen`, which can remove packages.
   - What guards it: a `grep -c` for the old SHA, a before/after `pip list` diff with "restore every removed package", `uv lock --check`, and the provenance test.
   - It needs the merged SHA, so only the owner's real run exercises it.
2. **Step 9's consequence is the owner's real decision.** About 142 commits of generator change mean gate 2 (regeneration) and gate 4 (snapshots) may refuse every fusion-tea package until each is regenerated.
   - The runbook states this, but only as a note. It gives no guidance for needing `integrate` in that window.
   - The owner should decide the pin move with 8a's B-against-A results and 8c's in hand.
3. **Step 7 has a `--force` trap.** `--force` would replace fusion-tea's ratified `STUDY_POLICY.md`. The runbook guards this explicitly ("Do not re-run with `--force`"; delete the one file or answer `o` at a terminal).
4. **Step 5's `sed -i` on route files could reach record copies.** It is well guarded: nine named files, no pathspec glob, and a status check that nothing else under `exploration/` changed, matched by whole path.
5. **Step 7 removes the local skill.** That is safe only after step 3's no-loss check, and the order guarantees it.
6. **Step 8b may be unrehearsable for the chosen record.** It needs the store under teax's uncommitted `_work/`. The runbook falls back on identity mismatch, but it names no fallback for a missing store.
7. **F1 ships to fusion-tea on adoption** if its fix does not land before merge. Gate 7 in fusion-tea would inherit the same fail-open.

---

## Certification

**Checked by re-running** (outputs in `.orchestrate-logs/audit-probes/`, run by the orchestrator at the auditor's request because this session could not execute Python):

- the full suite;
- ruff and mypy;
- the teax lane;
- the record checker and its self-test;
- the wheel's asset list;
- a strict mypy probe;
- the `PYTHONTZPATH` probe;
- the parity re-report from stored runs, byte-identical;
- `check_anchors.py` at `699b0a74d`.

**Checked by the auditor directly:**

- the schema `diff -r`;
- `roots.py`, `declarations.py`, `cli/install.py` and `cli/study.py` read in full;
- the agentic-mbse installer diff;
- the study package's import boundary;
- the template and placeholder collision;
- F-DR2's cause;
- the backlog and product-index gaps;
- the runbook draft.

**Delegated read-only reviews:**

- the product-lens;
- the edit map;
- the shipped-text bar;
- SC10's ledger.

Their load-bearing claims (F5's lines, F8's lines, `run_points`, the TZPATH mechanism) were re-verified by the auditor.

**Marked in `spec.md`:** SC1, SC2, SC3, SC4, SC5, SC6, SC7, SC8, SC10 and SC12. **Left open:** SC9 (pending the rehearsal) and SC11 (the agentic-mbse half was not re-run). **Plan:** all phase checkboxes were already ticked, and I verified them; nothing changed. **Epic:** it lives in agentic-mbse, outside this worktree, so it was not edited.

**To finish the certification:**

1. F1's fix lands. Re-check only F1: the new and rewritten B13 tests, the teax lane, the parity re-run, and the re-measured preload set.
2. SC9's rehearsal results.
3. agentic-mbse's full suite at its branch head, for SC11.

The F8 text pass can ride with F1's fix and needs no separate re-audit.

**Not checked:**

- SC9's rehearsal.
- agentic-mbse's full suite.
- The `no-any-return` sites, which were not re-probed; their list rests on Phase 1's recorded mypy run.
- The install transcript and the dry run were not re-executed. Their committed outputs, and the checker over the dry-run record, were.
- The fusion-tea text was read through the staged diff and the anchor run, not in fusion-tea's own suite.
- About 80 of 126 read-through rows were not sampled.
- The behaviour of symlinked `--package` paths that leave the work tree.
- Ported-module behaviour outside the 28 parity cases and the suites.
