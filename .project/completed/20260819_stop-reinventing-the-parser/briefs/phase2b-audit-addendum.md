Phase 2b reopened the tree you audited and landed two commits on top of `68bca37`:
`efc235a` (tests) → `3f8bd58` (production). Your task: audit that landing and write the
**Phase 2 audit addendum** that plan Revision 4 requires — re-establishing your finding m3 on
its new basis. This is a targeted audit of the reopening, not a re-audit of Phase 2.

Context to read first: design.md is now **Revision 8** — its `#one-total-inspection-operation`
section carries the owner's opaque-unit contract, the shared `unit_annotation_value` primitive,
the arity ruling, and "What this retires in the Phase-2 tree" (which names the two superseded
shape assertions your m3 confirmation partly rested on). Plan Revision 4's "Phase 2b" section
and its completion record state what was claimed. `run-records/phase3-stop-report.md` is the
measured cause.

Audit by execution, from your own fresh extraction of `3f8bd58`:

1. **The falsified premise is actually gone.** The stop report's exact case — compound-unit
   density on the real corpus — must elaborate; `[m]`, `[kg/m^3]`, `[W/(m*K)]` accepted; the
   unit operand neither traversed nor emitted. Verify the non-traversal proof (the
   raise-on-read double) is real — kill it in a copy if cheap.
2. **m3 re-established on non-emission.** Your original m3 said the unit operand must never be
   emitted as a reference use; your confirmation accepted shape validation as part of the
   closure. That shape validation is now retired by owner ruling. State explicitly whether
   non-emission alone, plus the arity refusal, closes m3's substance — and whether the
   project-scoped-unit double from your confirmation still holds under the new mechanism.
3. **The primitive's contract.** Exactly-two-operands raises the named refusal
   (`EXPRESSION_KIND_UNSUPPORTED`); `None` strictly means "not a `[` annotation"; recognition
   from mapped metatype + operator, no runtime class names; `inspect_reference_uses` is the
   sole caller and walks only the returned value operand.
4. **No collateral movement.** The rest of the boundary you audited must be unchanged: rerun
   your key gates (focused suites, scoped strict, fast-suite baseline — expect exactly the 18
   optional-dep failures, repo-wide 101/119, wheel markers at unchanged `0.1.3` /
   `semantic-evidence/v2` with deleted symbols still absent). The completion record claims
   38/20/8 focused, 18/1899/1 fast, 840/1 isolated — verify or correct.
5. **The implementer's two flags.** (a) Design rev 8 said "kept tests pin both" retired rules;
   the implementer found no such test nodes — confirm by your own sweep and say whether the
   design's factual claim needs a correction note. (b) The `[W/(m·K)]` → `[W/(m*K)]`
   substitution under SysIDE 0.8.4 — verify the middle-dot form really fails to parse and that
   the substitution preserves the representative structural kind the owner named.

Same rules as before: worktrees read-only for you, build your own extraction (path containing
`agentic-mbse`), license via `set -a; source /home/reid/1cfe/agentic-mbse/.env; set +a`, never
invoke the PDF/paid suites, modify nothing, commit nothing.

Append a dated "Phase 2b addendum — the reopened landing" section to
`.project/active/stop-reinventing-the-parser/run-records/phase2-audit.md` (do not commit) with
verdict Confirmed / Not confirmed per item, any findings ranked, and whether Phase 3 may
consume `3f8bd58` as its upstream. Final message: prose summary ending with
ARTIFACT: .project/active/stop-reinventing-the-parser/run-records/phase2-audit.md
