# Audit 9 — the fresh narrow audit of the final candidate

**Date:** 2026-08-14
**Auditor:** independent step-9 auditor (read-only; this file is the only write)

**Audited at:**

| repo | OID | branch |
|---|---|---|
| sysml-codegen | `bd54f0a1584eaf91c4f728ad3af5fb6b061f7c35` (working tree; content OID under audit `2819501178370db230acefdbcd02dfa15b409ac4`) | `item7-rebuild` |
| agentic-mbse | `6372ef7ba6ba4c869759fcf201c59aa128175c6f` | `item7-rebuild` |
| teax | `75eecb3bcf4baa0306107a96aa78b74ee667e970` (evidence-only) | `constraint-semantics-item3` |

`bd54f0a` is the step-7-8 bookkeeping commit that added this evidence directory on top of
`2819501`; it touches no shipped path, so every code probe below measures the content tree.

Environment for every probe: `/home/reid/1cfe/item7-rebuild-venv/bin/python`, license loaded
with `set -a; source /home/reid/1cfe/agentic-mbse/.env; set +a` in the same shell command. No
`uv run`. The protected `/home/reid/1cfe/agentic-mbse` checkout was read only for its `.env`.

---

## Subject 1 — Compiler convergence and symbol removal

**Probed:** that L-033's three compiler symbols and L-034's three name-keyed payload fields are
absent from `src/`, and that the two pinning test files collect and pass.

Symbol absence, greps run from `/home/reid/1cfe/sysml-codegen-item7-rebuild`, each written to
exclude the kept exact/UUID-keyed survivors:

```
grep -rnE '(^|[^a-zA-Z_])CompilationResult' src/ | grep -v 'ExactCompilationResult'      -> no hits
grep -rnE '(^|[^a-zA-Z_])CalcDefCompilationResult' src/ | grep -v 'ExactCalcDef...'      -> no hits
grep -rnP 'compile_calc_def(?!_exact)' src/                                              -> no hits
grep -rn 'output_expression_asts' src/    -> 5 hits, all `output_expression_asts_by_id`
grep -rn 'member_expressions' src/        -> 6 hits, all `member_expressions_by_id`
grep -rn 'all_member_names' src/          -> 1 hit, a comment at
                                             extraction/computed_attribute_extractor.py:313
```

The single `all_member_names` hit is prose inside a comment describing historical
computed-attribute behavior — the exact case the step-2 brief carved out as "not this payload".
No bare name-keyed symbol survives in production.

Pinning tests:

```
pytest tests/conformance/test_public_authority_switch.py \
       tests/unit/test_elaboration_import_boundaries.py -q -rs
-> 32 passed in 0.88s
```

**CONFIRM.**

---

## Subject 2 — Replacement coverage for deleted tests

**Probed:** the three fast checker modes at HEAD, a recount of the committed sweep logs, and
eight spot-checked rows run live.

Checker modes, run by me:

```
python scripts/check_ledger_4a.py paths     -> 304 rows checked, 0 problems       (rc=0)
python scripts/check_ledger_4a.py surface   -> 0 unrowed breakages                (rc=0)
python scripts/check_ledger_4a.py groups    -> all six 4B groups affected=0 READY (rc=0)
```

Spot-checked replacement rows, each run live with the license loaded — the three named in my
charge plus five I chose (`L-033`/`L-034` because they are subject 1's own rows, `L-280` as a
step-2 disposition row, `L-298` because the checker docstring records it as the one false
label, `L-305` as the last row):

```
L-179  green   (10 passed; 1 passed)      L-033  green   (1 passed; 1 passed)
L-007  green   (1 passed)                 L-034  green   (1 passed; 1 passed; 28 passed, 9 skipped)
L-010  green   (1 passed)                 L-280  green   (1 passed; 1 passed; 1 passed)
                                          L-298  not-required (row deletes nothing)
                                          L-305  green   (1 passed)
```

Committed-log integrity, recounted by me rather than read off the record — for each of
`final-runs/run{1,2,3}/ledger_replace.log`:

```
awk '{print $1}' <log> | sort | uniq -c
-> 223 green   79 not-required   0 FAIL      (identical in all three runs)
```

The three logs differ from one another only in per-node wall-clock times, which is what three
independent runs of the same sweep should look like.

**FINDING (major) — the sweep is 302 rows, not 304.** 223 + 79 = 302, and the logs contain
exactly 302 row lines against a ledger of 304 rows. The two absent rows are `L-036` and
`L-037`, established by set difference:

