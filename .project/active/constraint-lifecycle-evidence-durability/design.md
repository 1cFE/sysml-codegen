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

- **A1 — No consumer needs typed access to `evidence.report`.** Grep at `07eb0ac`: the only readers
  are `projection.py:28–29` (duck-typed `report.headline`/`report.results`) and `evidence_io.py:49`
  (`report.model_dump(mode="json")`). Nothing does typed field access. → We may seal `report` into an
  immutable snapshot without losing a real capability. *If false:* isolation must keep a typed façade.
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
- **A5 — `output_router.write_outputs` raises a distinguishable error on write failure.** It raises
  `OutputRouterError` (`pipeline_executor.py:22`), and the write phase (`:154–161`) runs *after* the
  module loop, so `context.failed_module_key` is still `None` there. This is what lets OUTPUT_WRITE be
  emitted honestly (D3). *If false:* OUTPUT_WRITE collapses instead.

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
- `project(result, *, provenance)` (drop the `report` param). Inside: `report =
  result.outputs.get(REPORT_CHANNEL)` (move `REPORT_CHANNEL` to `projection.py`, or import it).
  - `report is None` → `responses = {}`, `report_out = None`, `outputs` built as today from scalar
    channels (`projection.py:32–36`). This is the constraint-free empty-evidence shape.
  - `report is not None` → today's behavior (headline + per-constraint responses), then seal (D2).
- `evaluator.py:132` and `:203` both collapse to `return project(result, provenance=provenance)`. One
  read seam, not two.

**Downstream join — policy must tolerate empty responses.** Policy reads `evidence.responses["headline"]`
unconditionally (`policy.py:65`; `ObjectivePolicy` `:121`) → that would move the `KeyError` from the
evaluator to the policy. So `DispositionPolicy.assess` and `ObjectivePolicy.assess` gain an explicit
first branch: `if "headline" not in evidence.responses:` → an **`unconstrained`** disposition (a new
demo-policy disposition, distinct from `not_assessed`). This keeps constraint-free (empty) and
excluded-only (`not_assessed`) as **structurally distinct** surfaces:

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

**Mechanism detail.**
- A `_freeze(value)` helper in `evidence.py` (or `projection.py`) recursively converts dict→`MappingProxyType`
  and list→`tuple`. `EvidenceProvenance` is already a frozen `StrictBaseModel`.
- `ModelEvidence.report` type changes from `Any` (the live model) to the frozen JSON tree
  (`Mapping[str, Any] | None`). `responses`/`outputs` gain a validator that wraps them in the
  read-only form.
- **`encode_evidence` adjusts** (`evidence_io.py:35–51`): today it calls `evidence.report.model_dump(mode="json")`
  (`:49`). Now `evidence.report` **is** the JSON tree already → the line becomes a pass-through of the
  sealed tree. `_tag_nonfinite` (`:20–32`) walks `dict`/`list`; a `MappingProxyType`/`tuple` tree needs
  the walker to accept `Mapping`/`Sequence` (or the snapshot uses plain dict/list and immutability is
  enforced by a wrapping proxy read at access). *Implementation note:* keep the sealed tree as
  plain dict/list for the digest walk, and expose it through a read-only proxy on the model — whichever
  keeps `encode_evidence` producing byte-identical output (A2). The parity test pins this.

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

**Decision.** **Emit** `OUTPUT_WRITE`. The condition: a failure raised by
`output_router.write_outputs(...)` on the persisting (file-backed) route — where the module loop has
already completed, so `context.failed_module_key is None`.

**Why emit, not collapse.** Item 6's F1 record flagged `OUTPUT_WRITE` (`failure.py:23`) as
defined-never-emitted — a lie in the taxonomy. The write phase is real and distinguishable:
- `pipeline_executor.py:154–161` runs `write_outputs(...)` **after** the topological module loop
  (`:128–148`), and only the loop sets `context.failed_module_key` (`:145`).
- `write_outputs` raises `OutputRouterError` (`pipeline_executor.py:22`); a filesystem failure raises
  `OSError`. Either way, at that point `failed_module_key is None` because the loop finished.
- Only `FileBackedEvaluator` persists (`persist_outputs=True`, `evaluator.py:199`); `PreparedEvaluator`
  uses `persist_outputs=False` (`evaluator.py:129`) and never reaches the write phase. So OUTPUT_WRITE
  is a file-backed-only phase — exactly what the runner comment already anticipates (`runner.py:119`,
  "OUTPUT_WRITE (a future persisting backend)").

**Change.** `_normalize_run_failure` (`evaluator.py:56–66`) branches:
```
phase = OUTPUT_WRITE if isinstance(error, OutputRouterError) or context.failed_module_key is None
        else MODULE_EXECUTION
```
`module_or_channel` stays `failed_module_key` (None on a write failure — honest: no module failed).
Primary discriminator is the `OutputRouterError` type; `failed_module_key is None` corroborates. The
runner already routes it: `_commit_execution_failure`'s `else` branch (`runner.py:119–124`) commits an
`execution_failed` case for both MODULE_EXECUTION and OUTPUT_WRITE — no runner change needed.

**Fixture.** The OUTPUT_WRITE coordinate forces a real write failure: point the FileBacked
`output_dir` at an unwritable path (read-only dir) so `write_outputs` raises `OSError` after a clean
module run. Non-contrived: a genuine persistence failure. Test asserts the committed
`failure_json.phase == "output_write"` and `module_or_channel is None`.

**Rejected.** Collapse the phase (shrink the taxonomy to three). Rejected because the condition is real
and reachable on the shipped file-backed route — collapsing would *lose* the honest phase name for a
failure that genuinely happens during output write.

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
- **The incidental encode-before-policy protection.** `runner.py:134` (encode) no longer sits before
  `:136` (assess) *for protection*; the ordering coupling is removed and `encode_evidence` moves to
  just before `commit_case`. The "protect the persisted copy by encoding early" rationale is deleted —
  immutability (D2) is the mechanism now.
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
  snapshot change for a report-bearing case (A2). Pinned by an encode golden test.

---

## Phased plan

Ordering is RED-first and bottom-up: prove the crash, fix the seam, seal immutability, then the
statuses and deletions. Each phase is independently testable; anchor movement in a report-bearing
encode (INV-G) is a STOP.

- **Phase 0 — RED coordinate one.** Author the `constraint_free` fixture (codegen). Reproduce
  `KeyError: 'constraint_report'` on both routes against the current evaluator. This is the
  reproduction the spec's provenance note says is still owed. Commit the fixture + the RED evidence.
- **Phase 1 — Absence seam (D1).** Move the read into `project`; collapse `evaluator.py:132`/`:203`;
  add the `report is None` empty-evidence branch; add the policy `unconstrained` branch. GREEN on
  `constraint_free` both routes. INV-A.
- **Phase 2 — Immutability (D2).** `_freeze` snapshot at project; `ModelEvidence.report` becomes the
  sealed tree; read-only `responses`/`outputs`; adjust `encode_evidence` to pass through the sealed
  tree byte-identically. Remove the encode-before-assess coupling (move encode to pre-commit). INV-C,
  INV-D, INV-G.
- **Phase 3 — OUTPUT_WRITE (D3).** Branch `_normalize_run_failure`; add the unwritable-`output_dir`
  coordinate. INV-F (phase half).
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
- **Sealed-tree representation detail.** Plain dict/list walked for the digest vs. `MappingProxyType`/
  `tuple` exposed on the model — whichever keeps `encode_evidence` byte-identical (INV-G). Settled at
  implementation against the golden test.
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
