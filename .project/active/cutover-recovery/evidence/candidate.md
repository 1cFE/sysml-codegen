# The post-REVISE candidate — the retired tree, its gates, its audit, and what is left for the owner

**Status:** ASSEMBLED at the content OIDs below. **Owner final disposition PENDING.**
**Assembled:** 2026-08-12, REVISE step 7c.
**Authority:** `.project/active/cutover-recovery/plan.md` — the owner gate, and
`owner-disposition-20260811.md` step 7.
**Content OIDs:** sysml-codegen `6c35aa0`, agentic-mbse `3fbda2f`, TEAx pinned `fa0e06a9`.
The record commit lands on top of `6c35aa0`, so it names the content OIDs rather than
containing its own.
**Machine-readable twin:** `evidence/candidate.json`. **Builder:**
`evidence/phase5-runs/build_candidate_revise.py`. Every table below is emitted by that builder
into `evidence/phase5-runs/revise-candidate-tables.md` and quoted here verbatim; §9 says how
each number was derived.

**This record replaces the one the owner reviewed on 2026-08-11.** That record described the
**pre-retirement** tree at `c4e9b76` and said the independent audit had not run. Both statements
were true then and are false now. The superseded record is at commit `013d6a1`
(`git show 013d6a1:.project/active/cutover-recovery/evidence/candidate.md`). §8 lists the five
discrepancies the owner named and what each now reads.

What the candidate is, stated plainly:

- The exact route is the **sole public generation authority**, and the legacy string-resolution
  stack is **gone from the tree** — not unreachable, gone. The retirement executed with **no
  provisional trim**, as the owner required.
- The v6 recapture batch is **ACCEPTED** (owner ruling 2026-08-11, recorded in
  `tests/fixtures/v6_recapture_batch/batch.json`).
- The retired tree passed **three consecutive complete gate runs with every compared field
  identical**, and was **independently audited** by a fresh session that did not implement any
  of the work.
- The audit's verdict is **FINDINGS** — ten, none blocking — with certification withheld on one
  item it could not reach. All eight probes it requested were executed and confirm the pending
  lines, so its own clause resolves to *Certify with the residual list* once F1–F3 are
  dispositioned. They are dispositioned.
- **Nothing here accepts anything.** R8 is untouched and parked, the ruff findings are unruled,
  audit-F4 is parked, and six further owner questions are open. §7 is the list.

---

## 1. The candidate

| | sysml-codegen | agentic-mbse |
|---|---|---|
| Path | `/home/reid/1cfe/sysml-codegen-item7-rebuild` | `/home/reid/1cfe/agentic-mbse-item7-rebuild` |
| Branch | `item7-rebuild` | `item7-rebuild` |
| Content OID | `6c35aa01c28e2afa3331db002d871bc9634121c9` | `3fbda2fbfa82f43d59b0262cedd7a7ae241f37d0` |
| Item 6 base | `1672c5766f67e7716f3c9f8f636c21e2ea444601` | `5088b417c9e5453271291d46cd5fb23fc0579b1e` |
| Diff vs base | 818 files changed, 181532 insertions(+), 104700 deletions(-) | 21 files changed, 738 insertions(+), 344 deletions(-) |
| Name-status vs base | 491 added / 114 modified / **195 deleted** | 2 added / 19 modified / **0 deleted** |
| Commits since base | 160 (`1672c5766f67e7716f3c9f8f636c21e2ea444601..6c35aa0`) | 4 (`5088b417c9e5453271291d46cd5fb23fc0579b1e..3fbda2f`) |
| Shipped paths (`src`, `tests`, `scripts`, `docs`, `pyproject.toml`) | clean | clean |

Pinned TEAx: `fa0e06a99b070346e68a3b3c29cfec546f3ac728`.

The last row is scoped to shipped paths on purpose. Writing this record dirties `.project/`,
so a whole-tree status would print a different value every time the builder ran and the record
would not survive its own re-run. What it asserts is the thing that matters: **this stage
changed no product, test, script, doc or packaging file**, in either repository.