```
python -c "...set(ledger ids) - set(ids in run1/ledger_replace.log)..."
-> in ledger not in log: ['L-036', 'L-037']
```

Cause: `check_replacements` skips every row whose repo is not this one
(`/home/reid/1cfe/sysml-codegen-item7-rebuild/scripts/check_ledger_4a.py:761`):

```python
if row["repo"] != "sysml-codegen":
    continue
```

`L-036` and `L-037` are the ledger's only two `agentic-mbse` rows, both `migrate`. Their cited
replacement proofs do not exist:

```
L-036 -> tests/unit/test_constraint_extraction.py
L-037 -> tests/unit/test_executable_profile.py

cd /home/reid/1cfe/agentic-mbse-item7-rebuild
pytest tests/unit/test_constraint_extraction.py tests/unit/test_executable_profile.py -q -rs
-> collected 0 items / no tests ran in 0.00s
ls tests/unit/test_constraint_extraction.py -> No such file or directory
```

The real files live under `tests/test_sysml/`, and they do carry the responsibility:

```
pytest tests/test_sysml/test_constraint_extraction.py \
       tests/test_sysml/test_executable_profile.py -q -rs
-> 65 passed in 1.12s
```

Three things follow, and they should be recorded separately.

- **The substantive coverage holds.** I ran the real replacement files myself; 65 tests pass.
  This is a citation defect, not a coverage hole.
- **The record overclaims.** `candidate.md` §3 and T4 say the checker "ran the full 304-row
  sweep"; it ran 302 of 304. The record's own arithmetic (223 + 79) contradicts the word "full".
- **There is an undisclosed sixth checker ceiling.** The checker's docstring
  (`scripts/check_ledger_4a.py:35-63`) enumerates five things it cannot see and states that a
  green run means "these five classes are unchecked". Cross-repo skipping is not among the five.
  This matters because it is precisely the L-179 defect class — a stale replacement citation —
  surviving in the two rows the checker structurally cannot reach. §6.1 credits the battery with
  catching L-179; it could never have caught these two.

I did not re-run the full ~11-minute sweep. I relied on the committed `ledger_replace.log`s for
the full-sweep outcome, after recounting all three from raw text and confirming they agree.

**FINDING** (details in the findings list, F1).

---

## Subject 3 — R8 same-leaf qualified-name preservation

**Probed:** that the inverted R8 witness and the option-C blast-radius pins exist and pass.

```
pytest tests/integration/test_costed_component_exact_route.py \
       tests/conformance/test_exact_group_identity.py -q -rs
-> 29 passed in 0.95s
```

The witness node named by the step-3 brief is present and is a positive proof, not a refusal:
`test_a_two_term_same_name_rollup_keeps_both_resolved_source_families`
(`/home/reid/1cfe/sysml-codegen-item7-rebuild/tests/integration/test_costed_component_exact_route.py:324`).
Its docstring records both narrowness pins the brief required — `panel_total` for the
single-resolved-chain boundary and `repeated_panel` for semantic-source deduplication. The
`panel` versus `caster` identities survive as distinct instance-scoped modules
(`:188-193`), and the hand-derived arithmetic the brief specified is asserted at `:309-318`
(`panel_capital == 180.0`, `caster_capital == 360.0`).

**CONFIRM.**

---

## Subject 4 — Portable provenance and route-equal bytes

**Probed:** the three byte-identity pins, and the generated bytes for checkout-absolute paths.

```
pytest tests/conformance/test_exact_route_generated_package.py \
       tests/conformance/test_snapshot_v6_routes.py \
       tests/conformance/test_exact_route_fingerprint_stability.py -q -rs
-> 13 passed in 4.71s   (no skips)
```

`test_the_two_packages_are_byte_identical`
(`/home/reid/1cfe/sysml-codegen-item7-rebuild/tests/conformance/test_exact_route_generated_package.py:114`)
is the pin L-179 now cites, and I read it rather than trusting its name. It asserts three
things, and the third is the one that matters here:

```python
differing = sorted(name for name in live if live[name] != from_snapshot[name])
assert differing == []                                     # routes are byte-equal
commented = [n for n in live if "SysML Source: root-0/" in live[n]]
assert commented                                           # anti-vacuity: the comment is present
absolute = [n for n in live if f"SysML Source: {FIXTURE}" in live[n]]
assert absolute == []                                      # and it is not checkout-absolute
```

