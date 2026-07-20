# Design: TEAx Constraint Evidence Durability (Lifecycle Item 11)

**Status:** Draft (carries the phased plan — no separate plan.md)
**Owner:** Reid W
**Created:** 2026-07-20
**Spec:** `.project/active/constraint-lifecycle-evidence-durability/spec.md`
**Targets:** TEAx `07eb0ac`+ (all code changes are TEAx-side); generated fixtures from codegen
**Contract rows settled:** 41, 45, 46, 46a, 51

---

## Frame

One evaluation turns a generated package's constraint outputs into study evidence. The path is:

```
executor.run() ─► project(result, report) ─► ModelEvidence ─► policy.assess() ─► encode_evidence() ─► store.commit_case() ─► StudyQuery
   (evaluator)        (projection seam)         (envelope)        (runner)          (runner)              (store)          (harvest)
```

Four things are wrong on this path (spec Problem). The design settles each against the actual code,
then folds the fixtures and the phasing in. The unifying move: **the projection seam is the single
place where absence is handled and immutability is sealed** — so both evaluator routes converge there
and the authoritative copy is immutable by construction, before anything downstream can touch it.

## Load-bearing assumptions

These are the premises the design rests on. If one is false, the named decision changes. Verify the
codegen-behavior ones (A3, A4) when the fixtures are actually generated — RED-first.

- **A1 — No *production* consumer needs typed access to `evidence.report`.** Grep at `07eb0ac`:
  the only `src/` readers are `projection.py:28-29` (duck-typed `report.headline`/`report.results`)
  and `evidence_io.py:49` (`report.model_dump(mode="json")`). Nothing does typed field access. → We
  may seal `report` into an immutable snapshot without losing a production capability. **The tests are
  a consumer too** — six sites build/assert typed reports and break under the type change; they are
  inventoried and migrated (M1, see D2), not silently in scope. *If false for production:* isolation
  must keep a typed façade.
- **A2 — `report.model_dump(mode="json")` is the exact persisted report today.** `evidence_io.py:49`.
  Sealing at project must reproduce identical bytes, so the persisted "exact report" (contract 46) is
  unchanged.
- **A3 — An excluded-only package emits a report whose headline is `not_assessed`.** The runtime
  vocabulary already carries `not_assessed` (`evidence.py:16`, `CANONICAL_HEADLINE` `:20–27`), so TEAx
  can *carry* it; whether codegen *emits* it for an all-excluded package is a codegen-behavior
  assumption the excluded-only fixture must prove. *If false:* the fixture plan gains a codegen ask.
- **A4 — A constraint-free package emits NO `constraint_report` channel** (not an empty report).
  Contract 46a licenses codegen to "omit constraint-only catalog/modules" → no aggregator module → no
  channel. The constraint-free fixture must prove the channel is genuinely absent (that is what makes
  the read `KeyError`, not an empty-report shape). *If false:* absence detection moves inside the
  report, not at the channel read.
- **A5 — The write phase is positively identifiable at the executor seam.** The write phase
  (`pipeline_executor.py:154-161`) runs after the module loop and can be bracketed by an explicit
  `context.in_output_write` flag. The stamp reads *only* this flag — **not** the exception type
  (`write_outputs` leaves `OSError` unwrapped) and **not** `failed_module_key is None` (entry-load and
  pre-loop write-handler failures also carry a null key). The converse "null key ⟹ write phase" is
  false and is not relied on (design-review C1). *If false:* OUTPUT_WRITE collapses instead.

---

## D1 — Absence semantics: one mechanism at the projection seam

**Decision.** Move report extraction *into* `project(...)`. Both evaluators pass the raw `result` and
stop reading the channel themselves; `project` does the single tolerant read and, when the channel is
absent, produces **empty constraint evidence** (empty `responses`, `report=None`, real `outputs`).

**Code today.**
- `evaluator.py:132` and `:203` each do `report = result.outputs[REPORT_CHANNEL]` then
  `project(result, report, provenance=...)`. Two copies of the same bare read.
