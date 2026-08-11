# Stage brief — Phase 4, Gate 4B Group G2: the v5 snapshot read path

**You are executing one approved deletion group** of the recovery plan:
`/home/reid/1cfe/sysml-codegen-item7-rebuild/.project/active/cutover-recovery/plan.md`.
Read first: `ledger-4a.md` G2 table + the 4C family tables (the blocking rows for
`snapshot_context.py`, `loader.py`, `graph_rebuild.py`, `serializer.py`), `ledger-4a.json` for
each blocking row's disposition and proof node, the Gate 4A approval record, and the G0/G1/4C
completion notes.

## Scope — G2's six production rows, plus exactly their ledgered dependents

Production: delete `orchestration/snapshot_context.py`, `snapshot/{loader,graph_rebuild,
serializer}.py`; migrate `snapshot/capture.py` (delete `capture_snapshot` v5 + its serializer
imports; `capture_instance_graph_snapshot` stays); migrate `snapshot/__init__.py` (drop the
three v5 re-exports — this empties the 3E pinned import residual; update that pin to assert
emptiness rather than deleting it).

Dependents: ONLY test/script rows whose `blocked_by` names a G2 owner and whose ledger
disposition authorizes action now. For each: execute the row exactly — retire (the
responsibility's specimen is green; name both in the commit), rewrite (if the row says migrate),
or repoint (if it also serves a G3 owner, it survives until G3). Every removed node is named in
the commit with its row id and proof node. A test file NOT in the ledger that breaks = STOP
(rule 10, unexplained blast radius).

**The 37 committed v5 snapshot fixtures and `scripts/capture_extraction_snapshots.py` are
RETAINED — not G2 rows.** If deleting the v5 read path breaks the capture script's imports or
any retained-row test, that is a declared-path stop, not a thing to fix ad hoc: report it with
the import chain. (Ledger says the capture script writes v5 without reading loader/serializer? —
verify before assuming; it imports what it imports.)

## Requirements

1. Declared path set from the ledger BEFORE editing; stop on any surprise.
2. **Battery before commit** (the G2 table mandates real TEAx): full licensed suite — every
   count delta named row-by-row against ledger authority; 37-path corpus 15/22 unchanged;
   execution lane 38 including real TEAx at the anchor values; ruff byte-identical; mypy
   measured; `git diff --check`; `check_ledger_4a.py` paths 0 problems with G2 rows moved to
   `executed`, replacements still 54 green / 0 pending / 0 failures.
3. One deletion commit + OID record; plan Phase 4 notes updated with the group record (rows
   executed, nodes removed with authorities, battery numbers).
4. v5 rejection behavior stays: the typed v6-required refusal for a v5 snapshot must still pass
   (it must not degrade to ImportError or a stack trace when the loader is gone).

## Hard rules

Only ledgered G2 rows and their authorized dependents. No G3/G4 material, no docs, no probes, no
snapshot fixtures. Full permissions; venv/license discipline as recorded; measured gates only.

## Report back

Rows executed, every removed test node with its authority and proof node, the battery numbers
with row-level delta accounting, checker state, the v5-refusal re-proof, commit OIDs.
`ARTIFACT:` the updated plan.
