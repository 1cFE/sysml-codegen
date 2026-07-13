# Audit: Part-Instance Index (Item 4)

**Verdict:** Certify-with-notes
**Audited:** 2026-07-12
**Branch:** constraint-exec-epic
**Commit:** ce590e8 (Phase 3 tip; audited 36a75cb → ce590e8)

---

## Summary

The core deliverable is solid and matches the design. `occurrences_of` — the specified Item-5
entry point — is correct: fail-closed cardinality by node-type dispatch, subtype-closure
projection, entry-independent identity, integer-index ordering, set dedup. All five success
criteria are covered by tests, and the additive boundary is structurally clean (the three phase
commits add six files and modify none — `git diff --stat 19abfeb..ce590e8`).

One real defect: the bulk convenience `all_occurrences()` (and `all_source_owners()`, built on it)
silently swallows `NonFiniteCardinalityError` per-definition. This is a third disposition — skip —
reachable through a public, completeness-named method, and it silently narrows INV-2. It is the
priority finding; it is confirmed and requires a cure before Item 5 consumes the index. It does not
compromise the specified `occurrences_of` contract, so the item certifies with that must-fix.

**Execution note:** every `uv run` / `pytest` / `python` invocation in this sandbox requires
interactive approval, which is unavailable in this orchestrated run. All gates below are verified
statically; the four live/venv gates are re-stated as **Requested live probes** for the
orchestrator to run and append. None of my findings depend on an un-run probe — the swallow is
proven by reading the code, and the additive/byte-identity claim is proven by the commit diff.

---

## Priority finding — the `all_occurrences()` swallow (CONFIRMED; must-fix)

**Location:** `src/sysml_codegen/analysis/part_instance_index.py:283-300` (`all_occurrences`),
`302-310` (`all_source_owners`).

**What the code does.** `all_occurrences()` iterates every user PartDef and calls
`occurrences_of(qn)` inside `try/except NonFiniteCardinalityError: continue` — so any definition
whose occurrence set touches a non-finite multiplicity is dropped from the dump with no signal
(no returned blocked-set, no log). `all_source_owners()` is a thin wrapper over
`all_occurrences()`, so it inherits the same silent omission.

**Adjudication against Design Principle 5 and INV-2.**

- INV-2 (design.md:280) is unqualified: "every multiplicity a queried path passes through is
  either expanded to a proven finite count or blocks with a named diagnostic. **No third arm.**"
  `all_occurrences()` queries paths (through `occurrences_of`) and adds a third arm — skip. The
  implementer's docstring narrows INV-2 to "a *direct* `occurrences_of` call," but the invariant
  as written carves out no such exception. An invariant weakened in a docstring to pass a test is
  exactly what an audit should catch.
- The design **named** `all_occurrences()`/`all_source_owners()` as "(optional convenience) …
  for tests and diagnostics" (design.md:251) but **never specified swallow semantics**. The
  catch-and-skip is an undocumented implementer deviation, adopted (per plan.md:416-420) so the
  determinism test's full dump would not abort on the combined fixture's blocked shapes.

**Is it a real defect in waiting?** Yes — by the brief's own test. If Item 5 iterates via
`all_occurrences()`, a constraint-owning definition with a blocked multiplicity (e.g. a member
`[n]`) is silently skipped: `occurrences_of(D)` raises, the bulk loop swallows it, and D's
assertion never lowers. Worse, `all_source_owners()` — the natural way to *discover* which
definitions to lower — silently omits every blocked owner from the worklist, with zero signal.
That is precisely the "silence is never an outcome" failure the concept exists to stop. The trap
is amplified by the method name: `all_occurrences()` implies completeness, so the next author who
reaches for "all" gets a partial set and no way to know.

Note the swallow is also *coarse*: `occurrences_of(D)` raises on the first non-finite step, so a
definition with both finite and non-finite occurrences loses **all** of them from the dump, not
just the blocked path.

