# Independent Audit — Slice 3A (v6 envelope and source admission)

**Verdict:** FINDINGS
**Audited:** 2026-08-10
**Commits:** `fe0b855` (slice) and `687f748` (OID record), branch `item7-rebuild`
**Auditor:** fresh session, not the implementer. Every claim below was re-derived by reading
code and running commands. No implementer note or commit-message claim was taken on trust.
**Contract:** `.project/active/cutover-recovery/plan.md` — Slice 3A, "Validation for every
Phase 3 slice", Non-Negotiable Execution Rules; stage brief `briefs/phase3a.md`.

---

## The Point

Item 7 replaces the legacy string-resolution front end with one exact instance-graph authority.
Slice 3A is the first vertical increment: a model elaborated live, captured to a v6 snapshot, and
loaded back — in place and relocated — must produce one instance graph and one projected
computation graph, license-free, while v5 stays whole.

The slice carries one extra burden. The earlier Item 7 candidate sealed a free-form
`capture.model_name` and `capture.captured_at` under an unkeyed SHA-256, so a forger who edited the
file recomputed the digest and a re-labelled snapshot loaded clean. The plan pins the closure as a
hard requirement: *"The loader must reject a re-sealed model-identity swap, which the failed
candidate currently accepts."*

## Summary

The engineering is strong and most of the slice is exactly what it claims. v5 is genuinely
untouched, the suite delta is precisely the 104 new tests, every gate re-runs green, the
dispositions are honest against the forensic parts bin, and the envelope matrix is a real,
non-tautological refusal matrix with re-sealing done properly. This is not the failed candidate's
pattern of self-certification.

But the headline claim is overclaimed. `sources.files[].referent` is a free-form declaration under
the same unkeyed digest the old `model_name` sat under, and it is checked only for *syntax*, never
against anything anchored. An adversarial probe against the real loader re-labelled a sealed
snapshot's source referent, re-sealed it the way a forger would, and **it loaded clean**. The
pinned refusal is therefore not achieved, while the plan, the commit message, the module docstring,
and the test-module docstring all state that it is.

That is the one finding that blocks 3B. Two smaller findings follow.

---

## Findings

### F1 — HIGH — A re-sealed model-identity swap is still accepted; the closure claim is false

**Severity:** HIGH. Blocks 3B.

**What is claimed.** Four places assert the hole is closed:

- `plan.md:497` — *"Closed by making the envelope carry no unanchored declaration at all."*
- `plan.md:996-999` — *"There is no unanchored declaration left, so a model-identity swap cannot
  be expressed."*
- `src/sysml_codegen/snapshot/envelope.py:8-13` — *"There is deliberately no free-form
  declaration — no model label, no capture timestamp."*
- `tests/conformance/test_snapshot_v6_envelope.py:12-13` — *"This format carries no unanchored
  declaration at all, so that swap cannot even be expressed."*

**What is true.** The envelope does carry a free-form declaration: `sources.files[].referent`.
`_validate_source_manifest_shape` (`src/sysml_codegen/snapshot/envelope.py:345`) passes each
referent to `validate_source_referent`, which is a purely *syntactic* canonical-form check
(`src/sysml_codegen/extraction/source_manifest.py:484-504`) — it validates percent-encoding and
suffix, never the value. `_validate_sources` (`envelope.py:439-448`) then checks only that every
graph row's `source_file` is *present in* `sources.files`; it never checks the converse, and
nothing anchors the referent to anything outside the document.

**Executed evidence.** Probe `/tmp/claude-audit3a/forge.py` — 14 cases, each editing a genuinely
captured snapshot and re-sealing inner fingerprint, source fingerprint, and outer digest in the
correct order, then calling the public `load_instance_graph_snapshot`. No internals stubbed.

