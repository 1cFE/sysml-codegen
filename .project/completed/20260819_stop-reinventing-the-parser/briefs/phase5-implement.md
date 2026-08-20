# Brief — Phase 5 implement: rebuild and verify the immutable artifact chain

You are executing **Phase 5 only** of plan **Revision 4** for
`.project/active/stop-reinventing-the-parser/`. Phases 1-4 are complete, audited, and closed.
Phase 5 names the production identities, builds and verifies the immutable artifact set through
the committed runner, clears the implementation-time product gate, and prepares the
independent-audit handoff. This is the strictest ceremony in the plan: every asserted status
must be produced by committed tooling, every count recorded, and nothing repaired after
sealing. Read in order:

1. `.project/active/stop-reinventing-the-parser/plan.md` — **Revision 4**, your contract:
   "Phase 5: Rebuild and verify the immutable artifact chain" (checklist, both validation
   blocks, stop rule), the Global Execution Contract, and the Phase 4 closure block (the
   production candidate and its rollback rule). The **`audit-phase3-F2`** item (plan.md:1231)
   is an explicit unchecked obligation gating `C_prod` — read it where it stands.
2. `design.md` — **Revision 8** — `#immutable-artifact-set`,
   `#acyclic-production-and-evidence-topology`, `#required-isolated-runs`,
   `#executable-codegen-execution-pins`, `#fusion-dependency-and-lock-changes`,
   `#codegen-pin-and-dependency-contract`.
3. `run-records/entry-status.md` — run scaffolding, checkout-integrity digests, and the
   "Phase 5 pre-work" note: all three external pins exist, and the fusion-tea user checkout
   currently sits on an unrelated item's branch.
4. `run-records/phase4-audit.md` — the bar your evidence records are held to.

Provenance: plan rev 4 and design rev 8 are binding. On any conflict, surface it in your final
message — never resolve it silently.

## Identities and trees

| Role | Where | Identity |
|---|---|---|
| Codegen production source | `/tmp/stop-parser-rev2/worktrees/sysml-codegen`, branch `stop-parser-impl-r2` | `571ed39` — the audited production candidate. Phase-5-scoped changes (runner, pins, evidence tests, version/lock files, docs the checklist names) land on top; `C_prod` is the resulting commit |
| Agentic production source | `/tmp/stop-parser-rev2/worktrees/agentic-mbse`, branch `stop-parser-evidence-r2` | `3f8bd58` — name it `A_final` after its independently-green run; write nothing there unless the plan's checklist explicitly places it |
| Fusion parent | commit `824a876e` in `/home/reid/1cfe/fusion-tea` | build `F_final` from this commit in a **dedicated worktree/clone under `/tmp/stop-parser-rev2/`** — the user checkout is on another item's branch and must not be touched |
| TEAx | commit `744745f8` in `/home/reid/1cfe/teax` | frozen source for isolated runs — dedicated extraction, read-only |
| 1costingfe | commit `02543850` in `/home/reid/1cfe/1costingfe` | frozen source for isolated runs — dedicated extraction, read-only |
| Docs checkout | `/home/reid/1cfe/sysml-codegen` | `.project/` updates + plan completion section only, committed as your final act |

Touch NOTHING else. No user checkout is ever modified, staged, stashed, or switched — all five
retain their entry status. No push to any remote. Old `/tmp/stop-parser.QVJIIP/*` remains
read-forbidden.

## The work (plan rev 4 Phase 5 is the contract; ordering and hard edges)

1. **The `audit-phase3-F2` gate first.** Deliver the licensed positive-capability proof the
   plan item specifies, as a kept test, before `C_prod` is named. If it cannot be delivered as
   specified, that is a stop, not a waiver.
2. **Tests first — provenance and topology.** Extend
   `tests/conformance/test_evidence_artifact_topology.py`, `tests/unit/test_environment_pins.py`,
   `tests/unit/test_teax_discovery.py`, and the verification tool tests to reject: external run
   staging, wrong roots/hashes, missing explicit TEAx paths, unexpected skips, dirty sources,
   wrong parents, extra evidence paths, and self-reference. Every rejection test must be able
   to fail — mutation-check the important ones; fake tests have been audit findings twice in
   this item.
3. **Committed runner.** Finish `verification/build_artifacts.py`,
   `verification/run_independent_green.py`, and `verification/audit_evidence.py` so the runner
   itself executes every command, retains and authenticates output and import probes, and
   writes the evidence records. **No external script, shell pipeline, or your own session may
   supply a passing status or output hash** — if you ran it by hand, it doesn't count; the
   runner must have run it.
4. **Production identities.** Run Agentic's battery from its clean archive; name `A_final`.
   Land every Codegen Phase-5 change in one reviewable sequence ending in **`C_prod`**; build
   deterministic source archives and wheels from clean extractions; record their hashes
   outside the repositories while downstream verification runs.
5. **Execution pins.** Update `tests/execution/environment_pins.py` and
   `tests/helpers/teax_discovery.py` to consume the closed execution-provenance manifest and an
   explicit TEAx root; reject the old sibling-shape assumption while preserving wrong-tree
   refusal.
