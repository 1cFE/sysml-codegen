# dc3 rerun with the 2a contract (Item 2a P7, 2026-10-19)

**Result: the 2a contract reports exactly what Item 1's did on both dc3 trees.** Same verdicts, same counts, and the same 274 and 45 findings, keyed by (rule, shape, context, declaration), with the same outcome, reason, subject, location and expected code. Two things differ, and neither is a finding: the contract version label (`subset-profile/v1` → `v2`), and the case IDs a finding cites as evidence, which grew where 2a added cases. **dc3 repaired still generates** at the final codegen revision, with no warnings and no manual stubs.

## How it was run

- **Screen.** `uv run python scripts/subset_profile/run_trees.py --final-rev HEAD --codegen-rev fdc1f784 --out /tmp/subset-2a/dc3 --tree dc3-baseline --tree dc3-repaired`, in agentic-mbse at `db25490c` (contract `subset-profile/v2`, `executable-profile/v4`), SysIDE 0.8.4. P7 gave `run_trees.py` a `--codegen-rev` parameter in place of Item 1's pinned `b5663c07`; it labels the identity and selects the corpus tree, and nothing else. Each dc3 tree was read from a `git archive` export of dc3 `808464df` or `60b44d53` into a temp directory. The dc3 checkout was only read (`git archive`, `git cat-file`); its `git status` was empty before and after.
- **Compared with** Item 1's `dc3-baseline.json` and `dc3-repaired.json` (agentic-mbse `.project/completed/20261018_exec-subset-profile/evidence/`, the runs behind `acceptance.md`), finding by finding, by a script in `/tmp` (not kept; the comparison is the one described here).
- **Generator.** `uv run sysml-codegen generate --models <export>/models --output <tmp>/pkg --package-name dc3_baseline` in this worktree at `fdc1f784`, with the license sourced, on a `git archive` export of dc3 `60b44d53` `models/` (the command dc3's own T-003 brief uses).
- **Outputs** are kept in `evidence/dc3/`: `dc3-baseline.{json,md}`, `dc3-repaired.{json,md}`, `dc3-repaired-generate.log`.

## dc3 baseline `808464df`

| | Item 1 | 2a |
|---|---|---|
| Verdict | REFUSED_INCOMPLETE | REFUSED_INCOMPLETE |
| Declarations / occurrences | 274 / 101 | 274 / 101 |
| refused / omitted / admitted / excluded / unconfirmed | 236 / 32 / 0 / 0 / 6 | 236 / 32 / 0 / 0 / 6 |
| unverified | 50 | 50, the same 50 checks |
| Roots used | all 8 generator roots | the same 8 |

B1 to B8 of `acceptance.md` are unchanged. Each difference, with its cause:

- **Contract version** `subset-profile/v1` → `v2`, on every run. Cause: 2a's record changes (P2.1 onward, design D12).
- **15 B3 findings** (`part-multiplicity` / `unresolved_bound` / `expanded_part_usage`) cite one more case, `part-multiplicity__unresolved_bound__expanded_part_usage__lower`. Cause: P2.4 added it to witness the lower-bound site.
- **32 B7 findings** (`string-value-omission` / `string_value` / `attribute_value`) cite four more cases: `…__read_by_attribute`, `…__read_by_attribute_shorthand`, `…__template`, `…__template_shorthand`. Cause: P2.2 and P4 added the String families.
- **B8 stays `unconfirmed`** (6 findings, `owner_other`). Its pairs are now recorded `unobservable` with a reason (P2.2: an unattached owner is refused first, by ES-001's code), which the finding does not print, so the run output is unchanged.

Not changed, though 2a changed the rules involved: P3 widened `calc-owned-assertion` to every owner kind the generator cannot attach (`unmapped_owner_kind`), and P4 added `calc-usage-result`. dc3's 164 asserted constraints are all owned by calc usages, which Item 1 already refused (B1), and the screen finds no calc usage with its own result expression in dc3, so neither change reaches it.

## dc3 repaired `60b44d53`

| | Item 1 | 2a |
|---|---|---|
| Verdict | CLEAR | CLEAR |
| Declarations / occurrences | 45 / 0 | 45 / 0 |
| refused / omitted / admitted / unconfirmed / unverified | 0 / 30 / 15 / 0 / 0 | 0 / 30 / 15 / 0 / 0 |
| Roots used | all 6 generator roots | the same 6 |

The only differences are the version label and the same four added String case citations on each of the 30 String omissions. Zero refused, so no R2.

**Generation at `fdc1f784`:** exit 0, "Code generation complete", 29 `INFO` lines and nothing else, so no `ManualStubNotice` warning (P4) and no refusal. `IMPLEMENTATION_BACKLOG.md` lists 0 functions to implement.

## What this does not show

- CLEAR still means no rule refuses and nothing was left unverified, not that the generator accepts (Item 1's recorded limit). Here the generator run confirms it for dc3 repaired.
- The generated package was not compared byte for byte with one generated at `b5663c07`, and its modules were not executed (that needs TEAx).
- The codegen corpus tree (`--tree corpus`) was not rerun; the plan asks for dc3 only, and the corpus is checked live by codegen's fixture agreement test (P3).