```
00-control-genuine              *** ACCEPTED ***          (expected)
01-toplevel-model-name          REFUSED SnapshotShapeError: unknown keys ['model_name']
02-authority-model-name         REFUSED SnapshotShapeError: unknown keys ['model_name']
03-integrity-captured-at        REFUSED SnapshotShapeError: unknown keys ['captured_at']
04-root-path-smuggle            REFUSED SnapshotShapeError: sources.roots[0] unknown keys ['path']
05-file-origin-smuggle          REFUSED SnapshotShapeError: sources.files[0] unknown keys ['origin']
06-graph-row-smuggle            REFUSED SnapshotShapeError: attribute node unknown keys [...]
07-consistent-referent-rename   *** ACCEPTED ***          <-- the identity swap
08-appended-phantom-source      *** ACCEPTED ***
09-restated-source-bytes        *** ACCEPTED ***
10-appended-phantom-with-roots  REFUSED SnapshotStaleSourceError
11-wholesale-content-swap       *** ACCEPTED ***          (expected — a valid other-model snapshot)
12-future-version               REFUSED SnapshotShapeError: unsupported version 7
13-sources-removed              REFUSED SnapshotShapeError: missing keys ['sources']
14-freshness-genuine            *** ACCEPTED ***          (expected)
```

Three unexpected acceptances, one root cause:

- **Case 07 — the identity swap.** Rename the sealed referent from `root-0/model.sysml` to
  `root-0/customer_proprietary.sysml` in the manifest and in every graph row's `source_file`,
  re-seal, load. Accepted. This is the same *shape* of attack as the old `model_name` re-label:
  edit a self-declared label, recompute the unkeyed digest, load clean.
- **Case 08 — phantom provenance.** Append a fabricated file row (arbitrary referent, size, and
  SHA-256) that no graph row references. Accepted.
- **Case 09 — restated source bytes.** Change a real row's sealed `sha256` and `size_bytes`.
  Accepted.

**Blast radius — it is not confined to metadata.** Probe `/tmp/claude-audit3a/misc_probe.py`
confirms the referent reaches the projected public surface:

```
instance-graph node source_file values: ['root-0/model.sysml']
'root-0/model.sysml' appears in projected ComputationGraph: True
```

So a forged referent propagates false provenance into the `ComputationGraph` that Slice 3B builds
its `PipelineContext` from. That is why this blocks 3B rather than waiting.

**Why the matrix missed it.** The identity cells only test *added* fields
(`test_added_outer_field_is_refused_even_when_resealed:198`,
`test_identity_declaration_cannot_be_smuggled_into_a_nested_block:220`). The single referent test,
`test_source_referent_shape_is_enforced:270`, uses `/absolute/model.sysml` — which fails the
syntactic gate. No test mutates a *syntactically valid* referent to a different value. The matrix
has a hole exactly where the plan pinned the requirement.

