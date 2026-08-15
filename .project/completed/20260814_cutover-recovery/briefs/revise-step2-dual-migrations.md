# Stage brief — REVISE step 2: the coordinated dual exact-ID type migrations (both repos)

**You are executing step 2 of the owner's REVISE path** on the Item 7 cutover recovery.
Plan: `/home/reid/1cfe/sysml-codegen-item7-rebuild/.project/active/cutover-recovery/plan.md`.
Read first, in order: `owner-disposition-20260811.md` (the ruling this stage executes), the
plan's "fifth entry" rulings (search `#### The fifth entry`), the measured probe inventories in
`evidence/dual-qualifier-drop-dryruns.txt`, `audit.md` ("Code integrity" and audit-F1), and
ledger rows L-033/L-034/L-036/L-037/L-280 in `ledger-4a.md`/`ledger-4a.json`.

Work synchronously. Never pause for background agents or schedule check-backs; finish the
artifact this turn or stop with questions as your entire final message.

## Intent

The owner ruled (2026-08-11) that the coordinated exact-ID type migration in BOTH repos is
Item 7 scope. Today eight retained 3C dual pairs keep a legacy name-keyed shape alive beside
its exact UUID-keyed replacement, and consumers still read the legacy side. This stage migrates
every consumer — production and test — onto the exact shapes, so the legacy duals lose all
readers and the retirement runbook's deletions become executable. **Adapters, shims, and
re-exports are banned by plan rule — consumers change, the exact types do not bend.**

This stage does NOT delete the legacy duals themselves: their deletion rows stay with the
retirement runbook (executed at revise step 6). The stage's exit measurement is reader counts:
for each dual, grep-measured readers of the legacy member in `src/`, `tests/`, `scripts/`
must be zero outside the dual's own definition site and the retirement-owned modules, and the
count is recorded in the report.

## Worklist (the measured inventories are the authority; re-measure, don't trust)

**codegen (`/home/reid/1cfe/sysml-codegen-item7-rebuild`):**

1. **L-033/L-280 — expression compiler.** `CompilationResult` (name-keyed, mutable) vs
   `ExactCompilationResult` (UUID-keyed, frozen); `compile_calc_def` (4 params) vs
   `compile_calc_def_exact` (1). Probe measured 26 failed + 5 errors of 79 nodes under the
   drop. Also detangle the survivor: `compile_calc_def_exact` constructs a legacy
   `CompilationResult` inside its own body (`extraction/expression_compiler.py:378`, body
   240–391) — that construction goes.
2. **L-034 — `extraction/data_models.py`.** Name-keyed fields vs `_by_id` twins; 58/86 nodes
   read the legacy side. The extractor still writes the name-keyed fields; after consumer
   migration they may become write-only — leave the fields in place (their removal is the
   retirement row) but record the post-stage reader count.

**agentic-mbse (`/home/reid/1cfe/agentic-mbse-item7-rebuild`):**

3. **L-036** — 34/450 nodes: missing fields on the identified payload.
4. **L-037** — three duals: `usage_id`/`definition_id` (134/450), `expected_usage_ids`
   (134/450), different preflight arguments (4/450).
5. **The two unledgered production call sites** (measured this recovery; they WILL break if
   legacy members are deleted unmigrated): `src/agentic_mbse/validation/level4_constraints.py:55-56`
   and `level6_architecture.py:620-621`. Migrate both to identified evaluation. The audit
   corroborates: neutral profile evaluation overwrites duplicate QNs by dictionary order
   (`sysml/executable_profile.py:1036`) — after migration the identified route must not
   inherit that; ambiguous inventories are refused explicitly, not last-writer-wins.

**agentic-mbse validation findings riding this wave (same files/area, audit-mandated):**