So the pin is not vacuous — it would still fail if step 5 had cured route divergence by simply
dropping the provenance comment.

Independent grep over the committed generated bytes:

```
grep -rn "sysml-codegen-item7-rebuild\|item7-rebuild-venv\|/tmp/pytest\|/tmp/tmp" \
     tests/fixtures/baseline_outputs/    -> no hits
grep -rhoE "root-[0-9]+/[^ \"']*" tests/fixtures/baseline_outputs/ | sort -u
     -> root-0/model.sysml, root-0/library.sysml, root-0/toy_library.sysml,
        root-0/library/physics/*.sysml, root-0/library/analyses/thermal_loads.sysml
```

One `/home/reid` class does appear in `baseline_outputs/solar_battery/computation_graph.json`
(five doc-comment fields citing `/home/reid/PyFECONS/pyfecons/costing/calculations/*.py`).
These are **authored SysML doc-comment text carried through verbatim**, not paths the generator
computed from its own checkout — a different thing from the referent step 5 made portable, and
outside this subject. Recording it so a later reader who runs the same grep is not surprised.

**CONFIRM.**

---

## Subject 5 — Final gate semantics

**Probed:** every R12 gate value re-measured live in both repos, the two enumerated ruff
baseline sets compared finding-by-finding, and the mypy clause's disputed number tested against
the base it names.

### Gate values, re-measured by me at the content OIDs

| gate | R12 / recorded | measured now | verdict |
|---|---|---|---|
| codegen `ruff check src` | 12 (enumerated set) | **Found 12 errors** | matches |
| codegen `ruff check src tests scripts` | 642 (T4) | **Found 642 errors** | matches |
| codegen `mypy src` | 52 in 11 | **Found 52 errors in 11 files** | matches |
| agentic `ruff check src` | 1 (enumerated) | **Found 1 error** | matches |
| agentic `ruff check tests` | 120 (T4) | **Found 120 errors** | matches |
| agentic `mypy src` | 108 in 26 | **Found 108 errors in 26 files** | matches |

Every T4 gate number reproduces exactly. Tooling: ruff 0.16.2, mypy 2.3.0, matching `env.json`.

### The enumerated ruff baseline sets — the substantive check

R12 requires set identity (`--output-format concise`, file:line:code), not count equality, so I
compared the sets, not the totals.

Codegen `ruff check src --output-format concise` returns exactly the 12 R12 enumerates, all
UP042, at exactly the recorded file:line pairs: `core/models.py:13`,
`elaboration/diagnostics.py:10`, `elaboration/graph.py:66`, `elaboration/identity.py:139`,
`extraction/data_models.py:194`, `extraction/expression_compiler.py:28`,
`extraction/source_evidence.py:37/57/151`, `resolution/models.py:48/203/284`. Class names match
too (BindingResolutionType, ElaborationCode, ValueSite, NodeKind,
ComputedAttributeClassification, Compilability, SourceForm, ValueSiteKind, ReadinessCode,
EntryPointType, ModuleKind, ConstraintInputResolution).

Agentic returns exactly the one R12 enumerates:
`src/agentic_mbse/extraction/index.py:146:5: N806 Variable _UNNUMBERED_RE ...`.

**Both recorded baseline sets match what ruff actually reports, byte for byte. CONFIRM** for
the amended ruff clause.

### The SURFACED DISCREPANCY — ruling

R12 (`/home/reid/1cfe/sysml-codegen-item7-rebuild/.project/active/elaborator-cutover/spec.md:352-353`)
says mypy "does not exceed the Item-6 baselines of 71 errors in 17 codegen files and 105 errors
in 23 agentic files." Every recorded measurement of the agentic arm is 108-in-26. `candidate.md`
§6.2 surfaced this rather than resolving it, which was the right call and left the ruling to me.

I tested it the only way that settles it — by measuring the base R12 names, under the
environment R12 itself now mandates. I extracted each Item-6 base OID read-only into my
scratchpad (`git archive <base> | tar -x -C <scratchpad>`; no checkout, no worktree, no write
to either repo) and ran the venv mypy against it:

```
agentic base 5088b417c9e5453271291d46cd5fb23fc0579b1e -> Found 118 errors in 28 files
agentic HEAD 6372ef7ba6ba4c869759fcf201c59aa128175c6f -> Found 108 errors in 26 files
codegen base 1672c5766f67e7716f3c9f8f636c21e2ea444601 -> Found  73 errors in 18 files
codegen HEAD 2819501178370db230acefdbcd02dfa15b409ac4 -> Found  52 errors in 11 files
```

