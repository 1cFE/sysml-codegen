# Stage brief — Independent audit of Slice 3C (coordinated compiler/constraint authority)

Fresh, independent auditor; you did not implement this. Audit the PAIRED commits:
agentic-mbse `8b63393` at `/home/reid/1cfe/agentic-mbse-item7-rebuild` and sysml-codegen
`7af5dc9` (+ OID record `5daa8ed`) at `/home/reid/1cfe/sysml-codegen-item7-rebuild`, both on
`item7-rebuild`. Contract: plan Slice 3C + per-slice validation + Non-Negotiable Execution Rules,
completion notes for 3C, and the prior audit records `evidence/audit-3{a,b}.md`. Read code and
run checks yourself; never trust the notes. Full permissions.

Environment: venv `/home/reid/1cfe/item7-rebuild-venv` (re-assert import paths — both packages
must resolve into the rebuild worktrees; F2 trap in `evidence/baseline.json`); license
`set -a; source /home/reid/1cfe/agentic-mbse/.env; set +a`; proof = zero `no live syside license`
lines. Scratch `/tmp/claude-audit3c/`. Parts bins read-only:
`git -C /home/reid/1cfe/sysml-codegen show 07531e64:<path>` and
`git -C /home/reid/1cfe/agentic-mbse show ed5b8b02:<path>`. Write only
`.project/active/cutover-recovery/evidence/audit-3c.md` (codegen worktree); no commits.

## Verify (minimum; add your own judgment)

1. **The decoupling is real, not cosmetic.** Confirm `elaboration/elaborate.py` and
   `elaboration/project.py` no longer import from `analysis/constraint_lowering.py` (AST-level,
   not grep), that the moved `mint_constraint_id` / `resolve_modeled_default` are semantically
   identical to their previous definitions (diff the bodies), and that the legacy module
   re-imports them so existing callers and monkeypatch targets genuinely resolve — run one legacy
   constraint test that patches the old path to prove it.
2. **The rendered-implementation fix is a real bug fix.** Reproduce the two failure shapes at
   `38c2e15` (undeclared intermediate → function referencing names it never assigns; two declared
   outputs → tuple/schema disagreement), confirm both now render correctly, and check the fix
   rule doesn't change any previously-correct rendered output (compare rendered stencils across
   the fixture corpus at 38c2e15 vs 7af5dc9 — only the broken shapes may differ).
3. **`preflight_identified` agrees and disagrees correctly.** Run the ambiguous-QN fixture (two
   defs, one qualified name, different predicates): neutral `preflight` must be unable to
   distinguish, exact must follow the UUID. Where identity is unambiguous, results must match.
   Check it is a genuine second gate, not a wrapper over the neutral one.
4. **Retained duals honest.** The 8 dual pairs recorded in the plan: confirm both halves of each
   pair are callable at the paired heads and that NO forensic rename hunk leaked (the legacy
   names must still bind their legacy meanings — spot-check against `ed5b8b02` which renamed
   them). Confirm the 11 forensic test-module shims (fake-UUID / SimpleNamespace) did NOT come
   across.
5. **Quality-cleanup hunks.** Verify each of the three separately as claimed: the shadowed
   duplicate really was unreachable (both definitions byte-identical at 5088b417); the import
   fallback really was dead (module imports agentic_mbse absolutely earlier); the `load_manifest`
   behavior change has its red→green test and the narrowed exception doesn't swallow a case a
   caller relied on (search callers).
6. **Item 6 pins unmoved:** `SI_CONSTRAINT_BLOCKED` on strict, lenient, and round-tripped routes;
   the exact-boundary guard tests; run them explicitly.
7. **Gates re-run, both repos:** codegen full licensed suite (3528/47/18 claimed; delta vs
   38c2e15 exactly the 8 new tests, zero removed); agentic suite (1824/1/5 claimed; +5, zero
   removed); execution lane; 3A/3B surface (70 claimed); ruff byte-identical (codegen) and the
   agentic mypy claim (118→108, zero new, ten fixed — verify by set diff, all ten attributable
   to the cleanup hunks); `git diff --check`; changed paths ⊆ declared sets; legacy CLI smoke.
8. **Test quality** per the established bar, especially the new agentic tests (script-execution
   test actually executes the file as a script; the preflight tests derive expectations from the
   model, not from the implementation).

## Verdict

CERTIFY / FINDINGS (numbered, severity, file:line, concrete resolution) / BLOCK. State what you
did not verify. `ARTIFACT: .project/active/cutover-recovery/evidence/audit-3c.md`