**The commit count has one definition and one number.** 160 is
`git rev-list --count 1672c576…..6c35aa0` — every commit reachable from the codegen content OID
and not from the Item 6 base this recovery branched from. The record commit lands on top of the
content OID, so it is not counted. The old record's 108 was the same measurement taken at the
pre-retirement OID `c4e9b76`. The 108-vs-112 ambiguity was the same measurement over two
different endpoints, re-derived here: `…..c4e9b76` (the product tree) counts 108 and
`…..800ec84` (the branch tip, record commits included) counts 112. Neither is wrong; naming the
endpoint is what was missing. There is one number here and its range is printed beside it.

**The 195 deletions are the point of this candidate.** The pre-retirement tree had deleted two
paths in the whole recovery. The retirement deleted the rest: the legacy builders, the v5 read
path and its family, the dual-run code, the test shims and the committed v5 snapshot fixtures.
§4 names the commits.

The four agentic-mbse commits are `8b63393` (an exact constraint gate beside the neutral one),
`cc6c7a7` (a mis-encoded manifest warns instead of aborting), `ffb6628` (every consumer migrated
onto the identified constraint route) and `3fbda2f` (the neutral route deleted).

**Forensic, do-not-merge** (preserved in Phase 1, referenced by nothing in the candidate):
sysml-codegen `07531e64ed912d6046afce47ef0d958605e6ca08`, agentic-mbse
`ed5b8b02a3064e767799cc6ee58e0119e9bfecba`, both on `item7-forensic-20260810`.

### Path inventory

| | sysml-codegen | agentic-mbse |
|---|---:|---:|
| Tracked files | 1,938 | 1,836 |
| Production modules (`src/**.py`) | 71 | — |
| Test modules | 127 | 67 |
| Fixture directories | 96 | — |
| Numbered reference documents | 31 | — |
| Scripts (`scripts/**.py`) | 43 | — |

Production modules went 87 → 71 and test modules 257 → 127 across the retirement. The test-module
drop is large because the v5 family, the dual-run tests and the wrong-oracle tests went together;
what the surviving suite still proves is the ledger's subject, and the replacement-proof gate
below is the mechanical check that it does.

---

## 2. Environment

Asserted **before** any measurement in each of the three runs, and each run aborts if the gate
fails. All three `env.json` files are byte-identical.

```
import-path gate  PASS   (all three runs)
python            3.12.11  /home/reid/1cfe/item7-rebuild-venv/bin/python
sysml_codegen     /home/reid/1cfe/sysml-codegen-item7-rebuild/src/sysml_codegen/__init__.py
agentic_mbse      /home/reid/1cfe/agentic-mbse-item7-rebuild/src/agentic_mbse/__init__.py
simkit            /home/reid/1cfe/teax/packages/teax-simkit/simkit/__init__.py
ruff 0.16.2   mypy 2.3.0   pytest 9.1.1   pydantic 2.13.4   jinja2 3.1.6   syside 0.8.4
license           key present (set -a; source /home/reid/1cfe/agentic-mbse/.env; set +a)
```

The gate pins each of the three imports to its own required worktree, so a cross-wired venv
cannot pass it. Neither protected original checkout was touched.

**The licence proof is direct, not inferential.** The codegen suite runs with `-rs`, so every
skip prints its reason, and `no live syside license` appears **zero** times — in all three runs
and in the step-7c re-measurement. The 34 skips are model-content skips.

---

## 3. Three consecutive complete runs on the retired tree

Measured at codegen `c0ceb24` / agentic `3fbda2f` / TEAx `fa0e06a9` (REVISE step 7a). Compared
field by field by `compare_revise_runs.py`, not by eye.