**The honest constraint.** No offline check can fix case 07. Verifying that a file really was named
`root-0/model.sysml` means reading that file, which is what `source_roots` does — and case 10 shows
that path works correctly. `envelope.py:28-31` already documents the general limit ("that the
sealed graph really is the elaboration of the sealed sources is not decidable offline"). The defect
is not that a limit exists; it is that four artifacts assert a stronger guarantee than the code
delivers, and the plan's pinned refusal is ticked as met.

**What would resolve it** (owner ruling likely needed, since it amends a plan-pinned requirement):

1. Correct the four overclaims to state the actual guarantee: the envelope admits no *new*
   unanchored field, but `sources` remains a self-declared manifest that is only verifiable when
   `source_roots` is supplied.
2. Add the three missing matrix cells (07, 08, 09) as tests asserting the *documented* behavior,
   so the limit is pinned rather than merely absent.
3. Decide and record whether provenance-critical loads must pass `source_roots`, and whether
   `_validate_sources` should additionally require every sealed source row to be referenced by at
   least one graph row (which closes 08, though not 07 or 09).
4. Re-open `plan.md:497` and the Slice 3A checkbox at line 495 until 1–3 land.

---

### F2 — MEDIUM — Route equality's "live" arm is not an independent route

**Severity:** MEDIUM. Should be resolved before 3B builds on the route-equality guarantee.

`test_live_in_place_and_relocated_routes_have_one_graph`
(`tests/conformance/test_snapshot_v6_routes.py:48-65`) compares three arms. The "live" arm calls
`admit_sources` + `elaborate_admitted_sources` (`:49-50`). `capture_instance_graph_snapshot` calls
**the same two functions** (`src/sysml_codegen/snapshot/capture.py:98-99`). The arms are not
independent, so the test proves seal → encode → decode round-trip fidelity, not that capture and
the live route agree.

**Executed evidence.** `/tmp/claude-audit3a/route_probe.py` injects a defect into
`elaborate_admitted_sources` (corrupting every calc `display_name`) and re-runs the test's own
comparison body:

```
UNPATCHED         three-way agreement: graph=True projection=True   fingerprint 35f023e5c65fdc62
DEFECT INJECTED   three-way agreement: graph=True projection=True   fingerprint ef290b6731042794
```

The fingerprint moves — the graph is demonstrably wrong — and the equality assertion stays green.

The projected-surface comparison itself is sound: `_computation_digest` (`:33-45`) hashes the full
`model_dump`, not a summary, which is what the plan demanded. The self-containment test is also
real — `test_relocated_snapshot_needs_no_source_tree` (`:81-89`) genuinely `shutil.rmtree`s the
model tree, and capture determinism (`test_snapshot_v6_envelope.py:122-134`) compares two real
captures byte for byte.

**What would resolve it.** Give the live arm a genuinely independent path — compare against
`build_elaborated_pipeline` (`src/sysml_codegen/orchestration/elaborated_pipeline.py:29`), which
reaches the elaborator without going through admission, and reconcile the expected `source_file`
difference explicitly. Alternatively, defer the claim to 3B and downgrade this module's docstring
(`test_snapshot_v6_routes.py:1-7`), which currently states the stronger three-route claim.

---

### F3 — LOW — `elaborate_admitted_sources` drops the empty-calc-defs gate its sibling raises

**Severity:** LOW. Fix in 3A or carry as a declared 3B item.

`build_elaborated_pipeline` refuses a model with no calculation definitions
(`src/sysml_codegen/orchestration/elaborated_pipeline.py:43-47`). `elaborate_admitted_sources`, in
the same file (`:78-82`), has no equivalent check, and `require_projectable()` does not catch it.

**Executed evidence** (`/tmp/claude-audit3a/misc_probe.py`, on a fixture with one part def and zero
calc defs):

```
build_elaborated_pipeline        -> CodeGenerationError: No calculation definitions found in models.
elaborate_admitted_sources       -> ACCEPTED (calcs=0)
capture_instance_graph_snapshot  -> WROTE nocalc.json
```

So capture seals a snapshot for a model the live route refuses. This is the "three empty graphs
agreeing with each other" hazard that `test_the_route_carries_real_modelled_content`
(`test_snapshot_v6_routes.py:68-78`) guards against at load time but capture does not guard at seal
time.

**What would resolve it.** Raise the same `CodeGenerationError` in `elaborate_admitted_sources`, or
have `build_envelope` refuse a graph with no calcs, with a test pinning it.

---

## Verified green

Each of these was re-run or re-derived, not accepted from the notes.

**Full licensed suite.** `3462 passed / 47 skipped / 18 deselected`, zero failures, **zero
`no live syside license` lines** — matches the claim exactly. Delta vs the Item 6 baseline
(3358/47/18) is `+104 passed`, with skips and deselections unchanged.

**The +104 is exactly the new tests.** The five new modules run standalone: `104 passed`. Collected
node count 3527 vs baseline 3423 = +104. Collected test-file inventory compared against
`evidence/baseline.json`: **zero of the 218 Item 6 test files removed**, exactly 5 added. (The four
`tests/execution/` files absent from the default run are the 18 deselected nodes; they collect and
pass in the execution lane.) No Item 6 test was removed, silenced, or deselected — plan rule 6
holds.

**v5 untouched.** `git diff --name-status beee0f4 fe0b855` shows no deletion anywhere.
`snapshot/{loader,serializer,graph_rebuild,__init__}.py` are absent from the changed set;
`SNAPSHOT_FORMAT_VERSION = 5` stands; `capture_snapshot` is intact beside the new
`capture_instance_graph_snapshot`. This matters: the forensic candidate *replaced* `capture_snapshot`
with the v6 implementation (`07531e64:src/sysml_codegen/snapshot/capture.py:16`, a 50-line file whose
only entry point is the v6 capture), so the "Reimplement as an addition" disposition and its stated
reason are both factually correct.

**Execution lane.** `pytest tests/execution -m execution` → 18 passed, unchanged.

**Gates.** `ruff check src` → 16 findings, error set **byte-identical** to the parent commit
(`diff` of concise output: no differences). `mypy src` → 71 errors in 17 files; error set
**byte-identical** to the parent commit, the only difference being `checked 82` → `checked 84`
source files, i.e. the two new modules contribute zero errors. Zero new, zero fixed, confirmed by
set comparison rather than by count. (The brief's "72-error baseline" is stale by one; the
parent-commit measurement is the authority and it is clean.) `git diff --check` → clean on both the
working tree and the commit range.

**Changed paths ⊆ declared set.** 12 paths: 2 under `.project/`, 5 under `src/`, 5 under `tests/`.
All fall within the brief's declared scope plus the one relocation
(`snapshot/source_manifest.py` → `extraction/source_manifest.py`) that the plan notes declare in
advance with its reason. No docs, spikes, probes, snapshots, or unrelated tests changed.

**Generated-package smoke, re-run independently.** `sysml-codegen generate --models
tests/fixtures/fusion_tea` produced a sealed **48-file** package. Traced the claimed artifact by
hand: `inputs/hif_driver_params.json` carries `hif_driver__HIF_Driver__efficiency: 0.35`, which is
`:>> efficiency = 0.35;` at `tests/fixtures/fusion_tea/designs/hif_ife/hif_driver.sysml:81`. Both
the file count and the traced value match the notes exactly.

**Dispositions honest, spot-checked against the forensic parts bin** (`07531e64`, read-only):

- `extraction/source_manifest.py` — claimed "Reuse, relocated + 3 edits". Verified: the diff
  against `07531e64:src/sysml_codegen/snapshot/source_manifest.py` is exactly the expanded
  docstring, the `PINNED_SYSIDE_VERSION` constant replacing two literals, `envelope_sources()`
  losing its `capture_options` argument, and both `import syside` statements routed through
  `get_syside()`. 26 added / 12 removed lines. Staging, collision policy, symlink policy, race
  detection, and referent encoding are unchanged. The claim is accurate.
- `snapshot/envelope.py` — claimed "Reimplement". Verified: forensic is 976 lines and carries
  `capture.model_name` / `capture.captured_at` (`07531e64:.../envelope.py:108,110,131-132,285-291`),
  confirming the identity-hole premise is real, not assumed. Delivered is 529 lines with no
  `capture` block.
- **Rejected material did not leak in.** The forensic commit deletes
  `snapshot/{loader,serializer,graph_rebuild}.py` and `orchestration/elaborated_pipeline.py`, and
  rewrites `snapshot/__init__.py` and `orchestration/pipeline_builder.py`. None of those changes
  are present in `fe0b855`.
- Forensic `tests/conformance/test_snapshot_v6_envelope.py` has 6 test functions; the delivered
  module has 22. The "covered about half the cells" note understates the improvement, in the
  conservative direction.

**Envelope matrix — cells the plan pins, each with a real test on public loader behavior.**
Missing/current/future version (`:142-154`, parametrized over `None, 5, 7, "6", 6.0, True`);
missing outer field (`:179-187`); added outer field, re-sealed (`:198-210`); nested identity
smuggle (`:220-227`); wrong-typed outer fields (`:230-256`, 11 cases); graph replacement at three
re-seal depths (`:362-383`); ordinary inner tamper (`:303-310`, `:329-354`); valid inner graph
inside a tampered outer envelope (`:283-300`); source-manifest replacement (`:386-392`);
compatibility (`:400-452`, 10 cases); certifiability (`:460-475`); stale sources
(`test_source_admission_routes.py:66,78`). `_reseal_outer` and `_reseal_graph` (`:47-65`) genuinely
recompute the digests, so no refusal is masked by a stale digest — my independent probe reproduced
the same refusals with my own re-sealing code.

**Test quality — the failed candidate's signature defect is absent.** Expectations are
independently derived, not read back from the code under test: exact percent-encodings
(`test_source_admission.py:84-87`), the closed failure vocabulary spelled out literally (`:270-280`),
exact referent accept/reject lists (`:289-318`). The three `monkeypatch` uses in the envelope module
(`:298, :324, :450`) install a `forbidden_decode` tripwire that *asserts decode is never reached* —
they prove layer ordering rather than disabling the code under test. I found no test asserting a
copy against itself and no tautological assertion. The two Item 6 invariant tests the forensic
candidate deleted (`test_no_direct_syside_imports`, the internal-route isolation test) are present
and passing, and they did catch real violations in this slice — direct evidence for plan rule 6.

---

## What I ran

| Command | Outcome |
|---|---|
| `pytest tests/ -q` (licensed) | 3462 passed / 47 skipped / 18 deselected, 0 failures, 0 license-skip lines |
| `pytest` on the 5 new modules | 104 passed |
| `pytest tests/execution -m execution -q` | 18 passed |
| `pytest tests/ --collect-only` + inventory diff vs `baseline.json` | 0 Item 6 files removed, 5 added |
| `ruff check src` at `fe0b855` and `beee0f4` | 16 findings each; concise output identical |
| `mypy src` at `fe0b855` and `beee0f4` | 71 errors each; error set identical (82 → 84 files checked) |
| `git diff --check`, `git diff beee0f4 fe0b855 --check` | clean |
| `git diff --name-status beee0f4 fe0b855` | 12 paths, no deletions |
| `sysml-codegen generate --models tests/fixtures/fusion_tea` | 48-file sealed package; `0.35` traced to `hif_driver.sysml:81` |
| `/tmp/claude-audit3a/forge.py` | 14 forgery cases; 3 unexpected acceptances (F1) |
| `/tmp/claude-audit3a/route_probe.py` | injected defect invisible to route equality (F2) |
| `/tmp/claude-audit3a/misc_probe.py` | calc-def asymmetry (F3); referent reaches projected graph |
| `git -C /home/reid/1cfe/sysml-codegen show 07531e64:<path>` | disposition spot-checks, read-only |

Environment: venv `/home/reid/1cfe/item7-rebuild-venv`, license via
`/home/reid/1cfe/agentic-mbse/.env`. A temporary detached worktree at `/tmp/claude-audit3a/base`
was used to measure the parent commit's lint/type baselines and was removed with
`git worktree remove --force`. The repository is clean at `687f748`; no tracked file was modified
and no commit was made.

## Not verified

Stated plainly rather than implied green.

- **Real TEAx execution.** Not attempted. Plan Slice 3D work; the v6 route ends at the projected
  `ComputationGraph` and no generated package is produced from a v6 snapshot yet.
- **Package generation from a v6 snapshot.** Does not exist yet — the smoke ran the live route, as
  the notes' scope statement says. The v6 route's end-to-end product value is therefore still
  unproven; 3A proves the snapshot layer only.
- **The 37-path corpus.** Not re-run in this audit. Slice 3A changes no resolver path, but I did
  not confirm that by measurement.
- **agentic-mbse.** Untouched by this slice and not audited. Its rebuild worktree was not inspected.
- **The strictness change to `snapshot/instance_graph.py`.** The exact-key gates are new behavior on
  a module the Item 5/6 elaboration tests share. The full suite is green, which is meaningful
  evidence, but I did not separately hunt for a valid-graph shape that the new exact-key checks now
  reject. Any committed historical instance-graph payload would be worth a targeted check before
  Phase 4.
- **Concurrency and filesystem-race behavior** of `admit_sources` beyond the single-threaded cases
  the unit tests exercise.
- **Whether F1 is acceptable to the owner.** I graded it against the plan's written requirement,
  which it does not meet. Whether the residual offline limit is acceptable once documented honestly
  is an owner decision, not mine.

## Disposition

**FINDINGS.** F1 must be resolved before Slice 3B begins — it is the exact requirement this slice
existed to satisfy, the artifacts assert a guarantee the code does not provide, and the forged
value propagates into the `ComputationGraph` that 3B consumes. F2 should be resolved with it, since
3B will otherwise build on a route-equality guarantee that a probe shows is not load-bearing. F3 is
small and may be carried as a declared 3B item.

Nothing here is a rule-10 premise conflict. The plan's approach is sound and the slice's other work
stands; F1 is a gap between a claim and its code, plus a matrix hole — both fixable inside 3A,
though correcting a plan-pinned requirement is an owner call.

---

# Confirmation Pass — 2026-08-10

**Verdict:** **CERTIFY**, with one named accepted residual (below). Slice 3B may begin.
**Confirmed at:** `6d144bd` (fix commit `4858911`, OID record `74224a6`, orchestrator rulings
`6d144bd`), branch `item7-rebuild`, worktree clean.
**Scope:** focused re-verification of F1/F2/F3 and the gates. Not a fresh audit — the areas listed
under "Not verified" above remain unverified unless restated here.

All three findings are resolved. Each was re-checked by running my own probes against the code at
`4858911`, not by reading the fix commit's claims.

## F1 — RESOLVED as a pinned limit, not a closure

The implementer did the right thing with a finding that had no clean fix: measured whether the
structural check I proposed was sound, found it was not, and shipped the truth instead.

**Re-ran my three forgery probes** (`/tmp/claude-audit3a/confirm_f1.py`), each re-sealing the
sources fingerprint, inner fingerprint, and outer digest in order, against the real loader:

```
07 referent re-label         offline: LOADS (documented limit)   source_roots: REFUSED SnapshotStaleSourceError
08 appended fabricated row   offline: LOADS (documented limit)   source_roots: REFUSED SnapshotStaleSourceError
09 restated sha/size         offline: LOADS (documented limit)   source_roots: REFUSED SnapshotStaleSourceError
```

Behavior is unchanged offline — as intended — and `source_roots` refuses all three. Both halves are
now pinned by tests parametrized over the same three shapes:
`test_a_resealed_relabelling_is_accepted_offline` (`test_snapshot_v6_envelope.py:459`) asserts each
loads *and* yields a usable graph, with a docstring naming it an accepted documented limit;
`test_source_roots_refuse_every_resealed_relabelling` (`:476`) asserts each raises
`SnapshotStaleSourceError`. The matrix now states the truth in both directions rather than implying
closure by omission.

**Spot-checked the converse-check decision independently.** The claim is that requiring every sealed
source to be referenced by some graph row would encode a false invariant, because the elaborator
records a node's *declaration* site. I captured three of the five named fixtures myself
(`/tmp/claude-audit3a/confirm_f3.py` and a direct probe):

```
agg_literal_probe      sealed=[design.sysml, library.sysml]  unreferenced=[design.sysml]
retype_model           sealed=[design.sysml, library.sysml]  unreferenced=[design.sysml]
quoted_owner_formula   sealed=[design.sysml, library.sysml]  unreferenced=[library.sysml]
```

All three carry a sealed source no graph row references, and the direction matches the note in each
case, including `quoted_owner_formula`, where it is the *library* rather than the design. The check
I asked for would reject these legitimate snapshots. Taking the documented-limit branch was correct,
and the measurement is real rather than asserted. It is pinned by
`test_a_sealed_source_need_not_be_referenced_by_any_graph_row` (`:509`), which asserts the exact
sealed and referenced sets for `agg_literal_probe`, and carried as a comment at the one-way check
(`snapshot/envelope.py:459-465`).

**The overclaims are corrected everywhere I found them.** `envelope.py`'s module docstring now
separates the three anchored field kinds from `sources`, names all three re-labelling shapes, and
states that a caller needing provenance must pass `source_roots`. The test-module docstring, the
Slice 3A checkbox (`plan.md`), and the 3A identity paragraph are corrected. `fe0b855`'s commit
message still overclaims; history was not rewritten and the plan records the correction explicitly,
which is the right call.

### The accepted residual, named

**A v6 snapshot loaded without `source_roots` proves structure, not provenance.** A forger who
re-seals correctly can rename the sealed source referents, append a fabricated source row, or restate
a real row's digest, and the snapshot loads as a full usable graph. The forged referent reaches the
projected `ComputationGraph`.

This is not closable offline — every check is a function of bytes the forger controls — and
mandating `source_roots` would break the relocated-snapshot route the cutover exists to deliver.
The orchestrator ruling (`plan.md`, Slice 3A checkbox, `[AGENT]` 2026-08-10) accepts it for the
rebuild and flags it for the Phase 5 owner packet. I concur with the disposition and record it here
so the Phase 5 auditor inherits it as a named residual rather than rediscovering it: **the plan's
originally pinned "must reject a re-sealed model-identity swap" is met for `model_name`/`captured_at`
and is *not* met for source-referent provenance.** That is a genuine narrowing of a plan-pinned
requirement and belongs in front of the owner, which is where it now goes.

## F2 — RESOLVED and verified by re-running the injection

The live arm now runs through `build_elaborated_pipeline`, which does not touch admission. I re-ran
my exact injection (corrupt every calc `display_name` inside `elaborate_admitted_sources`, via a
pytest plugin patching the module attribute so capture's local import picks it up):

```
UNPATCHED          5 passed
DEFECT INJECTED    1 failed, 4 passed
  test_live_in_place_and_relocated_routes_have_one_graph
  test_snapshot_v6_routes.py:160: AssertionError: the live elaborator and the sealed graph disagree
  assert '3312f2f4...' == '8669424899...'
```

The test now fails, on exactly the comparison that was missing before.

**The second comparison is real, not a summary.** `_graph_digest_ignoring_sources`
(`test_snapshot_v6_routes.py:75-88`) decodes the *encoded instance graph*, masks only the
`source_file` field on each row, and hashes the whole `graph` object. That is why it catches
`display_name` — the field projection drops, which is precisely why the projected-surface comparison
alone could not see my defect. The projected comparison `_masked` (`:110-129`) masks named sites
structurally (module `source_file`, entry-point group `name`/`class_name`/`source_file`, and
`param_group`) rather than blanket-masking by key name, so it stays blind to nothing else. Arm
independence is itself asserted by `test_the_live_arm_does_not_share_the_capture_route` (`:203`).

## F3 — RESOLVED; both routes share one gate

Confirmed by running both entry points on a model with no calc defs (`confirm_f3.py`):

```
build_elaborated_pipeline        -> CodeGenerationError: No calculation, constraint, or calculation definition found
capture_instance_graph_snapshot  -> CodeGenerationError: No calculation, constraint, or calculation definition found
```

Both now raise from the single `require_executable_content`
(`orchestration/elaborated_pipeline.py:56`), and the legacy pre-elaboration `calc def` precheck was
**not** copied across — the gate is graph-level emptiness (no calc, no constraint, no calc
definition). I verified the consequence the B37-01 ruling predicted: `agg_literal_probe`, whose only
computation is a modeled aggregation, now passes the exact route and produces
`calcs=1 attrs=3 constraints=0 diagnostics=0`, which is the ledger's amended `graph 1/3/0/0` exactly.
`tests/conformance/test_elaboration_corpus_ledger.py` → 3 passed.

**The ledger edit is honest.** Row 1 is reclassified `expected-collapse` → `expected-fix` with the
reason recorded; the totals move 26/11 → 25/12 and 13 graphs/24 errors → 14/23; a note preserves
what the Item 6 observation read and why the row moved. Critically, it does *not* resolve the
`14/22/1` versus `15/22/0` question by preference — it records that axis as belonging to the
un-re-run Phase-8 batch manifest and leaves it open, which is what `plan.md:316` demanded. The
orchestrator ruling confirming this edit sits inside the B37-01 owner pre-ruling scope
(`6d144bd`) is consistent with the pre-ruling as written (`plan.md:313-316`), which directed
amending the ledger row and left the count re-derivation open.

## Gates at `6d144bd`

| Gate | Result |
|---|---|
| Full licensed suite | **3473 passed / 47 skipped / 18 deselected**, 0 failures, **0** `no live syside license` lines |
| Delta vs `fe0b855` (3462) | **+11**, skips and deselections unchanged |
| Delta accounted for | envelope 60→67 (+7: 3 offline-accept, 3 `source_roots`-refuse, 1 converse), routes 3→5 (+2), capture 4→6 (+2) = **+11 exactly** |
| Delta vs Item 6 baseline (3358) | +115, all new tests; no Item 6 test removed, silenced, or deselected |
| `ruff check src` | 16 findings, concise output **byte-identical** to the parent-commit baseline |
| `mypy src` | 71 errors in 17 files; error set **identical** to baseline (82 → 84 files checked; the new module adds zero) |
| `git diff --check` | clean |
| Changed paths of `4858911` | 9, all inside the follow-up's declared set in the plan, including the mid-slice declaration of the ledger path |
| Worktree | clean at `6d144bd`; I modified no tracked file but this one and made no commit |

## The 3B blocker the fix uncovered

Making the route arms independent surfaced a real product defect, and the implementer pinned it
rather than normalising it away. `_group_identity` (`src/sysml_codegen/elaboration/project.py:164`)
names each entry-point group after the source path; on the v6 route that path is the staging
referent, so `root-0/model.sysml` yields group name `root_0_params` and class `Root0Params`. I read
the function and confirmed the derivation: `path.stem` is `model`, so it falls through to
`path.parent.name` = `root-0` → `sanitize_name(...).lower()` = `root_0`. A package generated from a
v6 snapshot would ship `inputs/root_0_params.json` and a `Root0Params` schema class instead of names
taken from the model.

`test_the_two_routes_diverge_only_on_source_derived_naming`
(`tests/conformance/test_snapshot_v6_routes.py:172`) encodes this honestly: it asserts the v6 side
by value (`{"root_0_params"}`, `{"Root0Params"}`) and the live side by value
(`{"source_identity_mixed_consumers_params"}`, `{"SourceIdentityMixedConsumersParams"}`), so the
test states current behavior and will fail the day it changes. It does not assert the v6 names are
*correct* — the docstring says plainly that this is a defect Slice 3B must resolve before the public
authority switch. That is the right shape for a pin: 3B can consume it, and it cannot be mistaken
for a passing guarantee. Confirmed green (1 passed) and confirmed recorded in `plan.md` with 3B
named as owner.

## Still not verified

The confirmation pass did not widen scope. Everything under "Not verified" above still stands —
real TEAx, package generation from a v6 snapshot, the 37-path corpus end to end, agentic-mbse, the
`instance_graph.py` strictness change against historical payloads, and concurrency behavior in
`admit_sources`. Additionally not verified in this pass: the two unmeasured members of the
five-fixture converse-check set (`d38_caret`, `sample_model`) — I spot-checked three of five and all
three held.

## Disposition

**CERTIFY.** All three findings are resolved with executed evidence, the gates are green and the
suite delta is fully accounted for, and the artifacts now state what the code actually does. The
accepted residual — a v6 snapshot loaded without `source_roots` proves structure, not provenance —
is named above and carried to the Phase 5 owner packet. Slice 3B may begin, and inherits the
`_group_identity` staging-referent defect as pinned work.