- `projection.py:28–29` then reads `report.headline` and `report.results` unconditionally.

**Change.**
- `project(result, *, provenance, expects_report: bool)` (drop the `report` param; add the
  corruption-vs-emptiness authority — M3). Inside: `report = result.outputs.get(REPORT_CHANNEL)`
  (move `REPORT_CHANNEL` to `projection.py`, or import it).
  - `report is not None` → today's behavior (headline + per-constraint responses), then seal (D2).
  - `report is None and not expects_report` → `responses = {}`, `report_out = None`, `outputs` built
    as today from scalar channels (`projection.py:32-36`). Constraint-free empty-evidence shape.
  - `report is None and expects_report` → **raise `CorruptConstraintEvidence`** (M3, below). Loud,
    never a silent `unconstrained` case.
- `evaluator.py:132` and `:203` both collapse to `return project(result, provenance=provenance,
  expects_report=self._expects_report)`. One read seam, not two.

**M3 — corruption vs emptiness (the catalog is the authority).** An absent report channel is
*expected* for a constraint-free package and *corruption* for a constraint-bearing one whose channel
vanished. The authority is codegen's embedded catalog, read through the single Item-8 seam
`load_model_contract(package_dir).concrete_entries` — **empty ⟺ constraint-free** (the seam's own
docstring guarantees "empty on a constraint-free package"). Wiring, keeping `evaluation/`
isolation-clean (it must never import `study/`):
- The **study-layer caller** (`study/cli.py:_prepared_evaluator`, and the study test harness) reads
  the catalog and passes `expects_constraint_report=bool(concrete_entries)` into the evaluator
  constructor. The evaluator stores it and forwards it to `project`. The evaluator receives a plain
  bool — it never imports `study.model_contract`.
- **Evaluation-layer default:** when no caller supplies it, the evaluator derives `expects_report`
  from the pipeline spec (the exit module declares a `constraint_report` output field), so
  evaluation-layer unit tests stay self-contained. **The flag only governs the *absent*-channel
  branch** — it is never read when the channel is present. So the excluded-only case, where the spec
  declares the channel (spec-derived True) but the catalog's `concrete_entries` is empty
  (catalog-derived False), is not a conflict: the channel is present, `not_assessed` flows, and the
  flag is moot. Corruption is only the *absent-channel + catalog-declares-constraints* combination.
- `CorruptConstraintEvidence(RuntimeError)` is a **plain exception, not `EvaluationFailed`** — it
  propagates past the runner's `except EvaluationFailed` (`runner.py:101`) and crashes the run loudly,
  rather than being recorded as a routine `execution_failed` case. Contrast: excluded-only produces a
  *present* channel (A3, `not_assessed` headline), so it never reaches this branch.

Coordinate: a corruption fixture — a constraint-bearing package (non-empty catalog) with the report
channel forced absent — asserts the loud raise, proving a vanished channel cannot commit as a healthy
`unconstrained` case.

**Downstream join — policy must tolerate empty responses.** Policy reads `evidence.responses["headline"]`
unconditionally (`policy.py:65`; `ObjectivePolicy` `:121`) → that would move the `KeyError` from the
evaluator to the policy. So `DispositionPolicy.assess` and `ObjectivePolicy.assess` gain an explicit
branch: `if "headline" not in evidence.responses:` → an **`unconstrained`** disposition (a new
demo-policy disposition, distinct from `not_assessed`). **Placement (m1):** in `ObjectivePolicy` this
branch must sit **before** the objective / response-role loops (`policy.py:106-119`), which read
`evidence.outputs`/`responses` and raise `AssessmentFailed` before the headline line — otherwise a
constraint-free package under a policy configuring any `response_role` yields `assessment_failed`, not
`unconstrained`. Pinned by a test with a configured `response_role`. This keeps constraint-free (empty)
and excluded-only (`not_assessed`) as **structurally distinct** surfaces:

