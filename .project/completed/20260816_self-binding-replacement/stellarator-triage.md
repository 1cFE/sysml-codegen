# Stellarator Triage — one read-only run of the exact route (D10)

**Date:** 2026-08-16
**Performed by:** self-binding-replacement Phase 5 (plan §Phase 5)
**Ruling:** triage only — one pipeline run, record what breaks, fix nothing, July owner hold
not reversed (`[OWNER 2026-08-15]`, spec `[NEED]` row 3).

## The run

| field | value |
|---|---|
| model root | `/home/reid/1cfe/fusion-tea-stellarator-mbse-demo/models` |
| exact command | `uv run sysml-codegen generate --models /home/reid/1cfe/fusion-tea-stellarator-mbse-demo/models --output <mktemp>/pkg --package-name stellarator_triage` (run from `/home/reid/1cfe/sysml-codegen`, `SYSIDE_LICENSE_KEY` loaded from the companion `.env`) |
| codegen commit | `20a8bb7` (Phases 1–3 landed; F-3 named-diagnostic boundary active) |
| exit code | **1** |
| first diagnostic class | `SI_SELF_BINDING` (readiness refusal: "Model is not ready for the exact route") |
| diagnostic count | **114**, all `SI_SELF_BINDING` — no other diagnostic class appeared |
| traceback | **none** (zero `Traceback` lines in the captured log) |
| output written | none — the temporary output directory was never created; the temp dir was deleted after inspection |
| retried after editing the model? | no — triage is the outcome |

Raw log: captured during the run (session scratchpad `stellarator_run.log`); the count was
derived by `grep -c SI_SELF_BINDING` and the class census by `grep -oE "SI_[A-Z_]+" | sort |
uniq -c` (exactly one class, 114 rows).

## No-mutation proof

Captured before and after the single run and compared byte for byte / line for line — all four
**UNCHANGED**:

| artifact | before = after |
|---|---|
| HEAD + branch | `7781721b`, `feat/stellarator-mbse-demo` ✓ |
| `git status --porcelain` (3 entries) | ✓ |
| tracked diff (`git diff`, 13 lines) | ✓ |
| untracked inventory (`git ls-files --others --exclude-standard`, 73 files) | ✓ |

Nothing was committed, staged, or written anywhere in the stellarator repository, and no repair
instructions were added to it.

## Reading

The refusal is exactly the defect family this item exists to end, at the count the spec
recorded: 114 self-named bindings (spec Problem §1). Per the 2026-08-15 sizing, 15 of the 114
are the copied-in fusion-tea files — whose upstream originals Phase 4 has now migrated — and 99
are the stellarator's own sites in two files (`generic_mfe/mfe_plant.sysml` ×94, including the
literal `in R = R` at `:117`; `stellarator_09/stellarator_plant.sysml` ×5). The F-3 repair held:
the refusal arrived as a typed, named diagnostic list rather than a traceback.

## Follow-up

**Owned follow-up filed:** `[STELLARATOR-D5-MIGRATION]` in `.project/backlog/BACKLOG.md` (P2,
unowned, needs an owner before any edit). The D-5 recipe and `make_d5_variant.py --root`
customer mode are proven on fusion-tea; the July hold on the stellarator repository stands.