| Gate | run 1 | run 2 | run 3 | identical |
|---|---|---|---|---|
| Full licensed codegen suite | 1705 passed, 34 skipped, 65 deselected | same | same | yes |
| `no live syside license` skip lines | 0 | same | same | yes |
| agentic-mbse suite, from the paired worktree | 1826 passed, 1 skipped, 5 deselected | same | same | yes |
| Execution lane (`-m execution`), incl. real TEAx | 65 passed | same | same | yes |
| Corpus ledger gate (`-k corpus`) | 9 passed, 1795 deselected | same | same | yes |
| `capture_v6_batch.py --verify` | 15 captured, 22 refused, 0 deviations | same | same | yes |
| Non-timestamp fixture diff after `--verify` | 0 | same | same | yes |
| `capture_v6_batch.py --check` | 15 captured, 22 refused, 0 deviations | same | same | yes |
| `ruff check src` | Found 14 error | same | same | yes |
| `ruff check src tests scripts` | Found 641 error | same | same | yes |
| `mypy src` | Found 57 errors in 11 files | same | same | yes |
| agentic `ruff check src` | Found 1 error | same | same | yes |
| agentic `ruff check tests` | Found 120 error | same | same | yes |
| agentic `mypy src` | Found 108 errors in 26 files | same | same | yes |
| `check_ledger_4a.py paths` | 304 rows checked, 0 problems | same | same | yes |
| `check_ledger_4a.py surface` | 0 unrowed breakages | same | same | yes |
| `check_ledger_4a.py replacements` — green | 221 | same | same | yes |
| `check_ledger_4a.py replacements` — not required | 81 | same | same | yes |
| `check_ledger_4a.py replacements` — FAIL | 0 | same | same | yes |
| `check_proof_integrity.py` | proof integrity: 0 problems over 0 blocked files | same | same | yes |
| `check_doc_distinctness.py` | 31 numbered reference documents checked, 0 identical-content groups | same | same | yes |
| `git diff --check`, codegen | rc=0 clean | same | same | yes |
| `git diff --check`, agentic | rc=0 clean | same | same | yes |

**51 / 51 compared fields identical across all three runs**, re-derived from the committed logs
by the builder through `compare_revise_runs.fields`. The rows above are the headline subset; the
full field list is in `candidate.json` under `three_runs.fields`.

**Two counting notes, so a reader does not trip over them.**

- `revise-runs/comparison.md` reports **33/33**. That document is authored prose whose table is a
  curated view of this same comparison, and its headline counts its own rows. The comparator over
  the same logs emits 51 fields. **No field differs under either count**, and the builder now
  reads comparison.md's headline back so the two numbers stay reconciled.
- The **`replacements` not-required count is 81**, not 0. The comparator's pattern read
  `not required` where the checker writes `not-required`, so its own line reported 0 while
  comparison.md's 81 — read straight from the log — was right. Corrected in
  `compare_revise_runs.py` at this step, with the reason in a comment. 221 green + 81 not-required
  = 302 of the ledger's 304 rows; the two that emit no line are **L-036 and L-037**, the pair that
  cannot execute, computed from the log and the ledger rather than recalled.

**`check_proof_integrity.py` reading `0 problems over 0 blocked files` means nothing left to
check, not checked-and-clean.** The log says so; the previous summary dropped the caveat
(audit-7 F4), and this record carries it.

### Scale, from the same three runs

Wall-clock is measurement, not a semantic result, so it is reported as a range rather than
compared for identity. Node counts, module counts, entry-point counts and envelope bytes **are**
compared and are byte-stable.

| fixture | live elaborate s | generate live s | peak RSS MiB (cumulative) | envelope bytes |
|---|---|---|---|---|
| `catf_mfe_d5` | 4.960–5.272 | 5.132–5.426 | 308.9–326.4 | 621,270 |
| `fusion_tea` | 0.117–0.133 | 0.191–0.196 | 222.7–244.7 | 112,046 |
| `solar_battery_d5` | 0.320–0.348 | 0.755–0.827 | 264.8–285.0 | 1,104,445 |