| axis | `responses` | `report` | disposition |
|---|---|---|---|
| constraint-free (zero usage) | `{}` | `None` | `unconstrained` |
| excluded-only (zero eligible) | `{"headline": "not_assessed", …}` | real report | `not_assessed` |

**Rejected.** Patching both bare reads in place (two `try/except KeyError` or two `.get`) — leaves two
copies of the mechanism to drift and does not fix the projection's own unconditional reads. Rejected:
the seam is `project`, which both routes already funnel through.

**Rejected.** Giving empty evidence a `not_assessed` headline to reuse the existing policy branch —
collapses the two axes the spec requires be distinct (SC row 2). Rejected.

---

## D2 — Immutability: defensive isolation at attach; the seal precedes policy by construction

**Decision.** TEAx seals evidence into an immutable form **at the projection seam**, by defensive
isolation — **not** by freezing codegen's report type. `ModelEvidence` holds a deep-frozen snapshot of
the report (the exact `model_dump(mode="json")` tree, made read-only) and read-only `responses`/
`outputs` mappings. The live generated report object is dropped after the snapshot is taken. Because
the envelope is immutable the moment it is projected, policy — which runs later in the runner — has no
mutable authoritative state to corrupt. The "seal before policy" property holds by construction.

**Why not freeze at the codegen template level.** Three reasons, each grounded:
1. **Out of scope / firewalled.** The spec Non-Goal is explicit: do not force codegen to freeze its
   report models; the fix is TEAx-side.
2. **Insufficient even if done.** The generated report is `ConstraintReport(BaseModel)` with
   `results: list[ConstraintEvaluation]` (`f1_arithmetic/.../schemas/constraint_types.py:13,23`).
   `ConfigDict(frozen=True)` blocks field *reassignment* but **not** `report.results.append(...)` or
   `report.results[0] = ...` — the list container stays mutable. So codegen-freeze is not airtight.
3. **Cross-repo byte churn.** It touches every generated package's `schemas/constraint_types.py`,
   moving byte-identity for all fixtures, for a weaker guarantee.

**Why defensive isolation is airtight here.** After A1, nothing needs the typed report. So project
computes `report.model_dump(mode="json")` once and stores it as a recursively read-only structure.
There is then **no mutable object reachable from `ModelEvidence`**: `responses`/`outputs` are read-only
mappings, `report` is a frozen tree. Every mutation attempt the spec names raises:
- `evidence.report.results[0].status = "satisfied"` → the frozen tree has no `.results` attribute /
  no item assignment → `TypeError`.
- `evidence.responses["headline"] = "violated"` / `evidence.outputs[k] = v` → read-only mapping →
  `TypeError`.
- `evidence.report = ...` / `evidence.responses = ...` → `StrictBaseModel` frozen (`schema.py:63`) →
  `ValidationError`.

**Mechanism detail — committed resolution (M2).** Store the frozen tree **and** widen the walkers.
The proxy-at-access alternative is dropped (it returns a mutable stored container → does not freeze).
- A `_freeze(value)` helper in `evidence.py` recursively converts dict→`MappingProxyType` and
  list→`tuple`. `EvidenceProvenance` is already a frozen `StrictBaseModel`.
- `project` computes `report.model_dump(mode="json")` **once**, `_freeze`s it, and stores it as
  `ModelEvidence.report`. The live generated model is dropped after the dump. `ModelEvidence.report`
  type changes from `Any` to the frozen tree (`Mapping[str, Any] | None`). `responses`/`outputs` gain
  a validator that `_freeze`s them (read-only mapping).
- **`encode_evidence` (`evidence_io.py:35-51`) drops its own `model_dump`:** today `:49` calls
  `evidence.report.model_dump(mode="json")`; now `evidence.report` **is** the (frozen) tree, so encode
  walks it directly. **Widen the three walkers** — `_tag_nonfinite` (`:20-32`), `_untag_nonfinite`
  (`:54-61`), and the `encode_evidence` payload build (`:45-51`) — to recurse `Mapping`/`Sequence`
  (accept `MappingProxyType`/`tuple`, emit plain `dict`/`list` for JSON). This is what makes the frozen
  report subtree walkable so (a) non-finite floats inside `report.results` still get tagged (INV-G
  byte-identity) and (b) the MF-3 poison-collision guard still fires inside the report.