**Required cure (pick one; the brief's menu):**

1. **Surface the blocked set.** `all_occurrences()` returns blocked definitions explicitly beside
   the occurrences (e.g. a small result object or `(occurrences, blocked_owners)`), so no caller
   can mistake a partial dump for a complete one. The determinism test then asserts on both.
2. **Remove/rename to make misuse impossible.** Drop the swallow and have the determinism test
   query specific enumerable owners (it already knows them), or rename to a name that states
   partiality *and* still surface what was skipped.

A docstring caveat is not a sufficient cure — the third arm must not be silently reachable through
a completeness-named public method. This must be fixed before Item 5 builds on the surface (cheap
now, load-bearing later). It does not require re-opening `occurrences_of`, which is correct.

---

## Findings

### Plan completion

All three phases are implemented and their changes-required boxes correspond to real code.

- **Phase 1** — classifier + 8-row truth table: `classify_cardinality`
  (`part_instance_index.py:72-120`) and `tests/unit/test_part_instance_index.py` (8 tests). The
  `.value` accessor the classifier reads (`part_instance_index.py:108,117`) matches the codebase
  idiom for `LiteralInteger` (`parameter_groups.py:212-214`) and the plan's live-confirmed
  `upper_bound.value == 3`. Verified.
- **Phase 2** — walker, closure, index object, promoted+extended fixture, 6 live positive tests.
  Walker (`part_instance_index.py:139-194`) mirrors `_find_instantiation_paths`
  (`usage_extractor.py:313-369`) and replicates the `_visited` cycle guard
  (`part_instance_index.py:157-161`). Both sites carry the "keep in sync" note. Verified.
- **Phase 3** — additive guard (`tests/unit/test_part_instance_index_additive.py`, AST scan) and
  byte-identity via commit diff. Verified structurally (see below).

Deviation recorded in Implementation Notes: the `all_occurrences()` swallow — see priority
finding. It is disclosed honestly in plan.md and the code docstring; the disclosure does not make
it correct.

### Spec conformance

Success-criteria walk (each maps to a test; all covered):

- **SC1 (9/9 oracle incl. plain subtype)** — `test_nine_instance_oracle` asserts the exact
  nine-path set (`test_part_instance_index.py:22-32,49-55`), including
  `InstanceIndexProbe__root__plain_subtype`. Covered. *Live-run pending (Probe A).*
- **SC2 (collision, same-named members, different owners/counts)** —
  `test_same_name_collision` asserts `{BankA: 3, BankB: 2}` keyed by `steps[-1].owning_def_qn`,
  never bare leaf name (`test_part_instance_index.py:58-71`). Fixture carries the two-`member`
  shape (`model.sysml` BankA/BankB). Covered.
- **SC3 (parameterized/variable/ordered/unbounded block with named diagnostic)** —
  `test_blocking_names_owner_and_feature` parametrizes `[n]`, `[*]`, `[0..5]` (variable range),
  `[3] ordered` and asserts owner+feature in the message (`test_part_instance_index.py:133-153`).
  `nonunique` is proven by the unit truth table instead of the fixture (load-error risk,
  correctly documented at the fixture site and in b1-evidence note 4). Covered.
- **SC4 (byte-identical across repeated live loads)** — `test_determinism` loads the fixture
  twice and asserts identical ordered `instance_path` lists from both `occurrences_of` and
  `all_occurrences` (`test_part_instance_index.py:114-130`). Covered.
- **SC5 (corpus regenerates byte-identically)** — additive guard test plus
  `git diff --stat 19abfeb..ce590e8`: six files added, **zero existing files modified**. Since no
  existing code path changed and nothing imports the module, byte-identity holds by construction.
  Strongly verified.

Tagged requirements:

- **[HARD] "fixed finite literal ≠ `count is None`"** — met. The classifier dispatches on the
  `upper_bound` **node type** and blocks `FeatureReferenceExpression`
  (`part_instance_index.py:100-101`) *before* reading `.value`, so a parameterized `[n]` with a
  non-`None` cached bound blocks. This is the core B2 protection; correctly implemented.
- **[HARD] consumes existing facts only, no new SysIDE facts** — met. Reads the live
  `multiplicity`/`is_ordered`/`is_nonunique` surface; imports only read-only helpers from
  `usage_extractor` (`part_instance_index.py:15-23`); does not import `MultiplicityData`.
- **[HARD] retyped/redefined dedup** — met. Dedup key is entry-independent
  (`part_def_qn` from `_leaf_part_def_qn`, computed from the usage via `most_specific`,
  `part_instance_index.py:251-260`); `occurrences_of` collects into a `set` (`:277-281`).
- **[HARD] additive** — met (SC5).
- **[INFERRED] one entry per concrete occurrence** — met; fixed-multiplicity siblings are
  distinct `InstanceOccurrence`s with distinct `occurrence_index` (Cartesian in the walker,
  `:180-184`), proven by `test_cartesian_expansion` (6 distinct paths).

Non-goals respected: no constraint lowering, no `constraint_id` minting, no snapshot changes, no
retrofit onto calc discovery. Confirmed by the commit diff (nothing outside the new module + its
tests/fixture).

### Design conformance

Implementation follows design rev 2.

- D3 node-type dispatch gate — implemented exactly, including the fail-closed default arm for an
  unrecognized `upper_bound` node (`part_instance_index.py:102-106`) and unrecognized *lower*
  bound (`:111-115`, a small hardening beyond the sketch, in the fail-closed spirit).
- D5/C3 entry-independent identity, D6 integer-index sort with `-1` singleton sentinel
  (`_occurrence_sort_key`, `:221-235`), D7 set dedup, D8 live-node-only (no `MultiplicityData`).
  All present.
- INV-5 collision-free keys from the walk's `PathStep` — present.
- **Deviation from INV-2** in the bulk API — the priority finding. This is the one place the
  implementation silently diverges from a stated invariant.

### Code integrity

- **Priority finding** (silent fallback on an invariant violation) — the `all_occurrences()` /
  `all_source_owners()` swallow. Classic "return a safe default instead of raising." See above.
- **Minor (nit, no finding raised):** `classify_cardinality`'s `owning_def_qn` parameter is
  unused (the raise happens in `_cardinality_indices`, which supplies it to the error). It matches
  the design sketch signature; harmless. `assert winner is not None`
  (`part_instance_index.py:259`) is stripped under `python -O`, but matches the codebase's
  invariant-guard idiom. Neither warrants a change.

No god functions, no parameter sprawl, no leaky names, no copy-paste siblings. The walker is a
deliberate, documented copy of `_find_instantiation_paths` (INV-1 forbids refactoring the
original this item) — acceptable and noted at both sites.

---

## Certification

**Checked (statically, by reading code + commit diff):**

- Classifier truth table vs `b1-probe-evidence.md`: all 8 rows map to the 8 unit tests, including
  the `FeatureReferenceExpression` block despite non-`None` cached bounds (dispatch precedes the
  `.value` read). Verified in code.
- Walker/closure/dedup/ordering logic traced by hand against the collision, Cartesian, and
  closure×multiplicity cases — the path spellings the tests assert are what the code produces.
- Additive gate: `git diff --stat` shows only additions; the AST additive-guard test is present
  and correct; `@requires_license` + the fixture's own ImportError guard make the live tests
  **skip** (not fail) in a license-free env, so the full suite stays green regardless.
- Success criteria SC1–SC5: each has a corresponding test with the right assertions.

**Marked:** Nothing promoted this pass. The plan phase boxes were already checked by the
implementer and correspond to real code. I am **not** checking the spec success criteria or the
epic heading, because (a) the live gates (Probes A–C) are un-run in this sandbox — I verified the
tests exist and are correct by inspection, not that they pass — and (b) one must-fix (the swallow)
remains. Recommend the orchestrator run Probes A–D, apply the swallow cure, then mark SC1–SC5 in
spec.md and promote the epic item to full Certify.

**Not checked (limits of this pass):**

- I did **not execute** any test, mypy, ruff, or the full suite — the sandbox requires approval
  for `uv`/`pytest`/`python` and this run is non-interactive. The plan's numeric claims (10/10
  live pass, suite 2161/4, mypy 77 baseline, ruff clean on new files) are **plausible and
  consistent with the code** but **unverified by me**; they are re-stated as Probes A–D.