The declared budget (spec R10, `[INFERRED]`) covers `fusion_tea` only: 10.0 s live elaboration,
30.0 s generation, 512 MiB peak RSS, 25 MiB envelope. `fusion_tea` holds every one with two
orders of magnitude to spare. The two D-5 variants carry **no pass/fail claim** — they are the
declared baseline for those fixtures, and `catf_mfe_d5`'s five-second live elaboration is the
number an owner would want before declaring a budget for it.

### The content OID, re-measured at step 7c

The three runs measured `c0ceb24`. The only product change since is the audited and dispositioned
audit-7 F3 CLI handler and its two pinned nodes, so this stage re-measured at the content OID
rather than carrying a number from a tree that no longer exists. Logs:
`evidence/phase5-runs/head-6c35aa0/`.

| Gate | value at the content OID |
|---|---|
| Full licensed codegen suite | 1707 passed, 34 skipped, 65 deselected |
| `no live syside license` skip lines | 0 |
| `check_ledger_4a.py paths` | 304 rows checked, 0 problems |
| `check_ledger_4a.py surface` | 0 unrowed breakages |
| `check_doc_distinctness.py` | 31 numbered reference documents checked, 0 identical-content groups |
| `git diff --check`, codegen | clean |
| `git diff --check`, agentic | clean |

**1707 / 34 / 65 at `6c35aa0` against 1705 / 34 / 65 in the three runs.** The delta is exactly
`tests/conformance/test_cli_snapshot_refusal.py`'s two nodes, added with the F3 fix. Skips and
deselections did not move.

---

## 4. The retirement, executed

Owner step 5 required the retirement to run against the real tree with **no provisional trim** —
the 113-node deselection list must not be used. It ran that way, in four commits.

| commit | subject | paths touched |
|---|---|---|
| `19072ad` | retire(step 1): G2' — the v5 read path | 99 |
| `82c7951` | retire(step 2): the v5 family | 167 |
| `882fc8d` | retire(step 3): G3' — resolution/producer_completeness.py | 1 |
| `3071fba` | retire(step 4): G4' — the last reach at the legacy route, and the dead v5 surface | 4 |

What is gone from the working tree, verified by the auditor by grep at HEAD rather than by
reading a note: `orchestration/pipeline_builder.py`, `orchestration/snapshot_context.py`,
`resolution/graph_builder.py`, `resolution/producer_resolution.py`,
`resolution/producer_completeness.py`, `core/output_registry.py`,
`snapshot/{loader,serializer,graph_rebuild}.py`, `elaboration/diff.py`,
`tests/helpers/legacy_route.py`, `tests/conformance/test_elaboration_dual_run.py`,
`scripts/capture_filter.py`, `scripts/run_elaboration_corpus.py`, and every committed
`extraction_snapshot.json`. `snapshot/__init__.py` re-exports nothing.
`orchestration/pipeline_context.py` survives as the `SysMLParsingError` /
`CodeGenerationError` re-export point and carries no `PipelineContext`.

**What holds the absence in place.** `tests/conformance/test_public_authority_switch.py` and
`tests/unit/test_elaboration_import_boundaries.py` pin the modules' non-existence and pin that
the CLI names none of them. The ledger checker is the mechanical half: an executed `delete` row
whose file is still present is a problem, and an executed `migrate`/`retain` row whose file is
gone is *also* a problem unless a recorded Gate 4C disposition authorises the absence. 304 rows,
0 problems, in three independent runs and again at the content OID.

The seven formerly owner-gated items were **implemented**, not held out — the coordinated
exact-ID type migration across both repositories, the ~111 affected behaviour tests repointed or
replaced before their evidence sources were deleted, unknown-fixture rejection carried into the
v6 capture driver, and the dead v5 exports removed. The per-step record is in the plan's "Revise
step 2/3/6" sections.

---

## 5. The independent audit