- **Byte-identity holds (A2):** the same `model_dump(mode="json")` output flows through the same
  tagging, whether done at project time (new) or encode time (old). Pinned by the INV-G golden.
- **Both properties are proven, not asserted:** a nested-mutation attack test (INV-C) *and* a
  byte-identity round-trip (INV-G), *and* the migrated MF-3 poison test still raising.

**Test migration inventory (M1 — A1's sweep re-scoped to include tests).** D2's `report` type change
(`Any` live model → frozen JSON tree) breaks six sites; each migrates in Phase 2. A broad
`report=` / `.report` grep runs alongside to catch any not listed:
- `tests/evaluation/test_projection.py:99` — `assert evidence.report is report` (identity). → assert
  by value: `evidence.report == <frozen tree of report>`. Intent (report attached faithfully) kept.
- `tests/evaluation/test_isolation.py:61` — `report=object()` in the INV1 opacity script. → a plain
  report-shaped dict (or `None`); the INV1 pin (evaluation imports no generated class) is *re-expressed*
  as "a plain dict tree, still no generated symbol," which is now the actual contract.
- `tests/study/test_policy.py:37` — `_StubReport(BaseModel)`. → `report={"stub": True}` (policy never
  reads report).
- `tests/study/test_evidence_io.py:55` — `_TypedReport(observed=…)`. → `report={"observed": {"y": v}}`
  (a plain dict tree holding real non-finite floats — the post-`model_dump` sealed shape).
- `tests/study/test_evidence_io.py:83` — `_PoisonedReport(weird=…)` (MF-3). →
  `report={"weird": {"__nonfinite__": "nan"}}`; the guard must still raise walking the sealed tree.
- `tests/study/conftest.py:213` — `report=ConstraintReport(…)`. → the equivalent dict tree
  (`{"catalog_fingerprint": …, "assessed_count": 0, "headline": "not_assessed", "results": []}`).

**The encode-before-assess ordering stops being a mechanism.** Today `runner.py:134` runs
`encode_evidence` *before* `policy.assess` (`:136`) — the incidental protection. Once D2 makes the
envelope immutable, that ordering protects nothing: policy cannot mutate the sealed evidence whatever
the order. So the coupling is removed (see Deletion inventory) and `encode_evidence` moves to its
natural place, just before `store.commit_case`. "Policy gets access only after the authoritative copy
is sealed" is then satisfied by the envelope being immutable from birth, not by call order.

**Rejected.** A per-instance runtime freeze of the live pydantic report (`object.__setattr__`
trickery) — fragile, still leaves list containers mutable, and couples TEAx to pydantic internals.
Rejected in favor of the JSON-tree snapshot.

---

## D3 — OUTPUT_WRITE: emit honestly

**Decision.** **Emit** `OUTPUT_WRITE`, driven by a **positive write-phase signal set at the executor
seam** — never inferred from exception type or a null module key (design-review C1). The condition:
a failure raised while the executor is inside the output-write phase, marked by an explicit flag.

**Why the positive signal (C1).** The tempting discriminators are both unsound:
- `failed_module_key is None` is **not** exclusive to the write phase. Only `_execute_module` is
  wrapped by the try that sets `failed_module_key` (`pipeline_executor.py:142-146`). `_execute_entry`
  (`:131`) and the pre-loop write-handler check `_ensure_exit_handlers` (`:125`, raises
  `OutputRouterError`) are **not** wrapped — an entry-load failure on the file-backed route (malformed
  entry JSON, missing artifact) leaves `failed_module_key is None` and would be misstamped
  `OUTPUT_WRITE`. That reintroduces the exact "phase name that lies" defect Item 11 exists to remove.
- `isinstance(error, OutputRouterError)` can't stand alone either: `write_outputs` calls
  `base_dir.mkdir(...)` (`output_router.py:240`) and `handler.fn(...)` (`:119`) with **no** `OSError`
  wrapping, so the unwritable-`output_dir` failure is a bare `OSError`, not `OutputRouterError`.

**Change (positive signal).**
- Executor: wrap the write phase (`pipeline_executor.py:154-161`) with a context flag —
  `context.in_output_write = True` immediately before `write_outputs(...)`, reset to `False` in a
  `finally`. The flag is `True` only while genuinely inside output write.
- `_normalize_run_failure` (`evaluator.py:56-66`): `phase = OUTPUT_WRITE if
  context.in_output_write else MODULE_EXECUTION`. `module_or_channel` stays `failed_module_key`
  (None on a write failure — honest: no module failed). No exception-type or null-key inference.
- Only `FileBackedEvaluator` persists (`persist_outputs=True`, `evaluator.py:199`); `PreparedEvaluator`
  uses `persist_outputs=False` (`evaluator.py:129`) and never enters the write phase — so OUTPUT_WRITE
  stays file-backed-only, matching the runner comment (`runner.py:119`).
- The runner already routes it: `_commit_execution_failure`'s `else` branch (`runner.py:119-124`)
  commits an `execution_failed` case for both MODULE_EXECUTION and OUTPUT_WRITE — no runner change.

**Why emit, not collapse.** Item 6's F1 record flagged `OUTPUT_WRITE` (`failure.py:23`) as
defined-never-emitted — a lie in the taxonomy. The write phase is real and, with the positive signal,
honestly identifiable. Collapsing would lose the honest phase name for a failure that genuinely
happens during output write.

**Fixtures (two, to pin both directions).**
- OUTPUT_WRITE coordinate: FileBacked with an unwritable `output_dir` → `write_outputs` raises bare
  `OSError` inside the flagged phase → stamped `OUTPUT_WRITE`. Test asserts committed
  `failure_json.phase == "output_write"`, `module_or_channel is None`.
- **Non-over-emission coordinate (m3):** an **entry-load failure on the file-backed route** (malformed
  entry JSON) → failure occurs with `in_output_write is False` → stamped its true phase
  (`MODULE_EXECUTION`), never `OUTPUT_WRITE`. This is the test that would have caught the C1
  misclassification.

**Rejected.** Collapse the phase (shrink to three). Rejected — the condition is real and reachable on
the shipped file-backed route.

---

## D4 — Four-status persistence/harvest, fixture-pinned phases

**Decision.** Prove an exact-report round-trip — evaluate → seal → persist → harvest — for each of the
four evidence-bearing statuses, each carrying package identity, and pin the expected failure phase
from the fixture, never from evaluator agreement.

**The four statuses and where they live.**
- `satisfied` / `violated` / `indeterminate` — three report headlines; all commit as `state="completed"`
  (`runner.py:149–153`) with the headline inside `evidence.responses["headline"]` and the per-constraint
  statuses under their `constraint_id` keys (`projection.py:28–30`).
- `assessment_failed` — a policy outcome that **preserves** evidence: `state="assessment_failed"`,
  `evidence_json=<real evidence>`, `assessment_json={"failure": ...}` (`runner.py:137–147`). Contract 51.

**Round-trip + identity.** Each status: `encode_evidence` → `store.commit_case` → `artifacts/{digest}.json`
→ `StudyQuery.cases()`. Assert the harvested report JSON equals the evaluated report exactly, and that
`executable_fingerprint` is present and consistent (`provenance.executable_fingerprint`, persisted in
the artifact `evidence_io.py:48` and bound in the store `compatibility` table `store.py:43`). Results
are never merged across fingerprints (`query.py:9`, INV-5) — a two-fingerprint control asserts the
harvest keeps them separate.

**Fixture-pinned phases.** The prepared/file-backed parity (contract 45) must equal a *fixed*
expectation, not just "the two routes agreed." Extend the arithmetic-shape fixture cases with an
`expected_phase` (and `expected_module`) field; the parity test asserts *both* routes normalize to the
pinned phase for that shape — so a shape that should fail in MODULE_EXECUTION is pinned to
MODULE_EXECUTION, and the write-failure coordinate is pinned to OUTPUT_WRITE. Two evaluators agreeing
on the wrong phase can no longer pass.

**Rejected.** Establishing phase truth by asserting `prepared.phase == filebacked.phase` alone — the
spec and brief forbid it (evaluator agreement is not truth). Rejected: the fixture is the oracle.

---

## D5 — Fixture plan

Generated-package fixtures are epic-sanctioned and come from codegen (`generate_fixture.py` pattern,
as `f1_arithmetic` was built). Grounded against the `07eb0ac` fixture tree.

1. **`constraint_free` — AUTHOR.** A codegen package with a real calc/output pipeline and **no
   constraints**, so no `constraint_report` channel and a **valid EntryPoint** (Item 9's zero-entry
   template fix makes the EntryPoint valid even with the minimal shape). Proves coordinate one:
   - RED first: `PreparedEvaluator.evaluate(...)` and `FileBackedEvaluator.evaluate(...)` raise
     `KeyError: 'constraint_report'` against the *pre-fix* evaluator (this is the 46a reproduction the
     spec's provenance note says is still owed — do it here).
   - GREEN: both routes return empty evidence (`responses == {}`, `report is None`, real `outputs`);
     the study runner commits a `completed` case with an `unconstrained` disposition.
   - Verifies A4 (channel genuinely absent).
2. **`excluded_only` — AUTHOR.** A codegen package whose constraints are all excluded (zero eligible)
   → report headline `not_assessed`. Proves the exact `not_assessed` surface, distinct from
   constraint-free. Verifies A3 (codegen emits the `not_assessed` headline); if A3 is false, this
   fixture surfaces a codegen ask before the TEAx work can claim SC row 2.
3. **`f1_arithmetic` — EXTEND (exists).** Already carries satisfied (`safe_satisfied.json`), violated
   (`safe_violated.json`), indeterminate (`nonfinite_indeterminate.json`), and the arithmetic-failure
   shapes (`division_by_zero`, `exponent_overflow`, `nested_division`, `zero_negative_power`). Add:
   - `expected_phase`/`expected_module` pins per failure case (D4).
   - An **`assessment_failed` coordinate**: drive it through the existing policy seam
     (`DispositionPolicy(reject_candidate_ids={...})`, `policy.py:59–66`) on a `safe_satisfied` case,
     so evidence is real and preserved. No new fixture package needed — a policy-config coordinate.
   - An **`OUTPUT_WRITE` coordinate**: FileBacked with an unwritable `output_dir` (D3).
   - An **entry-failure-on-file-backed coordinate (m3)**: malformed entry JSON on the file-backed
     route, pinned to `MODULE_EXECUTION` (`in_output_write is False`) — proves OUTPUT_WRITE is not
     *over*-emitted (would have caught C1).
4. **`corrupt_dropped_report` — AUTHOR (M3).** A constraint-bearing package (non-empty catalog) with
   its `constraint_report` channel forced absent → asserts the loud `CorruptConstraintEvidence` raise,
   proving a vanished channel does not commit as a healthy `unconstrained` case.

No fixture reintroduces a standalone catalog/report schema (contract 48 / D-3); the harvest reads
codegen's embedded catalog via `StudyQuery`/`_EmbeddedCatalog` (`query.py:60–84`).

---

## D6 — Deletion inventory (file:line)

Removed once the explicit mechanism (D1 seam + D2 isolation) owns durability:

- **One of the two unconditional report reads.** `evaluator.py:132` and `evaluator.py:203` both delete
  their bare `result.outputs[REPORT_CHANNEL]`; the read lives once inside `project` (D1). Net: two
  identical bare reads → one tolerant read.
- **The projection's unconditional report reads become conditional.** `projection.py:28–29` no longer
  assume a report; the `report is None` branch is the constraint-free path (not a deletion, a guard —
  listed so review sees the read is no longer unconditional).
- **The incidental encode-before-policy protection (m2 — a rationale deletion, not just a move).** The
  load-bearing deletion is the *protection rationale*, not the call site. `runner.py:134`'s
  `encode_evidence` currently serves both commit sites (`:138` assessment_failed, `:149` completed);
  after D2 the envelope is immutable, so "encode early to protect the persisted copy" is deleted as a
  reason. `encode_evidence` may sit anywhere before `commit_case`. **Crash-safety is not weakened:** the
  atomic durability seam is `store.commit_case(..., crash=self.crash)` (`store.py:374`), untouched by
  the reorder — stated explicitly because the epic names crash-safe persistence as a rows-13–15 concern.
- **`EvaluationPhase.OUTPUT_WRITE` is NOT deleted** — D3 emits it, so the phase stays and gains its
  first real emitter. (Recorded here to close the spec's "collapse candidate": decision is emit.)
- **No literal report `Adapter` exists to delete.** Confirmed: the only `*adapter*` in `simkit/` is
  `io/readers.py` ("Input adapters", unrelated). The epic's "generic/duplicate report adapter" is the
  duplicated bare-read + duck-typed projection pair, addressed by the D1 collapse. The design
  introduces **no** consumer-side report reshaper — the harvest continues to read codegen's embedded
  catalog directly (contract 46/48).

---

## Required invariants (what the tests pin)

- **INV-A (absence).** No `constraint_report` channel ⇒ empty evidence, no `KeyError`, on **both**
  routes. Pinned by the `constraint_free` fixture, RED-then-GREEN.
- **INV-B (distinct axes).** constraint-free empty evidence and excluded-only `not_assessed` are
  structurally different surfaces (table in D1). Pinned by `constraint_free` vs `excluded_only`.
- **INV-C (immutability).** Every named mutation attempt on `evidence` (report chain, responses,
  outputs) raises, and neither the authoritative in-memory evidence nor the persisted artifact changes.
  Pinned by a mutation-attempt test across the report tree and both mappings.
- **INV-D (seal precedes policy).** Policy runs against already-immutable evidence; reordering
  encode/assess cannot change the persisted bytes. Pinned by a test that mutates inside a policy and
  asserts the harvested artifact is unchanged.
- **INV-E (exact round-trip + identity).** For satisfied/violated/indeterminate/assessment_failed, the
  harvested report JSON equals the evaluated report and carries `executable_fingerprint`; never merged
  across fingerprints. Pinned by the four-status round-trip + a two-fingerprint control.
- **INV-F (pinned phase).** Parity uses fixture-pinned `expected_phase`, not evaluator agreement;
  OUTPUT_WRITE is emitted on a real write failure. Pinned by the extended `f1_arithmetic` cases and the
  OUTPUT_WRITE coordinate.
- **INV-G (byte-stable encode).** `encode_evidence` output is byte-identical before/after the D2
  snapshot change for a report-bearing case (A2), and the MF-3 poison guard still fires inside the
  sealed report. Pinned by an encode golden test + the migrated MF-3 test.
- **INV-H (corruption ≠ emptiness).** A constraint-bearing package (non-empty catalog) with an absent
  report channel raises `CorruptConstraintEvidence` loudly; only a zero-catalog package maps absence to
  empty evidence. Pinned by the `corrupt_dropped_report` coordinate.
- **INV-I (OUTPUT_WRITE not over-emitted).** An entry-load failure on the file-backed route stamps
  `MODULE_EXECUTION`, never `OUTPUT_WRITE` (the positive-signal guard, C1). Pinned by the
  entry-failure-on-file-backed coordinate.

---

## Phased plan

Ordering is RED-first and bottom-up: prove the crash, fix the seam, seal immutability, then the
statuses and deletions. Each phase is independently testable; anchor movement in a report-bearing
encode (INV-G) is a STOP.

- **Phase 0 — RED coordinate one.** Author the `constraint_free` fixture (codegen). Reproduce
  `KeyError: 'constraint_report'` on both routes against the current evaluator. This is the
  reproduction the spec's provenance note says is still owed. Commit the fixture + the RED evidence.
- **Phase 1 — Absence seam + corruption authority (D1, M3).** Move the read into `project`; collapse
  `evaluator.py:132`/`:203`; add `expects_report` (spec-derived default in the evaluator, catalog
  authority passed from `study/cli.py` + the study harness); add the three branches (present /
  absent+not-expected → empty / absent+expected → `CorruptConstraintEvidence`); add the policy
  `unconstrained` branch (m1 placement). GREEN on `constraint_free` both routes; corruption raises.
  INV-A, INV-H.
- **Phase 2 — Immutability + test migration (D2, M1, M2).** `_freeze` snapshot at project;
  `ModelEvidence.report` becomes the sealed frozen tree; read-only `responses`/`outputs`; widen the
  three encode/decode walkers to `Mapping`/`Sequence`; `encode_evidence` drops its own `model_dump`.
  Migrate the six M1 test sites (+ broad grep). Remove the encode-before-assess *rationale* (m2).
  INV-C, INV-D, INV-G (nested-mutation attack + byte-identity golden + MF-3 both proven).
- **Phase 3 — OUTPUT_WRITE positive signal (D3, C1).** Add `context.in_output_write` around the
  executor write phase; branch `_normalize_run_failure` on the flag only; add the unwritable-`output_dir`
  coordinate AND the entry-failure-on-file-backed coordinate (non-over-emission). INV-F (phase half),
  INV-I.
- **Phase 4 — Four-status round-trip + phase pins (D4, D5).** `excluded_only` fixture (INV-B); extend
  `f1_arithmetic` with `expected_phase` and the `assessment_failed` coordinate; the exact round-trip +
  two-fingerprint control. INV-E, INV-F.
- **Phase 5 — Deletion sweep + evidence (D6).** Confirm the deletions landed and nothing reintroduced;
  full teax suite green; ruff/mypy no-new; write `evidence.md`.

**Gates.** Full teax simkit suite green in the exec env (auto-memory `teax-simkit-execution-env`:
agentic-mbse venv + `sys.path` insert, not teax `.venv`); ruff clean; mypy no-new; `encode_evidence`
byte-stable on report-bearing cases. Nothing pushed (Item 13 owns the push).

---

## Open / deferred

- **Constraint-free disposition label.** `unconstrained` is proposed for the demo `DispositionPolicy`;
  the exact label is a small policy naming call, not a contract term. It must stay *distinct* from
  `not_assessed` (that constraint is settled; the spelling is open).
- **Sealed-tree representation — SETTLED (M2).** Frozen tree stored (`MappingProxyType`/`tuple`) +
  three walkers widened to `Mapping`/`Sequence`. The proxy-at-access alternative is dropped (it does
  not freeze). No longer open; pinned by INV-C + INV-G.
- **Item 12 boundary.** Legacy `grandfathered_off` / `tracking_key` (contract 53) stays out — Item 12.

---

## Related artifacts

- **Spec:** `.project/active/constraint-lifecycle-evidence-durability/spec.md`
- **Contract:** `.project/concepts/constraint-execution-authoritative-lifecycle-contract.md`
  (rows 41, 45, 46, 46a, 51)
- **Item 9:** `.project/active/constraint-lifecycle-multi-entry/` (zero-entry template fix; the
  constraint-free firewall the spec's provenance note corrects)
- **Epic:** `.project/backlog/epic_constraint_execution_lifecycle_remediation.md` (Item 11, rows 13–15)

**Next Steps:** Independent `/_my_design_review`, then `/_my_implement` from Phase 0 (RED-first).