Then the set comparison, on file|message identity:

```
comm -13 base_errs.txt head_errs.txt   (in HEAD, not in base)  -> EMPTY
comm -23 base_errs.txt head_errs.txt   (in base, not in HEAD)  -> 10 errors
```

The HEAD finding set is a **strict subset** of the base set. The 10 removed errors are one
`import-not-found` for module `common`, seven `no-redef` cascading from it, one `no-redef` in
`executable_profile.py`, and one `no-any-return` in `level6_architecture.py` — all three files
the recovery's cleanup hunks touched. That reproduces `plan.md:1850`'s recorded "118 → 108
errors, zero new and ten fixed, all ten from the three cleanup hunks" exactly, and I confirmed
the cause in source: the base carried a `try: from .common import ... except: from common
import ...` fallback (`git show 5088b417:src/agentic_mbse/validation/level4_constraints.py:20,31`)
which HEAD replaced with `from agentic_mbse.validation.common import ...` (`:27`). So the 118 is
a real property of the base, not an artifact of my extraction method.

**Ruling: the clause's number is wrong. The gate is not failing.**

The reasoning, stated plainly:

1. The true Item-6 agentic baseline, under the environment R12 mandates, is **118 in 28** — not
   105 in 23. 108-in-26 is an improvement of ten errors and two files against it.
2. Zero new findings, proven by set containment, not by count.
3. The same drift shows on the codegen arm, which is the discriminating evidence that this is
   environmental and not agentic-specific: R12 records 71-in-17, the same base OID measures
   **73-in-18** under this venv. Two independent baselines, both inherited, both drift upward
   when re-measured under the mandated toolchain.
4. The mechanism is recorded in R12's own amendment note: the original `uv run …` spelling
   "resolves the parked `/home/reid/1cfe/agentic-mbse` checkout … and would measure the wrong
   environment." Step 6 restated the command list to the venv form but did not re-measure the
   inherited mypy baselines against that form. The numbers are stale-by-environment — carried
   across from the Item-6 close record
   (`.project/completed/20260810_elaborator-identity-completion/plan.md:859`) without
   re-measurement.

Every operative arm of the mypy clause holds: zero new findings, no error in a changed file,
and the totals are below the real baselines on both repos. Read literally against a number no
measurement this recovery produced supports, the clause fails; read for its substance, it passes
with margin. This is a defect in the spec text, not in the tree.

**Recommended (owner call, since disposition 2 authorized amending the ruff clause only):**
amend R12's mypy clause to the measured Item-6 baselines under the mandated environment —
codegen **73 in 18**, agentic **118 in 28** — the same treatment disposition 2 gave the ruff
clause when it found the recorded 14 was stale and recorded the measured 12.

### One scope mismatch, found while checking the above

T4 reports `ruff check src tests scripts` = 642. R12's full-tree arm governs `src tests` against
Item-6 baselines of 358 codegen / 127 agentic. Measured at the **governing** scope:

```
codegen  ruff check src tests  -> 143   (base 1672c576: 374; R12 records 358)
agentic  ruff check src tests  -> 121   (base 5088b417: 127; R12 records 127 — exact)
```

The arm passes comfortably in both repos. The record simply reports a number at a scope no
clause governs, and omits the one that is governed. Minor, but a reader checking T4 against R12
cannot close the loop. (Note the codegen full-tree baseline shows the same small drift: 358
recorded, 374 measured. The agentic one is exact, which is consistent with ruff being far less
environment-sensitive than mypy.)

**FINDING** (F2, F3 in the list).

---

## Subject 6 — Evidence consistency

**Probed:** re-ran the comparator myself, recounted headline claims from raw logs, checked the
OIDs and the shipped diff in git, diffed the quoted tables against their generated source,
verified the evidence hash map, and re-derived numbers from git and from the matrix.

**Comparator, re-run by me:**

```
python .project/active/cutover-recovery/evidence/phase5-runs/compare_final_runs.py
-> EXIT=0
-> "**51 / 51 fields identical across all three runs.**"
```

`candidate.json` `three_runs.fields` holds 51 entries and none is marked non-identical.

**heads.tsv** — all three runs, byte-identical and naming exactly the charged OIDs:

```
codegen  2819501178370db230acefdbcd02dfa15b409ac4
agentic  6372ef7ba6ba4c869759fcf201c59aa128175c6f
teax     75eecb3bcf4baa0306107a96aa78b74ee667e970
```

**Shipped-path diff, owner-ruled `540ad59` vs content `2819501`:**

```
git diff --stat 540ad59 2819501 -- src tests scripts docs pyproject.toml  -> empty, rc=0
git diff --name-status 540ad59 2819501
-> A  .../phase5-runs/{build_candidate_final.py, chain_final.sh, compare_final_runs.py,
                       run_final_battery.sh}
   M  .project/active/cutover-recovery/ledger-4a.json
```

Empty on shipped paths, and the one modified file is the L-179 ledger repair §6.1 describes.
The builder's assertion is true.

**Headline claims re-derived from raw logs** (not from the record), all three runs:

| claim | run1 | run2 | run3 |
|---|---|---|---|
| codegen suite | 2086 passed, 34 skipped, 88 deselected | same | same |
| `no live syside license` lines in `suite_codegen.log` | 0 | 0 | 0 |
| agentic suite | 1831 passed, 1 skipped, 5 deselected | same | same |
| execution lane | 88 passed | same | same |
| corpus `-k corpus` | 9 passed, 2199 deselected | same | same |
| `--verify` / `--check` | 15 captured, 22 refused, 0 deviations | same | same |
| non-timestamp fixture diff lines | 0 | 0 | 0 |

The licence proof is direct as claimed: zero skip lines, in all three runs, from the `-rs`
output itself. `env.json` records `import_path_gate: PASS` with all three imports resolved to
their required worktrees.

**Quoted tables vs generated source.** I extracted the markdown table rows from each `## TN`
block in both files and compared them programmatically:

```
T1 IDENTICAL (10 lines)   T2 IDENTICAL (10)   T3 IDENTICAL (8)   T4 IDENTICAL (25)
T5 IDENTICAL (5)          T6 IDENTICAL (prose block, matches verbatim)   T7 IDENTICAL (6)
```

`candidate.md` quotes `final-candidate-tables.md` verbatim, as claimed.

**Evidence hash map.** All 79 entries in `candidate.json.evidence_hashes_sha256` re-hashed:
**0 missing, 0 mismatched.**

**Numbers re-derived** — more than the three required:

| record claim | my derivation | result |
|---|---|---|
| Tracked files 2,270 | `git ls-tree -r --name-only 2819501 \| wc -l` | 2270 ✓ |
| Commits since base 370 | `git rev-list --count 1672c576..2819501` | 370 ✓ |
| 825 A / 137 M / 196 D | `git diff --name-status 1672c576 2819501 \| uniq -c` | 825 A, 137 M, 196 D ✓ |
| 1176 files, +295589 / −106678 | `git diff --shortstat` | exact ✓ |
| Production modules 72 | `git ls-tree -r src \| grep -c '\.py$'` | 72 ✓ |
| Numbered reference documents 31 | `git ls-tree -r docs/architecture/reference` | 31 ✓ |
| Scripts 45 | `git ls-tree -r scripts \| grep -c '\.py$'` | 45 ✓ |
| T6: 288 / 156 PASS / 1 PARTIAL / 131 RETIRED / 0 UNTESTED | independent recount of `docs/architecture/verification-matrix.md` | 288 rows, 156 PASS, 1 PARTIAL, 131 RETIRED, 0 UNTESTED ✓ |

**FINDING (minor) — T1's name-status line omits renames.** It reports 825 added / 137 modified
/ 196 deleted. `git diff --name-status` also returns 18 renames (1 `R094`, 17 `R100`). The
three reported categories sum to 1158, and only 1158 + 18 = 1176 reconciles with the "1176 files
changed" in the row directly above it. A reader checking the row against itself finds an
18-file gap with no explanation.

Everything else in subject 6 verifies. **CONFIRM with F1 and F4 carried.**

---

## Findings

