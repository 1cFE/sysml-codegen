# Stage brief — Independent audit of Slice 3D (Fusion Tea customer vertical + real TEAx)

Fresh, independent auditor; you did not implement this. Audit codegen commit `848628b`
(+ OID record `4d1a3ed`) on `item7-rebuild` at `/home/reid/1cfe/sysml-codegen-item7-rebuild`
(agentic-mbse claimed unchanged at `cc6c7a7` — verify that claim too). Contract: plan Slice 3D +
per-slice validation + rules, the Phase 2 C25/C2 protocol decision, the fifteen-item rename
ledger (D11) in `.project/active/elaborator-cutover/`, and `evidence/audit-3{a,b,c}.md`.
This slice is the recovery's core evidence gate — the original Item 7 failed here by
self-certification. Run everything yourself. Full permissions.

Environment: venv `/home/reid/1cfe/item7-rebuild-venv`; re-assert `sysml_codegen`,
`agentic_mbse`, AND `simkit` import paths (F2 trap); old-commit comparisons force PYTHONPATH +
assert `__file__` (3C process note); license `set -a; source /home/reid/1cfe/agentic-mbse/.env;
set +a`; proof = zero `no live syside license` lines. Scratch `/tmp/claude-audit3d/`. Parts bin
read-only `git -C /home/reid/1cfe/sysml-codegen show 07531e64:<path>`. Write only
`.project/active/cutover-recovery/evidence/audit-3d.md`; no commits.

## Verify (minimum; add your own judgment)

1. **Re-execute the real-TEAx lane yourself** with the recorded command
   (`python -m pytest tests/execution -m execution -q`). Confirm 38 passed / 0 skipped, then go
   deeper than the tests: run one live and one relocated-v6 generation+execution end-to-end in a
   probe of your own and compare the 11 channel values against
   `tests/execution/fusion_tea_arithmetic.py` — then check that file's arithmetic against the
   SysML sources themselves (it claims to be a hand transcription; spot-derive LCOE and one
   mutation figure from the model equations, don't take the module's word).
2. **No stub, no self-report.** Confirm the fake-simkit runner (`pipeline_runner.py`
   `_install_simkit_stub`) never enters the evidence path (the implementer pinned this — verify
   the pin actually detects the stub if injected); confirm no new test asserts on a script
   self-report; confirm the new tests carry no `skipif` and genuinely fail without simkit or
   license (try one: hide the license and confirm failure, not skip).
3. **Mutation evidence.** Re-run both typed-entry injections; confirm the every-and-only
   partition really covers every (module, formal) port (count them against the graph), that
   nothing was written to disk, and that reseal refusal was proven against the real
   `check_reseal_provenance` gate.
4. **Rename byte-proof.** Reproduce the strip-check: removing the eleven authorized `_in`
   suffixes from the six model files must reproduce the Item 6 content byte-for-byte. Confirm
   all 15 ledger rows map to hunks and no unledgered model change exists (diff the fixture tree
   at 848628b vs 26e7d04).
5. **The two unnamed production hunks.** Both were declared mid-slice: the enumeration-literal
   handling in `elaborate.py` (7× SI_OCCURRENCE_MISSING otherwise) and `sanitize_name` in
   `project.py` (unimportable class name otherwise). Verify each against its red state at
   `26e7d04`, check the fixes are general (not fusion-tea-shaped special cases), and confirm the
   sanitize fix has the test 3B said was missing.
6. **Corpus.** Re-run the 37-path comparison; confirm 37/37 against the amended ledger, exactly
   one row moved (fusion_tea → `graph 9/27/1/7`, discharging census B37-15), totals now
   15 public graphs / 22 typed errors, both error classes decoded separately with exact
   multisets, old cells retained beside amendments.
7. **Gates.** Full licensed suite (3539/47/38 claimed — the +20 deselected must be exactly the
   new execution nodes; confirm the acceptance command in the plan includes them); agentic truly
   unchanged (`git -C ... status` + `rev-parse`); ruff/mypy byte-identical; `git diff --check`;
   changed paths ⊆ declared; the five changed test modules each have a recorded responsibility
   disposition (no silent rewrite).
8. **Test quality** per the established bar, especially: does the constraint-report assertion
   compare a full dump against an independent expectation; are channel sets pinned by name; is
   live/relocated difference confinement (SysML Source lines only) asserted across the whole
   tree rather than sampled?

## Verdict

CERTIFY / FINDINGS (numbered, severity, file:line, resolution) / BLOCK. State what you did not
verify. `ARTIFACT: .project/active/cutover-recovery/evidence/audit-3d.md`
