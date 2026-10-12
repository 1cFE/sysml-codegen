# Brief: implement the audit fixes — study-layer-to-codegen

Sent by the orchestrator (2026-10-12) to `/_my_implement`. Apply the fixes the audit calls for (`.project/active/study-layer-to-codegen/audit.md`, verdict Needs Work, committed at `01990a5`). Read the audit in full first. This is one fix pass. Do not reopen anything else.

## Fix now [AGENT, orchestrator, 2026-10-12]

1. **F1 (blocker): B13's time-zone roots come from the interpreter's build-time default.**
   - In `read_coverage`, take the time-zone roots from `sysconfig.get_config_var("TZPATH")`, split on `os.pathsep`. Ignore empty and non-absolute entries. Never read `zoneinfo.TZPATH` or `PYTHONTZPATH`.
   - Rewrite `tests/study/test_read_coverage.py:113-140` so it no longer relies on `PYTHONTZPATH`, and add a regression test: with `PYTHONTZPATH=/` set, an undeclared read outside the package is still refused.
   - Re-measure the preload set if the import change moves it, and update `evidence/parity/preloads.json` and the spec's B13 consequence paragraph to match. Amend the B13 text in `spec.md` to say "the interpreter's build-time `TZPATH`", and record that the change came from audit F1.
   - Re-run parity (`all`, a fresh `$S`, the README's command) and the teax lane. Both must stay green: 28 of 28 and 28 passed.
2. **F3: the record template must pass its own step-15 placeholder check when copied literally.** Change the template's preamble so it contains no `<`, or so the check excludes the preamble, whichever the runbook's check design makes cleaner. Add a test that copies the template literally and runs the step-15 placeholder Check over it.
3. **F8: shipped-text residue and missing read-through rows.**
   - Apply the audit's list to the policy template, `integration-guide.md:200`, `runbook.md:130` and `runbook.md:259`. Label the examples, or state them generally.
   - **Exception:** `STUDY_POLICY.md.template:29` sits inside an `[OWNER]` rule. Keep its words verbatim, and record in its read-through row "kept verbatim: owner-graded rule". Do not reword it.
   - Add read-through rows for the six unrecorded lines. For any row whose verdict is `moved`:
     - add its fusion-tea home as a patch in `evidence/fusion-tea/text/`, against the fusion-tea branch tip `699b0a74d` (the staged `b06585709` copy plus the branch diff in `.orchestrate-logs/src/audit/fusion-tea-branch.diff`);
     - add its ledger row to `evidence/ledger-rows.md`.

     The orchestrator applies both to the fusion-tea branch and the agentic-mbse ledger.
   - Also fix `teax-completion.md:58`, which names a script sysml-codegen does not have.
4. **F6 and F7: docs wording.** Narrow ADR-0015 to the root rule as implemented, and correct design DD2's claim about how a missing package fails. For DD2, add a note in the design's amendment section; do not rewrite the decision.
5. **F2: file the follow-ups durably, in sysml-codegen's `.project/backlog/BACKLOG.md`,** in its existing format, one item each:
   - **F-DR1:** a resume path for a record stopped at § 17;
   - **F4:** the route contract leaves the point runner open. Restate F-DR2's diagnosis per the audit;
   - **F5:** `integrate` reports a malformed census or baseline result as `seam-internal-error`. Inherited from fusion-tea; fixing it is a behaviour change;
   - **the mypy typing debt:** the per-module overrides on the eight ported modules, with what the audit says each hides;
   - **the product-ledger entry** for the study layer, due at close.

   Each item cites this item and the audit finding.

## Not in this pass

- F5's code fix (filed only).
- F9: the orchestrator completed it in agentic-mbse as `70d78d0`. `INSTALLER_API_REVISION` stays `0843fe2` until O5 moves it to the merge SHA.
- F10 (merge prep) belongs to the owner.

## As before

- **The contract** is `design.md` and `spec.md`. The closed list is B1–B13. Use `uv run --no-sync`.
- **Commit** each coherent fix with explicit paths (`git commit -- <paths>`), after checking the index is otherwise empty. Each subject leads with what changed and cites the finding. End each message with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`. Do not push.
- **Final checks:**
  - the full suite: `uv run --no-sync --env-file /home/reid/1cfe/sysml-codegen/.env pytest tests/`;
  - ruff and mypy;
  - the teax lane;
  - parity.

  Record each result in the plan's notes, under a new "Audit fix pass" heading.

Do not start background tasks. Finish with a short report per finding and `ARTIFACT: .project/active/study-layer-to-codegen/plan.md`.