**F1 — major. The replacements sweep covers 302 of 304 rows, and the two uncovered rows carry
broken citations.** `check_replacements` (`scripts/check_ledger_4a.py:761`) silently skips rows
whose `repo != "sysml-codegen"`. The two `agentic-mbse` rows, `L-036` and `L-037`, cite
`tests/unit/test_constraint_extraction.py` and `tests/unit/test_executable_profile.py`; neither
file exists in `/home/reid/1cfe/agentic-mbse-item7-rebuild` (both collect 0 items). The real
files are `tests/test_sysml/test_constraint_extraction.py` and
`tests/test_sysml/test_executable_profile.py`, which I ran: 65 passed. Three parts:
(a) `candidate.md` §3/T4's "full 304-row sweep" is an overclaim — 223 + 79 = 302;
(b) the two citations are wrong and should be repointed;
(c) cross-repo skipping is an undisclosed sixth ceiling — the checker docstring
(`scripts/check_ledger_4a.py:35-63`) enumerates five and instructs the reader to treat a green
run as "these five classes are unchecked". It is the same stale-citation class as L-179, in the
two rows the checker structurally cannot reach.
*Substantive coverage is intact — I verified it directly. This is a record-accuracy and
checker-honesty defect, cheap to fix: repoint two paths, correct the sweep wording, add the
sixth ceiling to the docstring.*

**F2 — minor. R12's mypy baselines do not reproduce under the environment R12 mandates.**
Recorded: codegen 71-in-17, agentic 105-in-23. Measured at the same base OIDs with the venv
mypy: codegen **73-in-18**, agentic **118-in-28**. Ruling below. Fix is a spec amendment, and
disposition 2 covered only the ruff clause, so it needs the owner.

**F3 — minor. T4's full-tree ruff number is at a scope R12 does not govern.** T4 reports
`ruff check src tests scripts` = 642; R12's arm is `src tests`, measured 143 codegen / 121
agentic against baselines of 358 / 127. The arm passes with margin, but the record does not show
the governed number, so T4 cannot be checked against R12 as written.

**F4 — minor. T1's name-status line omits 18 renames**, leaving 825 + 137 + 196 = 1158 against
the 1176 files changed reported one row above.

**Count: 1 major, 3 minor, 0 blocking.**

---

## Ruling on subject 5's mypy-clause question

**The clause's number is wrong. The gate is not failing.**

The agentic Item-6 base (`5088b417`) measures **118 errors in 28 files** under the environment
R12 mandates, not 105-in-23. The content tree measures 108-in-26, and its finding set is a
strict subset of the base set — zero new, ten fixed, all ten traceable to the three recorded
cleanup hunks and reproducing `plan.md:1850` exactly. The codegen arm drifts the same way
(71-in-17 recorded, 73-in-18 measured), which shows the cause is the measurement environment
rather than anything about agentic-mbse: R12's own amendment note records that the pre-cutover
`uv run` spelling resolved the parked checkout, and step 6 restated the commands to the venv
form without re-measuring the inherited mypy baselines against it.

Every operative arm of the clause holds. The literal number should be amended to the measured
values — codegen 73-in-18, agentic 118-in-28 — exactly as disposition 2 handled the stale ruff
14. That is an owner decision, not an audit one.

---

## What I ran versus what I relied on

**Probes I ran this session** (nothing below is taken from an implementation note):

- All three ledger checker fast modes, and eight replacement rows spot-checked live.
- Four focused pytest invocations covering subjects 1, 3, and 4 — 32, 29, 13, and 65 tests.
- Every R12 gate command in both repos, plus the two enumerated ruff sets in concise form.
- Both Item-6 base OIDs extracted read-only into scratchpad and measured with mypy and ruff.
- `compare_final_runs.py`, checked for exit code and output.
- Raw recounts of all three `ledger_replace.log`s and of every T4 headline claim from the run
  logs directly.
- All 79 evidence hashes; the table-quotation diff; eight git/matrix re-derivations.

**Committed evidence I relied on** (after checking its internal consistency): the full-sweep
replacements result and the full-suite counts under
`.project/active/cutover-recovery/evidence/phase5-runs/final-runs/`. I did not re-run the full
suites or the 11-minute sweep. I did recount every claim I cite from those logs out of their raw
text, and confirmed the three runs differ only in wall-clock timings.

**Not re-audited, per charge:** the 195 deletions individually, and the program of
`audit-7-retired.md`.

---

## Verdict

**CERTIFY-WITH-RESIDUALS** — all six subjects verify on their substance, with every gate value,
byte-identity pin, symbol removal, and evidence hash reproducing under my own probes; the four
residuals are record-accuracy and spec-text defects (one major: the sweep is 302 of 304 rows
with two broken cross-repo citations the checker cannot reach; three minor), none of which
touches the tree's correctness, and the R12 mypy discrepancy resolves as a stale spec number
rather than a failing gate.