- I did not independently re-derive the live SysIDE multiplicity surface (`b1-probe-evidence.md`);
  I took it as given and checked the classifier against it.
- I did not audit Item 5 consumption (not built) beyond assessing the misuse risk of the bulk API.

---

## Requested live probes (sandbox blocked execution — orchestrator to run and append)

**Probe A — license-free unit gates (plain venv).** Expected: GREEN.
```
uv run pytest tests/unit/test_part_instance_index.py tests/unit/test_part_instance_index_additive.py -q
```
Expected: 8 truth-table tests + 1 additive test pass (9 passed).

**Probe B — live conformance (plain venv if licensed, else licensed sibling env).** Expected:
GREEN (10 passed), or SKIPPED if no license (which still keeps the suite green).
```
uv run pytest tests/conformance/test_part_instance_index.py -v
```
Licensed sibling-env form (per plan.md Implementation Strategy) if the plain venv skips:
```
env UV_CACHE_DIR=/tmp/agentic-mbse-uv-cache PYTHONPATH=/home/reid/1cfe/sysml-codegen/src \
  uv run --directory /home/reid/1cfe/agentic-mbse \
  python -m pytest -c /home/reid/1cfe/sysml-codegen/pyproject.toml \
  /home/reid/1cfe/sysml-codegen/tests/conformance/test_part_instance_index.py -v
```
Confirms SC1 (9/9), SC2 (collision), SC3 (4 blocking shapes), SC4 (determinism), SC7 (`[3..3]`),
SC8 (Cartesian + closure×multiplicity). This is the only gate that proves the live walker; treat
its pass as required for full Certify.

**Probe C — full suite + type + lint (plain venv).** Expected: 2161 passed, 4 skipped; mypy 77
(baseline unchanged, none in new files); ruff clean on `src/`.
```
uv run pytest tests/ -q
uv run mypy src/
uv run ruff check src/
```

**Probe D — swallow-cure regression (after applying the must-fix).** Once `all_occurrences()` is
cured to surface blocked owners, re-run Probe B's `test_determinism` and confirm it still passes
against the combined fixture — the cure must not reintroduce an abort on the blocked shapes, and
must expose the blocked set rather than hide it.

**Optional RED confirmation of the defect (mutation probe).** To demonstrate the swallow is a real
silent drop: temporarily add `assert idx.all_source_owners()` containing a blocked owner's
definition QN — it will be absent, confirming the omission is silent. Not required for the verdict;
the code read already establishes it.
