# E5 rescan at the final revisions (Item 2a P7, 2026-10-19)

**Result: zero unaccounted sites and zero orphan rows in both repositories.** sysml-codegen has 494 sites, 53 more than Item 1's final scan: 50 come from the scanner port's new `unrecognized` channel, and 3 net from 2a's own code changes (6 added, 4 removed, 2 of those pairs being renames). agentic-mbse's 61 site IDs are identical to Item 1's.

## How it was run

- **sysml-codegen.** `tests/conformance/subset_profile/test_site_account.py` (E1) passes at `bec70d04`, the last commit that touches `src/`; the P7 commits touch no `src/` file, so the account is the same at the gate revision. To itemize, `evidence/experiments/rescan.py` scanned `src/` of the 2a base and of each 2a commit that touched `src/`, each from a `git archive` export, with the final scanner (`tests/helpers/subset_profile/site_scan.py`). It also compared the scan of the base with Item 1's final scan (agentic-mbse `.project/completed/20261018_exec-subset-profile/evidence/site-scan-final.csv`, `scan_sites/1`, codegen `b5663c07`), so a difference made by the scanner port is told apart from one made by the code. Command:
  `uv run --extra dev python .project/active/subset-profile-conformance/evidence/experiments/rescan.py <item1 site-scan-final.csv> /tmp/subset-2a/rescan b5663c07 06f938fc d2319b97 5f4b86ad 0a17b82b bab368fe 374e889f bec70d04` (full revisions passed).
- **agentic-mbse.** `uv run python scripts/subset_profile/scan_sites.py --agentic-rev HEAD --out /tmp/subset-2a/rescan/agentic-final.csv --reconcile tests/fixtures/subset_profile/inventory/site_account.csv` at `42798bc0` (the last commit that touches `src/`): 61 sites, "0 unaccounted, 0 orphan". The 61 site IDs equal Item 1's final scan's 61 agentic-mbse IDs, compared as sets.

## sysml-codegen: what changed and why

| Step | Commit | Change | Site | Cause |
|---|---|---|---|---|
| Scanner port | P1.4 `a353ddd3` | +50 | the `unrecognized` channel | The port reports every `raise` the `scan_sites/1` forms miss, by name. Each row's role was set by reading the raise (plan, Step 1.4 notes). Scanning the base with the final scanner gives Item 1's 441 IDs plus these 50, and nothing else. |
| P1.3 | `06f938fc` | +1 | `snapshot/instance_graph.py::_diagnostic_to_data::builtin::ValueError::1` | The v6 encoder refuses a `Diagnostic` that carries a `SiteReason` (design D8). Role `internal_invariant`. |
| P1.3 | `06f938fc` | −1 | `orchestration/elaborated_pipeline.py::_readiness_with_referent::coded-relay::finding.code::1` | The converter now copies the carrier with `dataclasses.replace`, so no `code=…code` relay call remains. |
| P1.3 | `06f938fc` | −1 | `orchestration/elaborated_pipeline.py::_diagnostic_with_referent::coded-relay::diagnostic.code::1` | Same as the line above. |
| P1.5 | `d2319b97` | +1 | `subset_profile_adapter.py::<module>::unrecognized::ImportError::1` | The adapter's import-time profile check (design D12). Role `environment`. |
| P1.5 | `d2319b97` | +1 | `subset_profile_adapter.py::render_finding::builtin::ValueError::1` | The renderer refuses a refused finding whose reason maps to `NO_REFUSAL`. Role `internal_invariant`. |
| P2.1 | `5f4b86ad` | +1 | `orchestration/exact_pipeline_context.py::_project_or_fail::free-text::CodeGenerationError::2` | The projection refusal now carries the diagnostics it wraps. Role `relay_plumbing`. |
| P4 | `bab368fe` | +1 | `extraction/expression_compiler.py::ExactCompilationResult.__post_init__::builtin::ValueError::1` | A compilation result whose `MANUAL_REQUIRED`, `stub_reason` and `unsupported_reason` disagree is refused. Role `internal_invariant`. |
| P6 | `bec70d04` | rename | `elaboration/elaborate.py::_ExactElaborator._typed_definition`: `builtin::ValueError::1` → `coded::SI_TYPE_INVALID::1` | The O8 conversion: an untyped calc usage was refused `SI_INTERNAL_DEFECT` through a plain `ValueError`, and is now refused `SI_TYPE_INVALID`. Same raise, new channel and code. Role `public_capability`. |
| P6 | `bec70d04` | rename | `elaboration/graph.py::InstanceGraph._expression_reference_count`: `builtin::TypeError::2` → `unrecognized::UnsupportedExpressionIRError::1` | The raise now uses `UnsupportedExpressionIRError` (a `TypeError` subclass) so its reason reaches `validate()`'s diagnostic. Role `public_capability`. |

P2.4, P5 and the P2.2 and P2.3 steps changed `src/` without adding or removing a site: they added reasons and carriers at existing raises.

Total: 441 + 50 − 2 + 2 + 1 + 1 + 0 = 494, the account's `sites:` header.

**Correction.** The Phase 6 notes say "three codegen site IDs were renamed". The rescan finds two: the P6 commit's account diff removes and adds exactly the four IDs in the last two rows above. The third was not a site ID change.

## agentic-mbse

No site added or removed since Item 1's final scan (`ce0ad1ff`). 2a's agentic-mbse changes under `src/` added rules, facts, cases and a qualification, none of which raises. The roles changed by E4 and P6 are row edits, not site changes.

## What this does not show

- The scanner is total over `raise` statements under `src/sysml_codegen/`, not over refusals. The blind spots in the account header still apply: refusals returned as values, raising helpers whose callers are not itemized, silent omissions, dynamic dispatch, and refusals outside Python source.
- The per-commit attribution scanned each codegen revision with the final agentic-mbse source for the cross-tree factory search, not the agentic-mbse revision of the time. The final scan, which is the one E5 requires, uses the final source of both.