6. **audit-F1 — remove the self-binding exemption.** `_owner_covers_name` and its uses in
   `src/agentic_mbse/validation/level2_structure.py` (~309–357) suppress `SI_SELF_BINDING`
   when an outer same-named attribute or sibling calc output exists. Authority to remove it is
   already on record: D-4 [OWNER-VERBATIM 2026-08-05] ("Never reinterpret a self-binding as an
   outer reference"), the contract's blocking-diagnostics clause and violation table
   (`.project/concepts/constraint-execution-authoritative-lifecycle-contract.md:370,:662` in
   the codegen repo). After removal the diagnostic fires on every true `in P = P`; align
   `tests/test_validation/test_item12_checks.py` (its :73 area currently requires the
   exemption) with exact elaboration, and correct `docs/patterns/plant-idiom.md:35` — the
   plant idiom's covered self-binding is a blocking diagnostic, not a supported rescue.
7. **Invalid-manifest fallback.** `src/agentic_mbse/validation/level6_architecture.py:47,:111`:
   malformed/unreadable manifests collapse to `None`, are skipped, and Level 6 can stay green;
   `tests/test_sysml_quality_checks.py:969` blesses that. Represent invalid input explicitly
   and emit a failing validation issue; fix the blessing test.

## Boundaries

- A test node whose only problem is that its evidence source is a retiring v5 fixture belongs
  to revise step 3 (the 111/113 replacement stage), not here. A node with both problems gets
  its type-shape migration here and is named in the report as still step-3-pending.
- Do not touch the 16 pre-existing production ruff findings (spec-vs-baseline conflict is an
  open owner question). No new findings may be added.
- Do not modify the 37 ratified corpus fixtures or the accepted v6 batch.
- Rule 10 stands: a premise conflict (recorded rule vs recorded goal, or evidence against a
  plan premise) STOPS the stage for surfacing — your final message becomes the surfacing.

## Environment (will burn hours if ignored)

- Worktrees: codegen `/home/reid/1cfe/sysml-codegen-item7-rebuild`, agentic
  `/home/reid/1cfe/agentic-mbse-item7-rebuild`, both branch `item7-rebuild`. Venv
  `/home/reid/1cfe/item7-rebuild-venv`. FIRST ACTION: assert resolved `__file__` for
  `sysml_codegen`, `agentic_mbse`, `simkit` points into the two rebuild worktrees and pinned
  teax (`/home/reid/1cfe/teax`). Re-assert after any venv operation.
- License: `set -a; source /home/reid/1cfe/agentic-mbse/.env; set +a`. The ONLY valid proof of
  a licensed run is zero `no live syside license` skip lines; counts don't discriminate.
- agentic: run the DEFAULT suite (`pytest tests/`); never `-m ""` (pulls the PDF-extraction
  corpus subsystem — never an acceptable gate for SysML-side items, [OWNER 2026-07-12]).
- Some agentic tests shell out to bare `python`; put the venv's `bin` on PATH.
- Scratch worktrees for probes/patch regeneration go beside the repos in `/home/reid/1cfe/`,
  never `/tmp`. Never commit `uv.lock`. Use `git -C <repo>` for cross-repo git; pathspec
  commits miss untracked files (stage first).
- Expected clean start: codegen **3862 / 47 skipped / 53 deselected** licensed; agentic
  **1825 / 1 / 5**; execution lane **53**; corpus **15/22**; ruff src **16**; mypy **69 in 16**.

## Requirements

- Declared path set first (both repos), in your first commit-planning note in the plan. An
  unexplained changed path stops the stage.
- **Runbook patch drift:** editing any file a prepared patch under `runbook-patches/step{1,2}/`
  touches breaks the patch. `tests/unit/test_runbook_patches.py` is the drift check. Regenerate
  broken patches from a scratch worktree at the NEW committed HEAD — hand-editing hunk headers
  fails.
- **Coordinated paired commits: agentic-mbse commits first; the codegen commit message names
  the agentic OID.** Serialize — one committer per tree at a time.
- Ledger + plan bookkeeping: on completion, amend the fifth-entry items 1–2 as executed (cite
  commits), update L-033/L-034/L-036/L-037/L-280 rows' dispositions so the retirement steps
  own only the deletions, and add a stage note to the plan.
- Battery before each commit: full licensed codegen suite + agentic default suite (deltas
  explained node by node), execution lane if touched (state the command), corpus
  `scripts/capture_v6_batch.py --check` 15/22/0, ruff (16, no new)/mypy (69 in 16, no new),
  `git diff --check`, `scripts/check_ledger_4a.py` paths + surface + groups,
  `tests/unit/test_runbook_patches.py` green.

## Report back

Per-dual: before/after legacy-reader counts and the node delta with names. audit-F1: the new
diagnostic's firing set on the corpus/validation fixtures and every test realigned. The two
production call sites: what identified evaluation replaced. Battery numbers both repos. Commit
OIDs, paired. Nodes deferred to step 3, named. Any rule-10 surfacing.
`ARTIFACT:` the updated plan.
