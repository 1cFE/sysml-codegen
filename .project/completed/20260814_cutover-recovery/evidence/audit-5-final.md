# Audit 5 — final independent audit of the Item 7 recovery candidate

**Verdict:** **FINDINGS** — five, numbered below: one medium, four low. **The candidate tree
certifies.** Nothing found blocks owner acceptance, and nothing found is a defect in shipped
code. All five are accuracy defects in the recovery's own records, and the medium one is exactly
the class this recovery exists to prevent: a written "green at every boundary" that is no longer
true of the tree it describes.

**Audited:** 2026-08-11
**Candidate:** sysml-codegen `item7-rebuild` `c4e9b76` (records at `013d6a1`, `3a6532d`) +
agentic-mbse `item7-rebuild` `cc6c7a7`
**Auditor:** implemented none of this recovery. Every number below was measured from my own
shell, in my own run, against code I read.

---

## 1. What I did, in one paragraph

I re-ran the whole acceptance battery once myself and got the three-run table back, field for
field. I then attacked the six central claims rather than reading about them: I booby-trapped
every legacy module and ran public generation to see whether the single-authority claim is
behavioural or only an import pin; I forged v6 envelopes as a competent attacker would; I
re-derived the LCOE anchor from the SysML files with no import of the transcription module; I
executed **all four** retirement steps in a scratch worktree following only the runbook text; I
planted deletions designed to slip past the ledger checker; I diffed the test inventories and the
37 corpus outcomes against Item 6 and the Phase 2 baseline row by row; and I compared the
candidate against the original incident's forensic branch on each of the owner's four complaints.

The environment gate passed before every measurement: python 3.12.11 from
`/home/reid/1cfe/item7-rebuild-venv`, `sysml_codegen` and `agentic_mbse` resolving into the two
`*-item7-rebuild` worktrees, `simkit` into the pinned TEAx, license key present, **zero
`no live syside license` lines** in a 3,862-node run.

---

## 2. The battery, re-run independently

My run is `evidence/phase5-runs/audit5-run/`. It is a fourth run of the same harness from my own
shell, after I read the harness. Every field matches the record's three runs.

| Gate | Record (runs 1–3) | My run | |
|---|---|---|---|
| Full licensed codegen suite | 3862 / 47 / 53, 0 failed | **3862 / 47 / 53, 0 failed** | ✅ |
| `no live syside license` lines | 0 | **0** | ✅ |
| agentic-mbse suite (paired worktree) | 1825 / 1 / 5 | **1825 / 1 / 5** | ✅ |
| Execution lane, incl. real TEAx | 53 passed | **53 passed** | ✅ |
| Corpus ledger tests | 12 | **12** | ✅ |
| Corpus driver — exact arm | 15 graphs / 22 `ElaborationError` | **15 / 22** | ✅ |
| Corpus driver — legacy arm | 36 / 1 `CodeGenerationError` | **36 / 1** | ✅ |
| Exact code multiset | `SI_SELF_BINDING` ×75, `SI_EXPRESSION_SOURCE_UNSUPPORTED` ×7 | **×75, ×7** | ✅ |
| `ElaborationDiagnosticError` count | 0 | **0** | ✅ |
| `capture_v6_batch.py --verify` | 15 / 22 / 0, writes nothing | **15 / 22 / 0**, `git status` clean, non-timestamp diff 0 lines | ✅ |
| `--check` | 15 / 22 / 0 | **15 / 22 / 0** | ✅ |
| `ruff check src` / whole tree | 16 / 866 | **16 / 866** | ✅ |
| `mypy src` | 69 in 16 (87 checked) | **69 in 16 (87)** | ✅ |
| `check_ledger_4a.py paths` | 303 rows, 0 problems | **303 / 0** | ✅ |
| `surface` | 0 unrowed breakages | **0** | ✅ |
| `groups` | all six READY | **all six READY** | ✅ |
| `check_proof_integrity.py` | 0 over 0 blocked | **0 over 0** | ✅ |
| Doc distinctness | 31 docs, 0 identical groups | **31 / 0** | ✅ |
| `git diff --check`, both repos | clean | **clean** | ✅ |
| `replacements` (40-minute gate) | 219 green / 82 not-required / 0 fail | log tallies **219 / 82 / 0**, covering 301 of 303 rows | ✅ (log verified, not re-run) |