`evidence/audit-7-retired.md`, 2026-08-12, a fresh session that implemented none of the work and
audited the retired tree at `48bf1b0` (product content `c0ceb24`).

**Verdict: FINDINGS — ten, none blocking. Certification withheld on one item it could not
reach.** The withheld item is not a defect the auditor found; it is a gap in what the auditor
could read: the product-lens ledger's controlling BLOCK is `audit-F1`, which lives entirely in
`agentic-mbse`, and that session had no read access to the companion repository and no
interpreter. Its own words: a certification that treats an unread repository as green is the
failure mode that caused the original incident.

**The certification clause, and how it resolves.** The record says: run probes P1–P8; if they
come back as the stage notes describe, the honest verdict on the evidence gathered is **Certify
with the residual list, once F1–F3 are dispositioned**. All eight probes were executed by the
orchestrator from the canonical environment and appended to the audit as the probe addendum.
**All eight CONFIRM** — the self-binding exemption is gone from the companion with its tests and
docs realigned (P1–P3), both production call sites run the identified constraint route with the
four legacy members absent (P4), the manifest refusal is typed (P5), the six mutation-matrix
cells pass (P6, 20 passed), the three import paths resolve to the required worktrees (P7), and
the ledger reads 304/0 at the audited OID (P8).

**F1–F3 are dispositioned** (plan, "Revise step 7"): the HR family carries the same
off-shipped-route disclosure its sibling family had; the three re-cited rows whose heir proves
less than the requirement text moved PASS → PARTIAL with the gap named per cell; and
`cmd_snapshot` now carries the same named refusal handlers `run_codegen` keeps, pinned by two
nodes. So the standing verdict is **Certify with the residual list**.

**F4–F10 are low or informational and remain open as record-quality work**, not as gates: the
vacuous proof-integrity cell (carried in §3 of this record), a matrix file count off by one, the
spec's stale success-criteria checkboxes (ticked at this step for SC4/SC8/SC9/SC10, with
provenance recorded in the spec), a plan sentence that overstates step 2's containment, a
single-owner claim that is true for two lanes rather than the tree, unit tests that build a
catalog shape the projector no longer emits, and three ledger rows whose `retain` disposition
reads against an authorised deletion.

**What the auditor could not verify, in its own list:** the entire agentic-mbse half, anything
requiring execution, the six mutation cells observed rather than read, the 304 rows one by one,
the scale timings, ~120 of the re-cited matrix rows, TEAx internals, and the forensic branches.
The probe addendum closes the first two for the items that decided the verdict; the rest stand as
stated limits.

---

## 6. What the customer proof rests on

Not re-derived here; named so the owner knows what was checked and by whom.

- **The mutation matrix.** Two off-default mutations × three public routes (live,
  in-place-snapshot, relocated-snapshot) = six cells, in
  `tests/execution/test_fusion_tea_mutation_teax.py`. The auditor derived the consumer sets from
  the SysML *before* reading the test's expectations and got exactly the two consumers each that
  the test asserts. The mover set is computed over every projected output and every constraint
  response, so it is an every-and-only claim. LCOE is checked against an independent hand
  transcription **and** against the forensic constants, so a self-consistent wrong answer still
  fails. Probe P6 observed 20 passed.
- **The accepted batch.** 15 v6 snapshots and 22 typed refusal records, produced through the
  shipped public capture entry point. `--verify` re-captures all 15 and writes nothing: zero
  non-timestamp diff lines in all three runs.
- **The R10 collision test.** `tests/conformance/test_constraint_name_collision.py`, 4 nodes: two
  same-named constraint usages under one owner are refused, typed (`SI_ID_UNSTABLE`), before
  generation, with the output path never created.

---

## 7. What is still the owner's

Nothing in this section is new, and nothing here has been decided by an agent.

**The gate: the final disposition on this candidate.**