6. **Fusion landing.** From the frozen parent in its dedicated worktree: pin Agentic `0.1.3`,
   Codegen `0.1.1`, 1costingfe `0.1.0`, exact immutable revisions, and the `C_prod` identity in
   `pyproject.toml` / `uv.lock`. Run the maintained model roots unchanged unless a real
   semantic violation is measured (if one is: that's a surfaced finding, not a quiet edit).
   Land the verified result as `F_final` on a branch in that worktree — nothing pushed.
7. **Evidence child.** Create **`C_evidence`** directly on `C_prod` with exactly
   `verification/dependencies.json`, `wheelhouse-requirements.txt`,
   `execution-provenance.json`, `independent-green.json`, `reconciliation-ledger.md`, and
   `evidence-lock.json`. No other path changes; no evidence file names or hashes `C_evidence`;
   the lock does not hash itself.
8. **Implementation-time product gate.** Only after the licensed live-and-capture indexed
   computed-attribute proof is green at `C_prod`: append the production result to the
   product-lens ledger, recording `audit3-F1` as fixed from that exact identity — never from a
   worktree-only run.

## Validation (plan rev 4 lists every box — all binding; highlights)

- **Isolated artifact runs**, each from its recorded archive/wheel, each through the committed
  runner: Agentic (focused semantic-evidence, fast suite, scoped strict, repo-wide mypy
  baseline, Ruff — **never** the PDF/HTML corpus or the 15 paid/network cases, per the
  owner-verbatim exclusion); 1costingfe (complete pytest + configured Ruff); TEAx (simkit and
  battery-demo suites); Codegen (scoped strict, mypy baseline, default and licensed suites,
  live/snapshot parity, generated-package tests, complete execution lane with manifest-pinned
  imports); Fusion (`uv lock --check`, configured suite, complete model validation, final
  generated Fusion/TEAx execution and mutation proofs using only recorded wheels and extracted
  sources).
- **No-unexpected-skip rule enforced**, with selected/passed/failed/error/skipped/xfailed/
  deselected counts recorded per pytest invocation, and **every figure recomputable from a
  recorded command** — untraceable numbers have been audit findings twice; do not create a
  third.
- **Topology and reconstruction:** rebuild the Codegen archive and wheel from `C_prod` and
  require exact filename and SHA-256 matches with `dependencies.json`; prove Fusion pins
  `C_prod` and never `C_evidence`, an editable source, or a sibling path; prove
  `C_evidence^ == C_prod` with the changed-path set exactly the six files; recompute every
  digest; run the committed mechanical auditor with explicit `C_prod`, `F_final`, and
  `C_evidence` inputs and require every group green.
- **Checkout integrity:** all five original user checkouts retain their entry digests.
- License: `set -a; source /home/reid/1cfe/agentic-mbse/.env; set +a`; never copy `.env`, its
  value, or any secret into any artifact, evidence file, commit, or report.

## Environment notes (measured in this run and its predecessors)

- Codegen's default suite and `capture_baseline.py` need the declared extraction lane:
  `STOP_PARSER_ARTIFACT_SOURCE_INPUTS=<extraction>/artifact-source-inputs.json`, and the
  Agentic sibling extraction present at the path the extraction's `uv` sources expect. Agentic
  extraction paths must contain the string `agentic-mbse`.
- TEAx's own `.venv`/`uv run` is broken at the frozen commit; execution-lane runs of generated
  packages have historically hosted TEAx via the consuming environment with an explicit
  `sys.path` insertion of `packages/teax-simkit`. Your committed runner must make whatever
  route it uses explicit and provenance-recorded; the discovery helper's explicit-TEAx-root
  contract exists precisely so nothing assumes a sibling layout.
- A full snapshot re-capture rewrites every `captured_at` timestamp; byte-identity gates must
  compare content, not re-capture wholesale — reconcile through the transition ledger, never by
  regenerating baselines to match.
- Stage all extractions, worktrees, wheelhouses, and evidence staging under
  `/tmp/stop-parser-rev2/`.

## Deliverables

1. Commits: the Phase-5 sequence ending in `C_prod`, then `C_evidence` as its only child, on
   `stop-parser-impl-r2`; `F_final` on its dedicated Fusion worktree branch; `A_final` named
   (tag or recorded identity per the design). Nothing pushed anywhere.
2. Every Phase 5 validation box executed with commands, counts, and results recorded; the six
   evidence files written by the committed runner only.
3. plan.md "Phase 5 completion" section filled (identities table with full SHAs, artifact
   hashes, run counts, issues/deviations, rollback identity) plus the product-lens append,
   committed in the docs checkout.
4. **The independent-audit handoff:** exact identities, artifact hashes, and how to
   reconstruct every run — prepared as the plan's manual box specifies. **Do not self-certify,
   do not run `close` or `pre_pr`, do not declare the item done** — the independent audit and
   the item close are the owner's.
5. Final message: prose summary — identities named, the artifact chain account, isolated-run
   results, topology proofs, product-gate disposition, deviations — ending with
   `ARTIFACT: .project/active/stop-reinventing-the-parser/plan.md`. If any stop rule trips,
   say so plainly at the top and stop.

**Stop rule (plan rev 4, verbatim in effect):** any Phase-5 failure caused by production
source, tests, fixtures, docs, package metadata, pins, or runner logic returns to the owning
production phase and creates a new dependent identity chain. **Never repair it only in
`C_evidence`.** A `deep_cross_scope_probe` graph restoration remains the global stop condition
everywhere, including in Fusion's model validation.
