# PIPELINE-TRUTH Epic — Full-Scope Report

**Date**: 2026-07-06
**Branch**: `pipeline-truth-epic` → PR [#5](https://github.com/1cFE/sysml-codegen/pull/5) (123 commits, 260 files, +33,266 / −1,594)
**Companions**: agentic-mbse branch `pipeline-truth-item4` (pushed, PR body drafted); fusion-tea branch `chore/retire-pipeline-truth-workarounds` (local)
**Audience**: Reid. Written to be readable without having followed the run.

---

## 1. What this epic was about

sysml-codegen turns SysML v2 models into executable Python simulation packages. Before this
epic, our first real consumer — fusion-tea, a fusion power-plant techno-economic model — could
not generate its package end-to-end. Generation aborted on exactly 10 model references, and
fusion-tea papered over the gap with a stack of workarounds: a hand-written bridge script that
injected 10 values, a fake model element (`hif_driver_instance`) added just to make wiring
resolve, a two-pass execution hack for a feedback loop, and hand-written input JSON files.

Behind that headline gap sat a credibility problem discovered by an 8-agent code sweep
(`.project/research/20260706_pipeline-truth-discovery.md`): 16 places where the pipeline
silently dropped or mis-handled model content instead of reporting it, 25 tests that were
structurally unable to fail (their expected values were computed by the code they were
testing), a "verification matrix" (our REQ-to-test traceability doc) whose PASS claims
diverged from reality in ~11 rows, and a validator in the companion repo that had never once
been able to fail.

The epic's mission, in one line: **the generated package is the truth** — a consumer's real
models generate, wire, and execute with zero hand-plumbing, and every diagnostic and test
that claims to guard something actually can.

## 2. The outcome, in one paragraph

All 10 items landed and passed independent audit. fusion-tea's models now generate the full
package with **zero offenders** from generated artifacts alone; its reference result (run-C
lcoe = $270.1211779380445/MWh) reproduces **bit-exactly** through the generated package, and
a perturbed-input rerun proves the generated JSON inputs are actually consumed. Every
fusion-tea workaround is deleted upstream. The constraint report now sees the constraint
shape fusion-tea actually uses, works offline from snapshots, and every diagnostic added or
changed in this epic ships with a test that demonstrably fires on the shape it claims plus a
test that it stays silent on clean input. Final gates: 2069 tests passed (up from 2005 at
epic start, with all deletions accounted), ruff 17 (was 21), mypy 104 (was 109).

---

## 3. Item-by-item

### Item 1 — Plant-value & blind-spot fixtures

**What.** Authored the test models ("fixtures") that reproduce, in-repo, the exact model
shapes fusion-tea uses to hand values to a whole-plant calculation — shapes no fixture
covered before. The headline fixture (`tests/fixtures/plant_values/`) deliberately **fails**
generation the same way fusion-tea did, pinned by a test, so Item 2 had a measured "before"
state to flip. A second fixture (`plant_value_shapes`) covers nine secondary shapes (quoted
output names, mixed return styles, enum-valued attributes, deep specialization chains, etc.),
each pinned at its *observed* current behavior. Also: selective-capture tooling (`--fixtures`
flag on the capture scripts) so one fixture can be re-captured without rewriting all of them,
and a refresh of three stale committed snapshots.

**Why it matters.** Everything downstream builds on these. Without a fixture that actually
trips the failure, Item 2's fix would have been unverifiable against "before", and Item 5's
diagnostics would have had no substrate to fire on. The selective-capture flag is what made
every later item's "only my fixture changed" byte-identity gate checkable at all.

**Judgment calls / gaps.**
- *The V11-trip was not automatic.* Review caught that a prior epic's pre-fill machinery
  would silently give the fixture's literals values (no trip, nothing for Item 2 to flip).
  The fixture was re-specified so literals are consumed cross-part, gated by a capture-time
  probe requiring a non-empty offender set covering all three mechanisms.
- *Audit cure*: the first landed version left one mechanism "trip-only" (nothing for Item 2
  to flip it TO) and a stale hand-computed anchor. Cured: the source literal restored
  (`:>> chamber.cost_per_unit = 7.0`), anchor recomputed and documented from fixture source.
- *Discovery en route*: `deep_cross_scope_probe` had been parse-broken all along (`derived`
  is a reserved KerML keyword) — that's why it never had a committed snapshot. Renamed and
  captured. Multi-hop chain truncation (a register finding) reproduced live here, feeding
  Item 5.
- *Deferred*: the low-leverage remainder of the discovered shape gaps is filed in a
  fixture-gap register rather than built.

### Item 2 — Whole-plant cross-part value resolution (the headline)

**What.** The mechanism fix. Built a **supplied-value materializer**
(`resolution/supplied_values.py`, REQ-SVM-01..04): a pre-pass that finds model literals
sitting on subsystem attributes (in redefinitions and design-override blocks — data the
extractor already captured but the graph builder never consumed), resolves the three-tier
precedence (usage override > specialized-def `:>>` > base def), and injects each as a
synthetic design attribute keyed by its **source qualified name**. The existing resolution
then carries the value to every consumer. Four shapes covered: (a) subtype-def literal via
retype, (b) bare no-retype `part :>>` override block, (c) plain one-hop cross-part attribute,
and (d) in-part reference to an inherited attribute the same def redefines. Also fixed two
latent `if value:` truthiness bugs that would have silently dropped a legitimate `0.0` to
null, and built the minimal in-repo pipeline runner (`tests/runtime/pipeline_runner.py`) that
actually executes generated packages for tolerance testing.

**Why it matters.** This closes the gap that made fusion-tea's package un-generatable — the
epic's entire reason to exist. The mechanism decision (fill values vs wire channels) also
sets the consumer contract: value-fill keeps the 10 parameters visible as JSON inputs a user
can edit, which is what a techno-economic analyst actually wants, and source-QN keying
collapses fan-out (one attribute feeding two differently-named calc inputs becomes ONE JSON
key, not two that can drift apart).

**Judgment calls / gaps.**
- *Value-fill over channel wiring* — argued from evidence: all 10 fusion-tea sources are
  literals with no producing calculation to wire to; wiring would have removed the params
  from the input JSON (breaking the consumer's harness) for zero gain.
- *Offender #9/#10 scope* — review caught that two of the 10 offenders are **in-part**, not
  cross-part; the item was re-scoped to include shape (d) rather than shipping a false "zero
  offenders" claim. Both cleared by the same mechanism (no escalation needed).
- *New REQ family, not an extension* — the design initially framed this as extending the
  existing literal-value-propagation family; its own doc explicitly fences that mechanism
  off from this case, so it landed as REQ-SVM with honest cross-references.
- *Audit cure (narrative only)*: the close-out claimed most values cleared via a
  "real-attribute-wins" path; the audit's logged probe showed all 10 clear by synthesis.
  Corrected — the code was right, the story was wrong.
- *Deferred*: non-literal right-hand sides in override blocks (expressions, chains) are
  **loudly skipped** by the materializer with a count-summary warning, not resolved —
  expression-valued overrides belong to a future expression-aware epic.

### Item 3 — fusion-tea acceptance & workaround retirement

**What.** The end-state assembly the original validation report never tested. In fusion-tea:
deleted `sanitize_names.py`, deleted the fake `hif_driver_instance` model element (and
re-anchored the affected channel names), removed the two-pass feedback hack, rewrote
`run_anchors.py` to a single pass reading generated inputs. In this repo: an acceptance test
suite reproducing run-C bit-exactly through the pipeline runner; a perturbed-input test
(gain 80→100 → lcoe 216.55528392479388, hand-computed from the model's own DCF arithmetic —
proving inputs are consumed, not baked-in defaults); the live-vs-snapshot parity test
parametrized over six shape-bearing fixtures (it previously ran on one trivial model); and
the fusion-tea canonical models vendored with a committed snapshot so all of this runs
license-free forever after.

**Why it matters.** SC-B's "reproduces the anchor" claim was previously vulnerable to a
subtle hole: every anchor value equaled a baked schema default, so a JSON-ignoring executor
would have passed identically. The perturbed-input rerun closes that permanently. And
"workarounds deleted, not just deletable" is the difference between a demo and a consumer
actually depending on the generator.

**Judgment calls / gaps.**
- *Runner completion deviation*: fusion_tea is the first multi-output package run through
  the in-repo runner, which needed its harness stub completed. Audit verified this touched
  zero `src/` and the generated wiring was already correct — harness surface, not a fix
  in disguise.
- *Kept, deliberately*: fusion-tea's `ηG > 10` viability check stays harness-side until a
  future constraint-execution epic; their teax OutputRouter/WriteHandler stays (out of
  scope by design); the seven `out attribute` style conversions were inspected and kept
  (genuine outputs, not workarounds). Historical documents still mention the workarounds —
  as history.
- *Gap noted by audit*: fusion-tea's real teax executor ran green during implement but was
  not re-run in the audit session (separate venv); corroborated instead via byte-identical
  wiring plus the in-repo executor reproducing identical numbers.

### Item 4 — Subtype-aware enumeration & constraint-report truth

**What.** The model-wide element queries in both repos used an exact-type match that never
sees subtypes. Consequence: `assert constraint` (which parses to `AssertConstraintUsage`, a
subtype) was invisible to the "constraints were dropped" report — the report was completely
silent for exactly the constraint shape fusion-tea uses. Fixed at one choke point: the shared
adapter (`agentic-mbse`) gained `include_subtypes` and `exclude` parameters plus a
**hard error on unknown type names** (previously `is_instance` silently returned False for
any name missing from its whitelist — a silent-failure generator). The constraint report was
split into collect (live model → typed manifest) + render (pure), the manifest is now
**serialized into snapshots** (format v2) so `generate --from-snapshot` reports constraints
identically to a live run, and three broken agentic-mbse validators were fixed — including a
Level-3 circular-import check that queried an abstract type, matched nothing, and had
therefore **never been able to fail**.

**Why it matters.** A diagnostic that cannot fire is worse than no diagnostic — it certifies
silence. fusion-tea's models are full of assert constraints that were being dropped with no
trace; now the report names them (wi014_toy's `affordable` assert at `toy_plant.sysml:51` is
the canonical pin; catf_mfe reports 65). The hard-error on unknown type names immediately
paid for itself: it exposed three production call sites asking for `LiteralReal` — a class
that does not exist in syside — dead branches that had silently returned False forever.

**Judgment calls / gaps.**
- *`satisfy` is excluded, deliberately*: syside's hierarchy makes `SatisfyRequirementUsage` a
  `RequirementUsage` subtype (my verification caught the spec claiming the opposite), so the
  requirement-exclusion drops satisfy-assertions too. Accepted and documented: no supported
  model uses `satisfy`, and the report's scanned/reported/excluded counts keep the exclusion
  observable.
- *Enum attributes stay invisible to entry-point derivation* (opt-out, pinned): flipping them
  on would mint mistyped float entry points; the safe diagnostic landed in Item 5 instead.
- *Format bump cost*: v2 hard-rejects v1 snapshots, forcing a repo-wide re-capture (23
  snapshots) — sequenced as one reviewed commit. Six fixtures showed extra diffs; audit
  traced each to pre-existing staleness, not behavior change (one disclosure was
  under-itemized and is noted in the audit).
- *An 8-row decision table* (published in agentic-mbse's docs) records every call site's
  opt-in/opt-out with rationale, so future type-visibility choices are deliberate.

### Item 5 — Silent-failure hardening

**What.** The discovery register listed 16 code sites where an unsupported model shape
produced a silent wrong outcome (dropped parameter, mis-wire, wrong math) instead of a
diagnostic. Per the epic's verify-then-fix protocol, each was **reproduced or refuted before
fixing**: 13 confirmed, 3 reclassified — including one live refutation (the claimed
"silent cross-wire" at D3-7 is actually blocked loudly by an existing registry collision
guard). The confirmed findings were fixed by family at choke points: (1) *blind dispatch* —
every expression/AST dispatch now has a total, loud terminal arm (unknown binding types warn;
3+-segment chains hard-diagnose instead of silently truncating; `^` translates to `**`
instead of silently becoming XOR); (2) *gated reports* — the usage-extraction warning report
that the live path threw away is now surfaced, and zero-found sentinels ("scanned N, matched
0") replace silence; (3) *name-keyed lookups* — ambiguous name matches now require uniqueness
or warn; (4) *exception swallows* — narrowed and logged (including `--smart-regen` no longer
silently regenerating a handwritten implementation to a stub on a transient read error).
Plus: the identifier sanitizer now fail-fasts on collisions (`'a b'` and `'a-b'` can no
longer silently merge into one key) and always yields legal Python identifiers; non-numeric
(enum/bool/string) entry points get a warning at JSON emission instead of a silent null.

**Why it matters.** This is the epic's insurance policy. Item 2 makes the happy path work;
Item 5 guarantees that when a consumer's model steps outside the supported subset, they get
told — instead of a package that generates fine and computes the wrong number. The root
cause found for the `^`→XOR bug is illustrative: the operator map was keyed by strings but
received enum values, so **every** operator was going through the fallback — the map had
never worked.

**Judgment calls / gaps.**
- *Loud-reject over full-parse for multi-hop chains*: parsing `a.b.c.d` chains is new
  capability, not hardening — filed as `[MULTIHOP-CHAIN-PARSE]`; until then the shape is a
  hard diagnostic, never a truncation.
- *Numeric expression defaults stay at DEBUG* (decided, not forgotten): a `Real` attribute
  with default `1.0 / q_eng` resolves through the expression-aware path and never lands as a
  silent omission; warning on it would false-fire on every legitimate expression default.
- *Closed-by-construction* accepted for two findings where the trip shape is unreachable
  (the closing invariant is documented and guard-pinned, no fake test).
- *Deferred*: the ~20-site benign "hygiene tail" is filed as one consolidated
  `[D3-HYGIENE-TAIL]` entry; some low-value single-INFO sentinel sites; per-component
  reference-doc touches were folded into Items 7/10 (verified there).

### Item 6 — Self-referential test remediation

**What.** Re-anchored the 25 tests discovery flagged as structurally unable to fail. The
disease: `expected = production_function(...)` — the test recomputes its expectation with the
same code under test, so both are wrong together. Every fix is a hand-transcribed literal or
an identity-selected on-disk anchor, each with a provenance comment naming its source. Two
pass-or-**skip** tests (they could never reach FAIL) converted to pass-or-fail. One test
re-anchored from a syntactic path check to on-disk truth (generated import paths must
correspond to files that exist). A "how to anchor a conformance expectation" note added to
the tests README so the anti-pattern doesn't regrow.

**Why it matters.** The verification matrix's PASS column is only as credible as the tests
behind it. Three deliberate production mutations were applied as proof: each made the
re-anchored tests go red and only the re-anchored tests (the old versions would have passed
all three). Two real behaviors surfaced that only literals catch — module names lowercase
their design prefix, and aggregation channel names carry a doubled trailing segment. The
doubling was verified **deliberate** (ADR-003 composition: channel = usage-QN + output name,
and an aggregation's QN already ends with the attribute) and is now documented at every
pinned literal so nobody "fixes" it later.

**Judgment calls / gaps.**
- *Test count dropped 2031 → 2005, on purpose*: 30 tautological parametrization instances
  replaced by stronger single pins (+4 new); the ledger names every one. No non-self-test
  lost coverage.
- *LOW-tier reconstruction*: the register's LOW-8 list survived only in a lost session
  transcript; I probed the archives, ruled it unrecoverable, and the reconstructed set (same
  heuristic, re-applied) stands as authoritative — documented as such.
- A sixth factory-naming tautology (register said five) was found and fixed; the count
  discrepancy was handed to Item 7's recount.

### Item 7 — REQ/matrix reconciliation (F2, F4, the divergent rows)

**What.** Made the verification matrix tell the truth. The two filed divergences:

- **F4** — a whole module (`input_resolver.py`, the "consolidated input resolver"), designed
  and documented as the intended architecture, tested by a 12-test parity suite, and **never
  wired into production** (zero callers). Three evidence probes were run to decide land-vs-
  delete: (i) parity extended over the new plant fixtures — 100% agreement; (ii) its
  Strategy-D dedup simulated against the baselines — zero key churn; (iii) drift analysis —
  the live path is byte-identical since the module's birth commit. **Verdict: the code is
  validated, so keep it and finish the wiring — but not in this item.** The probes also
  *discovered* the blocker: the module's entry-point key format diverges from the live
  path's (both formats coexist in the solar_battery baseline), so a naive rewire would
  collapse distinct parameters. The cutover is filed as `[ITEM7-F4-CUTOVER]` with the probe
  evidence; every matrix row and doc now says "validated, not yet wired" — no row claims
  live usage of unwired code.
- **F2** — the output-registry docs claimed alias registration happens "through typed
  lookup" in a later phase; the code registers at construction time with an inline NOTE
  admitting the divergence. Verdict: fix the text to the code (the construction-time dict
  feeds only guarded typed register calls — verified). The phase-ordering test that had been
  *weakened to accommodate* the divergence was restored as a presence assertion — and proven
  to bite: the named mutation (swap the registration phases) turns it red.

Plus: every divergent-PASS row from discovery dispositioned; the 12 UNTESTED rows reduced to
4 (each remaining one carries its argument); missing test-markers added; the 5 xfails
re-framed as documented contract (the classifier fix filed separately); and a leashed
deep-read sweep over the ~175 never-read PASS rows (stopping rule honored; ~46 rows of
residue named and filed, not silently skipped). Final recount: **253 rows = 249 PASS + 4
UNTESTED-argued + 0 PENDING**, matching the summary block exactly.

**Why it matters.** The matrix is the project's contract with itself — it's what lets a
future session trust that "PASS" means something. Before: the summary lied about its own row
count, an entire REQ family pinned dead code as if it were live, and a weakened test
memorialized a divergence instead of flagging it.

**Judgment calls / gaps.** The land-with-split verdict is the big one (rationale above).
Deferred: `[ITEM7-F4-CUTOVER]` (the actual rewire), `[ITEM7-MATRIX-SWEEP-RESIDUE]` (~46
unswept rows), the xfail classifier fix.

### Item 8 — Dead code & cleanup debt

**What.** One reviewed pass clearing the filed debt: 12 dead symbols deleted (two unused
templates, four zero-caller functions including `get_default_value` and the 7-site
`binding_to_entry_point` dual-write, a dead semantic-match cluster, vacuous test guards) —
each with grep-zero evidence before and after. Fixed one real bug: `_walk_aggregation_ast`
dispatched literals through the invocation catch-all (a literal `+ 5.0` in an aggregation
became `LiteralRationalEvaluation()` garbage and flagged the expression unsupported) — fixed
red-first with a new fixture, now REQ-AST-10, retiring doc-19's "known deviation" note.
Every leftover discovery-register residue item dispositioned (done or properly filed:
`[SC11-IMPORT-REWRITE]`, `[SANITIZER-MERGE]`, `[GB-PARAMGROUPS-TYPING]`).

**Why it matters.** Dead code with live-looking docs is how the F4 situation happens again.
The test-deletion rule mattered here: 11 tests deleted, every one a self-test of a deleted
symbol, named in the ledger.

**Judgment calls / gaps.** `get_default_value`'s deletion orphaned a REQ row — handled by
breadcrumbing the matrix row and handing the re-frame to Item 7 (completed there). The
AST-based import rewrite (SC-11) was assessed honestly as not-small and filed rather than
rushed.

### Item 9 — agentic-mbse sync

**What.** agentic-mbse is the modeling-guidance and validation repo consumers use while
authoring models; it must teach and check the same subset codegen accepts. Landed on the
companion branch: the whole-plant value idiom documented (the four mechanisms, precedence,
source-QN keying, literal-only rule, anchored on the landed fixtures); the long-owed
**expression-RHS warning** built (fires when `attribute :>> attr = <expression>` carries an
expression — the exact shape codegen silently drops); a sweep confirming no other guidance
surface teaches a stale pattern; the two cross-repo primitive audits (reference traversal —
COVERED; direction-string stability — STABLE, nothing filed); and every prior-epic residue
dispositioned (C8 kept filed with reasoning, the syside vendor note declined with reasoning,
F5 verified absorbed). An 18-row traceability table maps every accumulated impact to its
disposition — zero silently dropped.

**Why it matters.** The validated-subset contract is only enforceable if the teaching repo
and the generating repo move in lockstep. The new warning's design is notable: a live probe
found the `attribute` keyword is a perfect discriminator (the unsupported form parses as
`AttributeUsage`, the supported bare form as `ReferenceUsage` — disjoint categories), so the
check **structurally cannot** fire on a supported shape.

**Judgment calls / gaps.** The companion branch stacks Item 4's four commits + Item 9's
three on top of the prior epic's still-open PR #7 — the PR body carries a base-then-retarget
instruction. PR creation itself stays with you (precedent). Two unrelated untracked scratch
files in the agentic-mbse tree predate this epic; glance before opening the PR.

### Item 10 — Docs refresh & epic close

**What.** The docs-scrub-style close: every retired caveat (the 10-offender abort, the
assert-constraint silence, "four specific cross-part shapes", the open F2/F4 divergences,
the doc-19 deviation, the doc-25 hedge, the §8 overclaim) verified gone from every **live**
doc — and deliberately retained in historical documents as the record of what was true then.
`EXPLAINER_PROMPT.md` (the prompt for building the external explainer) rewritten so it
contains no claim contradicted by post-epic HEAD, with an explicit "retired — do NOT present
as open" list and the green acceptance run as its grounding. Spot-check audit (3 docs +
matrix recount from rows) passed. Epic file marked Completed with lessons learned;
CURRENT_WORK and BACKLOG updated.

---

## 4. Cross-cutting: everything deferred or filed (the complete list)

| Filed item | What it is | Why deferred |
|---|---|---|
| `[ITEM7-F4-CUTOVER]` | Wire the validated `input_resolver` into production | EP-key format divergence makes it a real refactor; probe evidence attached |
| `[MULTIHOP-CHAIN-PARSE]` | Parse 3+-segment chain bindings | New capability; currently a loud diagnostic |
| `[ITEM7-MATRIX-SWEEP-RESIDUE]` | ~46 PASS rows not deep-read | Sweep stopping rule; residue named, not hidden |
| `[D3-HYGIENE-TAIL]` | ~20 benign-leaning silent-failure sites | Triaged below the fix line at Item 5 spec |
| `[SC11-IMPORT-REWRITE]` | AST-based import rewriting | Assessed not-small |
| `[SANITIZER-MERGE]` | Consolidate the two name sanitizers | Load-bearing; needs its own pass |
| `[GB-PARAMGROUPS-TYPING]` | Clean fix for two type-ignores | Naive removal raises the mypy count |
| `[DOTTED-LEAF-PART-BLIND]` (P3) | Tighten dotted-leaf alias part-matching | Behavior kept and pinned; tightening optional |
| xfail classifier fix | Inherited-attr classification (5 xfails) | Re-framed as documented contract; misclassification is loud |
| Constraint execution | Execute constraints as boolean modules | Whole epic; needs an ADR. Item 4 made the drop loud in the meantime |
| Expression-RHS resolution | Non-literal override values | Expression-aware epic; loudly skipped today |
| EXPOSE_COMPUTED, non-uniform arrays, supertype-chain template inheritance, conditionals/function calls | Prior-epic deferrals | No new evidence moved them; unchanged |

PUSH-DOWN (the extraction-restructuring epic) is now unblocked per the sequencing ruling —
Items 5 and 8 landed the surfaces it moves.

## 5. Process notes you should know

- **Every item ran spec → adversarial review → (design → review) → plan → implement →
  independent audit.** Every single review round found at least one load-bearing defect
  before implementation (a false metamodel claim, a silently-vacuous exclusion filter, a
  0.0-truthiness silent null, a "restored" assertion that was itself vacuous). Three audits
  triggered cure commits; two found narrative errors in otherwise-correct work.
- **The verify-then-fix protocol (R4) worked as designed**: of the 16 register findings, 3
  were refuted or reclassified by live probes before any fix was written — including one
  the design had already accepted.
- **Concurrency cost**: two sessions committing to one working tree scrambled commit
  attribution in a handful of commits (net tree verified correct; noted in the Item-4
  audit). One external event — a concurrent session finishing the prior epic's agentic-mbse
  work and opening PR #7 mid-run — was absorbed cleanly.
- The full stage-by-stage trail is the commit history on `pipeline-truth-epic`; per-item
  artifacts (spec/design/plan/reviews/audit) live under `.project/active/<item>/`.

## 6. The three actions that are yours

1. **Merge agentic-mbse PR #7** (prior epic's companion; already open).
2. **Create the agentic-mbse companion PR** from branch `pipeline-truth-item4` using
   `.project/active/pipeline-truth-sync/COMPANION_PR_BODY.md` (base it on
   `upstream-findings-sync` while #7 is open; retarget to `main` after it merges).
3. **Open the fusion-tea PR** from `chore/retire-pipeline-truth-workarounds` (local branch
   in `~/1cfe/fusion-tea`; commits `5a889ac5`, `2286e5aa`).

Then review/merge sysml-codegen PR #5, and `/_my_close` archives the epic.