| # | Open question | Where it is recorded | State |
|---|---|---|---|
| 1 | **R8** — the qualifier-dropping same-name rollup refusal: fix-first, or shipping-gate with Item 10 scheduled | `owner-disposition-20260811.md` Q1; plan S4 | Untouched. The audit diffed the range and confirmed no `SI_RENDERING_COLLISION` logic moved. **Owner step 4 requires resolution or an explicit shipping gate before Item 7 closes.** |
| 2 | **The ruff findings** — clear them (orchestrator recommendation) or amend the spec | Q2 | Unanswered. Now **14**, not 16; the two that went sat in deleted files. All are `UP042`-class style findings with unsafe-only fixes. This is why the spec's coordinated-repository-gates criterion is deliberately left unticked. |
| 3 | **Item 10 scheduling** — raised by R8 either way | Q3 | Not blocking |
| 4 | **How the final audit runs** | Q4 | Answered in practice: it ran as a fresh independent session |
| 5 | **audit-F4** — route-dependent generated bytes: make live provenance portable, or amend invariants 34–35 with proper authority | Q5 | Properly parked, verified untouched. Design amendment A1 explicitly declines to converge D3 *because* convergence would answer audit-F4 by side effect |
| 6 | **Six items surfaced during the REVISE execution** — REQ-CL-03's total-inventory guarantee; whether the two non-shipping extraction modules stay; the nine UNTESTED matrix rows; the three PARTIAL rows; missing REQ families for the elaborator's own mechanisms; ratification of design amendments D3/R2 | Q6 | All genuinely owner-grade; none blocks the mechanical path |

**Accepted residuals, restated so they are in one place** (full list and evidence in
`evidence/audit-7-retired.md`): `mypy src` at 57 errors in 11 files, unchanged across the whole
REVISE path; 131 RETIRED matrix rows and the honest 275 → 136 drop, which after the F2
disposition reads 133 PASS + 3 PARTIAL; two extraction modules
kept by their tests with a measured disposition in their docstrings; one deliberately-kept
compatibility pin with no runtime consumer; `scripts/archive/` unreachable by collection; a
partial output tree surviving a mid-write failure, measured and deliberately unchanged; a stale
`PROVENANCE.md` in the `catf_mfe_d5` fixture; and ~110 behaviour nodes licence-gated by fixture,
detectable by skip reason.

**One provenance floor the owner should know.** `owner-disposition-20260811.md` is graded
`[INHERITED: handoff-20260811.md]`: the owner's review was given in a session transcript that the
recording session could not read, so every `[OWNER]` ruling in this REVISE path rests on an
agent-written handoff rather than on the owner's own words. The disposition record discloses this
in its second paragraph; the auditor raised it too.

---

## 8. The five record-integrity discrepancies, before and after

The owner named five. Each is listed with what the record said and what it says now.

| # | Before | After |
|---|---|---|
| 1 | "The independent audit … has not run against this record"; the candidate described as the tree at `c4e9b76` with the legacy stack "present in the tree, importable, unreachable — nothing has been retired" | This record describes the **retired** tree at `6c35aa0`: §4 the executed retirement, §3 the three-run gate table, §5 the audit verdict, its certification clause, the eight-probe addendum, and the F1–F3 dispositions. `c4e9b76` appears only where this record points back at the superseded one |
| 2 | "Commits since base 108", with a 108-vs-112 ambiguity and no stated range | **160**, one number, printed with its range `1672c576…..6c35aa0` and the command that produced it (`git rev-list --count`), in §1 and in `candidate.json` under `commit_counts` |
| 3 | The plan's owner gate named `800ec84` as *the* candidate | The plan's owner gate now records **both**: gate 1, the settled 2026-08-11 REVISE disposition at `800ec84`; gate 2, the post-REVISE candidate at `6c35aa0` / `3fbda2f`, open and awaiting the final disposition |
| 4 | Progress checkboxes read Phase 4 and Phase 5 unticked, with retirement "postponed"; the Phase 4 resequencing table's post-acceptance row read as future work | Phase 4 and Phase 5 are ticked with the executed retirement cited by commit (`19072ad` / `82c7951` / `882fc8d` / `3071fba`); the resequencing table carries a state column saying the same; a third line tracks the REVISE path as executed through step 7 and open at the owner's disposition |
| 5 | — | Three further inconsistencies found while regenerating, all fixed and disclosed above: the **51-vs-33** field count (§3), the comparator's **not-required 0** where the checker writes `not-required` and the true count is 81 (§3), and the dropped **proof-integrity caveat** (§3, audit-7 F4). The spec's four stale success-criteria checkboxes (audit-7 F6) were ticked with provenance, leaving the two the evidence does not support |