**Candidate identity, re-measured.** 362 files changed / 63,324 insertions / 2,074 deletions vs
`1672c57`; 249 added / 111 modified / **2 deleted**; 1,888 tracked files; 87 `src/**.py`; 108
commits. agentic-mbse: 5 files / 268 / 53, 2 commits. Every figure in §1 of the record is exact.

**The record commits change no code.** `git diff --name-only c4e9b76 3a6532d` returns only
`.project/` paths, so the candidate under review genuinely is the tree at `c4e9b76`.

**The 47 skips are not silenced tests.** I enumerated them with reasons: 43 are data-driven ("no
computed attributes in the golden", "no calc defs with output expressions"), 3 are
"no such scenario in this model", 1 is a missing `solar_battery_model` baseline. None is a
license skip, an `xfail`, or a disabled assertion. (Observation, not a finding: 43 skips that say
"this golden has nothing to check" is a pre-existing test-design weakness — the same count sits in
the Phase 2 baseline, so the recovery neither caused nor worsened it.)

---

## 3. Attacking the central claims

### 3.1 Single public authority — CONFIRMED, and more strongly than the shipped test does

The shipped pin is an AST import check plus a module-closure check. I replaced it with a
behavioural one. I imported all eleven legacy modules, replaced **206 callables** across them
(every module-level function and the `__init__`/`build`/`run`/`load`/`rebuild`/`serialize`/
`from_dict`/`to_dict` of every class) with a trap that raises, and then ran the shipped public
surface:

| Route | Fixture | Result | Legacy callables reached |
|---|---|---|---|
| `run_codegen(models_path=…)` | `d38_caret` | True, 23 `.py` files | **none** |
| `run_codegen(models_path=…)` | `fusion_tea` | True, 40 `.py` files | **none** |
| `main(["snapshot", …])` | `fusion_tea` | exit 0, 112,046-byte envelope | **none** |
| `run_codegen(from_snapshot=…)` | `fusion_tea` | True, 40 `.py` files | **none** |

Nothing legacy executes on either public route. I found no escape hatch.

The pinned residual is honestly stated. `LEGACY_AUTHORITY_MODULES` in
`tests/conformance/test_public_authority_switch.py:177` is a **named four-module** pin, three of
which the CLI import closure reaches — and the test's own docstring and `CLAUDE.md` both say the
pin is not a claim about the whole closure. I measured the whole closure myself against the
eleven-module list: **`sysml_codegen.cli` reaches 10 of 11, every one but
`orchestration/snapshot_context`**, and the construction closure from
`exact_pipeline_context` reaches **none**. That is exactly what `CLAUDE.md` says. No rounding
down.

### 3.2 The v6 envelope identity model — CONFIRMED, including the accepted residual

I re-ran a forgery probe against `tests/fixtures/fusion_tea/instance_graph_snapshot.json`.

Naive tampering (edit, don't re-seal) is caught every time by the outer digest. The interesting
case is the competent forger who recomputes the inner graph fingerprint, the source fingerprint
and the outer digest:

| Forgery, fully re-sealed | Offline | With `source_roots` |
|---|---|---|
| A modelled numeric value flipped (`5.0` → `999999`) | **ACCEPTED** | **ACCEPTED** |
| Every source referent relabelled | **ACCEPTED** | refused — `SnapshotStaleSourceError` |
| A source `sha256` restated | ACCEPTED offline | refused — `SnapshotStaleSourceError` |
| A fabricated source row appended | ACCEPTED offline | refused — `SnapshotStaleSourceError` |
| `format` downgraded to v5 | refused — `SnapshotCompatibilityError` | — |
| `syside_version` falsified | refused — `SnapshotCompatibilityError` | — |
| Standard-library digest restated | refused — `SnapshotCompatibilityError` | — |

Every one of those outcomes is what `snapshot/envelope.py:1-56` says will happen, in the words it
uses. The digest proves coherence, not authenticity; `sources` is a self-declared manifest that
`source_roots` closes; and no offline check can prove the sealed graph is the elaboration of the
sealed sources — which is why the value flip survives even in provenance mode. The module states
its own limit accurately and does not overclaim.

### 3.3 The hand-arithmetic anchors — RE-DERIVED, bit-for-bit

I read the design constants off `designs/hif_ife/hif_plant.sysml`,
`designs/hif_ife/hif_driver.sysml`, and the equations off `library/analyses/hif_economics.sysml`
and `library/analyses/ife_lcoe.sysml`, typed them into a fresh script, and imported nothing from
`tests/execution/fusion_tea_arithmetic.py`.

```
LCOE = 270.1211779380445      anchor = 270.1211779380445      delta = 0.0
```

The transcription module's docstring inventory of which file carries which number is accurate
line by line. This closes audit-3e's largest stated not-verified item.

### 3.4 The runbook's mechanical claim — I am the fresh-agent test, and it holds

I created a scratch worktree beside the repos (not `/tmp` — the recorded trap is real) at
`3a6532d`, and executed **all four steps** following only the runbook text, applying the
prepared patches, using `retire_step.py apply` / `close`, and running the battery at each
boundary with the 113-node trim deselected.

| Boundary | Runbook says | I measured |
|---|---|---|
| Step 1 | 2352 / 43 / 145, **0 failed** | 2356 / 43 / 148, **1 failed** |
| Step 2 | 1582 / 34 / 148, **0 failed** | 1589 / 34 / 148, **1 failed** |
| Step 3 | 1582 / 34 / 148, **0 failed** | 1589 / 34 / 148, **1 failed** |
| Step 4 | 1582 / 34 / 148, **0 failed** | **1586 / 34 / 148, 0 failed, 0 errors** |

Everything else matched or was better than recorded. `check_ledger_4a.py paths` read **303 rows /
0 problems** at every boundary; `surface` 0; `--verify` 15/22/0; the whole-tree ruff count landed
on the runbook's **derived** number (769 after step 1, **644** after step 4 — the runbook predicts
644 to the unit); the execution lane read 23 passed + the same 12 environment errors the runbook
names. After step 4 every legacy module is gone from disk: `pipeline_builder`, `snapshot_context`,
`graph_builder`, `producer_resolution`, `loader`, `serializer`, `graph_rebuild`.

**The mechanism is genuinely mechanical.** Every patch applied first time, both documented
apply-order traps were real and the runbook's ordering avoids them, and I needed no judgement call
the text did not supply. That is a strong result and I want it read as one.

The single failure is finding **F1** below. It is not a defect in the retirement; it is a stale
measurement in the runbook's intermediate rows.

### 3.5 The ledger's closure — the checker misses two shapes it does not list

I invented a deletion the three axes should miss and planted it. A single new test module that
(a) requests `offline_input_sources` — a conftest fixture step 1 deletes — as a parameter, and
(b) reaches a deleted module through `importlib.import_module("sysml_codegen.snapshot.loader")`.

Both `check_ledger_4a.py paths` and `surface` reported **0 problems / 0 unrowed breakages**. Both
shapes are invisible to all three axes: neither is a module-level import, neither is a literal
data basename, and neither is transitive.

This is not a surprise to the recovery — the runbook's `PULLED_FORWARD` note names exactly this
class ("a function-local import, a fixture use, or a subprocess/`importlib` load, which is the
class the checker's module-level AST scan cannot see") and carries fourteen measured rows for it.
But the checker's own docstring heads its limits section "**Four ceilings**" and enumerates four,
none of which is this one. See **F5**.

I also probed one axis nobody had: the twelve non-Python shipped files under `src/`. One Jinja
template names `parameter_groups`, and I checked it — it is a template variable, not the module.
That axis is clean.

### 3.6 The reconciliation — independently confirmed

Test inventory, `git ls-tree` at both ends: Item 6 base **218 modules → 257**, with exactly
**one removed** (`tests/unit/test_signature_extractor.py`) and 40 added. Matches §4 exactly.

Corpus, compared per fixture against `baseline.json`'s own 37 outcome rows: **exactly two rows
moved**, `agg_literal_probe` and `fusion_tea`, and no other row moved at all — the substantive
claim of §4 is true. Two numbers describing that comparison are wrong; see **F2** and **F3**.

### 3.7 The decision surface — measured, and the costs are stated fairly

I checked all seven gated items and five of eleven residuals — twelve of eighteen entries.

| Entry | What I verified |
|---|---|
| Gated 1 (dual qualifier drop) | `level4_constraints.py:55-56` and `level6_architecture.py:620-621` really do call `extract_constraint_facts` / `evaluate_profile` — the legacy members of L-036 and L-037, in the other repository. The "outside this ledger" claim is exact |
| Gated 2 (L-033/L-034) | `compile_calc_def_exact` constructs a legacy `CompilationResult` inside its own body at `extraction/expression_compiler.py:378`. Confirmed by reading |
| Gated 3–5 (node counts) | The trim file decomposes as 59 `test_extractor` + 44 `test_hierarchy_resolver` + 3 `test_ast_dispatch_invariant` + 5 `test_expression_compiler` + 2 `test_capture_fixtures_filter` = **113**, matching the table's 59 / 47 / 5 / 2 exactly |
| Gated 6 (`capture_filter`) | Its only non-test caller is `scripts/capture_pipeline_baselines.py`, which step 1 deletes. Claim confirmed |
| Gated 7 (dead v5 surface) | All six names' readers are v5-family modules and v5 test modules that step 2 retires. Claim confirmed |
| R1 / R9 (provenance, fingerprint) | Generated `fusion_tea` live and from snapshot and diffed the packages: file sets identical; the **only** content differences are the `SysML Source:` comment in 14 files, the seal manifest's hashes for exactly those 14, and `executable_fingerprint`. The semantic fingerprint is equal. Exactly as described |
| R2 (`source_file`) | `generation/stencils.py:243` renders the portable referent directly, as claimed |
| R5 (zero-constraint aggregator) | `elaboration/project.py:887` — `if not constraint_outputs: return`. Confirmed |
| R6 (V11 structural) | `fallback_entry_points=set()` at `project.py:229` and `:264` — both construction sites, as claimed |
| R8 (same-name rollup) | The refusal behaves as described and `test_costed_component_exact_route.py` is green (18 nodes). The code pointer is off; see **F4** |
| R11 (key rename) | `3e-package-comparison.md` records legacy 31 / exact 27 / shared 13 and enumerates each delta with its consumer set |

I found no entry where the measurement was fabricated or the cost understated. Several are stated
*against* the recovery's interest — R11's "an owner should read the table, not a summary of it",
the `catf_mfe_d5` capture time that "would sit just over the 5.0 s line", the run-0 harness defect
kept in full rather than discarded. That is the posture this audit was told to look for.

### 3.8 The original incident's four complaints — all four affirmatively remedied

I compared the candidate against the forensic branch (`item7-forensic-20260810`) in the original
repos, both measured from the same Item 6 base `1672c57`.

| Complaint | The incident | The candidate |
|---|---|---|
| Deleted spikes | **222 deletions**, including 7 `scripts/spikes/`, 3 `scripts/probes/`, 6 `analysis/` modules | **2 deletions**, both ledger-rowed (L-006/L-241). 10 spikes and 12 probes present |
| Docs replaced by stubs | **22 of 34 docs** rewritten to identical 776-byte stubs (`verification-matrix.md` 74,487 → 776) | **0 docs shrunk, 0 deleted, 0 added.** And a `check_doc_distinctness.py` gate now exists that would catch exactly that shape — 31 documents, 0 identical-content groups |
| Broken extraction | — | Full licensed suite 3,862 passed / 0 failed with **zero** license-skip lines; live extraction, capture and generation all run under my own hands |
| No progressive commits | **1 commit** | **108 commits**, each a named slice or gate |

Every OID referenced anywhere in the 110-commit series resolves to a real commit: 45 references
checked, the 17 that fail in this repository are all agentic-mbse OIDs that resolve in the paired
repository, plus LCOE digit strings caught by my regex. No fabricated OID, and no commit whose
subject claims more than its diff among those I read.

---

## 4. Findings

### F1 — medium — the runbook's "0 failed at every boundary" is stale at steps 1, 2 and 3

**What.** `tests/unit/test_runbook_patches.py::test_the_prepared_patches_replay_cleanly_in_step_order`
fails from step 1 onward. Once step 1 is applied and committed, HEAD carries the edit the step-1
patch describes, so the patch cannot replay — which is precisely what that test is designed to
detect. The record's §7.2 ("All four end with 0 failed and 0 errors") and the runbook's four
`PROVEN` rows are therefore false at three of the four boundaries on the candidate tree.

**Evidence.** `git ls-tree 5b682c1 -- tests/unit/test_runbook_patches.py` returns nothing;
`git ls-tree c4e9b76` returns the file. The step-1 post-state was measured in a worktree at
`5b682c1`, **before the file existed**, and never re-measured after `31f973d` and `858a6a6` added
the two modules the candidate itself counts as its `+8`. My replay measures 1 failed at steps 1,
2 and 3, and **0 failed at step 4** — because row L-304 deletes the module at step 4.

**Why it is not worse than it looks.** The end state is green, the mechanism is sound, and the
retirement has not run. L-304 exists, its reason already describes this exact self-referential
problem ("after the steps run it asserts that spent patches still apply"), and the runbook already
owns a mechanism for rows that break earlier than their column places them — `PULLED_FORWARD`,
which carries fourteen such rows today.

**Why it still matters.** This is the recovery's own signature failure mode in miniature: a
measurement taken at one commit, written as a property, and left standing after the tree moved
under it. The intermediate node counts drift the same way (recorded 2352 / 1582; measured 2356 /
1589 — the `+8` new nodes less the failing one).

**Resolution.** Pull L-304 forward to step 1 in `PULLED_FORWARD` with the measured reason, and
restate the three intermediate post-state rows against the candidate tree. One entry and three
table cells. Do not re-simulate — I have measured all four boundaries and the numbers are above.

### F2 — low — the record's Phase 2 corpus figure drops an error

`evidence/candidate.md:192` reads "The Phase 2 baseline recorded the exact arm at 13 graphs / 23
errors." 13 + 23 = 36, not 37. `baseline.json` records 13 graphs and **24** errors — 23
`ElaborationError` plus 1 `CodeGenerationError` on `agg_literal_probe`. The rest of §4 is
arithmetically consistent with 24 (both moved rows are error→graph, giving 15 / 22 with the
`CodeGenerationError` class emptied), so this is a transcription slip, not a wrong conclusion.
Fix: "13 graphs / 24 errors (23 `ElaborationError` + 1 `CodeGenerationError`)".

### F3 — low — the record's `fusion_tea` baseline cell says 3×, the baseline says 15×

`evidence/candidate.md:198` records `fusion_tea`'s Phase 2 exact outcome as "`ElaborationError`,
3× `SI_SELF_BINDING`". `baseline.json` records **15×**, and the same table cell's own authority
text says "the customer model's **fifteen** self-named bindings". Fix the cell to 15×.

### F4 — low — R8's code pointer is 36 lines off

`evidence/candidate.md:386` cites `elaboration/elaborate.py:1901` for "projection names an
expression parameter after the reference's last member and drops the qualifier". The site is
`elaborate.py:1937-1938` (`input_name = fact.resolved_member_names[-1] …`). Line 1901 is inside
the aggregation-ordinal loop and carries no naming. R8 is the one residual that reaches outside
Item 7 (it is the Item 10 blocker), so its pointer is the one most likely to be followed.

### F5 — low — the ledger checker's "Four ceilings" list is incomplete

`scripts/check_ledger_4a.py:26` heads its limits section "**Four ceilings**, measured by the
Phase 4 composite audit (F7)" and enumerates four. I planted a file that requests a
step-1-deleted conftest fixture and dynamically imports a step-1-deleted module; `paths` and
`surface` both reported 0 problems. Neither shape is any of the four (transitive import,
label-not-measurement, vacuity, computed filenames). The class *is* named — in the runbook's
`PULLED_FORWARD` prose, one document away. A closed list of four in the checker's own "what this
checker cannot see" invites reading it as complete. Fix: add a fifth ceiling naming dynamic
imports and fixture requests, and point at `PULLED_FORWARD`.

---

## 5. Accepted residuals, restated

Acceptance of the candidate carries these. Each is recorded, evidenced, and measured; none is a
surprise I found.

1. **R1 / R9 — provenance and fingerprint.** Live and snapshot packages differ by construction, in
   the `SysML Source:` comment and `executable_fingerprint` only. Verified by direct diff. The
   semantic fingerprint is equal. Closing this means giving up snapshot portability.
2. **R2 — module `source_file` divergence.** Cosmetic, reaches bytes only through that comment.
3. **R3 — `d38_caret` shipped key spelling changed** (a fixed defect, recorded as a corpus row).
4. **R4 — `unresolvable_attr_probe` is now publicly refused**, typed and before the writer runs.
5. **R5 — the zero-constraint report aggregator disappears** with the retirement. A product
   question, correctly labelled as one.
6. **R6 — V11 coverage is a rot pin, not a live gate.**
7. **R7 — the units gap**, surfaced and closed.
8. **R8 — the same-name rollup refusal stands**, and is a modelling requirement the route imposes.
   This is the Item 10 cross-part blocker; it reaches outside Item 7.
9. **R10 — the constraint-threshold disambiguator drop.** No corpus model has the colliding shape.
10. **R11 — the customer-visible entry-point key rename.** 31 legacy keys → 27 exact, 13 shared.
    The largest customer-visible change here. Read `3e-package-comparison.md`, not a summary.
11. **The v6 envelope digest is unkeyed.** It proves coherence, not authenticity. A competent
    forger can flip a modelled value and re-seal, and it loads — offline *and* with
    `source_roots`. Pass `source_roots` when provenance matters; it closes relabelling, not
    value tampering.
12. **The corpus exercises `ElaborationDiagnosticError` zero times.** The separate-classification
    rule still binds; this corpus does not test it.
13. **`check_proof_integrity.py` reading 0/0 means nothing left to check**, not checked-and-clean.
14. **The seven owner-gated items and the 113-node trim.** Every retirement "green" is green with
    those held out — including mine.

---

## 6. What I did not verify

A certification with unstated limits is a blank check. These are mine.

- **The 40-minute `replacements` gate was not re-run.** I verified its committed log tallies to
  219 green / 82 not-required / 0 fail across 301 of 303 rows, and that the two silent rows are
  L-036 and L-037. I did not re-execute the 301 pytest invocations.
- **The scale measurements (§5) were not re-taken.** I confirmed one figure incidentally — the
  `fusion_tea` v6 envelope is 112,046 bytes, matching exactly. Timings and RSS I did not measure.
- **Six of the eight dual dry-run probes** remain unverified by execution, as they were after
  audit-4. I confirmed the L-036/L-037 caller claim by reading both agentic-mbse call sites.
- **267-odd ledger rows I did not read individually.** I read the four dual rows, L-304, and the
  rows behind each gated item. For the rest I relied on the checkers, whose ceilings I tested and
  extended (F5).
- **`docs/` prose was not read claim by claim.** I verified structurally: 0 stubs, 0 deletions, 31
  distinct numbered documents, and I did not re-derive individual prose assertions. The three Gate
  4D items recorded as belonging to whoever touches those files next remain open, as recorded.
- **Chunk 19's post-retirement node accounting** (432 nodes / 166 / 254 / 12) — not recounted.
- **TEAx internals** were treated as a trusted pinned dependency.
- **Concurrency and filesystem-race behaviour** of `admit_sources` — untested, as in audit-3a.
- **The v6 batch's 15 snapshots were not compared to a hand-elaboration.** I confirmed `--verify`
  re-derives all 15 through the public capture path writing nothing, which is a strong property,
  but the graphs' semantic correctness rests on the corpus ledger, not on my reading.
- **The 47 skips' historical sets were not diffed node by node** against Phase 2. I enumerated the
  current 47 with reasons and confirmed the count never moved.
- **agentic-mbse's own code was not audited**, only run (1825 passed) and read at the two call
  sites gated item 1 names.

---

## 7. For the owner — one page, plain

**The candidate is sound, and you can accept it.** I re-ran the whole acceptance battery myself
and got back exactly what the record says, on every one of twenty gates. I then went after the
six claims the recovery rests on, and each one held up under an attack designed to break it.

The biggest one first. The record says the new exact route is the only thing your `generate`
command actually runs, and that the old string-resolution code, while still sitting in the tree,
never executes. I did not take the shipped test's word for that — it checks imports. Instead I
sabotaged 206 functions and methods across all eleven old modules so that any one of them would
blow up if it were called, then generated packages both ways, live and from a snapshot. Everything
worked, and nothing old was touched. The claim is true in behaviour, not just on paper.

The LCOE number your execution tests assert — 270.1211779380445 — I re-derived from your SysML
files by hand, typing the constants and equations out myself without importing the project's
transcription of them. It came out identical to the last digit. That number is real.

The snapshot format is honest about what it can and cannot promise. I forged snapshots the way a
competent attacker would, recomputing every internal checksum. Renaming the source files is caught
if you pass `source_roots`, and not otherwise. Changing a number inside the sealed graph is not
caught either way. That is exactly what the code's own documentation says, in the same words. It
does not oversell itself.

I also acted as the fresh agent for the retirement runbook — the document that says how to delete
the old code once you approve. I followed only its text, in a throwaway copy of the repo, and ran
all four steps. Every patch applied first time. Both of the traps the runbook warns about are
real, and its instructions avoid them. The final state is completely green: 1,586 tests passing,
zero failures, and every old module gone from disk. The retirement is genuinely mechanical work,
not a plan that will fall apart on contact.

**What I found.** Five things, none of which changes any of the above.

The one worth your attention: the runbook says all four retirement steps end with zero failures.
Three of them don't, any more. There is a test whose whole job is to check that the pending
patches still match the tree — and applying a patch necessarily breaks it. That test was written
*after* the runbook measured steps 1 through 3, and those measurements were never redone. The
final step is unaffected, because the ledger already schedules that test for deletion there. The
fix is to move it three steps earlier, which is a one-line change to a mechanism the runbook
already has, plus correcting three sets of numbers I have measured for you. I want to name this
plainly because it is the same shape as the failure that caused this whole recovery: a number that
was true when it was written, left standing after the ground moved. It is small here, and it was
caught. But it is the shape.

The other four are small record errors: two mistyped numbers in the reconciliation table, a code
line reference that is 36 lines off, and a list in the ledger checker that says "four ceilings"
when there are at least five. All are one-line corrections. None affects a conclusion.

**What acceptance still costs you.** Nothing I found is new, but three items deserve your eyes
rather than a summary. The entry-point key rename (R11) is the largest customer-visible change in
this work — 31 published keys become 27 — and the comparison table matching each old key to its
new one is the thing to read. The same-name rollup refusal (R8) is a real modelling requirement
your models will now have to satisfy, and it reaches past Item 7 into Item 10. And the seven gated
items are genuinely unresolved: every "green" in the retirement, including my own runs, is green
with 113 test nodes deliberately held out. Those seven need your ruling before the retirement is
mechanical.

**My verdict.** Findings, not a block, and not a clean certification either. The tree is good, the
evidence is real, and the record is honest — noticeably more honest than it had to be, in places
where a less careful record would have rounded down. Fix F1 before anyone executes the retirement,
so the next person following that runbook is not told to expect a green suite that will not be
green.

---

**Auditor's note on discipline.** I wrote no file in either repository except this one, made no
commit, and removed the scratch worktree when I was done. Both repositories are clean at the
recorded OIDs; the only untracked paths in sysml-codegen are the Phase 5 brief and my own run
directory `evidence/phase5-runs/audit5-run/`.