---

## 9. How every number here was derived

The rule for this record is that no number is typed by hand.

- **Run values** — parsed from the committed logs under `evidence/phase5-runs/revise-runs/` by
  `compare_revise_runs.fields`, the same parser behind `comparison.md`, called from
  `build_candidate_revise.py`.
- **The content-OID re-measurement** — run by this stage into
  `evidence/phase5-runs/head-6c35aa0/` and parsed from those logs by the same builder. The suite
  ran with `-rs` under the licence, from the canonical venv.
- **OIDs, commit counts, diff stats, name-status counts, path inventory, the retirement commits'
  subjects and path counts** — `git`, run by the builder, each with the range or command that
  defines it recorded beside the value in `candidate.json`.
- **Evidence hashes** — SHA-256 over the bytes on disk, 37 artifacts, in `candidate.json` under
  `evidence_hashes_sha256`. Headline entries:

| Artifact | SHA-256 |
|---|---|
| `.project/active/cutover-recovery/plan.md` | `1f10f2df24a450887364da8c15aad9d46f413e8324a218b0d22f8aa922b93e0e` |
| `.project/active/cutover-recovery/ledger-4a.json` | `013cd4aec88e91dbd4e06bafd4de481713210dd04c77774e3f20142a53484faf` |
| `.project/active/cutover-recovery/owner-disposition-20260811.md` | `17e115061d9268ed0dd45ba763f749e8d6106a6a538d93faf0c13b9ed3c8be0d` |
| `evidence/audit-7-retired.md` | `6b7b651fc5d7c0744cbe679c45c69fd82d112dc09534a5978dc39bb55f3f0e33` |
| `evidence/phase5-runs/revise-runs/comparison.md` | `372cfcd0335d374f2c646121d1617dc9c4b950e06cd777f427784a3b34e88299` |
| `tests/fixtures/v6_recapture_batch/batch.json` | `8feb8099a99273f390eb71f68f37f5d9786f9236954ab34880582ed22e1c462c` |

The plan hash covers the gate-2 and checkbox amendments made at this step. `candidate.md` and
`candidate.json` are excluded from their own hash table.

**The old builder is not deleted and is not the authority.** `build_candidate.py` reads inputs
the retirement removed (`scripts/run_elaboration_corpus.py` and its corpus-driver, residue and
scale outputs), so it cannot run against this tree. `build_candidate_revise.py` is its
replacement and says so in its docstring.

---

## 10. What this record does not claim

- It is **not** an audit. The audit is `evidence/audit-7-retired.md`, written by a session that
  did not implement the work; this record collates it.
- It does **not** accept anything. The final disposition is the owner's, R8 is unresolved, the
  ruff question is unanswered, audit-F4 is parked, and the six step-7 surfacings are open.
- The audit's own certification is **conditional**, and this record states the condition rather
  than rounding it to "certified".
- `check_proof_integrity.py` reading `0 problems over 0 blocked files` means *nothing left to
  check*.
- The v6 envelope digest is unkeyed: it proves coherence, not authenticity.
- Scale numbers for the two D-5 variants are a baseline, not a pass.
- Every `[OWNER]` ruling in the REVISE path rests on an agent-written handoff, not on the owner's
  own words.
